"""
Agent Service Client for wnc-log-agents integration
"""

import httpx
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import structlog
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

class AgentServiceClient:
    """Client for interacting with wnc-log-agents service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.WNC_LOG_AGENTS_URL
        self.timeout = self.settings.WNC_LOG_AGENTS_TIMEOUT
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if agent service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Agent service health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def list_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents and their capabilities"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/agents")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []
    
    async def can_process_application(self, app_name: str, log_files: List[Path]) -> Tuple[bool, str, float]:
        """Check if any agent can process the application logs"""
        agents = await self.list_available_agents()
        
        for agent in agents:
            agent_name = agent["name"]
            supported_types = agent["supported_log_types"]
            
            # Check if agent supports this application type
            if app_name in supported_types or any(app_name in log_type for log_type in supported_types):
                # Check first log file for compatibility
                if log_files:
                    try:
                        # This would need to be implemented as a separate endpoint
                        # For now, assume compatibility based on app name
                        return True, agent_name, 0.9
                    except Exception:
                        continue
        
        return False, "", 0.0
    
    async def start_analysis(
        self, 
        project_id: str, 
        app_name: str, 
        log_paths: List[str], 
        output_path: Path,
        agent_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start agent analysis for specific application"""
        try:
            # For now, send the first log path as input_path since agent service expects single path
            # TODO: Update agent service to handle multiple log paths
            input_path = log_paths[0] if log_paths else ""
            
            request_data = {
                "project_id": project_id,
                "application_name": app_name,
                "agent_type": agent_type,
                "input_path": input_path,
                "output_path": str(output_path),
                "config": {**(config or {}), "log_paths": log_paths}
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/analyze",
                json=request_data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to start agent analysis: {e}")
            raise
    
    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """Get analysis status"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/analysis/{analysis_id}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get analysis status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def wait_for_completion(self, analysis_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """Wait for analysis to complete"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < max_wait_time:
            status = await self.get_analysis_status(analysis_id)
            
            if status["status"] in ["completed", "failed"]:
                return status
            
            await asyncio.sleep(5)  # Poll every 5 seconds
        
        return {"status": "timeout", "error": "Analysis timed out"}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
