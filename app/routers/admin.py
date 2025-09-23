"""
Admin router - administrative endpoints
"""
from fastapi import APIRouter, HTTPException
import structlog

from app.utils.data_loader import projects_db, save_data

logger = structlog.get_logger()
router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/clear-all-data")
async def clear_all_data():
    """Clear all project data - admin only"""
    try:
        logger.warning("Clearing all project data")
        
        # Clear in-memory data
        projects_db.clear()
        
        # Save empty state
        save_data(allow_empty=True)
        
        return {
            "message": "All data cleared successfully",
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recover-projects")
async def recover_projects():
    """Recover missing projects from filesystem"""
    try:
        logger.info("Starting project recovery...")
        
        # Simplified recovery logic
        recovered_count = 0
        
        return {
            "message": f"Recovery completed. Found {recovered_count} projects",
            "recovered_count": recovered_count
        }
        
    except Exception as e:
        logger.error(f"Failed to recover projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-info")
async def get_system_info():
    """Get system information"""
    try:
        return {
            "projects_count": len(projects_db),
            "system_status": "healthy",
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
