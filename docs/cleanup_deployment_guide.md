# Production Deployment Guide - prplOS LCM Log Analysis System v3.0

**Date**: 2025-01-09  
**Version**: 3.0  
**Status**: Production Ready with Advanced Features  

## Production Deployment Requirements

### System Dependencies

#### Required Services
- **Python 3.8+**: Backend application runtime
- **Node.js 16+**: Frontend build and development
- **Redis Server**: Real-time communication and caching
- **SQLite 3**: Application-specific data storage
- **Docker**: Container management (optional)

#### Installation Commands
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv nodejs npm redis-server sqlite3 docker.io

# CentOS/RHEL
sudo yum install python3 python3-pip nodejs npm redis sqlite docker

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Environment Configuration

#### Required Environment Variables
```bash
# Data directory (absolute path)
DATA_DIR=/opt/prplos-analysis/data

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Database configuration
DATABASE_URL=sqlite:///opt/prplos-analysis/data/prplos_analysis.db

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=/opt/prplos-analysis/logs/app.log

# Security (production)
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost
```

### Service Configuration

#### Systemd Service Files

**Backend Service** (`/etc/systemd/system/prplos-backend.service`):
```ini
[Unit]
Description=prplOS LCM Log Analysis Backend
After=network.target redis.service

[Service]
Type=simple
User=prplos
Group=prplos
WorkingDirectory=/opt/prplos-analysis
Environment=PATH=/opt/prplos-analysis/venv/bin
ExecStart=/opt/prplos-analysis/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Security Configuration

#### Firewall Rules
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to backend
sudo ufw deny 8000/tcp
sudo ufw deny 3000/tcp
```

### Database Management

#### SQLite Database Setup
```bash
# Create application databases
mkdir -p /opt/prplos-analysis/data/projects
sqlite3 /opt/prplos-analysis/data/prplos_analysis.db < scripts/sqlite_schema_fixed.sql

# Set permissions
chown -R prplos:prplos /opt/prplos-analysis/data
chmod -R 755 /opt/prplos-analysis/data
```

---

## Enhanced Cleanup Scripts

## Available Scripts

### 1. Enhanced Shell Script (`cleanup.sh`)
- **Location**: `scripts/cleanup.sh`
- **Features**: Command-line options, backup support, dry-run mode
- **Dependencies**: bash, docker, standard Unix tools

### 2. Python Script (`cleanup_enhanced.py`)
- **Location**: `scripts/cleanup_enhanced.py`
- **Features**: Advanced logging, detailed reporting, cross-platform support
- **Dependencies**: Python 3.6+

### 3. Wrapper Script (`cleanup`)
- **Location**: `scripts/cleanup`
- **Features**: Auto-detection, script selection, unified interface
- **Dependencies**: bash, python3 (optional)

## Usage Examples

### Basic Cleanup
```bash
# Use wrapper script (auto-detects best script)
./scripts/cleanup

# Use specific script
./scripts/cleanup shell
./scripts/cleanup python
```

### Cleanup with Backup
```bash
# Create backup before cleanup
./scripts/cleanup --backup

# Or using environment variable
CREATE_BACKUP=true ./scripts/cleanup
```

### Dry Run (See What Would Be Cleaned)
```bash
# See what would be cleaned without actually cleaning
./scripts/cleanup --dry-run
```

### Selective Cleanup
```bash
# Skip certain cleanup steps
./scripts/cleanup --no-processes --no-containers
./scripts/cleanup --no-data --no-cache
```

### Verbose Output
```bash
# Get detailed output
./scripts/cleanup --verbose
```

## What Gets Cleaned

### Data Directories
- **Old Structure**: `data/extracted/extract_YYYYMMDD_HHMMSS/`
- **New Structure**: `data/projects/{project_id}/extracted/`
- **Database Files**: `projects.json`, `analyses.json`, `*.db`, `*.sqlite`
- **Analysis Results**: All analysis output files

### Logs and Cache
- **Log Files**: All files in `logs/` directory
- **Python Cache**: `__pycache__`, `*.pyc`, `*.pyo`
- **Node.js Cache**: `node_modules/.cache`, `dist`, `.next`
- **Temporary Files**: `*.tmp`, `*.temp`, `.DS_Store`

### Processes and Containers
- **Processes**: uvicorn, vite, npm
- **Containers**: Docker containers with project name

## Backup Features

### Automatic Backup
```bash
# Create timestamped backup
./scripts/cleanup --backup
```

### Backup Contents
- Complete `data/` directory
- Complete `logs/` directory
- Configuration files (`.env`, `projects.json`, `analyses.json`)

### Backup Location
```
backups/cleanup_YYYYMMDD_HHMMSS/
├── data/
├── logs/
├── projects.json
├── analyses.json
└── .env
```

## Deployment Scenarios

### 1. Development Environment
```bash
# Quick cleanup for development
./scripts/cleanup --no-containers
```

### 2. Staging Environment
```bash
# Cleanup with backup for staging
./scripts/cleanup --backup --verbose
```

### 3. Production Environment
```bash
# Full cleanup with backup for production
CREATE_BACKUP=true ./scripts/cleanup python --verbose
```

### 4. CI/CD Pipeline
```bash
# Automated cleanup in CI/CD
./scripts/cleanup --no-processes --no-containers --dry-run
```

## Safety Features

### Confirmation Prompts
- Interactive confirmation before cleanup (unless dry-run)
- Clear warnings about data loss

### Dry Run Mode
- Shows exactly what would be cleaned
- No actual changes made
- Perfect for testing and validation

### Backup Integration
- Automatic backup creation
- Timestamped backup directories
- Complete data preservation

### Error Handling
- Graceful error handling
- Detailed error messages
- Non-destructive failure modes

## Monitoring and Logging

### Log Levels
- **INFO**: General information
- **SUCCESS**: Successful operations
- **WARNING**: Potential issues
- **ERROR**: Critical errors

### Output Format
```
2025-01-27 10:30:15 - INFO - Starting cleanup process
2025-01-27 10:30:16 - INFO - ✅ Data directories cleaned
2025-01-27 10:30:17 - INFO - ✅ Cleanup completed successfully!
```

### Status Reporting
- Process status check
- Container status check
- Directory status check
- Next steps guidance

## Integration with Extraction Reuse Architecture

### Old Structure Cleanup
- Removes timestamp-based extractions (`extract_YYYYMMDD_HHMMSS/`)
- Preserves project metadata
- Cleans up legacy analysis results

### New Structure Support
- Handles project-based extractions (`data/projects/{project_id}/extracted/`)
- Preserves metadata directories
- Maintains extraction reuse functionality

### Migration Support
- Works with both old and new structures
- Supports migration from old to new architecture
- Maintains data integrity during transition

## Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Fix permissions
chmod +x scripts/cleanup*
```

#### Python Not Found
```bash
# Use shell script instead
./scripts/cleanup shell
```

#### Docker Not Available
```bash
# Skip container cleanup
./scripts/cleanup --no-containers
```

#### Insufficient Space
```bash
# Clean cache first
./scripts/cleanup --no-data --no-processes --no-containers
```

### Debug Mode
```bash
# Enable verbose logging
./scripts/cleanup --verbose
```

### Manual Cleanup
```bash
# Manual step-by-step cleanup
./scripts/cleanup --no-processes
./scripts/cleanup --no-containers
./scripts/cleanup --no-data
./scripts/cleanup --no-cache
```

## Best Practices

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

## Performance Considerations

### Storage Savings
- **Old Structure**: 26+ extraction directories per project
- **New Structure**: 1 extraction directory per project
- **Savings**: 90%+ reduction in storage requirements

### Time Savings
- **Extraction Reuse**: No re-extraction needed
- **Faster Analysis**: Direct access to existing data
- **Reduced I/O**: Less disk operations

### Memory Usage
- **Efficient Cleanup**: Minimal memory footprint
- **Streaming Operations**: Large file handling
- **Garbage Collection**: Automatic cleanup

## Security Considerations

### Data Protection
- **Backup Encryption**: Consider encrypting backups
- **Access Control**: Restrict cleanup script access
- **Audit Logging**: Log all cleanup operations

### Process Security
- **User Permissions**: Run with appropriate privileges
- **Process Isolation**: Isolate cleanup processes
- **Error Handling**: Prevent data corruption

## Future Enhancements

### Planned Features
- **Cloud Backup**: Support for cloud storage backups
- **Incremental Cleanup**: Only clean changed files
- **Scheduled Cleanup**: Automated cleanup scheduling
- **Metrics Collection**: Cleanup performance metrics

### Integration Points
- **Monitoring Systems**: Integration with monitoring tools
- **CI/CD Pipelines**: Enhanced CI/CD integration
- **Container Orchestration**: Kubernetes/Docker Swarm support
- **Cloud Platforms**: AWS/Azure/GCP integration

## Conclusion

The enhanced cleanup scripts provide a robust, production-ready solution for managing the prplOS LCM Log Analysis System. With support for both old and new extraction architectures, comprehensive backup features, and extensive safety measures, these scripts ensure reliable system maintenance while preserving data integrity.

The scripts are designed for deployment in various environments, from development to production, with appropriate safety measures and monitoring capabilities for each scenario.
