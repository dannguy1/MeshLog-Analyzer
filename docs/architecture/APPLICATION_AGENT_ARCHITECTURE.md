# Application/Agent Architecture - Detailed Specification

## 📋 Document Overview

This document provides a comprehensive architectural specification for the Application/Agent concept in MeshLog, designed to guide current implementation understanding and future extensions. It details the three-tier hierarchy (Projects → Applications → Agents), their relationships, implementation patterns, and extension guidelines.

## 🏗️ Three-Tier Hierarchical Architecture

MeshLog implements a **three-tier hierarchical architecture** that provides structured, scalable log analysis:

```
┌─────────────────────────────────────────────────────────────┐
│                    MeshLog System Architecture                │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │   PROJECTS   │      │ APPLICATIONS │      │  AGENTS  │  │
│  │              │      │              │      │          │  │
│  │ • Container  │      │ • Domain-    │      │ • Domain │  │
│  │   for log    │─────►│   Specific   │─────►│   Expert │  │
│  │   package    │ 1:N  │   Data       │ 1:1  │   Engine │  │
│  │              │      │              │      │          │  │
│  │ • Extraction │      │ • Discovery  │      │ • Analysis│  │
│  │ • Discovery  │      │ • Binding    │      │ • Insights│  │
│  │ • Metadata   │      │ • Storage    │      │ • Reports │  │
│  └──────────────┘      └──────────────┘      └──────────┘  │
│                                                             │
│           Projects contain Applications                     │
│           Applications bind to Agents                       │
│           Agents analyze Application data                   │
└─────────────────────────────────────────────────────────────┘
```

### Relationship Summary

- **Projects → Applications**: One-to-Many (1:N)
  - One project can contain multiple applications
  - Applications are discovered from log package contents
  - Each application represents a distinct PrplVAS LCM application type

- **Applications → Agents**: One-to-One (1:1) with Strict Binding
  - Each application type has exactly one corresponding agent
  - Binding is enforced at system level
  - Application name determines agent selection

- **Agents → Applications**: Domain-Specific Analysis
  - Agents are designed exclusively for their application type
  - Agents receive application-specific log data
  - Analysis results are stored per application

## 🎯 Core Concepts

### 1. Projects (Top-Level Container)

**Definition**: A Project is the top-level container representing a complete log analysis session for a specific log package.

#### Key Characteristics

- **Lifecycle Management**: Manages the complete workflow from upload to analysis completion
- **Package Management**: Handles log package upload, extraction, and storage
- **Multi-Application Support**: Can contain multiple applications discovered from the package
- **Metadata Persistence**: Stores comprehensive metadata about the package and analysis

#### Implementation Location

```12:14:app/models/core.py
class Project:
    """Project database model"""
    id: UUID
```

#### Project Lifecycle

```
1. Log Package Upload
   └─► Project Creation (UUID generated)
       └─► Package Extraction (files extracted to disk)
           └─► Application Discovery (applications identified)
               └─► Metadata Storage (discovery results saved)
                   └─► Analysis Ready (applications available for analysis)
```

#### Project Data Structure

**Storage Location**: `{DATA_DIR}/projects/{project_id}/`

**Key Files**:
- `extracted/` - Extracted log package contents
- `extracted/metadata/application_discovery.json` - Application discovery results
- `extracted/metadata/package_structure.json` - Package structure metadata
- `applications/{app_name}/` - Per-application data and results

### 2. Applications (Domain-Specific Data Containers)

**Definition**: An Application represents a specific PrplVAS LCM application type identified within a project's log package.

#### Key Characteristics

- **Domain-Specific**: Each application type has specific log patterns and analysis requirements
- **Data Isolation**: Each application's data is processed and stored separately
- **Strict Agent Binding**: Each application is bound to exactly one corresponding agent
- **Discovery-Based**: Applications are automatically discovered from log package contents

#### Supported Application Types

| Application Name | Domain | Agent Type | Description |
|-----------------|--------|------------|-------------|
| `wnc-steer` | WiFi Client Steering | `wnc-steering` | WiFi client steering and load balancing |
| `wnc-acs` | Auto Channel Selection | `wnc-acs` | Automatic WiFi channel selection optimization |
| `wnc-tpyopt` | Topology Optimization | `wnc-tpyopt` | WiFi network topology optimization |
| `wnc-iot` | IoT Device Management | `wnc-iot` | IoT device management (future) |
| `otbr-agent` | Thread Border Router | `otbr-agent` | OpenThread Border Router agent |

#### Application Discovery

Applications are discovered during package extraction through pattern matching and configuration file detection.

**Discovery Mechanism**:

```100:124:app/classifiers/application_classifier.py
    def classify_application(self, log_entries: List[LogEntry], container_id: str = "") -> List[ApplicationInfo]:
        """Classify applications based on log patterns"""
        logger.info(f"Classifying applications for container: {container_id}")
        
        if not log_entries:
            logger.warning("No log entries provided for classification")
            return []
        
        # Group entries by application name
        app_groups = {}
        for entry in log_entries:
            app_name = entry.application
            if app_name not in app_groups:
                app_groups[app_name] = []
            app_groups[app_name].append(entry)
        
        # Classify each application group
        application_infos = []
        for app_name, entries in app_groups.items():
            app_info = self._classify_single_application(app_name, entries, container_id)
            if app_info:
                application_infos.append(app_info)
        
        logger.info(f"Classification completed: {len(application_infos)} applications identified")
        return application_infos
```

**Pattern Matching**:

```20:98:app/classifiers/application_classifier.py
        # Application classification patterns
        self.application_patterns = {
            "wnc-steer": {
                "name": "WiFi Network Controller - Client Steering",
                "description": "Manages client steering and load balancing across WiFi access points",
                "patterns": [
                    r"steer_info",
                    r"sta_info\.mac",
                    r"weak signal clients",
                    r"RSSI",
                    r"client steering",
                    r"load balancing",
                    r"steering decision"
                ],
                "keywords": [
                    "steer", "client", "RSSI", "signal", "load", "balance", "decision"
                ],
                "config_files": [
                    "steer_config.json",
                    "client_config.json"
                ]
            },
            "wnc-acs": {
                "name": "WiFi Network Controller - Auto Channel Selection",
                "description": "Automatically selects optimal WiFi channels based on interference analysis",
                "patterns": [
                    r"channelList",
                    r"opClass",
                    r"X_PRPL-ORG_WiFiController",
                    r"channel selection",
                    r"interference",
                    r"auto channel"
                ],
                "keywords": [
                    "channel", "interference", "auto", "selection", "opClass", "WiFiController"
                ],
                "config_files": [
                    "acs_config.json",
                    "channel_config.json"
                ]
            },
```

#### Application Data Model

**Implementation**:

```1056:1084:app/models/core.py
class Application:
    """Application database model"""
    project_id: UUID
    container_id: str
    application_name: str
    id: UUID = field(default_factory=uuid4)
    functional_domain: Optional[str] = None
    relative_path: str = ""
    log_file_count: int = 0
    total_log_size_bytes: int = 0
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "container_id": self.container_id,
            "application_name": self.application_name,
            "functional_domain": self.functional_domain,
            "relative_path": self.relative_path,
            "log_file_count": self.log_file_count,
            "total_log_size_bytes": self.total_log_size_bytes,
            "time_range_start": self.time_range_start.isoformat() if self.time_range_start else None,
            "time_range_end": self.time_range_end.isoformat() if self.time_range_end else None,
            "confidence_score": self.confidence_score
        }
```

#### Application Storage Structure

```
{project_id}/
└── applications/
    └── {application_name}/
        ├── logs/              # Application-specific log files
        ├── metadata/          # Application metadata
        ├── application-analysis/  # Application-level analysis results
        └── agent-analysis/       # Agent-level analysis results
```

### 3. Agents (Specialized Analysis Engines)

**Definition**: An Agent is a specialized analysis engine that provides domain-specific analysis capabilities for a particular application type.

#### Key Characteristics

- **Domain Expertise**: Contains specialized knowledge for specific application domains
- **Strict Binding**: Each agent is exclusively designed for its corresponding application type
- **Standardized Interface**: All agents implement the `AgentInterface` abstract base class
- **Hybrid Execution**: Supports both integrated (Python module) and service-based (HTTP) execution modes
- **Result Standardization**: Agents produce standardized output formats

#### Agent Types and Binding

| Application | Agent Type | Implementation | Execution Mode |
|------------|------------|----------------|----------------|
| `wnc-steer` | `wnc-steering` | `WNCSteeringAgent` | Integrated |
| `wnc-acs` | `wnc-acs` | `WNCAcsAgent` | Integrated |
| `wnc-tpyopt` | `wnc-tpyopt` | `WNCTpyoptAgent` | Integrated |
| `otbr-agent` | `otbr-agent` | (Future) | Service/Integrated |
| Any | `template-agent` | `TemplateAgent` | Integrated |

#### Agent Interface

All agents must implement the `AgentInterface` abstract base class:

```11:60:app/core/agent_interface.py
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
```

#### Agent Discovery and Registry

**Agent Registry** manages integrated agent discovery and lifecycle:

```18:108:app/core/agent_registry.py
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
```

**Agent Package Structure**:

```1:18:app/agents/__init__.py
"""
MeshLog Agent System

This module contains all analysis agents integrated into MeshLog.
Agents are automatically discovered and loaded by the AgentRegistry.
"""

from .wnc_steering import WNCSteeringAgent
from .wnc_acs import WNCAcsAgent
from .wnc_tpyopt import WNCTpyoptAgent
from .template_agent import TemplateAgent

__all__ = [
    'WNCSteeringAgent',
    'WNCAcsAgent',
    'WNCTpyoptAgent',
    'TemplateAgent'
]
```

## 🔗 Application-Agent Binding

### Binding Mechanism

Applications are automatically mapped to agents through a deterministic mapping function:

```161:174:app/services/data_preparation_service.py
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
```

### Binding Rules

1. **Deterministic Mapping**: Application name determines agent type
2. **Case-Insensitive**: Matching is case-insensitive
3. **Pattern-Based**: Uses substring matching for flexibility
4. **Enforced at Runtime**: API validates binding before agent execution
5. **Error on Mismatch**: Invalid bindings return clear error messages

### Binding Validation

The system enforces binding rules at multiple levels:

1. **API Level**: Validates application-agent compatibility before processing
2. **Orchestrator Level**: Checks agent availability for requested application
3. **Agent Level**: Agents can validate incoming data matches their domain

## 🔄 System Data Flow

### Complete Application/Agent Analysis Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Application/Agent Data Flow                 │
└──────────────────────────────────────────────────────────────┘

1. LOG PACKAGE UPLOAD
   ┌─────────────────┐
   │ User uploads    │
   │ log package     │
   └────────┬────────┘
            │
            ▼
2. PROJECT CREATION
   ┌─────────────────┐
   │ • Generate UUID │
   │ • Create project│
   │ • Store package │
   └────────┬────────┘
            │
            ▼
3. PACKAGE EXTRACTION
   ┌─────────────────┐
   │ • Extract files │
   │ • Parse structure│
   └────────┬────────┘
            │
            ▼
4. APPLICATION DISCOVERY
   ┌─────────────────┐
   │ • Pattern match │
   │ • Classify apps │
   │ • Store metadata│
   └────────┬────────┘
            │
            ▼
5. APPLICATION-AGENT BINDING
   ┌─────────────────┐
   │ • Map app→agent │
   │ • Validate      │
   │ • Prepare data  │
   └────────┬────────┘
            │
            ▼
6. AGENT ANALYSIS EXECUTION
   ┌─────────────────┐
   │ • Get log paths │
   │ • Create agent  │
   │ • Execute       │
   │ • Store results │
   └────────┬────────┘
            │
            ▼
7. RESULTS STORAGE
   ┌─────────────────┐
   │ • Save results  │
   │ • Update metadata│
   │ • Return to API │
   └─────────────────┘
```

### Detailed Flow Components

#### 1. Application Discovery Flow

```
Package Extraction
    │
    ├─► Parse Container Structure
    │       │
    │       └─► Extract Log Files
    │               │
    │               └─► Parse Log Entries
    │                       │
    │                       └─► Application Classifier
    │                               │
    │                               ├─► Pattern Matching
    │                               ├─► Keyword Detection
    │                               └─► Config File Detection
    │                                       │
    │                                       └─► Application Discovery Results
    │                                               │
    │                                               └─► Store in application_discovery.json
```

**Metadata Storage**:

```850:885:app/models/core.py
@dataclass
class ApplicationDiscoveryMetadata:
    """Persistent metadata for application discovery"""
    project_id: str
    discovery_timestamp: datetime
    applications: List[ApplicationDiscoveryResult]
    discovery_methods_used: List[str]
    confidence_scores: Dict[str, float]
    validation_status: str
    
    def get_application_info(self, app_name: str) -> Optional[ApplicationDiscoveryResult]:
        """Get cached application information"""
        for app in self.applications:
            if app.application_name == app_name:
                return app
        return None
    
    def update_application_info(self, app_info: ApplicationDiscoveryResult):
        """Update cached application information"""
        # Update or add application information
        for i, existing_app in enumerate(self.applications):
            if existing_app.application_name == app_info.application_name:
                self.applications[i] = app_info
                return
        self.applications.append(app_info)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_id": self.project_id,
            "discovery_timestamp": self.discovery_timestamp.isoformat(),
            "applications": [app.to_dict() for app in self.applications],
            "discovery_methods_used": self.discovery_methods_used,
            "confidence_scores": self.confidence_scores,
            "validation_status": self.validation_status
        }
```

#### 2. Agent Execution Flow

**Orchestrator** routes requests to appropriate agent execution mode:

```32:88:app/core/agent_orchestrator.py
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
```

**Integrated Agent Execution**:

```157:199:app/core/agent_orchestrator.py
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
```

## 📁 Directory Structure and Data Organization

### Project-Level Structure

```
{DATA_DIR}/projects/{project_id}/
├── extracted/
│   ├── {container_id}/
│   │   └── messages (log files)
│   └── metadata/
│       ├── application_discovery.json    # Application discovery results
│       ├── package_structure.json        # Package structure metadata
│       └── extraction_info.json          # Extraction metadata
├── applications/
│   ├── {application_name}/
│   │   ├── logs/                         # Application-specific log files
│   │   ├── metadata/                     # Application metadata
│   │   ├── application-analysis/         # Application-level analysis
│   │   └── agent-analysis/               # Agent-level analysis results
│   │       ├── agent_data.json           # Agent analysis data
│   │       ├── agent_report.html         # HTML report
│   │       └── {other_output_files}      # Agent-specific outputs
└── project_metadata.json                 # Project-level metadata
```

### Application-Specific Data

Each application has its own directory structure:

```
applications/{application_name}/
├── logs/                                  # Log files for this application
├── metadata/
│   ├── application_info.json             # Application metadata
│   └── discovery_result.json             # Discovery result snapshot
├── application-analysis/                  # Application-level analysis results
│   └── {analysis_id}.json
└── agent-analysis/                        # Agent analysis results
    ├── agent_data.json                   # Main analysis data
    ├── agent_report.html                 # HTML report
    ├── agent_config.json                 # Analysis configuration used
    └── {additional_outputs}              # Agent-specific outputs
```

## 🔌 API Integration

### Application Discovery Endpoints

**Get Project Applications**:
```http
GET /api/v1/projects/{project_id}/applications
```

Returns list of applications discovered in the project with their metadata and agent bindings.

**Get Available Applications for Agent Analysis**:
```http
GET /api/v1/projects/{project_id}/applications/{application_name}/agent-analysis/available-applications
```

Returns applications ready for agent analysis with agent type mapping.

### Agent Analysis Endpoints

**Start Agent Analysis**:
```http
POST /api/v1/projects/{project_id}/applications/{application_name}/agent-analysis/start
```

Body:
```json
{
  "agent_type": "wnc-steering",
  "analysis_config": {
    "time_range": {...},
    "filters": {...}
  }
}
```

**Get Analysis Results**:
```http
GET /api/v1/projects/{project_id}/applications/{application_name}/agent-analysis/results?analysis_id={analysis_id}&format=html
```

**Get Analysis Status**:
```http
GET /api/v1/projects/{project_id}/applications/{application_name}/agent-analysis/status/{analysis_id}
```

## 🚀 Extension Guidelines

### Adding a New Application Type

To add support for a new application type:

#### 1. Update Application Classifier

Add pattern definitions to `app/classifiers/application_classifier.py`:

```python
self.application_patterns = {
    # ... existing patterns ...
    "new-app-name": {
        "name": "New Application Display Name",
        "description": "Description of the application",
        "patterns": [
            r"pattern1",
            r"pattern2"
        ],
        "keywords": [
            "keyword1", "keyword2"
        ],
        "config_files": [
            "config_file.json"
        ]
    }
}
```

#### 2. Create Corresponding Agent

Create a new agent class in `app/agents/new_agent.py`:

```python
from app.core.agent_interface import AgentInterface

class NewAgent(AgentInterface):
    @property
    def agent_type(self) -> str:
        return "new-agent"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def analyze(self, log_paths: list, output_path: str, analysis_config: Dict[str, Any] = None) -> Dict[str, Any]:
        # Implement analysis logic
        # Write results to output_path
        # Return status and metadata
        pass
```

#### 3. Register Agent

Add import to `app/agents/__init__.py`:

```python
from .new_agent import NewAgent

__all__ = [
    # ... existing agents ...
    'NewAgent'
]
```

#### 4. Update Agent Mapping

Update `_determine_agent_type` in `app/services/data_preparation_service.py`:

```python
def _determine_agent_type(self, app_name: str) -> Optional[str]:
    app_lower = app_name.lower()
    
    # ... existing mappings ...
    elif "new-app-name" in app_lower:
        return "new-agent"
    
    return None
```

#### 5. Test Discovery and Binding

1. Upload a log package containing the new application type
2. Verify application is discovered correctly
3. Verify agent mapping works
4. Test agent analysis execution
5. Verify results are stored correctly

### Adding a New Agent (Without New Application)

To add a new analysis agent for an existing application (e.g., alternative analysis):

#### 1. Create Agent Class

Follow the same pattern as creating an agent for a new application.

#### 2. Choose Agent Type Name

Use a descriptive, unique agent type name (e.g., `wnc-steering-v2`, `wnc-acs-enhanced`).

#### 3. Register Agent

Add to `app/agents/__init__.py`.

#### 4. Manual Agent Selection

For agents without automatic application binding, users can manually select the agent via the API:

```http
POST /api/v1/projects/{project_id}/applications/{application_name}/agent-analysis/start
```

With explicit `agent_type` in the request body.

### Best Practices for Agent Development

#### 1. Follow the Interface Contract

- Implement all required methods from `AgentInterface`
- Use standard method signatures
- Return data in expected formats

#### 2. Output Standardization

Agents should write results in standard formats:

- **agent_data.json**: Main analysis results in JSON format
- **agent_report.html**: Human-readable HTML report
- **Additional files**: Agent-specific outputs (CSV, charts, etc.)

#### 3. Error Handling

```python
def analyze(self, log_paths: list, output_path: str, analysis_config: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        # Analysis logic
        return {
            "status": "completed",
            "analysis_id": "...",
            "analysis_data": {...},
            "metadata": {...}
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": time.time()
        }
```

#### 4. Logging

Use structured logging:

```python
import structlog

logger = structlog.get_logger(__name__)

logger.info("Starting analysis", agent_type=self.agent_type, input_files=len(log_paths))
```

#### 5. Configuration Support

Support configuration through `analysis_config`:

```python
def analyze(self, log_paths: list, output_path: str, analysis_config: Dict[str, Any] = None) -> Dict[str, Any]:
    config = analysis_config or {}
    time_range = config.get("time_range")
    filters = config.get("filters", {})
    # Use configuration in analysis
```

#### 6. Metadata Documentation

Provide comprehensive metadata:

```python
def __init__(self):
    self.capabilities = ["feature1", "feature2"]
    self.description = "Clear description of what this agent does"
    self.input_schema = {
        "type": "object",
        "properties": {
            # Document expected input structure
        }
    }
    self.output_schema = {
        "type": "object",
        "properties": {
            # Document output structure
        }
    }
```

## 🔍 Example: WNC Steering Agent

The WNC Steering agent demonstrates a complete agent implementation:

**Agent Type**: `wnc-steering`  
**Application Binding**: `wnc-steer`  
**Implementation**: `app/agents/wnc_steering.py`

### Key Features

1. **Modular Components**: Uses separate analyzers and report generators
2. **Pattern Recognition**: Integrates with MeshLog's pattern recognition framework
3. **Comprehensive Analysis**: Provides multiple analysis dimensions
4. **Standard Output**: Produces JSON data and HTML reports

### Implementation Structure

```24:100:app/agents/wnc_steering.py
class WNCSteeringAgent(AgentInterface):
    """Enhanced WNC Steering Analysis Agent with comprehensive failure detection and modular architecture"""
    
    @property
    def agent_type(self) -> str:
        return "wnc-steering"
    
    @property
    def version(self) -> str:
        return "2.1.0-enhanced"
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize pattern recognition framework
        self.pattern_registry = PatternRegistry()
        self.pattern_interface = AgentPatternInterface("wnc-steering", self.pattern_registry)
        
        # Agent metadata
        self.capabilities = [
            "steering_analysis", 
            "client_transition_tracking", 
            "failure_pattern_detection",
            "bss_transition_analysis",
            "neighbor_report_analysis",
            "beacon_measurement_analysis",
            "enhanced_failure_patterns",
            "modular_components",
            "rssi_tracking",
            "client_capability_detection",
            "performance_metrics",
            "timeline_analysis",
            "html_report_generation",
            "csv_data_export",
            "actionable_insights"
        ]
        
        self.description = "Enhanced WNC WiFi Client Steering Agent with modular failure analysis and comprehensive pattern detection"
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "log_data": {
                    "type": "object",
                    "description": "Log data from MeshLog storage"
                },
                "analysis_config": {
                    "type": "object",
                    "properties": {
                        "time_range": {"type": "string"},
                        "client_filter": {"type": "string"},
                        "enable_enhanced_patterns": {"type": "boolean", "default": True},
                        "generate_html_report": {"type": "boolean", "default": True},
                        "include_raw_data": {"type": "boolean", "default": False}
                    }
                }
            }
        }
        
        self.output_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "analysis_data": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "object"},
                        "steering_events": {"type": "array"},
                        "failure_patterns": {"type": "object"},
                        "client_transitions": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                "metadata": {"type": "object"}
            }
        }
```

## 📚 Reference: Template Agent

For developers creating new agents, use the template agent as a starting point:

**Location**: `app/agents/template_agent.py`

**Key Features**:
- Minimal implementation demonstrating the interface
- Standard output format
- Basic error handling
- HTML report generation

**Usage**: Copy and modify for new agent development.

## 🎯 Summary

### Key Architectural Principles

1. **Separation of Concerns**: Projects, Applications, and Agents have distinct responsibilities
2. **Strict Binding**: One-to-one mapping between applications and agents ensures domain expertise
3. **Extensibility**: Clear patterns for adding new applications and agents
4. **Standardization**: Consistent interfaces and data formats across all components
5. **Discovery-Based**: Automatic application detection from log packages
6. **Hybrid Execution**: Support for both integrated and service-based agent execution

### Extension Checklist

When adding a new application/agent pair:

- [ ] Add application patterns to `ApplicationClassifier`
- [ ] Create agent class implementing `AgentInterface`
- [ ] Register agent in `app/agents/__init__.py`
- [ ] Update agent mapping function
- [ ] Test discovery workflow
- [ ] Test agent execution
- [ ] Verify result storage
- [ ] Document agent capabilities and schemas
- [ ] Update API documentation if needed

### Future Enhancements

Potential areas for extension:

1. **Dynamic Agent Selection**: Allow multiple agents per application with selection criteria
2. **Agent Composition**: Support chaining multiple agents for analysis pipelines
3. **Agent Versioning**: Support multiple versions of agents with version selection
4. **Remote Agents**: Enhanced support for service-based agents with health checking
5. **Agent Marketplace**: External agent registration and discovery
6. **Performance Optimization**: Caching and incremental analysis capabilities

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Related Documents**:
- [System Architecture Specification](./SYSTEM_ARCHITECTURE_SPECIFICATION.md)
- [Agent Analysis System Guide](./AGENT_ANALYSIS_SYSTEM_GUIDE.md)
- [System Summary](../overview/SYSTEM_SUMMARY.md)

