"""
Refactored main FastAPI application with organized routers
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import structlog

# Import existing components
from app.websocket_manager import manager
from app.core.config import get_settings

# Import new router modules  
from app.routers import (
    health,
    projects, 
    analysis,
    admin,
    visualization
)

# Configure logging
settings = get_settings()
logs_dir = os.path.join(settings.DATA_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, 'app.log')),
        logging.StreamHandler()
    ]
)

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="prplOS LCM Log Analysis System",
    description="Advanced log analysis and monitoring system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(projects.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(visualization.router, prefix="/api/v1")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message: {data}", websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

# Load data on startup
@app.on_event("startup")
async def startup_event():
    """Load data when application starts"""
    from app.utils.data_loader import load_data
    await load_data()
    logger.info("Application started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_refactored:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
