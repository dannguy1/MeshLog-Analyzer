#!/bin/bash

# prplOS LCM Log Analysis System - Development Environment Management Scripts
# 
# Usage:
#   ./dev-start.sh [-b|--background] [-f|--foreground] [-h|--help]
#   ./dev-stop.sh [-h|--help]
#   ./dev-restart.sh [-b|--background] [-f|--foreground] [-h|--help]
#   ./dev-status.sh [-h|--help]

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
BACKEND_PORT=8000
FRONTEND_PORT=3000
REDIS_PORT=6379

# SQLite Configuration
SQLITE_DB_PATH="./data/prplos_analysis.db"
SQLITE_DB_DIR="./data"

# Log files
LOG_DIR="./logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"
REDIS_LOG="$LOG_DIR/redis.log"

# PID files
PID_DIR="./pids"
BACKEND_PID="$PID_DIR/backend.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"
REDIS_PID="$PID_DIR/redis.pid"

# Default mode
MODE="foreground"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to print help
print_help() {
    echo "prplOS LCM Log Analysis System - Development Environment Management"
    echo ""
    echo "Usage:"
    echo "  $0 [-b|--background] [-f|--foreground] [-h|--help]"
    echo ""
    echo "Options:"
    echo "  -b, --background    Start services in background mode"
    echo "  -f, --foreground    Start services in foreground mode (default)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Start in foreground mode"
    echo "  $0 -f              # Start in foreground mode"
    echo "  $0 -b              # Start in background mode"
    echo ""
}

# Function to create necessary directories
create_directories() {
    print_status $BLUE "Creating necessary directories..."
    mkdir -p "$LOG_DIR" "$PID_DIR" "uploads" "analysis_results" "data"
    print_status $GREEN "Directories created successfully"
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

# Function to check if port is available
check_port() {
    local port=$1
    local service_name=$2
    
    # Try multiple methods to check port availability
    if command -v nc >/dev/null 2>&1; then
        nc -z localhost "$port" 2>/dev/null
    elif command -v ss >/dev/null 2>&1; then
        ss -tuln | grep ":$port " >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tuln | grep ":$port " >/dev/null 2>&1
    else
        # Fallback: try to connect with timeout
        timeout 1 bash -c "</dev/tcp/localhost/$port" 2>/dev/null
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    print_status $BLUE "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_port "$port" "$service_name"; then
            print_status $GREEN "$service_name is ready"
            return 0
        fi
        print_status $YELLOW "Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_status $RED "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to setup SQLite database
setup_sqlite() {
    print_status $BLUE "Setting up SQLite database..."
    
    # Create data directory
    mkdir -p "$SQLITE_DB_DIR"
    
    # Check if database exists and has tables
    if [ -f "$SQLITE_DB_PATH" ]; then
        # Check if database has tables
        if command -v sqlite3 >/dev/null 2>&1; then
            local table_count=$(sqlite3 "$SQLITE_DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0")
            if [ "$table_count" -gt 0 ]; then
                print_status $YELLOW "SQLite database already exists with $table_count tables"
                return 0
            fi
        fi
    fi
    
    print_status $BLUE "Creating SQLite database..."
    if source venv/bin/activate 2>/dev/null && python3 scripts/setup_sqlite.py; then
        print_status $GREEN "SQLite database created successfully"
    else
        print_status $RED "Failed to create SQLite database"
        return 1
    fi
}

# Function to start Redis
start_redis() {
    if is_service_running "$REDIS_PID" "Redis"; then
        print_status $YELLOW "Redis is already running"
        return 0
    fi
    
    print_status $BLUE "Starting Redis..."
    
    if command -v docker >/dev/null 2>&1; then
        # Use Docker if available
        # Check if container already exists
        if docker ps -aq --filter name="${PROJECT_NAME}-redis" >/dev/null 2>&1; then
            print_status $YELLOW "Redis container already exists, starting it..."
            docker start "${PROJECT_NAME}-redis" >/dev/null 2>&1
        else
            # Create new container
            docker run -d \
                --name "${PROJECT_NAME}-redis" \
                -p "$REDIS_PORT:6379" \
                redis:7-alpine >/dev/null 2>&1
        fi
        
        echo "docker-$(docker ps -q --filter name=${PROJECT_NAME}-redis)" > "$REDIS_PID"
        print_status $GREEN "Redis started successfully (Docker)"
    else
        # Use system Redis if Docker is not available
        if command -v redis-server >/dev/null 2>&1; then
            redis-server --daemonize yes --port "$REDIS_PORT" > "$REDIS_LOG" 2>&1
            echo $(pgrep redis-server | head -1) > "$REDIS_PID"
            print_status $GREEN "Redis started successfully (System)"
        else
            print_status $RED "Redis not found. Please install Redis or Docker."
            return 1
        fi
    fi
    
    # Wait for Redis to be ready
    if ! wait_for_service "$REDIS_PORT" "Redis"; then
        return 1
    fi
}

# Function to start backend
start_backend() {
    if is_service_running "$BACKEND_PID" "Backend"; then
        print_status $YELLOW "Backend is already running"
        return 0
    fi
    
    print_status $BLUE "Starting Backend (FastAPI)..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status $YELLOW "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    if ! source venv/bin/activate 2>/dev/null; then
        print_status $RED "Failed to activate virtual environment"
        return 1
    fi
    
    print_status $BLUE "Installing/updating dependencies..."
    pip install -r requirements.txt >/dev/null 2>&1
    
    # Set environment variables
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export DATABASE_URL="sqlite:///./data/prplos_analysis.db"
    export REDIS_URL="redis://localhost:$REDIS_PORT/0"
    export ENVIRONMENT="development"
    export DEBUG="true"
    
    if [ "$MODE" = "background" ]; then
        # Start in background
        nohup uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" > "$BACKEND_LOG" 2>&1 &
        echo $! > "$BACKEND_PID"
        print_status $GREEN "Backend started successfully in background mode"
        
        # Wait for backend to be ready
        if ! wait_for_service "$BACKEND_PORT" "Backend"; then
            print_status $RED "Backend failed to start properly"
            return 1
        fi
    else
        # Start in foreground
        print_status $GREEN "Starting Backend in foreground mode..."
        print_status $CYAN "Backend will be available at: http://localhost:$BACKEND_PORT"
        print_status $CYAN "API documentation: http://localhost:$BACKEND_PORT/docs"
        print_status $YELLOW "Press Ctrl+C to stop the backend"
        
        uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT"
    fi
}

# Function to start frontend
start_frontend() {
    if is_service_running "$FRONTEND_PID" "Frontend"; then
        print_status $YELLOW "Frontend is already running"
        return 0
    fi
    
    print_status $BLUE "Starting Frontend (React)..."
    
    # Check if ui directory exists
    if [ ! -d "ui" ]; then
        print_status $RED "Frontend directory 'ui' not found"
        return 1
    fi
    
    # Check if node_modules exists
    if [ ! -d "ui/node_modules" ]; then
        print_status $YELLOW "Installing frontend dependencies..."
        cd ui && npm install >/dev/null 2>&1 && cd ..
    fi
    
    if [ "$MODE" = "background" ]; then
        # Start in background
        cd ui
        # Set environment variables for external access
        export VITE_HOST="0.0.0.0"
        export VITE_PORT="$FRONTEND_PORT"
        nohup npm run dev > "../$FRONTEND_LOG" 2>&1 &
        echo $! > "../$FRONTEND_PID"
        cd ..
        print_status $GREEN "Frontend started successfully in background mode"
        
        # Wait for frontend to be ready
        if ! wait_for_service "$FRONTEND_PORT" "Frontend"; then
            print_status $YELLOW "Frontend may still be starting up..."
        fi
    else
        # Start in foreground
        print_status $GREEN "Starting Frontend in foreground mode..."
        print_status $CYAN "Frontend will be available at: http://0.0.0.0:$FRONTEND_PORT"
        print_status $YELLOW "Press Ctrl+C to stop the frontend"
        
        cd ui
        # Set environment variables for external access
        export VITE_HOST="0.0.0.0"
        export VITE_PORT="$FRONTEND_PORT"
        npm run dev
    fi
}

# Function to start all services
start_all_services() {
    print_status $PURPLE "Starting prplOS LCM Log Analysis System Development Environment"
    print_status $BLUE "Mode: $MODE"
    
    create_directories
    
    # Setup SQLite database
    if ! setup_sqlite; then
        print_status $RED "Failed to setup SQLite database"
        exit 1
    fi
    
    # Start Redis first
    if ! start_redis; then
        print_status $RED "Failed to start Redis"
        exit 1
    fi
    
    if [ "$MODE" = "background" ]; then
        # Start backend
        if ! start_backend; then
            print_status $RED "Failed to start backend"
            exit 1
        fi
        
        # Start frontend
        if ! start_frontend; then
            print_status $RED "Failed to start frontend"
            exit 1
        fi
        
        print_status $GREEN "All services started successfully!"
        print_status $CYAN "Backend API: http://0.0.0.0:$BACKEND_PORT"
        print_status $CYAN "API Docs: http://0.0.0.0:$BACKEND_PORT/docs"
        print_status $CYAN "Frontend: http://0.0.0.0:$FRONTEND_PORT"
        print_status $CYAN "Redis: localhost:$REDIS_PORT"
        print_status $YELLOW "Use './dev-status.sh' to check service status"
        print_status $YELLOW "Use './dev-stop.sh' to stop all services"
    else
        # Foreground mode - start backend (this will block)
        print_status $GREEN "Starting Backend in foreground mode..."
        print_status $CYAN "Backend API: http://0.0.0.0:$BACKEND_PORT"
        print_status $CYAN "API Docs: http://0.0.0.0:$BACKEND_PORT/docs"
        print_status $YELLOW "To start frontend, open a new terminal and run: cd ui && npm run dev"
        print_status $YELLOW "Frontend will be available at: http://0.0.0.0:$FRONTEND_PORT"
        print_status $YELLOW "Press Ctrl+C to stop the backend"
        
        start_backend
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--background)
            MODE="background"
            shift
            ;;
        -f|--foreground)
            MODE="foreground"
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            print_status $RED "Unknown option: $1"
            print_help
            exit 1
            ;;
    esac
done

# Main execution
start_all_services
