#!/bin/bash

# prplOS LCM Log Analysis System - Development Environment Stop Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="prplos-log-analysis"

# PID files
PID_DIR="./pids"
BACKEND_PID="$PID_DIR/backend.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"
REDIS_PID="$PID_DIR/redis.pid"

# Default options
CLEANUP_CONTAINERS=false

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to print help
print_help() {
    echo "prplOS LCM Log Analysis System - Development Environment Stop Script"
    echo ""
    echo "Usage:"
    echo "  $0 [-h|--help] [-c|--cleanup]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -c, --cleanup       Also remove Docker containers (not just stop them)"
    echo ""
    echo "This script stops all development services:"
    echo "  - Backend (FastAPI)"
    echo "  - Frontend (React)"
    echo "  - Redis"
    echo ""
}

# Function to check if service is running
is_service_running() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Service is running
        else
            # PID file exists but process is dead
            rm -f "$pid_file"
        fi
    fi
    return 1  # Service is not running
}

# Function to stop service
stop_service() {
    local pid_file=$1
    local service_name=$2
    local force_stop=${3:-false}
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        
        # Check if it's a Docker container
        if [[ "$pid" == docker-* ]]; then
            local container_id=${pid#docker-}
            if docker ps -q --filter id="$container_id" >/dev/null 2>&1; then
                print_status $BLUE "Stopping $service_name (Docker)..."
                docker stop "$container_id" >/dev/null 2>&1
                docker rm "$container_id" >/dev/null 2>&1
                print_status $GREEN "$service_name stopped successfully"
            else
                print_status $YELLOW "$service_name container not found"
            fi
        else
            # Regular process
            if ps -p "$pid" > /dev/null 2>&1; then
                print_status $BLUE "Stopping $service_name..."
                
                # Try graceful shutdown first
                if [ "$force_stop" = "false" ]; then
                    kill "$pid" >/dev/null 2>&1
                    
                    # Wait for process to stop gracefully
                    local wait_time=0
                    while ps -p "$pid" > /dev/null 2>&1 && [ $wait_time -lt 10 ]; do
                        sleep 1
                        wait_time=$((wait_time + 1))
                    done
                fi
                
                # Force kill if still running
                if ps -p "$pid" > /dev/null 2>&1; then
                    print_status $YELLOW "Force stopping $service_name..."
                    kill -9 "$pid" >/dev/null 2>&1
                    
                    # Wait a bit more for force kill
                    sleep 2
                fi
                
                if ! ps -p "$pid" > /dev/null 2>&1; then
                    print_status $GREEN "$service_name stopped successfully"
                else
                    print_status $RED "Failed to stop $service_name"
                fi
            else
                print_status $YELLOW "$service_name process not found"
            fi
        fi
        
        # Remove PID file
        rm -f "$pid_file"
    else
        print_status $YELLOW "$service_name PID file not found"
    fi
}

# Function to stop all services
stop_all_services() {
    print_status $PURPLE "Stopping prplOS LCM Log Analysis System Development Environment"
    
    # Stop services in reverse order (frontend -> backend -> redis)
    if is_service_running "$FRONTEND_PID" "Frontend"; then
        stop_service "$FRONTEND_PID" "Frontend"
    else
        print_status $YELLOW "Frontend is not running"
    fi
    
    if is_service_running "$BACKEND_PID" "Backend"; then
        stop_service "$BACKEND_PID" "Backend"
    else
        print_status $YELLOW "Backend is not running"
    fi
    
    if is_service_running "$REDIS_PID" "Redis"; then
        stop_service "$REDIS_PID" "Redis"
    else
        print_status $YELLOW "Redis is not running"
    fi
    
    # Clean up any remaining Docker containers
    print_status $BLUE "Cleaning up Docker containers..."
    local containers=$(docker ps -q --filter name="${PROJECT_NAME}-*" 2>/dev/null)
    if [ -n "$containers" ]; then
        echo "$containers" | xargs -r docker stop >/dev/null 2>&1
        if [ "$CLEANUP_CONTAINERS" = "true" ]; then
            echo "$containers" | xargs -r docker rm >/dev/null 2>&1
            print_status $GREEN "Docker containers stopped and removed"
        else
            print_status $GREEN "Docker containers stopped (use -c to remove them)"
        fi
    else
        print_status $YELLOW "No project containers found"
    fi
    
    # Clean up any orphaned processes
    print_status $BLUE "Checking for orphaned processes..."
    
    # Kill any uvicorn processes (multiple patterns to catch all variants)
    local orphaned_uvicorn=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || true)
    if [ -z "$orphaned_uvicorn" ]; then
        orphaned_uvicorn=$(pgrep -f "uvicorn.*main:app" 2>/dev/null || true)
    fi
    if [ -z "$orphaned_uvicorn" ]; then
        orphaned_uvicorn=$(pgrep -f "uvicorn" 2>/dev/null || true)
    fi
    if [ -n "$orphaned_uvicorn" ]; then
        print_status $YELLOW "Found orphaned backend processes, stopping them..."
        echo "$orphaned_uvicorn" | xargs -r kill -9 >/dev/null 2>&1
        sleep 1
    fi
    
    # Kill any Python processes that might be running the backend
    local orphaned_python=$(pgrep -f "python.*app.main" 2>/dev/null || true)
    if [ -z "$orphaned_python" ]; then
        orphaned_python=$(pgrep -f "python3.*app.main" 2>/dev/null || true)
    fi
    if [ -n "$orphaned_python" ]; then
        print_status $YELLOW "Found orphaned Python backend processes, stopping them..."
        echo "$orphaned_python" | xargs -r kill -9 >/dev/null 2>&1
        sleep 1
    fi
    
    # CRITICAL: Check if anything is using port 8000 and kill it
    # This catches processes that weren't found by PID file or process name
    if command -v lsof >/dev/null 2>&1; then
        local port_pids=$(lsof -ti:8000 2>/dev/null || true)
        if [ -n "$port_pids" ]; then
            print_status $YELLOW "Found processes using port 8000, force stopping..."
            echo "$port_pids" | xargs -r kill -9 >/dev/null 2>&1
            sleep 2
            # Verify port is free
            local still_using=$(lsof -ti:8000 2>/dev/null || true)
            if [ -n "$still_using" ]; then
                print_status $RED "Warning: Port 8000 still in use after kill attempt"
            else
                print_status $GREEN "Port 8000 is now free"
            fi
        fi
    elif command -v fuser >/dev/null 2>&1; then
        # Fallback to fuser if lsof is not available
        fuser -k 8000/tcp >/dev/null 2>&1 || true
        sleep 2
    fi
    
    local orphaned_frontend=$(pgrep -f "npm.*run.*dev" 2>/dev/null || true)
    if [ -n "$orphaned_frontend" ]; then
        print_status $YELLOW "Found orphaned frontend processes, stopping them..."
        echo "$orphaned_frontend" | xargs -r kill -9 >/dev/null 2>&1
    fi
    
    print_status $GREEN "All services stopped successfully!"
    print_status $CYAN "Use './dev-start.sh' to start services again"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_help
            exit 0
            ;;
        -c|--cleanup)
            CLEANUP_CONTAINERS=true
            shift
            ;;
        *)
            print_status $RED "Unknown option: $1"
            print_help
            exit 1
            ;;
    esac
done

# Main execution
stop_all_services
