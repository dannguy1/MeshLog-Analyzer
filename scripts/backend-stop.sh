#!/bin/bash

# Backend Development Stop Script
# This script stops only the backend services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="prplos-lcm-log-analysis"
LOGS_DIR="./logs"
BACKEND_PORT=8000

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

stop_backend() {
    log_info "Stopping Backend API server..."
    
    # First, check if anything is using the port
    local port_process=$(lsof -ti:$BACKEND_PORT 2>/dev/null || true)
    if [ -n "$port_process" ]; then
        log_info "Found process using port $BACKEND_PORT: $port_process"
        echo "$port_process" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Check if backend is running by process name
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        # Get PID from file
        if [ -f "$LOGS_DIR/backend.pid" ]; then
            local pid=$(cat "$LOGS_DIR/backend.pid")
            log_info "Stopping backend process (PID: $pid)..."
            kill $pid 2>/dev/null || true
            
            # Wait for process to stop
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                log_warning "Force killing backend process..."
                kill -9 $pid 2>/dev/null || true
            fi
        else
            # Kill by pattern if no PID file
            pkill -f "uvicorn.*main:app" || true
        fi
        
        # Remove PID file
        rm -f "$LOGS_DIR/backend.pid"
        log_success "Backend API stopped"
    else
        log_warning "Backend API is not running"
    fi
}

stop_redis() {
    log_info "Stopping Redis..."
    
    if docker ps --filter "name=$PROJECT_NAME-redis" --format "{{.Names}}" | grep -q "$PROJECT_NAME-redis"; then
        log_info "Stopping Redis container..."
        docker stop "$PROJECT_NAME-redis" 2>/dev/null || true
        log_success "Redis stopped"
    else
        log_warning "Redis container is not running"
    fi
}

cleanup_orphaned_processes() {
    log_info "Cleaning up orphaned processes..."
    
    # Kill any remaining uvicorn processes
    local orphaned_uvicorn=$(pgrep -f "uvicorn.*main:app" 2>/dev/null || true)
    if [ -n "$orphaned_uvicorn" ]; then
        log_warning "Found orphaned uvicorn processes, killing them..."
        echo "$orphaned_uvicorn" | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill any remaining Python processes that might be related
    local orphaned_python=$(pgrep -f "python.*app.main" 2>/dev/null || true)
    if [ -n "$orphaned_python" ]; then
        log_warning "Found orphaned Python processes, killing them..."
        echo "$orphaned_python" | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill any multiprocessing child processes
    local orphaned_multiprocessing=$(pgrep -f "multiprocessing.spawn" 2>/dev/null || true)
    if [ -n "$orphaned_multiprocessing" ]; then
        log_warning "Found orphaned multiprocessing processes, killing them..."
        echo "$orphaned_multiprocessing" | xargs kill -9 2>/dev/null || true
    fi
    
    # Final check: kill anything still using the port
    local final_port_process=$(lsof -ti:$BACKEND_PORT 2>/dev/null || true)
    if [ -n "$final_port_process" ]; then
        log_warning "Found processes still using port $BACKEND_PORT, force killing..."
        echo "$final_port_process" | xargs kill -9 2>/dev/null || true
    fi
}

show_status() {
    echo
    log_info "=== Backend Services Status ==="
    
    # Check Redis
    if docker ps --filter "name=$PROJECT_NAME-redis" --format "table {{.Names}}\t{{.Status}}" | grep -q "$PROJECT_NAME-redis"; then
        log_warning "Redis: Still running"
    else
        log_success "Redis: Stopped"
    fi
    
    # Check Backend
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        log_warning "Backend API: Still running"
    else
        log_success "Backend API: Stopped"
    fi
    
    # Check port
    if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
        log_warning "Port $BACKEND_PORT: Still in use"
    else
        log_success "Port $BACKEND_PORT: Available"
    fi
    
    echo
    log_info "=== Quick Commands ==="
    echo "Start backend: ./scripts/backend-start.sh"
    echo "View logs: tail -f $LOGS_DIR/backend.log"
    echo "Check status: ./scripts/backend-status.sh"
}

# Main execution
main() {
    log_info "Stopping Backend Services for prplOS LCM Log Analysis System"
    log_info "==========================================================="
    
    # Stop services
    stop_backend
    stop_redis
    cleanup_orphaned_processes
    
    # Show status
    show_status
    
    log_success "Backend services stopped successfully!"
}

# Run main function
main "$@"
