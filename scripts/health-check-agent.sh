#!/bin/bash
# health-check-agent.sh - Check agent integration health

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DATA_DIR="/data/WNC/LCM-Logs-Data"

echo -e "${BLUE}🔍 Checking Agent Integration Health...${NC}"
echo ""

# Check containers
echo -e "${BLUE}📦 Container Status:${NC}"
docker compose ps
echo ""

# Check if agent container is running
if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "wnc-log-agents.*Up"; then
    echo -e "${GREEN}✅ Agent container is running${NC}"
else
    echo -e "${RED}❌ Agent container is not running${NC}"
fi

# Check agent service health
echo -e "${BLUE}🤖 Agent Service Health:${NC}"
if docker exec prplos_backend curl -f http://wnc-log-agents:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Agent service is healthy${NC}"
    
    # Get detailed health info
    echo -e "${BLUE}📊 Agent service details:${NC}"
    docker exec prplos_backend curl -s http://wnc-log-agents:8001/health | jq . 2>/dev/null || echo "Health endpoint response received"
else
    echo -e "${RED}❌ Agent service is not healthy${NC}"
    echo -e "${YELLOW}📝 Agent service logs (last 10 lines):${NC}"
    docker logs wnc-log-agents --tail 10
fi
echo ""

# Check shared volume
echo -e "${BLUE}💾 Shared Volume Status:${NC}"
if [ -d "$DATA_DIR" ]; then
    echo -e "${GREEN}✅ Shared volume is mounted at $DATA_DIR${NC}"
    echo -e "${BLUE}📊 Volume usage:${NC}"
    df -h "$DATA_DIR"
    
    # Check if agent analysis directories exist
    if [ -d "$DATA_DIR/projects" ]; then
        echo -e "${GREEN}✅ Projects directory exists${NC}"
        project_count=$(find "$DATA_DIR/projects" -maxdepth 1 -type d | wc -l)
        echo -e "${BLUE}📁 Number of projects: $((project_count - 1))${NC}"
    else
        echo -e "${YELLOW}⚠️  Projects directory does not exist yet${NC}"
    fi
else
    echo -e "${RED}❌ Shared volume is not mounted${NC}"
fi
echo ""

# Check network connectivity
echo -e "${BLUE}🌐 Network Connectivity:${NC}"
if docker exec prplos_backend ping -c 1 wnc-log-agents > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Network connectivity is working${NC}"
else
    echo -e "${RED}❌ Network connectivity issues${NC}"
fi

# Check if containers can resolve each other
if docker exec prplos_backend nslookup wnc-log-agents > /dev/null 2>&1; then
    echo -e "${GREEN}✅ DNS resolution is working${NC}"
else
    echo -e "${RED}❌ DNS resolution issues${NC}"
fi
echo ""

# Check Redis connectivity (shared by both services)
echo -e "${BLUE}🔴 Redis Connectivity:${NC}"
if docker exec prplos_backend redis-cli -h redis ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is accessible from MeshLog backend${NC}"
else
    echo -e "${RED}❌ Redis is not accessible from MeshLog backend${NC}"
fi

if docker exec wnc-log-agents redis-cli -h redis ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is accessible from agent service${NC}"
else
    echo -e "${RED}❌ Redis is not accessible from agent service${NC}"
fi
echo ""

# Check container resource usage
echo -e "${BLUE}📊 Container Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" prplos_backend wnc-log-agents prplos_redis
echo ""

# Check for any error logs
echo -e "${BLUE}🔍 Recent Error Logs:${NC}"
echo -e "${YELLOW}Backend errors (last 5):${NC}"
docker logs prplos_backend --tail 100 | grep -i error | tail -5 || echo "No recent backend errors"

echo -e "${YELLOW}Agent service errors (last 5):${NC}"
docker logs wnc-log-agents --tail 100 | grep -i error | tail -5 || echo "No recent agent errors"
echo ""

# Test agent analysis API endpoint
echo -e "${BLUE}🧪 Testing Agent Analysis API:${NC}"
if docker exec prplos_backend curl -f http://localhost:8000/api/v1/projects > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MeshLog API is accessible${NC}"
    
    # Try to get projects list
    project_count=$(docker exec prplos_backend curl -s http://localhost:8000/api/v1/projects | jq '.projects | length' 2>/dev/null || echo "0")
    echo -e "${BLUE}📁 Available projects: $project_count${NC}"
else
    echo -e "${RED}❌ MeshLog API is not accessible${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}📋 Health Check Summary:${NC}"
healthy_containers=$(docker ps --format "{{.Names}}" | grep -E "(prplos_|wnc-log-agents)" | wc -l)
total_containers=6  # backend, frontend, redis, celery_worker, celery_beat, wnc-log-agents

if [ "$healthy_containers" -eq "$total_containers" ]; then
    echo -e "${GREEN}✅ All containers are running ($healthy_containers/$total_containers)${NC}"
else
    echo -e "${YELLOW}⚠️  Some containers may not be running ($healthy_containers/$total_containers)${NC}"
fi

echo -e "${BLUE}🏁 Health check completed${NC}"
