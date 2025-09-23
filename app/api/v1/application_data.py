"""
Application Data API endpoints
Provides search, sort, and analysis capabilities for application data
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
import structlog
from app.services.application_data_manager import ApplicationDataManager
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/projects/{project_id}/applications/{application_name}/data", tags=["application-data"])

@router.get("/logs")
async def search_logs(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name"),
    query: Optional[str] = Query(None, description="Full-text search query"),
    log_level: Optional[str] = Query(None, description="Filter by log level"),
    container_id: Optional[str] = Query(None, description="Filter by container ID"),
    message_types: Optional[List[str]] = Query(None, description="Filter by message types"),
    start_time: Optional[str] = Query(None, description="Start time filter (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time filter (ISO format)"),
    limit: int = Query(1000, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Search log entries with various filters"""
    try:
        settings = get_settings()
        data_manager = ApplicationDataManager(
            project_id=project_id,
            application_name=application_name,
            data_dir=settings.DATA_DIR
        )
        
        logs = data_manager.search_logs(
            query=query,
            log_level=log_level,
            container_id=container_id,
            message_types=message_types,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
        
        # Get total count with same filters
        total_count = data_manager.get_total_log_count(
            query=query,
            log_level=log_level,
            container_id=container_id,
            message_types=message_types,
            start_time=start_time,
            end_time=end_time
        )
        
        return {
            "logs": logs,
            "count": len(logs),
            "total_count": total_count,
            "filters": {
                "query": query,
                "log_level": log_level,
                "container_id": container_id,
                "message_types": message_types,
                "start_time": start_time,
                "end_time": end_time
            },
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching logs for {application_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_log_statistics(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name")
):
    """Get statistical summary of log data"""
    try:
        settings = get_settings()
        data_manager = ApplicationDataManager(
            project_id=project_id,
            application_name=application_name,
            data_dir=settings.DATA_DIR
        )
        
        stats = data_manager.get_log_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics for {application_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_data_summary(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name")
):
    """Get comprehensive data summary including metadata, logs, and analysis"""
    try:
        settings = get_settings()
        data_manager = ApplicationDataManager(
            project_id=project_id,
            application_name=application_name,
            data_dir=settings.DATA_DIR
        )
        
        summary = data_manager.get_data_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Error getting summary for {application_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csv")
async def export_to_csv(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name"),
    query: Optional[str] = Query(None, description="Full-text search query"),
    log_level: Optional[str] = Query(None, description="Filter by log level"),
    container_id: Optional[str] = Query(None, description="Filter by container ID"),
    start_time: Optional[str] = Query(None, description="Start time filter (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time filter (ISO format)")
):
    """Export log data to CSV format"""
    try:
        settings = get_settings()
        data_manager = ApplicationDataManager(
            project_id=project_id,
            application_name=application_name,
            data_dir=settings.DATA_DIR
        )
        
        # Create export path
        import os
        export_dir = os.path.join(settings.DATA_DIR, "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        export_filename = f"{project_id}_{application_name}_logs.csv"
        export_path = os.path.join(export_dir, export_filename)
        
        filters = {
            "query": query,
            "log_level": log_level,
            "container_id": container_id,
            "start_time": start_time,
            "end_time": end_time
        }
        
        count = data_manager.export_to_csv(export_path, filters)
        
        return {
            "message": f"Exported {count} log entries",
            "export_path": export_path,
            "filename": export_filename,
            "count": count
        }
        
    except Exception as e:
        logger.error(f"Error exporting CSV for {application_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_data(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name"),
    days_to_keep: int = Query(30, description="Number of days to keep")
):
    """Clean up old log data"""
    try:
        settings = get_settings()
        data_manager = ApplicationDataManager(
            project_id=project_id,
            application_name=application_name,
            data_dir=settings.DATA_DIR
        )
        
        deleted_count = data_manager.cleanup_old_data(days_to_keep)
        
        return {
            "message": f"Cleaned up {deleted_count} old log entries",
            "deleted_count": deleted_count,
            "days_to_keep": days_to_keep
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up data for {application_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/info")
async def get_database_info(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name")
):
    """Get database information and size"""
    try:
        settings = get_settings()
        data_manager = ApplicationDataManager(
            project_id=project_id,
            application_name=application_name,
            data_dir=settings.DATA_DIR
        )
        
        db_size = data_manager.get_database_size()
        
        return {
            "database_path": str(data_manager.db_path),
            "size_bytes": db_size,
            "size_mb": round(db_size / (1024 * 1024), 2),
            "exists": data_manager.db_path.exists()
        }
        
    except Exception as e:
        logger.error(f"Error getting database info for {application_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

