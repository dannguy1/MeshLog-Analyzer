# prplOS LCM Log Analysis System - Main FastAPI Application

import json
import os
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

# File locking for cross-machine consistency (fcntl on Linux, available on Unix)
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False  # Windows doesn't have fcntl
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from fastapi.websockets import WebSocket, WebSocketDisconnect
import uvicorn
from app.websocket_manager import manager
from app.services.project_analysis_manager import ProjectAnalysisManager
from app.services.redis_manager import redis_manager

# Import our new middleware and monitoring
from app.middleware.validation import (
    ProjectCreateRequest, AnalysisRequest, FileUploadValidator, 
    RequestValidator, validate_request_size, validate_rate_limit_headers
)
from app.middleware.auth import (
    get_current_user, verify_api_key, require_admin, SecurityHeaders, 
    log_security_event, auth_manager
)
from app.monitoring.metrics import (
    metrics_collector, health_checker, RequestMetricsMiddleware
)

# Configure logging
from app.core.config import get_settings
settings = get_settings()

# Create logs directory in DATA_DIR
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

# Import models and components
from app.models.core import Project, Analysis, PackageStructure, LogEntry, LogLevel
from app.processors.package_processor import PackageProcessor
from app.analytics.analysis_engine import AnalysisEngine
from app.reporting.report_generator import ReportGenerator
from app.api.visualization import router as visualization_router

# Initialize components
package_processor = PackageProcessor()
analysis_engine = AnalysisEngine()
report_generator = ReportGenerator()

# Temporary in-memory storage for backwards compatibility
# TODO: Replace with ProjectAnalysisManager throughout the codebase
analyses_db: Dict[str, Analysis] = {}

# In-memory storage (will be replaced with database)
projects_db: Dict[str, Project] = {}
# Note: analyses_db removed - now using project-scoped analysis management

# File-based persistence - use configured data directory
PROJECTS_FILE = os.path.join(settings.DATA_DIR, "projects.json")
ANALYSES_FILE = os.path.join(settings.DATA_DIR, "analyses.json")

def load_data():
    """Load data from files with path normalization for cross-machine compatibility"""
    try:
        if os.path.exists(PROJECTS_FILE):
            # Load original projects data for comparison
            with open(PROJECTS_FILE, 'r') as f:
                original_projects_data = json.load(f)
            
            projects_data = original_projects_data.copy()  # Work with a copy
            paths_normalized = False
            
            for project_id, project_dict in projects_data.items():
                # Normalize paths based on current DATA_DIR (fixes cross-machine issues)
                stored_project_root = project_dict.get("project_root_path", "")
                expected_project_root = os.path.join(settings.DATA_DIR, "projects", project_id)
                
                # Update paths if they don't match current DATA_DIR
                if stored_project_root and stored_project_root != expected_project_root:
                    # Check if stored path exists
                    if not os.path.exists(stored_project_root):
                        # Stored path doesn't exist, use expected path based on current DATA_DIR
                        logger.info(f"Normalizing paths for project {project_id}: stored path doesn't exist, using current DATA_DIR")
                        paths_normalized = True
                        project_dict["project_root_path"] = expected_project_root
                        
                        # Update related paths
                        if project_dict.get("extraction_path"):
                            old_extraction = project_dict["extraction_path"]
                            if old_extraction.startswith(stored_project_root):
                                # Rebuild relative to new project root
                                relative_part = os.path.relpath(old_extraction, stored_project_root)
                                project_dict["extraction_path"] = os.path.join(expected_project_root, relative_part)
                            else:
                                # Try standard location
                                project_dict["extraction_path"] = os.path.join(expected_project_root, "extracted")
                        
                        if project_dict.get("extraction_metadata_path"):
                            old_metadata = project_dict["extraction_metadata_path"]
                            if old_metadata.startswith(stored_project_root):
                                relative_part = os.path.relpath(old_metadata, stored_project_root)
                                project_dict["extraction_metadata_path"] = os.path.join(expected_project_root, relative_part)
                            else:
                                project_dict["extraction_metadata_path"] = os.path.join(expected_project_root, "extracted", "metadata")
                
                project = Project(
                    id=UUID(project_id),
                    name=project_dict["name"],
                    description=project_dict.get("description"),
                    original_filename=project_dict["original_filename"],
                    file_size_bytes=project_dict["file_size_bytes"],
                    upload_timestamp=datetime.fromisoformat(project_dict["upload_timestamp"]),
                    extraction_path=project_dict["extraction_path"],
                    status=project_dict["status"],
                    created_by=project_dict.get("created_by"),
                    last_modified=datetime.fromisoformat(project_dict["last_modified"]),
                    analysis_count=project_dict["analysis_count"],
                    last_analysis_timestamp=datetime.fromisoformat(project_dict["last_analysis_timestamp"]) if project_dict.get("last_analysis_timestamp") else None,
                    extraction_metadata_path=project_dict.get("extraction_metadata_path"),
                    project_root_path=project_dict.get("project_root_path", ""),
                    package_structure_metadata=project_dict.get("package_structure_metadata"),
                    application_discovery_metadata=project_dict.get("application_discovery_metadata")
                )
                projects_db[project_id] = project
            
            logger.info(f"Loaded {len(projects_db)} projects from file")
            
            # Save normalized paths back if any changes were made
            if paths_normalized:
                logger.info("Saving normalized project paths back to projects.json")
                save_data()
    except Exception as e:
        logger.error(f"Failed to load projects: {e}")

    # Note: Analyses are now loaded per-project when needed
    logger.info("Data loading completed - using project-scoped analysis management")

def save_data(allow_empty=False):
    """Save data to files with atomic operations and backup
    
    Args:
        allow_empty: If True, allows saving empty projects_db even when existing file has data
    """
    try:
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        
        # Save projects
        projects_data = {}
        for project_id, project in projects_db.items():
            # Handle both Project objects and dictionaries with better type checking
            logger.debug(f"Processing project {project_id}, type: {type(project)}, hasattr to_dict: {hasattr(project, 'to_dict')}")
            
            if hasattr(project, 'to_dict') and callable(getattr(project, 'to_dict', None)):
                # Project object - convert to dict
                try:
                    projects_data[project_id] = project.to_dict()
                except Exception as e:
                    logger.error(f"Failed to convert project {project_id} to dict: {e}")
                    logger.error(f"Project type: {type(project)}, project: {project}")
                    # Try to save as dict if it's already a dict-like object
                    if isinstance(project, dict):
                        projects_data[project_id] = project
                    continue
            elif isinstance(project, dict):
                # Already a dictionary - use as is
                projects_data[project_id] = project
            else:
                logger.error(f"Project {project_id} is not a Project object or dict: {type(project)}")
                continue
        
        # DEFENSIVE CHECK: Don't save empty project data unless it's intentional
        # This prevents data loss due to race conditions during module reloading
        if len(projects_data) == 0 and not allow_empty and os.path.exists(PROJECTS_FILE):
            # Check if the existing file has data
            try:
                with open(PROJECTS_FILE, 'r') as f:
                    existing_data = json.load(f)
                if len(existing_data) > 0:
                    logger.warning("🛡️  DEFENSIVE SAVE PROTECTION ACTIVATED")
                    logger.warning("Refusing to save empty projects_db over existing data with projects")
                    logger.warning("This likely indicates a race condition during module reload")
                    logger.warning(f"Existing file has {len(existing_data)} projects, in-memory has {len(projects_db)} projects")
                    return
            except (json.JSONDecodeError, FileNotFoundError):
                # If existing file is corrupted or missing, allow empty save
                logger.info("Existing projects file is corrupted or missing, allowing empty save")
                pass
        
        # Atomic write: write to temporary file first, then rename
        temp_file = PROJECTS_FILE + '.tmp'
        backup_file = PROJECTS_FILE + '.backup'
        
        # Create backup if original exists
        if os.path.exists(PROJECTS_FILE):
            import shutil
            shutil.copy2(PROJECTS_FILE, backup_file)
        
        # Write to temporary file with explicit flushing and synchronization
        # This ensures data is fully written to disk before rename (critical for NFS/network mounts)
        with open(temp_file, 'w') as f:
            json.dump(projects_data, f, indent=2)
            f.flush()  # Flush Python's buffer to OS
            try:
                os.fsync(f.fileno())  # Force OS to write to disk (critical for cross-machine consistency)
            except OSError as e:
                # fsync may fail on some filesystems (e.g., network mounts), log but continue
                logger.debug(f"fsync failed (this is OK on some filesystems): {e}")
        
        # Verify file was written correctly before renaming
        if not os.path.exists(temp_file):
            raise Exception(f"Temporary file {temp_file} was not created")
        
        temp_stat = os.stat(temp_file)
        if temp_stat.st_size == 0:
            raise Exception(f"Temporary file {temp_file} is empty after write")
        
        # Atomic rename (on most filesystems, this is atomic, but ensure parent directory is synced)
        try:
            parent_dir = os.path.dirname(PROJECTS_FILE)
            if parent_dir:
                parent_fd = os.open(parent_dir, os.O_RDONLY)
                try:
                    os.fsync(parent_fd)  # Sync directory metadata (ensures rename is visible)
                finally:
                    os.close(parent_fd)
        except Exception as e:
            logger.debug(f"Could not sync parent directory: {e}")
        
        os.rename(temp_file, PROJECTS_FILE)
        
        # Final sync to ensure rename is visible to all readers
        try:
            final_fd = os.open(PROJECTS_FILE, os.O_RDONLY)
            try:
                os.fsync(final_fd)
            finally:
                os.close(final_fd)
        except Exception as e:
            logger.debug(f"Could not sync final file: {e}")
            
        logger.info(f"Saved {len(projects_db)} projects to file (atomic operation with fsync)")
    except Exception as e:
        logger.error(f"Failed to save data: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up temporary file if it exists
        temp_file = PROJECTS_FILE + '.tmp'
        if os.path.exists(temp_file):
            os.remove(temp_file)

def validate_data_consistency():
    """Validate consistency between projects_db and filesystem"""
    try:
        logger.info("Validating data consistency...")
        
        # Check if projects.json exists and is readable
        if not os.path.exists(PROJECTS_FILE):
            logger.warning("projects.json file does not exist")
            return False
        
        # Load projects from file
        with open(PROJECTS_FILE, 'r') as f:
            file_projects = json.load(f)
        
        # Compare with in-memory database
        memory_count = len(projects_db)
        file_count = len(file_projects)
        
        if memory_count != file_count:
            logger.warning(f"Data inconsistency detected: memory={memory_count}, file={file_count}")
            return False
        
        # Check if all projects in memory exist in file
        for project_id in projects_db:
            if project_id not in file_projects:
                logger.warning(f"Project {project_id} exists in memory but not in file")
                return False
        
        # Check if all projects in file exist in memory
        for project_id in file_projects:
            if project_id not in projects_db:
                logger.warning(f"Project {project_id} exists in file but not in memory")
                return False
        
        logger.info("Data consistency validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Data consistency validation failed: {e}")
        return False

def recover_orphaned_projects():
    """Recover projects that exist in one storage system but not others"""
    try:
        logger.info("Starting orphaned project recovery...")
        
        # Check if projects.json exists
        if not os.path.exists(PROJECTS_FILE):
            logger.warning("projects.json file does not exist, cannot recover")
            return 0
        
        # Load projects from file
        with open(PROJECTS_FILE, 'r') as f:
            file_projects = json.load(f)
        
        recovered_count = 0
        
        # Find projects in file but not in memory
        for project_id, project_dict in file_projects.items():
            if project_id not in projects_db:
                try:
                    # Reconstruct project object
                    project = Project(
                        id=UUID(project_id),
                        name=project_dict["name"],
                        description=project_dict.get("description"),
                        original_filename=project_dict["original_filename"],
                        file_size_bytes=project_dict["file_size_bytes"],
                        upload_timestamp=datetime.fromisoformat(project_dict["upload_timestamp"]),
                        extraction_path=project_dict["extraction_path"],
                        status=project_dict["status"],
                        created_by=project_dict.get("created_by"),
                        last_modified=datetime.fromisoformat(project_dict["last_modified"]),
                        analysis_count=project_dict["analysis_count"],
                        last_analysis_timestamp=datetime.fromisoformat(project_dict["last_analysis_timestamp"]) if project_dict.get("last_analysis_timestamp") else None,
                        extraction_metadata_path=project_dict.get("extraction_metadata_path"),
                        project_root_path=project_dict.get("project_root_path", ""),
                        package_structure_metadata=project_dict.get("package_structure_metadata"),
                        application_discovery_metadata=project_dict.get("application_discovery_metadata")
                    )
                    projects_db[project_id] = project
                    recovered_count += 1
                    logger.info(f"Recovered project {project_id} from file to memory")
                except Exception as e:
                    logger.error(f"Failed to recover project {project_id}: {e}")
        
        logger.info(f"Recovered {recovered_count} orphaned projects")
        return recovered_count
        
    except Exception as e:
        logger.error(f"Orphaned project recovery failed: {e}")
        return 0

def load_package_structure_metadata(project_id: str):
    """Load package structure metadata for project"""
    try:
        # Use configured DATA_DIR instead of hardcoded path
        settings = get_settings()
        metadata_path = os.path.join(
            settings.DATA_DIR, "projects", project_id, "extracted", "metadata", "package_structure.json"
        )
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                data = json.load(f)
            
            # Convert datetime string to datetime object
            if 'extraction_timestamp' in data and isinstance(data['extraction_timestamp'], str):
                from datetime import datetime
                data['extraction_timestamp'] = datetime.fromisoformat(data['extraction_timestamp'])
            
            from app.models.core import PackageStructureMetadata
            return PackageStructureMetadata(**data)
    except Exception as e:
        logger.warning(f"Failed to load package structure metadata: {e}")
        import traceback
        traceback.print_exc()
    return None

def load_application_discovery_metadata(project_id: str):
    """Load application discovery metadata for project"""
    try:
        # Use configured DATA_DIR instead of hardcoded path
        settings = get_settings()
        metadata_path = os.path.join(
            settings.DATA_DIR, "projects", project_id, "extracted", "metadata", "application_discovery.json"
        )
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                data = json.load(f)
            
            # Convert datetime string to datetime object
            if 'discovery_timestamp' in data and isinstance(data['discovery_timestamp'], str):
                from datetime import datetime
                data['discovery_timestamp'] = datetime.fromisoformat(data['discovery_timestamp'])
            
            from app.models.core import ApplicationDiscoveryMetadata, ApplicationDiscoveryResult
            # Convert applications data back to objects
            applications = [ApplicationDiscoveryResult(**app) for app in data.get("applications", [])]
            data["applications"] = applications
            return ApplicationDiscoveryMetadata(**data)
    except Exception as e:
        logger.warning(f"Failed to load application discovery metadata: {e}")
        import traceback
        traceback.print_exc()
    return None

def cleanup_project_files(project):
    """Clean up all files associated with a project (project-centric approach)"""
    try:
        # Clean up uploaded file using configured DATA_DIR
        if project.original_filename:
            from app.core.config import get_settings
            settings = get_settings()
            upload_dir = os.path.join(settings.DATA_DIR, settings.UPLOAD_DIR)
            upload_path = os.path.join(upload_dir, project.original_filename)
            if os.path.exists(upload_path):
                os.remove(upload_path)
                logger.info(f"Deleted uploaded file: {upload_path}")
        
        # Clean up entire project directory (contains all project data)
        from app.core.config import get_data_dir
        data_dir = os.path.abspath(get_data_dir())
        project_dir = os.path.join(data_dir, "projects", str(project.id))
        if os.path.exists(project_dir):
            import shutil
            shutil.rmtree(project_dir)
            logger.info(f"Deleted project directory: {project_dir}")
            
    except Exception as e:
        logger.error(f"Failed to cleanup files for project {project.id}: {e}")

def clear_all_project_data():
    """Clear all project data including uploads, extracted data, and database"""
    try:
        import shutil
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Clear uploads directory
        uploads_dir = os.path.join(settings.DATA_DIR, settings.UPLOAD_DIR)
        if os.path.exists(uploads_dir):
            shutil.rmtree(uploads_dir)
            os.makedirs(uploads_dir, exist_ok=True)
            logger.info("Cleared uploads directory")
        
        # Clear extracted data directory
        # Clean up old extraction directories if they exist
        extracted_dir = os.path.join(settings.DATA_DIR, "extracted")
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
            logger.info("Removed old data/extracted directory")
            logger.info("Cleared extracted data directory")
        
        # Clear analysis results directory
        analysis_dir = os.path.join(settings.DATA_DIR, settings.ANALYSIS_DIR)
        if os.path.exists(analysis_dir):
            shutil.rmtree(analysis_dir)
            os.makedirs(analysis_dir, exist_ok=True)
            logger.info("Cleared analysis results directory")
        
        # Clear database files
        if os.path.exists(PROJECTS_FILE):
            os.remove(PROJECTS_FILE)
            logger.info("Cleared projects database")
        
        if os.path.exists(ANALYSES_FILE):
            os.remove(ANALYSES_FILE)
            logger.info("Cleared analyses database")
        
        # Clear in-memory databases
        projects_db.clear()
        analyses_db.clear()
        
        logger.info("All project data cleared successfully")
        
    except Exception as e:
        logger.error(f"Failed to clear project data: {e}")

# Load data on startup
load_data()

# Validate data consistency on startup
if not validate_data_consistency():
    logger.warning("Data consistency issues detected on startup - attempting recovery")
    recovered_count = recover_orphaned_projects()
    if recovered_count > 0:
        logger.info(f"Recovered {recovered_count} orphaned projects")
        # Re-validate after recovery
        if validate_data_consistency():
            logger.info("Data consistency restored after recovery")
        else:
            logger.error("Data consistency issues persist after recovery")
    else:
        logger.error("No projects could be recovered")

# Create FastAPI app
app = FastAPI(
    title="prplOS LCM Log Analysis System",
    version="1.0.0",
    description="A comprehensive log analysis platform for prplOS LCM applications",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware with dynamic origin support
# Allow common development origins and any origin that matches the frontend hostname pattern
cors_origins = settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
    "http://192.168.10.5:3000",
    # Allow any IP-based origin for cross-machine development access
    "http://192.168.*.*:3000",  # Pattern matching (if supported)
]

# In development, allow all origins for cross-machine access
# In production, use configured CORS_ORIGINS
if settings.ENVIRONMENT == "development" or settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development for cross-machine access
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add security and monitoring middleware
# app.add_middleware(RequestMetricsMiddleware, metrics_collector)

# Add request size validation
@app.middleware("http")
async def add_security_middleware(request: Request, call_next):
    # Validate request size
    await validate_request_size(request)
    
    # Check rate limiting
    validate_rate_limit_headers(request)
    
    # Process request
    response = await call_next(request)
    
    # Add security headers
    response = SecurityHeaders.add_security_headers(response)
    
    return response

# Include routers
app.include_router(visualization_router, prefix="/api/v1")

# Include application data API
from app.api.v1.application_data import router as application_data_router
app.include_router(application_data_router)

# Include agent analysis API
from app.api.v1.agent_analysis import router as agent_analysis_router
app.include_router(agent_analysis_router)

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Starting prplOS LCM Log Analysis System")
    logger.info("Configuration: prplOS LCM Log Analysis System v1.0.0")
    logger.info("Debug mode: False")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Shutting down prplOS LCM Log Analysis System")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "prplOS LCM Log Analysis System",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    try:
        system_health = metrics_collector.get_system_health()
        health_checks = await health_checker.run_checks()
        
        overall_status = "healthy"
        if system_health.status in ["critical", "warning"]:
            overall_status = system_health.status
        elif any(check["status"] != "healthy" for check in health_checks.values()):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "system": system_health.to_dict(),
            "checks": health_checks,
            "authentication": {
                "enabled": auth_manager.enabled,
                "type": "basic_auth" if auth_manager.enabled else "disabled"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics_collector.get_metrics_summary(),
            "system_health": metrics_collector.get_system_health().to_dict()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

def _validate_project_name(name: str) -> None:
    """Validate project name"""
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Project name is required")
    
    # Allow duplicate project names since project IDs are unique
    # Users can have multiple projects with the same name if they want

def _validate_package_file(filename: str, file_size: int) -> None:
    """Validate package file format and size"""
    if not filename.endswith(('.tar', '.tar.gz', '.tgz')):
        raise HTTPException(status_code=400, detail="Only tarball files are supported")
    
    # Get file size limit from configuration
    settings = get_settings()
    max_size = settings.MAX_FILE_SIZE
    
    if file_size > max_size:
        raise HTTPException(status_code=400, detail=f"File size ({file_size} bytes) exceeds maximum limit ({max_size} bytes)")

def _create_project_record(name: str, description: Optional[str], filename: str, file_size: int, status: str) -> Project:
    """Create a project record with consistent settings"""
    settings = get_settings()
    
    project = Project(
        name=name.strip(),
        description=description.strip() if description else None,
        original_filename=filename,
        file_size_bytes=file_size,
        extraction_path="",  # Will be set during background processing
        status=status
    )
    
    # Set absolute project root path using configured DATA_DIR
    project.project_root_path = os.path.join(settings.DATA_DIR, "projects", str(project.id))
    
    return project

def _save_and_process_project(project: Project, package_path: str, background_tasks: BackgroundTasks, description: Optional[str]) -> dict:
    """Save project and start background processing with proper transaction management"""
    project_id = str(project.id)
    
    try:
        # Step 1: Add project to in-memory database
        projects_db[project_id] = project
        logger.info(f"Added project {project_id} to in-memory database")
        
        # Step 2: Persist to JSON file with atomic operation
        save_data()
        logger.info(f"Persisted project {project_id} to JSON file")
        
        # Step 3: Verify project was saved correctly
        if project_id not in projects_db:
            raise Exception(f"Project {project_id} not found in memory after save")
        
        # Step 4: Schedule background processing
        background_tasks.add_task(process_package_background, package_path, project_id, description)
        logger.info(f"Scheduled background processing for project {project_id}")
        
        # Step 5: Return success response
        return {
            "id": project_id,
            "project_id": project_id,  # Keep for frontend compatibility
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.upload_timestamp.isoformat() if project.upload_timestamp else None,
            "file_size": project.file_size_bytes,  # Frontend expects file_size
            "file_size_bytes": project.file_size_bytes,  # Keep for compatibility
            "original_filename": project.original_filename,
            "message": f"Project {project.status} started successfully"
        }
        
    except Exception as e:
        # Rollback: Remove project from memory if it was added
        if project_id in projects_db:
            del projects_db[project_id]
            logger.error(f"Rolled back project {project_id} from memory due to error: {e}")
        
        # Rollback: Remove uploaded file if it exists
        if os.path.exists(package_path):
            try:
                os.remove(package_path)
                logger.info(f"Cleaned up uploaded file: {package_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup uploaded file {package_path}: {cleanup_error}")
        
        # Re-raise the exception
        raise e

@app.post("/api/v1/projects")
async def create_project(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: str = Depends(get_current_user)
):
    """Create a new project with uploaded package"""
    try:
        logger.info(f"Creating project: {name} (user: {current_user})")
        
        # Validate inputs using new validation system
        project_request = ProjectCreateRequest(name=name, description=description)
        FileUploadValidator.validate_file(file.filename, file.size or 0)
        
        # Read file content to get accurate size
        content = await file.read()
        actual_size = len(content)
        
        # Re-validate with actual size
        FileUploadValidator.validate_file(file.filename, actual_size)
        
        logger.info(f"File validation passed: filename={file.filename}, size={actual_size}")
        
        # Record metric
        metrics_collector.record_metric("project_creation", 1, {"user": current_user})
        max_size = settings.MAX_FILE_SIZE
        if actual_size > max_size:
            logger.error(f"File size validation failed: {actual_size} > {max_size}")
            raise HTTPException(status_code=400, detail=f"File size ({actual_size} bytes) exceeds maximum limit ({max_size} bytes)")
        
        # Save uploaded file using configured DATA_DIR
        upload_dir = os.path.join(settings.DATA_DIR, settings.UPLOAD_DIR)
        os.makedirs(upload_dir, exist_ok=True)
        upload_path = os.path.join(upload_dir, file.filename)
        with open(upload_path, "wb") as buffer:
            buffer.write(content)
        
        # Create project record
        project = _create_project_record(name, description, file.filename, actual_size, "processing")
        
        # Save and process
        return _save_and_process_project(project, upload_path, background_tasks, description)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_package_background(package_path: str, project_id: str, description: Optional[str]):
    """Background task to process package with robust error handling and recovery"""
    project = None
    try:
        logger.info(f"Processing package in background: {package_path} for project: {project_id}")
        
        # Find project by ID (more reliable than name)
        if project_id not in projects_db:
            logger.error(f"Project not found in memory: {project_id}")
            # Try to recover from JSON file
            try:
                if os.path.exists(PROJECTS_FILE):
                    with open(PROJECTS_FILE, 'r') as f:
                        projects_data = json.load(f)
                        if project_id in projects_data:
                            logger.info(f"Recovered project {project_id} from JSON file")
                            # Reconstruct project object
                            project_dict = projects_data[project_id]
                            project = Project(
                                id=UUID(project_id),
                                name=project_dict["name"],
                                description=project_dict.get("description"),
                                original_filename=project_dict["original_filename"],
                                file_size_bytes=project_dict["file_size_bytes"],
                                upload_timestamp=datetime.fromisoformat(project_dict["upload_timestamp"]),
                                extraction_path=project_dict["extraction_path"],
                                status=project_dict["status"],
                                created_by=project_dict.get("created_by"),
                                last_modified=datetime.fromisoformat(project_dict["last_modified"]),
                                analysis_count=project_dict["analysis_count"],
                                last_analysis_timestamp=datetime.fromisoformat(project_dict["last_analysis_timestamp"]) if project_dict.get("last_analysis_timestamp") else None,
                                extraction_metadata_path=project_dict.get("extraction_metadata_path"),
                                project_root_path=project_dict.get("project_root_path", ""),
                                package_structure_metadata=project_dict.get("package_structure_metadata"),
                                application_discovery_metadata=project_dict.get("application_discovery_metadata")
                            )
                            projects_db[project_id] = project
                        else:
                            logger.error(f"Project {project_id} not found in JSON file either")
                            return
# FIXME:                     else:
                        logger.error(f"Project {project_id} not found in JSON file")
                        return
            except Exception as recovery_error:
                logger.error(f"Failed to recover project {project_id}: {recovery_error}")
                return
        else:
            project = projects_db[project_id]
        
        logger.info(f"Processing project: {project.name} (ID: {project_id})")
        
        # Update project status to processing
        project.status = "processing"
        project.last_modified = datetime.now()
        save_data()  # Save immediately to persist processing state
        
        # Process package with project-based extraction
        package_structure = package_processor.process_package(
            package_path=package_path,
            project_id=project_id,
            reuse_extraction=False  # Force new extraction for initial processing
        )
        
        # Update project status and extraction path
        project.status = "completed" if package_structure.is_valid else "failed"
        project.extraction_path = package_structure.metadata.extraction_path
        
        # Set extraction metadata path
        project.extraction_metadata_path = os.path.join(project.extraction_path, "metadata")
        
        # Load metadata for future use
        project.package_structure_metadata = load_package_structure_metadata(project_id)
        project.application_discovery_metadata = load_application_discovery_metadata(project_id)
        
        logger.info(f"Updated project {project_id} with extraction path: {project.extraction_path}")
        
        # Parse logs and store in SQLite using ApplicationDataManager
        if package_structure.is_valid:
            logger.info(f"Parsing logs and storing in SQLite for project: {project.name}")
            try:
                app_logs = await parse_logs_from_package(package_structure)
                logger.info(f"Successfully stored logs in SQLite for {len(app_logs)} applications")
            except Exception as e:
                logger.error(f"Failed to parse logs and store in SQLite: {e}")
                import traceback
                traceback.print_exc()
                # Don't fail the entire project for SQLite parsing errors
        
        # Save to file - CRITICAL: Always save regardless of processing outcome
        save_data()
        
        logger.info(f"Package processing completed for project: {project.name} (ID: {project_id})")
        
    except Exception as e:
        logger.error(f"Background processing failed for project {project_id}: {e}")
        import traceback
        traceback.print_exc()
        
        # CRITICAL: Always update project status and save, even on failure
        try:
            if project_id in projects_db:
                project = projects_db[project_id]
                project.status = "failed"
                project.last_modified = datetime.now()
                save_data()
                logger.info(f"Project {project_id} marked as failed and saved to database")
            else:
                logger.error(f"Project {project_id} not found in database during error handling")
                # Try to create a minimal project record for failed projects
                try:
                    failed_project = Project(
                        id=UUID(project_id),
                        name=f"Failed Project {project_id[:8]}",
                        description="Project failed during processing",
                        original_filename="unknown",
                        file_size_bytes=0,
                        status="failed"
                    )
                    projects_db[project_id] = failed_project
                    save_data()
                    logger.info(f"Created minimal project record for failed project {project_id}")
                except Exception as create_error:
                    logger.error(f"Failed to create minimal project record: {create_error}")
        except Exception as save_error:
            logger.error(f"Failed to save project status during error handling: {save_error}")
        
        # Clean up uploaded file on failure
        try:
            if os.path.exists(package_path):
                os.remove(package_path)
                logger.info(f"Cleaned up uploaded file after failure: {package_path}")
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup uploaded file: {cleanup_error}")

@app.post("/api/v1/admin/recover-projects")
async def recover_projects():
    """Recover missing projects from filesystem"""
    try:
        logger.info("Starting manual project recovery...")
        
        # Run the recovery script logic
        recovered_count = 0
        projects_dir = os.path.join(settings.DATA_DIR, "projects")
        
        if os.path.exists(projects_dir):
            for project_dir in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, project_dir)
                if os.path.isdir(project_path):
                    project_id = project_dir
                    
                    # Check if project exists in database
                    if project_id not in projects_db:
                        # Try to recover project metadata
                        metadata_dir = os.path.join(project_path, "extracted", "metadata")
                        package_structure_file = os.path.join(metadata_dir, "package_structure.json")
                        
                        if os.path.exists(package_structure_file):
                            try:
                                with open(package_structure_file, 'r') as f:
                                    package_metadata = json.load(f)
                                
                                # Create basic project entry
                                project_entry = {
                                    "id": project_id,
                                    "name": package_metadata.get("original_filename", f"Project-{project_id[:8]}"),
                                    "description": f"Recovered project from {package_metadata.get('original_filename', 'unknown')}",
                                    "original_filename": package_metadata.get("original_filename", "unknown"),
                                    "file_size_bytes": 0,
                                    "upload_timestamp": package_metadata.get("extraction_timestamp", datetime.now().isoformat()),
                                    "extraction_path": os.path.join(project_path, "extracted"),
                                    "status": "completed",
                                    "created_by": None,
                                    "last_modified": datetime.now().isoformat(),
                                    "analysis_count": 0,
                                    "last_analysis_timestamp": None,
                                    "extraction_metadata_path": metadata_dir,
                                    "project_root_path": project_path,
                                    "package_structure_metadata": package_metadata
                                }
                                
                                # Add to projects database
                                project = Project(
                                    id=UUID(project_id),
                                    name=project_entry["name"],
                                    description=project_entry["description"],
                                    original_filename=project_entry["original_filename"],
                                    file_size_bytes=project_entry["file_size_bytes"],
                                    upload_timestamp=datetime.fromisoformat(project_entry["upload_timestamp"]),
                                    extraction_path=project_entry["extraction_path"],
                                    status=project_entry["status"],
                                    created_by=project_entry["created_by"],
                                    last_modified=datetime.fromisoformat(project_entry["last_modified"]),
                                    analysis_count=project_entry["analysis_count"],
                                    last_analysis_timestamp=None,
                                    extraction_metadata_path=project_entry["extraction_metadata_path"],
                                    project_root_path=project_entry["project_root_path"],
                                    package_structure_metadata=PackageStructureMetadata(**package_metadata)
                                )
                                
                                projects_db[project_id] = project
                                recovered_count += 1
                                logger.info(f"Recovered project: {project_id}")
                                
                            except Exception as e:
                                logger.error(f"Failed to recover project {project_id}: {e}")
        
        # Save recovered projects
        if recovered_count > 0:
            save_data()
        
        return {
            "success": True,
            "recovered_count": recovered_count,
            "message": f"Recovered {recovered_count} projects"
        }
        
    except Exception as e:
        logger.error(f"Project recovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/validate-data-consistency")
async def validate_data_consistency_endpoint():
    """Validate data consistency between memory and file storage"""
    try:
        logger.info("Starting data consistency validation...")
        
        # Run validation
        is_consistent = validate_data_consistency()
        
        if is_consistent:
            return {
                "status": "consistent",
                "message": "Data consistency validation passed",
                "memory_projects": len(projects_db),
                "file_projects": len(projects_db) if os.path.exists(PROJECTS_FILE) else 0
            }
        else:
            # Attempt recovery
            recovered_count = recover_orphaned_projects()
            
            return {
                "status": "inconsistent",
                "message": "Data consistency issues detected and recovery attempted",
                "memory_projects": len(projects_db),
                "file_projects": len(projects_db) if os.path.exists(PROJECTS_FILE) else 0,
                "recovered_count": recovered_count,
                "recovery_successful": recovered_count > 0
            }
        
    except Exception as e:
        logger.error(f"Data consistency validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects")
async def list_projects(refresh: bool = Query(False, description="Force reload from disk")):
    """List all projects - reads from disk to ensure consistency across browsers/machines
    
    Args:
        refresh: If True, reload from disk before returning. Default False (uses current memory cache).
                 Note: For cross-machine consistency, this endpoint always reads from disk (source of truth).
    """
    try:
        # Always read from disk to ensure consistency across browsers/machines
        # projects.json is the source of truth per user's architecture design
        if os.path.exists(PROJECTS_FILE):
            # Use file locking to ensure we read a consistent state
            # Retry logic for cases where file might be mid-write
            max_retries = 3
            retry_delay = 0.1
            
            for attempt in range(max_retries):
                try:
                    with open(PROJECTS_FILE, 'r') as f:
                        # Use file locking to prevent reading during write (if supported)
                        if HAS_FCNTL:
                            try:
                                fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
                            except (AttributeError, OSError):
                                # File locking not supported on this filesystem (e.g., some NFS)
                                pass
                        
                        try:
                            projects_data = json.load(f)
                        finally:
                            if HAS_FCNTL:
                                try:
                                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock
                                except (AttributeError, OSError):
                                    pass
                        break  # Successfully read, exit retry loop
                except json.JSONDecodeError as e:
                    if attempt < max_retries - 1:
                        # File might be mid-write, wait and retry
                        logger.debug(f"JSON decode error (attempt {attempt + 1}/{max_retries}), retrying...: {e}")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        # Last attempt failed, raise error
                        logger.error(f"Failed to parse projects.json after {max_retries} attempts: {e}")
                        raise
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.debug(f"Error reading projects.json (attempt {attempt + 1}/{max_retries}), retrying...: {e}")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        logger.error(f"Failed to read projects.json after {max_retries} attempts: {e}")
                        raise
        else:
            projects_data = {}
            logger.debug("projects.json does not exist, returning empty list")
        
        projects = []
        for project_id, project_dict in projects_data.items():
            try:
                # Convert dict to Project object for consistent handling
                project = Project(
                    id=UUID(project_id),
                    name=project_dict["name"],
                    description=project_dict.get("description"),
                    original_filename=project_dict["original_filename"],
                    file_size_bytes=project_dict["file_size_bytes"],
                    upload_timestamp=datetime.fromisoformat(project_dict["upload_timestamp"]),
                    extraction_path=project_dict.get("extraction_path", ""),
                    status=project_dict["status"],
                    created_by=project_dict.get("created_by"),
                    last_modified=datetime.fromisoformat(project_dict["last_modified"]),
                    analysis_count=project_dict.get("analysis_count", 0),
                    last_analysis_timestamp=datetime.fromisoformat(project_dict["last_analysis_timestamp"]) if project_dict.get("last_analysis_timestamp") else None,
                    extraction_metadata_path=project_dict.get("extraction_metadata_path"),
                    project_root_path=project_dict.get("project_root_path", ""),
                    package_structure_metadata=project_dict.get("package_structure_metadata"),
                    application_discovery_metadata=project_dict.get("application_discovery_metadata")
                )
                
                projects.append({
                    "id": project_id,
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "created_at": project.upload_timestamp.isoformat(),
                    "file_size": project.file_size_bytes
                })
            except Exception as e:
                logger.warning(f"Failed to parse project {project_id}: {e}")
                continue
        
        # Update in-memory cache to keep it in sync (but don't block on errors)
        try:
            if refresh or len(projects) != len(projects_db):
                # Sync memory cache with disk
                load_data()
        except Exception as e:
            logger.debug(f"Could not sync memory cache: {e}")
        
        # Set cache control headers to prevent browser caching
        response = JSONResponse(content={"projects": projects})
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
        
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str, refresh: bool = Query(False, description="Force reload from disk")):
    """Get project details including package metadata - reads from disk for consistency
    
    Args:
        refresh: If True, reload from disk before returning. Default False.
    """
    try:
        # Reload from disk if refresh requested or if project not in memory
        if refresh or project_id not in projects_db:
            if os.path.exists(PROJECTS_FILE):
                with open(PROJECTS_FILE, 'r') as f:
                    projects_data = json.load(f)
                    if project_id in projects_data:
                        project_dict = projects_data[project_id]
                        project = Project(
                            id=UUID(project_id),
                            name=project_dict["name"],
                            description=project_dict.get("description"),
                            original_filename=project_dict["original_filename"],
                            file_size_bytes=project_dict["file_size_bytes"],
                            upload_timestamp=datetime.fromisoformat(project_dict["upload_timestamp"]),
                            extraction_path=project_dict.get("extraction_path", ""),
                            status=project_dict["status"],
                            created_by=project_dict.get("created_by"),
                            last_modified=datetime.fromisoformat(project_dict["last_modified"]),
                            analysis_count=project_dict.get("analysis_count", 0),
                            last_analysis_timestamp=datetime.fromisoformat(project_dict["last_analysis_timestamp"]) if project_dict.get("last_analysis_timestamp") else None,
                            extraction_metadata_path=project_dict.get("extraction_metadata_path"),
                            project_root_path=project_dict.get("project_root_path", ""),
                            package_structure_metadata=project_dict.get("package_structure_metadata"),
                            application_discovery_metadata=project_dict.get("application_discovery_metadata")
                        )
                        projects_db[project_id] = project
        
        if project_id not in projects_db:
            logger.warning(f"Project not found: {project_id}")
            logger.info(f"Available projects: {list(projects_db.keys())}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        print(f"DEBUG: Project from projects_db: {project.name}")
        print(f"DEBUG: Project extraction_metadata_path: {project.extraction_metadata_path}")
        
        # Get package structure if available
        package_metadata = None
        applications_detected = []
        
        print(f"DEBUG: extraction_metadata_path = {project.extraction_metadata_path}")
        
        # First check for embedded metadata in the project object
        if project.package_structure_metadata:
            print(f"DEBUG: Using embedded package structure metadata")
            # Handle both dict and object formats
            if isinstance(project.package_structure_metadata, dict):
                package_metadata = {
                    "total_containers": project.package_structure_metadata["total_containers"],
                    "total_log_files": project.package_structure_metadata["total_log_files"],
                    "total_log_size_bytes": project.package_structure_metadata["total_log_size_bytes"],
                    "applications_detected": project.package_structure_metadata["applications_detected"]
                }
            else:
                package_metadata = {
                    "total_containers": project.package_structure_metadata.total_containers,
                    "total_log_files": project.package_structure_metadata.total_log_files,
                    "total_log_size_bytes": project.package_structure_metadata.total_log_size_bytes,
                    "applications_detected": project.package_structure_metadata.applications_detected
                }
        
        if project.application_discovery_metadata:
            print(f"DEBUG: Using embedded application discovery metadata")
            # Handle both dict and object formats
            if isinstance(project.application_discovery_metadata, dict):
                print(f"DEBUG: application_discovery_metadata.applications count: {len(project.application_discovery_metadata['applications'])}")
                applications_detected = [app["application_name"] for app in project.application_discovery_metadata["applications"]]
            else:
                print(f"DEBUG: application_discovery_metadata.applications count: {len(project.application_discovery_metadata.applications)}")
                applications_detected = [app.application_name for app in project.application_discovery_metadata.applications]
            print(f"DEBUG: applications_detected: {applications_detected}")
        
        # If no embedded metadata, try loading from files
        print(f"DEBUG: package_metadata: {package_metadata}")
        print(f"DEBUG: applications_detected: {applications_detected}")
        if not package_metadata or not applications_detected:
            print(f"DEBUG: No embedded metadata found, trying file-based loading")
            
            # Handle both relative and absolute paths
            metadata_path = None
            if project.extraction_metadata_path:
                # Try the path as-is first
                if os.path.exists(project.extraction_metadata_path):
                    metadata_path = project.extraction_metadata_path
                    print(f"DEBUG: Using relative path: {metadata_path}")
                else:
                    # Try absolute path
                    abs_path = os.path.abspath(project.extraction_metadata_path)
                    if os.path.exists(abs_path):
                        metadata_path = abs_path
                        print(f"DEBUG: Using absolute path: {metadata_path}")
                    else:
                        print(f"DEBUG: Path does not exist: {project.extraction_metadata_path} or {abs_path}")
            
            if metadata_path:
                try:
                    print(f"DEBUG: Loading metadata for project {project_id}")
                    print(f"DEBUG: Extraction metadata path: {project.extraction_metadata_path}")
                    
                    # Load package structure metadata
                    package_structure_metadata = load_package_structure_metadata(project_id)
                    if package_structure_metadata:
                        print(f"DEBUG: Package structure metadata loaded: {len(package_structure_metadata.applications_detected)} applications")
                        package_metadata = {
                            "total_containers": package_structure_metadata.total_containers,
                            "total_log_files": package_structure_metadata.total_log_files,
                            "total_log_size_bytes": package_structure_metadata.total_log_size_bytes,
                            "applications_detected": package_structure_metadata.applications_detected
                        }
                    else:
                        print(f"DEBUG: Package structure metadata not loaded for project {project_id}")
                    
                    # Load application discovery metadata
                    application_discovery_metadata = load_application_discovery_metadata(project_id)
                    if application_discovery_metadata:
                        print(f"DEBUG: Application discovery metadata loaded: {len(application_discovery_metadata.applications)} applications")
                        applications_detected = [app.application_name for app in application_discovery_metadata.applications]
                    else:
                        print(f"DEBUG: Application discovery metadata not loaded for project {project_id}")
                        
                except Exception as e:
                    logger.warning(f"Failed to get package metadata for project {project_id}: {e}")
                    import traceback
                    traceback.print_exc()
        
        response_data = {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "original_filename": project.original_filename,
            "file_size": project.file_size_bytes,  # Frontend expects file_size
            "file_size_bytes": project.file_size_bytes,  # Keep for compatibility
            "upload_timestamp": project.upload_timestamp.isoformat(),
            "extraction_path": project.extraction_path,
            "analysis_count": project.analysis_count,
            "last_analysis_timestamp": project.last_analysis_timestamp.isoformat() if project.last_analysis_timestamp else None,
            "package_metadata": package_metadata,
            "applications_detected": applications_detected
        }
        
        # Set cache control headers to prevent browser caching
        response = JSONResponse(content=response_data)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/clear-all-data")
async def clear_all_data():
    """Clear all project data including uploads, extracted data, and database"""
    try:
        clear_all_project_data()
        return {
            "message": "All project data cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to clear all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project and all its associated analyses"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get the project to check if it's safe to delete
        project = projects_db[project_id]
        
        # Check if there are any running analyses using project-scoped analysis manager
        from app.core.config import get_data_dir
        data_dir = os.path.abspath(get_data_dir())
        project_analysis_manager = ProjectAnalysisManager(data_dir, project_id)
        project_analyses = project_analysis_manager.list_analyses()
        
        # Only block on analyses that are actually running (not stuck)
        # Stuck analyses with no started_timestamp should be allowed to be deleted
        running_analyses = [
            a for a in project_analyses 
            if a.status in ["running"] and a.started_timestamp is not None
        ]
        
        if running_analyses:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete project with running analyses. Please wait for analyses to complete."
            )
        
        # Delete all analyses for this project (this is redundant since we'll delete the whole project dir)
        # for analysis in project_analyses:
        #     project_analysis_manager.delete_analysis(str(analysis.id))
        
        # Clean up project directory (contains all project data)
        cleanup_project_files(project)
        
        # Delete the project from global database
        del projects_db[project_id]
        
        # Save changes to file
        save_data()
        
        logger.info(f"Deleted project {project_id} and {len(project_analyses)} associated analyses")
        
        return {
            "message": "Project deleted successfully",
            "project_id": project_id,
            "deleted_analyses_count": len(project_analyses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects/restore/available")
async def list_available_packages():
    """List all available packages in UPLOAD_DIR that can be used for restoration"""
    try:
        from app.core.config import get_settings
        settings = get_settings()
        upload_dir = os.path.join(settings.DATA_DIR, settings.UPLOAD_DIR)
        
        if not os.path.exists(upload_dir):
            return {"packages": []}
        
        packages = []
        for filename in os.listdir(upload_dir):
            if filename.endswith(('.tar', '.tar.gz', '.tgz')):
                file_path = os.path.join(upload_dir, filename)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                
                packages.append({
                    "filename": filename,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "uploaded_at": datetime.fromtimestamp(file_mtime).isoformat(),
                    "path": file_path
                })
        
        # Sort by upload time (newest first)
        packages.sort(key=lambda x: x["uploaded_at"], reverse=True)
        
        return {"packages": packages}
        
    except Exception as e:
        logger.error(f"Failed to list available packages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/projects/restore")
async def restore_project_from_package(
    background_tasks: BackgroundTasks,
    filename: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Restore a project from a previously uploaded package"""
    try:
        logger.info(f"Restoring project from package: {filename}")
        
        # Validate inputs
        _validate_project_name(name)
        
        # Check if package exists in UPLOAD_DIR
        settings = get_settings()
        upload_dir = os.path.join(settings.DATA_DIR, settings.UPLOAD_DIR)
        package_path = os.path.join(upload_dir, filename)
        
        if not os.path.exists(package_path):
            raise HTTPException(status_code=404, detail=f"Package not found: {filename}")
        
        # Get file size and validate
        file_size = os.path.getsize(package_path)
        _validate_package_file(filename, file_size)
        
        # Create project record with consistent description handling
        project_description = description.strip() if description else f"Restored from {filename}"
        project = _create_project_record(name, project_description, filename, file_size, "restoring")
        
        # Save and process
        return _save_and_process_project(project, package_path, background_tasks, project_description)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restore project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/projects/{project_id}/analyze")
async def start_analysis(
    project_id: str,
    background_tasks: BackgroundTasks,
    config: Optional[Dict[str, Any]] = None
):
    """Start analysis for a project"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        if project.status != "completed":
            raise HTTPException(status_code=400, detail="Project not ready for analysis")
        
        # Create analysis record
        analysis = Analysis(
            project_id=project_id,
            configuration=config or {
                "time_series_analysis": True,
                "anomaly_detection": True,
                "pattern_recognition": True,
                "correlation_analysis": True,
                "applications": [
                    "wnc-steer",
                    "wnc-acs", 
                    "wnc-tpyopt",
                    "otbr-agent"
                ]
            },
            status="queued"
        )
        
        # Store analysis using ProjectAnalysisManager
        from app.core.config import get_data_dir
        data_dir = os.path.abspath(get_data_dir())
        project_manager = ProjectAnalysisManager(data_dir, project_id)
        project_manager.save_analysis(analysis)
        
        # Also add to in-memory storage for background task compatibility
        analyses_db[str(analysis.id)] = analysis
        
        # Start analysis in background
        background_tasks.add_task(run_analysis_background, str(analysis.id), project_id)
        
        return {
            "analysis_id": str(analysis.id),
            "project_id": project_id,
            "status": analysis.status,
            "message": "Analysis started"
        }
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/projects/{project_id}/analyze/{application_name}")
async def start_application_analysis(
    project_id: str,
    application_name: str,
    background_tasks: BackgroundTasks,
    config: Optional[Dict[str, Any]] = None
):
    """Start analysis for a specific application"""
    try:
        logger.info(f"Starting application analysis: project_id={project_id}, application_name={application_name}")
        
        if project_id not in projects_db:
            logger.error(f"Project not found: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        if project.status != "completed":
            logger.error(f"Project not ready for analysis: {project_id} (status: {project.status})")
            raise HTTPException(status_code=400, detail="Project not ready for analysis")
        
        # Validate application name
        supported_applications = ["wnc-steer", "wnc-acs", "wnc-tpyopt", "otbr-agent"]
        if application_name not in supported_applications:
            logger.error(f"Unsupported application: {application_name}")
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported application: {application_name}. Supported: {supported_applications}"
            )
        
        # Get applications_detected from project object (preferred) or endpoint response (fallback)
        applications_detected = []
        try:
            # First, try to get from project object directly (more efficient)
            if project.package_structure_metadata:
                if isinstance(project.package_structure_metadata, dict):
                    applications_detected = project.package_structure_metadata.get('applications_detected', [])
                else:
                    applications_detected = getattr(project.package_structure_metadata, 'applications_detected', [])
            
            # If still empty, try application_discovery_metadata
            if not applications_detected and project.application_discovery_metadata:
                if isinstance(project.application_discovery_metadata, dict):
                    applications_detected = [app.get('application_name') for app in project.application_discovery_metadata.get('applications', [])]
                else:
                    applications_detected = [app.application_name for app in getattr(project.application_discovery_metadata, 'applications', [])]
            
            # If still empty, try calling get_project endpoint as fallback
            if not applications_detected:
                logger.warning(f"No applications_detected from project object, trying get_project endpoint")
                try:
                    project_response = await get_project(project_id)
                    applications_detected = project_response.get('applications_detected', [])
                    logger.info(f"Applications detected via get_project endpoint: {applications_detected}")
                except Exception as e:
                    logger.warning(f"Failed to get applications from get_project endpoint: {e}")
            
            logger.info(f"Final applications detected in project: {applications_detected}")
        except Exception as e:
            logger.error(f"Failed to get applications for project {project_id}: {e}", exc_info=True)
        
        # Normalize application names for comparison (handle case sensitivity and format differences)
        normalized_detected = [app.lower().replace('_', '-') for app in applications_detected]
        normalized_requested = application_name.lower().replace('_', '-')
        
        # Check if application exists in project (with normalization)
        if not applications_detected:
            logger.error(f"No applications detected in project {project_id}. Project status: {project.status}")
            raise HTTPException(
                status_code=400, 
                detail=f"No applications detected in project. Please ensure the project has been processed and applications have been discovered."
            )
        
        if normalized_requested not in normalized_detected:
            logger.error(f"Application {application_name} (normalized: {normalized_requested}) not found in project. Available: {applications_detected} (normalized: {normalized_detected})")
            raise HTTPException(
                status_code=400, 
                detail=f"Application {application_name} not found in project. Available: {applications_detected}"
            )
        
        # Create analysis record for specific application
        try:
            analysis = Analysis(
                project_id=UUID(project_id),
                configuration=config or {
                    "time_series_analysis": True,
                    "anomaly_detection": True,
                    "pattern_recognition": True,
                    "correlation_analysis": True,
                    "applications": [application_name]  # Focus on single application
                },
                status="queued",
                application_focus=application_name
            )
            logger.info(f"Created analysis record: {analysis.id}")
        except Exception as e:
            logger.error(f"Failed to create analysis record: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create analysis record: {str(e)}")
        
        # Store analysis using ProjectAnalysisManager
        try:
            from app.core.config import get_settings
            settings = get_settings()
            project_manager = ProjectAnalysisManager(settings.DATA_DIR, project_id)
            project_manager.save_analysis(analysis)
            logger.info(f"Saved analysis to ProjectAnalysisManager: {analysis.id}")
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save analysis: {str(e)}")
        
        # Save to file
        try:
            save_data()
        except Exception as e:
            logger.warning(f"Failed to save data to file: {e}")
        
        # Start application-specific analysis in background
        try:
            background_tasks.add_task(run_application_analysis_background, str(analysis.id), project_id, application_name)
            logger.info(f"Started background task for analysis: {analysis.id}")
        except Exception as e:
            logger.error(f"Failed to start background task: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start background task: {str(e)}")
        
        return {
            "analysis_id": str(analysis.id),
            "project_id": project_id,
            "application": application_name,
            "status": analysis.status,
            "message": f"Analysis started for {application_name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start application analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start application analysis: {str(e)}")

@app.get("/api/v1/projects/{project_id}/analyses")
async def get_project_analyses(project_id: str, refresh: bool = Query(False, description="Force reload from disk")):
    """Get all analyses for a project - reads from disk for consistency"""
    try:
        # Reload project from disk if not in memory or refresh requested (consistent with get_project)
        if refresh or project_id not in projects_db:
            if os.path.exists(PROJECTS_FILE):
                with open(PROJECTS_FILE, 'r') as f:
                    projects_data = json.load(f)
                    if project_id in projects_data:
                        project_dict = projects_data[project_id]
                        project = Project(
                            id=UUID(project_id),
                            name=project_dict["name"],
                            description=project_dict.get("description"),
                            original_filename=project_dict["original_filename"],
                            file_size_bytes=project_dict["file_size_bytes"],
                            upload_timestamp=datetime.fromisoformat(project_dict["upload_timestamp"]),
                            extraction_path=project_dict.get("extraction_path", ""),
                            status=project_dict["status"],
                            created_by=project_dict.get("created_by"),
                            last_modified=datetime.fromisoformat(project_dict["last_modified"]),
                            analysis_count=project_dict.get("analysis_count", 0),
                            last_analysis_timestamp=datetime.fromisoformat(project_dict["last_analysis_timestamp"]) if project_dict.get("last_analysis_timestamp") else None,
                            extraction_metadata_path=project_dict.get("extraction_metadata_path"),
                            project_root_path=project_dict.get("project_root_path", ""),
                            package_structure_metadata=project_dict.get("package_structure_metadata"),
                            application_discovery_metadata=project_dict.get("application_discovery_metadata")
                        )
                        projects_db[project_id] = project
        
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load analyses using ProjectAnalysisManager
        from app.core.config import get_settings
        settings = get_settings()
        try:
            project_manager = ProjectAnalysisManager(settings.DATA_DIR, project_id)
            analyses = project_manager.list_analyses()
        except Exception as e:
            logger.error(f"Failed to load analyses for project {project_id}: {e}")
            import traceback
            traceback.print_exc()
            # Return empty list instead of failing completely
            analyses = []
        
        # Convert Analysis objects to dict format
        analyses_data = []
        for analysis in analyses:
            try:
                analysis_data = {
                    "id": str(analysis.id),
                    "project_id": project_id,
                    "status": analysis.status,
                    "progress_percentage": analysis.progress_percentage,
                    "current_stage": analysis.current_stage,
                    "created_timestamp": analysis.created_timestamp.isoformat() if analysis.created_timestamp else None,
                    "started_timestamp": analysis.started_timestamp.isoformat() if analysis.started_timestamp else None,
                    "completed_timestamp": analysis.completed_timestamp.isoformat() if analysis.completed_timestamp else None,
                    "error_message": analysis.error_message,
                    "application_focus": analysis.application_focus,
                    "configuration": analysis.configuration
                }
                analyses_data.append(analysis_data)
            except Exception as e:
                logger.warning(f"Failed to serialize analysis {getattr(analysis, 'id', 'unknown')}: {e}")
                continue
        
        # Set cache control headers
        response = JSONResponse(content={"analyses": analyses_data})
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project analyses: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analyses/{analysis_id}/result")
async def get_analysis_result(analysis_id: str):
    """Get analysis result by analysis ID"""
    try:
        # Find analysis across all projects
        analysis = None
        project_id = None
        
        # Search through all projects for the analysis
        for pid in projects_db:
            try:
                from app.core.config import get_settings
                settings = get_settings()
                project_manager = ProjectAnalysisManager(settings.DATA_DIR, pid)
                found_analysis = project_manager.get_analysis(analysis_id)
                if found_analysis:
                    analysis = found_analysis
                    project_id = pid
                    break
            except Exception:
                continue
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis.status != "completed":
            raise HTTPException(status_code=400, detail=f"Analysis not completed. Status: {analysis.status}")
        
        if not analysis.result:
            raise HTTPException(status_code=404, detail="Analysis result not available")
        
        # Convert AnalysisResult to dict format
        result_data = {
            "analysis_id": str(analysis.id),
            "project_id": project_id,
            "completed_at": analysis.completed_timestamp.isoformat() if analysis.completed_timestamp else None,
            "application_analyses": {}
        }
        
        # Add application analyses if available
        if hasattr(analysis.result, 'application_analyses'):
            for app_name, app_analysis in analysis.result.application_analyses.items():
                # Convert ApplicationAnalysis to dict
                app_data = {
                    "functional_domain": getattr(app_analysis, 'functional_domain', 'Unknown'),
                    "container_id": getattr(app_analysis, 'container_id', 'N/A'),
                    "health_score": getattr(app_analysis, 'health_score', 0),
                    "log_volume": getattr(app_analysis, 'log_volume', 0),
                    "error_rate": getattr(app_analysis, 'error_rate', 0.0),
                    "anomalies": getattr(app_analysis, 'anomalies', []),
                    "time_series_data": getattr(app_analysis, 'time_series_data', []),
                    "time_sequence_preview": getattr(app_analysis, 'time_sequence_preview', None)
                }
                result_data["application_analyses"][app_name] = app_data
        
        return result_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis result: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analysis/run")
async def run_analysis(
    background_tasks: BackgroundTasks,
    log_entries: List[Dict[str, Any]],
    project_id: str,
    config: Optional[Dict[str, Any]] = None
):
    """Run analysis on provided log entries"""
    try:
        logger.info(f"Running analysis for project: {project_id}")
        
        # Convert log entries to LogEntry objects
        from app.models.core import LogEntry, LogLevel
        from datetime import datetime
        
        parsed_entries = []
        for entry_data in log_entries:
            try:
                log_entry = LogEntry(
                    timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                    container_id=entry_data.get("container_id", ""),
                    application=entry_data.get("application", ""),
                    log_level=LogLevel(entry_data.get("log_level", "info")),
                    message=entry_data.get("message", ""),
                    structured_data=entry_data.get("structured_data"),
                    raw_line=entry_data.get("raw_line", ""),
                    line_number=entry_data.get("line_number", 0),
                    file_path=entry_data.get("file_path", "")
                )
                parsed_entries.append(log_entry)
            except Exception as e:
                logger.warning(f"Failed to parse log entry: {e}")
                continue
        
        # Run analysis
        analysis_result = analysis_engine.analyze_logs(parsed_entries, project_id, config)
        
        return {
            "analysis_id": analysis_result.analysis_id,
            "project_id": project_id,
            "summary": analysis_result.summary,
            "recommendations": analysis_result.recommendations,
            "system_health_score": analysis_result.summary["system_health_score"],
            "message": "Analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to run analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/reports/generate")
async def generate_report(
    analysis_result: Dict[str, Any],
    report_type: str = "summary",
    output_format: str = "json"
):
    """Generate a report from analysis results"""
    try:
        logger.info(f"Generating {report_type} report in {output_format} format")
        
        # Convert analysis result back to AnalysisResult object
        from app.analytics.analysis_engine import AnalysisResult
        from datetime import datetime
        
        # This is a simplified conversion - in production, you'd have proper serialization
        result = AnalysisResult(
            analysis_id=analysis_result.get("analysis_id", "unknown"),
            project_id=analysis_result.get("project_id", "unknown"),
            timestamp=datetime.now(),
            summary=analysis_result.get("summary", {}),
            time_series_data=[],  # Would need proper conversion
            event_patterns=[],    # Would need proper conversion
            correlations=[],       # Would need proper conversion
            application_insights=analysis_result.get("application_insights", []),
            system_insights=analysis_result.get("system_insights", {}),
            recommendations=analysis_result.get("recommendations", []),
            metadata=analysis_result.get("metadata", {})
        )
        
        # Generate report
        report_content = report_generator.generate_report(
            result, 
            report_type=report_type, 
            output_format=output_format
        )
        
        return {
            "report_type": report_type,
            "output_format": output_format,
            "content": report_content,
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis_background(analysis_id: str, project_id: str):
    """Background task to run analysis with extraction reuse"""
    try:
        logger.info(f"Running analysis in background: {analysis_id}")
        
        analysis = analyses_db[analysis_id]
        project = projects_db[project_id]
        
        # Update status
        analysis.status = "running"
        analysis.started_timestamp = datetime.now()
        
        # Get package structure using extraction reuse
        package_structure = package_processor.process_package(
            package_path=None,  # Will use existing extraction
            project_id=project_id,
            reuse_extraction=True
        )
        
        # Parse logs from package
        log_entries = await parse_logs_from_package(package_structure)
        
        # Use application-specific analysis
        from app.analyzers.analysis_orchestrator import AnalysisOrchestrator
        
        orchestrator = AnalysisOrchestrator()
        analysis_result = orchestrator.analyze_project(
            project_name=project.name,
            package_structure=package_structure,
            log_entries=log_entries
        )
        
        # Store analysis result
        analysis.result = analysis_result
        
        # Update status
        analysis.status = "completed"
        analysis.completed_timestamp = datetime.now()
        analysis.progress_percentage = 100.0;
        
        # Update project
        project.analysis_count += 1
        project.last_analysis_timestamp = datetime.now()
        
        logger.info(f"Analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # Load analysis using ProjectAnalysisManager for error handling
        from app.core.config import get_settings
        settings = get_settings()
        project_manager = ProjectAnalysisManager(settings.DATA_DIR, project_id)
        analysis = project_manager.get_analysis(analysis_id)
        if analysis:
            analysis.status = "failed"
            analysis.error_message = str(e)
            project_manager.save_analysis(analysis)

async def run_application_analysis_background(analysis_id: str, project_id: str, application_name: str):
    """Background task to run application-specific analysis with intelligent re-analysis detection"""
    try:
        logger.info(f"Running application-specific analysis in background: {analysis_id} for {application_name}")
        
        # Load analysis using ProjectAnalysisManager
        from app.core.config import get_settings
        settings = get_settings()
        project_manager = ProjectAnalysisManager(settings.DATA_DIR, project_id)
        analysis = project_manager.get_analysis(analysis_id)
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        project = projects_db[project_id]
        
        # Initialize application analysis manager with proper configuration
        from app.services.application_analysis_manager import ApplicationAnalysisManager
        from app.core.config import get_data_dir
        import os
        # Get absolute path to data directory
        data_dir = os.path.abspath(get_data_dir())
        analysis_manager = ApplicationAnalysisManager(data_dir)
        
        # Check if there's already an analysis for this application
        existing_analysis = project_manager.get_analysis(application_name=application_name)
        
        if existing_analysis:
            # Check if the existing analysis is truly running (not stuck)
            if existing_analysis.status == "running" and existing_analysis.started_timestamp is not None:
                logger.info(f"Analysis already running for {application_name}: {existing_analysis.id}")
                # Update the current analysis to point to the running one
                analysis.status = "running"
                analysis.started_timestamp = existing_analysis.started_timestamp
                project_manager.save_analysis(analysis)
                
                # Publish status update
                await redis_manager.publish_analysis_status(
                    project_id, application_name, str(analysis.id), "running", {
                        "message": "Analysis already in progress",
                        "existing_analysis_id": str(existing_analysis.id)
                    }
                )
                return
            elif existing_analysis.status == "running" and existing_analysis.started_timestamp is None:
                # Clean up stuck analysis
                logger.warning(f"Cleaning up stuck analysis for {application_name}: {existing_analysis.id}")
                existing_analysis.status = "failed"
                existing_analysis.error_message = "Analysis was stuck and cleaned up"
                project_manager.save_analysis(existing_analysis)
            
            # For any other status (completed, failed, queued), we'll replace it with the new analysis
            logger.info(f"Replacing existing analysis for {application_name}: {existing_analysis.id} -> {analysis.id}")
        
        # Check if re-analysis is needed
        config = analysis.configuration
        if not analysis_manager.needs_reanalysis(project_id, application_name, config):
            logger.info(f"No re-analysis needed for {application_name}")
            
            # Load existing analysis metadata to get the correct analysis ID
            existing_metadata = analysis_manager.load_analysis_metadata(project_id, application_name)
            if existing_metadata:
                existing_analysis_id = existing_metadata.analysis_id
                logger.info(f"Using existing analysis ID: {existing_analysis_id}")
                
                # Load existing analysis result using the correct analysis ID
                existing_result = analysis_manager.load_analysis_result(project_id, application_name, existing_analysis_id)
                if existing_result:
                    # Create analysis result with existing data
                    from app.models.core import AnalysisResult
                    analysis_result = AnalysisResult(
                        analysis_id=existing_analysis_id,  # Use the existing analysis ID
                        project_name=project.name
                    )
                    analysis_result.application_analyses[application_name] = existing_result
                    
                    # Store analysis result
                    analysis.result = analysis_result
                    analysis.status = "completed"
                    analysis.completed_timestamp = datetime.now()
                    analysis.progress_percentage = 100.0
                    
                    # Save updated analysis to ProjectAnalysisManager
                    project_manager.save_analysis(analysis)
                    
                    # Publish analysis completed event (reusing existing result)
                    await redis_manager.publish_analysis_completed(project_id, application_name, analysis_id, {
                        "log_volume": existing_result.log_volume,
                        "error_rate": existing_result.error_rate,
                        "health_score": existing_result.health_score,
                        "reused": True
                    })
                    
                    # Save to file
                    save_data()
                    
                    logger.info(f"Application-specific analysis loaded from cache: {existing_analysis_id} for {application_name}")
                    return
        
        # Update status for new analysis
        analysis.status = "running"
        analysis.started_timestamp = datetime.now()
        
        # Publish analysis started event
        await redis_manager.publish_analysis_started(project_id, application_name, analysis_id)
        
        # Save updated analysis to ProjectAnalysisManager
        project_manager.save_analysis(analysis)
        
        # Get package structure using extraction reuse
        package_structure = package_processor.process_package(
            package_path=None,  # Will use existing extraction
            project_id=project_id,
            reuse_extraction=True
        )
        
        # Parse logs from package (now returns app-specific data)
        app_logs = await parse_logs_from_package(package_structure)
        
        # Publish progress update
        await redis_manager.publish_analysis_progress(project_id, application_name, analysis_id, 30.0, "Parsing logs")
        
        # Get logs for the specific application
        if application_name not in app_logs:
            raise ValueError(f"No logs found for application: {application_name}")
        
        log_entries = app_logs[application_name]
        
        # Publish progress update
        await redis_manager.publish_analysis_progress(project_id, application_name, analysis_id, 50.0, "Analyzing logs")
        
        # Use application-specific analysis
        from app.analyzers.analysis_orchestrator import AnalysisOrchestrator
        
        orchestrator = AnalysisOrchestrator()
        
        # Filter containers for the specific application
        app_containers = [c for c in package_structure.containers if c.application_name == application_name]
        
        if not app_containers:
            raise ValueError(f"No containers found for application: {application_name}")
        
        # Analyze only the specific application
        app_analysis = orchestrator._analyze_application(application_name, app_containers, log_entries)
        
        # Create analysis metadata
        from app.models.core import ApplicationAnalysisMetadata
        analysis_metadata = ApplicationAnalysisMetadata(
            application_name=application_name,
            analysis_id=analysis_id,
            project_id=project_id,
            analysis_timestamp=datetime.now(),
            status="completed",
            log_volume=len(log_entries),
            error_rate=app_analysis.error_rate,
            health_score=app_analysis.health_score,
            analysis_config_hash=analysis_manager.calculate_config_hash(config),
            data_hash=analysis_manager.calculate_data_hash(project_id, application_name),
            result_file_path=analysis_manager.get_app_result_file(project_id, application_name, analysis_id)
        )
        
        # Save application-specific analysis metadata and result
        analysis_manager.save_analysis_metadata(analysis_metadata, project_id, application_name)
        analysis_manager.save_analysis_result(app_analysis, project_id, application_name, analysis_id)
        
        # Create analysis result with only the specific application
        from app.models.core import AnalysisResult
        analysis_result = AnalysisResult(
            analysis_id=analysis_id,
            project_name=project.name
        )
        analysis_result.application_analyses[application_name] = app_analysis
        
        # Store analysis result
        analysis.result = analysis_result
        
        # Update status
        analysis.status = "completed"
        analysis.completed_timestamp = datetime.now()
        analysis.progress_percentage = 100.0;
        
        # Save updated analysis to ProjectAnalysisManager
        project_manager.save_analysis(analysis)
        
        # Publish analysis completed event
        await redis_manager.publish_analysis_completed(project_id, application_name, analysis_id, {
            "log_volume": len(log_entries),
            "error_rate": app_analysis.error_rate,
            "health_score": app_analysis.health_score
        })
        
        # Save to file
        save_data()
        
        logger.info(f"Application-specific analysis completed: {analysis_id} for {application_name}")
        
    except Exception as e:
        logger.error(f"Application analysis failed: {e}")
        
        # Publish analysis failed event
        await redis_manager.publish_analysis_failed(project_id, application_name, analysis_id, str(e))
        
        # Load analysis using ProjectAnalysisManager for error handling
        from app.core.config import get_settings
        settings = get_settings()
        project_manager = ProjectAnalysisManager(settings.DATA_DIR, project_id)
        analysis = project_manager.get_analysis(analysis_id)
        if analysis:
            analysis.status = "failed"
            analysis.error_message = str(e)
            project_manager.save_analysis(analysis)

def categorize_event_for_application(message: str, application: str) -> str:
    """Categorize message based on content - matches frontend filter categories"""
    message_lower = message.lower()
    
    # Application-specific categorization for wnc-steer
    if application == "wnc-steer":
        if "steering" in message_lower and ("evaluation" in message_lower or "steer_info" in message_lower or "neighbor" in message_lower):
            return "steering_evaluation"
        elif "steering" in message_lower and ("action" in message_lower or "triggered" in message_lower or "moved" in message_lower):
            return "steering_action"
        elif "steering" in message_lower and ("decision" in message_lower or "request" in message_lower):
            return "steering_decision"
        elif "rssi" in message_lower or "rcpi" in message_lower or "signal" in message_lower or "weak" in message_lower:
            return "monitoring"
        elif "load" in message_lower or "balance" in message_lower or "capacity" in message_lower or "distribution" in message_lower:
            return "optimization"
        elif "error" in message_lower or "fail" in message_lower or "critical" in message_lower:
            return "errors"
        else:
            return "general"
    
    elif application == "wnc-acs":
        # Map to frontend filter categories: scanning, detection, optimization, analysis, compliance
        if "scan" in message_lower and ("channel" in message_lower or "frequency" in message_lower):
            return "scanning"
        elif "interference" in message_lower or "noise" in message_lower:
            return "detection"
        elif "channel" in message_lower and ("switch" in message_lower or "change" in message_lower or "select" in message_lower):
            return "optimization"
        elif "spectrum" in message_lower or "frequency" in message_lower or "bandwidth" in message_lower or "analysis" in message_lower:
            return "analysis"
        elif "regulatory" in message_lower or "compliance" in message_lower or "legal" in message_lower or "dfs" in message_lower:
            return "compliance"
        elif "error" in message_lower or "fail" in message_lower:
            return "errors"
        elif "channel" in message_lower:
            # Channel-related but not switching - default to scanning
            return "scanning"
        else:
            return "general"
    
    elif application == "wnc-tpyopt":
        if "topology" in message_lower or "optimization" in message_lower:
            return "topology_optimization"
        elif "scan" in message_lower or "trigger" in message_lower:
            return "scan_management"
        elif "error" in message_lower or "fail" in message_lower:
            return "errors"
        else:
            return "general"
    
    elif application == "otbr-agent":
        if "thread" in message_lower or "mesh" in message_lower:
            return "thread_management"
        elif "border" in message_lower or "router" in message_lower:
            return "border_router"
        elif "error" in message_lower or "fail" in message_lower:
            return "errors"
        else:
            return "general"
    
    # Default categorization for other applications
    if "error" in message_lower or "fail" in message_lower or "critical" in message_lower:
        return "errors"
    else:
        return "general"

async def parse_logs_from_package(package_structure: PackageStructure) -> Dict[str, List[Any]]:
    """Parse logs from package structure and organize by application"""
    from app.models.core import LogEntry, LogLevel
    import re
    import json
    
    # Dictionary to store logs by application
    app_logs = {}
    
    print(f"DEBUG: parse_logs_from_package - extraction_path: {package_structure.metadata.extraction_path}")
    print(f"DEBUG: parse_logs_from_package - containers count: {len(package_structure.containers)}")
    
    for container in package_structure.containers:
        app_name = container.application_name
        print(f"DEBUG: Container {app_name} - relative_path: {container.relative_path}")
        print(f"DEBUG: Container {app_name} - log_files: {container.log_files}")
        
        # Initialize app-specific log list
        if app_name not in app_logs:
            app_logs[app_name] = []
        
        # Parse log files for this container
        for log_file in container.log_files:
            # Construct the correct file path using the relative path
            file_path = os.path.join(package_structure.metadata.extraction_path, container.relative_path, log_file)
            print(f"DEBUG: Constructed file_path: {file_path}")
            print(f"DEBUG: File exists: {os.path.exists(file_path)}")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            try:
                                # Parse syslog format: timestamp hostname application: message
                                # Example: 2025 Sep 03 08:10:11.689216 31be8750-b807-5888-aa3c-599acbdfb6e6 wnc-steer: units   - [i]steer_info->enable=1, Interval=45
                                # Or: 2025 Sep  3 11:50:15 31be8750-b807-5888-aa3c-599acbdfb6e6 wnc-steer: units   - [i]steer_info->enable=1, Interval=45
                                
                                # Extract timestamp and message (handle both with and without microseconds)
                                # Handle different log formats:
                                # Format 1: timestamp hostname application: message
                                # Format 2: timestamp hostname application[pid]: message
                                match = re.match(r'(\d{4}\s+\w+\s+\d+\s+\d+:\d+:\d+(?:\.\d+)?)\s+(\S+)\s+(\S+)(?:\[\d+\])?:\s*(.*)', line.strip())
                                if match:
                                    timestamp_str, hostname, application, message = match.groups()
                                    
                                    # Parse timestamp (handle microseconds)
                                    try:
                                        timestamp = datetime.strptime(timestamp_str, '%Y %b %d %H:%M:%S.%f')
                                    except ValueError:
                                        # Try without microseconds
                                        timestamp = datetime.strptime(timestamp_str, '%Y %b %d %H:%M:%S')
                                    
                                    # Determine log level from message
                                    log_level = LogLevel.INFO
                                    if any(keyword in message.lower() for keyword in ['error', 'fail', 'critical']):
                                        log_level = LogLevel.ERROR
                                    elif any(keyword in message.lower() for keyword in ['warning', 'warn']):
                                        log_level = LogLevel.WARNING
                                    elif any(keyword in message.lower() for keyword in ['debug']):
                                        log_level = LogLevel.DEBUG
                                    
                                    # Categorize message for fast filtering
                                    message_type = categorize_event_for_application(message, container.application_name)
                                    
                                    # Create log entry
                                    log_entry = LogEntry(
                                        timestamp=timestamp,
                                        container_id=container.container_id,
                                        application=container.application_name,  # Use container's application name, not log line's
                                        log_level=log_level,
                                        message=message,
                                        raw_line=line.strip(),
                                        line_number=line_num,
                                        file_path=file_path,
                                        message_type=message_type
                                    )
                                    app_logs[app_name].append(log_entry)
                                    
                            except Exception as e:
                                logger.warning(f"Failed to parse log line {line_num} in {file_path}: {e}")
                                continue
                                
                except Exception as e:
                    logger.warning(f"Failed to read log file {file_path}: {e}")
                    continue
    
    # Store application-specific logs
    await store_application_logs(package_structure.metadata.extraction_path, app_logs)
    
    total_logs = sum(len(logs) for logs in app_logs.values())
    print(f"DEBUG: Total log entries parsed: {total_logs}")
    for app_name, logs in app_logs.items():
        print(f"DEBUG: {app_name}: {len(logs)} log entries")
    
    logger.info(f"Parsed {total_logs} log entries from package, organized by {len(app_logs)} applications")
    return app_logs

async def store_application_logs(extraction_path: str, app_logs: Dict[str, List[Any]]):
    """Store application-specific logs using ApplicationDataManager with SQLite"""
    from app.services.application_data_manager import ApplicationDataManager
    from app.core.config import get_settings
    import os
    
    settings = get_settings()
    
    # Extract project_id from extraction_path
    # extraction_path format: {DATA_DIR}/projects/{project_id}/extracted
    path_parts = extraction_path.split(os.sep)
    project_id = None
    for i, part in enumerate(path_parts):
        if part == "projects" and i + 1 < len(path_parts):
            project_id = path_parts[i + 1]
            break
    
    if not project_id:
        logger.error(f"Could not extract project_id from extraction_path: {extraction_path}")
        return
    
    for app_name, logs in app_logs.items():
        try:
            # Initialize ApplicationDataManager for this application
            data_manager = ApplicationDataManager(project_id, app_name, settings.DATA_DIR)
            
            # Insert logs into SQLite database
            data_manager.store_log_entries(logs)
            
            # Update metadata
            metadata = {
                "application_name": app_name,
                "total_logs": len(logs),
                "log_files": list(set(log.file_path for log in logs)),
                "time_range": {
                    "start": min(log.timestamp for log in logs).isoformat() if logs else None,
                    "end": max(log.timestamp for log in logs).isoformat() if logs else None
                },
                "log_levels": {
                    level.value: sum(1 for log in logs if log.log_level.value == level.value)
                    for level in [LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.DEBUG]
                },
                "updated_at": datetime.now().isoformat()
            }
            
            # Save metadata to JSON file
            metadata_file = data_manager.metadata_path
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Stored {len(logs)} logs for {app_name} in SQLite database")
            
        except Exception as e:
            logger.error(f"Failed to store logs for {app_name}: {e}")
            continue

@app.get("/api/v1/projects/{project_id}/export")
async def export_project(project_id: str):
    """Export a complete project with all metadata and data"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        # Get comprehensive project data
        export_data = {
            "project_metadata": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "created_by": project.created_by,
                "original_filename": project.original_filename,
                "file_size_bytes": project.file_size_bytes,
                "upload_timestamp": project.upload_timestamp.isoformat(),
                "extraction_timestamp": getattr(project, 'extraction_timestamp', None).isoformat() if getattr(project, 'extraction_timestamp', None) else None,
                "last_modified": project.last_modified.isoformat(),
                "analysis_count": project.analysis_count,
                "last_analysis_timestamp": project.last_analysis_timestamp.isoformat() if project.last_analysis_timestamp else None
            },
            "package_structure_metadata": project.package_structure_metadata,
            "application_discovery_metadata": project.application_discovery_metadata,
            "export_timestamp": datetime.now().isoformat(),
            "export_version": "1.0",
            "export_compatibility": {
                "min_version": "1.0.0",
                "max_version": "1.0.0"
            }
        }
        
        return {
            "success": True,
            "project_id": project_id,
            "export_data": export_data,
            "message": "Project export data ready"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/projects/import")
async def import_project(
    project_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Import a project from export data"""
    try:
        # Validate export data structure
        if "project_metadata" not in project_data:
            raise HTTPException(status_code=400, detail="Invalid export data: missing project_metadata")
        
        project_metadata = project_data["project_metadata"]
        
        # Generate new project ID for import
        new_project_id = str(uuid4())
        
        # Create project object
        project = Project(
            id=UUID(new_project_id),
            name=project_metadata.get("name", f"Imported-{new_project_id[:8]}"),
            description=project_metadata.get("description", "Imported project"),
            original_filename=project_metadata.get("original_filename", ""),
            file_size_bytes=project_metadata.get("file_size_bytes", 0),
            upload_timestamp=datetime.fromisoformat(project_metadata.get("upload_timestamp", datetime.now().isoformat())),
            extraction_path=os.path.join(settings.DATA_DIR, "projects", new_project_id, "extracted"),
            status="imported",
            created_by=project_metadata.get("created_by", "import"),
            last_modified=datetime.now(),
            analysis_count=project_metadata.get("analysis_count", 0),
            last_analysis_timestamp=datetime.fromisoformat(project_metadata["last_analysis_timestamp"]) if project_metadata.get("last_analysis_timestamp") else None,
            package_structure_metadata=project_data.get("package_structure_metadata"),
            application_discovery_metadata=project_data.get("application_discovery_metadata")
        )
        
        # Add to projects database
        projects_db[new_project_id] = project
        
        # Save to file
        background_tasks.add_task(save_data)
        
        return {
            "success": True,
            "project_id": new_project_id,
            "message": f"Project imported successfully as {project.name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to import project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects/{project_id}/applications")
async def get_project_applications(project_id: str):
    """Get list of applications for a project"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        applications = []
        
        # Get applications list from project metadata
        applications_detected = []
        
        # Try to get applications from application_discovery_metadata
        if project.application_discovery_metadata:
            if isinstance(project.application_discovery_metadata, dict):
                applications_detected = [app["application_name"] for app in project.application_discovery_metadata["applications"]]
            else:
                applications_detected = [app.application_name for app in project.application_discovery_metadata.applications]
        
        # Fallback to package_structure_metadata
        elif project.package_structure_metadata:
            if isinstance(project.package_structure_metadata, dict):
                applications_detected = project.package_structure_metadata.get("applications_detected", [])
            else:
                applications_detected = project.package_structure_metadata.applications_detected
        
        # Default applications if nothing found
        if not applications_detected:
            applications_detected = ["wnc-steer", "otbr-agent", "wnc-acs", "unknown"]
        
        # Get data for each application
        for app_name in applications_detected:
            # Check if application has data
            from app.services.application_data_manager import ApplicationDataManager
            from app.core.config import get_settings
            
            settings = get_settings()
            data_manager = ApplicationDataManager(project_id, app_name, settings.DATA_DIR)
            
            has_data = data_manager.db_path.exists()
            log_count = 0
            if has_data:
                log_count = data_manager.get_total_log_count()
            
            applications.append({
                "name": app_name,
                "has_data": has_data,
                "log_count": log_count,
                "data_path": str(data_manager.db_path) if has_data else None
            })
        
        return {"applications": applications}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects/{project_id}/applications/{app_name}")
async def get_application_info(project_id: str, app_name: str):
    """Get information about a specific application"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        # Get applications list from project metadata (same logic as above)
        applications_detected = []
        
        if project.application_discovery_metadata:
            if isinstance(project.application_discovery_metadata, dict):
                applications_detected = [app["application_name"] for app in project.application_discovery_metadata["applications"]]
            else:
                applications_detected = [app.application_name for app in project.application_discovery_metadata.applications]
        elif project.package_structure_metadata:
            if isinstance(project.package_structure_metadata, dict):
                applications_detected = project.package_structure_metadata.get("applications_detected", [])
            else:
                applications_detected = project.package_structure_metadata.applications_detected
        
        if not applications_detected:
            applications_detected = ["wnc-steer", "otbr-agent", "wnc-acs", "unknown"]
        
        if app_name not in applications_detected:
            raise HTTPException(status_code=404, detail="Application not found in project")
        
        # Get application data
        from app.services.application_data_manager import ApplicationDataManager
        from app.core.config import get_settings
        
        settings = get_settings()
        data_manager = ApplicationDataManager(project_id, app_name, settings.DATA_DIR)
        
        has_data = data_manager.db_path.exists()
        
        app_info = {
            "name": app_name,
            "project_id": project_id,
            "has_data": has_data,
            "data_path": str(data_manager.db_path) if has_data else None
        }
        
        if has_data:
            # Get statistics
            log_count = data_manager.get_total_log_count()
            stats = data_manager.get_log_statistics()
            
            app_info.update({
                "log_count": log_count,
                "statistics": stats,
                "data_available": True
            })
        else:
            app_info.update({
                "log_count": 0,
                "statistics": {},
                "data_available": False
            })
        
        return app_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get application info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Duplicate endpoint removed - see first definition at line 1618
# This was a duplicate of GET /api/v1/projects/{project_id}/analyses and has been removed to prevent routing conflicts

@app.get("/api/v1/analyses/{analysis_id}/result")
async def get_analysis_result(analysis_id: str):
    """Get analysis result by analysis ID"""
    try:
        # Find analysis across all projects
        analysis = None
        project_id = None
        
        # Search through all projects for the analysis
        for pid in projects_db:
            try:
                from app.core.config import get_settings
                settings = get_settings()
                project_manager = ProjectAnalysisManager(settings.DATA_DIR, pid)
                found_analysis = project_manager.get_analysis(analysis_id)
                if found_analysis:
                    analysis = found_analysis
                    project_id = pid
                    break
            except Exception:
                continue
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis.status != "completed":
            raise HTTPException(status_code=400, detail=f"Analysis not completed. Status: {analysis.status}")
        
        if not analysis.result:
            raise HTTPException(status_code=404, detail="Analysis result not available")
        
        # Convert AnalysisResult to dict format
        result_data = {
            "analysis_id": str(analysis.id),
            "project_id": project_id,
            "completed_at": analysis.completed_timestamp.isoformat() if analysis.completed_timestamp else None,
            "application_analyses": {}
               }
        
        # Add application analyses if available
        if hasattr(analysis.result, 'application_analyses'):
            for app_name, app_analysis in analysis.result.application_analyses.items():
                # Convert ApplicationAnalysis to dict
                app_data = {
                    "functional_domain": getattr(app_analysis, 'functional_domain', 'Unknown'),
                    "container_id": getattr(app_analysis, 'container_id', 'N/A'),
                    "health_score": getattr(app_analysis, 'health_score', 0),
                    "log_volume": getattr(app_analysis, 'log_volume', 0),
                    "error_rate": getattr(app_analysis, 'error_rate', 0.0),
                    "anomalies": getattr(app_analysis, 'anomalies', []),
                    "time_series_data": getattr(app_analysis, 'time_series_data', []),
                    "time_sequence_preview": getattr(app_analysis, 'time_sequence_preview', None)
                }
                result_data["application_analyses"][app_name] = app_data
        
        return result_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis result: {e}")
        raise HTTPException(status_code=500, detail=str(e))
