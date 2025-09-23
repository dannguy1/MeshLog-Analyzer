"""
Application-Specific Analysis Manager

This service manages analysis metadata and results for each application independently,
enabling on-demand loading and intelligent re-analysis detection.
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from app.models.core import ApplicationAnalysisMetadata, ApplicationAnalysisResult, LogEntry, LogLevel


class ApplicationAnalysisManager:
    """Manages application-specific analysis metadata and results"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
    
    def get_app_analysis_dir(self, project_id: str, app_name: str) -> str:
        """Get the analysis directory for a specific application"""
        return os.path.join(
            self.data_dir, 
            "projects", project_id, "extracted", app_name, "analysis"
        )
    
    def get_app_metadata_file(self, project_id: str, app_name: str) -> str:
        """Get the metadata file path for an application's analysis"""
        analysis_dir = self.get_app_analysis_dir(project_id, app_name)
        return os.path.join(analysis_dir, "analysis_metadata.json")
    
    def get_app_result_file(self, project_id: str, app_name: str, analysis_id: str) -> str:
        """Get the result file path for a specific analysis"""
        analysis_dir = self.get_app_analysis_dir(project_id, app_name)
        return os.path.join(analysis_dir, f"analysis_result_{analysis_id}.json")
    
    def calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Calculate hash of analysis configuration"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def calculate_data_hash(self, project_id: str, app_name: str) -> str:
        """Calculate hash of application's log data"""
        logs_file = os.path.join(
            self.data_dir,
            "projects", project_id, "extracted", app_name, "logs.json"
        )
        
        if not os.path.exists(logs_file):
            return ""
        
        # Use file modification time and size as data hash
        stat = os.stat(logs_file)
        data_str = f"{stat.st_mtime}_{stat.st_size}"
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def load_analysis_metadata(self, project_id: str, app_name: str) -> Optional[ApplicationAnalysisMetadata]:
        """Load analysis metadata for an application"""
        metadata_file = self.get_app_metadata_file(project_id, app_name)
        
        if not os.path.exists(metadata_file):
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            return ApplicationAnalysisMetadata.from_dict(data)
        except Exception as e:
            print(f"Error loading analysis metadata for {app_name}: {e}")
            return None
    
    def save_analysis_metadata(self, metadata: ApplicationAnalysisMetadata, project_id: str, app_name: str):
        """Save analysis metadata for an application"""
        analysis_dir = self.get_app_analysis_dir(project_id, app_name)
        os.makedirs(analysis_dir, exist_ok=True)
        
        metadata_file = self.get_app_metadata_file(project_id, app_name)
        metadata.metadata_file_path = metadata_file
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
    
    def save_analysis_result(self, result: ApplicationAnalysisResult, project_id: str, app_name: str, analysis_id: str):
        """Save detailed analysis result for an application"""
        analysis_dir = self.get_app_analysis_dir(project_id, app_name)
        os.makedirs(analysis_dir, exist_ok=True)
        
        result_file = self.get_app_result_file(project_id, app_name, analysis_id)
        
        with open(result_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
    
    def load_analysis_result(self, project_id: str, app_name: str, analysis_id: str) -> Optional[ApplicationAnalysisResult]:
        """Load detailed analysis result for an application"""
        result_file = self.get_app_result_file(project_id, app_name, analysis_id)
        
        if not os.path.exists(result_file):
            return None
        
        try:
            with open(result_file, 'r') as f:
                data = json.load(f)
            
            # Convert back to ApplicationAnalysisResult
            return ApplicationAnalysisResult(
                application_name=data["application_name"],
                container_id=data["container_id"],
                functional_domain=data["functional_domain"],
                analysis_timestamp=datetime.fromisoformat(data["analysis_timestamp"]),
                log_volume=data["log_volume"],
                error_rate=data["error_rate"],
                performance_metrics=data["performance_metrics"],
                health_score=data["health_score"],
                time_series_data=data["time_series_data"],
                event_patterns=data["event_patterns"],
                anomalies=data["anomalies"],
                predictions=data["predictions"],
                statistical_results=data["statistical_results"],
                correlations=data["correlations"],
                insights=data["insights"],
                recommendations=data["recommendations"],
                time_sequence_preview=data["time_sequence_preview"]
            )
        except Exception as e:
            print(f"Error loading analysis result for {app_name}: {e}")
            return None
    
    def needs_reanalysis(self, project_id: str, app_name: str, config: Dict[str, Any]) -> bool:
        """Check if an application needs re-analysis based on config and data changes"""
        metadata = self.load_analysis_metadata(project_id, app_name)
        
        if not metadata:
            return True  # No previous analysis, needs analysis
        
        if metadata.status != "completed":
            return True  # Previous analysis failed or incomplete
        
        # Check if configuration changed
        current_config_hash = self.calculate_config_hash(config)
        if metadata.analysis_config_hash != current_config_hash:
            print(f"Configuration changed for {app_name}, re-analysis needed")
            return True
        
        # Check if data changed
        current_data_hash = self.calculate_data_hash(project_id, app_name)
        if metadata.data_hash != current_data_hash:
            print(f"Data changed for {app_name}, re-analysis needed")
            return True
        
        print(f"No re-analysis needed for {app_name}")
        return False
    
    def get_analysis_summary(self, project_id: str, app_name: str) -> Dict[str, Any]:
        """Get a summary of the latest analysis for an application"""
        metadata = self.load_analysis_metadata(project_id, app_name)
        
        if not metadata:
            return {
                "has_analysis": False,
                "status": "not_analyzed",
                "message": "No analysis available"
            }
        
        return {
            "has_analysis": True,
            "status": metadata.status,
            "analysis_id": metadata.analysis_id,
            "analysis_timestamp": metadata.analysis_timestamp.isoformat(),
            "log_volume": metadata.log_volume,
            "error_rate": metadata.error_rate,
            "health_score": metadata.health_score,
            "needs_reanalysis": False  # This would be determined by needs_reanalysis()
        }
    
    def list_available_analyses(self, project_id: str, app_name: str) -> List[Dict[str, Any]]:
        """List all available analyses for an application"""
        analysis_dir = self.get_app_analysis_dir(project_id, app_name)
        
        if not os.path.exists(analysis_dir):
            return []
        
        analyses = []
        for file_name in os.listdir(analysis_dir):
            if file_name.startswith("analysis_result_") and file_name.endswith(".json"):
                analysis_id = file_name.replace("analysis_result_", "").replace(".json", "")
                analyses.append({
                    "analysis_id": analysis_id,
                    "file_path": os.path.join(analysis_dir, file_name)
                })
        
        return analyses
