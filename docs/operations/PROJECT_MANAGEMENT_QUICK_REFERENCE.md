# Project Management Quick Reference

## 🚨 **Emergency Procedures**

### **Empty `projects.json` Recovery**
```bash
# 1. Stop backend immediately
./scripts/backend-stop.sh

# 2. Check if backup exists
ls -la /data/WNC/LCM-Logs-Data/projects.json*

# 3. Restore from backup
cp /data/WNC/LCM-Logs-Data/projects.json.backup /data/WNC/LCM-Logs-Data/projects.json

# 4. Verify recovery
python3 -c "import json; print(f'Recovered {len(json.load(open(\"/data/WNC/LCM-Logs-Data/projects.json\")))} projects')"

# 5. Start backend
./scripts/backend-start.sh
```

### **Race Condition Protection Triggered**
**Log Message**: `🛡️ DEFENSIVE SAVE PROTECTION ACTIVATED`

**Action**: This is NORMAL - the system prevented data loss!
- No action needed
- Protection is working correctly
- Check logs for root cause

## 🔍 **Diagnostic Commands**

### **Check System Health**
```bash
# Configuration
grep DATA_DIR .env

# Directory structure
ls -la /data/WNC/LCM-Logs-Data/

# Projects file
python3 -c "import json; data=json.load(open('/data/WNC/LCM-Logs-Data/projects.json')); print(f'Projects: {len(data)}')"

# Permissions
ls -la /data/WNC/LCM-Logs-Data/projects.json

# Disk space
df -h /data/WNC/LCM-Logs-Data/

# Backend status
./scripts/backend-status.sh
```

### **Data Consistency Check**
```bash
# Quick check
curl -s http://localhost:8000/api/v1/projects | jq '.projects | length'

# Detailed validation
tail -f /data/WNC/LCM-Logs-Data/logs/app.log | grep -i "consistency"
```

## 🛠️ **Common Fixes**

### **Permission Issues**
```bash
sudo chown -R $USER:$USER /data/WNC/LCM-Logs-Data
chmod -R 755 /data/WNC/LCM-Logs-Data
```

### **Corrupted Projects File**
```bash
# Test if file is valid JSON
python3 -c "import json; json.load(open('/data/WNC/LCM-Logs-Data/projects.json'))" && echo "Valid" || echo "Corrupted"

# If corrupted, restore from backup
cp /data/WNC/LCM-Logs-Data/projects.json.backup /data/WNC/LCM-Logs-Data/projects.json
```

### **Missing Project Directories**
```bash
# Recover orphaned projects
curl -X POST http://localhost:8000/api/v1/admin/recover-projects
```

## 📋 **Daily Checklist**

- [ ] Check backend status: `./scripts/backend-status.sh`
- [ ] Verify project count matches: `curl -s http://localhost:8000/api/v1/projects | jq '.projects | length'`
- [ ] Check logs for errors: `tail -n 50 /data/WNC/LCM-Logs-Data/logs/app.log | grep -i error`
- [ ] Verify disk space: `df -h /data/WNC/LCM-Logs-Data/`
- [ ] Check backup exists: `ls -la /data/WNC/LCM-Logs-Data/projects.json.backup`

## 🚫 **What NOT to Do**

- ❌ **Never manually edit** `projects.json` while backend is running
- ❌ **Never use relative paths** in configuration
- ❌ **Never delete project directories** without using the API
- ❌ **Never ignore** defensive protection warnings
- ❌ **Never run multiple backends** on the same DATA_DIR

## 📞 **Support Information**

**Critical Log Files:**
- Application: `/data/WNC/LCM-Logs-Data/logs/app.log`
- Backend: `/data/WNC/LCM-Logs-Data/logs/backend.log`

**Key Configuration:**
- Environment: `.env` file
- Template: `env.config`

**Important URLs:**
- Health Check: `http://localhost:8000/health`
- API Docs: `http://localhost:8000/api/docs`
- Projects API: `http://localhost:8000/api/v1/projects`
