"""
Agent Tasks for Celery
Background tasks for both integrated and service-based agent analysis
"""

from celery import current_task
from app.core.celery import celery_app
from app.core.agent_orchestrator import AgentOrchestrator
from app.services.agent_service_client import AgentServiceClient
from app.services.file_system_integration import FileSystemIntegration
from app.core.config import get_settings
import structlog
from pathlib import Path
import asyncio

logger = structlog.get_logger(__name__)

@celery_app.task(bind=True, name="app.tasks.agent_tasks.hybrid_agent_analysis_task")
def hybrid_agent_analysis_task(self, project_id: str, application_name: str, agent_type: str, analysis_config: dict = None):
    """Hybrid Celery task for running agent analysis (integrated or service-based)"""
    try:
        logger.info(f"Starting hybrid agent analysis task for {application_name} using {agent_type}")
        
        # Update task status
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': f'Starting {agent_type} agent analysis...'}
        )
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator()
        
        # Check agent execution mode
        execution_mode = "unknown"
        try:
            execution_mode = orchestrator.agent_registry.get_agent_execution_mode(agent_type)
            logger.info(f"Agent {agent_type} will run in {execution_mode} mode")
        except Exception as e:
            logger.warning(f"Could not determine execution mode for {agent_type}: {e}")
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': f'Using {execution_mode} mode for {agent_type}...'}
        )
        
        # Run analysis using orchestrator
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': f'Running {agent_type} analysis...'}
        )
        
        # Execute analysis (orchestrator handles both integrated and service modes)
        result = asyncio.run(orchestrator.analyze_logs(
            project_id=project_id,
            application_name=application_name,
            agent_type=agent_type,
            log_data={},  # Will be populated by orchestrator
            analysis_config=analysis_config or {}
        ))
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Processing results...'}
        )
        
        if result.get("status") == "completed":
            # Success
            current_task.update_state(
                state='SUCCESS',
                meta={'current': 100, 'total': 100, 'status': f'{agent_type} analysis completed successfully'}
            )
            
            logger.info(f"Hybrid agent analysis task completed for {application_name}")
            return {
                "status": "completed",
                "project_id": project_id,
                "application": application_name,
                "agent_type": agent_type,
                "execution_mode": execution_mode,
                "results": result
            }
        else:
            raise Exception(f"Agent analysis failed: {result}")
            
    except Exception as e:
        logger.error(f"Hybrid agent analysis task failed: {e}")
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e), 'agent_type': agent_type}
        )
        raise
