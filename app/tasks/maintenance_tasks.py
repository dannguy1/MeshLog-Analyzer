"""
Maintenance Tasks for Celery
Background tasks for system maintenance
"""

from celery import current_task
from app.core.celery import celery_app
from app.core.config import get_settings
import structlog
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

logger = structlog.get_logger(__name__)

@celery_app.task(name="app.tasks.maintenance_tasks.cleanup_expired_results")
def cleanup_expired_results():
    """Clean up expired analysis results and temporary files"""
    try:
        logger.info("Starting cleanup of expired results")
        
        settings = get_settings()
        data_dir = Path(settings.DATA_DIR)
        
        # Clean up temporary files older than 24 hours
        temp_dir = data_dir / "temp"
        if temp_dir.exists():
            cutoff_time = time.time() - (24 * 3600)  # 24 hours
            cleaned_files = 0
            
            for temp_file in temp_dir.rglob("*"):
                if temp_file.is_file() and temp_file.stat().st_mtime < cutoff_time:
                    try:
                        temp_file.unlink()
                        cleaned_files += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file {temp_file}: {e}")
            
            logger.info(f"Cleaned up {cleaned_files} temporary files")
        
        # Clean up old logs
        logs_dir = data_dir / "logs"
        if logs_dir.exists():
            cutoff_time = time.time() - (7 * 24 * 3600)  # 7 days
            cleaned_logs = 0
            
            for log_file in logs_dir.glob("*.log.*"):  # Rotated log files
                if log_file.stat().st_mtime < cutoff_time:
                    try:
                        log_file.unlink()
                        cleaned_logs += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete log file {log_file}: {e}")
            
            logger.info(f"Cleaned up {cleaned_logs} old log files")
        
        return {"status": "completed", "cleaned_files": cleaned_files, "cleaned_logs": cleaned_logs}
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise

@celery_app.task(name="app.tasks.maintenance_tasks.health_check")
def health_check():
    """Perform system health check"""
    try:
        logger.debug("Performing system health check")
        
        settings = get_settings()
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Check data directory
        data_dir = Path(settings.DATA_DIR)
        health_data["checks"]["data_directory"] = {
            "exists": data_dir.exists(),
            "writable": os.access(data_dir, os.W_OK) if data_dir.exists() else False
        }
        
        # Check disk space
        if data_dir.exists():
            statvfs = os.statvfs(data_dir)
            free_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
            health_data["checks"]["disk_space"] = {
                "free_gb": round(free_space_gb, 2),
                "low_space": free_space_gb < 1.0  # Less than 1GB
            }
        
        # Check Redis connection
        try:
            from app.services.redis_manager import redis_manager
            redis_manager.ping()
            health_data["checks"]["redis"] = {"status": "connected"}
        except Exception as e:
            health_data["checks"]["redis"] = {"status": "failed", "error": str(e)}
            health_data["status"] = "degraded"
        
        # Check wnc-log-agents if enabled
        if settings.WNC_LOG_AGENTS_ENABLED:
            try:
                from app.services.agent_service_client import AgentServiceClient
                client = AgentServiceClient()
                agents = client.list_agents()
                health_data["checks"]["agents"] = {
                    "status": "available",
                    "count": len(agents)
                }
                client.close()
            except Exception as e:
                health_data["checks"]["agents"] = {
                    "status": "unavailable",
                    "error": str(e)
                }
                # Don't mark as degraded if agents are optional
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        }
