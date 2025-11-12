# Agent Integration for Containerized Deployment

## Overview

This document summarizes the containerized agent integration setup for the prplOS LCM Log Analysis System. The integration enables MeshLog to communicate with specialized agent services for advanced log analysis while maintaining proper data flow and result management across Docker containers.

## Key Changes Made

### 1. Updated Agent Integration Specification

**File**: `architecture/AGENT-INTEGRATION-SUMMARY.md`

**Key Updates**:
- **Containerized Architecture**: Updated data flow to use Docker containers and shared volumes
- **Environment Variables**: Added container-specific environment variables
- **Docker Compose Configuration**: Complete Docker Compose setup for agent integration
- **Container Security**: Added security considerations for containerized deployment
- **Monitoring & Debugging**: Container-specific debugging tools and commands

### 2. Docker Compose Configuration

**File**: `docker-compose.agent.yml`

**Features**:
- **Shared Volume**: Both MeshLog and agent services use the same data volume
- **Network Isolation**: All services communicate through a dedicated Docker network
- **Health Checks**: Comprehensive health checks for all services
- **Service Dependencies**: Proper dependency management between services
- **Resource Management**: Container resource limits and restart policies

### 3. Deployment Scripts

**Files**: 
- `scripts/deploy-agent.sh`
- `scripts/health-check-agent.sh`

**Features**:
- **Automated Deployment**: One-command deployment with agent integration
- **Health Monitoring**: Comprehensive health checks for all services
- **Error Handling**: Robust error handling and recovery
- **Agent Connectivity Testing**: Automated testing of agent service connectivity

### 4. Updated Main Deploy Script

**File**: `deploy.sh`

**Updates**:
- **Enhanced deploy_agent()**: Improved agent deployment with connectivity testing
- **Agent Project Validation**: Checks for agent project existence before deployment
- **Build Process**: Automated agent service image building
- **Health Verification**: Comprehensive health checks after deployment

### 5. Enhanced WNC Steering Agent with 802.11k/v Capability Analysis

**File**: `app/agents/wnc_steering.py`

**New Features**:
- **Automatic Capability Detection**: Integrated 802.11k/v client capability analysis
- **Pattern Recognition**: 7 new detection patterns for wireless capability assessment
- **Strategy Recommendations**: Intelligent steering strategy recommendations based on client capabilities
- **Comprehensive Analysis**: Per-client capability breakdown and network-wide capability distribution
- **Seamless Integration**: Capability analysis automatically included in standard agent workflow

**Enhanced Patterns** (in `patterns.json`):
- `steering_capability_explicit`: Direct capability declarations
- `steering_rrm_capability`: 802.11k Radio Resource Measurement detection
- `steering_btm_capability`: 802.11v BSS Transition Management detection
- `steering_rrm_not_supported`: 802.11k failure detection
- `steering_btm_not_supported`: 802.11v failure detection
- `steering_neighbor_report`: 802.11k neighbor report usage
- `steering_bss_transition`: 802.11v BSS transition execution

**Analysis Output**: Agent results now include comprehensive `capability_analysis` section with:
- Network-wide capability overview and percentages
- Per-client capability details and pattern matches
- Strategic recommendations for optimal steering approaches
- Support for hybrid environments with mixed client capabilities

## Architecture

### Containerized Data Flow

```
MeshLog Frontend Container → MeshLog Backend Container → Agent Service Container
     ↓                              ↓                           ↓
Docker Volume (Shared Data) ← Agent Results ← Direct Write to Shared Volume
     ↓
Shared Data Directory (/data/WNC/LCM-Logs-Data)
```

### Service Communication

- **MeshLog Backend** ↔ **Agent Service**: HTTP communication via Docker network
- **Both Services** ↔ **Redis**: Shared Redis instance for coordination
- **All Services** ↔ **Shared Volume**: File system access for data persistence

## Configuration

### Environment Variables

```bash
# Agent Service Configuration
WNC_LOG_AGENTS_ENABLED=true
WNC_LOG_AGENTS_URL=http://wnc-log-agents:8001  # Container service name
WNC_LOG_AGENTS_TIMEOUT=300

# MeshLog Configuration (Containerized)
DATA_DIR=/app/data  # Inside container
HOST_DATA_DIR=/data/WNC/LCM-Logs-Data  # Host mount point

# Agent Service Configuration (Containerized)
AGENT_DATA_DIR=/app/data  # Inside agent container
AGENT_HOST_DATA_DIR=/data/WNC/LCM-Logs-Data  # Host mount point (same as MeshLog)
```

### Directory Structure

```
/data/WNC/LCM-Logs-Data/  # Host mount point
└── projects/
    └── {project_id}/
        ├── extracted/                       # MeshLog extracted data
        │   └── {app_name}/
        │       └── analysis/               # MeshLog local analysis results
        └── applications/
            └── {app_name}/
                └── agent-analysis/          # Agent analysis results
                    ├── agent_report.html
                    ├── agent_data.json
                    ├── agent_data.csv
                    └── agent_metadata.json
```

## Deployment Commands

### Basic Deployment (MeshLog Only)
```bash
./deploy.sh deploy
```

### Agent Integration Deployment
```bash
./deploy.sh deploy-agent
```

### Health Check
```bash
./scripts/health-check-agent.sh
```

### Manual Agent Deployment
```bash
./scripts/deploy-agent.sh
```

## Prerequisites

### Required Projects
1. **MeshLog Project**: Current project (prplOS LCM Log Analysis System)
2. **Agent Project**: `wnc-log-agents` project in `../wnc-log-agents/` directory

### Required Tools
- Docker with Compose support
- Bash shell
- curl (for health checks)
- jq (optional, for JSON parsing)

### System Requirements
- **Disk Space**: Minimum 10GB free space for data directory
- **Memory**: Minimum 4GB RAM for all containers
- **CPU**: Minimum 2 CPU cores
- **Network**: Ports 80, 8000, 6379 available

## Security Considerations

### Container Security
- **Non-root Users**: All containers run as non-root users
- **Resource Limits**: CPU and memory limits set for all containers
- **Network Isolation**: Services communicate through private Docker network
- **Volume Permissions**: Proper permissions on shared volumes

### Data Security
- **Shared Volume**: Controlled access to shared data directory
- **No Direct Database Access**: Agents don't have direct database access
- **Input Validation**: All API inputs are validated and sanitized
- **Error Handling**: Sensitive information not exposed in error messages

## Monitoring and Debugging

### Container Logs
```bash
# Check MeshLog backend logs
docker logs prplos_backend

# Check agent service logs
docker logs wnc-log-agents

# Follow logs in real-time
docker logs -f wnc-log-agents
```

### Health Checks
```bash
# Check container status
docker ps

# Check container health
docker inspect wnc-log-agents | grep Health

# Check container resources
docker stats wnc-log-agents
```

### Network Debugging
```bash
# Test container connectivity
docker exec prplos_backend curl http://wnc-log-agents:8001/health

# Check network configuration
docker network inspect meshlog-network

# Test DNS resolution
docker exec prplos_backend nslookup wnc-log-agents
```

## Troubleshooting

### Common Issues

1. **Agent Container Not Starting**
   - Check agent project exists at `../wnc-log-agents/`
   - Verify agent project has proper Dockerfile
   - Check agent service logs: `docker logs wnc-log-agents`

2. **Network Connectivity Issues**
   - Verify all containers are on the same network
   - Check DNS resolution: `docker exec prplos_backend nslookup wnc-log-agents`
   - Test connectivity: `docker exec prplos_backend curl http://wnc-log-agents:8001/health`

3. **Volume Mount Issues**
   - Check volume permissions: `ls -la /data/WNC/LCM-Logs-Data`
   - Verify volume is mounted: `docker inspect prplos_backend | grep Mounts`
   - Check disk space: `df -h /data/WNC/LCM-Logs-Data`

4. **Agent Service Not Responding**
   - Check agent service health: `docker exec prplos_backend curl http://wnc-log-agents:8001/health`
   - Check agent service logs: `docker logs wnc-log-agents --tail 50`
   - Verify agent service is running: `docker ps | grep wnc-log-agents`

### Recovery Procedures

1. **Restart Agent Service**
   ```bash
   docker restart wnc-log-agents
   ```

2. **Rebuild Agent Service**
   ```bash
   cd ../wnc-log-agents
   docker build -t wnc-log-agents .
   docker compose -f docker-compose.yml -f docker-compose.agent.yml up -d wnc-log-agents
   ```

3. **Full System Restart**
   ```bash
   ./deploy.sh deploy-agent
   ```

## Performance Considerations

### Container Optimization
- **Multi-stage Builds**: Use multi-stage Docker builds for smaller images
- **Layer Caching**: Optimize Docker layer caching for faster builds
- **Resource Allocation**: Proper CPU and memory allocation per container

### Volume Performance
- **SSD Storage**: Use SSD storage for shared volumes when possible
- **Volume Monitoring**: Monitor volume I/O performance
- **Backup Strategies**: Implement efficient backup strategies

### Network Performance
- **Container Networking**: Use appropriate Docker network drivers
- **Connection Pooling**: Use connection pooling for HTTP clients
- **Load Balancing**: Implement load balancing for agent services

## Future Enhancements

### Planned Features
- **Kubernetes Deployment**: Full Kubernetes manifests and operators
- **Service Mesh**: Istio or Linkerd integration
- **Auto-scaling**: Horizontal pod autoscaling for agent services
- **Multi-cluster**: Cross-cluster agent analysis capabilities

### Advanced Features
- **Container Monitoring**: Prometheus and Grafana integration
- **Distributed Tracing**: Jaeger or Zipkin integration
- **Secret Management**: Kubernetes secrets or HashiCorp Vault
- **CI/CD Integration**: GitOps deployment workflows

## Summary

The containerized agent integration provides:

✅ **Complete Containerization**: All services run in Docker containers
✅ **Shared Data Access**: Seamless data sharing between MeshLog and agents
✅ **Network Isolation**: Secure communication between services
✅ **Health Monitoring**: Comprehensive health checks and monitoring
✅ **Easy Deployment**: One-command deployment with agent integration
✅ **Robust Error Handling**: Graceful degradation and error recovery
✅ **Security**: Proper container security and data protection
✅ **Scalability**: Easy to scale individual services independently
✅ **Portability**: Deploy anywhere Docker runs

The system is now ready for production deployment with full agent integration support.
