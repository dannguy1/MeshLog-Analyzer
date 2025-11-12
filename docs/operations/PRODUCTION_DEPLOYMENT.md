# prplOS LCM Log Analysis System - Production Deployment Guide

## 🚀 Production Deployment Checklist

### Pre-Deployment Requirements
- [ ] Docker and Docker Compose installed
- [ ] At least 8GB RAM available
- [ ] 50GB free disk space
- [ ] SSL certificates (for HTTPS)
- [ ] Domain name configured
- [ ] Firewall rules configured
- [ ] Backup strategy implemented

### 1. Environment Setup

#### Copy Environment Template
```bash
cp env.template .env
```

#### Configure Production Environment Variables
```bash
# Edit .env file with production values
nano .env
```

**Critical Production Settings:**
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-strong-secret-key>
JWT_SECRET_KEY=<generate-strong-jwt-secret>
POSTGRES_PASSWORD=<strong-database-password>
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. SSL/HTTPS Configuration

#### Generate SSL Certificates
```bash
# Using Let's Encrypt
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

#### Update nginx.conf for HTTPS
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy to backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket proxy
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Production Docker Compose

#### Create Production Override
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  postgres:
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped

  redis:
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
    restart: unless-stopped

  celery_worker:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped

  celery_beat:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
    restart: unless-stopped
```

### 4. Monitoring and Logging

#### Add Monitoring Stack
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - prplos_network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - prplos_network

volumes:
  prometheus_data:
  grafana_data:

networks:
  prplos_network:
    external: true
```

### 5. Backup Strategy

#### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T postgres pg_dump -U prplos_user prplos_logs > $BACKUP_DIR/db_$DATE.sql

# File uploads backup
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Analysis results backup
tar -czf $BACKUP_DIR/results_$DATE.tar.gz analysis_results/

# Compress database backup
gzip $BACKUP_DIR/db_$DATE.sql

# Clean old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log backup completion
echo "Backup completed: $DATE" >> $BACKUP_DIR/backup.log
```

#### Setup Cron Job
```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
```

### 6. Security Hardening

#### Firewall Configuration
```bash
# UFW firewall rules
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### Docker Security
```bash
# Create non-root user for Docker
sudo groupadd docker
sudo usermod -aG docker $USER

# Enable Docker daemon security features
# Edit /etc/docker/daemon.json
{
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
```

### 7. Performance Optimization

#### Database Optimization
```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Reload configuration
SELECT pg_reload_conf();
```

#### Redis Optimization
```bash
# Redis configuration for production
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 8. Deployment Commands

#### Production Deployment
```bash
# Build and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale workers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale celery_worker=5

# Check service status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

#### Health Checks
```bash
# System health check
curl -f https://yourdomain.com/health

# API health check
curl -f https://yourdomain.com/api/v1/health

# Database connection
docker-compose exec postgres pg_isready -U prplos_user -d prplos_logs
```

### 9. Maintenance Procedures

#### Regular Maintenance Tasks
```bash
# Weekly database maintenance
docker-compose exec postgres psql -U prplos_user -d prplos_logs -c "VACUUM ANALYZE;"

# Monthly log rotation
docker system prune -f

# Quarterly SSL certificate renewal
sudo certbot renew

# Annual security updates
docker-compose pull
docker-compose up -d
```

#### Monitoring Alerts
- Set up monitoring alerts for:
  - CPU usage > 80%
  - Memory usage > 85%
  - Disk usage > 90%
  - Database connections > 80%
  - Response time > 2 seconds

### 10. Disaster Recovery

#### Recovery Procedures
```bash
# Stop all services
docker-compose down

# Restore from backup
docker-compose exec -T postgres psql -U prplos_user -d prplos_logs < backup.sql

# Restore files
tar -xzf uploads_backup.tar.gz
tar -xzf results_backup.tar.gz

# Start services
docker-compose up -d
```

#### High Availability Setup
- Use load balancer (HAProxy/Nginx)
- Database replication (PostgreSQL streaming replication)
- Redis cluster for high availability
- Multiple application instances

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring stack deployed
- [ ] Backup strategy implemented
- [ ] Security hardening applied
- [ ] Performance optimization completed
- [ ] Health checks configured
- [ ] Documentation updated
- [ ] Team training completed

## 📞 Support

For production support:
- Monitor system health regularly
- Set up alerting for critical issues
- Maintain backup and recovery procedures
- Keep documentation updated
- Train team on maintenance procedures
