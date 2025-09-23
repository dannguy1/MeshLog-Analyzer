"""
Project management endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends
from typing import Optional, Dict, Any
from app.services.project_service import ProjectService
from app.services.validation_service import ValidationService
from app.api.v1.dependencies import get_project_service, get_validation_service

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/")
async def list_projects(
    project_service: ProjectService = Depends(get_project_service)
):
    """List all projects"""
    return await project_service.list_projects()

@router.post("/")
async def create_project(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    project_service: ProjectService = Depends(get_project_service),
    validation_service: ValidationService = Depends(get_validation_service)
):
    """Create a new project with uploaded package"""
    return await project_service.create_project(
        background_tasks, file, name, description, validation_service
    )

@router.get("/{project_id}")
async def get_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """Get project details including package metadata"""
    return await project_service.get_project(project_id)

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """Delete a project and all its associated analyses"""
    return await project_service.delete_project(project_id)

@router.get("/restore/available")
async def list_available_packages(
    project_service: ProjectService = Depends(get_project_service)
):
    """List all available packages in UPLOAD_DIR that can be used for restoration"""
    return await project_service.list_available_packages()

@router.post("/restore")
async def restore_project_from_package(
    background_tasks: BackgroundTasks,
    filename: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    project_service: ProjectService = Depends(get_project_service),
    validation_service: ValidationService = Depends(get_validation_service)
):
    """Restore a project from a previously uploaded package"""
    return await project_service.restore_project_from_package(
        background_tasks, filename, name, description, validation_service
    )

@router.get("/{project_id}/export")
async def export_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """Export a complete project with all metadata and data"""
    return await project_service.export_project(project_id)

@router.post("/import")
async def import_project(
    project_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    project_service: ProjectService = Depends(get_project_service)
):
    """Import a project from export data"""
    return await project_service.import_project(project_data, background_tasks)

@router.get("/{project_id}/applications")
async def get_project_applications(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """Get list of applications for a project"""
    return await project_service.get_project_applications(project_id)

@router.get("/{project_id}/applications/{app_name}")
async def get_application_info(
    project_id: str,
    app_name: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """Get information about a specific application"""
    return await project_service.get_application_info(project_id, app_name)
