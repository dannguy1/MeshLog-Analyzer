"""
Enhanced Project Analysis Manager with Agent Integration
Handles MeshLog's complete data preparation workflow before invoking agents
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import structlog
from app.services.project_analysis_manager import ProjectAnalysisManager
from app.services.data_preparation_service import DataPreparationService
from app.services.agent_service_client import AgentServiceClient
from app.services.file_system_integration import FileSystemIntegration
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

class EnhancedProjectAnalysisManager(ProjectAnalysisManager):
    """Enhanced project analysis manager with complete data preparation"""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self.settings = get_settings()
        self.data_preparation = DataPreparationService()
        self.agent_client = None
        self.fs_integration = FileSystemIntegration()
    
    async def create_project_with_complete_preparation(self, project_data: Dict[str, Any]):
        """
        Complete MeshLog workflow:
        1. Create project and complete MeshLog processing
        2. Prepare data for agent consumption
        3. Only invoke agents when data is ready
        """
        logger.info(f"Starting complete project preparation workflow")
        
        # Step 1: Complete MeshLog's standard project creation and processing
        project = await self.create_project(project_data)
        logger.info(f"MeshLog processing complete for project {project.id}")
        
        # Step 2: Prepare data for agent analysis (MeshLog's responsibility)
        if self.settings.WNC_LOG_AGENTS_ENABLED:
            preparation_result = await self.data_preparation.prepare_project_for_agent_analysis(
                str(project.id), project_data
            )
            
            # Step 3: Only invoke agents for applications with ready data
            ready_apps = [
                app for app in preparation_result["agent_candidates"] 
                if app["preparation_status"] == "ready"
            ]
            
            if ready_apps:
                await self._invoke_agents_for_ready_applications(str(project.id), ready_apps)
            else:
                logger.info("No applications ready for agent analysis")
        
        return project
    
    async def _invoke_agents_for_ready_applications(
        self, 
        project_id: str, 
        ready_apps: List[Dict[str, Any]]
    ):
        """Invoke agents only for applications with prepared data"""
        try:
            self.agent_client = AgentServiceClient()
            
            # Check agent service health before proceeding
            health = await self.agent_client.health_check()
            if health.get("status") != "healthy":
                logger.warning("Agent service not healthy, skipping agent invocation")
                return
            
            for app_info in ready_apps:
                app_name = app_info["app_name"]
                agent_type = app_info["agent_type"]
                
                # Verify data is actually ready
                if not self.data_preparation.is_data_ready_for_agent(project_id, app_name):
                    logger.warning(f"Data not ready for {app_name}, skipping agent invocation")
                    continue
                
                logger.info(f"Invoking {agent_type} agent for {app_name} (data ready)")
                
                # Get prepared paths
                shared_logs_path = Path(app_info["shared_logs_path"])
                agent_output_path = self.fs_integration.get_agent_output_path(project_id, app_name)
                
                # Start agent analysis
                analysis_response = await self.agent_client.start_analysis(
                    project_id=project_id,
                    app_name=app_name,
                    input_path=shared_logs_path,
                    output_path=agent_output_path,
                    agent_type=agent_type,
                    config={"meshlog_data_prepared": True}
                )
                
                logger.info(f"Started {agent_type} analysis: {analysis_response['analysis_id']}")
            
            await self.agent_client.close()
            
        except Exception as e:
            logger.error(f"Error invoking agents for ready applications: {e}")
    
    async def trigger_agent_analysis_for_application(
        self, 
        project_id: str, 
        app_name: str, 
        agent_type: str
    ) -> Dict[str, Any]:
        """
        Trigger agent analysis for a specific application.
        Only works if MeshLog has prepared the data.
        """
        try:
            # Verify data preparation is complete
            if not self.data_preparation.is_data_ready_for_agent(project_id, app_name):
                return {
                    "status": "error",
                    "message": "Data not prepared by MeshLog. Complete MeshLog processing first.",
                    "data_ready": False
                }
            
            # Initialize agent client
            self.agent_client = AgentServiceClient()
            
            # Get prepared paths
            shared_logs_path = self.fs_integration.prepare_logs_for_agent(
                project_id, app_name, 
                self.fs_integration.meshlog_data_path / "projects" / project_id / "applications" / app_name
            )
            agent_output_path = self.fs_integration.get_agent_output_path(project_id, app_name)
            
            # Start analysis
            analysis_response = await self.agent_client.start_analysis(
                project_id=project_id,
                app_name=app_name,
                input_path=shared_logs_path,
                output_path=agent_output_path,
                agent_type=agent_type,
                config={"meshlog_data_prepared": True}
            )
            
            await self.agent_client.close()
            
            return {
                "status": "initiated",
                "analysis_id": analysis_response["analysis_id"],
                "message": "Agent analysis started for prepared data",
                "data_ready": True
            }
            
        except Exception as e:
            logger.error(f"Error triggering agent analysis: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data_ready": False
            }
