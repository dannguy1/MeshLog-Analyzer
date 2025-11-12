# Containerized Deployment Guide - MeshLog with Agent Engine Integration

## 🐳 Containerized Architecture Overview

When deploying MeshLog as containers with an external agent engine, Redis should **definitely** run as a container for the following reasons:

### ✅ Benefits of Containerized Redis

1. **Service Isolation**: No dependency on host Redis service
2. **Consistent Environment**: All services run in containers
3. **Proper Orchestration**: Service dependencies and health checks
4. **Shared State**: Both MeshLog and agent engine can access the same Redis instance
5. **Scalability**: Easy to scale Redis independently
6. **Portability**: Works on any host without Redis installation

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Frontend  │    │   Backend   │    │   Redis     │    │
│  │  (Nginx)    │◄───┤  (FastAPI)  │◄───┤  (Cache)    │    │
│  │   Port 80   │    │  Port 8000  │    │ Port 6379   │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                │                │         │
│  ┌─────────────┐               │                │         │
│  │   Celery    │               │                │         │
│  │   Worker    │───────────────┘                │         │
│  └─────────────┘                               │         │
│                                                │         │
│  ┌─────────────────────────────────────────────┘         │
│  │              External Agent Engine                     │
│  │              (Separate Container)                     │
│  │              Connects to Redis:6379                   │
│  └─────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Deployment Options

### Option 1: MeshLog + Shared Redis (Recommended)

Use the provided `docker-compose.agent.yml`:

```bash
# Deploy MeshLog with containerized Redis
docker compose -f docker-compose.agent.yml up -d

# Agent engine connects to the same Redis instance
# Agent engine configuration:
# REDIS_URL=redis://<host-ip>:6379/0
```

### Option 2: External Redis Service

If you prefer to use an external Redis service (AWS ElastiCache, etc.):

```bash
# Update environment variables
export REDIS_URL=redis://your-redis-endpoint:6379/0

# Deploy without Redis container
docker compose -f docker-compose.yml up -d --scale redis=0
```

## 🔧 Configuration for Agent Engine Integration

### Environment Variables

Create a `.env` file for agent engine integration:

```bash
# Agent Engine Configuration
AGENT_ENGINE_URL=http://agent-engine:8001
WNC_LOG_AGENTS_ENABLED=true
WNC_LOG_AGENTS_TIMEOUT=300
AGENT_ANALYSIS_ENABLED=true
AGENT_RESULT_CACHE_TTL=3600

# Redis Configuration (for both MeshLog and Agent Engine)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Agent Engine Configuration

Your agent engine should connect to the same Redis instance:

```python
# Agent Engine Redis Configuration
REDIS_URL = "redis://<host-ip>:6379/0"
# or if running on same Docker network:
REDIS_URL = "redis://redis:6379/0"
```

## 📋 Deployment Commands

### Start MeshLog with Agent Integration

```bash
# Using the agent-optimized compose file
docker compose -f docker-compose.agent.yml up -d

# Check service status
docker compose -f docker-compose.agent.yml ps

# View logs
docker compose -f docker-compose.agent.yml logs -f
```

### Scale Services

```bash
# Scale Celery workers
docker compose -f docker-compose.agent.yml up -d --scale celery_worker=3

# Scale backend (with load balancer)
docker compose -f docker-compose.agent.yml up -d --scale backend=2
```

### Health Checks

```bash
# Check Redis
docker compose -f docker-compose.agent.yml exec redis redis-cli ping

# Check Backend
curl http://localhost:8000/health

# Check Frontend
curl http://localhost/health
```

## 🔍 Monitoring and Troubleshooting

### Redis Connection Issues

```bash
# Check Redis container logs
docker compose -f docker-compose.agent.yml logs redis

# Test Redis connectivity from backend
docker compose -f docker-compose.agent.yml exec backend redis-cli -h redis ping

# Check Redis memory usage
docker compose -f docker-compose.agent.yml exec redis redis-cli info memory
```

### Agent Engine Integration

```bash
# Check if agent engine can reach Redis
# From agent engine container:
redis-cli -h <redis-host-ip> ping

# Check MeshLog agent configuration
curl http://localhost:8000/api/v1/agent-analysis/agents
```

### Network Connectivity

```bash
# Check Docker network
docker network ls
docker network inspect prplos_network

# Test connectivity between containers
docker compose -f docker-compose.agent.yml exec backend ping redis
```

## 🛡️ Security Considerations

### Redis Security

```bash
# Enable Redis authentication (recommended for production)
# In docker-compose.agent.yml, update Redis command:
command: redis-server --appendonly yes --requirepass your-secure-password

# Update REDIS_URL in all services:
REDIS_URL=redis://:your-secure-password@redis:6379/0
```

### Network Security

```bash
# Use internal network for Redis (remove port exposure)
# In docker-compose.agent.yml:
redis:
  # Remove: ports: - "6379:6379"
  # Keep internal network access only
```

## 📊 Performance Optimization

### Redis Configuration

```bash
# Optimize Redis for your workload
command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru --save 900 1 --save 300 10 --save 60 10000
```

### Resource Limits

```bash
# Adjust resource limits based on your needs
deploy:
  resources:
    limits:
      memory: 1G      # Increase for larger datasets
      cpus: '1.0'     # Increase for high-throughput
```

## 🔄 Migration from System Redis

If you're currently using system Redis and want to migrate to containerized Redis:

```bash
# 1. Stop system Redis
sudo systemctl stop redis-server
sudo systemctl disable redis-server

# 2. Backup Redis data (if needed)
sudo cp -r /var/lib/redis /backup/redis-backup

# 3. Deploy containerized Redis
docker compose -f docker-compose.agent.yml up -d redis

# 4. Verify connectivity
docker compose -f docker-compose.agent.yml exec redis redis-cli ping
```

## 📈 Production Recommendations

1. **Use Redis Persistence**: Enable AOF for data durability
2. **Monitor Memory Usage**: Set appropriate memory limits
3. **Enable Health Checks**: Monitor Redis health
4. **Use Resource Limits**: Prevent resource exhaustion
5. **Backup Strategy**: Regular Redis data backups
6. **Security**: Enable Redis authentication in production
7. **Monitoring**: Use Redis monitoring tools (RedisInsight, etc.)

## 🎯 Summary

**Yes, Redis should run as a container** when deploying MeshLog with agent engine integration because:

- ✅ **Consistency**: All services containerized
- ✅ **Isolation**: No host dependencies
- ✅ **Shared State**: Both MeshLog and agent engine access same Redis
- ✅ **Orchestration**: Proper service management
- ✅ **Scalability**: Easy to scale and manage
- ✅ **Portability**: Works anywhere Docker runs

The provided `docker-compose.agent.yml` is optimized for this architecture and includes proper agent engine integration settings.


