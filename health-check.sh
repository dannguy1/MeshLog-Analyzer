#!/bin/bash
# prplOS LCM Log Analysis System - Health Check Script

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
FRONTEND_URL="http://localhost"
BACKEND_URL="http://localhost:8000"
REDIS_HOST="localhost"
REDIS_PORT="6379"

# Functions
check_service() {
    local service_name="$1"
    local check_command="$2"
    
    if eval "$check_command" &>/dev/null; then
        echo -e "${GREEN}✅ $service_name${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name${NC}"
        return 1
    fi
}

# Main health check
echo "🔍 prplOS LCM Log Analysis System - Health Check"
echo "=============================================="

# Check Docker services
echo ""
echo "🐳 Docker Services:"
if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    echo "Docker Compose not found"
fi

echo ""
echo "🌐 Service Health:"

# Check Frontend
check_service "Frontend" "curl -f $FRONTEND_URL/health"

# Check Backend
check_service "Backend API" "curl -f $BACKEND_URL/health"

# Check Backend Projects API
check_service "Backend Projects API" "curl -f $BACKEND_URL/api/v1/projects"

# Check Redis
check_service "Redis" "redis-cli -h $REDIS_HOST -p $REDIS_PORT ping"

echo ""
echo "📊 System Resources:"

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✅ Disk Usage: ${DISK_USAGE}%${NC}"
else
    echo -e "${RED}❌ Disk Usage: ${DISK_USAGE}%${NC}"
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✅ Memory Usage: ${MEMORY_USAGE}%${NC}"
else
    echo -e "${RED}❌ Memory Usage: ${MEMORY_USAGE}%${NC}"
fi

echo ""
echo "🔗 Service URLs:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend: $BACKEND_URL"
echo "  API Docs: $BACKEND_URL/docs"
echo "  Health: $BACKEND_URL/health"

