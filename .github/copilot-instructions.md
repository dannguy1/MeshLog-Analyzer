# MeshLog Analyzer - AI Coding Agent Instructions

## Project Overview

**MeshLog Analyzer** (prplOS LCM Log Analysis System) is a production-ready log analysis platform for WiFi mesh network diagnostics. The system processes containerized syslog packages, performs domain-specific analysis using modular agents, and provides real-time monitoring via WebSocket updates.

**Key Architecture**: FastAPI backend + React/TypeScript frontend + SQLite/Redis storage + Modular agent system

## Critical Data Flow & Storage Patterns

### Project-Scoped Architecture (Not Global Registries)
- **All data is project-scoped**: Projects live in `/data/WNC/LCM-Logs-Data/projects/{project_id}/`
- **Never use global analysis registries**: Use `ProjectAnalysisManager` for per-project analysis metadata
- **Application-level storage**: Each application gets its own directory at `{project_root}/applications/{app_name}/`
- **Analysis results**: Stored in application directories, not separate analysis collections

```python
# CORRECT: Project-scoped data access
from app.services.project_analysis_manager import ProjectAnalysisManager
manager = ProjectAnalysisManager(data_dir, project_id)
analyses = manager.get_analyses_metadata()  # Returns Dict[str, Analysis]

# WRONG: Don't use global analyses_db dictionary
analyses_db[analysis_id] = analysis  # Anti-pattern from legacy code
```

### DATA_DIR Configuration
- **Central storage**: Everything under `settings.DATA_DIR` (default: `/data/WNC/LCM-Logs-Data/`)
- **Path construction**: Always use `os.path.join(settings.DATA_DIR, ...)` for cross-machine compatibility
- **Normalization required**: Project paths may differ across machines; normalize on load (see `load_data()` in `app/main.py`)

## Agent System Architecture

### Agent Discovery & Registration
Agents are **automatically discovered** via `AgentRegistry` from `app.agents/` when `INTEGRATED_AGENTS_ENABLED=true`:

```python
# Agent must implement AgentInterface with required properties
from app.core.agent_interface import AgentInterface

class MyAgent(AgentInterface):
    @property
    def agent_type(self) -> str:
        return "my-app"  # Must match application name
    
    @property  
    def version(self) -> str:
        return "1.0.0"
    
    def analyze(self, log_paths: list, output_path: str, analysis_config: Dict = None) -> Dict:
        # Write results to output_path, return metadata
        pass
```

- **One-to-one binding**: Each agent analyzes exactly one application type (e.g., `wnc-steering` agent only processes `wnc-steer` logs)
- **Registry location**: `app/core/agent_registry.py` handles discovery via introspection
- **Export agents**: Add to `app/agents/__init__.py` to make discoverable

### Pattern Recognition Framework
Centralized pattern matching at `app/core/pattern_recognition.py` eliminates duplication:

```python
from app.core.pattern_recognition import PatternRegistry, AgentPatternInterface

# Initialize in agent constructor
self.pattern_registry = PatternRegistry()  # Auto-loads from patterns.json
self.pattern_interface = AgentPatternInterface("wnc-steering", self.pattern_registry)

# Use in analysis
result = self.pattern_interface.parse_log_line(line, line_number)
if result['status'] == 'matched':
    pattern_name = result['pattern_name']
    match_data = result['match_data']
```

- **Pattern config**: `patterns.json` at repo root defines all patterns with agent_types, priority, validation samples
- **Performance tracking**: Pattern registry tracks match counts and performance scores

## Development Workflows

### Local Development Start/Stop
```bash
# Start backend + frontend + Redis
./scripts/dev-start.sh              # Foreground (logs visible)
./scripts/dev-start.sh --background # Background with PID files

# Check status
./scripts/dev-status.sh

# Stop all services  
./scripts/dev-stop.sh
```

- **Backend**: Uvicorn on port 8000 with auto-reload
- **Frontend**: Vite dev server on port 3000 with HMR
- **Redis**: Port 6379 (required for background tasks)
- **Logs**: `logs/backend.log`, `logs/frontend.log`, `logs/app.log`

### Python Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Core dependencies
# OR for minimal install:
pip install -r requirements-minimal.txt
```

### Database Initialization
```bash
mkdir -p data logs
sqlite3 data/prplos_analysis.db < sqlite_schema.sql
# Each project gets its own SQLite DB at:
# /data/WNC/LCM-Logs-Data/projects/{project_id}/project.db
```

## API Structure & Refactoring Status

### Current State: Dual Main Files
- **Production**: `app/main.py` (2600+ lines, monolithic, actively used)
- **Refactored**: `app/main_refactored.py` (76 lines, modular routers, not yet active)

**When editing APIs**:
1. **Default to `app/main.py`** unless refactoring
2. Refactored routers exist in `app/routers/` (health, projects, analysis, admin, visualization)
3. Migration to `main_refactored.py` is planned but incomplete (see `refactoring_plan.md`)

### Key Endpoints
- `POST /api/v1/projects` - Upload .tar.gz syslog package (validates name/file, extracts, discovers applications)
- `POST /api/v1/projects/{id}/analyze/{app}` - Trigger agent analysis for specific application
- `GET /api/v1/projects` - List all projects with metadata
- `WebSocket /ws/{project_id}` - Real-time analysis progress updates via `websocket_manager.py`

## Testing & Validation

### Running Tests
```bash
# Pattern recognition tests
python test_802.11kv_detection.py

# Agent integration tests  
python test_agent_integration.py
python test_integrated_agents_container.py

# Final integration test
python test_final_integration.py
```

### Debugging Analysis Issues
```bash
# Check project structure
./scripts/health-check-projects.sh

# Validate agent registry
python validate_agent_registry.py

# Backend debug mode
./scripts/backend-debug.sh
```

## Docker Deployment

### Standard Deployment
```bash
docker compose up -d  # Development
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d  # Production
```

### Agent-Integrated Deployment
```bash
# Uses docker-compose.agent.yml with Redis coordination
docker compose -f docker-compose.agent.yml up -d
```

- **Shared volumes**: `/data/WNC/LCM-Logs-Data` mounted across containers
- **Redis URL**: Containers use `redis://redis:6379/0` (service name)
- **Health checks**: All services have HTTP/Redis health checks

## Project-Specific Conventions

### File Naming & Module Organization
- **Agents**: `app/agents/wnc_{application}.py` (e.g., `wnc_steering.py`, `wnc_acs.py`)
- **Agent modules**: Subdirectories like `app/agents/acs_modules/`, `steering_modules/` for component classes
- **Report generators**: `{agent}_report_generator.py` for HTML/CSV output generation
- **Services**: `app/services/` for managers (ProjectAnalysisManager, RedisManager, etc.)

### Configuration Management
```python
from app.core.config import get_settings

settings = get_settings()  # Singleton instance
# All env vars defined in Settings class with Field defaults
# Env file: .env (gitignored), template: env.config
```

**Critical env vars**:
- `DATA_DIR` - Absolute path to persistent storage
- `WNC_LOG_AGENTS_ENABLED` - Enable external agent services (default: false)
- `INTEGRATED_AGENTS_ENABLED` - Enable built-in agents (default: true)
- `REDIS_URL` - Redis connection string

### Application Discovery Flow
1. Package uploaded → `PackageProcessor` extracts to `{project_dir}/extracted/`
2. `ApplicationClassifier` scans logs for component identifiers (`wnc-acs:`, `wnc-steer:`, etc.)
3. Application metadata saved to `{project_dir}/applications/{app_name}/discovery_metadata.json`
4. Agent analysis reads from application directory, writes results to same location

## Anti-Patterns to Avoid

❌ **Don't create global analysis collections** - Use ProjectAnalysisManager  
❌ **Don't hardcode paths** - Always use `settings.DATA_DIR` + `os.path.join()`  
❌ **Don't bypass pattern framework** - Use PatternRegistry instead of custom regex  
❌ **Don't modify `main.py` and `main_refactored.py` inconsistently** - Check refactoring_plan.md first  
❌ **Don't skip agent type validation** - Agents must only process their designated application  

## Documentation Structure

- `README.md` - Quick start, installation, basic usage
- `docs/architecture/` - System specs, agent architecture, gap analysis
- `docs/operations/` - Deployment guides, security, monitoring
- `docs/guides/` - User-facing product documentation
- `refactoring_plan.md` - Endpoint migration strategy (main.py → main_refactored.py)
- `GITHUB_SETUP.md` - Repository initialization checklist

## WebSocket Real-Time Updates

```python
from app.websocket_manager import manager

# In background task
await manager.send_progress(project_id, {
    "status": "analyzing",
    "application": "wnc-steering", 
    "progress": 50,
    "message": "Processing steering events..."
})
```

Frontend receives updates via `/ws/{project_id}` connection for live progress bars.

---

**When in doubt**: Check `app/main.py` for production patterns, use `semantic_search` for cross-file architecture understanding, and reference `patterns.json` for log parsing conventions.
