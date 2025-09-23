"""
Project-Scoped Analysis Manager

This service manages analysis metadata and results at the project level,
eliminating the need for global analysis registries and making each project self-contained.
Now uses ApplicationDataManager for unified data storage.
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from app.models.core import Analysis, AnalysisResult
from app.services.application_data_manager import ApplicationDataManager

logger = logging.getLogger(__name__)


class ProjectAnalysisManager:
    """Manages analysis metadata and results at the project level"""
    
    def __init__(self, data_dir: str, project_id: str):
        self.data_dir = data_dir
        self.project_id = project_id
        self.project_dir = os.path.join(data_dir, "projects", project_id)
        self.applications_dir = os.path.join(self.project_dir, "applications")
        
        # Ensure directories exist
        os.makedirs(self.applications_dir, exist_ok=True)
    
    def get_analyses_metadata(self) -> Dict[str, Analysis]:
        """Load all analyses metadata for this project from application directories"""
        analyses = {}
        
        # Look for analysis metadata in each application directory
        for app_dir in Path(self.applications_dir).iterdir():
            if app_dir.is_dir():
                app_name = app_dir.name
                analysis_metadata_file = app_dir / "analysis_metadata.json"
                
                if analysis_metadata_file.exists():
                    try:
                        with open(analysis_metadata_file, 'r') as f:
                            analysis_data = json.load(f)
                        
                        analysis = Analysis.from_dict(analysis_data)
                        analyses[app_name] = analysis
                    except Exception as e:
                        print(f"Error loading analysis for {app_name} in project {self.project_id}: {e}")
                        continue
        
        return analyses
    
    def save_analyses_metadata(self, analyses: Dict[str, Analysis]):
        """Save all analyses metadata for this project"""
        try:
            data = {}
            for analysis_id, analysis in analyses.items():
                data[analysis_id] = analysis.to_dict()
            
            with open(self.analyses_metadata_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving analyses metadata for project {self.project_id}: {e}")
    
    def get_analysis(self, analysis_id: str = None, application_name: str = None) -> Optional[Analysis]:
        """Get analysis for this project"""
        analyses = self.get_analyses_metadata()
        
        # If analysis_id is provided, try to find it by ID
        if analysis_id:
            for analysis in analyses.values():
                if str(analysis.id) == analysis_id:
                    return analysis
            return None
        
        # If application_name is provided, get analysis for that application
        if application_name:
            return analyses.get(application_name)
        
        # Return the first available analysis (for backward compatibility)
        if analyses:
            return list(analyses.values())[0]
        
        return None
    
    def save_analysis(self, analysis: Analysis):
        """Save analysis metadata to application-specific directory"""
        try:
            # Determine application name from analysis
            app_name = analysis.application_focus or "general"
            app_dir = Path(self.applications_dir) / app_name
            app_dir.mkdir(exist_ok=True)
            
            # Save analysis metadata
            analysis_metadata_file = app_dir / "analysis_metadata.json"
            
            # Debug: Try to get the dict representation
            try:
                analysis_dict = analysis.to_dict()
                logger.info(f"Successfully converted analysis to dict with keys: {list(analysis_dict.keys())}")
            except Exception as e:
                logger.error(f"Failed to convert analysis to dict: {e}")
                logger.error(f"Analysis type: {type(analysis)}")
                logger.error(f"Analysis fields: {[attr for attr in dir(analysis) if not attr.startswith('_')]}")
                raise
            
            with open(analysis_metadata_file, 'w') as f:
                json.dump(analysis_dict, f, indent=2)
            
            # Save analysis results if available
            if analysis.result:
                analysis_results_file = app_dir / "analysis_results.json"
                try:
                    if hasattr(analysis.result, 'to_dict'):
                        result_data = analysis.result.to_dict()
                    else:
                        # If it's already a dict, use it directly
                        result_data = analysis.result
                        logger.warning(f"Analysis result for {app_name} is not an object with to_dict method, using as dict")
                    
                    with open(analysis_results_file, 'w') as f:
                        json.dump(result_data, f, indent=2)
                except Exception as e:
                    logger.error(f"Failed to save analysis results for {app_name}: {e}")
                    # Continue without failing the entire save operation
            
            print(f"Saved analysis for {app_name} in project {self.project_id}")
            
        except Exception as e:
            print(f"Error saving analysis for project {self.project_id}: {e}")
            raise
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """Delete an analysis"""
        analyses = self.get_analyses_metadata()
        if analysis_id in analyses:
            del analyses[analysis_id]
            self.save_analyses_metadata(analyses)
            return True
        return False
    
    def list_analyses(self) -> List[Analysis]:
        """List all analyses for this project (one per application)"""
        analyses = self.get_analyses_metadata()
        return list(analyses.values())
    
    def get_latest_analysis(self, application_name: str = None) -> Optional[Analysis]:
        """Get the latest analysis for this project or specific application"""
        analyses = self.get_analyses_metadata()
        
        if application_name:
            return analyses.get(application_name)
        
        # Return the most recently created analysis
        if analyses:
            return max(analyses.values(), key=lambda x: x.created_timestamp)
        
        return None
    
    def create_analysis(self, configuration: Dict[str, Any]) -> Analysis:
        """Create a new analysis for this project"""
        analysis_id = str(uuid.uuid4())
        analysis = Analysis(
            id=analysis_id,
            project_id=self.project_id,
            configuration=configuration,
            status="created",
            created_timestamp=datetime.now()
        )
        
        self.save_analysis(analysis)
        return analysis
    
    def get_analysis_summary(self, application_name: str = None) -> Dict[str, Any]:
        """Get a summary of analyses for this project or specific application"""
        analyses = self.get_analyses_metadata()
        
        if application_name:
            # Return summary for specific application
            analysis = analyses.get(application_name)
            if not analysis:
                return {
                    "total_analyses": 0,
                    "latest_analysis": None,
                    "completed_analyses": 0,
                    "running_analyses": 0,
                    "failed_analyses": 0,
                    "status_counts": {}
                }
            
            status_counts = {analysis.status: 1}
            return {
                "total_analyses": 1,
                "latest_analysis": {
                    "id": analysis.id,
                    "status": analysis.status,
                    "created_timestamp": analysis.created_timestamp.isoformat(),
                    "completed_timestamp": analysis.completed_timestamp.isoformat() if analysis.completed_timestamp else None
                },
                "completed_analyses": 1 if analysis.status == "completed" else 0,
                "running_analyses": 1 if analysis.status == "running" else 0,
                "failed_analyses": 1 if analysis.status == "failed" else 0,
                "status_counts": status_counts
            }
        
        # Return summary for all applications
        if not analyses:
            return {
                "total_analyses": 0,
                "latest_analysis": None,
                "completed_analyses": 0,
                "running_analyses": 0,
                "failed_analyses": 0,
                "status_counts": {}
            }
        
        # Count by status across all applications
        status_counts = {}
        for analysis in analyses.values():
            status = analysis.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get the most recent analysis
        latest = max(analyses.values(), key=lambda x: x.created_timestamp)
        
        return {
            "total_analyses": len(analyses),
            "latest_analysis": {
                "id": latest.id,
                "status": latest.status,
                "created_timestamp": latest.created_timestamp.isoformat(),
                "completed_timestamp": latest.completed_timestamp.isoformat() if latest.completed_timestamp else None
            },
            "completed_analyses": status_counts.get("completed", 0),
            "running_analyses": status_counts.get("running", 0),
            "failed_analyses": status_counts.get("failed", 0),
            "status_counts": status_counts
        }
    
    def cleanup_old_analyses(self, keep_count: int = 10) -> int:
        """Clean up old analyses - not needed since we only keep one analysis per application"""
        # Since we only keep one analysis per application, no cleanup is needed
        return 0

