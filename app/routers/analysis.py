"""
Analysis router - simplified analysis endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import structlog

from app.utils.data_loader import projects_db

logger = structlog.get_logger()
router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/run/{project_id}")
async def run_analysis(project_id: str, background_tasks: BackgroundTasks):
    """Run analysis on a project"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        logger.info(f"Starting analysis for project: {project.name}")
        
        # Schedule background analysis
        background_tasks.add_task(run_analysis_background, project_id)
        
        return {
            "message": "Analysis started",
            "project_id": project_id,
            "status": "running"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{project_id}")
async def get_analysis_results(project_id: str):
    """Get analysis results for a project"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Simplified - return basic project info for now
        project = projects_db[project_id]
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "status": project.status,
            "analysis_count": getattr(project, 'analysis_count', 0),
            "results": "Analysis results would be here"
        }
        
    except Exception as e:
        logger.error(f"Failed to get analysis results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis_background(project_id: str):
    """Background task for analysis"""
    try:
        logger.info(f"Running background analysis for project: {project_id}")
        # Simplified analysis logic here
        # In real implementation, this would call the analysis engine
        
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")
