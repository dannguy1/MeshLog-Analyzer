#!/usr/bin/env python3
"""
Project Recovery Script
Recovers missing projects from filesystem and rebuilds projects.json
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from core.config import get_settings

def recover_projects():
    """Recover missing projects from filesystem"""
    settings = get_settings()
    data_dir = Path(settings.DATA_DIR)
    projects_dir = data_dir / "projects"
    projects_file = data_dir / "projects.json"
    
    print(f"Scanning projects directory: {projects_dir}")
    print(f"Projects file: {projects_file}")
    
    # Load existing projects
    existing_projects = {}
    if projects_file.exists():
        with open(projects_file, 'r') as f:
            existing_projects = json.load(f)
        print(f"Found {len(existing_projects)} existing projects in projects.json")
    
    # Scan filesystem for project directories
    recovered_projects = {}
    missing_projects = []
    
    if projects_dir.exists():
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                project_id = project_dir.name
                
                # Check if project exists in projects.json
                if project_id in existing_projects:
                    print(f"✓ Project {project_id} already exists in projects.json")
                    continue
                
                # Try to recover project metadata
                metadata_dir = project_dir / "extracted" / "metadata"
                package_structure_file = metadata_dir / "package_structure.json"
                application_discovery_file = metadata_dir / "application_discovery.json"
                
                if package_structure_file.exists():
                    try:
                        with open(package_structure_file, 'r') as f:
                            package_metadata = json.load(f)
                        
                        # Create basic project entry
                        project_entry = {
                            "id": project_id,
                            "name": package_metadata.get("original_filename", f"Project-{project_id[:8]}"),
                            "description": f"Recovered project from {package_metadata.get('original_filename', 'unknown')}",
                            "original_filename": package_metadata.get("original_filename", "unknown"),
                            "file_size_bytes": 0,  # Unknown
                            "upload_timestamp": package_metadata.get("extraction_timestamp", datetime.now().isoformat()),
                            "extraction_path": str(project_dir / "extracted"),
                            "status": "completed",
                            "created_by": None,
                            "last_modified": datetime.now().isoformat(),
                            "analysis_count": 0,
                            "last_analysis_timestamp": None,
                            "extraction_metadata_path": str(metadata_dir),
                            "project_root_path": str(project_dir),
                            "package_structure_metadata": package_metadata
                        }
                        
                        # Add application discovery metadata if available
                        if application_discovery_file.exists():
                            try:
                                with open(application_discovery_file, 'r') as f:
                                    app_metadata = json.load(f)
                                project_entry["application_discovery_metadata"] = app_metadata
                            except Exception as e:
                                print(f"Warning: Could not load application discovery metadata for {project_id}: {e}")
                        
                        recovered_projects[project_id] = project_entry
                        missing_projects.append(project_id)
                        print(f"✓ Recovered project {project_id}: {project_entry['name']}")
                        
                    except Exception as e:
                        print(f"✗ Failed to recover project {project_id}: {e}")
                else:
                    print(f"✗ Project {project_id} missing package_structure.json")
    
    # Merge recovered projects with existing ones
    all_projects = {**existing_projects, **recovered_projects}
    
    if missing_projects:
        print(f"\nRecovered {len(missing_projects)} missing projects:")
        for project_id in missing_projects:
            project = all_projects[project_id]
            print(f"  - {project_id}: {project['name']}")
        
        # Backup existing projects.json
        if projects_file.exists():
            backup_file = projects_file.with_suffix('.json.backup')
            projects_file.rename(backup_file)
            print(f"Backed up existing projects.json to {backup_file}")
        
        # Write updated projects.json
        with open(projects_file, 'w') as f:
            json.dump(all_projects, f, indent=2)
        
        print(f"Updated projects.json with {len(all_projects)} total projects")
        return True
    else:
        print("No missing projects found")
        return False

if __name__ == "__main__":
    try:
        success = recover_projects()
        if success:
            print("\n✓ Project recovery completed successfully!")
            print("Please restart the backend to load the recovered projects.")
        else:
            print("\n✓ No recovery needed - all projects are already registered.")
    except Exception as e:
        print(f"\n✗ Project recovery failed: {e}")
        sys.exit(1)



