# prplOS LCM Log Analysis System - Development Environment Scripts

## 📋 **Overview**

This directory contains comprehensive scripts for managing the prplOS LCM Log Analysis System development environment. These scripts provide easy-to-use commands for starting, stopping, restarting, and monitoring all development services.

## 🚀 **Available Scripts**

### **1. dev-start.sh** - Start Development Environment
Starts all development services with support for background and foreground modes.

**Usage:**
```bash
./scripts/dev-start.sh [-b|--background] [-f|--foreground] [-h|--help]
```

**Options:**
- `-b, --background`: Start services in background mode
- `-f, --foreground`: Start services in foreground mode (default)
- `-h, --help`: Show help message

**Examples:**
```bash
./scripts/dev-start.sh              # Start in foreground mode
./scripts/dev-start.sh -f           # Start in foreground mode
./scripts/dev-start.sh -b           # Start in background mode
```

**Services Started:**
- PostgreSQL (Docker or system)
- Redis (Docker or system)
- Backend (FastAPI with uvicorn)
- Frontend (React with Vite)

### **2. dev-stop.sh** - Stop Development Environment
Stops all development services cleanly.

**Usage:**
```bash
./scripts/dev-stop.sh [-h|--help]
```

**Examples:**
```bash
./scripts/dev-stop.sh               # Stop all services
./scripts/dev-stop.sh --help        # Show help
```

**Services Stopped:**
- Frontend (React)
- Backend (FastAPI)
- Redis
- PostgreSQL
- Docker containers (if used)

### **3. dev-restart.sh** - Restart Development Environment
Stops all services and then starts them again with specified mode.

**Usage:**
```bash
./scripts/dev-restart.sh [-b|--background] [-f|--foreground] [-h|--help]
```

**Options:**
- `-b, --background`: Restart services in background mode
- `-f, --foreground`: Restart services in foreground mode (default)
- `-h, --help`: Show help message

**Examples:**
```bash
./scripts/dev-restart.sh            # Restart in foreground mode
./scripts/dev-restart.sh -b         # Restart in background mode
```

### **4. dev-status.sh** - Check Development Environment Status
Shows comprehensive status information for all services.

**Usage:**
```bash
./scripts/dev-status.sh [-h|--help]
```

**Examples:**
```bash
./scripts/dev-status.sh             # Show all status information
./scripts/dev-status.sh --help      # Show help
```

**Information Displayed:**
- System information (OS, Python, Node.js, Docker, etc.)
- Service status (running/stopped)
- Port availability
- Docker containers
- Log files
- Quick action commands

## 🔧 **Configuration**

### **Port Configuration**
The scripts use the following default ports:
- **Backend**: 8000
- **Frontend**: 3000
- **PostgreSQL**: 5432
- **Redis**: 6379

### **Directory Structure**
```
prplOS-Log-Analysis-System/
├── scripts/
│   ├── dev-start.sh           # Start script
│   ├── dev-stop.sh            # Stop script
│   ├── dev-restart.sh         # Restart script
│   ├── dev-status.sh          # Status script
│   ├── backend-start.sh       # Backend-only start
│   ├── backend-stop.sh        # Backend-only stop
│   ├── backend-restart.sh     # Backend-only restart
│   ├── backend-status.sh      # Backend-only status
│   ├── backend-debug.sh       # Backend debug mode
│   ├── frontend-start.sh      # Frontend-only start
│   ├── frontend-stop.sh       # Frontend-only stop
│   ├── install_complete.sh    # Complete installation
│   ├── cleanup_enhanced.py    # Enhanced cleanup
│   └── setup_sqlite.py        # Database setup
├── logs/                  # Log files
│   ├── backend.log
│   ├── frontend.log
│   ├── postgres.log
│   └── redis.log
├── pids/                  # PID files
│   ├── backend.pid
│   ├── frontend.pid
│   ├── postgres.pid
│   └── redis.pid
├── data/                  # Data directory
├── uploads/               # Upload directory
└── analysis_results/      # Analysis results
```

## 📋 **Available Scripts**

### **Development Environment Scripts**
- **`dev-start.sh`** - Start all services (backend, frontend, Redis)
- **`dev-stop.sh`** - Stop all services
- **`dev-restart.sh`** - Restart all services
- **`dev-status.sh`** - Check status of all services

### **Backend-Specific Scripts**
- **`backend-start.sh`** - Start only backend services
- **`backend-stop.sh`** - Stop only backend services
- **`backend-restart.sh`** - Restart only backend services
- **`backend-status.sh`** - Check backend service status
- **`backend-debug.sh`** - Start backend in debug mode

### **Frontend-Specific Scripts**
- **`frontend-start.sh`** - Start only frontend services
- **`frontend-stop.sh`** - Stop only frontend services

### **System Management Scripts**
- **`install_complete.sh`** - Complete system installation
- **`cleanup_enhanced.py`** - Enhanced cleanup with backup options
- **`setup_sqlite.py`** - Database setup and initialization
- **`setup_dev.sh`** - Development environment setup

## 🎯 **Usage Examples**

### **Quick Start (Background Mode)**
```bash
# Start all services in background
./scripts/dev-start.sh -b

# Check status
./scripts/dev-status.sh

# Access the application
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

### **Development Mode (Foreground)**
```bash
# Start services in foreground for development
./scripts/dev-start.sh -f

# This will start backend in foreground
# Press Ctrl+C to stop backend
# Then start frontend separately if needed
```

### **Complete Workflow**
```bash
# 1. Start services
./scripts/dev-start.sh -b

# 2. Check status
./scripts/dev-status.sh

# 3. View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# 4. Restart services
./scripts/dev-restart.sh -b

# 5. Stop services
./scripts/dev-stop.sh
```

## 🔍 **Service Management**

### **Individual Service Control**

**Backend (FastAPI):**
```bash
# Start backend only
source venv/bin/activate
export DATABASE_URL="postgresql://prplos_user:prplos_password@localhost:5432/prplos_logs"
export REDIS_URL="redis://localhost:6379/0"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (React):**
```bash
# Start frontend only
cd ui
npm install
npm run dev
```

**PostgreSQL:**
```bash
# Using Docker
docker run -d --name prplos-postgres \
  -e POSTGRES_DB=prplos_logs \
  -e POSTGRES_USER=prplos_user \
  -e POSTGRES_PASSWORD=prplos_password \
  -p 5432:5432 \
  postgres:15-alpine

# Using system PostgreSQL
pg_ctl -D /usr/local/var/postgres start
```

**Redis:**
```bash
# Using Docker
docker run -d --name prplos-redis \
  -p 6379:6379 \
  redis:7-alpine

# Using system Redis
redis-server --daemonize yes --port 6379
```

### **Environment Variables**
The scripts automatically set the following environment variables:
```bash
DATABASE_URL="postgresql://prplos_user:prplos_password@localhost:5432/prplos_logs"
REDIS_URL="redis://localhost:6379/0"
ENVIRONMENT="development"
DEBUG="true"
```

## 🛠️ **Troubleshooting**

### **Common Issues**

**1. Port Already in Use**
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3000
lsof -i :5432
lsof -i :6379

# Kill the process
kill -9 <PID>
```

**2. Services Not Starting**
```bash
# Check logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Check status
./scripts/dev-status.sh

# Restart services
./scripts/dev-restart.sh -b
```

**3. Docker Issues**
```bash
# Check Docker status
docker ps
docker ps -a

# Clean up containers
docker stop $(docker ps -q --filter name=prplos-*)
docker rm $(docker ps -aq --filter name=prplos-*)
```

**4. Permission Issues**
```bash
# Make scripts executable
chmod +x dev-*.sh

# Check file permissions
ls -la dev-*.sh
```

### **Health Checks**

**Backend Health:**
```bash
curl http://localhost:8000/api/v1/health
```

**Frontend Health:**
```bash
curl http://localhost:3000
```

**PostgreSQL Health:**
```bash
pg_isready -h localhost -p 5432
```

**Redis Health:**
```bash
redis-cli ping
```

## 📊 **Monitoring and Logs**

### **Log Files**
- `logs/backend.log`: Backend application logs
- `logs/frontend.log`: Frontend development server logs
- `logs/postgres.log`: PostgreSQL logs (system installation)
- `logs/redis.log`: Redis logs (system installation)

### **Real-time Log Monitoring**
```bash
# Monitor all logs
tail -f logs/*.log

# Monitor specific service
tail -f logs/backend.log
tail -f logs/frontend.log
```

### **Performance Monitoring**
```bash
# Check resource usage
top
htop

# Check disk usage
df -h
du -sh *

# Check memory usage
free -h
```

## 🔒 **Security Considerations**

### **Development Environment**
- Services run on localhost only
- No external network access
- Debug mode enabled for development
- No production secrets in development

### **Data Protection**
- Data stored locally in `data/` directory
- Uploads stored in `uploads/` directory
- Analysis results in `analysis_results/` directory
- Logs contain no sensitive information

## 🚀 **Production vs Development**

### **Development Environment**
- Uses these scripts for local development
- Debug mode enabled
- Hot reload enabled
- Local database and cache
- Development ports

### **Production Environment**
- Uses Docker Compose (`docker-compose.yml`)
- Production configuration
- No debug mode
- Production database and cache
- Production ports and security

## 📚 **Additional Resources**

### **Documentation**
- `README.md`: Main project documentation
- `DEPLOYMENT.md`: Deployment guide
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md): Production deployment guide
- [SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md): Complete system overview

### **Testing**
```bash
# Run backend tests
python -m pytest tests/ -v

# Run frontend tests
cd ui && npm test

# Run integration tests
python test_integration.py
```

### **Development Tools**
- **Backend**: FastAPI, uvicorn, pytest
- **Frontend**: React, Vite, npm
- **Database**: PostgreSQL, SQLAlchemy
- **Cache**: Redis
- **Containerization**: Docker, Docker Compose

---

## 🎉 **Quick Reference**

| Command | Description |
|---------|-------------|
| `./scripts/dev-start.sh -b` | Start all services in background |
| `./scripts/dev-start.sh -f` | Start all services in foreground |
| `./scripts/dev-stop.sh` | Stop all services |
| `./scripts/dev-restart.sh -b` | Restart all services in background |
| `./scripts/dev-status.sh` | Check service status |
| `tail -f logs/*.log` | Monitor all logs |
| `curl http://localhost:8000/api/v1/health` | Check backend health |

**Default URLs:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
