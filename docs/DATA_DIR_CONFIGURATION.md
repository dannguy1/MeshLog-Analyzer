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
/data/WNC/LCM-Logs-Data/           ← DATA_DIR (configurable)
├── projects.json                   ← Project registry (CRITICAL FILE)
├── prplos_analysis.db             ← SQLite database
├── logs/                          ← Application logs
│   ├── app.log
│   └── backend.log
├── uploads/                       ← Original uploaded packages
│   ├── package1.tar.gz
│   └── package2.tar.gz
├── projects/                      ← Per-project data
│   ├── {project-uuid-1}/
│   │   ├── extracted/             ← Extracted package contents
│   │   │   ├── metadata/          ← Extraction metadata
│   │   │   │   ├── package_structure.json
│   │   │   │   └── application_discovery.json
│   │   │   └── {package-contents}
│   │   └── analysis/              ← Project-specific analyses
│   └── {project-uuid-2}/
├── analysis/                      ← Global analysis results
├── temp/                          ← Temporary processing files
├── backups/                       ← Automatic backups
│   ├── projects.json.backup
│   └── prplos_analysis.db.backup
└── uploads/                       ← Uploaded packages
```

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

### **2. Atomic File Operations**

All critical file operations use atomic writes:
- Write to `.tmp` file first
- Create `.backup` of existing file
- Atomic rename on success
- Cleanup on failure

### **3. Data Consistency Validation**

```python
def validate_data_consistency():
    """Validate projects_db matches projects.json"""
    # Compare in-memory vs file storage
    # Detect discrepancies
    # Log warnings for investigation
```

## ⚙️ **Configuration Management**

### **Single Source of Truth: `.env`**

All configuration is managed through the `.env` file:

```bash
# Copy the template
cp env.config .env

# Edit your settings
nano .env
```

### **Critical Settings**

```bash
# Primary data directory - ALL data is stored under this path
DATA_DIR=/data/WNC/LCM-Logs-Data

# Database with absolute path
DATABASE_URL=sqlite:////data/WNC/LCM-Logs-Data/prplos_analysis.db

# File upload limits
MAX_FILE_SIZE=1073741824  # 1GB
```

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
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@db:5432/prplos
```

#### **Docker/Container**
```bash
DATA_DIR=/app/data
DATABASE_URL=sqlite:///app/data/prplos_analysis.db
REDIS_URL=redis://redis:6379/0
```

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
- `save_data()` called when `projects_db` is empty

**Solution:**
- Defensive protection now prevents this
- Manual recovery: `cp projects.json.backup projects.json`

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
- Always use absolute paths in `.env`
- Never rely on working directory
- Verify paths: `echo $DATA_DIR`

## 🔄 **Migration Guide**

### **From Environment Variables to .env**

```bash
# 1. Stop backend
./scripts/backend-stop.sh

# 2. Create .env file
cp env.config .env

# 3. Move settings from bashrc to .env
# OLD: export DATA_DIR="/custom/path"
# NEW: DATA_DIR=/custom/path  (in .env file)

# 4. Remove from bashrc
sed -i '/DATA_DIR/d' ~/.bashrc
sed -i '/DATABASE_URL/d' ~/.bashrc

# 5. Start backend
./scripts/backend-start.sh
```

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
- ✅ **Atomic operations**: Prevent partial writes
- ✅ **Regular backups**: Automatic backup creation
- ✅ **Validation checks**: Consistency monitoring

### **Deployment**
- ✅ **Pre-create directories**: Set proper permissions
- ✅ **Test configuration**: Validate paths before start
- ✅ **Monitor logs**: Watch for configuration issues
- ✅ **Backup strategy**: Regular data backups

## 🔍 **Troubleshooting Commands**

```bash
# Check current configuration
grep DATA_DIR .env

# Verify directory structure
ls -la /data/WNC/LCM-Logs-Data/

# Check file permissions
ls -la /data/WNC/LCM-Logs-Data/projects.json

# Validate projects file
python3 -c "import json; print(len(json.load(open('/data/WNC/LCM-Logs-Data/projects.json'))))"

# Check backend logs
tail -f /data/WNC/LCM-Logs-Data/logs/app.log

# Test write permissions
touch /data/WNC/LCM-Logs-Data/test.txt && rm /data/WNC/LCM-Logs-Data/test.txt
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
