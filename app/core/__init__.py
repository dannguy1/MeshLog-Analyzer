"""
Core modules for MeshLog Integrated Agent System

This package contains the core components for the integrated agent system:
- AgentInterface: Base interface for all agents
- AgentRegistry: Agent discovery and management
- WorkspaceManager: Agent execution and data flow management
"""

from .agent_interface import AgentInterface
from .agent_registry import AgentRegistry
from .workspace_manager import WorkspaceManager

__all__ = [
    'AgentInterface',
    'AgentRegistry', 
    'WorkspaceManager'
]