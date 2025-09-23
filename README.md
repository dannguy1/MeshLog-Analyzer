# prplOS LCM Log Analysis System

A comprehensive log analysis platform for prplOS LCM applications with real-time monitoring, advanced analytics, intelligent filtering, and production-ready features.

## ✨ New Features (v3.0)

### 🎯 Advanced Analytics & Intelligence
- **Message Type Categorization**: Intelligent classification of log messages by content patterns
- **Statistical Analysis**: Time series analysis, trend detection, error pattern analysis
- **Performance Metrics**: Message length analysis, timeout detection, container health scoring
- **Correlation Analysis**: Cross-container and temporal correlation detection

### 🔍 Enhanced Filtering & Search
- **Time Sequence Filtering**: OR logic filtering with multiple message types
- **Pagination**: 25 items per page with total count and page navigation
- **Full-Text Search**: SQLite FTS5 integration for fast content search
- **Advanced Filtering**: Filter by log level, container, message type, time range

### 📊 Production-Ready Architecture
- **SQLite Integration**: Application-specific databases with indexed storage
- **Redis Communication**: Real-time status updates and background task coordination
- **Project Export/Import**: Complete project portability with metadata preservation
- **WebSocket Updates**: Real-time analysis progress and status broadcasting

### 🤖 Agent Services Integration
- **Remote Agent Analysis**: Integration with specialized analysis agents
- **Domain-Specific Analysis**: Separate analysis for steering, access control, and network applications
- **Real-Time Results**: Live monitoring of agent analysis progress
- **Unified Interface**: Seamless integration between local and agent analysis

### 🚀 Performance Improvements
- **100x+ Faster**: SQLite-based storage vs JSON parsing
- **Efficient Pagination**: Server-side pagination with total count
- **Background Processing**: Non-blocking analysis execution
- **Memory Optimization**: Reduced memory footprint and faster queries

## 🚀 Quick Installation

### Prerequisites

Make sure you have the following system dependencies installed:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv nodejs npm docker.io netcat redis-server
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip nodejs npm docker netcat redis
```

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Mesh-Log
   ```

2. **Run the complete installation script:**
   ```bash
   ./scripts/install_complete.sh
   ```

   This script will:
   - Check system dependencies
   - Set up Python virtual environment
   - Install all Python dependencies
   - Create SQLite database with schema
   - Install frontend dependencies
   - Test backend imports
   - Make all scripts executable

## 🛠️ Development Setup

### Manual Installation (if automatic fails)

1. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip setuptools wheel
   pip install -r requirements-minimal.txt
   pip install matplotlib seaborn
   ```

2. **Set up database:**
   ```bash
   mkdir -p data logs
   sqlite3 data/prplos_analysis.db < scripts/sqlite_schema_fixed.sql
   ```

3. **Set up frontend:**
   ```bash
   cd ui
   npm install
   cd ..
   ```

4. **Make scripts executable:**
   ```bash
   chmod +x scripts/*.sh
   ```

## 🚀 Running the Application

### Start Backend Only
```bash
./scripts/backend-start.sh
```

### Start Frontend Only
```bash
./scripts/frontend-start.sh
```

### Start Both Services
```bash
./scripts/dev-start.sh
```

### Stop All Services
```bash
./scripts/dev-stop.sh
```

### Check Status
```bash
./scripts/dev-status.sh
```

## 📊 Access URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs
- **Health Check:** http://localhost:8000/health
- **Agent Services:** http://localhost:8001 (if enabled)

## 🤖 Agent Services Configuration

The system supports integration with external agent services for specialized analysis:

### Configuration

1. **Copy environment template:**
   ```bash
   cp env.config .env
   ```

2. **Edit `.env` file and configure agent services:**
   ```bash
   # Agent Services Integration
   WNC_LOG_AGENTS_ENABLED=true
   WNC_LOG_AGENTS_URL=http://localhost:8001
   WNC_LOG_AGENTS_TIMEOUT=300
   AGENT_ANALYSIS_ENABLED=true
   AGENT_RESULT_CACHE_TTL=3600
   AGENT_DETECTION_CONFIDENCE_THRESHOLD=0.7
   AGENT_AUTO_TRIGGER=true
   AGENT_RESULT_FORMATS=["html", "json"]
   ```

3. **Start agent services** (if available):
   ```bash
   # Start your agent service on port 8001
   # The system will automatically detect and integrate
   ```

### Agent Analysis Features

- **Domain-Specific Analysis**: Each application gets specialized analysis
  - **wnc-steer**: Steering control analysis, trajectory optimization
  - **wnc-acs**: Access control analysis, security events
  - **otbr-agent**: Thread network analysis, mesh connectivity

- **Real-Time Monitoring**: Live progress updates during analysis
- **Result Integration**: Seamless display of agent results in the UI
- **Fallback Support**: Graceful degradation when agents are unavailable

## 🔧 Troubleshooting

### Backend Issues

**Missing dependencies:**
```bash
   ./scripts/install_complete.sh
```

**Database issues:**
```bash
rm -f data/prplos_analysis.db
sqlite3 data/prplos_analysis.db < scripts/sqlite_schema_fixed.sql
```

**Import errors:**
```bash
source venv/bin/activate
python -c "import app.main; print('Backend import successful')"
```

### Frontend Issues

**Missing dependencies:**
```bash
cd ui
npm install
cd ..
```

**Port conflicts:**
```bash
# Check what's using port 3000
lsof -i :3000
# Kill the process if needed
kill -9 <PID>
```

### Extraction Reuse Issues

**Storage bloat (old architecture):**
```bash
# Check current storage usage
du -sh data/extracted/

# Clean up old extractions
./scripts/cleanup --dry-run
./scripts/cleanup --backup
```

**Migration issues:**
```bash
# Test migration script
python3 scripts/migrate_extraction_reuse.py

# Test new implementation
python3 scripts/test_extraction_reuse.py
```

**Extraction validation errors:**
```bash
# Check extraction integrity
python3 -c "
from app.processors.package_processor import PackageProcessor
processor = PackageProcessor()
print('PackageProcessor loaded successfully')
"
```

**Metadata corruption:**
```bash
# Rebuild metadata
rm -rf data/projects/*/extracted/metadata
# Re-upload and process packages to regenerate metadata
```

### Cleanup Script Issues

**Permission denied:**
```bash
chmod +x scripts/cleanup*
```

**Python not found:**
```bash
# Use shell script instead
./scripts/cleanup shell
```

**Docker not available:**
```bash
# Skip container cleanup
./scripts/cleanup --no-containers
```

**Insufficient space:**
```bash
# Clean cache first
./scripts/cleanup --no-data --no-processes --no-containers
```

### Clean Installation

**Complete cleanup with enhanced scripts:**
```bash
# Option 1: Use wrapper script (recommended)
./scripts/cleanup --backup --dry-run

# Option 2: Clean with backup
./scripts/cleanup --backup

# Option 3: Use Python script directly
python3 scripts/cleanup_enhanced.py --backup

# Then reinstall
   ./scripts/install_complete.sh
```

## 🧹 Enhanced Cleanup Scripts

The system includes advanced cleanup scripts that support both the old timestamp-based extraction structure and the new project-based extraction reuse architecture.

### Available Cleanup Scripts

1. **Wrapper Script** (`scripts/cleanup`) - **Recommended**
   - Auto-detects best script to use
   - Unified interface for all cleanup operations
   - Supports all cleanup options

2. **Enhanced Shell Script** (`scripts/cleanup.sh`)
   - Improved with backup support and dry-run mode
   - Handles both old and new extraction structures
   - Production-ready with comprehensive logging

3. **Python Script** (`scripts/cleanup_enhanced.py`)
   - Advanced features with detailed reporting
   - Cross-platform support and better error handling
   - Detailed size reporting and progress tracking

### Cleanup Usage Examples

```bash
# Basic cleanup (recommended)
./scripts/cleanup

# Cleanup with backup
./scripts/cleanup --backup

# Dry run (see what would be cleaned)
./scripts/cleanup --dry-run

# Verbose output
./scripts/cleanup --verbose

# Selective cleanup
./scripts/cleanup --no-processes --no-containers

# Use specific script
./scripts/cleanup python --backup
./scripts/cleanup shell --dry-run
```

### What Gets Cleaned

**Data Directories:**
- Old structure: `data/extracted/extract_YYYYMMDD_HHMMSS/`
- New structure: `data/projects/{project_id}/extracted/`
- Database files: `projects.json`, `analyses.json`, `*.db`, `*.sqlite`

**Logs and Cache:**
- All log files in `logs/` directory
- Python cache: `__pycache__`, `*.pyc`, `*.pyo`
- Node.js cache: `node_modules/.cache`, `dist`, `.next`
- Temporary files: `*.tmp`, `*.temp`, `.DS_Store`

**Processes and Containers:**
- Processes: uvicorn, vite, npm
- Docker containers with project name

### Safety Features

- **Backup Support**: `--backup` creates timestamped backups
- **Dry Run**: `--dry-run` shows what would be cleaned without making changes
- **Confirmation**: Interactive prompts before cleanup
- **Selective Cleanup**: Skip specific steps if needed
- **Error Handling**: Graceful error handling with detailed messages

## 🏗️ Extraction Reuse Architecture

The system implements a **"extract once, analyze many times"** architecture to eliminate storage bloat and improve performance.

### Key Benefits

- **90% storage reduction** (from 26+ extractions to 1 per project)
- **Faster analysis startup** (no re-extraction needed)
- **Consistent results** across multiple analyses
- **Better organization** with project-based structure

### File System Organization

```
data/
├── projects/
│   ├── {project_id}/
│   │   ├── extracted/                    # Single extraction per project
│   │   │   ├── {extracted_contents}
│   │   │   └── metadata/
│   │   │       ├── package_structure.json
│   │   │       ├── application_discovery.json
│   │   │       └── extraction_info.json
│   │   └── analysis/
│   │       └── {analysis_results}
└── extracted/                            # Legacy extractions (can be cleaned up)
    └── extract_YYYYMMDD_HHMMSS/
```

### Migration Support

The system includes migration tools to convert existing timestamp-based extractions to the new project-based structure:

```bash
# Run migration script
python3 scripts/migrate_extraction_reuse.py

# Test the new implementation
python3 scripts/test_extraction_reuse.py
```

## 📁 Project Structure

```
Mesh-Log/
├── app/                    # Backend application
│   ├── main.py            # FastAPI application
│   ├── core/              # Configuration and core modules
│   ├── models/            # Data models (with extraction reuse support)
│   ├── api/               # API endpoints
│   ├── analytics/         # Analysis engines
│   ├── visualization/     # Chart generation
│   └── processors/        # Data processors (with extraction reuse)
├── ui/                    # Frontend React application
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   ├── Dockerfile         # Frontend Docker image
│   ├── nginx.conf         # Nginx configuration
│   └── build-production.sh # Production build script
├── scripts/               # Utility scripts
│   ├── backend-start.sh   # Start backend
│   ├── frontend-start.sh  # Start frontend
│   ├── cleanup            # Enhanced cleanup wrapper
│   ├── cleanup.sh         # Enhanced shell cleanup
│   ├── cleanup_enhanced.py # Python cleanup script
│   ├── migrate_extraction_reuse.py # Migration script
│   └── test_extraction_reuse.py # Test script
├── data/                  # Data storage
│   ├── projects/          # Project-based extractions (new)
│   └── extracted/         # Legacy extractions (old)
├── logs/                  # Application logs
├── docs/                  # Documentation
│   ├── extraction_reuse_implementation.md
│   ├── extraction_reuse_summary.md
│   └── cleanup_deployment_guide.md
├── requirements-minimal.txt # Python dependencies
├── requirements.txt      # Full Python dependencies
├── docker-compose.yml     # Base Docker Compose configuration
├── docker-compose.prod.yml # Production Docker Compose overrides
├── Dockerfile            # Backend Docker image
├── Dockerfile.backend    # Alternative backend Docker image
├── deploy.sh             # Production deployment script
├── health-check.sh       # System health monitoring script
├── env.production        # Production environment configuration
├── .dockerignore         # Docker build optimization
├── DEPLOYMENT.md         # Comprehensive deployment guide
└── README.md             # This file
```

## 🐛 Debug Scripts

### Backend Debug
```bash
./scripts/backend-debug.sh
```

### Database Check
```bash
source venv/bin/activate
sqlite3 data/prplos_analysis.db ".tables"
```

### Process Check
```bash
ps aux | grep uvicorn
ps aux | grep vite
```

## 📝 Log Files

- **Backend logs:** `logs/backend.log`
- **Frontend logs:** `logs/frontend.log`
- **Application logs:** `logs/app.log`

## 🔄 Development Workflow

1. **Start development:**
   ```bash
   ./scripts/dev-start.sh
   ```

2. **Make changes to code**

3. **Test changes:**
   - Backend auto-reloads with `--reload` flag
   - Frontend auto-reloads with Vite HMR

4. **Stop development:**
   ```bash
   ./scripts/dev-stop.sh
   ```

## 🚀 Production Deployment

### Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Node.js** 18+ (for frontend development)
- **Python** 3.11+ (for backend development)
- **Git** (for version control)

### Quick Deployment

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd Mesh-Log
   
   # Make deployment scripts executable
   chmod +x deploy.sh
   chmod +x ui/build-production.sh
   ```

2. **Deploy the entire system:**
   ```bash
   ./deploy.sh deploy
   ```

3. **Verify deployment:**
   ```bash
   ./deploy.sh status
   ./deploy.sh health
   ```

### Docker Services

The deployment includes the following services:

| Service | Port | Description |
|---------|------|-------------|
| `frontend` | 80 | React frontend with Nginx |
| `backend` | 8000 | FastAPI backend |
| `redis` | 6379 | Redis cache and message broker |
| `celery_worker` | - | Background task processor |
| `celery_beat` | - | Scheduled task scheduler |

### Access Points

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Deployment Commands

```bash
# Deploy the application
./deploy.sh deploy

# Stop all services
./deploy.sh stop

# Restart services
./deploy.sh restart

# View logs
./deploy.sh logs

# Check status
./deploy.sh status

# Check health
./deploy.sh health

# Clean up containers and images
./deploy.sh cleanup
```

### Configuration

Create a `.env` file or use the provided `env.production`:

```bash
# Copy production environment template
cp env.production .env

# Edit configuration
nano .env
```

Key configuration options:
```bash
# Data Directory
DATA_DIR=/data/WNC/LCM-Logs-Data

# Database
DATABASE_URL=sqlite:///./data/prplos_analysis.db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production

# File Upload
MAX_FILE_SIZE_MB=100
```

### Scaling

```bash
# Scale Celery workers
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale celery_worker=5

# Scale backend (with load balancer)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3
```

### Monitoring and Troubleshooting

```bash
# Check individual services
curl http://localhost/health          # Frontend
curl http://localhost:8000/health     # Backend
docker compose exec redis redis-cli ping  # Redis

# View logs
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery_worker

# System health check
./health-check.sh
```

### Security Considerations

- [ ] Change default `SECRET_KEY`
- [ ] Use HTTPS in production (configure reverse proxy)
- [ ] Set up proper firewall rules
- [ ] Regular security updates
- [ ] Backup data regularly
- [ ] Monitor logs for suspicious activity

### Updates and Maintenance

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/ uploads/ analysis_results/

# Restore data
tar -xzf backup-20240101.tar.gz
```

For detailed deployment information, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 🚀 Development Scenarios

### Development Environment
```bash
# Quick cleanup for development
./scripts/cleanup --no-containers

# Start fresh
./scripts/dev-start.sh
```

### Staging Environment
```bash
# Cleanup with backup for staging
./scripts/cleanup --backup --verbose

# Verify cleanup
./scripts/cleanup --dry-run

# Start services
./scripts/dev-start.sh
```

### CI/CD Pipeline
```bash
# Automated cleanup in CI/CD
./scripts/cleanup --no-processes --no-containers --dry-run

# If dry run passes, run actual cleanup
./scripts/cleanup --no-processes --no-containers
```

## 📋 Best Practices

### Before Cleanup
1. **Create Backup**: Always use `--backup` in production
2. **Test First**: Use `--dry-run` to verify what will be cleaned
3. **Stop Services**: Ensure all services are stopped
4. **Check Dependencies**: Verify all required tools are available

### During Cleanup
1. **Monitor Output**: Watch for errors or warnings
2. **Verify Steps**: Confirm each cleanup step completes successfully
3. **Check Status**: Review final status report

### After Cleanup
1. **Verify Cleanup**: Check that directories are empty
2. **Test Startup**: Verify system starts correctly
3. **Restore if Needed**: Use backup if issues arise

### Storage Management
- **Regular Cleanup**: Run cleanup scripts regularly to prevent storage bloat
- **Monitor Usage**: Keep track of storage usage with `--verbose` output
- **Archive Old Data**: Consider archiving old projects before cleanup
- **Backup Strategy**: Maintain regular backups of important data

## 📚 API Documentation

### Core Endpoints

#### Application Data Management
```
GET /api/v1/projects/{project_id}/applications/{app_name}/data/logs
- Advanced filtering with OR logic for message types
- Pagination with total count and page metadata
- Full-text search capabilities

GET /api/v1/projects/{project_id}/applications/{app_name}/data/message-types
- Dynamic filter generation for UI
- Message type counts and categorization

GET /api/v1/projects/{project_id}/applications/{app_name}/data/statistics
- Time series analysis and trend detection
- Performance metrics and error pattern analysis
```

#### Project Management
```
GET /api/v1/projects/{project_id}/export
- Complete project metadata and data summary
- Export/import functionality for project portability

POST /api/v1/projects/import
- Import projects with full metadata preservation
```

#### Real-Time Communication
```
WS /ws/analysis/{analysis_id}
- Real-time analysis progress updates
- Redis Pub/Sub integration for live status
```

### Interactive Documentation
Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
