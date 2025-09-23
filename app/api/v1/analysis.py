"""
Analysis and processing endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Optional, Dict, Any, List
from app.services.analysis_service import AnalysisService
from app.services.project_service import ProjectService
from app.api.v1.dependencies import get_analysis_service, get_project_service

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/run/{project_id}")
async def run_analysis(
    project_id: str,
    background_tasks: BackgroundTasks,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    project_service: ProjectService = Depends(get_project_service)
):
    """Run analysis on a project"""
    return await analysis_service.run_analysis(background_tasks, project_id, project_service)

@router.get("/results/{project_id}")
async def get_analysis_results(
    project_id: str,
    app_name: Optional[str] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get analysis results for a project, optionally filtered by application"""
    return await analysis_service.get_analysis_results(project_id, app_name)

@router.get("/logs/{project_id}")
async def get_log_files(
    project_id: str,
    app_name: Optional[str] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get list of log files for a project/application"""
    return await analysis_service.get_log_files(project_id, app_name)

@router.get("/log-content/{project_id}")
async def get_log_content(
    project_id: str,
    file_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get content of a specific log file with optional line range"""
    return await analysis_service.get_log_content(project_id, file_path, start_line, end_line)

@router.get("/aggregated/{project_id}")
async def get_aggregated_data(
    project_id: str,
    app_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get aggregated analysis data with optional filters"""
    return await analysis_service.get_aggregated_data(
        project_id, app_name, start_date, end_date
    )

@router.get("/advanced/{project_id}")
async def get_advanced_analysis(
    project_id: str,
    app_name: Optional[str] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get advanced analysis results"""
    return await analysis_service.get_advanced_analysis(project_id, app_name)

@router.get("/anomalies/{project_id}")
async def get_anomalies(
    project_id: str,
    app_name: Optional[str] = None,
    threshold: Optional[float] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get anomaly detection results"""
    return await analysis_service.get_anomalies(project_id, app_name, threshold)

@router.get("/statistics/{project_id}")
async def get_analysis_statistics(
    project_id: str,
    app_name: Optional[str] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get comprehensive analysis statistics"""
    return await analysis_service.get_analysis_statistics(project_id, app_name)
