#!/bin/bash
# deploy-agent.sh - Deploy MeshLog with Agent Integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DATA_DIR="/data/WNC/LCM-Logs-Data"
AGENT_PROJECT_PATH="../wnc-log-agents"  # Adjust path as needed

echo -e "${BLUE}🚀 Deploying MeshLog with Agent Integration...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if agent project exists
if [ ! -d "$AGENT_PROJECT_PATH" ]; then
    echo -e "${YELLOW}⚠️  Agent project not found at $AGENT_PROJECT_PATH${NC}"
    echo -e "${YELLOW}   Please ensure the wnc-log-agents project is in the correct location${NC}"
    echo -e "${YELLOW}   You can also modify the AGENT_PROJECT_PATH variable in this script${NC}"
    exit 1
fi

# Create data directory if it doesn't exist
echo -e "${BLUE}📁 Creating data directory...${NC}"
sudo mkdir -p "$DATA_DIR"

# Set proper permissions
echo -e "${BLUE}🔐 Setting permissions...${NC}"
sudo chown -R 1000:1000 "$DATA_DIR"

# Build agent service image
echo -e "${BLUE}📦 Building agent service image...${NC}"
cd "$AGENT_PROJECT_PATH"
docker build -t wnc-log-agents .
cd - > /dev/null

# Deploy with agent integration
echo -e "${BLUE}🐳 Starting containers with agent integration...${NC}"
docker compose -f docker-compose.yml -f docker-compose.agent.yml up -d

# Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
sleep 15

# Check service health
echo -e "${BLUE}🔍 Checking service health...${NC}"
docker compose ps

# Test agent connectivity
echo -e "${BLUE}🧪 Testing agent connectivity...${NC}"
max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker exec prplos_backend curl -f http://wnc-log-agents:8001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Agent service is healthy and accessible${NC}"
        break
    else
        echo -e "${YELLOW}⏳ Attempt $attempt/$max_attempts: Agent service not ready yet...${NC}"
        sleep 5
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo -e "${RED}❌ Agent service is not accessible after $max_attempts attempts${NC}"
    echo -e "${YELLOW}   Checking agent service logs...${NC}"
    docker logs wnc-log-agents --tail 20
    exit 1
fi

# Test MeshLog backend connectivity to agent
echo -e "${BLUE}🧪 Testing MeshLog backend to agent connectivity...${NC}"
if docker exec prplos_backend curl -f http://wnc-log-agents:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MeshLog backend can communicate with agent service${NC}"
else
    echo -e "${RED}❌ MeshLog backend cannot communicate with agent service${NC}"
    exit 1
fi

# Check shared volume
echo -e "${BLUE}💾 Checking shared volume...${NC}"
if [ -d "$DATA_DIR" ]; then
    echo -e "${GREEN}✅ Shared volume is mounted at $DATA_DIR${NC}"
    echo -e "${BLUE}📊 Volume usage:${NC}"
    df -h "$DATA_DIR"
else
    echo -e "${RED}❌ Shared volume is not mounted${NC}"
    exit 1
fi

# Final status check
echo -e "${BLUE}🔍 Final service status:${NC}"
docker compose ps

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}📊 Access MeshLog at: http://localhost${NC}"
echo -e "${GREEN}🔧 Agent service available internally at: http://wnc-log-agents:8001${NC}"
echo -e "${BLUE}📝 To view logs: docker logs wnc-log-agents${NC}"
echo -e "${BLUE}📝 To stop services: docker compose -f docker-compose.yml -f docker-compose.agent.yml down${NC}"
