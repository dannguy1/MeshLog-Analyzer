"""
Data loading utilities extracted from main.py
"""
import json
import os
from datetime import datetime
from uuid import UUID
from typing import Dict, Any
import structlog

from app.models.core import Project
from app.core.config import get_settings

logger = structlog.get_logger()

# Global data storage (maintaining compatibility with existing code)
projects_db: Dict[str, Project] = {}

# File paths
settings = get_settings()
PROJECTS_FILE = os.path.join(settings.DATA_DIR, "projects.json")

async def load_data():
    """Load data from files"""
    try:
        if os.path.exists(PROJECTS_FILE):
            with open(PROJECTS_FILE, 'r') as f:
                projects_data = json.load(f)
                for project_id, project_dict in projects_data.items():
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
    except Exception as e:
        logger.error(f"Failed to load projects: {e}")

    logger.info("Data loading completed")

def save_data(allow_empty=False):
    """Save data to files with atomic operations and backup"""
    try:
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        
        # Save projects
        projects_data = {}
        for project_id, project in projects_db.items():
            # Handle both Project objects and dictionaries
            if hasattr(project, 'to_dict'):
                try:
                    projects_data[project_id] = project.to_dict()
                except Exception as e:
                    logger.error(f"Failed to convert project {project_id} to dict: {e}")
                    continue
            elif isinstance(project, dict):
                projects_data[project_id] = project
            else:
                logger.error(f"Invalid project type for {project_id}: {type(project)}")
                continue
        
        # Safety check - don't overwrite with empty data unless explicitly allowed
        if not projects_data and not allow_empty and os.path.exists(PROJECTS_FILE):
            with open(PROJECTS_FILE, 'r') as f:
                existing_data = json.load(f)
                if existing_data:
                    logger.warning("Refusing to overwrite non-empty projects file with empty data")
                    return
        
        # Create backup before saving
        if os.path.exists(PROJECTS_FILE):
            backup_file = f"{PROJECTS_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(PROJECTS_FILE, backup_file)
        
        # Save projects atomically
        temp_file = f"{PROJECTS_FILE}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(projects_data, f, indent=2)
        
        # Atomic move
        import shutil
        shutil.move(temp_file, PROJECTS_FILE)
        
        logger.info(f"Saved {len(projects_data)} projects to file")
        
    except Exception as e:
        logger.error(f"Failed to save data: {e}")
        # Clean up temp file if it exists
        temp_file = f"{PROJECTS_FILE}.tmp"
        if os.path.exists(temp_file):
            os.remove(temp_file)
