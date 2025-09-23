#!/bin/bash

# Frontend Development Stop Script
# This script stops only the frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
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

stop_frontend() {
    log_info "Stopping Frontend development server..."
    
    # Check if frontend is running
    if pgrep -f "vite.*dev" > /dev/null; then
        # Get PID from file
        if [ -f "$LOGS_DIR/frontend.pid" ]; then
            local pid=$(cat "$LOGS_DIR/frontend.pid")
            log_info "Stopping frontend process (PID: $pid)..."
            kill $pid 2>/dev/null || true
            
            # Wait for process to stop
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                log_warning "Force killing frontend process..."
                kill -9 $pid 2>/dev/null || true
            fi
        else
            # Kill by pattern if no PID file
            pkill -f "vite.*dev" || true
        fi
        
        # Remove PID file
        rm -f "$LOGS_DIR/frontend.pid"
        log_success "Frontend stopped"
    else
        log_warning "Frontend is not running"
    fi
}

cleanup_orphaned_processes() {
    log_info "Cleaning up orphaned processes..."
    
    # Kill any remaining vite processes
    local orphaned_vite=$(pgrep -f "vite.*dev" 2>/dev/null || true)
    if [ -n "$orphaned_vite" ]; then
        log_warning "Found orphaned vite processes, killing them..."
        echo "$orphaned_vite" | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill any remaining node processes that might be related
    local orphaned_node=$(pgrep -f "node.*vite" 2>/dev/null || true)
    if [ -n "$orphaned_node" ]; then
        log_warning "Found orphaned node processes, killing them..."
        echo "$orphaned_node" | xargs kill -9 2>/dev/null || true
    fi
}

show_status() {
    echo
    log_info "=== Frontend Services Status ==="
    
    # Check Frontend
    if pgrep -f "vite.*dev" > /dev/null; then
        log_warning "Frontend: Still running"
    else
        log_success "Frontend: Stopped"
    fi
    
    echo
    log_info "=== Quick Commands ==="
    echo "Start frontend: ./scripts/frontend-start.sh"
    echo "View logs: tail -f $LOGS_DIR/frontend.log"
    echo "Check status: ./scripts/frontend-status.sh"
}

# Main execution
main() {
    log_info "Stopping Frontend for prplOS LCM Log Analysis System"
    log_info "==================================================="
    
    # Stop services
    stop_frontend
    cleanup_orphaned_processes
    
    # Show status
    show_status
    
    log_success "Frontend stopped successfully!"
}

# Run main function
main "$@"
