"""
Database manager for SQLite operations and data persistence
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from app.core.config import settings


class DatabaseManager:
    """Database manager for SQLite operations"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self.data_file = settings.DATA_FILE
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    status TEXT DEFAULT 'created',
                    package_file TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    results TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            
            conn.commit()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    async def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects from database"""
        async with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, name, description, created_at, updated_at, status, package_file, metadata
                FROM projects
                ORDER BY created_at DESC
            """)
            
            projects = []
            for row in cursor:
                project = dict(row)
                if project['metadata']:
                    try:
                        project['metadata'] = json.loads(project['metadata'])
                    except json.JSONDecodeError:
                        project['metadata'] = {}
                else:
                    project['metadata'] = {}
                projects.append(project)
            
            return projects
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get specific project by ID"""
        async with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, name, description, created_at, updated_at, status, package_file, metadata
                FROM projects
                WHERE id = ?
            """, (project_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            project = dict(row)
            if project['metadata']:
                try:
                    project['metadata'] = json.loads(project['metadata'])
                except json.JSONDecodeError:
                    project['metadata'] = {}
            else:
                project['metadata'] = {}
            
            return project
    
    async def create_project(self, project_data: Dict[str, Any]) -> None:
        """Create new project in database"""
        async with self.get_connection() as conn:
            metadata = project_data.get('metadata', {})
            
            conn.execute("""
                INSERT INTO projects (id, name, description, created_at, status, package_file, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                project_data['id'],
                project_data['name'],
                project_data.get('description', ''),
                project_data['created_at'],
                project_data.get('status', 'created'),
                project_data.get('package_file', ''),
                json.dumps(metadata)
            ))
            
            conn.commit()
    
    async def update_project_status(self, project_id: str, status: str) -> None:
        """Update project status"""
        async with self.get_connection() as conn:
            conn.execute("""
                UPDATE projects 
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, datetime.now().isoformat(), project_id))
            
            conn.commit()
    
    async def update_project_metadata(self, project_id: str, metadata_update: Dict[str, Any]) -> None:
        """Update project metadata"""
        async with self.get_connection() as conn:
            # Get current metadata
            cursor = conn.execute("SELECT metadata FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            
            if row:
                current_metadata = {}
                if row['metadata']:
                    try:
                        current_metadata = json.loads(row['metadata'])
                    except json.JSONDecodeError:
                        current_metadata = {}
                
                # Merge with update
                current_metadata.update(metadata_update)
                
                # Update database
                conn.execute("""
                    UPDATE projects 
                    SET metadata = ?, updated_at = ?
                    WHERE id = ?
                """, (json.dumps(current_metadata), datetime.now().isoformat(), project_id))
                
                conn.commit()
    
    async def delete_project(self, project_id: str) -> None:
        """Delete project from database"""
        async with self.get_connection() as conn:
            # Delete analysis results first
            conn.execute("DELETE FROM analysis_results WHERE project_id = ?", (project_id,))
            
            # Delete project
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            
            conn.commit()
    
    async def save_analysis_result(
        self,
        project_id: str,
        analysis_type: str,
        results: Dict[str, Any]
    ) -> None:
        """Save analysis results to database"""
        async with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO analysis_results (project_id, analysis_type, created_at, results)
                VALUES (?, ?, ?, ?)
            """, (
                project_id,
                analysis_type,
                datetime.now().isoformat(),
                json.dumps(results)
            ))
            
            conn.commit()
    
    async def get_analysis_results(
        self,
        project_id: str,
        analysis_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get analysis results for a project"""
        async with self.get_connection() as conn:
            if analysis_type:
                cursor = conn.execute("""
                    SELECT id, analysis_type, created_at, results
                    FROM analysis_results
                    WHERE project_id = ? AND analysis_type = ?
                    ORDER BY created_at DESC
                """, (project_id, analysis_type))
            else:
                cursor = conn.execute("""
                    SELECT id, analysis_type, created_at, results
                    FROM analysis_results
                    WHERE project_id = ?
                    ORDER BY created_at DESC
                """, (project_id,))
            
            results = []
            for row in cursor:
                result = dict(row)
                if result['results']:
                    try:
                        result['results'] = json.loads(result['results'])
                    except json.JSONDecodeError:
                        result['results'] = {}
                else:
                    result['results'] = {}
                results.append(result)
            
            return results
    
    def load_data_from_file(self) -> Dict[str, Any]:
        """Load data from JSON file (for backward compatibility)"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"projects": []}
        return {"projects": []}
    
    def save_data_to_file(self, data: Dict[str, Any]) -> None:
        """Save data to JSON file (for backward compatibility)"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save data to file: {str(e)}")
    
    async def sync_file_to_database(self) -> None:
        """Sync data from JSON file to database"""
        file_data = self.load_data_from_file()
        
        for project in file_data.get("projects", []):
            # Check if project exists in database
            existing = await self.get_project(project['id'])
            
            if not existing:
                # Create project in database
                await self.create_project(project)
            else:
                # Update if file version is newer
                file_updated = project.get('updated_at') or project.get('created_at')
                db_updated = existing.get('updated_at') or existing.get('created_at')
                
                if file_updated > db_updated:
                    await self.update_project_metadata(project['id'], project.get('metadata', {}))
    
    async def sync_database_to_file(self) -> None:
        """Sync data from database to JSON file"""
        projects = await self.get_all_projects()
        data = {"projects": projects}
        self.save_data_to_file(data)
