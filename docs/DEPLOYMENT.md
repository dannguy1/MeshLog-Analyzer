# prplOS LCM Log Analysis System - Deployment Scripts

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- 10GB free disk space

### 1. Clone and Setup
```bash
git clone <repository-url>
cd prplOS-Log-Analysis-System
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Start the System
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Development Setup

### Backend Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://prplos_user:prplos_password@localhost:5432/prplos_logs"
export REDIS_URL="redis://localhost:6379/0"

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd ui

# Install dependencies
npm install

# Start development server
npm run dev
```

## Production Deployment

### Using Docker Compose
```bash
# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale celery_worker=3
```

### Using Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

## Monitoring and Maintenance

### Health Checks
```bash
# Check all services
docker-compose ps

# View service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Database Management
```bash
# Connect to database
docker-compose exec postgres psql -U prplos_user -d prplos_logs

# Backup database
docker-compose exec postgres pg_dump -U prplos_user prplos_logs > backup.sql

# Restore database
docker-compose exec -T postgres psql -U prplos_user -d prplos_logs < backup.sql
```

### Log Management
```bash
# View application logs
docker-compose logs -f backend

# View nginx logs
docker-compose logs -f frontend

# View database logs
docker-compose logs -f postgres
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Database connection issues**
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready -U prplos_user -d prplos_logs
   
   # Restart database
   docker-compose restart postgres
   ```

3. **Memory issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

### Performance Tuning

1. **Database optimization**
   ```sql
   -- Analyze table statistics
   ANALYZE;
   
   -- Check slow queries
   SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   ```

2. **Redis optimization**
   ```bash
   # Check Redis memory usage
   docker-compose exec redis redis-cli info memory
   
   # Monitor Redis performance
   docker-compose exec redis redis-cli monitor
   ```

## Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong passwords for database and Redis
- Rotate secrets regularly

### Network Security
- Use HTTPS in production
- Configure firewall rules
- Limit container network access

### Data Protection
- Encrypt sensitive data at rest
- Implement proper backup strategies
- Follow data retention policies

## Backup and Recovery

### Automated Backups
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
docker-compose exec -T postgres pg_dump -U prplos_user prplos_logs > $BACKUP_DIR/db_$DATE.sql

# File uploads backup
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Analysis results backup
tar -czf $BACKUP_DIR/results_$DATE.tar.gz analysis_results/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Recovery Procedures
```bash
# Stop services
docker-compose down

# Restore database
docker-compose exec -T postgres psql -U prplos_user -d prplos_logs < backup.sql

# Restore files
tar -xzf uploads_backup.tar.gz
tar -xzf results_backup.tar.gz

# Start services
docker-compose up -d
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend workers
docker-compose up -d --scale celery_worker=5

# Scale frontend (with load balancer)
docker-compose up -d --scale frontend=3
```

### Vertical Scaling
```bash
# Increase memory limits
deploy:
  resources:
    limits:
      memory: 4G
    reservations:
      memory: 2G
```

## Updates and Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Migrations
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current
```

## Support and Documentation

- **API Documentation**: http://localhost:8000/docs
- **System Health**: http://localhost:8000/api/v1/health
- **Logs**: Check Docker logs for troubleshooting
- **Issues**: Report bugs and feature requests via GitHub

## License

This project is part of the prplOS LCM Log Analysis System.
