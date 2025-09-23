"""
Administrative endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from app.services.admin_service import AdminService
from app.api.v1.dependencies import get_admin_service

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/validate-data")
async def validate_data_consistency(
    admin_service: AdminService = Depends(get_admin_service)
):
    """Validate data consistency across projects and database"""
    return await admin_service.validate_data_consistency()

@router.post("/cleanup")
async def cleanup_projects(
    admin_service: AdminService = Depends(get_admin_service)
):
    """Clean up orphaned projects and files"""
    return await admin_service.cleanup_projects()

@router.get("/system-info")
async def get_system_info(
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get system information and statistics"""
    return await admin_service.get_system_info()

@router.get("/backup")
async def backup_data(
    admin_service: AdminService = Depends(get_admin_service)
):
    """Create backup of all project data"""
    return await admin_service.backup_data()

@router.post("/restore")
async def restore_from_backup(
    backup_file: str,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Restore data from backup file"""
    return await admin_service.restore_from_backup(backup_file)

@router.get("/disk-usage")
async def get_disk_usage(
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get disk usage statistics"""
    return await admin_service.get_disk_usage()

@router.get("/logs")
async def get_application_logs(
    lines: Optional[int] = 100,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get application logs"""
    return await admin_service.get_application_logs(lines)
