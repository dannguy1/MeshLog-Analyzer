"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/api")
async def api_health_check():
    """API health check"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "timestamp": datetime.now().isoformat()
    }
