"""
Processing Tasks for Celery
Background tasks for package processing operations
"""

from celery import current_task
from app.core.celery import celery_app
from app.processors.package_processor import PackageProcessor
from app.core.config import get_settings
import structlog

logger = structlog.get_logger(__name__)

@celery_app.task(bind=True, name="app.tasks.processing_tasks.process_package_task")
def process_package_task(self, package_path: str, project_id: str):
    """Celery task for processing uploaded packages"""
    try:
        logger.info(f"Starting package processing task for project: {project_id}")
        
        # Update task status
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting package processing...'}
        )
        
        # Initialize processor
        processor = PackageProcessor()
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': 'Extracting package...'}
        )
        
        # Process package
        result = processor.process_package(package_path, project_id)
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 75, 'total': 100, 'status': 'Finalizing extraction...'}
        )
        
        # Complete
        current_task.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Package processing completed'}
        )
        
        logger.info(f"Package processing task completed for project: {project_id}")
        return {"status": "completed", "project_id": project_id, "result": result}
        
    except Exception as e:
        logger.error(f"Package processing task failed: {e}")
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
