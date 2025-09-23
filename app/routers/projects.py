"""
Projects router - extracted from main.py
"""
import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
import structlog

from app.utils.data_loader import projects_db, save_data
from app.core.config import get_settings

logger = structlog.get_logger()
router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/")
async def list_projects():
    """List all projects"""
    try:
        projects = []
        for project_id, project in projects_db.items():
            projects.append({
                "id": project_id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "created_at": project.upload_timestamp.isoformat(),
                "file_size": project.file_size_bytes
            })
        
        return {"projects": projects}
        
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    try:
        if project_id not in projects_db:
            logger.warning(f"Project not found: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        return {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.upload_timestamp.isoformat(),
            "file_size": project.file_size_bytes,
            "extraction_path": project.extraction_path
        }
        
    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        # Remove project directory if it exists
        if hasattr(project, 'extraction_path') and project.extraction_path:
            import shutil
            if os.path.exists(project.extraction_path):
                shutil.rmtree(project.extraction_path)
        
        # Remove from database
        del projects_db[project_id]
        save_data()
        
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_project(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Create a new project - simplified version"""
    try:
        logger.info(f"Creating project: {name}")
        
        # Basic validation
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Project name is required")
        
        # Read file content
        content = await file.read()
        actual_size = len(content)
        
        # Basic size check (100MB limit)
        if actual_size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 100MB limit")
        
        settings = get_settings()
        upload_dir = os.path.join(settings.DATA_DIR, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        upload_path = os.path.join(upload_dir, file.filename)
        with open(upload_path, "wb") as buffer:
            buffer.write(content)
        
        return {
            "message": "Project creation started",
            "status": "processing",
            "file_size": actual_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))
