"""
Analysis Tasks for Celery
Background tasks for log analysis operations
"""

from celery import current_task
from app.core.celery import celery_app
from app.analytics.analysis_engine import AnalysisEngine
from app.services.project_analysis_manager import ProjectAnalysisManager
from app.core.config import get_settings
import structlog

logger = structlog.get_logger(__name__)

@celery_app.task(bind=True, name="app.tasks.analysis_tasks.run_analysis_task")
def run_analysis_task(self, analysis_id: str, project_id: str):
    """Celery task for running project analysis"""
    try:
        logger.info(f"Starting analysis task: {analysis_id} for project: {project_id}")
        
        # Update task status
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting analysis...'}
        )
        
        # Initialize components
        settings = get_settings()
        analysis_engine = AnalysisEngine()
        project_manager = ProjectAnalysisManager(settings.DATA_DIR, project_id)
        
        # Get analysis configuration
        analysis = project_manager.get_analysis(analysis_id)
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': 'Loading project data...'}
        )
        
        # Run analysis
        result = analysis_engine.run_analysis(
            project_id=project_id,
            config=analysis.configuration
        )
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 75, 'total': 100, 'status': 'Saving results...'}
        )
        
        # Save results
        analysis.status = "completed"
        analysis.result = result
        project_manager.save_analysis(analysis)
        
        # Complete
        current_task.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Analysis completed'}
        )
        
        logger.info(f"Analysis task completed: {analysis_id}")
        return {"status": "completed", "analysis_id": analysis_id}
        
    except Exception as e:
        logger.error(f"Analysis task failed: {e}")
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.analysis_tasks.run_application_analysis_task")
def run_application_analysis_task(self, analysis_id: str, project_id: str, application_name: str):
    """Celery task for running application-specific analysis"""
    try:
        logger.info(f"Starting application analysis task: {analysis_id} for {application_name}")
        
        # Update task status
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': f'Starting {application_name} analysis...'}
        )
        
        # Initialize components
        settings = get_settings()
        from app.services.application_analysis_manager import ApplicationAnalysisManager
        analysis_manager = ApplicationAnalysisManager(settings.DATA_DIR)
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': f'Analyzing {application_name} logs...'}
        )
        
        # Run application-specific analysis
        result = analysis_manager.analyze_application(
            project_id=project_id,
            application_name=application_name,
            analysis_id=analysis_id
        )
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Finalizing results...'}
        )
        
        # Complete
        current_task.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': f'{application_name} analysis completed'}
        )
        
        logger.info(f"Application analysis task completed: {analysis_id} for {application_name}")
        return {"status": "completed", "analysis_id": analysis_id, "application": application_name}
        
    except Exception as e:
        logger.error(f"Application analysis task failed: {e}")
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
