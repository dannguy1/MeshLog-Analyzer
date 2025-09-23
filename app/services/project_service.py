"""
Project management service layer
"""
import os
import shutil
import uuid
import zipfile
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, BackgroundTasks, UploadFile
import aiofiles

from app.database.database import DatabaseManager
from app.core.config import settings


class ProjectService:
    """Service class for project management operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.data_dir = settings.DATA_DIR
        self.upload_dir = settings.UPLOAD_DIR
        
    async def list_projects(self) -> Dict[str, Any]:
        """List all projects with their metadata"""
        try:
            projects = await self.db_manager.get_all_projects()
            
            # Add file system statistics
            for project in projects:
                project_path = os.path.join(self.data_dir, project['id'])
                if os.path.exists(project_path):
                    project['file_count'] = self._count_files(project_path)
                    project['total_size'] = self._get_directory_size(project_path)
                else:
                    project['file_count'] = 0
                    project['total_size'] = 0
                    
            return {"projects": projects}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get detailed project information"""
        try:
            project = await self.db_manager.get_project(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
                
            # Add detailed file system info
            project_path = os.path.join(self.data_dir, project_id)
            if os.path.exists(project_path):
                project['applications'] = self._get_applications(project_path)
                project['file_structure'] = self._get_file_structure(project_path)
            else:
                project['applications'] = []
                project['file_structure'] = {}
                
            return project
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")
    
    async def create_project(
        self,
        background_tasks: BackgroundTasks,
        file: UploadFile,
        name: str,
        description: Optional[str],
        validation_service
    ) -> Dict[str, Any]:
        """Create a new project from uploaded package"""
        try:
            # Generate unique project ID
            project_id = str(uuid.uuid4())
            
            # Save uploaded file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(self.upload_dir, filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Create project record
            project_data = {
                'id': project_id,
                'name': name,
                'description': description or "",
                'created_at': datetime.now().isoformat(),
                'package_file': filename,
                'status': 'created'
            }
            
            await self.db_manager.create_project(project_data)
            
            # Schedule background processing
            background_tasks.add_task(
                self._process_package_background,
                project_id,
                file_path,
                validation_service
            )
            
            return {
                "message": "Project created successfully",
                "project_id": project_id,
                "status": "processing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")
    
    async def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project and all its data"""
        try:
            project = await self.db_manager.get_project(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Remove project directory
            project_path = os.path.join(self.data_dir, project_id)
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            
            # Remove from database
            await self.db_manager.delete_project(project_id)
            
            return {"message": "Project deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")
    
    async def list_available_packages(self) -> Dict[str, Any]:
        """List available packages for restoration"""
        try:
            packages = []
            if os.path.exists(self.upload_dir):
                for filename in os.listdir(self.upload_dir):
                    if filename.endswith(('.zip', '.tar.gz', '.tar')):
                        file_path = os.path.join(self.upload_dir, filename)
                        stat = os.stat(file_path)
                        packages.append({
                            'filename': filename,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
            
            return {"packages": packages}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list packages: {str(e)}")
    
    async def restore_project_from_package(
        self,
        background_tasks: BackgroundTasks,
        filename: str,
        name: str,
        description: Optional[str],
        validation_service
    ) -> Dict[str, Any]:
        """Restore project from existing package file"""
        try:
            file_path = os.path.join(self.upload_dir, filename)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Package file not found")
            
            # Generate new project ID
            project_id = str(uuid.uuid4())
            
            # Create project record
            project_data = {
                'id': project_id,
                'name': name,
                'description': description or "",
                'created_at': datetime.now().isoformat(),
                'package_file': filename,
                'status': 'created'
            }
            
            await self.db_manager.create_project(project_data)
            
            # Schedule background processing
            background_tasks.add_task(
                self._process_package_background,
                project_id,
                file_path,
                validation_service
            )
            
            return {
                "message": "Project restoration started",
                "project_id": project_id,
                "status": "processing"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to restore project: {str(e)}")
    
    def _count_files(self, directory: str) -> int:
        """Count total files in directory recursively"""
        count = 0
        for root, dirs, files in os.walk(directory):
            count += len(files)
        return count
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def _get_applications(self, project_path: str) -> List[str]:
        """Get list of applications in project"""
        applications = []
        if os.path.exists(project_path):
            for item in os.listdir(project_path):
                item_path = os.path.join(project_path, item)
                if os.path.isdir(item_path):
                    applications.append(item)
        return sorted(applications)
    
    def _get_file_structure(self, project_path: str) -> Dict[str, Any]:
        """Get file structure for project"""
        structure = {}
        if os.path.exists(project_path):
            for root, dirs, files in os.walk(project_path):
                rel_path = os.path.relpath(root, project_path)
                if rel_path == ".":
                    rel_path = "root"
                structure[rel_path] = {
                    'directories': dirs,
                    'files': files,
                    'file_count': len(files)
                }
        return structure
    
    async def _process_package_background(
        self,
        project_id: str,
        file_path: str,
        validation_service
    ):
        """Background task to process uploaded package"""
        try:
            # Update status
            await self.db_manager.update_project_status(project_id, "processing")
            
            # Extract package
            extract_path = os.path.join(self.data_dir, project_id)
            os.makedirs(extract_path, exist_ok=True)
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Validate extracted data
            validation_result = await validation_service.validate_project_data(project_id)
            
            if validation_result['valid']:
                await self.db_manager.update_project_status(project_id, "ready")
            else:
                await self.db_manager.update_project_status(project_id, "error")
                await self.db_manager.update_project_metadata(project_id, {
                    'error': validation_result.get('error', 'Validation failed')
                })
                
        except Exception as e:
            await self.db_manager.update_project_status(project_id, "error")
            await self.db_manager.update_project_metadata(project_id, {
                'error': str(e)
            })
    
    async def export_project(self, project_id: str) -> Dict[str, Any]:
        """Export project data"""
        # Implementation for project export
        pass
    
    async def import_project(self, project_data: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Import project from export data"""
        # Implementation for project import
        pass
    
    async def get_project_applications(self, project_id: str) -> Dict[str, Any]:
        """Get applications for a project"""
        project_path = os.path.join(self.data_dir, project_id)
        applications = self._get_applications(project_path)
        return {"applications": applications}
    
    async def get_application_info(self, project_id: str, app_name: str) -> Dict[str, Any]:
        """Get information about specific application"""
        app_path = os.path.join(self.data_dir, project_id, app_name)
        if not os.path.exists(app_path):
            raise HTTPException(status_code=404, detail="Application not found")
        
        return {
            "name": app_name,
            "path": app_path,
            "file_count": self._count_files(app_path),
            "size": self._get_directory_size(app_path),
            "log_files": [f for f in os.listdir(app_path) if f.endswith('.log')]
        }
