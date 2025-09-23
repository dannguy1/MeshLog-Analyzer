"""
File System Integration for Agent Services
Handles shared file system operations between MeshLog and wnc-log-agents
"""

import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import structlog
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

class FileSystemIntegration:
    """Manages file system integration with agent services"""
    
    def __init__(self):
        self.settings = get_settings()
        self.meshlog_data_path = Path(self.settings.DATA_DIR)
    
    
    def prepare_application_specific_logs_for_agent(
        self,
        project_id: str,
        app_name: str,
        project_root_path: Path
    ) -> list:
        """Get application-specific log paths for agent processing using MeshLog's discovery data"""
        # Ensure project_root_path is absolute
        project_root_path = project_root_path.resolve()
        
        # Read MeshLog's application discovery data
        discovery_file = project_root_path / "extracted" / "metadata" / "application_discovery.json"
        
        if not discovery_file.exists():
            raise ValueError(f"Application discovery data not found: {discovery_file}")
        
        import json
        with open(discovery_file, 'r') as f:
            discovery_data = json.load(f)
        
        # Find containers for this specific application
        app_containers = [
            app for app in discovery_data["applications"] 
            if app["application_name"] == app_name
        ]
        
        if not app_containers:
            raise ValueError(f"No containers found for application {app_name}")
        
        # Return original source log file paths (no copying needed)
        log_paths = []
        for container_info in app_containers:
            container_id = container_info["container_id"]
            container_path = project_root_path / "extracted" / "Containerize" / container_id
            messages_file = container_path / "messages"
            
            if messages_file.exists():
                log_paths.append(str(messages_file))
                logger.info(f"Found logs for {app_name} from container {container_id}: {messages_file}")
        
        if not log_paths:
            raise ValueError(f"No log files found for application {app_name}")
        
        logger.info(f"Found {len(log_paths)} application-specific log paths for {app_name}")
        return log_paths
    
    def _container_has_app_logs(self, messages_file: Path, app_name: str) -> bool:
        """Check if a container's messages file contains logs for the specified application"""
        try:
            with open(messages_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first 100 lines to check for application logs
                for i, line in enumerate(f):
                    if i > 100:  # Limit check to first 100 lines for performance
                        break
                    if app_name in line.lower():
                        return True
            return False
        except Exception as e:
            logger.warning(f"Error checking container logs: {e}")
            return False
    
    def get_agent_output_path(self, project_id: str, app_name: str) -> Path:
        """Get the path where agent will write results (same as MeshLog data directory)"""
        return self.meshlog_data_path / "projects" / project_id / "applications" / app_name / "agent-analysis"
    
    def read_agent_results(self, output_path: Path) -> Dict[str, Any]:
        """Read agent analysis results from shared directory"""
        results = {
            "html_content": None,
            "json_data": None,
            "csv_data": None,
            "metadata": None
        }
        
        if not output_path.exists():
            return results
        
        # Look for HTML report
        html_files = list(output_path.glob("*.html"))
        if html_files:
            try:
                results["html_content"] = html_files[0].read_text(encoding='utf-8')
            except Exception as e:
                logger.warning(f"Failed to read HTML report: {e}")
        
        # Look for JSON data
        json_files = list(output_path.glob("*.json"))
        if json_files:
            try:
                import json
                results["json_data"] = json.loads(json_files[0].read_text(encoding='utf-8'))
            except Exception as e:
                logger.warning(f"Failed to read JSON data: {e}")
        
        # Look for CSV data
        csv_files = list(output_path.glob("*.csv"))
        if csv_files:
            try:
                results["csv_data"] = csv_files[0].read_text(encoding='utf-8')
            except Exception as e:
                logger.warning(f"Failed to read CSV data: {e}")
        
        # Look for metadata
        metadata_files = list(output_path.glob("*metadata*.json"))
        if metadata_files:
            try:
                import json
                results["metadata"] = json.loads(metadata_files[0].read_text(encoding='utf-8'))
            except Exception as e:
                logger.warning(f"Failed to read metadata: {e}")
        
        return results
    
    def ensure_agent_directory(self, project_id: str, app_name: str) -> Path:
        """Ensure agent analysis directory exists"""
        agent_path = self.meshlog_data_path / "projects" / project_id / "applications" / app_name / "agent-analysis"
        agent_path.mkdir(parents=True, exist_ok=True)
        return agent_path
