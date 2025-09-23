# MeshLog System Architecture Specification

## 📋 Document Overview

This document provides a comprehensive system architecture specification for MeshLog, clearly describing the concepts of **Projects**, **Applications**, and **Agents** and their relationships within the system.

## 🏗️ System Architecture Overview

MeshLog implements a **three-tier hierarchical architecture** that provides structured log analysis capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    MeshLog System Architecture                │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │     PROJECTS    │  │   APPLICATIONS   │  │    AGENTS   │ │
│  │                 │  │                 │  │             │ │
│  │ • Log Package   │  │ • wnc-steer     │  │ • wnc-steer │ │
│  │   Management    │  │ • wnc-acs       │  │ • wnc-acs   │ │
│  │ • Extraction    │  │ • wnc-tpyopt    │  │ • wnc-tpyopt│ │
│  │ • Discovery     │  │ • wnc-iot       │  │ • wnc-iot   │ │
│  │ • Metadata      │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│           │                       │                       │
│           │              ┌────────┴────────┐              │
│           │              │  STRICT BINDING │              │
│           │              │  wnc-steer ────► wnc-steering  │
│           │              │  wnc-acs ──────► wnc-acs       │
│           │              │  wnc-tpyopt ───► wnc-tpyopt    │
│           │              │  wnc-iot ──────► wnc-iot       │
│           │              └─────────────────┘              │
│           ▼                       ▼                       ▼
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              ANALYSIS ARCHITECTURE                      │ │
│  │                                                         │ │
│  │  Application Analysis (Foundation)                      │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │ • Log Parsing & Cleaning                        │   │ │
│  │  │ • Message Type Classification                   │   │ │
│  │  │ • Data Standardization                          │   │ │
│  │  │ • Basic Analytics                               │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  │                           │                             │ │
│  │                           ▼                             │ │
│  │  Agent Analysis (Advanced)                             │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │ • Domain-Specific Analysis                      │   │ │
│  │  │ • Pattern Recognition                           │   │ │
│  │  │ • Business Logic                                │   │ │
│  │  │ • Insight Generation                            │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Core Concepts

### 1. Projects (Top-Level Container)

**Definition**: A Project is the top-level container that represents a complete log analysis session for a specific log package.

**Key Characteristics**:
- **One-to-One Relationship**: Each log package upload creates exactly one project
- **Unique Identity**: Each project has a unique UUID identifier
- **Lifecycle Management**: Manages the complete lifecycle from upload to analysis completion
- **Multi-Application Support**: A single project can contain data for multiple applications

**Project Components**:
- **Project Metadata**: Name, description, upload timestamp, file information
- **Package Structure**: Original log package file and extraction metadata
- **Application Discovery**: Identified applications within the package
- **Analysis History**: Track of all analyses performed on the project

**Project Lifecycle**:
```
Log Package Upload → Project Creation → Package Extraction → Application Discovery → Analysis Execution → Results Storage
```

### 2. Applications (Domain-Specific Data Containers)

**Definition**: An Application represents a specific PrplVAS LCM application type (e.g., wnc-steer, wnc-acs, wnc-tpyopt, wnc-iot) identified within a project's log package.

**Key Characteristics**:
- **One-to-Many Relationship**: A project can contain multiple applications
- **Domain-Specific**: Each application type has specific log patterns and analysis requirements
- **Data Isolation**: Each application's data is processed and stored separately
- **Agent Association**: Each application can invoke its corresponding specialized agent

**Application Types**:
- **wnc-steer**: WiFi client steering behavior analysis
- **wnc-acs**: Auto Channel Selection optimization analysis
- **wnc-tpyopt**: Topology optimization analysis
- **wnc-iot**: IoT device management analysis

**Application Components**:
- **Raw Log Data**: Application-specific log files extracted from the package
- **Processed Data**: Cleaned and classified data from Application Analysis
- **Analysis Results**: Results from both Application and Agent Analysis
- **Metadata**: Application-specific metadata and configuration
- **Agent Binding**: Each application is strictly bound to its corresponding agent

### 3. Agents (Specialized Analysis Engines)

**Definition**: An Agent is a specialized analysis engine that provides domain-specific analysis capabilities for a particular application type.

**Key Characteristics**:
- **One-to-One Mapping**: Each application type has a corresponding agent
- **Application-Specific**: Agents are designed exclusively for their corresponding application type
- **Strict Binding**: Applications can only invoke their designated agent (e.g., wnc-steer application can only invoke wnc-steering agent)
- **Domain Expertise**: Contains specialized knowledge for specific application domains
- **Two-Tier Analysis**: Provides both Application Analysis and Agent Analysis capabilities
- **Integrated Execution**: Runs within the MeshLog system for optimal performance

**Agent Architecture**:
- **Application Analysis**: Foundation layer for data processing and cleanup
- **Agent Analysis**: Advanced layer for domain-specific insights and recommendations

## 🔄 System Data Flow

### Complete Processing Pipeline

```
1. LOG PACKAGE UPLOAD
   ┌─────────────────┐
   │ User uploads     │
   │ .tar/.tar.gz    │
   │ log package     │
   └─────────────────┘
           │
           ▼

2. PROJECT CREATION
   ┌─────────────────┐
   │ • Generate UUID │
   │ • Create project│
   │ • Save metadata │
   │ • Store package │
   └─────────────────┘
           │
           ▼

3. PACKAGE EXTRACTION
   ┌─────────────────┐
   │ • Extract files │
   │ • Parse structure│
   │ • Generate hash │
   │ • Validate data │
   └─────────────────┘
           │
           ▼

4. APPLICATION DISCOVERY
   ┌─────────────────┐
   │ • Scan log files│
   │ • Identify apps │
   │ • Generate      │
   │   metadata      │
   │ • Create app    │
   │   containers    │
   └─────────────────┘
           │
           ▼

5. APPLICATION ANALYSIS
   ┌─────────────────┐
   │ • Parse logs    │
   │ • Clean data    │
   │ • Add message_  │
   │   type          │
   │ • Store results │
   └─────────────────┘
           │
           ▼

6. AGENT ANALYSIS
   ┌─────────────────┐
   │ • Domain        │
   │   analysis      │
   │ • Pattern       │
   │   recognition   │
   │ • Generate      │
   │   insights      │
   │ • Create reports│
   └─────────────────┘
           │
           ▼

7. RESULTS STORAGE
   ┌─────────────────┐
   │ • Store analysis│
   │   results       │
   │ • Update        │
   │   metadata      │
   │ • Enable        │
   │   visualization │
   └─────────────────┘
```

## 📁 Directory Structure

### Project-Level Structure
```
data/
└── projects/
    └── {project_id}/
        ├── extracted/                    # Extracted log files
        │   ├── metadata/
        │   │   ├── package_structure.json
        │   │   └── application_discovery.json
        │   └── {container_id}/
        │       └── {log_files}
        ├── applications/                 # Application-specific data
        │   ├── wnc-steer/
        │   │   ├── analysis_metadata.json
        │   │   ├── processed_data/
        │   │   └── agent_results/
        │   ├── wnc-acs/
        │   │   ├── analysis_metadata.json
        │   │   ├── processed_data/
        │   │   └── agent_results/
        │   └── wnc-tpyopt/
        │       ├── analysis_metadata.json
        │       ├── processed_data/
        │       └── agent_results/
        └── project_metadata.json         # Project-level metadata
```

## 🔧 Component Specifications

### Project Component

**Purpose**: High-level project data management and coordination

**Responsibilities**:
- **Package Management**: Handle log package upload, storage, and extraction
- **Application Discovery**: Identify applications within the log package
- **Metadata Management**: Maintain project-level metadata and configuration
- **Lifecycle Coordination**: Coordinate the complete analysis lifecycle
- **User Interface**: Provide project selection and management capabilities

**Key Classes**:
- `Project`: Core project data model
- `ProjectService`: Project management service
- `ProjectAnalysisManager`: Project-scoped analysis management
- `PackageProcessor`: Log package extraction and processing

**API Endpoints**:
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/` - List all projects
- `GET /api/v1/projects/{project_id}` - Get project details
- `DELETE /api/v1/projects/{project_id}` - Delete project

### Application Component

**Purpose**: Application-specific data processing and management

**Responsibilities**:
- **Data Processing**: Clean and standardize application-specific log data
- **Message Classification**: Add `message_type` field to log entries
- **Data Storage**: Store processed data in application-specific directories
- **Analysis Coordination**: Coordinate Application Analysis and Agent Analysis
- **Metadata Management**: Maintain application-specific metadata

**Key Classes**:
- `ApplicationDataManager`: Application data management
- `ApplicationDiscoveryResult`: Application discovery metadata
- `ApplicationDiscoveryMetadata`: Application discovery results

**API Endpoints**:
- `GET /api/v1/projects/{project_id}/applications/` - List applications in project
- `GET /api/v1/projects/{project_id}/applications/{app_name}/` - Get application details
- `POST /api/v1/projects/{project_id}/applications/{app_name}/analyze/` - Start application analysis

### Agent Component

**Purpose**: Specialized domain-specific analysis

**Responsibilities**:
- **Domain Analysis**: Perform specialized analysis for specific application types
- **Pattern Recognition**: Use advanced pattern matching for insights
- **Business Logic**: Apply application-specific rules and algorithms
- **Insight Generation**: Create actionable recommendations
- **Report Generation**: Generate specialized reports and visualizations
- **Application Validation**: Ensure agents only process data from their designated application type

**Key Classes**:
- `AgentInterface`: Base interface for all agents
- `AgentRegistry`: Agent discovery and management
- `AgentOrchestrator`: Agent execution coordination
- `WorkspaceManager`: Agent workspace and data integration

### **Agent Interface Specification**

#### **AgentInterface Base Class**
```python
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
```

#### **Implementation Requirements**

**Required Methods**:
- `agent_type`: Must return a unique string identifier
- `version`: Must return the agent version string
- `analyze`: Must implement the core analysis logic

**Optional Methods**:
- `get_metadata`: Provides agent metadata (default implementation available)
- `render_components`: Provides UI components for results display
- `validate_input`: Validates input data before processing
- `get_health_status`: Provides health status information

#### **Agent Implementation Example**
```python
class WNCSteeringAgent(AgentInterface):
    """WiFi Steering Analysis Agent"""
    
    @property
    def agent_type(self) -> str:
        return "wnc-steering-agent"
    
    @property
    def version(self) -> str:
        return "2.1.0"
    
    def analyze(self, log_paths: list, output_path: str, analysis_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform WiFi steering analysis"""
        try:
            # Analysis logic here
            results = self._perform_steering_analysis(log_paths, analysis_config)
            
            # Write results to output_path
            self._write_results(results, output_path)
            
            return {
                "status": "completed",
                "analysis_type": "wnc-steering",
                "files_processed": len(log_paths),
                "results_path": output_path
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _perform_steering_analysis(self, log_paths: list, config: Dict[str, Any]) -> Dict[str, Any]:
        """Internal analysis implementation"""
        # Agent-specific analysis logic
        pass
    
    def _write_results(self, results: Dict[str, Any], output_path: str) -> None:
        """Write analysis results to output directory"""
        # Write results to files
        pass
```

#### **Agent Registry Integration**

**Agent Discovery**:
```python
# Agents are automatically discovered by the AgentRegistry
# They must be imported in the agents package
from app.agents.wnc_steering_agent import WNCSteeringAgent
from app.agents.wnc_acs_agent import WNCAcsAgent
from app.agents.wnc_tpyopt_agent import WNCTpyoptAgent
```

**Agent Execution Modes**:
- **Integrated Mode**: Agents run as Python modules within the application
- **Service Mode**: Agents run as external HTTP services (legacy support)

#### **Agent Configuration**

**Configuration Schema**:
```json
{
  "agent_type": "wnc-steering-agent",
  "version": "2.1.0",
  "capabilities": ["steering_analysis", "pattern_detection"],
  "description": "WiFi Steering Analysis Agent",
  "input_schema": {
    "log_paths": {"type": "array", "items": {"type": "string"}},
    "analysis_config": {"type": "object"}
  },
  "output_schema": {
    "status": {"type": "string"},
    "results_path": {"type": "string"},
    "files_processed": {"type": "integer"}
  }
}
```

#### **Agent Development Guidelines**

**1. Naming Convention**:
- Class names: `{Domain}Agent` (e.g., `WNCSteeringAgent`)
- Agent types: `{domain}-agent` (e.g., `wnc-steering-agent`)
- File names: `{domain}_agent.py` (e.g., `wnc_steering_agent.py`)

**2. Error Handling**:
```python
def analyze(self, log_paths: list, output_path: str, analysis_config: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        # Analysis logic
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"status": "failed", "error": str(e)}
```

**3. Result Writing**:
```python
def _write_results(self, results: Dict[str, Any], output_path: str) -> None:
    """Write results to output directory"""
    os.makedirs(output_path, exist_ok=True)
    
    # Write main results
    with open(os.path.join(output_path, "analysis_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    # Write additional files as needed
    # - Charts, graphs, reports, etc.
```

**4. Input Validation**:
```python
def validate_input(self, data: dict) -> bool:
    """Validate input data before processing"""
    required_fields = ["log_paths", "output_path"]
    return all(field in data for field in required_fields)
```

**Available Agents**:
- `WNCSteeringAgent`: WiFi steering analysis (exclusively for wnc-steer application)
- `WNCAcsAgent`: Auto Channel Selection analysis (exclusively for wnc-acs application)
- `WNCTpyoptAgent`: Topology optimization analysis (exclusively for wnc-tpyopt application)
- `TemplateAgent`: Generic agent template

**API Endpoints**:
- `POST /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/start` - Start agent analysis
- `GET /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/{analysis_id}` - Get agent analysis results

## 🔒 Application-Agent Binding Rules

### Strict Binding Requirements

**Core Principle**: Each application type can only invoke its corresponding specialized agent. This binding is enforced at the system level to ensure data integrity and analysis accuracy.

### Binding Matrix

| Application Type | Allowed Agent | Prohibited Agents | Reason |
|------------------|---------------|-------------------|---------|
| **wnc-steer** | wnc-steering-agent | wnc-acs-agent, wnc-tpyopt-agent, wnc-iot-agent | Steering agent designed exclusively for steering data patterns |
| **wnc-acs** | wnc-acs-agent | wnc-steering-agent, wnc-tpyopt-agent, wnc-iot-agent | ACS agent designed exclusively for channel selection data patterns |
| **wnc-tpyopt** | wnc-tpyopt-agent | wnc-steering-agent, wnc-acs-agent, wnc-iot-agent | TPYOPT agent designed exclusively for topology optimization data patterns |
| **wnc-iot** | wnc-iot-agent | wnc-steering-agent, wnc-acs-agent, wnc-tpyopt-agent | IoT agent designed exclusively for IoT device data patterns |

### Enforcement Mechanisms

**1. Agent Registry Validation**
- Agent registry validates application-agent compatibility before execution
- Rejects requests for incompatible application-agent combinations
- Returns clear error messages for invalid bindings

**2. Data Pattern Validation**
- Each agent validates incoming data against expected patterns
- Agents reject data that doesn't match their domain-specific patterns
- Prevents cross-domain data contamination

**3. API-Level Restrictions**
- API endpoints enforce application-agent binding rules
- Agent analysis endpoints validate application type before processing
- System prevents unauthorized agent invocations

### Example Scenarios

**✅ Valid Operations**:
- wnc-steer application → wnc-steering-agent analysis
- wnc-acs application → wnc-acs-agent analysis
- wnc-tpyopt application → wnc-tpyopt-agent analysis

**❌ Invalid Operations**:
- wnc-steer application → wnc-acs-agent analysis (REJECTED)
- wnc-acs application → wnc-steering-agent analysis (REJECTED)
- wnc-tpyopt application → wnc-acs-agent analysis (REJECTED)

### Benefits of Strict Binding

1. **Data Integrity**: Ensures agents only process compatible data
2. **Analysis Accuracy**: Prevents incorrect analysis due to incompatible data patterns
3. **System Reliability**: Reduces errors and unexpected behavior
4. **Maintainability**: Clear boundaries make system easier to maintain
5. **Performance**: Optimized processing for specific data types

## 🔄 Analysis Architecture

### Two-Tier Analysis System

#### Application Analysis (Foundation Layer)

**Purpose**: Provides foundational data processing for all applications

**Process**:
1. **Log Parsing**: Extract structured data from raw log files
2. **Data Cleaning**: Standardize timestamps, formats, and structures
3. **Message Classification**: Add `message_type` field to categorize entries
4. **Application Detection**: Identify specific PrplVAS LCM applications
5. **Basic Analytics**: Perform statistical analysis and anomaly detection

**Output**: Standardized, classified log data ready for advanced analysis

#### Agent Analysis (Advanced Layer)

**Purpose**: Provides specialized, domain-specific analysis

**Process**:
1. **Domain Expertise**: Apply specialized knowledge for specific application types
2. **Pattern Recognition**: Use advanced pattern matching for insights
3. **Business Logic**: Apply application-specific rules and algorithms
4. **Insight Generation**: Create actionable recommendations
5. **Report Generation**: Generate specialized reports and visualizations

**Output**: Advanced analysis results, insights, and recommendations

### Analysis Flow Integration

```
Raw Logs → Application Analysis → Agent Analysis → Insights & Reports
    ↓              ↓                    ↓              ↓
  Clean        Add message_type    Domain-specific   Actionable
  Data         Classifications     Deep Analysis     Results
```

## 🎯 User Workflow

### Complete User Journey

1. **Project Creation**
   - User uploads log package (.tar, .tar.gz, .tgz)
   - System creates project with unique ID
   - Package is extracted and applications are discovered
   - User can view discovered applications

2. **Application Selection**
   - User selects specific application to work with
   - System loads application-specific data
   - User can view application metadata and log structure

3. **Analysis Execution**
   - User initiates Application Analysis (automatic)
   - User can optionally invoke Agent Analysis
   - System processes data through both analysis layers
   - Results are stored and made available for visualization

4. **Results Review**
   - User can view analysis results and insights
   - Interactive visualizations and reports are available
   - User can export results in various formats

## 🔧 Configuration and Deployment

### Environment Configuration

**Project Settings**:
- `DATA_DIR`: Root directory for project data storage
- `UPLOAD_DIR`: Directory for uploaded log packages
- `MAX_FILE_SIZE`: Maximum allowed package size
- `SUPPORTED_FORMATS`: Supported log package formats

**Application Settings**:
- `APPLICATION_DISCOVERY_METHODS`: Methods for identifying applications
- `MESSAGE_TYPE_PATTERNS`: Patterns for message classification
- `DATA_CLEANING_RULES`: Rules for data standardization

**Agent Settings**:
- `INTEGRATED_AGENTS_ENABLED`: Enable integrated agent execution
- `AGENT_TIMEOUT`: Timeout for agent execution
- `PATTERN_RECOGNITION_CONFIG`: Configuration for pattern matching

### Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   Project        │             │
         │              │   Management    │             │
         │              └─────────────────┘             │
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   Application   │             │
         │              │   Analysis      │             │
         │              └─────────────────┘             │
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   Agent         │             │
         │              │   Analysis      │             │
         │              └─────────────────┘             │
         │                       │                       │
         │              ┌─────────────────┐             │
         └──────────────►│   WebSocket    │◄────────────┘
                        │   Monitor       │
                        └─────────────────┘
```

## 📊 Data Models

### Project Model
```python
@dataclass
class Project:
    id: UUID
    name: str
    description: Optional[str]
    original_filename: str
    file_size_bytes: int
    upload_timestamp: datetime
    extraction_path: str
    status: str
    project_root_path: str
    package_structure_metadata: Optional[PackageStructureMetadata]
    application_discovery_metadata: Optional[ApplicationDiscoveryMetadata]
```

### Application Discovery Model
```python
@dataclass
class ApplicationDiscoveryResult:
    container_id: str
    application_name: str
    functional_domain: str
    relative_path: str
    log_file_count: int
    total_log_size_bytes: int
    time_range: Optional[Dict[str, datetime]]
    confidence_score: float
    discovery_method: str
```

### Analysis Model
```python
@dataclass
class Analysis:
    project_id: UUID
    id: UUID
    configuration: Dict[str, Any]
    status: str
    created_timestamp: datetime
    application_focus: Optional[str]
    result_path: Optional[str]
    result: Optional[Any]
```

### Application Model
```python
@dataclass
class Application:
    project_id: UUID
    container_id: str
    application_name: str
    id: UUID
    functional_domain: Optional[str]
    relative_path: str
    log_file_count: int
    total_log_size_bytes: int
    time_range_start: Optional[datetime]
    time_range_end: Optional[datetime]
    confidence_score: float
```

**Usage Examples**:
```python
# Create application instance
app = Application(
    project_id=project.id,
    container_id="container_001",
    application_name="wnc-steer",
    functional_domain="WiFi Steering",
    relative_path="extracted/container_001/wnc-steer",
    log_file_count=15,
    total_log_size_bytes=2048576,
    confidence_score=0.95
)

# Convert to dictionary for API responses
app_dict = app.to_dict()
```

**Relationships**:
- **Project**: Each application belongs to one project (`project_id`)
- **Container**: Each application is associated with one container (`container_id`)
- **Agent**: Each application can invoke its corresponding agent (e.g., `wnc-steer` → `WNCSteeringAgent`)

## 🔌 API Endpoints

### **Project Management Endpoints**

#### **Core Project Operations**
```http
GET    /api/v1/projects/                    # List all projects
POST   /api/v1/projects/                    # Create new project
GET    /api/v1/projects/{project_id}        # Get project details
DELETE /api/v1/projects/{project_id}        # Delete project
```

#### **Project Import/Export**
```http
GET    /api/v1/projects/restore/available   # List available packages for restore
POST   /api/v1/projects/restore             # Restore project from package
GET    /api/v1/projects/{project_id}/export # Export project data
POST   /api/v1/projects/import              # Import project data
```

#### **Project Applications**
```http
GET    /api/v1/projects/{project_id}/applications                    # List applications in project
GET    /api/v1/projects/{project_id}/applications/{app_name}         # Get application details
```

### **Application Data Endpoints**

#### **Log Data Operations**
```http
GET    /api/v1/projects/{project_id}/applications/{app_name}/data/logs           # Search and filter logs
GET    /api/v1/projects/{project_id}/applications/{app_name}/data/statistics     # Get log statistics
GET    /api/v1/projects/{project_id}/applications/{app_name}/data/summary        # Get data summary
GET    /api/v1/projects/{project_id}/applications/{app_name}/data/export/csv     # Export data as CSV
POST   /api/v1/projects/{project_id}/applications/{app_name}/data/cleanup        # Clean up data
GET    /api/v1/projects/{project_id}/applications/{app_name}/data/database/info  # Get database info
```

### **Agent Analysis Endpoints**

#### **Agent Management**
```http
GET    /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/agents                    # List available agents
GET    /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/agents/{agent_type}/metadata # Get agent metadata
GET    /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/available-applications     # List available applications
```

#### **Analysis Operations**
```http
POST   /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/start     # Start agent analysis
GET    /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/status/{analysis_id} # Get analysis status
GET    /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/results   # Get analysis results
POST   /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/direct    # Direct analysis execution
```

#### **Health and Monitoring**
```http
GET    /api/v1/projects/{project_id}/applications/{app_name}/agent-analysis/health    # Agent analysis health check
```

### **Analysis Endpoints**

#### **Analysis Operations**
```http
POST   /api/v1/analysis/run/{project_id}                    # Run analysis on project
GET    /api/v1/analysis/results/{project_id}                # Get analysis results
GET    /api/v1/analysis/logs/{project_id}                   # Get analysis logs
GET    /api/v1/analysis/log-content/{project_id}            # Get log content
GET    /api/v1/analysis/aggregated/{project_id}             # Get aggregated analysis data
GET    /api/v1/analysis/advanced/{project_id}               # Get advanced analysis data
GET    /api/v1/analysis/anomalies/{project_id}              # Get anomaly detection results
GET    /api/v1/analysis/statistics/{project_id}             # Get analysis statistics
```

#### **Project-Specific Analysis**
```http
POST   /api/v1/projects/{project_id}/analyze                # Analyze entire project
POST   /api/v1/projects/{project_id}/analyze/{app_name}     # Analyze specific application
GET    /api/v1/projects/{project_id}/analyses               # List project analyses
GET    /api/v1/analyses/{analysis_id}/result                # Get specific analysis result
```

### **Reports Endpoints**

#### **Report Generation**
```http
GET    /api/v1/reports/{project_id}                         # Generate project report
GET    /api/v1/reports/{project_id}/summary                 # Get project summary
GET    /api/v1/reports/{project_id}/performance             # Get performance report
GET    /api/v1/reports/{project_id}/errors                  # Get error report
GET    /api/v1/reports/{project_id}/trends                  # Get trends report
GET    /api/v1/reports/{project_id}/export                  # Export report
GET    /api/v1/reports/comparison                           # Compare reports
```

### **Visualization Endpoints**

#### **Charts and Dashboards**
```http
GET    /api/v1/charts/{project_id}                          # Get project charts
GET    /api/v1/summary/{project_id}                         # Get project summary
POST   /api/v1/charts/generate                              # Generate custom charts
POST   /api/v1/dashboard/generate                           # Generate dashboard
```

#### **Monitoring and Alerts**
```http
POST   /api/v1/monitoring/start                             # Start monitoring
POST   /api/v1/monitoring/stop                              # Stop monitoring
GET    /api/v1/monitoring/alerts                            # Get alerts
GET    /api/v1/monitoring/alerts/summary                    # Get alerts summary
POST   /api/v1/monitoring/alerts/{alert_id}/acknowledge     # Acknowledge alert
GET    /api/v1/health                                       # Health check
```

### **Steering Capabilities Endpoints**

#### **WiFi Steering Analysis**
```http
GET    /api/v1/capabilities/summary                         # Get capability summary
GET    /api/v1/capabilities/detailed                        # Get detailed capabilities
GET    /api/v1/strategy/{mac_address}                       # Get steering strategy
GET    /api/v1/analysis/capability-trends                   # Get capability trends
GET    /api/v1/patterns/802.11kv                            # Get 802.11kv patterns
POST   /api/v1/analysis/refresh                             # Refresh analysis
```

### **Administrative Endpoints**

#### **System Management**
```http
GET    /api/v1/health                                       # System health check
GET    /api/v1/                                            # Root endpoint
```

#### **Data Management**
```http
POST   /api/v1/admin/clear-all-data                         # Clear all data
POST   /api/v1/admin/recover-projects                       # Recover projects
GET    /api/v1/admin/system-info                            # Get system information
```

#### **Advanced Admin Operations**
```http
POST   /api/v1/admin/validate-data                          # Validate data consistency
POST   /api/v1/admin/cleanup                                # Cleanup projects
GET    /api/v1/admin/backup                                 # Create backup
POST   /api/v1/admin/restore                                # Restore from backup
GET    /api/v1/admin/disk-usage                             # Get disk usage
GET    /api/v1/admin/logs                                   # Get system logs
```

### **Request/Response Models**

#### **Project Creation Request**
```json
{
  "name": "string",
  "description": "string",
  "file": "multipart/form-data"
}
```

#### **Project Response**
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "status": "string",
  "created_at": "datetime",
  "file_size": "integer",
  "original_filename": "string"
}
```

#### **Analysis Request**
```json
{
  "configuration": {
    "analysis_type": "string",
    "parameters": {}
  }
}
```

#### **Analysis Response**
```json
{
  "analysis_id": "uuid",
  "status": "string",
  "progress": "float",
  "result_path": "string",
  "created_at": "datetime"
}
```

#### **Error Response**
```json
{
  "error": "string",
  "detail": "string",
  "status_code": "integer"
}
```

### **Authentication and Authorization**

#### **Current Implementation**
- **No authentication required** for development
- **CORS enabled** for local development
- **API key authentication** planned for production

#### **Future Security Enhancements**
- **JWT token authentication**
- **Role-based access control**
- **API rate limiting**
- **Request validation and sanitization**

### **API Versioning**

#### **Current Version**: v1
- **Base URL**: `/api/v1/`
- **Backward compatibility**: Maintained
- **Deprecation policy**: 6-month notice

#### **Versioning Strategy**
- **URL-based versioning**: `/api/v1/`, `/api/v2/`
- **Header-based versioning**: `Accept: application/vnd.meshlog.v1+json`
- **Query parameter versioning**: `?version=1`

## 🏗️ Service Layer Architecture

### **Service Layer Overview**

The service layer provides business logic abstraction between the API endpoints and the data layer. It encapsulates complex operations, data validation, and business rules while maintaining separation of concerns.

### **Core Service Classes**

#### **ProjectService**
**Purpose**: Project lifecycle management and operations

**Responsibilities**:
- **Project CRUD Operations**: Create, read, update, delete projects
- **File Management**: Handle package uploads and storage
- **Project Validation**: Validate project data and constraints
- **Background Processing**: Coordinate project processing tasks
- **Project Statistics**: Calculate and provide project metrics

**Key Methods**:
```python
async def list_projects() -> Dict[str, Any]
async def get_project(project_id: str) -> Dict[str, Any]
async def create_project(background_tasks, file, name, description, validation_service) -> Dict[str, Any]
async def delete_project(project_id: str) -> Dict[str, Any]
```

**Dependencies**:
- `DatabaseManager`: Database operations
- `ValidationService`: Input validation
- `BackgroundTasks`: Async task management

#### **AnalysisService**
**Purpose**: Analysis execution and result management

**Responsibilities**:
- **Analysis Orchestration**: Coordinate analysis execution
- **Result Management**: Store and retrieve analysis results
- **Progress Tracking**: Monitor analysis progress
- **Error Handling**: Manage analysis failures and recovery
- **Background Processing**: Execute analyses asynchronously

**Key Methods**:
```python
async def run_analysis(background_tasks, project_id, project_service) -> Dict[str, Any]
async def get_analysis_results(project_id: str, app_name: Optional[str] = None) -> Dict[str, Any]
async def _run_analysis_background(project_id: str) -> None
```

**Dependencies**:
- `DatabaseManager`: Analysis metadata storage
- `ProjectService`: Project data access
- `BackgroundTasks`: Async execution

#### **DataPreparationService**
**Purpose**: Data preprocessing and preparation for analysis

**Responsibilities**:
- **Data Cleaning**: Clean and standardize log data
- **Data Transformation**: Convert data formats for analysis
- **Data Validation**: Ensure data quality and integrity
- **Data Aggregation**: Combine and summarize data
- **Data Export**: Prepare data for external consumption

**Key Methods**:
```python
async def prepare_data(project_id: str, application_name: str) -> Dict[str, Any]
async def clean_log_data(log_data: List[Dict]) -> List[Dict]
async def validate_data_quality(data: Dict[str, Any]) -> bool
```

**Dependencies**:
- `ApplicationDataManager`: Data access
- `ValidationService`: Data validation

#### **AgentServiceClient**
**Purpose**: Communication with external agent services

**Responsibilities**:
- **Service Communication**: HTTP client for agent services
- **Request/Response Handling**: Manage agent service interactions
- **Error Handling**: Handle service failures and timeouts
- **Service Discovery**: Locate and connect to agent services
- **Load Balancing**: Distribute requests across service instances

**Key Methods**:
```python
async def send_analysis_request(agent_type: str, data: Dict[str, Any]) -> Dict[str, Any]
async def get_service_status(agent_type: str) -> Dict[str, Any]
async def discover_services() -> List[str]
```

**Dependencies**:
- `httpx`: HTTP client library
- `AgentRegistry`: Service configuration

### **Manager Classes**

#### **DatabaseManager**
**Purpose**: Database operations and data persistence

**Responsibilities**:
- **Database Connection Management**: Handle database connections
- **CRUD Operations**: Create, read, update, delete operations
- **Transaction Management**: Ensure data consistency
- **Query Optimization**: Optimize database queries
- **Data Migration**: Handle schema changes

**Key Methods**:
```python
async def get_all_projects() -> List[Dict[str, Any]]
async def get_project(project_id: str) -> Optional[Dict[str, Any]]
async def create_project(project_data: Dict[str, Any]) -> None
async def update_project_status(project_id: str, status: str) -> None
```

#### **ApplicationDataManager**
**Purpose**: Application-specific data management

**Responsibilities**:
- **Data Storage**: Store application-specific data
- **Data Retrieval**: Query and filter application data
- **Data Indexing**: Maintain data indexes for performance
- **Data Archiving**: Archive old data
- **Data Synchronization**: Sync data across systems

**Key Methods**:
```python
async def store_application_data(project_id: str, app_name: str, data: Dict[str, Any]) -> None
async def get_application_data(project_id: str, app_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]
async def update_application_metadata(project_id: str, app_name: str, metadata: Dict[str, Any]) -> None
```

#### **ProjectAnalysisManager**
**Purpose**: Project-scoped analysis management

**Responsibilities**:
- **Analysis Metadata**: Manage analysis metadata and results
- **Analysis Coordination**: Coordinate multiple analyses
- **Result Aggregation**: Combine analysis results
- **Analysis History**: Maintain analysis history
- **Analysis Scheduling**: Schedule and manage analysis tasks

**Key Methods**:
```python
async def create_analysis(project_id: str, config: Dict[str, Any]) -> str
async def get_analysis_results(project_id: str, analysis_id: str) -> Dict[str, Any]
async def update_analysis_status(analysis_id: str, status: str) -> None
```

#### **ApplicationAnalysisManager**
**Purpose**: Application-specific analysis management

**Responsibilities**:
- **Application Analysis**: Execute application-specific analyses
- **Analysis Configuration**: Manage analysis configurations
- **Result Processing**: Process and format analysis results
- **Analysis Validation**: Validate analysis inputs and outputs
- **Performance Monitoring**: Monitor analysis performance

**Key Methods**:
```python
async def run_application_analysis(project_id: str, app_name: str, config: Dict[str, Any]) -> Dict[str, Any]
async def get_application_analysis_results(project_id: str, app_name: str) -> Dict[str, Any]
async def validate_analysis_config(config: Dict[str, Any]) -> bool
```

#### **WorkspaceManager**
**Purpose**: Agent workspace and data integration

**Responsibilities**:
- **Workspace Creation**: Create and manage agent workspaces
- **Data Integration**: Integrate data for agent consumption
- **Workspace Cleanup**: Clean up agent workspaces
- **Resource Management**: Manage workspace resources
- **Security**: Ensure workspace security and isolation

**Key Methods**:
```python
async def create_workspace(project_id: str, app_name: str, agent_type: str) -> str
async def prepare_workspace_data(workspace_path: str, data: Dict[str, Any]) -> None
async def cleanup_workspace(workspace_path: str) -> None
```

#### **ConnectionManager**
**Purpose**: WebSocket connection management

**Responsibilities**:
- **Connection Management**: Manage WebSocket connections
- **Message Broadcasting**: Broadcast messages to connected clients
- **Connection Monitoring**: Monitor connection health
- **Message Queuing**: Queue messages for disconnected clients
- **Connection Cleanup**: Clean up disconnected clients

**Key Methods**:
```python
async def connect(websocket: WebSocket) -> None
async def disconnect(websocket: WebSocket) -> None
async def send_personal_message(message: str, websocket: WebSocket) -> None
async def broadcast(message: str) -> None
```

### **Service Layer Patterns**

#### **Dependency Injection**
Services use dependency injection for loose coupling and testability:

```python
class ProjectService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.data_dir = settings.DATA_DIR
```

#### **Async/Await Pattern**
All service methods are asynchronous for non-blocking operations:

```python
async def list_projects(self) -> Dict[str, Any]:
    try:
        projects = await self.db_manager.get_all_projects()
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### **Error Handling Pattern**
Consistent error handling across all services:

```python
try:
    # Service operation
    result = await self._perform_operation()
    return result
except HTTPException:
    raise
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

#### **Background Task Pattern**
Long-running operations use background tasks:

```python
async def create_project(self, background_tasks: BackgroundTasks, ...):
    # Immediate response
    background_tasks.add_task(self._process_package_background, ...)
    return {"status": "processing"}
```

### **Service Interactions**

#### **Service Dependencies**
```mermaid
graph TD
    A[API Endpoints] --> B[ProjectService]
    A --> C[AnalysisService]
    A --> D[DataPreparationService]
    
    B --> E[DatabaseManager]
    B --> F[ValidationService]
    
    C --> E
    C --> B
    
    D --> G[ApplicationDataManager]
    D --> F
    
    E --> H[SQLite Database]
    G --> H
    
    I[AgentServiceClient] --> J[External Agent Services]
    C --> I
```

#### **Data Flow**
1. **API Request** → **Service Layer** → **Data Layer** → **Database**
2. **Background Task** → **Service Layer** → **External Services**
3. **WebSocket** → **ConnectionManager** → **Client**

### **Service Configuration**

#### **Environment Configuration**
Services are configured through environment variables and settings:

```python
from app.core.config import settings

class ProjectService:
    def __init__(self, db_manager: DatabaseManager):
        self.data_dir = settings.DATA_DIR
        self.upload_dir = settings.UPLOAD_DIR
```

#### **Service Registration**
Services are registered and injected through FastAPI's dependency system:

```python
def get_project_service() -> ProjectService:
    return ProjectService(get_database_manager())

@router.get("/projects/")
async def list_projects(
    project_service: ProjectService = Depends(get_project_service)
):
    return await project_service.list_projects()
```

## 🏗️ Project Management System

### **Project Management Overview**

The project management system provides robust, reliable project lifecycle management with comprehensive error handling, data consistency validation, and recovery mechanisms to prevent the common issue of projects being created but not appearing in the project list.

### **Core Project Management Features**

#### **1. Transaction Management**
- **Atomic Operations**: Project creation is atomic - either fully succeeds or fully fails
- **Rollback Capabilities**: Automatic cleanup of partial data on failure
- **Resource Management**: Proper cleanup of uploaded files and temporary data

#### **2. Data Consistency Validation**
- **Dual Storage Validation**: Ensures consistency between in-memory database and JSON file
- **Cross-Reference Validation**: Validates projects exist in both storage systems
- **Automatic Recovery**: Recovers orphaned projects from file storage

#### **3. Error Handling and Recovery**
- **Comprehensive Error Handling**: Handles all failure scenarios gracefully
- **Background Processing Recovery**: Recovers from background processing failures
- **Data Integrity Protection**: Prevents data corruption and loss

### **Project Creation Flow**

#### **Step 1: File Upload and Validation**
```python
# Validate file and create project record
project = _create_project_record(name, description, filename, file_size, "processing")
```

#### **Step 2: Atomic Project Creation**
```python
def _save_and_process_project(project, package_path, background_tasks, description):
    project_id = str(project.id)
    
    try:
        # Step 1: Add to in-memory database
        projects_db[project_id] = project
        
        # Step 2: Persist to JSON file
        save_data()
        
        # Step 3: Verify project was saved
        if project_id not in projects_db:
            raise Exception(f"Project {project_id} not found after save")
        
        # Step 4: Schedule background processing
        background_tasks.add_task(process_package_background, package_path, project_id, description)
        
        return success_response
        
    except Exception as e:
        # Rollback: Remove from memory and cleanup files
        if project_id in projects_db:
            del projects_db[project_id]
        if os.path.exists(package_path):
            os.remove(package_path)
        raise e
```

#### **Step 3: Background Processing with Recovery**
```python
async def process_package_background(package_path, project_id, description):
    try:
        # Check if project exists in memory
        if project_id not in projects_db:
            # Attempt recovery from JSON file
            project = recover_project_from_file(project_id)
            if not project:
                logger.error(f"Project {project_id} not found and cannot be recovered")
                return
        
        # Process package and update status
        project.status = "processing"
        save_data()
        
        # ... processing logic ...
        
        project.status = "completed"
        save_data()
        
    except Exception as e:
        # Handle failures gracefully
        if project_id in projects_db:
            project = projects_db[project_id]
            project.status = "failed"
            save_data()
        else:
            # Create minimal project record for failed projects
            create_failed_project_record(project_id)
        
        # Clean up resources
        cleanup_uploaded_file(package_path)
```

### **Data Consistency Validation**

#### **Validation Process**
```python
def validate_data_consistency():
    """Validate consistency between projects_db and filesystem"""
    try:
        # Check if projects.json exists
        if not os.path.exists(PROJECTS_FILE):
            return False
        
        # Load projects from file
        with open(PROJECTS_FILE, 'r') as f:
            file_projects = json.load(f)
        
        # Compare counts
        memory_count = len(projects_db)
        file_count = len(file_projects)
        
        if memory_count != file_count:
            return False
        
        # Validate each project exists in both systems
        for project_id in projects_db:
            if project_id not in file_projects:
                return False
        
        for project_id in file_projects:
            if project_id not in projects_db:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Data consistency validation failed: {e}")
        return False
```

#### **Recovery Process**
```python
def recover_orphaned_projects():
    """Recover projects that exist in one storage system but not others"""
    try:
        # Load projects from file
        with open(PROJECTS_FILE, 'r') as f:
            file_projects = json.load(f)
        
        recovered_count = 0
        
        # Find projects in file but not in memory
        for project_id, project_dict in file_projects.items():
            if project_id not in projects_db:
                # Reconstruct project object
                project = Project(
                    id=UUID(project_id),
                    name=project_dict["name"],
                    # ... other fields ...
                )
                projects_db[project_id] = project
                recovered_count += 1
        
        return recovered_count
        
    except Exception as e:
        logger.error(f"Orphaned project recovery failed: {e}")
        return 0
```

### **API Endpoints for Project Management**

#### **Data Consistency Validation**
```http
POST /api/v1/admin/validate-data-consistency
```

**Response**:
```json
{
  "status": "consistent|inconsistent",
  "message": "Validation result message",
  "memory_projects": 5,
  "file_projects": 5,
  "recovered_count": 0,
  "recovery_successful": true
}
```

#### **Project Recovery**
```http
POST /api/v1/admin/recover-projects
```

**Response**:
```json
{
  "success": true,
  "recovered_count": 2,
  "message": "Recovered 2 projects"
}
```

### **Startup Validation and Recovery**

#### **Automatic Startup Recovery**
```python
# Load data on startup
load_data()

# Validate data consistency on startup
if not validate_data_consistency():
    logger.warning("Data consistency issues detected on startup - attempting recovery")
    recovered_count = recover_orphaned_projects()
    if recovered_count > 0:
        logger.info(f"Recovered {recovered_count} orphaned projects")
        # Re-validate after recovery
        if validate_data_consistency():
            logger.info("Data consistency restored after recovery")
        else:
            logger.error("Data consistency issues persist after recovery")
    else:
        logger.error("No projects could be recovered")
```

### **Error Handling Patterns**

#### **1. Project Creation Failures**
- **File Upload Failure**: Clean up uploaded file
- **Database Save Failure**: Remove from memory
- **Background Processing Failure**: Mark as failed, cleanup resources

#### **2. Background Processing Failures**
- **Project Not Found**: Attempt recovery from file
- **Processing Error**: Mark as failed, cleanup files
- **Resource Cleanup**: Remove uploaded files, temporary data

#### **3. Data Consistency Issues**
- **Memory-File Mismatch**: Attempt recovery
- **Corrupted Data**: Log error, attempt partial recovery
- **Missing Files**: Create minimal project records

### **Monitoring and Logging**

#### **Comprehensive Logging**
```python
logger.info(f"Added project {project_id} to in-memory database")
logger.info(f"Persisted project {project_id} to JSON file")
logger.info(f"Scheduled background processing for project {project_id}")
logger.error(f"Rolled back project {project_id} from memory due to error: {e}")
logger.info(f"Cleaned up uploaded file: {package_path}")
```

#### **Status Tracking**
- **Project Status**: `created`, `processing`, `completed`, `failed`
- **Processing Stages**: File upload, database save, background processing
- **Error Categories**: Validation errors, database errors, processing errors

### **Benefits of Enhanced Project Management**

#### **1. Reliability**
- **Zero Data Loss**: Projects are never lost due to system failures
- **Consistent State**: Data consistency maintained across all storage systems
- **Automatic Recovery**: System recovers from failures automatically

#### **2. User Experience**
- **Immediate Visibility**: Projects appear in list immediately after creation
- **Clear Status**: Users can see project status and progress
- **Error Transparency**: Clear error messages and recovery status

#### **3. System Stability**
- **Resource Management**: Proper cleanup of temporary files and data
- **Memory Management**: Efficient memory usage and cleanup
- **Error Isolation**: Failures don't affect other projects

## 🔄 Analysis Orchestration System

### **Analysis Orchestration Overview**

The analysis orchestration system coordinates the execution of complex analysis workflows, managing data flow between components, handling background processing, and ensuring reliable analysis execution across the two-tier architecture.

### **Core Orchestration Components**

#### **1. AgentOrchestrator**
**Purpose**: Hybrid orchestrator for agent-based analysis execution

**Responsibilities**:
- **Execution Mode Routing**: Routes analysis to integrated or service-based agents
- **Analysis Lifecycle Management**: Manages analysis initiation, execution, and completion
- **Result Aggregation**: Combines results from multiple analysis sources
- **Error Handling**: Manages analysis failures and recovery
- **Performance Monitoring**: Tracks analysis performance and resource usage

**Key Methods**:
```python
async def analyze_logs(project_id: str, application_name: str, agent_type: str, log_data: dict, analysis_config: dict = None) -> dict
async def _analyze_with_integrated_agent(project_id: str, application_name: str, agent_type: str, log_data: dict, analysis_config: dict) -> dict
async def _analyze_with_service(project_id: str, application_name: str, agent_type: str, log_data: dict, analysis_config: dict) -> dict
```

**Execution Modes**:
- **Integrated Mode**: Agents run as Python modules within the application
- **Service Mode**: Agents run as external HTTP services (legacy support)

#### **2. AnalysisOrchestrator**
**Purpose**: Application-specific analysis coordination

**Responsibilities**:
- **Application Grouping**: Groups containers by application type
- **Analysis Coordination**: Coordinates analysis across multiple applications
- **Cross-Application Correlation**: Identifies patterns across applications
- **System-Level Insights**: Generates system-wide analysis results
- **Result Management**: Manages analysis results and metadata

**Key Methods**:
```python
def analyze_project(project_name: str, package_structure: PackageStructure, log_entries: List[LogEntry]) -> AnalysisResult
def _group_containers_by_application(containers: List[ContainerInfo]) -> Dict[str, List[ContainerInfo]]
def _analyze_application(app_name: str, containers: List[ContainerInfo], log_entries: List[LogEntry]) -> ApplicationAnalysisResult
def _generate_cross_application_correlations(application_analyses: Dict[str, ApplicationAnalysisResult]) -> List[CorrelationResult]
```

#### **3. AnalysisEngine**
**Purpose**: Core analysis execution engine

**Responsibilities**:
- **Analysis Execution**: Executes analysis algorithms and patterns
- **Data Processing**: Processes log data for analysis
- **Pattern Recognition**: Identifies patterns and anomalies
- **Insight Generation**: Generates actionable insights
- **Result Formatting**: Formats analysis results for consumption

**Key Methods**:
```python
def run_analysis(project_id: str, config: Dict[str, Any]) -> AnalysisResult
def process_log_data(log_entries: List[LogEntry], config: Dict[str, Any]) -> ProcessedData
def identify_patterns(data: ProcessedData) -> List[Pattern]
def generate_insights(patterns: List[Pattern]) -> List[Insight]
```

#### **4. WorkspaceManager**
**Purpose**: Agent workspace and data integration management

**Responsibilities**:
- **Workspace Creation**: Creates isolated workspaces for agent execution
- **Data Integration**: Integrates data for agent consumption
- **Resource Management**: Manages workspace resources and cleanup
- **Security Isolation**: Ensures workspace security and isolation
- **Data Synchronization**: Synchronizes data between workspaces and main system

**Key Methods**:
```python
async def create_workspace(project_id: str, app_name: str, agent_type: str) -> str
async def prepare_workspace_data(workspace_path: str, data: Dict[str, Any]) -> None
async def cleanup_workspace(workspace_path: str) -> None
async def sync_workspace_data(workspace_path: str, main_system_path: str) -> None
```

### **Analysis Orchestration Flow**

#### **Phase 1: Analysis Initiation**
```mermaid
sequenceDiagram
    participant API as API Endpoint
    participant AO as AgentOrchestrator
    participant AR as AgentRegistry
    participant WM as WorkspaceManager
    
    API->>AO: analyze_logs(project_id, app_name, agent_type, log_data, config)
    AO->>AO: Generate analysis_id
    AO->>AO: Store analysis info in active_analyses
    AO->>AR: get_agent_execution_mode(agent_type)
    AR-->>AO: execution_mode (integrated/service)
    
    alt execution_mode == "integrated"
        AO->>WM: create_workspace(project_id, app_name, agent_type)
        WM-->>AO: workspace_path
        AO->>AO: _analyze_with_integrated_agent()
    else execution_mode == "service"
        AO->>AO: _analyze_with_service()
    end
```

#### **Phase 2: Data Processing and Analysis**
```mermaid
sequenceDiagram
    participant AO as AgentOrchestrator
    participant AE as AnalysisEngine
    participant AA as ApplicationAnalyzer
    participant Agent as Agent
    
    AO->>AE: run_analysis(project_id, config)
    AE->>AE: process_log_data(log_entries, config)
    AE->>AA: analyze_application(app_name, containers, log_entries)
    AA->>Agent: analyze(log_paths, output_path, analysis_config)
    Agent-->>AA: analysis_results
    AA-->>AE: application_analysis_result
    AE->>AE: identify_patterns(processed_data)
    AE->>AE: generate_insights(patterns)
    AE-->>AO: analysis_result
```

#### **Phase 3: Result Aggregation and Storage**
```mermaid
sequenceDiagram
    participant AO as AgentOrchestrator
    participant PAM as ProjectAnalysisManager
    participant DB as Database
    participant FS as FileSystem
    
    AO->>AO: Update analysis status to "completed"
    AO->>AO: Store result in active_analyses
    AO->>AO: Add to analysis_history
    AO->>PAM: save_analysis_result(analysis_id, result)
    PAM->>DB: Store analysis metadata
    PAM->>FS: Store analysis results
    PAM-->>AO: success_confirmation
    AO-->>API: analysis_response
```

### **Background Processing Architecture**

#### **Celery Task Management**
```python
@celery_app.task(bind=True, name="app.tasks.analysis_tasks.run_analysis_task")
def run_analysis_task(self, analysis_id: str, project_id: str):
    """Celery task for running project analysis"""
    try:
        # Update task status
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting analysis...'}
        )
        
        # Initialize components
        analysis_engine = AnalysisEngine()
        project_manager = ProjectAnalysisManager(settings.DATA_DIR, project_id)
        
        # Run analysis with progress updates
        result = analysis_engine.run_analysis(project_id=project_id, config=analysis.configuration)
        
        # Save results
        analysis.status = "completed"
        analysis.result = result
        project_manager.save_analysis(analysis)
        
        return {"status": "completed", "analysis_id": analysis_id}
        
    except Exception as e:
        # Handle errors and update status
        analysis.status = "failed"
        analysis.error_message = str(e)
        project_manager.save_analysis(analysis)
        raise e
```

#### **Hybrid Agent Analysis Task**
```python
@celery_app.task(bind=True, name="app.tasks.agent_tasks.hybrid_agent_analysis_task")
def hybrid_agent_analysis_task(self, project_id: str, application_name: str, agent_type: str, analysis_config: dict = None):
    """Hybrid agent analysis task supporting both integrated and service-based agents"""
    try:
        # Initialize orchestrator
        orchestrator = AgentOrchestrator()
        
        # Get log data
        log_data = get_application_log_data(project_id, application_name)
        
        # Run analysis
        result = await orchestrator.analyze_logs(
            project_id=project_id,
            application_name=application_name,
            agent_type=agent_type,
            log_data=log_data,
            analysis_config=analysis_config
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Agent analysis failed: {e}")
        raise e
```

### **Data Flow Architecture**

#### **Analysis Data Flow**
```mermaid
graph TD
    A[Log Package] --> B[Package Processor]
    B --> C[Application Discovery]
    C --> D[Application Data Manager]
    D --> E[Analysis Orchestrator]
    E --> F[Agent Orchestrator]
    F --> G[Agent Registry]
    G --> H[Integrated Agent]
    G --> I[Service Agent]
    H --> J[Analysis Engine]
    I --> J
    J --> K[Result Aggregation]
    K --> L[Project Analysis Manager]
    L --> M[Database Storage]
    L --> N[File System Storage]
```

#### **Component Interactions**
```mermaid
graph LR
    A[API Endpoint] --> B[Agent Orchestrator]
    B --> C[Agent Registry]
    B --> D[Workspace Manager]
    B --> E[Analysis Engine]
    E --> F[Application Analyzer]
    F --> G[Agent Interface]
    G --> H[Integrated Agent]
    G --> I[Service Client]
    I --> J[External Agent Service]
    H --> K[Result Processor]
    J --> K
    K --> L[Project Analysis Manager]
    L --> M[Database]
    L --> N[File System]
```

### **Performance Considerations**

#### **1. Parallel Processing**
- **Multi-Application Analysis**: Applications analyzed in parallel
- **Agent Execution**: Multiple agents can run concurrently
- **Background Tasks**: Analysis runs asynchronously

#### **2. Resource Management**
- **Memory Optimization**: Efficient data structures and cleanup
- **CPU Utilization**: Multi-threaded processing where appropriate
- **Storage Optimization**: Compressed storage and efficient indexing

#### **3. Scalability**
- **Horizontal Scaling**: Multiple analysis workers
- **Load Balancing**: Distributed analysis across workers
- **Caching**: Result caching for repeated analyses

### **Error Handling and Recovery**

#### **Analysis Failure Handling**
```python
try:
    # Analysis execution
    result = await orchestrator.analyze_logs(...)
    return result
except AnalysisTimeoutError as e:
    # Handle timeout
    logger.error(f"Analysis timeout: {e}")
    return {"status": "timeout", "error": str(e)}
except AnalysisError as e:
    # Handle analysis errors
    logger.error(f"Analysis error: {e}")
    return {"status": "failed", "error": str(e)}
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
    return {"status": "error", "error": str(e)}
```

#### **Recovery Mechanisms**
- **Retry Logic**: Automatic retry for transient failures
- **Fallback Strategies**: Fallback to alternative analysis methods
- **Partial Results**: Return partial results when possible
- **Error Reporting**: Comprehensive error reporting and logging

### **Monitoring and Observability**

#### **Analysis Metrics**
- **Execution Time**: Track analysis execution duration
- **Success Rate**: Monitor analysis success/failure rates
- **Resource Usage**: Monitor CPU, memory, and storage usage
- **Throughput**: Track analysis throughput and capacity

#### **Health Monitoring**
- **Component Health**: Monitor health of orchestration components
- **Agent Status**: Track agent availability and performance
- **System Load**: Monitor system load and capacity
- **Error Rates**: Track error rates and patterns

## ⚙️ Configuration System

### **Configuration Overview**

The MeshLog system uses a comprehensive configuration system based on Pydantic Settings, supporting environment variables, configuration files, and environment-specific settings for flexible deployment across different environments.

### **Configuration Architecture**

#### **1. Settings Class Structure**
```python
class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    APP_NAME: str = Field(default="prplOS LCM Log Analysis System", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from .env file
```

#### **2. Configuration Sources**
- **Environment Variables**: Primary configuration source
- **Configuration Files**: `.env` files for local development
- **Default Values**: Fallback values for all settings
- **Environment-Specific**: Different configs for dev/staging/production

### **Core Configuration Categories**

#### **1. Application Settings**
```python
# Application Identity
APP_NAME: str = "prplOS LCM Log Analysis System"
APP_VERSION: str = "1.0.0"
ENVIRONMENT: str = "development"  # development, staging, production
DEBUG: bool = False

# Development Features
AUTO_RELOAD: bool = False
HOT_RELOAD: bool = False
```

#### **2. Data Storage Configuration**
```python
# Primary Data Directory
DATA_DIR: str = "/data/WNC/LCM-Logs-Data"

# Subdirectories (relative to DATA_DIR)
UPLOAD_DIR: str = "uploads"
ANALYSIS_DIR: str = "analysis"
TEMP_DIR: str = "temp"
BACKUP_DIR: str = "backups"

# File Size Limits
MAX_FILE_SIZE: int = 1073741824  # 1GB
```

#### **3. Database Configuration**
```python
# SQLite (Default)
DATABASE_URL: str = "sqlite:////data/WNC/LCM-Logs-Data/prplos_analysis.db"
DATABASE_PATH: str = "/data/WNC/LCM-Logs-Data/meshlog.db"
DATA_FILE: str = "/data/WNC/LCM-Logs-Data/projects.json"

# PostgreSQL (Production)
POSTGRES_DB: str = "prplos_logs"
POSTGRES_USER: str = "prplos_user"
POSTGRES_PASSWORD: str = "prplos_password"
```

#### **4. Redis Configuration**
```python
# Redis Connection
REDIS_URL: str = "redis://localhost:6379/0"
REDIS_HOST: str = "localhost"
REDIS_PORT: int = 6379
REDIS_DB: int = 0
```

#### **5. Security Configuration**
```python
# Authentication
SECRET_KEY: str = "your-secret-key-change-in-production"
JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# CORS
CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000", "http://0.0.0.0:3000"]
```

#### **6. Logging Configuration**
```python
# Logging Settings
LOG_LEVEL: str = "INFO"
LOG_FILE: str = "./logs/app.log"
LOG_MAX_SIZE: int = 10485760  # 10MB
LOG_BACKUP_COUNT: int = 5
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

#### **7. Analysis Configuration**
```python
# Analysis Settings
ANALYSIS_TIMEOUT: int = 3600  # 1 hour
MAX_CONCURRENT_ANALYSES: int = 5
ANOMALY_DETECTION_ENABLED: bool = True
PREDICTIVE_ANALYTICS_ENABLED: bool = True

# Default Analysis Configuration
DEFAULT_ANALYSIS_CONFIG: Dict[str, Any] = {
    "include_raw_logs": False,
    "extract_structured_data": True,
    "perform_correlation": True,
    "detect_anomalies": True,
    "generate_summary": True,
    "create_visualizations": True,
    "embed_analysis": True
}
```

#### **8. Processing Configuration**
```python
# Worker Settings
MAX_WORKERS: int = 4
WORKER_PROCESSES: int = 4
WORKER_CONNECTIONS: int = 1000
MAX_REQUESTS: int = 1000
MAX_REQUESTS_JITTER: int = 50
CHUNK_SIZE: int = 8192
TIMEOUT_SECONDS: int = 300
```

#### **9. Agent System Configuration**
```python
# Agent Services Integration
WNC_LOG_AGENTS_ENABLED: bool = False
WNC_LOG_AGENTS_URL: str = "http://localhost:8001"
WNC_LOG_AGENTS_TIMEOUT: int = 300  # 5 minutes
SHARED_DATA_PATH: str = "/shared-data"
AGENT_ANALYSIS_ENABLED: bool = True
AGENT_RESULT_CACHE_TTL: int = 3600  # 1 hour

# Integrated Agent System
INTEGRATED_AGENTS_ENABLED: bool = True
INTEGRATED_AGENTS_PATH: str = "app.agents"
HYBRID_AGENT_MODE: bool = True  # Support both integrated and service agents
INTEGRATED_AGENT_TIMEOUT: int = 600  # 10 minutes
AGENT_EXECUTION_PRIORITY: str = "integrated"  # "integrated" or "service"
AGENT_DISCOVERY_AUTO_REFRESH: bool = True

# Agent-specific Settings
AGENT_DETECTION_CONFIDENCE_THRESHOLD: float = 0.7
AGENT_AUTO_TRIGGER: bool = True
AGENT_RESULT_FORMATS: list = ["html", "json"]
```

#### **10. Monitoring Configuration**
```python
# Metrics and Monitoring
ENABLE_METRICS: bool = True
METRICS_PORT: int = 9090
MONITORING_ENABLED: bool = True
ALERT_THRESHOLD_ERROR_RATE: float = 0.1
ALERT_THRESHOLD_RESPONSE_TIME: int = 1000
ALERT_THRESHOLD_MEMORY_USAGE: int = 80
```

#### **11. WebSocket Configuration**
```python
# WebSocket Settings
WEBSOCKET_ENABLED: bool = True
WEBSOCKET_PORT: int = 8000
WEBSOCKET_MAX_CONNECTIONS: int = 100
WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
WEBSOCKET_CONNECTION_TIMEOUT: int = 300
```

#### **12. Visualization Configuration**
```python
# Chart and Visualization Settings
CHART_THEME: str = "plotly"
DEFAULT_CHART_TYPE: str = "line"
CHART_COLORS: list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
CHART_ANIMATION_ENABLED: bool = True
CHART_RESPONSIVE: bool = True
```

### **Environment-Specific Configuration**

#### **Development Environment**
```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
AUTO_RELOAD=true
HOT_RELOAD=true
DATABASE_URL=sqlite:///./data/dev.db
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

#### **Staging Environment**
```bash
# .env.staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
AUTO_RELOAD=false
HOT_RELOAD=false
DATABASE_URL=postgresql://staging_user:staging_pass@staging-db:5432/staging_db
REDIS_URL=redis://staging-redis:6379/0
CORS_ORIGINS=["https://staging.meshlog.com"]
```

#### **Production Environment**
```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
AUTO_RELOAD=false
HOT_RELOAD=false
DATABASE_URL=postgresql://prod_user:prod_pass@prod-db:5432/prod_db
REDIS_URL=redis://prod-redis:6379/0
CORS_ORIGINS=["https://meshlog.com", "https://www.meshlog.com"]
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-secret-key
```

### **Configuration Management**

#### **1. Settings Instance**
```python
# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

#### **2. Environment Variable Override**
```python
# Environment variables take precedence over defaults
# Example: Setting DATA_DIR via environment variable
export DATA_DIR="/custom/data/path"
# This will override the default value in Settings
```

#### **3. Configuration Validation**
```python
# Pydantic automatically validates configuration values
# Invalid values will raise ValidationError
try:
    settings = Settings()
except ValidationError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise
```

### **Configuration Best Practices**

#### **1. Security**
- **Never commit secrets** to version control
- **Use environment variables** for sensitive data
- **Rotate secrets regularly** in production
- **Use different secrets** for each environment

#### **2. Environment Management**
- **Use separate configs** for each environment
- **Validate configuration** on startup
- **Document all settings** and their purposes
- **Use meaningful defaults** for development

#### **3. Performance**
- **Tune worker settings** based on hardware
- **Configure appropriate timeouts** for operations
- **Set reasonable limits** for file sizes and connections
- **Monitor resource usage** and adjust accordingly

#### **4. Monitoring**
- **Enable metrics collection** in production
- **Configure appropriate log levels** for each environment
- **Set up alerting thresholds** for critical metrics
- **Monitor configuration changes** and their impact

### **Configuration Examples**

#### **1. Docker Environment**
```yaml
# docker-compose.yml
version: '3.8'
services:
  meshlog:
    image: meshlog:latest
    environment:
      - DATA_DIR=/app/data
      - DATABASE_URL=postgresql://user:pass@db:5432/meshlog
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
      - DEBUG=false
    volumes:
      - ./data:/app/data
```

#### **2. Kubernetes ConfigMap**
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: meshlog-config
data:
  DATA_DIR: "/app/data"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  MAX_WORKERS: "8"
  ANALYSIS_TIMEOUT: "7200"
```

#### **3. Systemd Service**
```ini
# meshlog.service
[Unit]
Description=MeshLog Analysis System
After=network.target

[Service]
Type=exec
User=meshlog
Group=meshlog
WorkingDirectory=/opt/meshlog
ExecStart=/opt/meshlog/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Environment=DATA_DIR=/opt/meshlog/data
Environment=ENVIRONMENT=production
Environment=LOG_LEVEL=INFO
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **Configuration Troubleshooting**

#### **Common Issues**
1. **Missing Environment Variables**: Check that all required variables are set
2. **Invalid Configuration Values**: Validate configuration on startup
3. **Permission Issues**: Ensure proper file and directory permissions
4. **Network Connectivity**: Verify database and Redis connections

#### **Debugging Tools**
```python
# Print current configuration
def print_config():
    settings = get_settings()
    for field_name, field_value in settings.dict().items():
        print(f"{field_name}: {field_value}")

# Validate configuration
def validate_config():
    try:
        settings = Settings()
        print("Configuration is valid")
        return True
    except ValidationError as e:
        print(f"Configuration validation failed: {e}")
        return False
```

## 🚨 Error Handling System

### **Error Handling Overview**

The MeshLog system implements comprehensive error handling across all layers, providing robust error recovery, detailed logging, and user-friendly error messages. The system handles errors gracefully while maintaining data integrity and system stability.

### **Error Handling Architecture**

#### **1. Error Classification**
```python
# Error Categories
class ErrorCategory(Enum):
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND_ERROR = "not_found_error"
    CONFLICT_ERROR = "conflict_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    FILE_SYSTEM_ERROR = "file_system_error"
    ANALYSIS_ERROR = "analysis_error"
    AGENT_ERROR = "agent_error"
    SYSTEM_ERROR = "system_error"
```

#### **2. Error Response Format**
```python
# Standard Error Response
class ErrorResponse(BaseModel):
    error_code: str
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: Optional[str] = None
    suggestions: Optional[List[str]] = None
```

### **Error Handling Patterns**

#### **1. API Layer Error Handling**
```python
# FastAPI Exception Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": f"HTTP_{exc.status_code}",
            "error_type": "http_error",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "request_id": request.headers.get("X-Request-ID")
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "error_type": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.headers.get("X-Request-ID")
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "error_type": "system_error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat(),
            "request_id": request.headers.get("X-Request-ID")
        }
    )
```

#### **2. Service Layer Error Handling**
```python
# Service Layer Error Handling Pattern
class ProjectService:
    async def create_project(self, ...):
        try:
            # Service logic
            result = await self._perform_operation()
            return result
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise HTTPException(status_code=404, detail="Required file not found")
        except PermissionError as e:
            logger.error(f"Permission error: {e}")
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        except Exception as e:
            logger.error(f"Unexpected error in create_project: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
```

#### **3. Background Task Error Handling**
```python
# Background Task Error Handling
async def process_package_background(package_path: str, project_id: str, description: Optional[str]):
    try:
        # Background processing logic
        result = await process_package(package_path, project_id, description)
        return result
    except AnalysisTimeoutError as e:
        logger.error(f"Analysis timeout for project {project_id}: {e}")
        await mark_project_failed(project_id, "timeout", str(e))
        await cleanup_resources(project_id, package_path)
    except AnalysisError as e:
        logger.error(f"Analysis error for project {project_id}: {e}")
        await mark_project_failed(project_id, "analysis_error", str(e))
        await cleanup_resources(project_id, package_path)
    except Exception as e:
        logger.error(f"Unexpected error in background processing: {e}", exc_info=True)
        await mark_project_failed(project_id, "system_error", str(e))
        await cleanup_resources(project_id, package_path)
```

### **Error Recovery Mechanisms**

#### **1. Project Creation Recovery**
```python
def _save_and_process_project(project: Project, package_path: str, background_tasks: BackgroundTasks, description: Optional[str]) -> dict:
    project_id = str(project.id)
    
    try:
        # Step 1: Add project to in-memory database
        projects_db[project_id] = project
        logger.info(f"Added project {project_id} to in-memory database")
        
        # Step 2: Persist to JSON file
        save_data()
        logger.info(f"Persisted project {project_id} to JSON file")
        
        # Step 3: Schedule background processing
        background_tasks.add_task(process_package_background, package_path, project_id, description)
        
        return success_response
        
    except Exception as e:
        # Rollback: Remove project from memory if it was added
        if project_id in projects_db:
            del projects_db[project_id]
            logger.error(f"Rolled back project {project_id} from memory due to error: {e}")
        
        # Rollback: Remove uploaded file if it exists
        if os.path.exists(package_path):
            try:
                os.remove(package_path)
                logger.info(f"Cleaned up uploaded file: {package_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup uploaded file {package_path}: {cleanup_error}")
        
        # Re-raise the exception
        raise e
```

#### **2. Data Consistency Recovery**
```python
def recover_orphaned_projects():
    """Recover projects that exist in one storage system but not others"""
    try:
        logger.info("Starting orphaned project recovery...")
        
        # Load projects from file
        with open(PROJECTS_FILE, 'r') as f:
            file_projects = json.load(f)
        
        recovered_count = 0
        
        # Find projects in file but not in memory
        for project_id, project_dict in file_projects.items():
            if project_id not in projects_db:
                try:
                    # Reconstruct project object
                    project = Project(
                        id=UUID(project_id),
                        name=project_dict["name"],
                        # ... other fields ...
                    )
                    projects_db[project_id] = project
                    recovered_count += 1
                    logger.info(f"Recovered project {project_id} from file to memory")
                except Exception as e:
                    logger.error(f"Failed to recover project {project_id}: {e}")
        
        logger.info(f"Recovered {recovered_count} orphaned projects")
        return recovered_count
        
    except Exception as e:
        logger.error(f"Orphaned project recovery failed: {e}")
        return 0
```

#### **3. Agent Analysis Recovery**
```python
async def analyze_logs_with_recovery(project_id: str, application_name: str, agent_type: str, log_data: dict, analysis_config: dict = None) -> dict:
    try:
        # Attempt analysis
        result = await orchestrator.analyze_logs(project_id, application_name, agent_type, log_data, analysis_config)
        return result
    except AgentTimeoutError as e:
        logger.error(f"Agent timeout: {e}")
        # Retry with shorter timeout
        return await retry_analysis_with_timeout(project_id, application_name, agent_type, log_data, analysis_config, timeout=300)
    except AgentError as e:
        logger.error(f"Agent error: {e}")
        # Fallback to alternative agent
        return await fallback_analysis(project_id, application_name, log_data, analysis_config)
    except Exception as e:
        logger.error(f"Unexpected error in agent analysis: {e}")
        # Return partial results if available
        return await get_partial_results(project_id, application_name, agent_type)
```

### **Error Monitoring and Alerting**

#### **1. Error Metrics Collection**
```python
# Error Metrics
class ErrorMetrics:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.error_rates = defaultdict(float)
        self.last_error_times = {}
    
    def record_error(self, error_type: str, error_code: str):
        """Record error occurrence"""
        self.error_counts[error_type] += 1
        self.last_error_times[error_type] = datetime.now()
        
        # Check if error rate exceeds threshold
        if self.error_counts[error_type] > 10:  # Threshold
            self.send_alert(error_type, error_code)
    
    def send_alert(self, error_type: str, error_code: str):
        """Send alert for high error rate"""
        alert_message = f"High error rate detected: {error_type} ({error_code})"
        logger.warning(alert_message)
        # Send to monitoring system
```

#### **2. Error Alerting**
```python
# Error Alerting Configuration
ERROR_ALERT_THRESHOLDS = {
    "validation_error": 5,      # 5 errors per minute
    "authentication_error": 3,  # 3 errors per minute
    "database_error": 2,        # 2 errors per minute
    "system_error": 1,          # 1 error per minute
}

async def check_error_thresholds():
    """Check if error rates exceed thresholds"""
    for error_type, threshold in ERROR_ALERT_THRESHOLDS.items():
        error_count = get_error_count_last_minute(error_type)
        if error_count > threshold:
            await send_error_alert(error_type, error_count, threshold)
```

### **Error Logging and Diagnostics**

#### **1. Structured Error Logging**
```python
# Structured Error Logging
def log_error(error_type: str, error_code: str, message: str, details: Dict[str, Any] = None, exc_info: bool = False):
    """Log error with structured format"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "error_type": error_type,
        "error_code": error_code,
        "message": message,
        "details": details or {},
        "level": "ERROR"
    }
    
    if exc_info:
        logger.error(log_data, exc_info=True)
    else:
        logger.error(log_data)
```

#### **2. Error Context Collection**
```python
# Error Context Collection
class ErrorContext:
    def __init__(self, request: Request = None):
        self.request_id = request.headers.get("X-Request-ID") if request else None
        self.user_id = getattr(request.state, "user_id", None) if request else None
        self.endpoint = request.url.path if request else None
        self.method = request.method if request else None
        self.timestamp = datetime.now()
        self.system_info = get_system_info()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "endpoint": self.endpoint,
            "method": self.method,
            "timestamp": self.timestamp.isoformat(),
            "system_info": self.system_info
        }
```

### **Error Handling Best Practices**

#### **1. Error Prevention**
- **Input Validation**: Validate all inputs at API boundaries
- **Resource Limits**: Set appropriate limits for file sizes, timeouts, etc.
- **Graceful Degradation**: Provide fallback mechanisms for non-critical features
- **Circuit Breakers**: Implement circuit breakers for external service calls

#### **2. Error Recovery**
- **Retry Logic**: Implement exponential backoff for transient failures
- **Fallback Strategies**: Provide alternative paths when primary operations fail
- **Resource Cleanup**: Always clean up resources in error scenarios
- **State Recovery**: Maintain system state consistency during errors

#### **3. Error Communication**
- **User-Friendly Messages**: Provide clear, actionable error messages
- **Error Codes**: Use consistent error codes for programmatic handling
- **Error Details**: Include sufficient detail for debugging without exposing sensitive information
- **Error Suggestions**: Provide suggestions for resolving errors

#### **4. Error Monitoring**
- **Error Tracking**: Track error rates and patterns
- **Performance Impact**: Monitor impact of errors on system performance
- **Alerting**: Set up appropriate alerts for critical errors
- **Trend Analysis**: Analyze error trends to identify systemic issues

### **Error Handling Examples**

#### **1. File Upload Error Handling**
```python
@app.post("/api/v1/projects")
async def create_project(file: UploadFile = File(...), name: str = Form(...)):
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File size ({file.size} bytes) exceeds maximum limit ({MAX_FILE_SIZE} bytes)"
            )
        
        # Process file
        result = await process_uploaded_file(file, name)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="File upload failed")
```

#### **2. Database Error Handling**
```python
async def save_project_to_database(project: Project):
    try:
        # Save to database
        await db_manager.create_project(project.to_dict())
        logger.info(f"Project {project.id} saved to database")
    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(status_code=409, detail="Project already exists")
    except sqlite3.OperationalError as e:
        logger.error(f"Database operational error: {e}")
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")
    except Exception as e:
        logger.error(f"Database error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database operation failed")
```

#### **3. Agent Analysis Error Handling**
```python
async def run_agent_analysis(project_id: str, application_name: str, agent_type: str):
    try:
        # Get agent
        agent = agent_registry.get_agent(agent_type)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_type} not found")
        
        # Run analysis
        result = await agent.analyze(project_id, application_name)
        return result
        
    except AgentTimeoutError as e:
        logger.error(f"Agent timeout: {e}")
        raise HTTPException(status_code=408, detail="Analysis timeout - please try again")
    except AgentError as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=422, detail=f"Analysis failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected agent error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis system error")
```

### **Error Handling Testing**

#### **1. Error Scenario Testing**
```python
# Test error handling scenarios
def test_error_handling():
    # Test validation errors
    response = client.post("/api/v1/projects", json={"invalid": "data"})
    assert response.status_code == 422
    assert "validation_error" in response.json()["error_type"]
    
    # Test file size errors
    large_file = create_large_file(MAX_FILE_SIZE + 1)
    response = client.post("/api/v1/projects", files={"file": large_file})
    assert response.status_code == 413
    assert "file_size" in response.json()["message"]
    
    # Test database errors
    with patch("app.database.database.DatabaseManager.create_project", side_effect=sqlite3.OperationalError):
        response = client.post("/api/v1/projects", files={"file": valid_file})
        assert response.status_code == 503
```

## 🚀 Deployment Architecture

### **Deployment Overview**

The MeshLog system supports multiple deployment strategies, from simple Docker Compose setups to enterprise-grade Kubernetes clusters. The deployment architecture is designed for scalability, reliability, and maintainability across different environments.

### **Deployment Strategies**

#### **1. Development Deployment**
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend:
    build: .
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - DATABASE_URL=sqlite:///./data/dev.db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
      - ./data:/app/data
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./ui
    environment:
      - NODE_ENV=development
    volumes:
      - ./ui:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    command: npm run dev

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

#### **2. Staging Deployment**
```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  backend:
    environment:
      - ENVIRONMENT=staging
      - DEBUG=false
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://staging_user:staging_pass@postgres:5432/staging_db
      - REDIS_URL=redis://redis:6379/0
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=staging_db
      - POSTGRES_USER=staging_user
      - POSTGRES_PASSWORD=staging_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
    restart: unless-stopped

  redis:
    command: redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
    restart: unless-stopped
```

#### **3. Production Deployment**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=WARNING
      - DATABASE_URL=postgresql://prod_user:prod_pass@postgres:5432/prod_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    environment:
      - NODE_ENV=production
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=prod_db
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD=prod_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  celery_worker:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://prod_user:prod_pass@postgres:5432/prod_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  celery_beat:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://prod_user:prod_pass@postgres:5432/prod_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
        reservations:
          memory: 128M
          cpus: '0.1'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### **Kubernetes Deployment**

#### **1. Namespace and ConfigMap**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: meshlog
  labels:
    name: meshlog
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: meshlog-config
  namespace: meshlog
data:
  DATA_DIR: "/app/data"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  MAX_WORKERS: "8"
  ANALYSIS_TIMEOUT: "7200"
  REDIS_URL: "redis://redis-service:6379/0"
  DATABASE_URL: "postgresql://meshlog_user:meshlog_pass@postgres-service:5432/meshlog_db"
```

#### **2. Secrets**
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: meshlog-secrets
  namespace: meshlog
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret-key>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret-key>
  POSTGRES_PASSWORD: <base64-encoded-postgres-password>
```

#### **3. Backend Deployment**
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: meshlog-backend
  namespace: meshlog
  labels:
    app: meshlog-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: meshlog-backend
  template:
    metadata:
      labels:
        app: meshlog-backend
    spec:
      containers:
      - name: backend
        image: meshlog/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: meshlog-config
              key: ENVIRONMENT
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: meshlog-secrets
              key: SECRET_KEY
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: meshlog-config
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: meshlog-config
              key: REDIS_URL
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: meshlog-data-pvc
      - name: logs-volume
        persistentVolumeClaim:
          claimName: meshlog-logs-pvc
```

#### **4. Frontend Deployment**
```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: meshlog-frontend
  namespace: meshlog
  labels:
    app: meshlog-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: meshlog-frontend
  template:
    metadata:
      labels:
        app: meshlog-frontend
    spec:
      containers:
      - name: frontend
        image: meshlog/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### **5. Services**
```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: meshlog-backend-service
  namespace: meshlog
spec:
  selector:
    app: meshlog-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: meshlog-frontend-service
  namespace: meshlog
spec:
  selector:
    app: meshlog-frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: meshlog
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: meshlog
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

#### **6. Ingress**
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: meshlog-ingress
  namespace: meshlog
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - meshlog.example.com
    secretName: meshlog-tls
  rules:
  - host: meshlog.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: meshlog-frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: meshlog-backend-service
            port:
              number: 8000
```

### **Container Specifications**

#### **1. Backend Container**
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 meshlog && chown -R meshlog:meshlog /app
USER meshlog

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **2. Frontend Container**
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### **Service Dependencies**

#### **1. Database Services**
```yaml
# PostgreSQL Configuration
postgres:
  image: postgres:15-alpine
  environment:
    - POSTGRES_DB=meshlog_db
    - POSTGRES_USER=meshlog_user
    - POSTGRES_PASSWORD=meshlog_password
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./init.sql:/docker-entrypoint-initdb.d/init.sql
  ports:
    - "5432:5432"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U meshlog_user -d meshlog_db"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### **2. Cache Services**
```yaml
# Redis Configuration
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### **Network Configuration**

#### **1. Docker Network**
```yaml
# Network Configuration
networks:
  meshlog-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### **2. Service Communication**
```yaml
# Service Communication
services:
  backend:
    networks:
      - meshlog-network
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://meshlog_user:meshlog_password@postgres:5432/meshlog_db
      - REDIS_URL=redis://redis:6379/0
```

### **Monitoring and Logging**

#### **1. Monitoring Stack**
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

volumes:
  prometheus_data:
  grafana_data:
```

#### **2. Logging Configuration**
```yaml
# Logging Configuration
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service,environment"
```

### **Security Configuration**

#### **1. Security Headers**
```yaml
# Security Headers
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - CHOWN
  - SETGID
  - SETUID
```

#### **2. Resource Limits**
```yaml
# Resource Limits
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'
```

### **Deployment Commands**

#### **1. Development Deployment**
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### **2. Production Deployment**
```bash
# Deploy production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale celery_worker=5

# Check service status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

#### **3. Kubernetes Deployment**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n meshlog
kubectl get services -n meshlog
kubectl get ingress -n meshlog

# View logs
kubectl logs -f deployment/meshlog-backend -n meshlog
kubectl logs -f deployment/meshlog-frontend -n meshlog

# Scale deployments
kubectl scale deployment meshlog-backend --replicas=5 -n meshlog
kubectl scale deployment meshlog-frontend --replicas=3 -n meshlog
```

### **Health Checks and Monitoring**

#### **1. Health Check Endpoints**
```python
# Health Check Implementation
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": get_settings().APP_VERSION,
        "environment": get_settings().ENVIRONMENT,
        "checks": {
            "database": await check_database_health(),
            "redis": await check_redis_health(),
            "disk_space": check_disk_space(),
            "memory": check_memory_usage()
        }
    }
    
    # Determine overall health
    all_healthy = all(check["status"] == "healthy" for check in health_status["checks"].values())
    health_status["status"] = "healthy" if all_healthy else "unhealthy"
    
    status_code = 200 if all_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)
```

#### **2. Monitoring Metrics**
```python
# Metrics Collection
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
ANALYSIS_QUEUE_SIZE = Gauge('analysis_queue_size', 'Number of analyses in queue')

# Middleware for metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response
```

## 📊 Performance Metrics and Optimization

### **Performance Metrics Overview**

The MeshLog system implements comprehensive performance monitoring and optimization strategies to ensure optimal system performance across all components. Performance metrics are collected, analyzed, and used to drive optimization decisions.

### **Performance Metrics Categories**

#### **1. System Performance Metrics**
```python
# System Performance Metrics
class SystemMetrics:
    def __init__(self):
        self.cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('system_memory_usage_bytes', 'Memory usage in bytes')
        self.disk_usage = Gauge('system_disk_usage_bytes', 'Disk usage in bytes')
        self.network_io = Gauge('system_network_io_bytes', 'Network I/O in bytes')
        self.load_average = Gauge('system_load_average', 'System load average')
    
    def collect_metrics(self):
        """Collect system performance metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.used)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.disk_usage.set(disk.used)
        
        # Network I/O
        network = psutil.net_io_counters()
        self.network_io.set(network.bytes_sent + network.bytes_recv)
        
        # Load average
        load_avg = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
        self.load_average.set(load_avg)
```

#### **2. Application Performance Metrics**
```python
# Application Performance Metrics
class ApplicationMetrics:
    def __init__(self):
        self.request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
        self.request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
        self.response_size = Histogram('http_response_size_bytes', 'HTTP response size in bytes', ['endpoint'])
        self.active_connections = Gauge('active_connections', 'Number of active connections')
        self.connection_pool_size = Gauge('connection_pool_size', 'Database connection pool size')
        self.connection_pool_usage = Gauge('connection_pool_usage', 'Database connection pool usage')
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float, response_size: int):
        """Record HTTP request metrics"""
        self.request_count.labels(method=method, endpoint=endpoint, status=status_code).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        self.response_size.labels(endpoint=endpoint).observe(response_size)
```

#### **3. Database Performance Metrics**
```python
# Database Performance Metrics
class DatabaseMetrics:
    def __init__(self):
        self.query_count = Counter('database_queries_total', 'Total database queries', ['operation', 'table'])
        self.query_duration = Histogram('database_query_duration_seconds', 'Database query duration', ['operation', 'table'])
        self.connection_count = Gauge('database_connections', 'Number of database connections')
        self.transaction_count = Counter('database_transactions_total', 'Total database transactions', ['status'])
        self.lock_wait_time = Histogram('database_lock_wait_seconds', 'Database lock wait time')
        self.cache_hit_ratio = Gauge('database_cache_hit_ratio', 'Database cache hit ratio')
    
    def record_query(self, operation: str, table: str, duration: float):
        """Record database query metrics"""
        self.query_count.labels(operation=operation, table=table).inc()
        self.query_duration.labels(operation=operation, table=table).observe(duration)
```

#### **4. Analysis Performance Metrics**
```python
# Analysis Performance Metrics
class AnalysisMetrics:
    def __init__(self):
        self.analysis_count = Counter('analyses_total', 'Total analyses performed', ['type', 'status'])
        self.analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration', ['type'])
        self.analysis_queue_size = Gauge('analysis_queue_size', 'Number of analyses in queue')
        self.analysis_throughput = Gauge('analysis_throughput_per_second', 'Analysis throughput per second')
        self.agent_execution_time = Histogram('agent_execution_seconds', 'Agent execution time', ['agent_type'])
        self.data_processing_time = Histogram('data_processing_seconds', 'Data processing time', ['operation'])
    
    def record_analysis(self, analysis_type: str, status: str, duration: float):
        """Record analysis metrics"""
        self.analysis_count.labels(type=analysis_type, status=status).inc()
        self.analysis_duration.labels(type=analysis_type).observe(duration)
```

#### **5. Agent Performance Metrics**
```python
# Agent Performance Metrics
class AgentMetrics:
    def __init__(self):
        self.agent_invocations = Counter('agent_invocations_total', 'Total agent invocations', ['agent_type', 'status'])
        self.agent_duration = Histogram('agent_duration_seconds', 'Agent execution duration', ['agent_type'])
        self.agent_memory_usage = Gauge('agent_memory_usage_bytes', 'Agent memory usage', ['agent_type'])
        self.agent_cpu_usage = Gauge('agent_cpu_usage_percent', 'Agent CPU usage', ['agent_type'])
        self.agent_queue_size = Gauge('agent_queue_size', 'Agent queue size', ['agent_type'])
        self.agent_success_rate = Gauge('agent_success_rate', 'Agent success rate', ['agent_type'])
    
    def record_agent_execution(self, agent_type: str, status: str, duration: float, memory_usage: int, cpu_usage: float):
        """Record agent execution metrics"""
        self.agent_invocations.labels(agent_type=agent_type, status=status).inc()
        self.agent_duration.labels(agent_type=agent_type).observe(duration)
        self.agent_memory_usage.labels(agent_type=agent_type).set(memory_usage)
        self.agent_cpu_usage.labels(agent_type=agent_type).set(cpu_usage)
```

### **Performance Monitoring Implementation**

#### **1. Metrics Collection Middleware**
```python
# Performance Monitoring Middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Middleware to collect performance metrics"""
    start_time = time.time()
    
    # Record request start
    metrics.record_request_start(request.method, request.url.path)
    
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record request metrics
        metrics.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
            response_size=len(response.body) if hasattr(response, 'body') else 0
        )
        
        return response
        
    except Exception as e:
        # Record error metrics
        duration = time.time() - start_time
        metrics.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=500,
            duration=duration,
            response_size=0
        )
        raise e
```

#### **2. Database Performance Monitoring**
```python
# Database Performance Monitoring
class DatabasePerformanceMonitor:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.metrics = DatabaseMetrics()
    
    async def execute_query(self, query: str, params: tuple = None):
        """Execute query with performance monitoring"""
        start_time = time.time()
        
        try:
            result = await self.db_manager.execute_query(query, params)
            
            # Record successful query
            duration = time.time() - start_time
            operation = self._extract_operation(query)
            table = self._extract_table(query)
            
            self.metrics.record_query(operation, table, duration)
            
            return result
            
        except Exception as e:
            # Record failed query
            duration = time.time() - start_time
            self.metrics.record_query("error", "unknown", duration)
            raise e
    
    def _extract_operation(self, query: str) -> str:
        """Extract operation type from query"""
        query_upper = query.upper().strip()
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def _extract_table(self, query: str) -> str:
        """Extract table name from query"""
        # Simple table extraction - in production, use proper SQL parsing
        words = query.upper().split()
        for i, word in enumerate(words):
            if word in ['FROM', 'INTO', 'UPDATE', 'DELETE'] and i + 1 < len(words):
                return words[i + 1].strip('`"[]')
        return 'unknown'
```

#### **3. Analysis Performance Monitoring**
```python
# Analysis Performance Monitoring
class AnalysisPerformanceMonitor:
    def __init__(self):
        self.metrics = AnalysisMetrics()
    
    async def monitor_analysis(self, analysis_type: str, analysis_func, *args, **kwargs):
        """Monitor analysis execution with performance metrics"""
        start_time = time.time()
        
        try:
            # Update queue size
            self.metrics.analysis_queue_size.inc()
            
            # Execute analysis
            result = await analysis_func(*args, **kwargs)
            
            # Record successful analysis
            duration = time.time() - start_time
            self.metrics.record_analysis(analysis_type, 'success', duration)
            
            return result
            
        except Exception as e:
            # Record failed analysis
            duration = time.time() - start_time
            self.metrics.record_analysis(analysis_type, 'failed', duration)
            raise e
            
        finally:
            # Update queue size
            self.metrics.analysis_queue_size.dec()
```

### **Performance Optimization Strategies**

#### **1. Caching Strategy**
```python
# Performance-Optimized Caching
class PerformanceCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
    
    async def get(self, key: str):
        """Get value from cache with performance tracking"""
        if key in self.cache:
            # Check TTL
            if time.time() - self.cache[key]['timestamp'] < self.ttl:
                self.access_times[key] = time.time()
                self.hit_count += 1
                return self.cache[key]['value']
            else:
                # Expired, remove from cache
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
        
        self.miss_count += 1
        return None
    
    async def set(self, key: str, value: any):
        """Set value in cache with performance tracking"""
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            await self._evict_lru()
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        self.access_times[key] = time.time()
    
    async def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def get_hit_ratio(self) -> float:
        """Get cache hit ratio"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0
```

#### **2. Database Connection Pooling**
```python
# Performance-Optimized Database Connection Pool
class DatabaseConnectionPool:
    def __init__(self, min_connections: int = 5, max_connections: int = 20):
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connections = []
        self.available_connections = []
        self.busy_connections = []
        self.metrics = DatabaseMetrics()
    
    async def get_connection(self):
        """Get database connection with performance monitoring"""
        start_time = time.time()
        
        try:
            if self.available_connections:
                connection = self.available_connections.pop()
            else:
                if len(self.connections) < self.max_connections:
                    connection = await self._create_connection()
                    self.connections.append(connection)
                else:
                    # Wait for available connection
                    connection = await self._wait_for_connection()
            
            self.busy_connections.append(connection)
            self.metrics.connection_count.set(len(self.busy_connections))
            
            return connection
            
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_query("connection_error", "pool", duration)
            raise e
    
    async def return_connection(self, connection):
        """Return connection to pool with performance monitoring"""
        if connection in self.busy_connections:
            self.busy_connections.remove(connection)
            self.available_connections.append(connection)
            self.metrics.connection_count.set(len(self.busy_connections))
    
    async def _create_connection(self):
        """Create new database connection"""
        # Implementation depends on database type
        pass
    
    async def _wait_for_connection(self):
        """Wait for available connection"""
        # Implementation for waiting logic
        pass
```

#### **3. Asynchronous Processing Optimization**
```python
# Performance-Optimized Asynchronous Processing
class AsyncProcessor:
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        self.metrics = AnalysisMetrics()
    
    async def process_batch(self, items: List[Any], process_func, batch_size: int = 100):
        """Process items in batches with performance monitoring"""
        start_time = time.time()
        
        try:
            # Process in batches
            results = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_results = await self._process_batch(batch, process_func)
                results.extend(batch_results)
            
            # Record performance metrics
            duration = time.time() - start_time
            self.metrics.record_analysis('batch_processing', 'success', duration)
            
            return results
            
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_analysis('batch_processing', 'failed', duration)
            raise e
    
    async def _process_batch(self, batch: List[Any], process_func):
        """Process a single batch with concurrency control"""
        async with self.semaphore:
            tasks = [process_func(item) for item in batch]
            return await asyncio.gather(*tasks)
```

### **Performance Benchmarking**

#### **1. Load Testing Framework**
```python
# Performance Load Testing
class LoadTester:
    def __init__(self, base_url: str, concurrent_users: int = 100):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []
    
    async def run_load_test(self, duration: int = 300):
        """Run load test for specified duration"""
        start_time = time.time()
        end_time = start_time + duration
        
        # Create concurrent users
        tasks = []
        for i in range(self.concurrent_users):
            task = asyncio.create_task(self._simulate_user(end_time))
            tasks.append(task)
        
        # Wait for all users to complete
        await asyncio.gather(*tasks)
        
        # Analyze results
        return self._analyze_results()
    
    async def _simulate_user(self, end_time: float):
        """Simulate a single user's behavior"""
        while time.time() < end_time:
            try:
                # Simulate user actions
                await self._perform_action()
                await asyncio.sleep(random.uniform(1, 5))  # Random delay
            except Exception as e:
                self.results.append({
                    'timestamp': time.time(),
                    'status': 'error',
                    'error': str(e)
                })
    
    async def _perform_action(self):
        """Perform a user action"""
        # Simulate API calls
        actions = [
            self._create_project,
            self._list_projects,
            self._get_project,
            self._run_analysis
        ]
        
        action = random.choice(actions)
        await action()
    
    def _analyze_results(self):
        """Analyze load test results"""
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r['status'] == 'success'])
        failed_requests = total_requests - successful_requests
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'error_rate': failed_requests / total_requests if total_requests > 0 else 0
        }
```

#### **2. Performance Regression Testing**
```python
# Performance Regression Testing
class PerformanceRegressionTester:
    def __init__(self):
        self.baseline_metrics = {}
        self.current_metrics = {}
    
    def set_baseline(self, metrics: Dict[str, float]):
        """Set performance baseline"""
        self.baseline_metrics = metrics
    
    def compare_performance(self, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Compare current performance with baseline"""
        self.current_metrics = current_metrics
        
        comparison = {}
        for metric, baseline_value in self.baseline_metrics.items():
            if metric in current_metrics:
                current_value = current_metrics[metric]
                improvement = ((baseline_value - current_value) / baseline_value) * 100
                
                comparison[metric] = {
                    'baseline': baseline_value,
                    'current': current_value,
                    'improvement_percent': improvement,
                    'status': 'improved' if improvement > 0 else 'degraded'
                }
        
        return comparison
    
    def detect_regressions(self, threshold: float = 10.0) -> List[str]:
        """Detect performance regressions above threshold"""
        regressions = []
        
        for metric, comparison in self.compare_performance(self.current_metrics).items():
            if comparison['status'] == 'degraded' and abs(comparison['improvement_percent']) > threshold:
                regressions.append(metric)
        
        return regressions
```

### **Performance Tuning Guidelines**

#### **1. Database Performance Tuning**
```sql
-- Database Performance Optimization
-- Index optimization
CREATE INDEX CONCURRENTLY idx_projects_status ON projects(status);
CREATE INDEX CONCURRENTLY idx_projects_created_at ON projects(created_at);
CREATE INDEX CONCURRENTLY idx_analyses_project_id ON analyses(project_id);

-- Query optimization
EXPLAIN ANALYZE SELECT * FROM projects WHERE status = 'completed' ORDER BY created_at DESC;

-- Connection pool tuning
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

#### **2. Application Performance Tuning**
```python
# Application Performance Tuning
class PerformanceTuner:
    def __init__(self):
        self.tuning_config = {
            'max_workers': 8,
            'connection_pool_size': 20,
            'cache_size': 1000,
            'batch_size': 100,
            'timeout': 30
        }
    
    def tune_application(self, metrics: Dict[str, float]):
        """Tune application based on performance metrics"""
        # CPU-bound optimization
        if metrics.get('cpu_usage', 0) > 80:
            self.tuning_config['max_workers'] = min(
                self.tuning_config['max_workers'] + 2, 16
            )
        
        # Memory-bound optimization
        if metrics.get('memory_usage', 0) > 80:
            self.tuning_config['cache_size'] = max(
                self.tuning_config['cache_size'] - 100, 500
            )
        
        # I/O-bound optimization
        if metrics.get('disk_io', 0) > 80:
            self.tuning_config['batch_size'] = min(
                self.tuning_config['batch_size'] + 50, 200
            )
        
        return self.tuning_config
```

## 🔒 Security Considerations

### **Security Overview**

The MeshLog system implements comprehensive security measures to protect data, ensure system integrity, and maintain compliance with security standards. Security is integrated throughout all system layers, from authentication and authorization to data encryption and secure communication.

### **Security Architecture**

#### **1. Security Layers**
```mermaid
graph TD
    A[Network Security] --> B[Application Security]
    B --> C[Data Security]
    C --> D[Infrastructure Security]
    D --> E[Operational Security]
    
    A --> A1[Firewall Rules]
    A --> A2[DDoS Protection]
    A --> A3[Network Segmentation]
    
    B --> B1[Authentication]
    B --> B2[Authorization]
    B --> B3[Input Validation]
    B --> B4[Output Encoding]
    
    C --> C1[Data Encryption]
    C --> C2[Data Masking]
    C --> C3[Data Backup]
    C --> C4[Data Retention]
    
    D --> D1[Container Security]
    D --> D2[Host Security]
    D --> D3[Network Security]
    D --> D4[Monitoring]
    
    E --> E1[Access Control]
    E --> E2[Audit Logging]
    E --> E3[Incident Response]
    E --> E4[Security Training]
```

#### **2. Security Principles**
- **Defense in Depth**: Multiple security layers
- **Least Privilege**: Minimal necessary access
- **Zero Trust**: Verify everything, trust nothing
- **Security by Design**: Built-in security from the start
- **Continuous Monitoring**: Real-time security monitoring

### **Authentication and Authorization**

#### **1. Authentication System**
```python
# JWT-based Authentication
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

class AuthenticationService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = get_settings().JWT_SECRET_KEY
        self.algorithm = get_settings().JWT_ALGORITHM
        self.access_token_expire_minutes = get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
```

#### **2. Role-Based Access Control (RBAC)**
```python
# Role-Based Access Control
class RBACService:
    def __init__(self):
        self.roles = {
            "admin": ["read", "write", "delete", "manage_users", "manage_system"],
            "analyst": ["read", "write", "run_analysis"],
            "viewer": ["read"],
            "guest": ["read_public"]
        }
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """Check if user role has specific permission"""
        if user_role not in self.roles:
            return False
        return permission in self.roles[user_role]
    
    def get_user_permissions(self, user_role: str) -> List[str]:
        """Get all permissions for a user role"""
        return self.roles.get(user_role, [])
    
    def check_resource_access(self, user_id: str, resource_type: str, resource_id: str, action: str) -> bool:
        """Check if user can access specific resource"""
        # Implementation depends on resource ownership and sharing policies
        pass
```

#### **3. API Security Middleware**
```python
# API Security Middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware for all requests"""
    # Add security headers
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/projects")
@limiter.limit("10/minute")
async def create_project(request: Request, ...):
    """Rate-limited project creation"""
    pass
```

### **Data Security**

#### **1. Data Encryption**
```python
# Data Encryption Service
from cryptography.fernet import Fernet
import base64

class DataEncryptionService:
    def __init__(self):
        self.key = get_settings().ENCRYPTION_KEY.encode()
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(decoded_data)
        return decrypted_data.decode()
    
    def encrypt_file(self, file_path: str, output_path: str):
        """Encrypt file"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str):
        """Decrypt file"""
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
```

#### **2. Data Masking and Anonymization**
```python
# Data Masking Service
class DataMaskingService:
    def __init__(self):
        self.masking_rules = {
            "email": self._mask_email,
            "phone": self._mask_phone,
            "ip_address": self._mask_ip,
            "mac_address": self._mask_mac,
            "ssn": self._mask_ssn
        }
    
    def mask_sensitive_data(self, data: dict, fields_to_mask: List[str]) -> dict:
        """Mask sensitive fields in data"""
        masked_data = data.copy()
        
        for field in fields_to_mask:
            if field in masked_data:
                field_type = self._detect_field_type(field, masked_data[field])
                if field_type in self.masking_rules:
                    masked_data[field] = self.masking_rules[field_type](masked_data[field])
        
        return masked_data
    
    def _mask_email(self, email: str) -> str:
        """Mask email address"""
        if '@' in email:
            local, domain = email.split('@', 1)
            return f"{local[:2]}***@{domain}"
        return "***@***"
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number"""
        if len(phone) >= 4:
            return f"***-***-{phone[-4:]}"
        return "***-***-****"
    
    def _mask_ip(self, ip: str) -> str:
        """Mask IP address"""
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.***.***"
        return "***.***.***.***"
    
    def _mask_mac(self, mac: str) -> str:
        """Mask MAC address"""
        if len(mac) >= 6:
            return f"**:**:**:**:**{mac[-2:]}"
        return "**:**:**:**:****"
    
    def _mask_ssn(self, ssn: str) -> str:
        """Mask SSN"""
        if len(ssn) >= 4:
            return f"***-**-{ssn[-4:]}"
        return "***-**-****"
```

#### **3. Data Retention and Purging**
```python
# Data Retention Service
class DataRetentionService:
    def __init__(self):
        self.retention_policies = {
            "projects": 365,  # 1 year
            "analyses": 180,  # 6 months
            "logs": 90,       # 3 months
            "temp_files": 7   # 1 week
        }
    
    async def enforce_retention_policies(self):
        """Enforce data retention policies"""
        for data_type, retention_days in self.retention_policies.items():
            await self._purge_expired_data(data_type, retention_days)
    
    async def _purge_expired_data(self, data_type: str, retention_days: int):
        """Purge expired data"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        if data_type == "projects":
            await self._purge_expired_projects(cutoff_date)
        elif data_type == "analyses":
            await self._purge_expired_analyses(cutoff_date)
        elif data_type == "logs":
            await self._purge_expired_logs(cutoff_date)
        elif data_type == "temp_files":
            await self._purge_temp_files(cutoff_date)
    
    async def _purge_expired_projects(self, cutoff_date: datetime):
        """Purge expired projects"""
        # Implementation for purging expired projects
        pass
    
    async def _purge_expired_analyses(self, cutoff_date: datetime):
        """Purge expired analyses"""
        # Implementation for purging expired analyses
        pass
    
    async def _purge_expired_logs(self, cutoff_date: datetime):
        """Purge expired logs"""
        # Implementation for purging expired logs
        pass
    
    async def _purge_temp_files(self, cutoff_date: datetime):
        """Purge temporary files"""
        # Implementation for purging temporary files
        pass
```

### **Input Validation and Sanitization**

#### **1. Input Validation**
```python
# Input Validation Service
from pydantic import BaseModel, validator, Field
import re

class InputValidationService:
    def __init__(self):
        self.validation_rules = {
            "project_name": r"^[a-zA-Z0-9\s\-_]{1,100}$",
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "filename": r"^[a-zA-Z0-9._-]{1,255}$",
            "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        }
    
    def validate_input(self, field_name: str, value: str) -> bool:
        """Validate input against rules"""
        if field_name not in self.validation_rules:
            return True
        
        pattern = self.validation_rules[field_name]
        return bool(re.match(pattern, value))
    
    def sanitize_input(self, value: str) -> str:
        """Sanitize input to prevent injection attacks"""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
        sanitized = value
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    def validate_file_upload(self, filename: str, file_size: int, content_type: str) -> bool:
        """Validate file upload"""
        # Check filename
        if not self.validate_input("filename", filename):
            return False
        
        # Check file size
        max_size = get_settings().MAX_FILE_SIZE
        if file_size > max_size:
            return False
        
        # Check content type
        allowed_types = [
            "application/x-tar",
            "application/gzip",
            "application/x-gzip",
            "application/octet-stream"
        ]
        if content_type not in allowed_types:
            return False
        
        return True

# Pydantic models with validation
class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-Z0-9\s\-_]{1,100}$", v):
            raise ValueError('Invalid project name format')
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            # Remove potentially dangerous content
            dangerous_patterns = [
                r'<script.*?>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'<iframe.*?>.*?</iframe>'
            ]
            for pattern in dangerous_patterns:
                if re.search(pattern, v, re.IGNORECASE):
                    raise ValueError('Description contains potentially dangerous content')
        return v
```

#### **2. SQL Injection Prevention**
```python
# SQL Injection Prevention
class SecureDatabaseService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    async def execute_secure_query(self, query: str, params: tuple = None):
        """Execute query with parameterized statements"""
        # Use parameterized queries to prevent SQL injection
        if params is None:
            params = ()
        
        # Validate query structure
        if not self._validate_query_structure(query):
            raise ValueError("Invalid query structure")
        
        return await self.db_manager.execute_query(query, params)
    
    def _validate_query_structure(self, query: str) -> bool:
        """Validate query structure to prevent injection"""
        # Check for dangerous patterns
        dangerous_patterns = [
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*update\s+.*\s+set',
            r'union\s+select',
            r'--',
            r'/\*.*\*/'
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                return False
        
        return True
    
    async def get_projects_by_user(self, user_id: str, limit: int = 10, offset: int = 0):
        """Get projects by user with secure query"""
        query = """
        SELECT id, name, description, status, created_at 
        FROM projects 
        WHERE created_by = ? 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
        """
        params = (user_id, limit, offset)
        return await self.execute_secure_query(query, params)
```

### **Network Security**

#### **1. HTTPS/TLS Configuration**
```python
# HTTPS/TLS Configuration
class TLSService:
    def __init__(self):
        self.tls_config = {
            "cert_file": get_settings().TLS_CERT_FILE,
            "key_file": get_settings().TLS_KEY_FILE,
            "ca_file": get_settings().TLS_CA_FILE,
            "min_version": "TLSv1.2",
            "ciphers": [
                "ECDHE-RSA-AES256-GCM-SHA384",
                "ECDHE-RSA-AES128-GCM-SHA256",
                "ECDHE-RSA-AES256-SHA384",
                "ECDHE-RSA-AES128-SHA256"
            ]
        }
    
    def get_tls_context(self):
        """Get TLS context for secure connections"""
        import ssl
        
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(self.tls_config["cert_file"], self.tls_config["key_file"])
        
        if self.tls_config["ca_file"]:
            context.load_verify_locations(self.tls_config["ca_file"])
        
        context.minimum_version = getattr(ssl, f"TLSVersion.{self.tls_config['min_version'].upper()}")
        context.set_ciphers(':'.join(self.tls_config["ciphers"]))
        
        return context
```

#### **2. Network Access Control**
```python
# Network Access Control
class NetworkAccessControl:
    def __init__(self):
        self.allowed_ips = get_settings().ALLOWED_IPS
        self.blocked_ips = get_settings().BLOCKED_IPS
        self.rate_limits = get_settings().RATE_LIMITS
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        # Check blocked IPs first
        if ip_address in self.blocked_ips:
            return False
        
        # Check allowed IPs (if specified)
        if self.allowed_ips and ip_address not in self.allowed_ips:
            return False
        
        return True
    
    def check_rate_limit(self, ip_address: str, endpoint: str) -> bool:
        """Check rate limit for IP and endpoint"""
        key = f"{ip_address}:{endpoint}"
        current_time = time.time()
        
        # Implementation depends on rate limiting backend (Redis, etc.)
        # This is a simplified version
        return True  # Placeholder
```

### **Container and Infrastructure Security**

#### **1. Container Security**
```dockerfile
# Secure Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r meshlog && useradd -r -g meshlog meshlog

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=meshlog:meshlog . .

# Switch to non-root user
USER meshlog

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **2. Security Scanning**
```python
# Security Scanning Service
class SecurityScanner:
    def __init__(self):
        self.scan_rules = {
            "vulnerabilities": self._scan_vulnerabilities,
            "secrets": self._scan_secrets,
            "dependencies": self._scan_dependencies,
            "configuration": self._scan_configuration
        }
    
    async def run_security_scan(self, scan_type: str) -> dict:
        """Run security scan"""
        if scan_type not in self.scan_rules:
            raise ValueError(f"Unknown scan type: {scan_type}")
        
        return await self.scan_rules[scan_type]()
    
    async def _scan_vulnerabilities(self) -> dict:
        """Scan for known vulnerabilities"""
        # Implementation for vulnerability scanning
        return {"status": "completed", "vulnerabilities": []}
    
    async def _scan_secrets(self) -> dict:
        """Scan for exposed secrets"""
        # Implementation for secret scanning
        return {"status": "completed", "secrets": []}
    
    async def _scan_dependencies(self) -> dict:
        """Scan dependencies for vulnerabilities"""
        # Implementation for dependency scanning
        return {"status": "completed", "vulnerable_dependencies": []}
    
    async def _scan_configuration(self) -> dict:
        """Scan configuration for security issues"""
        # Implementation for configuration scanning
        return {"status": "completed", "issues": []}
```

### **Audit Logging and Monitoring**

#### **1. Security Audit Logging**
```python
# Security Audit Logging
class SecurityAuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler("security_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_authentication_attempt(self, user_id: str, ip_address: str, success: bool):
        """Log authentication attempt"""
        event = {
            "event_type": "authentication_attempt",
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"Authentication attempt: {event}")
    
    def log_authorization_failure(self, user_id: str, resource: str, action: str):
        """Log authorization failure"""
        event = {
            "event_type": "authorization_failure",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.warning(f"Authorization failure: {event}")
    
    def log_data_access(self, user_id: str, resource_type: str, resource_id: str, action: str):
        """Log data access"""
        event = {
            "event_type": "data_access",
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"Data access: {event}")
    
    def log_security_event(self, event_type: str, details: dict):
        """Log general security event"""
        event = {
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.warning(f"Security event: {event}")
```

#### **2. Security Monitoring**
```python
# Security Monitoring Service
class SecurityMonitoringService:
    def __init__(self):
        self.alert_thresholds = {
            "failed_login_attempts": 5,
            "authorization_failures": 10,
            "suspicious_activity": 3,
            "data_access_anomalies": 5
        }
        self.monitoring_rules = {
            "brute_force": self._detect_brute_force,
            "privilege_escalation": self._detect_privilege_escalation,
            "data_exfiltration": self._detect_data_exfiltration,
            "anomalous_access": self._detect_anomalous_access
        }
    
    async def monitor_security_events(self):
        """Monitor security events in real-time"""
        while True:
            try:
                # Check for security events
                for rule_name, rule_func in self.monitoring_rules.items():
                    await rule_func()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _detect_brute_force(self):
        """Detect brute force attacks"""
        # Implementation for brute force detection
        pass
    
    async def _detect_privilege_escalation(self):
        """Detect privilege escalation attempts"""
        # Implementation for privilege escalation detection
        pass
    
    async def _detect_data_exfiltration(self):
        """Detect data exfiltration attempts"""
        # Implementation for data exfiltration detection
        pass
    
    async def _detect_anomalous_access(self):
        """Detect anomalous access patterns"""
        # Implementation for anomalous access detection
        pass
```

### **Compliance and Standards**

#### **1. Security Compliance Framework**
```python
# Security Compliance Framework
class SecurityComplianceFramework:
    def __init__(self):
        self.compliance_standards = {
            "ISO27001": self._check_iso27001_compliance,
            "SOC2": self._check_soc2_compliance,
            "GDPR": self._check_gdpr_compliance,
            "HIPAA": self._check_hipaa_compliance
        }
    
    async def check_compliance(self, standard: str) -> dict:
        """Check compliance with security standard"""
        if standard not in self.compliance_standards:
            raise ValueError(f"Unknown compliance standard: {standard}")
        
        return await self.compliance_standards[standard]()
    
    async def _check_iso27001_compliance(self) -> dict:
        """Check ISO 27001 compliance"""
        # Implementation for ISO 27001 compliance checking
        return {"status": "compliant", "score": 95, "issues": []}
    
    async def _check_soc2_compliance(self) -> dict:
        """Check SOC 2 compliance"""
        # Implementation for SOC 2 compliance checking
        return {"status": "compliant", "score": 92, "issues": []}
    
    async def _check_gdpr_compliance(self) -> dict:
        """Check GDPR compliance"""
        # Implementation for GDPR compliance checking
        return {"status": "compliant", "score": 98, "issues": []}
    
    async def _check_hipaa_compliance(self) -> dict:
        """Check HIPAA compliance"""
        # Implementation for HIPAA compliance checking
        return {"status": "compliant", "score": 90, "issues": []}
```

### **Security Best Practices**

#### **1. Development Security**
- **Secure Coding**: Follow secure coding practices
- **Code Review**: Mandatory security code reviews
- **Dependency Management**: Regular dependency updates
- **Secret Management**: Use secure secret management
- **Testing**: Security testing in CI/CD pipeline

#### **2. Deployment Security**
- **Container Security**: Use secure container images
- **Network Security**: Implement network segmentation
- **Access Control**: Restrict access to production systems
- **Monitoring**: Continuous security monitoring
- **Updates**: Regular security updates

#### **3. Operational Security**
- **Incident Response**: Defined incident response procedures
- **Backup Security**: Secure backup and recovery
- **Access Management**: Regular access reviews
- **Training**: Security awareness training
- **Documentation**: Security documentation and procedures

## 📈 Monitoring and Alerting System

### **Monitoring Overview**

The MeshLog system implements comprehensive monitoring and alerting capabilities to ensure system health, performance, and reliability. The monitoring system provides real-time visibility into system operations, proactive alerting for issues, and detailed analytics for performance optimization.

### **Monitoring Architecture**

#### **1. Monitoring Stack**
```mermaid
graph TD
    A[Application Metrics] --> B[Metrics Collector]
    B --> C[Time Series Database]
    C --> D[Monitoring Dashboard]
    D --> E[Alerting Engine]
    E --> F[Notification Channels]
    
    G[Log Aggregation] --> H[Log Processor]
    H --> I[Log Storage]
    I --> J[Log Analysis]
    J --> K[Log Alerts]
    
    L[Health Checks] --> M[Health Monitor]
    M --> N[Status Dashboard]
    N --> O[Health Alerts]
    
    P[Distributed Tracing] --> Q[Trace Collector]
    Q --> R[Trace Storage]
    R --> S[Trace Analysis]
    S --> T[Performance Alerts]
```

#### **2. Monitoring Components**
- **Metrics Collection**: Prometheus-based metrics collection
- **Log Aggregation**: Centralized log collection and analysis
- **Health Monitoring**: Application and infrastructure health checks
- **Distributed Tracing**: Request tracing across services
- **Alerting**: Multi-channel alerting system
- **Dashboards**: Real-time monitoring dashboards

### **Metrics Collection**

#### **1. Application Metrics**
```python
# Application Metrics Collection
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import time

class ApplicationMetrics:
    def __init__(self):
        # HTTP Metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
        self.http_response_size = Histogram(
            'http_response_size_bytes',
            'HTTP response size',
            ['endpoint']
        )
        
        # Business Metrics
        self.projects_created_total = Counter(
            'projects_created_total',
            'Total projects created',
            ['status']
        )
        
        self.analyses_completed_total = Counter(
            'analyses_completed_total',
            'Total analyses completed',
            ['type', 'status']
        )
        
        self.active_users = Gauge(
            'active_users',
            'Number of active users'
        )
        
        # System Metrics
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage'
        )
        
        self.disk_usage = Gauge(
            'disk_usage_bytes',
            'Disk usage in bytes'
        )
        
        # Database Metrics
        self.database_connections = Gauge(
            'database_connections',
            'Number of database connections'
        )
        
        self.database_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration',
            ['operation', 'table']
        )
        
        # Cache Metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type']
        )
        
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type']
        )
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float, response_size: int):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        self.http_response_size.labels(endpoint=endpoint).observe(response_size)
    
    def record_project_creation(self, status: str):
        """Record project creation metric"""
        self.projects_created_total.labels(status=status).inc()
    
    def record_analysis_completion(self, analysis_type: str, status: str):
        """Record analysis completion metric"""
        self.analyses_completed_total.labels(type=analysis_type, status=status).inc()
    
    def update_system_metrics(self):
        """Update system metrics"""
        import psutil
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.used)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.set(cpu_percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.disk_usage.set(disk.used)
```

#### **2. Custom Metrics**
```python
# Custom Business Metrics
class BusinessMetrics:
    def __init__(self):
        # Analysis Metrics
        self.analysis_queue_size = Gauge(
            'analysis_queue_size',
            'Number of analyses in queue'
        )
        
        self.analysis_processing_time = Histogram(
            'analysis_processing_time_seconds',
            'Analysis processing time',
            ['analysis_type']
        )
        
        self.analysis_success_rate = Gauge(
            'analysis_success_rate',
            'Analysis success rate',
            ['analysis_type']
        )
        
        # Agent Metrics
        self.agent_execution_time = Histogram(
            'agent_execution_time_seconds',
            'Agent execution time',
            ['agent_type']
        )
        
        self.agent_success_rate = Gauge(
            'agent_success_rate',
            'Agent success rate',
            ['agent_type']
        )
        
        # Data Processing Metrics
        self.data_processing_throughput = Gauge(
            'data_processing_throughput_bytes_per_second',
            'Data processing throughput'
        )
        
        self.log_parsing_duration = Histogram(
            'log_parsing_duration_seconds',
            'Log parsing duration',
            ['log_type']
        )
        
        # User Activity Metrics
        self.user_sessions = Gauge(
            'user_sessions_active',
            'Number of active user sessions'
        )
        
        self.user_actions = Counter(
            'user_actions_total',
            'Total user actions',
            ['action_type', 'user_role']
        )
    
    def record_analysis_metrics(self, analysis_type: str, processing_time: float, success: bool):
        """Record analysis metrics"""
        self.analysis_processing_time.labels(analysis_type=analysis_type).observe(processing_time)
        
        # Update success rate (simplified calculation)
        # In production, this would be calculated over a time window
        pass
    
    def record_agent_metrics(self, agent_type: str, execution_time: float, success: bool):
        """Record agent metrics"""
        self.agent_execution_time.labels(agent_type=agent_type).observe(execution_time)
        
        # Update success rate
        pass
```

### **Log Aggregation and Analysis**

#### **1. Structured Logging**
```python
# Structured Logging Service
import structlog
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self):
        # Configure structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger()
    
    def log_request(self, method: str, endpoint: str, status_code: int, duration: float, user_id: str = None):
        """Log HTTP request"""
        self.logger.info(
            "HTTP request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration=duration,
            user_id=user_id
        )
    
    def log_analysis_event(self, event_type: str, analysis_id: str, analysis_type: str, status: str, details: dict = None):
        """Log analysis event"""
        self.logger.info(
            "Analysis event",
            event_type=event_type,
            analysis_id=analysis_id,
            analysis_type=analysis_type,
            status=status,
            details=details or {}
        )
    
    def log_security_event(self, event_type: str, user_id: str = None, ip_address: str = None, details: dict = None):
        """Log security event"""
        self.logger.warning(
            "Security event",
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {}
        )
    
    def log_error(self, error_type: str, error_message: str, stack_trace: str = None, context: dict = None):
        """Log error"""
        self.logger.error(
            "Application error",
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context or {}
        )
```

#### **2. Log Analysis and Alerting**
```python
# Log Analysis Service
class LogAnalysisService:
    def __init__(self):
        self.alert_rules = {
            "error_rate": {
                "threshold": 0.05,  # 5% error rate
                "window": 300,      # 5 minutes
                "action": "alert"
            },
            "response_time": {
                "threshold": 2.0,   # 2 seconds
                "window": 300,      # 5 minutes
                "action": "alert"
            },
            "security_events": {
                "threshold": 10,    # 10 events
                "window": 60,       # 1 minute
                "action": "alert"
            }
        }
    
    async def analyze_logs(self, log_data: List[dict]) -> List[dict]:
        """Analyze logs for patterns and anomalies"""
        alerts = []
        
        # Analyze error rates
        error_rate = self._calculate_error_rate(log_data)
        if error_rate > self.alert_rules["error_rate"]["threshold"]:
            alerts.append({
                "type": "error_rate_high",
                "severity": "warning",
                "message": f"Error rate is {error_rate:.2%}, above threshold of {self.alert_rules['error_rate']['threshold']:.2%}",
                "timestamp": datetime.now().isoformat()
            })
        
        # Analyze response times
        avg_response_time = self._calculate_avg_response_time(log_data)
        if avg_response_time > self.alert_rules["response_time"]["threshold"]:
            alerts.append({
                "type": "response_time_high",
                "severity": "warning",
                "message": f"Average response time is {avg_response_time:.2f}s, above threshold of {self.alert_rules['response_time']['threshold']}s",
                "timestamp": datetime.now().isoformat()
            })
        
        # Analyze security events
        security_events = self._count_security_events(log_data)
        if security_events > self.alert_rules["security_events"]["threshold"]:
            alerts.append({
                "type": "security_events_high",
                "severity": "critical",
                "message": f"High number of security events: {security_events}",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def _calculate_error_rate(self, log_data: List[dict]) -> float:
        """Calculate error rate from logs"""
        total_requests = len([log for log in log_data if log.get("event_type") == "http_request"])
        error_requests = len([log for log in log_data if log.get("status_code", 200) >= 400])
        
        return error_requests / total_requests if total_requests > 0 else 0
    
    def _calculate_avg_response_time(self, log_data: List[dict]) -> float:
        """Calculate average response time from logs"""
        response_times = [log.get("duration", 0) for log in log_data if log.get("event_type") == "http_request"]
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _count_security_events(self, log_data: List[dict]) -> int:
        """Count security events in logs"""
        return len([log for log in log_data if log.get("event_type") == "security_event"])
```

### **Health Monitoring**

#### **1. Health Check System**
```python
# Health Check Service
class HealthCheckService:
    def __init__(self):
        self.health_checks = {
            "database": self._check_database_health,
            "redis": self._check_redis_health,
            "disk_space": self._check_disk_space,
            "memory": self._check_memory_health,
            "external_services": self._check_external_services
        }
    
    async def run_health_checks(self) -> dict:
        """Run all health checks"""
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        for check_name, check_func in self.health_checks.items():
            try:
                check_result = await check_func()
                health_status["checks"][check_name] = check_result
                
                if check_result["status"] != "healthy":
                    health_status["overall_status"] = "unhealthy"
                    
            except Exception as e:
                health_status["checks"][check_name] = {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    async def _check_database_health(self) -> dict:
        """Check database health"""
        try:
            # Test database connection
            start_time = time.time()
            await db_manager.execute_query("SELECT 1")
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response_time < 1.0 else "degraded",
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_redis_health(self) -> dict:
        """Check Redis health"""
        try:
            # Test Redis connection
            start_time = time.time()
            await redis_client.ping()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response_time < 0.5 else "degraded",
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_disk_space(self) -> dict:
        """Check disk space"""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage("/")
            usage_percent = (used / total) * 100
            
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "usage_percent": usage_percent,
                "free_bytes": free,
                "total_bytes": total,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_memory_health(self) -> dict:
        """Check memory health"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "usage_percent": usage_percent,
                "available_bytes": memory.available,
                "total_bytes": memory.total,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_external_services(self) -> dict:
        """Check external services health"""
        try:
            # Check external agent services
            external_services = get_settings().EXTERNAL_SERVICES
            
            service_status = {}
            overall_status = "healthy"
            
            for service_name, service_url in external_services.items():
                try:
                    response = await httpx.get(f"{service_url}/health", timeout=5.0)
                    if response.status_code == 200:
                        service_status[service_name] = "healthy"
                    else:
                        service_status[service_name] = "unhealthy"
                        overall_status = "degraded"
                except Exception:
                    service_status[service_name] = "unreachable"
                    overall_status = "degraded"
            
            return {
                "status": overall_status,
                "services": service_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

### **Alerting System**

#### **1. Alert Rules Engine**
```python
# Alert Rules Engine
class AlertRulesEngine:
    def __init__(self):
        self.alert_rules = {
            "high_error_rate": {
                "metric": "http_requests_total",
                "condition": "error_rate > 0.05",
                "window": "5m",
                "severity": "warning",
                "enabled": True
            },
            "high_response_time": {
                "metric": "http_request_duration_seconds",
                "condition": "p95 > 2.0",
                "window": "5m",
                "severity": "warning",
                "enabled": True
            },
            "low_disk_space": {
                "metric": "disk_usage_percent",
                "condition": "value > 90",
                "window": "1m",
                "severity": "critical",
                "enabled": True
            },
            "high_memory_usage": {
                "metric": "memory_usage_percent",
                "condition": "value > 90",
                "window": "1m",
                "severity": "critical",
                "enabled": True
            },
            "analysis_failure_rate": {
                "metric": "analyses_completed_total",
                "condition": "failure_rate > 0.1",
                "window": "10m",
                "severity": "warning",
                "enabled": True
            }
        }
        
        self.alert_history = []
        self.alert_cooldowns = {}
    
    async def evaluate_rules(self, metrics_data: dict) -> List[dict]:
        """Evaluate alert rules against current metrics"""
        triggered_alerts = []
        
        for rule_name, rule_config in self.alert_rules.items():
            if not rule_config["enabled"]:
                continue
            
            # Check cooldown
            if self._is_in_cooldown(rule_name):
                continue
            
            # Evaluate rule condition
            if await self._evaluate_condition(rule_config, metrics_data):
                alert = {
                    "rule_name": rule_name,
                    "severity": rule_config["severity"],
                    "message": self._generate_alert_message(rule_name, rule_config, metrics_data),
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics_data.get(rule_config["metric"], {})
                }
                
                triggered_alerts.append(alert)
                self._set_cooldown(rule_name)
        
        return triggered_alerts
    
    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if rule is in cooldown period"""
        if rule_name not in self.alert_cooldowns:
            return False
        
        cooldown_end = self.alert_cooldowns[rule_name]
        return datetime.now() < cooldown_end
    
    def _set_cooldown(self, rule_name: str, minutes: int = 15):
        """Set cooldown period for rule"""
        self.alert_cooldowns[rule_name] = datetime.now() + timedelta(minutes=minutes)
    
    async def _evaluate_condition(self, rule_config: dict, metrics_data: dict) -> bool:
        """Evaluate alert condition"""
        # Simplified condition evaluation
        # In production, this would use a proper expression evaluator
        metric_name = rule_config["metric"]
        condition = rule_config["condition"]
        
        if metric_name not in metrics_data:
            return False
        
        metric_value = metrics_data[metric_name]
        
        # Parse and evaluate condition
        if ">" in condition:
            threshold = float(condition.split(">")[1].strip())
            return metric_value > threshold
        elif "<" in condition:
            threshold = float(condition.split("<")[1].strip())
            return metric_value < threshold
        elif "==" in condition:
            threshold = float(condition.split("==")[1].strip())
            return metric_value == threshold
        
        return False
    
    def _generate_alert_message(self, rule_name: str, rule_config: dict, metrics_data: dict) -> str:
        """Generate alert message"""
        messages = {
            "high_error_rate": "High error rate detected",
            "high_response_time": "High response time detected",
            "low_disk_space": "Low disk space warning",
            "high_memory_usage": "High memory usage detected",
            "analysis_failure_rate": "High analysis failure rate"
        }
        
        return messages.get(rule_name, f"Alert triggered: {rule_name}")
```

#### **2. Notification System**
```python
# Notification Service
class NotificationService:
    def __init__(self):
        self.notification_channels = {
            "email": EmailNotifier(),
            "slack": SlackNotifier(),
            "webhook": WebhookNotifier(),
            "sms": SMSNotifier()
        }
        
        self.notification_rules = {
            "critical": ["email", "slack", "sms"],
            "warning": ["email", "slack"],
            "info": ["slack"]
        }
    
    async def send_alert(self, alert: dict):
        """Send alert through appropriate channels"""
        severity = alert["severity"]
        channels = self.notification_rules.get(severity, ["slack"])
        
        for channel_name in channels:
            if channel_name in self.notification_channels:
                try:
                    await self.notification_channels[channel_name].send(alert)
                except Exception as e:
                    logger.error(f"Failed to send alert via {channel_name}: {e}")
    
    async def send_health_status(self, health_status: dict):
        """Send health status update"""
        if health_status["overall_status"] != "healthy":
            alert = {
                "type": "health_check",
                "severity": "warning",
                "message": f"System health status: {health_status['overall_status']}",
                "details": health_status,
                "timestamp": datetime.now().isoformat()
            }
            await self.send_alert(alert)

# Email Notifier
class EmailNotifier:
    def __init__(self):
        self.smtp_server = get_settings().SMTP_SERVER
        self.smtp_port = get_settings().SMTP_PORT
        self.smtp_username = get_settings().SMTP_USERNAME
        self.smtp_password = get_settings().SMTP_PASSWORD
        self.alert_recipients = get_settings().ALERT_EMAIL_RECIPIENTS
    
    async def send(self, alert: dict):
        """Send email alert"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = ", ".join(self.alert_recipients)
        msg['Subject'] = f"[{alert['severity'].upper()}] {alert['message']}"
        
        body = f"""
        Alert Details:
        - Type: {alert.get('type', 'Unknown')}
        - Severity: {alert['severity']}
        - Message: {alert['message']}
        - Timestamp: {alert['timestamp']}
        
        Details:
        {json.dumps(alert.get('details', {}), indent=2)}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)

# Slack Notifier
class SlackNotifier:
    def __init__(self):
        self.webhook_url = get_settings().SLACK_WEBHOOK_URL
        self.channel = get_settings().SLACK_ALERT_CHANNEL
    
    async def send(self, alert: dict):
        """Send Slack alert"""
        import httpx
        
        color_map = {
            "critical": "danger",
            "warning": "warning",
            "info": "good"
        }
        
        payload = {
            "channel": self.channel,
            "attachments": [{
                "color": color_map.get(alert["severity"], "good"),
                "title": f"[{alert['severity'].upper()}] {alert['message']}",
                "text": f"Timestamp: {alert['timestamp']}",
                "fields": [
                    {"title": "Type", "value": alert.get("type", "Unknown"), "short": True},
                    {"title": "Severity", "value": alert["severity"], "short": True}
                ]
            }]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(self.webhook_url, json=payload)
```

### **Dashboard and Visualization**

#### **1. Monitoring Dashboard**
```python
# Monitoring Dashboard Service
class MonitoringDashboard:
    def __init__(self):
        self.dashboard_config = {
            "system_overview": {
                "title": "System Overview",
                "widgets": [
                    {"type": "metric", "metric": "http_requests_total", "title": "HTTP Requests"},
                    {"type": "metric", "metric": "response_time", "title": "Response Time"},
                    {"type": "metric", "metric": "error_rate", "title": "Error Rate"},
                    {"type": "metric", "metric": "active_users", "title": "Active Users"}
                ]
            },
            "performance": {
                "title": "Performance Metrics",
                "widgets": [
                    {"type": "graph", "metric": "http_request_duration_seconds", "title": "Request Duration"},
                    {"type": "graph", "metric": "memory_usage", "title": "Memory Usage"},
                    {"type": "graph", "metric": "cpu_usage", "title": "CPU Usage"},
                    {"type": "graph", "metric": "disk_usage", "title": "Disk Usage"}
                ]
            },
            "business_metrics": {
                "title": "Business Metrics",
                "widgets": [
                    {"type": "counter", "metric": "projects_created_total", "title": "Projects Created"},
                    {"type": "counter", "metric": "analyses_completed_total", "title": "Analyses Completed"},
                    {"type": "gauge", "metric": "analysis_queue_size", "title": "Analysis Queue Size"},
                    {"type": "gauge", "metric": "analysis_success_rate", "title": "Analysis Success Rate"}
                ]
            }
        }
    
    async def get_dashboard_data(self, dashboard_name: str) -> dict:
        """Get dashboard data"""
        if dashboard_name not in self.dashboard_config:
            raise ValueError(f"Unknown dashboard: {dashboard_name}")
        
        dashboard_config = self.dashboard_config[dashboard_name]
        dashboard_data = {
            "title": dashboard_config["title"],
            "widgets": []
        }
        
        for widget_config in dashboard_config["widgets"]:
            widget_data = await self._get_widget_data(widget_config)
            dashboard_data["widgets"].append(widget_data)
        
        return dashboard_data
    
    async def _get_widget_data(self, widget_config: dict) -> dict:
        """Get widget data"""
        widget_type = widget_config["type"]
        metric_name = widget_config["metric"]
        
        if widget_type == "metric":
            return await self._get_metric_data(metric_name)
        elif widget_type == "graph":
            return await self._get_graph_data(metric_name)
        elif widget_type == "counter":
            return await self._get_counter_data(metric_name)
        elif widget_type == "gauge":
            return await self._get_gauge_data(metric_name)
        else:
            return {"error": f"Unknown widget type: {widget_type}"}
    
    async def _get_metric_data(self, metric_name: str) -> dict:
        """Get metric data"""
        # Implementation to fetch metric data from Prometheus
        return {
            "type": "metric",
            "metric": metric_name,
            "value": 0,  # Placeholder
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_graph_data(self, metric_name: str) -> dict:
        """Get graph data"""
        # Implementation to fetch time series data
        return {
            "type": "graph",
            "metric": metric_name,
            "data": [],  # Placeholder for time series data
            "timestamp": datetime.now().isoformat()
        }
```

### **Monitoring Best Practices**

#### **1. Metrics Design**
- **Use meaningful names**: Clear, descriptive metric names
- **Include labels**: Add relevant dimensions for filtering
- **Avoid high cardinality**: Don't create too many unique label combinations
- **Use appropriate types**: Counter, Gauge, Histogram, Summary
- **Document metrics**: Provide clear documentation for each metric

#### **2. Alerting Strategy**
- **Set appropriate thresholds**: Based on historical data and SLAs
- **Use multiple severity levels**: Critical, Warning, Info
- **Implement cooldowns**: Prevent alert fatigue
- **Test alerting**: Regularly test alert delivery
- **Review and tune**: Continuously improve alert rules

#### **3. Dashboard Design**
- **Focus on key metrics**: Show most important metrics prominently
- **Use appropriate visualizations**: Choose right chart types
- **Group related metrics**: Organize by functional areas
- **Provide context**: Include historical data for comparison
- **Make it actionable**: Include links to relevant systems

#### **4. Log Management**
- **Use structured logging**: JSON format for better parsing
- **Include correlation IDs**: Track requests across services
- **Set appropriate log levels**: Don't log everything at DEBUG
- **Implement log rotation**: Prevent disk space issues
- **Secure sensitive data**: Don't log passwords or tokens

## 💾 Backup and Recovery System

### **Backup and Recovery Overview**

The MeshLog system implements comprehensive backup and recovery capabilities to ensure data protection, business continuity, and disaster recovery. The system provides automated backups, point-in-time recovery, and disaster recovery procedures to minimize data loss and downtime.

### **Backup Architecture**

#### **1. Backup Strategy**
```mermaid
graph TD
    A[Data Sources] --> B[Backup Scheduler]
    B --> C[Backup Engine]
    C --> D[Data Compression]
    D --> E[Data Encryption]
    E --> F[Backup Storage]
    F --> G[Backup Verification]
    G --> H[Backup Catalog]
    
    I[Recovery Request] --> J[Recovery Engine]
    J --> K[Backup Selection]
    K --> L[Data Decryption]
    L --> M[Data Decompression]
    M --> N[Data Restoration]
    N --> O[Recovery Verification]
    
    P[Disaster Recovery] --> Q[Failover System]
    Q --> R[Data Synchronization]
    R --> S[Service Restoration]
```

#### **2. Backup Components**
- **Backup Scheduler**: Automated backup scheduling
- **Backup Engine**: Core backup processing
- **Data Compression**: Efficient storage utilization
- **Data Encryption**: Secure backup storage
- **Backup Storage**: Multiple storage backends
- **Backup Verification**: Data integrity validation
- **Recovery Engine**: Data restoration capabilities

### **Backup Types and Strategies**

#### **1. Full Backup**
```python
# Full Backup Service
class FullBackupService:
    def __init__(self):
        self.backup_config = {
            "schedule": "weekly",  # weekly, monthly
            "retention": 12,       # months
            "compression": True,
            "encryption": True,
            "verification": True
        }
    
    async def create_full_backup(self, backup_name: str = None) -> dict:
        """Create full system backup"""
        if not backup_name:
            backup_name = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_info = {
            "backup_id": str(uuid4()),
            "backup_name": backup_name,
            "backup_type": "full",
            "start_time": datetime.now(),
            "status": "in_progress",
            "components": []
        }
        
        try:
            # Backup database
            db_backup = await self._backup_database(backup_name)
            backup_info["components"].append(db_backup)
            
            # Backup file system
            fs_backup = await self._backup_file_system(backup_name)
            backup_info["components"].append(fs_backup)
            
            # Backup configuration
            config_backup = await self._backup_configuration(backup_name)
            backup_info["components"].append(config_backup)
            
            # Backup metadata
            metadata_backup = await self._backup_metadata(backup_name)
            backup_info["components"].append(metadata_backup)
            
            # Verify backup
            if self.backup_config["verification"]:
                verification_result = await self._verify_backup(backup_info)
                backup_info["verification"] = verification_result
            
            backup_info["status"] = "completed"
            backup_info["end_time"] = datetime.now()
            backup_info["duration"] = (backup_info["end_time"] - backup_info["start_time"]).total_seconds()
            
            # Update backup catalog
            await self._update_backup_catalog(backup_info)
            
            return backup_info
            
        except Exception as e:
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
            backup_info["end_time"] = datetime.now()
            raise e
    
    async def _backup_database(self, backup_name: str) -> dict:
        """Backup database"""
        db_backup = {
            "component": "database",
            "start_time": datetime.now(),
            "status": "in_progress"
        }
        
        try:
            # Create database dump
            dump_file = f"{backup_name}_database.sql"
            dump_path = os.path.join(get_settings().BACKUP_DIR, dump_file)
            
            # Use pg_dump for PostgreSQL or sqlite3 for SQLite
            if get_settings().DATABASE_URL.startswith("postgresql"):
                await self._backup_postgresql(dump_path)
            else:
                await self._backup_sqlite(dump_path)
            
            # Compress if enabled
            if self.backup_config["compression"]:
                compressed_path = await self._compress_file(dump_path)
                os.remove(dump_path)
                dump_path = compressed_path
            
            # Encrypt if enabled
            if self.backup_config["encryption"]:
                encrypted_path = await self._encrypt_file(dump_path)
                os.remove(dump_path)
                dump_path = encrypted_path
            
            db_backup["status"] = "completed"
            db_backup["file_path"] = dump_path
            db_backup["file_size"] = os.path.getsize(dump_path)
            db_backup["end_time"] = datetime.now()
            
            return db_backup
            
        except Exception as e:
            db_backup["status"] = "failed"
            db_backup["error"] = str(e)
            raise e
    
    async def _backup_file_system(self, backup_name: str) -> dict:
        """Backup file system"""
        fs_backup = {
            "component": "file_system",
            "start_time": datetime.now(),
            "status": "in_progress"
        }
        
        try:
            # Create tar archive of data directory
            archive_file = f"{backup_name}_filesystem.tar.gz"
            archive_path = os.path.join(get_settings().BACKUP_DIR, archive_file)
            
            data_dir = get_settings().DATA_DIR
            
            # Create tar archive
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(data_dir, arcname="data")
            
            # Encrypt if enabled
            if self.backup_config["encryption"]:
                encrypted_path = await self._encrypt_file(archive_path)
                os.remove(archive_path)
                archive_path = encrypted_path
            
            fs_backup["status"] = "completed"
            fs_backup["file_path"] = archive_path
            fs_backup["file_size"] = os.path.getsize(archive_path)
            fs_backup["end_time"] = datetime.now()
            
            return fs_backup
            
        except Exception as e:
            fs_backup["status"] = "failed"
            fs_backup["error"] = str(e)
            raise e
```

#### **2. Incremental Backup**
```python
# Incremental Backup Service
class IncrementalBackupService:
    def __init__(self):
        self.backup_config = {
            "schedule": "daily",
            "retention": 30,  # days
            "compression": True,
            "encryption": True,
            "verification": True
        }
    
    async def create_incremental_backup(self, backup_name: str = None) -> dict:
        """Create incremental backup"""
        if not backup_name:
            backup_name = f"incremental_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get last backup timestamp
        last_backup_time = await self._get_last_backup_time()
        
        backup_info = {
            "backup_id": str(uuid4()),
            "backup_name": backup_name,
            "backup_type": "incremental",
            "start_time": datetime.now(),
            "last_backup_time": last_backup_time,
            "status": "in_progress",
            "components": []
        }
        
        try:
            # Backup changed database records
            db_backup = await self._backup_changed_database_records(backup_name, last_backup_time)
            backup_info["components"].append(db_backup)
            
            # Backup changed files
            fs_backup = await self._backup_changed_files(backup_name, last_backup_time)
            backup_info["components"].append(fs_backup)
            
            # Verify backup
            if self.backup_config["verification"]:
                verification_result = await self._verify_backup(backup_info)
                backup_info["verification"] = verification_result
            
            backup_info["status"] = "completed"
            backup_info["end_time"] = datetime.now()
            backup_info["duration"] = (backup_info["end_time"] - backup_info["start_time"]).total_seconds()
            
            # Update backup catalog
            await self._update_backup_catalog(backup_info)
            
            return backup_info
            
        except Exception as e:
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
            backup_info["end_time"] = datetime.now()
            raise e
    
    async def _backup_changed_database_records(self, backup_name: str, last_backup_time: datetime) -> dict:
        """Backup changed database records"""
        db_backup = {
            "component": "database_changes",
            "start_time": datetime.now(),
            "status": "in_progress"
        }
        
        try:
            # Query for changed records
            changed_records = await self._get_changed_records(last_backup_time)
            
            if not changed_records:
                db_backup["status"] = "completed"
                db_backup["records_count"] = 0
                db_backup["end_time"] = datetime.now()
                return db_backup
            
            # Create backup file
            backup_file = f"{backup_name}_database_changes.json"
            backup_path = os.path.join(get_settings().BACKUP_DIR, backup_file)
            
            # Write changed records to file
            with open(backup_path, 'w') as f:
                json.dump(changed_records, f, indent=2, default=str)
            
            # Compress and encrypt
            if self.backup_config["compression"]:
                compressed_path = await self._compress_file(backup_path)
                os.remove(backup_path)
                backup_path = compressed_path
            
            if self.backup_config["encryption"]:
                encrypted_path = await self._encrypt_file(backup_path)
                os.remove(backup_path)
                backup_path = encrypted_path
            
            db_backup["status"] = "completed"
            db_backup["file_path"] = backup_path
            db_backup["records_count"] = len(changed_records)
            db_backup["file_size"] = os.path.getsize(backup_path)
            db_backup["end_time"] = datetime.now()
            
            return db_backup
            
        except Exception as e:
            db_backup["status"] = "failed"
            db_backup["error"] = str(e)
            raise e
    
    async def _get_changed_records(self, last_backup_time: datetime) -> List[dict]:
        """Get changed records since last backup"""
        # Implementation to query database for changed records
        # This would depend on the specific database schema
        pass
```

#### **3. Differential Backup**
```python
# Differential Backup Service
class DifferentialBackupService:
    def __init__(self):
        self.backup_config = {
            "schedule": "weekly",
            "retention": 8,  # weeks
            "compression": True,
            "encryption": True,
            "verification": True
        }
    
    async def create_differential_backup(self, backup_name: str = None) -> dict:
        """Create differential backup"""
        if not backup_name:
            backup_name = f"differential_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get last full backup timestamp
        last_full_backup_time = await self._get_last_full_backup_time()
        
        backup_info = {
            "backup_id": str(uuid4()),
            "backup_name": backup_name,
            "backup_type": "differential",
            "start_time": datetime.now(),
            "last_full_backup_time": last_full_backup_time,
            "status": "in_progress",
            "components": []
        }
        
        try:
            # Backup all changes since last full backup
            db_backup = await self._backup_database_since_full(backup_name, last_full_backup_time)
            backup_info["components"].append(db_backup)
            
            fs_backup = await self._backup_files_since_full(backup_name, last_full_backup_time)
            backup_info["components"].append(fs_backup)
            
            # Verify backup
            if self.backup_config["verification"]:
                verification_result = await self._verify_backup(backup_info)
                backup_info["verification"] = verification_result
            
            backup_info["status"] = "completed"
            backup_info["end_time"] = datetime.now()
            backup_info["duration"] = (backup_info["end_time"] - backup_info["start_time"]).total_seconds()
            
            # Update backup catalog
            await self._update_backup_catalog(backup_info)
            
            return backup_info
            
        except Exception as e:
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
            backup_info["end_time"] = datetime.now()
            raise e
```

### **Backup Storage and Management**

#### **1. Backup Storage Backends**
```python
# Backup Storage Service
class BackupStorageService:
    def __init__(self):
        self.storage_backends = {
            "local": LocalStorageBackend(),
            "s3": S3StorageBackend(),
            "gcs": GCSStorageBackend(),
            "azure": AzureStorageBackend()
        }
        
        self.primary_backend = get_settings().BACKUP_PRIMARY_STORAGE
        self.secondary_backends = get_settings().BACKUP_SECONDARY_STORAGE
    
    async def store_backup(self, backup_info: dict, file_path: str) -> dict:
        """Store backup in multiple backends"""
        storage_result = {
            "backup_id": backup_info["backup_id"],
            "storage_results": []
        }
        
        # Store in primary backend
        try:
            primary_result = await self.storage_backends[self.primary_backend].store(
                backup_info, file_path
            )
            storage_result["storage_results"].append(primary_result)
        except Exception as e:
            logger.error(f"Primary storage failed: {e}")
            storage_result["storage_results"].append({
                "backend": self.primary_backend,
                "status": "failed",
                "error": str(e)
            })
        
        # Store in secondary backends
        for backend_name in self.secondary_backends:
            try:
                secondary_result = await self.storage_backends[backend_name].store(
                    backup_info, file_path
                )
                storage_result["storage_results"].append(secondary_result)
            except Exception as e:
                logger.error(f"Secondary storage {backend_name} failed: {e}")
                storage_result["storage_results"].append({
                    "backend": backend_name,
                    "status": "failed",
                    "error": str(e)
                })
        
        return storage_result
    
    async def retrieve_backup(self, backup_id: str, backend: str = None) -> str:
        """Retrieve backup from storage"""
        if not backend:
            backend = self.primary_backend
        
        return await self.storage_backends[backend].retrieve(backup_id)

# Local Storage Backend
class LocalStorageBackend:
    def __init__(self):
        self.storage_path = get_settings().BACKUP_STORAGE_PATH
    
    async def store(self, backup_info: dict, file_path: str) -> dict:
        """Store backup locally"""
        try:
            # Create backup directory structure
            backup_dir = os.path.join(self.storage_path, backup_info["backup_id"])
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy backup file
            destination_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, destination_path)
            
            # Create metadata file
            metadata_path = os.path.join(backup_dir, "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(backup_info, f, indent=2, default=str)
            
            return {
                "backend": "local",
                "status": "success",
                "storage_path": backup_dir,
                "file_size": os.path.getsize(destination_path)
            }
            
        except Exception as e:
            return {
                "backend": "local",
                "status": "failed",
                "error": str(e)
            }
    
    async def retrieve(self, backup_id: str) -> str:
        """Retrieve backup from local storage"""
        backup_dir = os.path.join(self.storage_path, backup_id)
        if not os.path.exists(backup_dir):
            raise FileNotFoundError(f"Backup {backup_id} not found")
        
        # Find backup file
        for file in os.listdir(backup_dir):
            if file != "metadata.json":
                return os.path.join(backup_dir, file)
        
        raise FileNotFoundError(f"Backup file not found for {backup_id}")

# S3 Storage Backend
class S3StorageBackend:
    def __init__(self):
        self.bucket_name = get_settings().S3_BACKUP_BUCKET
        self.aws_access_key = get_settings().AWS_ACCESS_KEY_ID
        self.aws_secret_key = get_settings().AWS_SECRET_ACCESS_KEY
        self.region = get_settings().AWS_REGION
    
    async def store(self, backup_info: dict, file_path: str) -> dict:
        """Store backup in S3"""
        try:
            import boto3
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region
            )
            
            # Upload backup file
            backup_key = f"backups/{backup_info['backup_id']}/{os.path.basename(file_path)}"
            s3_client.upload_file(file_path, self.bucket_name, backup_key)
            
            # Upload metadata
            metadata_key = f"backups/{backup_info['backup_id']}/metadata.json"
            s3_client.put_object(
                Bucket=self.bucket_name,
                Key=metadata_key,
                Body=json.dumps(backup_info, indent=2, default=str)
            )
            
            return {
                "backend": "s3",
                "status": "success",
                "bucket": self.bucket_name,
                "key": backup_key,
                "file_size": os.path.getsize(file_path)
            }
            
        except Exception as e:
            return {
                "backend": "s3",
                "status": "failed",
                "error": str(e)
            }
    
    async def retrieve(self, backup_id: str) -> str:
        """Retrieve backup from S3"""
        try:
            import boto3
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region
            )
            
            # List objects in backup directory
            response = s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"backups/{backup_id}/"
            )
            
            # Find backup file (not metadata)
            for obj in response.get('Contents', []):
                if not obj['Key'].endswith('metadata.json'):
                    # Download file
                    local_path = os.path.join(get_settings().TEMP_DIR, os.path.basename(obj['Key']))
                    s3_client.download_file(self.bucket_name, obj['Key'], local_path)
                    return local_path
            
            raise FileNotFoundError(f"Backup {backup_id} not found in S3")
            
        except Exception as e:
            raise e
```

#### **2. Backup Catalog Management**
```python
# Backup Catalog Service
class BackupCatalogService:
    def __init__(self):
        self.catalog_file = os.path.join(get_settings().BACKUP_DIR, "backup_catalog.json")
        self.catalog = self._load_catalog()
    
    def _load_catalog(self) -> dict:
        """Load backup catalog"""
        if os.path.exists(self.catalog_file):
            with open(self.catalog_file, 'r') as f:
                return json.load(f)
        return {"backups": [], "metadata": {"version": "1.0", "created": datetime.now().isoformat()}}
    
    async def add_backup(self, backup_info: dict):
        """Add backup to catalog"""
        self.catalog["backups"].append(backup_info)
        await self._save_catalog()
    
    async def get_backup(self, backup_id: str) -> dict:
        """Get backup information"""
        for backup in self.catalog["backups"]:
            if backup["backup_id"] == backup_id:
                return backup
        raise ValueError(f"Backup {backup_id} not found")
    
    async def list_backups(self, backup_type: str = None, limit: int = 100) -> List[dict]:
        """List backups with optional filtering"""
        backups = self.catalog["backups"]
        
        if backup_type:
            backups = [b for b in backups if b["backup_type"] == backup_type]
        
        # Sort by start time (newest first)
        backups.sort(key=lambda x: x["start_time"], reverse=True)
        
        return backups[:limit]
    
    async def delete_backup(self, backup_id: str):
        """Delete backup from catalog"""
        self.catalog["backups"] = [
            b for b in self.catalog["backups"] if b["backup_id"] != backup_id
        ]
        await self._save_catalog()
    
    async def _save_catalog(self):
        """Save backup catalog"""
        with open(self.catalog_file, 'w') as f:
            json.dump(self.catalog, f, indent=2, default=str)
    
    async def cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        current_time = datetime.now()
        
        for backup in self.catalog["backups"][:]:  # Copy list to avoid modification during iteration
            backup_time = datetime.fromisoformat(backup["start_time"])
            
            # Check retention policy
            if backup["backup_type"] == "full":
                retention_days = 365  # 1 year
            elif backup["backup_type"] == "differential":
                retention_days = 56   # 8 weeks
            else:  # incremental
                retention_days = 30   # 30 days
            
            if (current_time - backup_time).days > retention_days:
                # Delete backup
                await self._delete_backup_files(backup)
                await self.delete_backup(backup["backup_id"])
                logger.info(f"Deleted old backup: {backup['backup_id']}")
    
    async def _delete_backup_files(self, backup_info: dict):
        """Delete backup files from storage"""
        # Implementation to delete backup files from all storage backends
        pass
```

### **Recovery System**

#### **1. Point-in-Time Recovery**
```python
# Point-in-Time Recovery Service
class PointInTimeRecoveryService:
    def __init__(self):
        self.recovery_config = {
            "max_recovery_time": 3600,  # 1 hour
            "verification": True,
            "rollback_on_failure": True
        }
    
    async def recover_to_point_in_time(self, target_time: datetime, recovery_name: str = None) -> dict:
        """Recover system to specific point in time"""
        if not recovery_name:
            recovery_name = f"recovery_{target_time.strftime('%Y%m%d_%H%M%S')}"
        
        recovery_info = {
            "recovery_id": str(uuid4()),
            "recovery_name": recovery_name,
            "target_time": target_time,
            "start_time": datetime.now(),
            "status": "in_progress",
            "steps": []
        }
        
        try:
            # Step 1: Find appropriate backup
            backup_info = await self._find_backup_for_time(target_time)
            recovery_info["steps"].append({
                "step": "find_backup",
                "status": "completed",
                "backup_id": backup_info["backup_id"]
            })
            
            # Step 2: Restore database
            db_recovery = await self._recover_database(backup_info, target_time)
            recovery_info["steps"].append(db_recovery)
            
            # Step 3: Restore file system
            fs_recovery = await self._recover_file_system(backup_info, target_time)
            recovery_info["steps"].append(fs_recovery)
            
            # Step 4: Restore configuration
            config_recovery = await self._recover_configuration(backup_info)
            recovery_info["steps"].append(config_recovery)
            
            # Step 5: Verify recovery
            if self.recovery_config["verification"]:
                verification_result = await self._verify_recovery(recovery_info)
                recovery_info["verification"] = verification_result
            
            recovery_info["status"] = "completed"
            recovery_info["end_time"] = datetime.now()
            recovery_info["duration"] = (recovery_info["end_time"] - recovery_info["start_time"]).total_seconds()
            
            return recovery_info
            
        except Exception as e:
            recovery_info["status"] = "failed"
            recovery_info["error"] = str(e)
            recovery_info["end_time"] = datetime.now()
            
            # Rollback if enabled
            if self.recovery_config["rollback_on_failure"]:
                await self._rollback_recovery(recovery_info)
            
            raise e
    
    async def _find_backup_for_time(self, target_time: datetime) -> dict:
        """Find the most appropriate backup for the target time"""
        # Get all backups
        all_backups = await BackupCatalogService().list_backups()
        
        # Filter backups before target time
        valid_backups = [
            b for b in all_backups 
            if datetime.fromisoformat(b["start_time"]) <= target_time
        ]
        
        if not valid_backups:
            raise ValueError(f"No backup found for time {target_time}")
        
        # Sort by start time (newest first)
        valid_backups.sort(key=lambda x: x["start_time"], reverse=True)
        
        # Prefer full backup, then differential, then incremental
        for backup_type in ["full", "differential", "incremental"]:
            for backup in valid_backups:
                if backup["backup_type"] == backup_type:
                    return backup
        
        # Fallback to newest backup
        return valid_backups[0]
    
    async def _recover_database(self, backup_info: dict, target_time: datetime) -> dict:
        """Recover database to target time"""
        db_recovery = {
            "step": "recover_database",
            "start_time": datetime.now(),
            "status": "in_progress"
        }
        
        try:
            # Retrieve backup files
            backup_files = await self._retrieve_backup_files(backup_info)
            
            # Restore database
            if backup_info["backup_type"] == "full":
                await self._restore_full_database(backup_files)
            else:
                # For incremental/differential, need to restore from full backup first
                full_backup = await self._find_full_backup_for_backup(backup_info)
                full_backup_files = await self._retrieve_backup_files(full_backup)
                await self._restore_full_database(full_backup_files)
                
                # Then apply incremental changes
                await self._apply_incremental_changes(backup_files, target_time)
            
            db_recovery["status"] = "completed"
            db_recovery["end_time"] = datetime.now()
            
            return db_recovery
            
        except Exception as e:
            db_recovery["status"] = "failed"
            db_recovery["error"] = str(e)
            raise e
    
    async def _restore_full_database(self, backup_files: List[str]):
        """Restore full database from backup"""
        # Find database backup file
        db_file = None
        for file_path in backup_files:
            if "database" in os.path.basename(file_path):
                db_file = file_path
                break
        
        if not db_file:
            raise ValueError("Database backup file not found")
        
        # Decrypt if needed
        if db_file.endswith('.enc'):
            decrypted_file = await self._decrypt_file(db_file)
            os.remove(db_file)
            db_file = decrypted_file
        
        # Decompress if needed
        if db_file.endswith('.gz'):
            decompressed_file = await self._decompress_file(db_file)
            os.remove(db_file)
            db_file = decompressed_file
        
        # Restore database
        if get_settings().DATABASE_URL.startswith("postgresql"):
            await self._restore_postgresql(db_file)
        else:
            await self._restore_sqlite(db_file)
    
    async def _apply_incremental_changes(self, backup_files: List[str], target_time: datetime):
        """Apply incremental changes to database"""
        # Find incremental backup files
        for file_path in backup_files:
            if "database_changes" in os.path.basename(file_path):
                # Decrypt and decompress
                if file_path.endswith('.enc'):
                    decrypted_file = await self._decrypt_file(file_path)
                    os.remove(file_path)
                    file_path = decrypted_file
                
                if file_path.endswith('.gz'):
                    decompressed_file = await self._decompress_file(file_path)
                    os.remove(file_path)
                    file_path = decompressed_file
                
                # Load changes
                with open(file_path, 'r') as f:
                    changes = json.load(f)
                
                # Apply changes up to target time
                for change in changes:
                    change_time = datetime.fromisoformat(change["timestamp"])
                    if change_time <= target_time:
                        await self._apply_database_change(change)
```

#### **2. Disaster Recovery**
```python
# Disaster Recovery Service
class DisasterRecoveryService:
    def __init__(self):
        self.dr_config = {
            "rto": 3600,  # Recovery Time Objective: 1 hour
            "rpo": 300,   # Recovery Point Objective: 5 minutes
            "failover_automation": True,
            "health_check_interval": 60
        }
    
    async def initiate_disaster_recovery(self, disaster_type: str) -> dict:
        """Initiate disaster recovery procedures"""
        dr_info = {
            "dr_id": str(uuid4()),
            "disaster_type": disaster_type,
            "start_time": datetime.now(),
            "status": "in_progress",
            "steps": []
        }
        
        try:
            # Step 1: Assess disaster impact
            impact_assessment = await self._assess_disaster_impact(disaster_type)
            dr_info["steps"].append(impact_assessment)
            
            # Step 2: Activate failover system
            failover_result = await self._activate_failover_system()
            dr_info["steps"].append(failover_result)
            
            # Step 3: Restore data from backup
            data_restoration = await self._restore_data_from_backup()
            dr_info["steps"].append(data_restoration)
            
            # Step 4: Synchronize services
            service_sync = await self._synchronize_services()
            dr_info["steps"].append(service_sync)
            
            # Step 5: Verify system health
            health_verification = await self._verify_system_health()
            dr_info["steps"].append(health_verification)
            
            # Step 6: Update DNS/routing
            routing_update = await self._update_routing()
            dr_info["steps"].append(routing_update)
            
            dr_info["status"] = "completed"
            dr_info["end_time"] = datetime.now()
            dr_info["duration"] = (dr_info["end_time"] - dr_info["start_time"]).total_seconds()
            
            return dr_info
            
        except Exception as e:
            dr_info["status"] = "failed"
            dr_info["error"] = str(e)
            dr_info["end_time"] = datetime.now()
            raise e
    
    async def _assess_disaster_impact(self, disaster_type: str) -> dict:
        """Assess the impact of the disaster"""
        assessment = {
            "step": "assess_impact",
            "start_time": datetime.now(),
            "status": "in_progress"
        }
        
        try:
            # Check system components
            components_status = {
                "database": await self._check_database_status(),
                "file_system": await self._check_file_system_status(),
                "external_services": await self._check_external_services_status(),
                "network": await self._check_network_status()
            }
            
            # Determine impact level
            failed_components = [k for k, v in components_status.items() if v["status"] != "healthy"]
            
            if len(failed_components) == 0:
                impact_level = "none"
            elif len(failed_components) <= 2:
                impact_level = "limited"
            else:
                impact_level = "severe"
            
            assessment["status"] = "completed"
            assessment["impact_level"] = impact_level
            assessment["failed_components"] = failed_components
            assessment["components_status"] = components_status
            assessment["end_time"] = datetime.now()
            
            return assessment
            
        except Exception as e:
            assessment["status"] = "failed"
            assessment["error"] = str(e)
            raise e
    
    async def _activate_failover_system(self) -> dict:
        """Activate failover system"""
        failover = {
            "step": "activate_failover",
            "start_time": datetime.now(),
            "status": "in_progress"
        }
        
        try:
            # Start failover services
            failover_services = get_settings().FAILOVER_SERVICES
            
            for service_name, service_config in failover_services.items():
                await self._start_failover_service(service_name, service_config)
            
            # Wait for services to be ready
            await self._wait_for_services_ready(failover_services.keys())
            
            failover["status"] = "completed"
            failover["end_time"] = datetime.now()
            
            return failover
            
        except Exception as e:
            failover["status"] = "failed"
            failover["error"] = str(e)
            raise e
    
    async def _restore_data_from_backup(self) -> dict:
        """Restore data from backup"""
        restoration = {
            "step": "restore_data",
            "start_time": datetime.now(),
            "status": "in_progress"
        }
        
        try:
            # Get latest backup
            latest_backup = await self._get_latest_backup()
            
            # Restore database
            await self._restore_database_from_backup(latest_backup)
            
            # Restore file system
            await self._restore_file_system_from_backup(latest_backup)
            
            restoration["status"] = "completed"
            restoration["backup_used"] = latest_backup["backup_id"]
            restoration["end_time"] = datetime.now()
            
            return restoration
            
        except Exception as e:
            restoration["status"] = "failed"
            restoration["error"] = str(e)
            raise e
```

### **Backup and Recovery Best Practices**

#### **1. Backup Strategy**
- **3-2-1 Rule**: 3 copies, 2 different media, 1 offsite
- **Regular Testing**: Test backups regularly
- **Automated Scheduling**: Use automated backup scheduling
- **Incremental Approach**: Use incremental backups for efficiency
- **Verification**: Always verify backup integrity

#### **2. Recovery Planning**
- **RTO/RPO Definition**: Define Recovery Time and Point Objectives
- **Recovery Procedures**: Document step-by-step recovery procedures
- **Testing**: Regular disaster recovery testing
- **Automation**: Automate recovery procedures where possible
- **Communication**: Plan communication during disasters

#### **3. Data Protection**
- **Encryption**: Encrypt backups at rest and in transit
- **Access Control**: Restrict access to backup systems
- **Monitoring**: Monitor backup and recovery operations
- **Compliance**: Ensure compliance with data protection regulations
- **Documentation**: Maintain comprehensive documentation

## 🎯 Key Benefits

### Architectural Benefits

1. **Clear Separation of Concerns**: Projects, Applications, and Agents have distinct responsibilities
2. **Scalability**: Each tier can be scaled independently
3. **Maintainability**: Clear boundaries make the system easier to maintain and extend
4. **Flexibility**: Easy to add new applications and agents without affecting existing components
5. **Performance**: Optimized data flow and processing at each tier

### User Experience Benefits

1. **Intuitive Workflow**: Clear progression from project creation to analysis results
2. **Application Focus**: Users can work with specific applications without confusion
3. **Comprehensive Analysis**: Two-tier analysis provides both foundational and advanced insights
4. **Flexible Selection**: Users can choose which applications to analyze
5. **Rich Results**: Multiple analysis layers provide comprehensive insights

## 🔮 Future Extensibility

### Adding New Applications

1. **Define Application Type**: Create new application type (e.g., wnc-security)
2. **Implement Discovery**: Add patterns to identify the new application
3. **Create Agent**: Implement corresponding agent for specialized analysis
4. **Update UI**: Add application-specific UI components

### Adding New Agents

1. **Implement Agent Interface**: Create new agent class
2. **Register Agent**: Add agent to the registry
3. **Configure Patterns**: Define application-specific patterns
4. **Test Integration**: Verify agent works with existing applications

### System Evolution

- **Microservices**: Can evolve to microservices architecture
- **Cloud Deployment**: Ready for cloud deployment and scaling
- **API Extensions**: Easy to add new API endpoints and capabilities
- **Integration**: Can integrate with external systems and tools

---

## 📚 Related Documentation

- [System Summary](SYSTEM_SUMMARY.md) - Complete system implementation overview
- [Agent Analysis System Guide](AGENT_ANALYSIS_SYSTEM_GUIDE.md) - Detailed agent system documentation
- [Deployment Guide](DEPLOYMENT.md) - System deployment instructions
- [API Documentation](API_CONSOLIDATION_COMPLETE.md) - API reference and examples

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Complete System Architecture Specification
