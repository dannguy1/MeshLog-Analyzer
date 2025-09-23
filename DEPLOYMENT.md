# prplOS LCM Log Analysis System - Deployment Guide

## 🚀 Quick Start Deployment

### Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Node.js** 18+ (for frontend development)
- **Python** 3.11+ (for backend development)
- **Git** (for version control)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Mesh-Log

# Make deployment scripts executable
chmod +x deploy.sh
chmod +x ui/build-production.sh
```

### 2. Production Deployment

```bash
# Deploy the entire system
./deploy.sh deploy

# Or use Docker Compose directly
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. Verify Deployment

```bash
# Check service status
./deploy.sh status

# Check service health
./deploy.sh health

# View logs
./deploy.sh logs
```

## 📊 Service Endpoints

After deployment, the following services will be available:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🐳 Docker Services

The deployment includes the following services:

| Service | Port | Description |
|---------|------|-------------|
| `frontend` | 80 | React frontend with Nginx |
| `backend` | 8000 | FastAPI backend |
| `redis` | 6379 | Redis cache and message broker |
| `celery_worker` | - | Background task processor |
| `celery_beat` | - | Scheduled task scheduler |

## 🔧 Configuration

### Environment Variables

Create a `.env` file or use the provided `env.production`:

```bash
# Copy production environment template
cp env.production .env

# Edit configuration
nano .env
```

### Key Configuration Options

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

## 📁 Directory Structure

```
Mesh-Log/
├── app/                    # Backend application
├── ui/                     # Frontend application
├── data/                   # Persistent data
│   └── WNC/
│       └── LCM-Logs-Data/  # Project data
├── logs/                   # Application logs
├── uploads/               # File uploads
├── analysis_results/      # Analysis outputs
├── docker-compose.yml     # Base Docker Compose
├── docker-compose.prod.yml # Production overrides
├── Dockerfile             # Backend Docker image
├── Dockerfile.backend     # Alternative backend image
├── deploy.sh              # Deployment script
└── env.production         # Production environment
```

## 🛠️ Management Commands

### Using the Deployment Script

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

### Using Docker Compose Directly

```bash
# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Stop services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Scale workers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale celery_worker=3

# Rebuild and restart
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 🔍 Monitoring and Troubleshooting

### Health Checks

All services include health checks:

```bash
# Check individual services
curl http://localhost/health          # Frontend
curl http://localhost:8000/health     # Backend
docker-compose exec redis redis-cli ping  # Redis
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

### Common Issues

1. **Port Conflicts**: Ensure ports 80 and 8000 are available
2. **Permission Issues**: Check directory permissions for data volumes
3. **Memory Issues**: Adjust resource limits in docker-compose.prod.yml
4. **Database Issues**: Check SQLite file permissions in data directory

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Use HTTPS in production (configure reverse proxy)
- [ ] Set up proper firewall rules
- [ ] Regular security updates
- [ ] Backup data regularly
- [ ] Monitor logs for suspicious activity

### HTTPS Setup (Optional)

For HTTPS in production, use a reverse proxy like Nginx or Traefik:

```nginx
# Nginx configuration example
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://frontend:80;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
    }
}
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale Celery workers
docker-compose up -d --scale celery_worker=5

# Scale backend (with load balancer)
docker-compose up -d --scale backend=3
```

### Resource Optimization

Adjust resource limits in `docker-compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Backup and Restore

```bash
# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/ uploads/ analysis_results/

# Restore data
tar -xzf backup-20240101.tar.gz
```

## 📞 Support

For deployment issues:

1. Check the logs: `./deploy.sh logs`
2. Verify service health: `./deploy.sh health`
3. Check Docker status: `docker system df`
4. Review configuration files

## 🎯 Next Steps

After successful deployment:

1. **Configure Monitoring**: Set up Prometheus/Grafana for metrics
2. **Set up Backups**: Implement automated backup strategy
3. **Security Hardening**: Configure firewall and SSL certificates
4. **Performance Tuning**: Optimize based on usage patterns
5. **Documentation**: Update team documentation with deployment details

