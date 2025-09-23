"""
Agent Registry for MeshLog Integrated Agent System

This module handles the discovery and management of integrated agents
using Python's module loading capabilities with configuration support.
"""

import importlib
import os
from pathlib import Path
from typing import Dict, List, Type, Any
from app.core.agent_interface import AgentInterface
from app.core.config import get_settings
import structlog

logger = structlog.get_logger(__name__)

class AgentRegistry:
    def __init__(self):
        self.settings = get_settings()
        self.agents_path = self.settings.INTEGRATED_AGENTS_PATH
        self.agents: Dict[str, Type[AgentInterface]] = {}
        
        # Only discover integrated agents if enabled
        if self.settings.INTEGRATED_AGENTS_ENABLED:
            self.discover_agents()
        else:
            logger.info("Integrated agents disabled by configuration")
    
    def discover_agents(self):
        """Discover and load agent modules with configuration support"""
        try:
            logger.info(f"Discovering agents from: {self.agents_path}")
            
            # Import agents package
            agents_module = importlib.import_module(self.agents_path)
            
            # Find all agent classes
            discovered_count = 0
            for attr_name in dir(agents_module):
                attr = getattr(agents_module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, AgentInterface) and 
                    attr != AgentInterface):
                    
                    # Create a temporary instance to get the agent_type
                    try:
                        temp_instance = attr()
                        agent_type = temp_instance.agent_type
                        # Store agent class
                        self.agents[agent_type] = attr
                        discovered_count += 1
                        logger.info(f"Discovered integrated agent: {agent_type}")
                    except Exception as e:
                        logger.warning(f"Error creating instance of {attr_name}: {e}")
            
            logger.info(f"Successfully discovered {discovered_count} integrated agents")
            
        except ImportError as e:
            logger.warning(f"Could not import agents module '{self.agents_path}': {e}")
        except Exception as e:
            logger.error(f"Error discovering agents: {e}")
    
    def refresh_agents(self):
        """Refresh agent discovery (useful for development)"""
        if self.settings.AGENT_DISCOVERY_AUTO_REFRESH:
            self.agents.clear()
            self.discover_agents()
            logger.info("Agent registry refreshed")
        else:
            logger.info("Agent auto-refresh disabled by configuration")
    
    def get_agent(self, agent_type: str) -> Type[AgentInterface]:
        """Get agent class by type"""
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type} not found")
        return self.agents[agent_type]
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent types"""
        return list(self.agents.keys())
    
    def create_agent(self, agent_type: str) -> AgentInterface:
        """Create agent instance"""
        agent_class = self.get_agent(agent_type)
        return agent_class()
    
    def get_agents_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all available agents"""
        agents = []
        for agent_type in self.agents.keys():
            agent = self.create_agent(agent_type)
            agents.append(agent.get_metadata())
        return agents
    
    def get_agent_execution_mode(self, agent_type: str) -> str:
        """Determine execution mode for an agent"""
        if agent_type in self.agents:
            return "integrated"
        else:
            return "service"
    
    def create_integrated_agent(self, agent_type: str) -> AgentInterface:
        """Create integrated agent instance (alias for create_agent for clarity)"""
        if agent_type not in self.agents:
            raise ValueError(f"Integrated agent {agent_type} not found")
        return self.create_agent(agent_type)
    
    def is_agent_available(self, agent_type: str) -> bool:
        """Check if an agent is available as integrated agent"""
        return agent_type in self.agents
    
    def get_agent_info(self, agent_type: str) -> Dict[str, Any]:
        """Get detailed information about a specific agent"""
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type} not found")
        
        agent = self.create_agent(agent_type)
        return {
            "agent_type": agent_type,
            "execution_mode": "integrated",
            "metadata": agent.get_metadata(),
            "class_name": self.agents[agent_type].__name__,
            "module": self.agents[agent_type].__module__
        }
    
    def validate_agent(self, agent_type: str) -> Dict[str, Any]:
        """Validate that an agent can be created and has required methods"""
        try:
            if agent_type not in self.agents:
                return {
                    "valid": False,
                    "error": f"Agent {agent_type} not found in registry"
                }
            
            # Try to create agent instance
            agent = self.create_agent(agent_type)
            
            # Check required methods
            required_methods = ["analyze", "get_metadata", "validate_input"]
            missing_methods = []
            
            for method in required_methods:
                if not hasattr(agent, method) or not callable(getattr(agent, method)):
                    missing_methods.append(method)
            
            if missing_methods:
                return {
                    "valid": False,
                    "error": f"Agent missing required methods: {missing_methods}"
                }
            
            # Try to get metadata
            metadata = agent.get_metadata()
            if not isinstance(metadata, dict):
                return {
                    "valid": False,
                    "error": "Agent metadata must return a dictionary"
                }
            
            return {
                "valid": True,
                "agent_type": agent_type,
                "metadata": metadata,
                "available_methods": [method for method in dir(agent) if not method.startswith('_')]
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error validating agent: {str(e)}"
            }
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get overall registry status and health"""
        return {
            "enabled": self.settings.INTEGRATED_AGENTS_ENABLED,
            "agents_path": self.agents_path,
            "total_agents": len(self.agents),
            "available_agents": list(self.agents.keys()),
            "auto_refresh": self.settings.AGENT_DISCOVERY_AUTO_REFRESH
        }