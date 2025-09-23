"""
Data Preparation Service for Agent Integration
Handles MeshLog's responsibility for preparing data for agent consumption
"""

import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import structlog
from app.core.config import get_settings
from app.services.file_system_integration import FileSystemIntegration

logger = structlog.get_logger(__name__)

class DataPreparationService:
    """Manages MeshLog's data preparation responsibilities for agent integration"""
    
    def __init__(self):
        self.settings = get_settings()
        self.fs_integration = FileSystemIntegration()
    
    async def prepare_project_for_agent_analysis(
        self, 
        project_id: str, 
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simplified MeshLog data preparation workflow:
        1. Find raw application data from log package
        2. Determine which applications need agent analysis
        3. Prepare raw logs for agent consumption
        """
        logger.info(f"Starting raw data preparation for project {project_id}")
        
        # Get project root path
        project_root_path = Path(project_data.get("project_root_path", "")).resolve()
        if not project_root_path.exists():
            raise ValueError(f"Project root path not found: {project_root_path}")
        
        # Step 1: Find applications with raw log data
        available_apps = self._find_applications_with_raw_logs(project_root_path)
        
        # Step 2: Identify applications that need specialized analysis
        agent_candidates = []
        for app_name in available_apps:
            agent_type = self._determine_agent_type(app_name)
            if agent_type:
                agent_candidates.append({
                    "app_name": app_name,
                    "agent_type": agent_type,
                    "confidence": 0.9,
                    "data_ready": True,
                    "preparation_status": "pending",
                    "raw_data_path": str(project_root_path)
                })
        
        # Step 3: Prepare raw logs for each agent candidate
        for app_info in agent_candidates:
            await self._prepare_raw_application_data_for_agent(project_id, app_info)
        
        return {
            "project_id": project_id,
            "raw_data_preparation_complete": True,
            "agent_candidates": agent_candidates,
            "preparation_timestamp": datetime.now().isoformat()
        }
    
    def _find_applications_with_raw_logs(self, project_root_path: Path) -> List[str]:
        """Find applications that have raw log data using MeshLog's discovery data"""
        applications = []
        
        # Read MeshLog's application discovery data
        discovery_file = project_root_path / "extracted" / "metadata" / "application_discovery.json"
        
        if not discovery_file.exists():
            logger.warning(f"Application discovery data not found: {discovery_file}")
            return applications
        
        import json
        with open(discovery_file, 'r') as f:
            discovery_data = json.load(f)
        
        # Extract unique application names from discovery data
        for app_info in discovery_data["applications"]:
            app_name = app_info["application_name"]
            if app_name not in applications:
                applications.append(app_name)
        
        logger.info(f"Found applications from discovery data: {applications}")
        return applications
    
    def _container_has_app_logs(self, messages_file: Path, app_name: str) -> bool:
        """Check if a container's messages file contains logs for the specified application"""
        try:
            with open(messages_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first 200 lines to check for application logs
                for i, line in enumerate(f):
                    if i > 200:  # Limit check to first 200 lines for performance
                        break
                    if app_name in line.lower():
                        return True
            return False
        except Exception as e:
            logger.warning(f"Error checking container logs: {e}")
            return False
    
    async def _complete_meshlog_processing(
        self, 
        project_id: str, 
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete MeshLog's standard data processing pipeline"""
        logger.info(f"Completing MeshLog processing for project {project_id}")
        
        # This would integrate with existing MeshLog processing:
        # - Package extraction
        # - Log parsing and structuring
        # - Application detection
        # - Basic analysis
        
        # For now, return structured data indicating processing is complete
        return {
            "extraction_complete": True,
            "parsing_complete": True,
            "application_detection_complete": True,
            "basic_analysis_complete": True,
            "applications": project_data.get("applications", []),
            "log_files_processed": project_data.get("log_count", 0)
        }
    
    async def _identify_agent_candidates(
        self, 
        processed_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify applications that would benefit from specialized agent analysis"""
        candidates = []
        
        if not self.settings.WNC_LOG_AGENTS_ENABLED:
            return candidates
        
        applications = processed_data.get("applications", [])
        
        for app_name in applications:
            # Check if this application type has specialized agents available
            agent_type = self._determine_agent_type(app_name)
            
            if agent_type:
                candidates.append({
                    "app_name": app_name,
                    "agent_type": agent_type,
                    "confidence": 0.9,
                    "data_ready": True,
                    "preparation_status": "pending"
                })
        
        logger.info(f"Identified {len(candidates)} agent candidates: {[c['app_name'] for c in candidates]}")
        return candidates
    
    def _determine_agent_type(self, app_name: str) -> Optional[str]:
        """Determine which agent type should be used for this application"""
        app_lower = app_name.lower()
        
        if "wnc-steer" in app_lower or "steering" in app_lower:
            return "wnc-steering"
        elif "wnc-acs" in app_lower or "acs" in app_lower:
            return "wnc-acs"
        elif "wnc-tpyopt" in app_lower or "tpyopt" in app_lower:
            return "wnc-tpyopt"
        elif "otbr-agent" in app_lower:
            return "otbr-agent"
        
        return None
    
    async def _prepare_raw_application_data_for_agent(
        self, 
        project_id: str, 
        app_info: Dict[str, Any]
    ):
        """Prepare raw application data for agent consumption"""
        app_name = app_info["app_name"]
        agent_type = app_info["agent_type"]
        project_root_path = Path(app_info["raw_data_path"])
        
        logger.info(f"Preparing raw data for {agent_type} analysis of {app_name}")
        
        # Set up shared directory structure
        project_paths = self.fs_integration.setup_project_structure(project_id)
        
        # Get original source log file paths (no copying)
        log_paths = self.fs_integration.prepare_application_specific_logs_for_agent(
            project_id, app_name, project_root_path
        )
        
        # Create agent configuration
        agent_config = self._create_raw_agent_configuration(
            project_id, app_name, agent_type, log_paths, project_root_path
        )
        
        # Write configuration to shared directory
        config_path = self.fs_integration.get_agent_output_path(project_id, app_name) / "agent_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(agent_config, indent=2))
        
        # Update app info
        app_info["preparation_status"] = "ready"
        app_info["log_paths"] = log_paths
        app_info["agent_config_path"] = str(config_path)
        
        logger.info(f"Raw data preparation complete for {app_name} -> {agent_type}")
    
    def _create_raw_agent_configuration(
        self, 
        project_id: str, 
        app_name: str, 
        agent_type: str, 
        log_paths: list,
        project_root_path: Path
    ) -> Dict[str, Any]:
        """Create agent-specific configuration for raw data"""
        return {
            "meshlog_project_id": project_id,
            "application_name": app_name,
            "agent_type": agent_type,
            "log_paths": log_paths,
            "output_path": str(self.fs_integration.get_agent_output_path(project_id, app_name)),
            "config": {
                "include_raw_data": True,
                "generate_consolidated_report": True,
                "detailed_analysis": True,
                "meshlog_integration_mode": True,
                "raw_data_mode": True,
                "preparation_timestamp": datetime.now().isoformat()
            },
            "meshlog_metadata": {
                "raw_data_preparation_complete": True,
                "logs_from_log_package": True,
                "application_detected_from_raw_logs": True,
                "ready_for_agent_analysis": True,
                "project_root_path": str(project_root_path)
            }
        }
    
    def is_data_ready_for_agent(self, project_id: str, app_name: str) -> bool:
        """Check if data is ready for agent analysis"""
        agent_output_path = self.fs_integration.get_agent_output_path(project_id, app_name)
        config_file = agent_output_path / "agent_config.json"
        
        return config_file.exists() and config_file.stat().st_size > 0

    def get_application_log_paths(self, project_id: str, application_name: str) -> List[str]:
        """Get log file paths for a specific application"""
        try:
            # Load project data to get project_root_path
            projects_file = Path(self.settings.DATA_DIR) / "projects.json"
            if not projects_file.exists():
                raise ValueError(f"Projects file not found: {projects_file}")
            
            with open(projects_file, 'r') as f:
                projects_data = json.load(f)
            
            project_data = projects_data.get(project_id)
            if not project_data:
                raise ValueError(f"Project {project_id} not found")
            
            project_root_path = Path(project_data.get("project_root_path", ""))
            if not project_root_path.exists():
                raise ValueError(f"Project root path not found: {project_root_path}")
            
            # Use FileSystemIntegration to get log paths
            log_paths = self.fs_integration.prepare_application_specific_logs_for_agent(
                project_id=project_id,
                app_name=application_name,
                project_root_path=project_root_path
            )
            
            return log_paths
            
        except Exception as e:
            logger.error(f"Failed to get log paths for {project_id}/{application_name}: {e}")
            raise
