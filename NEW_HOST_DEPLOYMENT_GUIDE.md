# 🚀 New Host Deployment Guide - WNC LCM Log Analysis System

## 📋 Quick Start Overview

This guide will help you deploy the WNC LCM Log Analysis System on a completely new host from scratch. The system includes a React frontend, Python FastAPI backend, Redis cache, and comprehensive log analysis capabilities.

---

## 📦 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, etc.)
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB free space
- **Network**: Internet connection for downloading dependencies

### Required Software
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For cloning the repository

---

## 🛠️ Step 1: Install Dependencies

### Install Docker (Ubuntu/Debian)
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Install Docker (CentOS/RHEL)
```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Verify Installation
```bash
# Check Docker
docker --version
# Expected: Docker version 20.10.x or higher

# Check Docker Compose
docker-compose --version
# Expected: Docker Compose version 2.x.x or higher

# Test Docker (may need to logout/login first)
docker run hello-world
```

---

## 📥 Step 2: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/Dan-Nguyen_wnc/wnc-lcm-log-analysis-system.git

# Enter project directory
cd wnc-lcm-log-analysis-system

# Verify files
ls -la
# Should see: docker-compose.yml, Dockerfile, app/, ui/, etc.
```

---

## ⚙️ Step 3: Configure Environment

### Create Data Directory
```bash
# Create persistent data directory
sudo mkdir -p /data/WNC/LCM-Logs-Data
sudo chown -R $USER:$USER /data/WNC

# Verify permissions
ls -la /data/WNC/
```

### Set Up Environment File
```bash
# Copy production environment template
cp env.production .env

# Edit configuration (optional - defaults work for most cases)
nano .env
```

### Key Configuration Options (Optional Customization)
```bash
# Data Directory
DATA_DIR=/data/WNC/LCM-Logs-Data

# Database
DATABASE_URL=sqlite:///./data/prplos_analysis.db

# Redis
REDIS_URL=redis://redis:6379/0

# Security (change in production)
SECRET_KEY=your-unique-secret-key-here

# File Upload Limits
MAX_FILE_SIZE_MB=100

# Analysis Settings
WNC_LOG_AGENTS_ENABLED=true
AGENT_ANALYSIS_ENABLED=true
```

---

## 🚀 Step 4: Deploy the System

### Option A: Quick Deployment (Recommended)
```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy everything
./deploy.sh deploy

# This will:
# - Build all Docker images
# - Start all services
# - Configure networking
# - Set up persistent storage
```

### Option B: Manual Docker Compose
```bash
# Build and start all services
docker-compose up -d --build

# Or for production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Monitor Deployment Progress
```bash
# Watch the deployment logs
docker-compose logs -f

# Check service status
docker-compose ps
```

---

## ✅ Step 5: Verify Deployment

### Check Service Status
```bash
# Using deployment script
./deploy.sh status

# Or manually
docker-compose ps
```

Expected output:
```
NAME                STATUS              PORTS
prplos_backend      Up x minutes        0.0.0.0:8000->8000/tcp
prplos_frontend     Up x minutes        0.0.0.0:80->80/tcp  
prplos_redis        Up x minutes        6379/tcp
```

### Test Service Health
```bash
# Backend API health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"...","version":"1.0.0"}

# Frontend accessibility
curl -I http://localhost:80
# Expected: HTTP/1.1 200 OK

# Check all services
./deploy.sh health
```

### Test Web Interface
Open your browser and navigate to:
- **Frontend**: http://your-server-ip (or http://localhost)
- **API Documentation**: http://your-server-ip:8000/docs
- **Health Check**: http://your-server-ip:8000/health

---

## 🔧 Step 6: Post-Deployment Configuration

### Firewall Configuration (if needed)
```bash
# Allow HTTP traffic (port 80)
sudo ufw allow 80/tcp

# Allow API traffic (port 8000) - optional, usually behind proxy
sudo ufw allow 8000/tcp

# Apply firewall rules
sudo ufw enable
```

### Set Up Reverse Proxy (Production)
For production deployment, consider setting up Nginx as a reverse proxy:

```nginx
# /etc/nginx/sites-available/meshlog
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Step 7: Monitoring and Maintenance

### View Logs
```bash
# All services
./deploy.sh logs

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f redis
```

### Service Management
```bash
# Stop all services
./deploy.sh stop

# Restart services
./deploy.sh restart

# Update and rebuild
git pull
./deploy.sh deploy
```

### Backup Data
```bash
# Create backup
tar -czf meshlog-backup-$(date +%Y%m%d).tar.gz \
    /data/WNC/LCM-Logs-Data/ \
    logs/ \
    uploads/ \
    analysis_results/

# Schedule regular backups (crontab -e)
0 2 * * * /path/to/backup-script.sh
```

---

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Change default `SECRET_KEY` in `.env`
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up regular security updates
- [ ] Implement backup strategy
- [ ] Monitor logs for suspicious activity
- [ ] Use strong passwords for any external services

### SSL/HTTPS Setup (Optional)
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use
```bash
# Check what's using port 80 or 8000
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# Stop conflicting services
sudo systemctl stop apache2  # or nginx
```

#### 2. Permission Denied for Data Directory
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER /data/WNC/
sudo chmod -R 755 /data/WNC/
```

#### 3. Docker Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### 4. Services Won't Start
```bash
# Check Docker daemon
sudo systemctl status docker

# Check system resources
df -h          # Disk space
free -h        # Memory
```

### Get Help
```bash
# Check deployment script help
./deploy.sh --help

# View detailed service logs
docker-compose logs --tail=100 [service-name]

# Check container resource usage
docker stats
```

---

## 📈 Scaling and Performance

### Resource Monitoring
```bash
# Monitor container resources
docker stats

# Check system load
htop
# or
top
```

### Scale Services (if needed)
```bash
# Scale Celery workers
docker-compose up -d --scale celery_worker=3

# Scale backend (with load balancer)
docker-compose up -d --scale backend=2
```

---

## 🎯 Next Steps

After successful deployment:

1. **Upload Log Files**: Use the web interface to upload and analyze logs
2. **Configure Projects**: Set up project structures for your data
3. **Set Up Monitoring**: Consider Prometheus/Grafana for metrics
4. **Schedule Backups**: Implement automated backup strategy
5. **Performance Tuning**: Optimize based on your usage patterns

---

## 📞 Support and Documentation

### Additional Documentation
- `DEPLOYMENT.md` - Detailed deployment options
- `CONTAINERIZED-DEPLOYMENT.md` - Advanced container configuration
- `README.md` - Project overview and features
- `docs/` - Comprehensive system documentation

### Deployment Verification
After deployment, you should have:
- ✅ Frontend accessible at http://your-server
- ✅ Backend API at http://your-server:8000
- ✅ All services showing "healthy" status
- ✅ Data persistence working
- ✅ Log analysis capabilities functional

---

**🎉 Congratulations! Your WNC LCM Log Analysis System is now deployed and ready to use!**

**Total Deployment Time**: ~10-15 minutes (depending on system and internet speed)  
**Services**: 3 containers (Frontend, Backend, Redis)  
**Storage**: Persistent data at `/data/WNC/LCM-Logs-Data/`  
**Access**: Web interface ready for log analysis
