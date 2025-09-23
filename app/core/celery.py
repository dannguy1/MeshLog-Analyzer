"""
Celery Configuration for prplOS LCM Log Analysis System
"""

import os
from celery import Celery
from app.core.config import get_settings

# Get settings
settings = get_settings()

# Create Celery instance
celery_app = Celery(
    "prplos_log_analysis",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.analysis_tasks",
        "app.tasks.processing_tasks", 
        "app.tasks.agent_tasks",
        "app.tasks.maintenance_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=[settings.CELERY_ACCEPT_CONTENT],
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    
    # Task routing with hybrid agent support
    task_routes={
        "app.tasks.analysis_tasks.*": {"queue": "analysis"},
        "app.tasks.processing_tasks.*": {"queue": "processing"},
        "app.tasks.agent_tasks.*": {"queue": "agent_analysis"},
        "app.tasks.agent_tasks.hybrid_agent_analysis_task": {"queue": "integrated_agents"},
        "app.tasks.agent_tasks.legacy_agent_analysis_task": {"queue": "service_agents"},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Task timeouts
    task_soft_time_limit=settings.ANALYSIS_TIMEOUT - 60,  # 59 minutes
    task_time_limit=settings.ANALYSIS_TIMEOUT,  # 60 minutes
    
    # Result expiration
    result_expires=3600,  # 1 hour
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-expired-results': {
        'task': 'app.tasks.maintenance_tasks.cleanup_expired_results',
        'schedule': 3600.0,  # Run every hour
    },
    'health-check': {
        'task': 'app.tasks.maintenance_tasks.health_check',
        'schedule': 300.0,  # Run every 5 minutes
    },
}

if __name__ == "__main__":
    celery_app.start()
