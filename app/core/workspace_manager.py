"""
Workspace Manager for MeshLog Integrated Agent System

This module manages agent execution and data flow within MeshLog,
providing a unified interface for log analysis using existing MeshLog infrastructure.
"""

from typing import Dict, Any, List
import time
import json
from pathlib import Path
from app.core.agent_registry import AgentRegistry
from app.services.application_data_manager import ApplicationDataManager
from app.core.config import get_settings
import structlog

logger = structlog.get_logger(__name__)

class WorkspaceManager:
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.settings = get_settings()
    
    async def analyze_logs(self, project_id: str, app_name: str, 
                          agent_type: str, analysis_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze logs using specified agent with real MeshLog data"""
        
        try:
            logger.info(f"Starting analysis: {agent_type} for {project_id}/{app_name}")
            
            # Get log data from MeshLog's ApplicationDataManager
            log_data = await self._get_log_data(project_id, app_name)
            
            # Create agent instance
            agent = self.agent_registry.create_agent(agent_type)
            
            # Prepare data for agent
            agent_data = {
                "project_id": project_id,
                "app_name": app_name,
                "log_data": log_data,
                "analysis_config": analysis_config or {}
            }
            
            # Execute analysis
            start_time = time.time()
            result = agent.analyze(agent_data)
            processing_time = time.time() - start_time
            
            # Add processing time to metadata
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"]["processing_time"] = processing_time
            result["metadata"]["data_source"] = "meshlog_integrated"
            
            # Store result using existing infrastructure
            await self._store_result(project_id, app_name, result)
            
            logger.info(f"Analysis completed: {agent_type} for {project_id}/{app_name} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {agent_type} for {project_id}/{app_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_id": f"error_{int(time.time())}",
                "metadata": {
                    "agent_type": agent_type,
                    "error_time": time.time(),
                    "project_id": project_id,
                    "app_name": app_name
                }
            }
    
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get available agents with metadata"""
        return self.agent_registry.get_agents_metadata()
    
    async def _get_log_data(self, project_id: str, app_name: str) -> Dict[str, Any]:
        """Get log data using MeshLog's ApplicationDataManager"""
        try:
            # Initialize ApplicationDataManager for this project/app
            data_manager = ApplicationDataManager(
                project_id=project_id,
                application_name=app_name,
                data_dir=str(self.settings.DATA_DIR)
            )
            
            # Get all log entries (using search with no filters to get all)
            log_entries = data_manager.search_logs(limit=10000)  # Get up to 10k entries
            
            # Get metadata
            metadata = data_manager.get_metadata()
            
            # Get file structure information
            files_info = []
            app_dir = Path(self.settings.DATA_DIR) / "projects" / project_id / "applications" / app_name
            if app_dir.exists():
                for log_file in app_dir.rglob("*.log"):
                    files_info.append({
                        "path": str(log_file),
                        "size": log_file.stat().st_size if log_file.exists() else 0,
                        "name": log_file.name
                    })
            
            # Structure data for agents
            structured_data = {
                "project_id": project_id,
                "app_name": app_name,
                "log_entries": log_entries,
                "metadata": metadata,
                "files": files_info,
                "total_entries": len(log_entries),
                "data_source": "application_data_manager",
                "timestamp": time.time()
            }
            
            logger.info(f"Retrieved {len(log_entries)} log entries for {project_id}/{app_name}")
            return structured_data
            
        except Exception as e:
            logger.error(f"Failed to get log data for {project_id}/{app_name}: {e}")
            # Return minimal structure on error
            return {
                "project_id": project_id,
                "app_name": app_name,
                "log_entries": [],
                "metadata": {},
                "files": [],
                "total_entries": 0,
                "data_source": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _store_result(self, project_id: str, app_name: str, result: Dict[str, Any]):
        """Store analysis result using MeshLog's infrastructure"""
        try:
            # Initialize ApplicationDataManager for this project/app
            data_manager = ApplicationDataManager(
                project_id=project_id,
                application_name=app_name,
                data_dir=str(self.settings.DATA_DIR)
            )
            
            # Store result in analysis_results
            analysis_id = result.get("analysis_id", f"analysis_{int(time.time())}")
            agent_type = result.get("metadata", {}).get("agent_type", "unknown")
            
            # Prepare result data for storage
            result_data = {
                "analysis_id": analysis_id,
                "agent_type": agent_type,
                "timestamp": time.time(),
                "status": result.get("status", "unknown"),
                "result": result,
                "metadata": {
                    "project_id": project_id,
                    "app_name": app_name,
                    "storage_method": "integrated_agent",
                    "stored_at": time.time()
                }
            }
            
            # Store in ApplicationDataManager
            data_manager.store_analysis_results({analysis_id: result_data})
            
            # Also store in dedicated agent results file for backward compatibility
            agent_results_path = Path(self.settings.DATA_DIR) / "projects" / project_id / "applications" / app_name / "agent_results"
            agent_results_path.mkdir(parents=True, exist_ok=True)
            
            result_file = agent_results_path / f"{agent_type}_{analysis_id}.json"
            with open(result_file, 'w') as f:
                json.dump(result_data, f, indent=2, default=str)
            
            logger.info(f"Stored analysis result: {analysis_id} for {project_id}/{app_name}")
            
        except Exception as e:
            logger.error(f"Failed to store result for {project_id}/{app_name}: {e}")
            # Don't raise exception here - analysis succeeded even if storage failed
