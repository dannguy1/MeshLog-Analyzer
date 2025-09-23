"""
FastAPI dependencies for service injection
"""
from app.services.project_service import ProjectService
from app.services.analysis_service import AnalysisService

# Simple placeholder classes for missing services
class ValidationService:
    pass

class ReportService:
    pass

class AdminService:
    pass

def get_project_service() -> ProjectService:
    """Get project service instance"""
    return ProjectService()

def get_analysis_service() -> AnalysisService:
    """Get analysis service instance"""
    return AnalysisService()

def get_validation_service() -> ValidationService:
    """Get validation service instance"""
    return ValidationService()

def get_report_service() -> ReportService:
    """Get report service instance"""
    return ReportService()

def get_admin_service() -> AdminService:
    """Get admin service instance"""
    return AdminService()
