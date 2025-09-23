"""
Agent Interface for MeshLog Integrated Agent System

This module defines the base interface that all agents must implement
to be compatible with MeshLog's integrated module system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class AgentInterface(ABC):
    """Base interface for all MeshLog agents"""
    
    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return agent type identifier"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Return agent version"""
        pass
    
    @abstractmethod
    def analyze(self, log_paths: list, output_path: str, analysis_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main analysis method - follows the same pattern as service-based agents
        
        Args:
            log_paths: List of paths to log files to analyze
            output_path: Directory path where agent should write result files
            analysis_config: Optional configuration for the analysis
            
        Returns:
            Dict with status and basic metadata. Actual results should be written to output_path.
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return agent metadata"""
        return {
            "agent_type": self.agent_type,
            "name": self.agent_type,  # Frontend compatibility
            "version": self.version,
            "capabilities": getattr(self, 'capabilities', []),
            "supported_log_types": getattr(self, 'capabilities', []),  # Frontend compatibility
            "description": getattr(self, 'description', ''),
            "input_schema": getattr(self, 'input_schema', {}),
            "output_schema": getattr(self, 'output_schema', {})
        }
    
    def render_components(self, analysis_data: dict) -> dict:
        """Optional: Provide pre-rendered UI components"""
        return {}
    
    def validate_input(self, data: dict) -> bool:
        """Optional: Validate input data before processing"""
        return True
    
    def get_health_status(self) -> dict:
        """Optional: Provide health status information"""
        return {"status": "healthy"}