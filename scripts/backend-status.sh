#!/bin/bash

# Backend Development Status Script
# This script shows the status of backend services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="prplos-lcm-log-analysis"
BACKEND_PORT=8000
REDIS_PORT=6379
LOGS_DIR="./logs"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_service_health() {
    local port=$1
    local service=$2
    
    if nc -z localhost $port 2>/dev/null; then
        # Try to get a response
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "$service is healthy on port $port"
            return 0
        else
            log_warning "$service is running on port $port but not responding"
            return 1
        fi
    else
        log_error "$service is not running on port $port"
        return 1
    fi
}

show_backend_status() {
    echo
    log_info "=== Backend Services Status ==="
    
    # Check Redis
    if docker ps --filter "name=$PROJECT_NAME-redis" --format "table {{.Names}}\t{{.Status}}" | grep -q "$PROJECT_NAME-redis"; then
        log_success "Redis: Running"
        docker ps --filter "name=$PROJECT_NAME-redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        log_error "Redis: Not running"
    fi
    
    # Check Backend
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        log_success "Backend API: Running"
        if [ -f "$LOGS_DIR/backend.pid" ]; then
            local pid=$(cat "$LOGS_DIR/backend.pid")
            echo "  PID: $pid"
        fi
    else
        log_error "Backend API: Not running"
    fi
    
    # Check ports
    echo
    log_info "=== Port Status ==="
    check_service_health $REDIS_PORT "Redis"
    check_service_health $BACKEND_PORT "Backend API"
}

show_log_files() {
    echo
    log_info "=== Log Files ==="
    
    if [ -d "$LOGS_DIR" ]; then
        for log_file in "$LOGS_DIR"/*.log; do
            if [ -f "$log_file" ]; then
                local filename=$(basename "$log_file")
                local size=$(du -h "$log_file" | cut -f1)
                local modified=$(stat -c %y "$log_file" | cut -d' ' -f1,2)
                echo "  $filename: $size (modified: $modified)"
            fi
        done
    else
        log_warning "Logs directory not found: $LOGS_DIR"
    fi
}

show_recent_logs() {
    echo
    log_info "=== Recent Backend Logs (last 10 lines) ==="
    
    if [ -f "$LOGS_DIR/backend.log" ]; then
        tail -10 "$LOGS_DIR/backend.log" | while IFS= read -r line; do
            echo "  $line"
        done
    else
        log_warning "Backend log file not found: $LOGS_DIR/backend.log"
    fi
}

show_quick_actions() {
    echo
    log_info "=== Quick Actions ==="
    echo "  Start backend: ./scripts/backend-start.sh"
    echo "  Stop backend: ./scripts/backend-stop.sh"
    echo "  Restart backend: ./scripts/backend-restart.sh"
    echo "  View backend logs: tail -f $LOGS_DIR/backend.log"
    echo "  View Redis logs: docker logs $PROJECT_NAME-redis"
    echo "  Backend URL: http://localhost:$BACKEND_PORT"
    echo "  API Docs: http://localhost:$BACKEND_PORT/api/docs"
    echo "  Health Check: http://localhost:$BACKEND_PORT/health"
}

# Main execution
main() {
    log_info "Backend Services Status for prplOS LCM Log Analysis System"
    log_info "========================================================="
    
    show_backend_status
    show_log_files
    show_recent_logs
    show_quick_actions
}

# Run main function
main "$@"
