#!/bin/bash

# Frontend Development Start Script
# This script starts only the frontend for debugging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=3000
BACKEND_PORT=8000
UI_DIR="./ui"
LOGS_DIR="./logs"

# Parse command line arguments
BACKGROUND=true
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--foreground)
            BACKGROUND=false
            shift
            ;;
        -b|--background)
            BACKGROUND=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -f, --foreground    Run frontend in foreground (see logs in terminal)"
            echo "  -b, --background   Run frontend in background (default)"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

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

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm is required but not installed"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

check_backend() {
    log_info "Checking backend availability..."
    
    if nc -z localhost $BACKEND_PORT 2>/dev/null; then
        if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
            log_success "Backend is available on port $BACKEND_PORT"
            return 0
        else
            log_warning "Backend is running on port $BACKEND_PORT but not responding to health check"
            return 1
        fi
    else
        log_warning "Backend is not running on port $BACKEND_PORT"
        log_info "You may want to start the backend first: ./scripts/backend-start.sh"
        return 1
    fi
}

setup_frontend() {
    log_info "Setting up frontend..."
    
    if [ ! -d "$UI_DIR" ]; then
        log_error "UI directory not found: $UI_DIR"
        exit 1
    fi
    
    cd "$UI_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_info "Installing npm dependencies..."
        npm install
    else
        log_info "npm dependencies already installed"
    fi
    
    # Check if package-lock.json is newer than node_modules
    if [ "package-lock.json" -nt "node_modules" ]; then
        log_info "package-lock.json is newer, updating dependencies..."
        npm install
    fi
    
    cd ..
    
    log_success "Frontend setup completed"
}

is_frontend_running() {
    # Check multiple patterns for Vite processes
    if pgrep -f "vite" > /dev/null || pgrep -f "npm.*dev" > /dev/null || pgrep -f "node.*vite" > /dev/null; then
        return 0
    fi
    
    # Check if port is in use
    if nc -z localhost $FRONTEND_PORT 2>/dev/null; then
        return 0
    fi
    
    return 1
}

start_frontend() {
    log_info "Starting Frontend development server..."
    
    # Check if frontend is already running
    if is_frontend_running; then
        log_warning "Frontend is already running"
        return 0
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOGS_DIR"
    
    # Set environment variables
    export VITE_HOST="0.0.0.0"
    export VITE_PORT="$FRONTEND_PORT"
    export VITE_API_URL="http://localhost:$BACKEND_PORT"
    
    if [ "$BACKGROUND" = true ]; then
        log_info "Starting frontend in BACKGROUND mode (logs in $LOGS_DIR/frontend.log)"
        
        # Start frontend in background
        cd "$UI_DIR"
        nohup npm run dev \
            > "../$LOGS_DIR/frontend.log" 2>&1 &
        
        # Save PID
        echo $! > "../$LOGS_DIR/frontend.pid"
        cd ..
        
        # Wait for frontend to be ready
        local max_attempts=30
        local attempt=1
        
        log_info "Waiting for frontend to be ready on port $FRONTEND_PORT..."
        
        while [ $attempt -le $max_attempts ]; do
            if nc -z localhost $FRONTEND_PORT 2>/dev/null; then
                log_success "Frontend is ready on port $FRONTEND_PORT"
                break
            fi
            
            log_info "Attempt $attempt/$max_attempts: Frontend not ready yet..."
            sleep 2
            attempt=$((attempt + 1))
        done
        
        if [ $attempt -gt $max_attempts ]; then
            log_error "Frontend failed to start on port $FRONTEND_PORT after $max_attempts attempts"
            log_info "Check the logs: tail -f $LOGS_DIR/frontend.log"
            exit 1
        fi
        
        log_success "Frontend started successfully"
        log_info "Frontend URL: http://localhost:$FRONTEND_PORT"
        log_info "Frontend logs: tail -f $LOGS_DIR/frontend.log"
    else
        log_info "Starting frontend in FOREGROUND mode (logs will appear in terminal)"
        log_info "Press Ctrl+C to stop the frontend"
        log_info "Frontend URL: http://localhost:$FRONTEND_PORT"
        
        # Run in foreground
        cd "$UI_DIR"
        npm run dev
    fi
}

show_status() {
    echo
    log_info "=== Frontend Services Status ==="
    
    # Check Frontend
    if is_frontend_running; then
        log_success "Frontend: Running"
        if [ -f "$LOGS_DIR/frontend.pid" ]; then
            local pid=$(cat "$LOGS_DIR/frontend.pid")
            echo "  PID: $pid"
        fi
    else
        log_error "Frontend: Not running"
    fi
    
    # Check ports
    echo
    log_info "=== Port Status ==="
    if nc -z localhost $FRONTEND_PORT 2>/dev/null; then
        log_success "Frontend port $FRONTEND_PORT: Available"
    else
        log_error "Frontend port $FRONTEND_PORT: Not available"
    fi
    
    if nc -z localhost $BACKEND_PORT 2>/dev/null; then
        log_success "Backend port $BACKEND_PORT: Available"
    else
        log_warning "Backend port $BACKEND_PORT: Not available"
    fi
    
    echo
    log_info "=== Quick Commands ==="
    echo "View frontend logs: tail -f $LOGS_DIR/frontend.log"
    echo "Stop frontend: ./scripts/frontend-stop.sh"
    echo "Restart frontend: ./scripts/frontend-restart.sh"
    echo "Start in foreground: ./scripts/frontend-start.sh -f"
    echo "Frontend URL: http://localhost:$FRONTEND_PORT"
    echo "Backend URL: http://localhost:$BACKEND_PORT"
}

# Main execution
main() {
    log_info "Starting Frontend for prplOS LCM Log Analysis System"
    log_info "==================================================="
    
    # Check dependencies
    check_dependencies
    
    # Check backend (but don't fail if not available)
    check_backend || true
    
    # Setup and start
    setup_frontend
    start_frontend
    
    # Show status only if not in foreground mode
    if [ "$BACKGROUND" = true ]; then
        show_status
        log_success "Frontend started successfully!"
        log_info "You can now access the application at: http://localhost:$FRONTEND_PORT"
    fi
}

# Run main function
main "$@"
