"""
Reporting and export endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Optional, Dict, Any, List
from app.services.report_service import ReportService
from app.services.project_service import ProjectService
from app.api.v1.dependencies import get_report_service, get_project_service

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{project_id}")
async def generate_project_report(
    project_id: str,
    app_name: Optional[str] = None,
    format: str = "json",
    report_service: ReportService = Depends(get_report_service),
    project_service: ProjectService = Depends(get_project_service)
):
    """Generate comprehensive project report"""
    return await report_service.generate_project_report(
        project_id, app_name, format, project_service
    )

@router.get("/{project_id}/summary")
async def get_project_summary(
    project_id: str,
    app_name: Optional[str] = None,
    report_service: ReportService = Depends(get_report_service)
):
    """Get project summary statistics"""
    return await report_service.get_project_summary(project_id, app_name)

@router.get("/{project_id}/performance")
async def get_performance_report(
    project_id: str,
    app_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    report_service: ReportService = Depends(get_report_service)
):
    """Get performance analysis report"""
    return await report_service.get_performance_report(
        project_id, app_name, start_date, end_date
    )

@router.get("/{project_id}/errors")
async def get_error_report(
    project_id: str,
    app_name: Optional[str] = None,
    severity: Optional[str] = None,
    report_service: ReportService = Depends(get_report_service)
):
    """Get error analysis report"""
    return await report_service.get_error_report(project_id, app_name, severity)

@router.get("/{project_id}/trends")
async def get_trends_report(
    project_id: str,
    app_name: Optional[str] = None,
    metric: str = "all",
    period: str = "daily",
    report_service: ReportService = Depends(get_report_service)
):
    """Get trends analysis report"""
    return await report_service.get_trends_report(project_id, app_name, metric, period)

@router.get("/{project_id}/export")
async def export_analysis_data(
    project_id: str,
    format: str = "csv",
    app_name: Optional[str] = None,
    report_service: ReportService = Depends(get_report_service)
):
    """Export analysis data in various formats"""
    return await report_service.export_analysis_data(project_id, format, app_name)

@router.get("/comparison")
async def compare_projects(
    project_ids: List[str],
    metric: str = "performance",
    report_service: ReportService = Depends(get_report_service)
):
    """Compare metrics across multiple projects"""
    return await report_service.compare_projects(project_ids, metric)
