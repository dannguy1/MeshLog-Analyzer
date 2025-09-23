"""
Hybrid Agent Orchestrator
Supports both current service-based and future integrated agent execution
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import structlog

from app.core.config import get_settings
from app.core.agent_registry import AgentRegistry
from app.services.agent_service_client import AgentServiceClient

logger = structlog.get_logger(__name__)

class AgentOrchestrator:
    """
    Hybrid orchestrator that can work with both:
    1. Current persistent wnc-log-agents service
    2. Future integrated agents as Python modules
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.agent_registry = AgentRegistry()
        self.active_analyses = {}
        self.analysis_history = []
    
    async def analyze_logs(self, 
                          project_id: str, 
                          application_name: str,
                          agent_type: str, 
                          log_data: dict,
                          analysis_config: dict = None) -> dict:
        """
        Main entry point for log analysis
        Currently uses service-based approach, will support on-demand in future
        """
        
        # Generate analysis ID
        analysis_id = f"{project_id}_{application_name}_{agent_type}_{int(datetime.now().timestamp())}"
        
        try:
            logger.info(f"Starting analysis {analysis_id} for {application_name} using {agent_type}")
            
            # Store analysis info
            self.active_analyses[analysis_id] = {
                "status": "initiated",
                "start_time": datetime.now(),
                "project_id": project_id,
                "application_name": application_name,
                "agent_type": agent_type,
                "config": analysis_config or {}
            }
            
            # Check execution mode and route accordingly
            execution_mode = self.agent_registry.get_agent_execution_mode(agent_type)
            
            if execution_mode == "integrated":
                result = await self._analyze_with_integrated_agent(project_id, application_name, agent_type, log_data, analysis_config)
            else:  # service mode
                result = await self._analyze_with_service(project_id, application_name, agent_type, log_data, analysis_config)
            
            # Update analysis status
            self.active_analyses[analysis_id].update({
                "status": "completed",
                "end_time": datetime.now(),
                "result": result
            })
            
            # Store in history
            self._add_to_history(analysis_id)
            
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "result": result,
                "metadata": {
                    "project_id": project_id,
                    "application_name": application_name,
                    "agent_type": agent_type,
                    "start_time": self.active_analyses[analysis_id]["start_time"].isoformat(),
                    "end_time": self.active_analyses[analysis_id]["end_time"].isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}")
            
            # Update analysis status
            if analysis_id in self.active_analyses:
                self.active_analyses[analysis_id].update({
                    "status": "failed",
                    "end_time": datetime.now(),
                    "error": str(e)
                })
                self._add_to_history(analysis_id)
            
            return {
                "analysis_id": analysis_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_with_service(self, project_id: str, application_name: str, 
                                   agent_type: str, log_data: dict, 
                                   analysis_config: dict = None) -> dict:
        """Use current service-based approach"""
        try:
            client = AgentServiceClient()
            
            # Get log paths for the application
            from app.services.data_preparation_service import DataPreparationService
            data_service = DataPreparationService()
            log_paths = data_service.get_application_log_paths(project_id, application_name)
            
            if not log_paths:
                raise ValueError(f"No log files found for application {application_name}")
            
            # Set up agent output path
            agent_output_path = Path(self.settings.DATA_DIR) / "projects" / project_id / "applications" / application_name / "agent_results"
            
            # Start agent analysis using current service
            analysis_response = await client.start_analysis(
                app_name=application_name,
                log_paths=log_paths,
                output_path=agent_output_path,
                agent_type=agent_type,
                config=analysis_config or {"raw_data_mode": True, "meshlog_raw_data": True}
            )
            
            # Wait for completion
            final_status = await client.wait_for_completion(analysis_response["analysis_id"])
            
            if final_status["status"] == "completed":
                # Read and return results
                from app.services.file_system_integration import FileSystemIntegration
                fs_integration = FileSystemIntegration()
                agent_results = fs_integration.read_agent_results(agent_output_path)
                
                return {
                    "status": "completed",
                    "analysis_data": agent_results,
                    "output_path": str(agent_output_path),
                    "method": "service_based"
                }
            else:
                raise Exception(f"Agent analysis failed: {final_status}")
                
        finally:
            await client.close()
    
    async def _analyze_with_integrated_agent(self, project_id: str, application_name: str, 
                                            agent_type: str, log_data: dict, 
                                            analysis_config: dict = None) -> dict:
        """Use integrated agent (follows same pattern as service agents)"""
        try:
            # Create agent instance
            agent = self.agent_registry.create_integrated_agent(agent_type)
            
            # Set up output path (same as service agents)
            agent_output_path = Path(self.settings.DATA_DIR) / "projects" / project_id / "applications" / application_name / "agent-analysis"
            agent_output_path.mkdir(parents=True, exist_ok=True)
            
            # Get log paths for the application
            from app.services.data_preparation_service import DataPreparationService
            data_service = DataPreparationService()
            log_paths = data_service.get_application_log_paths(project_id, application_name)
            
            if not log_paths:
                raise ValueError(f"No log files found for application {application_name}")
            
            # Execute analysis with same interface as service agents
            result = agent.analyze(
                log_paths=log_paths,
                output_path=str(agent_output_path),
                analysis_config=analysis_config or {}
            )
            
            # Read results from files (same as service agents)
            from app.services.file_system_integration import FileSystemIntegration
            fs_integration = FileSystemIntegration()
            agent_results = fs_integration.read_agent_results(agent_output_path)
            
            return {
                "status": "completed",
                "analysis_data": agent_results,
                "output_path": str(agent_output_path),
                "execution_mode": "integrated",
                "agent_metadata": agent.get_metadata()
            }
            
        except Exception as e:
            logger.error(f"Integrated agent analysis failed: {e}")
            raise
    
    def _should_use_spawning(self, agent_type: str) -> bool:
        """Determine whether to use spawning or service for this agent type"""
        # Future logic to decide between spawning and service
        # For now, always use service
        return False
    
    def _add_to_history(self, analysis_id: str):
        """Add analysis to history"""
        if analysis_id in self.active_analyses:
            analysis = self.active_analyses[analysis_id].copy()
            analysis["analysis_id"] = analysis_id
            self.analysis_history.append(analysis)
    
    async def get_analysis_status(self, analysis_id: str) -> dict:
        """Get status of analysis"""
        if analysis_id not in self.active_analyses:
            # Check history
            for historical in self.analysis_history:
                if historical["analysis_id"] == analysis_id:
                    return {
                        "analysis_id": analysis_id,
                        "status": historical["status"],
                        "project_id": historical["project_id"],
                        "application_name": historical["application_name"],
                        "agent_type": historical["agent_type"]
                    }
            raise ValueError(f"Analysis {analysis_id} not found")
        
        analysis = self.active_analyses[analysis_id]
        
        return {
            "analysis_id": analysis_id,
            "status": analysis["status"],
            "project_id": analysis["project_id"],
            "application_name": analysis["application_name"],
            "agent_type": analysis["agent_type"],
            "start_time": analysis["start_time"].isoformat(),
            "error": analysis.get("error")
        }
    
    async def get_analysis_result(self, analysis_id: str) -> dict:
        """Get analysis result"""
        if analysis_id not in self.active_analyses:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        analysis = self.active_analyses[analysis_id]
        
        if analysis["status"] != "completed":
            raise ValueError(f"Analysis {analysis_id} not completed")
        
        return analysis["result"]
    
    def get_available_agents(self) -> List[dict]:
        """Get list of available agents with metadata from registry"""
        return self.agent_registry.get_agents_metadata()
    
    def get_analysis_history(self, project_id: str = None) -> List[dict]:
        """Get analysis history"""
        if project_id:
            return [a for a in self.analysis_history if a["project_id"] == project_id]
        return self.analysis_history