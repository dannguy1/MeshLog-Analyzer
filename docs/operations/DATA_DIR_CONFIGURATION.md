# DATA_DIR Configuration & Project Management Guide

## 🚨 **CRITICAL: Data Directory Fundamentals**

The prplOS LCM Log Analysis System uses a **single, centralized data directory strategy** to prevent data loss and corruption. Understanding this architecture is essential for system reliability.

### ⚡ **Core Principle: Absolute Path Strategy**

```bash
# ✅ ALWAYS USE ABSOLUTE PATHS
DATA_DIR=/data/WNC/LCM-Logs-Data
DATABASE_URL=sqlite:////data/WNC/LCM-Logs-Data/prplos_analysis.db

# ❌ NEVER USE RELATIVE PATHS
DATA_DIR=./data
DATABASE_URL=sqlite:///./data/prplos_analysis.db
```

### 🗂️ **Directory Structure**

```
/data/WNC/LCM-Logs-Data/           ← DATA_DIR (configurable via .env)
├── projects.json                   ← Project registry (CRITICAL FILE - source of truth)
├── projects.json.backup            ← Automatic backup (created before writes)
├── projects.json.tmp               ← Temporary file (during atomic writes)
├── prplos_analysis.db             ← SQLite database (if used)
├── logs/                          ← Application logs (auto-created in DATA_DIR)
│   ├── app.log
│   └── backend.log
├── uploads/                       ← Original uploaded packages (UPLOAD_DIR setting)
│   ├── package1.tar.gz
│   └── package2.tar.gz
├── projects/                      ← Per-project data directories
│   ├── {project-uuid-1}/
│   │   ├── extracted/             ← Extracted package contents
│   │   │   ├── metadata/          ← Extraction metadata
│   │   │   │   ├── package_structure.json
│   │   │   │   └── application_discovery.json
│   │   │   └── {package-contents} ← Extracted log files
│   │   └── analysis/              ← Project-specific analysis results
│   │       └── {analysis-uuid}/
│   └── {project-uuid-2}/
├── analysis/                      ← Global analysis results (ANALYSIS_DIR setting)
├── temp/                          ← Temporary processing files (TEMP_DIR setting)
└── backups/                       ← Scheduled backups (BACKUP_DIR setting, if used)
```

**Key Points**:
- **`projects.json`**: Located directly in DATA_DIR, not in a subdirectory
- **Backup files**: Created as `{filename}.backup` in the same directory as the original file
- **Subdirectories**: `UPLOAD_DIR`, `ANALYSIS_DIR`, `TEMP_DIR`, `BACKUP_DIR` are relative to DATA_DIR (defaults: "uploads", "analysis", "temp", "backups")
- **Project paths**: Stored in `project_root_path` field, automatically normalized on load for cross-machine compatibility

## 🛡️ **Data Protection Mechanisms**

### **1. Race Condition Protection**

The system now includes defensive mechanisms to prevent `projects.json` corruption:

```python
def save_data(allow_empty=False):
    """Save with race condition protection"""
    # DEFENSIVE CHECK: Don't save empty data unless intentional
    if len(projects_data) == 0 and not allow_empty and os.path.exists(PROJECTS_FILE):
        # Check if existing file has data
        try:
            with open(PROJECTS_FILE, 'r') as f:
                existing_data = json.load(f)
            if len(existing_data) > 0:
                logger.warning("🛡️ DEFENSIVE SAVE PROTECTION ACTIVATED")
                return  # Prevents corruption!
        except (json.JSONDecodeError, FileNotFoundError):
            pass  # Allow save if file is corrupted/missing
```

### **2. Atomic File Operations with File System Synchronization**

All critical file operations use atomic writes with explicit file system synchronization for cross-machine consistency:

**Process**:
1. Create `.backup` of existing file (if it exists)
2. Write to `.tmp` file with explicit flushing (`f.flush()`)
3. Force OS sync to disk (`os.fsync()`)
4. Verify file exists and is not empty
5. Sync parent directory metadata
6. Atomic rename (`.tmp` → original)
7. Final sync to ensure rename is visible

**Key Features**:
- ✅ **Explicit flushing**: Python buffers → OS buffers
- ✅ **File system sync**: OS buffers → disk (critical for NFS/network mounts)
- ✅ **Directory metadata sync**: Ensures rename is immediately visible
- ✅ **Graceful degradation**: Handles filesystems that don't support fsync
- ✅ **File validation**: Verifies file before rename to prevent empty/corrupt writes

This ensures data is immediately visible to all readers across different machines accessing the same backend.

### **3. Data Consistency Validation**

The system validates consistency between in-memory cache and disk storage:

```python
def validate_data_consistency():
    """Validate projects_db matches projects.json"""
    # Compare in-memory vs file storage
    # Detect discrepancies
    # Log warnings for investigation
    # Attempt recovery if inconsistencies found
```

### **4. Cross-Machine Path Normalization**

Paths are automatically normalized on load to handle different DATA_DIR configurations across machines:

**Automatic Normalization**:
- When `projects.json` is loaded, stored `project_root_path` values are checked
- If stored path doesn't match current DATA_DIR and doesn't exist, it's normalized to current DATA_DIR
- Related paths (`extraction_path`, `extraction_metadata_path`) are rebuilt relative to normalized project root
- Normalized paths are saved back to `projects.json` automatically

**Benefits**:
- ✅ Projects created on one machine work on another machine with different DATA_DIR
- ✅ Supports both shared storage (NFS) and local storage scenarios
- ✅ No manual migration needed when moving between environments

## ⚙️ **Configuration Management**

### **Single Source of Truth: `.env` File**

All configuration is managed through the `.env` file using Pydantic Settings:

```bash
# Copy the template
cp env.config .env

# Edit your settings
nano .env
```

**Configuration System**:
- Uses `pydantic_settings.BaseSettings` for environment variable management
- Automatically loads from `.env` file
- Environment variables override `.env` file values
- Default values provided for all settings

### **Critical Settings**

```bash
# Primary data directory - ALL data is stored under this path
# Use absolute paths for production deployments
DATA_DIR=/data/WNC/LCM-Logs-Data

# Subdirectories (relative to DATA_DIR)
UPLOAD_DIR=uploads
ANALYSIS_DIR=analysis
TEMP_DIR=temp
BACKUP_DIR=backups

# Database with absolute path (SQLite)
DATABASE_URL=sqlite:////data/WNC/LCM-Logs-Data/prplos_analysis.db

# File upload limits
MAX_FILE_SIZE=1073741824  # 1GB (1073741824 bytes)
```

**Note**: The default `DATABASE_URL` uses an absolute path. For SQLite, ensure the path uses `///` (three slashes) for absolute paths on Unix systems.

### **Environment-Specific Configurations**

#### **Development**
```bash
DATA_DIR=/home/user/dev/mesh-log-data
DEBUG=true
LOG_LEVEL=DEBUG
```

#### **Production**
```bash
DATA_DIR=/var/lib/prplos/data
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@db:5432/prplos
# Or for SQLite with absolute path:
# DATABASE_URL=sqlite:////var/lib/prplos/data/prplos_analysis.db
```

#### **Docker/Container**
```bash
DATA_DIR=/app/data
DATABASE_URL=sqlite:////app/data/prplos_analysis.db  # Note: three slashes for absolute path
REDIS_URL=redis://redis:6379/0
# Volume mount: /host/data:/app/data
```

**Important**: When using Docker volumes, ensure the mounted directory path matches your DATA_DIR configuration.

## 🔧 **Deployment Examples**

### **Local Development**
```bash
# 1. Setup data directory
sudo mkdir -p /data/WNC/LCM-Logs-Data
sudo chown $USER:$USER /data/WNC/LCM-Logs-Data

# 2. Configure environment
cp env.config .env
# Edit .env with your paths

# 3. Start backend
./scripts/backend-start.sh
```

### **Production Server**
```bash
# 1. Create production data directory
sudo mkdir -p /var/lib/prplos/data
sudo chown prplos:prplos /var/lib/prplos/data

# 2. Production configuration
cat > .env << EOF
DATA_DIR=/var/lib/prplos/data
DATABASE_URL=postgresql://prplos_user:secure_pass@localhost:5432/prplos_db
DEBUG=false
ENVIRONMENT=production
EOF

# 3. Start with production settings
./scripts/backend-start.sh
```

### **Docker Deployment**
```bash
# docker-compose.yml configuration
services:
  app:
    volumes:
      - /host/prplos/data:/app/data
    environment:
      - DATA_DIR=/app/data
      - DATABASE_URL=sqlite:///app/data/prplos_analysis.db
```

## 🚨 **Common Issues & Solutions**

### **Issue: Empty `projects.json` File**

**Symptoms:**
- File contains only `{}`
- All projects disappear from UI
- Logs show "Loaded 0 projects"

**Root Cause:**
- Race condition during FastAPI auto-reload
- `save_data()` called when `projects_db` is empty (before data loaded)

**Solution:**
- **Defensive protection**: `save_data()` now checks if existing file has data before saving empty dict
- **Manual recovery**: Restore from backup:
  ```bash
  cp /data/WNC/LCM-Logs-Data/projects.json.backup /data/WNC/LCM-Logs-Data/projects.json
  ```
- **Automatic backup**: Created before every write operation

### **Issue: Permission Denied Errors**

**Symptoms:**
- Cannot create directories
- Cannot write files
- Upload failures

**Solution:**
```bash
# Fix ownership
sudo chown -R $USER:$USER /data/WNC/LCM-Logs-Data

# Fix permissions
chmod -R 755 /data/WNC/LCM-Logs-Data
```

### **Issue: Working Directory Confusion**

**Symptoms:**
- Data saved in wrong location
- Cannot find project files
- Relative path failures

**Solution:**
- Always use absolute paths in `.env` file
- Never rely on working directory
- Verify configuration: Check actual DATA_DIR value in code, not just environment variable
- Use `get_settings().DATA_DIR` in Python code, not environment variables directly

### **Issue: Cross-Machine Path Mismatch**

**Symptoms:**
- Projects created on Machine A not accessible on Machine B
- Path errors when accessing project data
- Different DATA_DIR configurations across machines

**Solution:**
- **Automatic normalization**: System automatically normalizes paths on load
- **Shared storage**: If using NFS/shared storage, ensure consistent mount points
- **Path storage**: Project paths stored in `project_root_path` field, normalized automatically
- **Diagnostic tool**: Use `scripts/diagnose_project_paths.py` to check for path issues

## 🔄 **Migration Guide**

### **From Environment Variables to .env**

The system uses Pydantic Settings, which loads from `.env` file automatically. Environment variables can still override `.env` values if needed.

```bash
# 1. Stop backend
./scripts/backend-stop.sh

# 2. Create .env file
cp env.config .env

# 3. Move settings from bashrc/profile to .env
# OLD: export DATA_DIR="/custom/path"
# NEW: DATA_DIR=/custom/path  (in .env file, no quotes needed)

# 4. Remove from bashrc/profile (optional, env vars still work as override)
sed -i '/DATA_DIR/d' ~/.bashrc
sed -i '/DATABASE_URL/d' ~/.bashrc

# 5. Start backend
./scripts/backend-start.sh
```

**Note**: Environment variables take precedence over `.env` file, so you can use either method or both (with env vars as overrides).

### **From Relative to Absolute Paths**

```bash
# 1. Identify current data location
ls -la ./data/

# 2. Move to absolute location
sudo mkdir -p /data/WNC/LCM-Logs-Data
sudo mv ./data/* /data/WNC/LCM-Logs-Data/
sudo chown -R $USER:$USER /data/WNC/LCM-Logs-Data

# 3. Update .env
DATA_DIR=/data/WNC/LCM-Logs-Data
DATABASE_URL=sqlite:////data/WNC/LCM-Logs-Data/prplos_analysis.db

# 4. Restart system
./scripts/backend-restart.sh
```

## ✅ **Best Practices**

### **Configuration**
- ✅ **Single .env file**: All settings in one place
- ✅ **Absolute paths**: Predictable, deployment-safe
- ✅ **Environment separation**: Different .env for dev/staging/prod
- ✅ **Version control**: Template in `env.config`, actual in `.env`

### **Data Management**
- ✅ **Centralized storage**: Everything under DATA_DIR
- ✅ **Atomic operations**: Prevent partial writes with file system synchronization
- ✅ **Regular backups**: Automatic backup creation before every write
- ✅ **Validation checks**: Consistency monitoring between memory and disk
- ✅ **Path normalization**: Automatic cross-machine path handling
- ✅ **Disk as source of truth**: API endpoints read from disk for consistency

### **Deployment**
- ✅ **Pre-create directories**: Set proper permissions
- ✅ **Test configuration**: Validate paths before start
- ✅ **Monitor logs**: Watch for configuration issues
- ✅ **Backup strategy**: Regular data backups

## 🔍 **Troubleshooting Commands**

```bash
# Check current configuration in .env file
grep DATA_DIR .env

# Check actual DATA_DIR being used by backend (from Python)
python3 -c "from app.core.config import get_settings; print(get_settings().DATA_DIR)"

# Verify directory structure
ls -la /data/WNC/LCM-Logs-Data/

# Check file permissions
ls -la /data/WNC/LCM-Logs-Data/projects.json

# Validate projects file (count projects)
python3 -c "import json; data=json.load(open('/data/WNC/LCM-Logs-Data/projects.json')); print(f'Projects: {len(data)}')"

# Check for path normalization issues
python3 scripts/diagnose_project_paths.py

# Check backend logs
tail -f /data/WNC/LCM-Logs-Data/logs/app.log

# Test write permissions
touch /data/WNC/LCM-Logs-Data/test.txt && rm /data/WNC/LCM-Logs-Data/test.txt

# Verify backup file exists
ls -la /data/WNC/LCM-Logs-Data/projects.json.backup
```

## 📋 **Configuration Checklist**

- [ ] DATA_DIR uses absolute path
- [ ] Directory exists and is writable
- [ ] DATABASE_URL uses absolute path
- [ ] .env file contains all required settings
- [ ] No environment variables in bashrc
- [ ] Backup directory configured
- [ ] Log directory accessible
- [ ] File size limits appropriate
- [ ] Permissions correctly set
- [ ] Test configuration works
