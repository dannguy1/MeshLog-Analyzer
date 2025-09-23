"""
Analysis service layer for data processing and analysis operations
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, BackgroundTasks

from app.database.database import DatabaseManager
from app.core.config import settings


class AnalysisService:
    """Service class for analysis operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.data_dir = settings.DATA_DIR
        
    async def run_analysis(
        self,
        background_tasks: BackgroundTasks,
        project_id: str,
        project_service
    ) -> Dict[str, Any]:
        """Run analysis on a project"""
        try:
            # Check if project exists
            project = await project_service.get_project(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Schedule background analysis
            background_tasks.add_task(
                self._run_analysis_background,
                project_id
            )
            
            return {
                "message": "Analysis started",
                "project_id": project_id,
                "status": "running"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")
    
    async def get_analysis_results(
        self,
        project_id: str,
        app_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get analysis results for a project"""
        try:
            project_path = os.path.join(self.data_dir, project_id)
            if not os.path.exists(project_path):
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Load analysis results
            results_file = os.path.join(project_path, "analysis_results.json")
            if not os.path.exists(results_file):
                return {"results": [], "message": "No analysis results found"}
            
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            # Filter by application if specified
            if app_name:
                results = [r for r in results if r.get('application') == app_name]
            
            return {"results": results}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get analysis results: {str(e)}")
    
    async def get_log_files(
        self,
        project_id: str,
        app_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get list of log files for a project/application"""
        try:
            base_path = os.path.join(self.data_dir, project_id)
            if app_name:
                base_path = os.path.join(base_path, app_name)
            
            if not os.path.exists(base_path):
                raise HTTPException(status_code=404, detail="Path not found")
            
            log_files = []
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.endswith('.log'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, base_path)
                        stat = os.stat(file_path)
                        
                        log_files.append({
                            'name': file,
                            'path': rel_path,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
            
            return {"log_files": log_files}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get log files: {str(e)}")
    
    async def get_log_content(
        self,
        project_id: str,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get content of a specific log file"""
        try:
            full_path = os.path.join(self.data_dir, project_id, file_path)
            if not os.path.exists(full_path):
                raise HTTPException(status_code=404, detail="Log file not found")
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Apply line range if specified
            if start_line is not None:
                start_line = max(0, start_line - 1)  # Convert to 0-based indexing
            else:
                start_line = 0
                
            if end_line is not None:
                end_line = min(len(lines), end_line)
            else:
                end_line = len(lines)
            
            content_lines = lines[start_line:end_line]
            
            return {
                "content": "".join(content_lines),
                "total_lines": len(lines),
                "start_line": start_line + 1,
                "end_line": end_line,
                "returned_lines": len(content_lines)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get log content: {str(e)}")
    
    async def get_aggregated_data(
        self,
        project_id: str,
        app_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated analysis data"""
        try:
            # Load aggregated data from database or files
            aggregated_file = os.path.join(self.data_dir, project_id, "aggregated_data.json")
            if not os.path.exists(aggregated_file):
                return {"data": {}, "message": "No aggregated data found"}
            
            with open(aggregated_file, 'r') as f:
                data = json.load(f)
            
            # Apply filters
            if app_name:
                data = {k: v for k, v in data.items() if k.startswith(app_name)}
            
            # Date filtering would require more complex logic
            # This is a simplified implementation
            
            return {"data": data}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get aggregated data: {str(e)}")
    
    async def get_advanced_analysis(
        self,
        project_id: str,
        app_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get advanced analysis results"""
        try:
            # Load advanced analysis results
            advanced_file = os.path.join(self.data_dir, project_id, "advanced_analysis.json")
            if not os.path.exists(advanced_file):
                return {"analysis": {}, "message": "No advanced analysis found"}
            
            with open(advanced_file, 'r') as f:
                analysis = json.load(f)
            
            if app_name:
                analysis = analysis.get(app_name, {})
            
            return {"analysis": analysis}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get advanced analysis: {str(e)}")
    
    async def get_anomalies(
        self,
        project_id: str,
        app_name: Optional[str] = None,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get anomaly detection results"""
        try:
            # Load anomaly detection results
            anomalies_file = os.path.join(self.data_dir, project_id, "anomalies.json")
            if not os.path.exists(anomalies_file):
                return {"anomalies": [], "message": "No anomalies found"}
            
            with open(anomalies_file, 'r') as f:
                anomalies = json.load(f)
            
            # Filter by application and threshold
            if app_name:
                anomalies = [a for a in anomalies if a.get('application') == app_name]
            
            if threshold is not None:
                anomalies = [a for a in anomalies if a.get('score', 0) >= threshold]
            
            return {"anomalies": anomalies}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get anomalies: {str(e)}")
    
    async def get_analysis_statistics(
        self,
        project_id: str,
        app_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analysis statistics"""
        try:
            stats_file = os.path.join(self.data_dir, project_id, "statistics.json")
            if not os.path.exists(stats_file):
                return {"statistics": {}, "message": "No statistics found"}
            
            with open(stats_file, 'r') as f:
                statistics = json.load(f)
            
            if app_name:
                statistics = statistics.get(app_name, {})
            
            return {"statistics": statistics}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
    
    async def _run_analysis_background(self, project_id: str):
        """Background task to run analysis"""
        try:
            # Update analysis status
            await self.db_manager.update_project_metadata(project_id, {
                'analysis_status': 'running',
                'analysis_started': datetime.now().isoformat()
            })
            
            # Run actual analysis (simplified)
            project_path = os.path.join(self.data_dir, project_id)
            
            # Example analysis logic would go here
            # For now, just create some dummy results
            results = {
                'analysis_id': f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'project_id': project_id,
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'summary': {
                    'total_log_files': len([f for f in os.listdir(project_path) if f.endswith('.log')]),
                    'total_size': self._get_directory_size(project_path)
                }
            }
            
            # Save results
            results_file = os.path.join(project_path, "analysis_results.json")
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Update project status
            await self.db_manager.update_project_metadata(project_id, {
                'analysis_status': 'completed',
                'analysis_completed': datetime.now().isoformat()
            })
            
        except Exception as e:
            await self.db_manager.update_project_metadata(project_id, {
                'analysis_status': 'error',
                'analysis_error': str(e)
            })
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
