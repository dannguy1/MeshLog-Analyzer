
#!/bin/bash

# Backend Development Start Script
# This script starts only the backend services for debugging

set -e

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
# DATA_DIR is now loaded from .env file via the configuration system
LOGS_DIR="./logs"
VENV_DIR="./venv"

# Load DATA_DIR from configuration
load_data_dir() {
    # Try to load from .env file first
    if [ -f ".env" ]; then
        DATA_DIR=$(grep "^DATA_DIR=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    fi
    
    # Fallback to default if not found
    if [ -z "$DATA_DIR" ]; then
        DATA_DIR="./data"
    fi
    
    log_info "Using DATA_DIR: $DATA_DIR"
}

# Parse command line arguments
FOREGROUND=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--foreground)
            FOREGROUND=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -f, --foreground    Run backend in foreground (see logs in terminal)"
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

check_port() {
    local port=$1
    local service=$2
    
    if nc -z localhost $port 2>/dev/null; then
        log_warning "Port $port is already in use by $service"
        return 1
    else
        log_info "Port $port is available"
        return 0
    fi
}

wait_for_service() {
    local port=$1
    local service=$2
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for $service to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            log_success "$service is ready on port $port"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: $service not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "$service failed to start on port $port after $max_attempts attempts"
    return 1
}

setup_directories() {
    log_info "Setting up directories..."
    
    # Load DATA_DIR from configuration
    load_data_dir
    
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$DATA_DIR/extracted"
    mkdir -p "$DATA_DIR/uploads"
    
    log_success "Directories created"
}

setup_virtual_environment() {
    log_info "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    log_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    log_info "Installing/updating Python dependencies..."
    pip install --upgrade pip
    pip install --upgrade setuptools wheel
    
    # Try minimal requirements first
    if pip install -r requirements-minimal.txt; then
        log_success "Minimal dependencies installed successfully"
    else
        log_warning "Minimal dependencies failed, trying core packages individually..."
        pip install fastapi uvicorn pydantic pydantic-settings redis pandas numpy plotly python-multipart python-dotenv pyyaml structlog fastapi-cors websockets httpx aiofiles python-dateutil pytz scikit-learn joblib matplotlib seaborn
    fi
    
    log_success "Virtual environment ready"
}

setup_sqlite() {
    log_info "Setting up SQLite database..."
    
    source "$VENV_DIR/bin/activate"
    
    # Check if database exists
    if [ ! -f "$DATA_DIR/prplos_analysis.db" ]; then
        log_info "Creating new SQLite database..."
        sqlite3 "$DATA_DIR/prplos_analysis.db" < scripts/sqlite_schema_fixed.sql
    else
        log_info "SQLite database already exists"
    fi
    
    log_success "SQLite database ready"
}

cleanup_existing_processes() {
    log_info "Checking for existing processes..."
    
    # Check if anything is using the backend port
    local port_process=$(lsof -ti:$BACKEND_PORT 2>/dev/null || true)
    if [ -n "$port_process" ]; then
        log_warning "Found process using port $BACKEND_PORT: $port_process"
        log_info "Attempting to stop existing process..."
        echo "$port_process" | xargs kill -9 2>/dev/null || true
        sleep 3
    fi
    
    # Check for any orphaned uvicorn processes
    local orphaned_uvicorn=$(pgrep -f "uvicorn.*main:app" 2>/dev/null || true)
    if [ -n "$orphaned_uvicorn" ]; then
        log_warning "Found orphaned uvicorn processes, cleaning up..."
        echo "$orphaned_uvicorn" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Check for multiprocessing child processes
    local orphaned_multiprocessing=$(pgrep -f "multiprocessing.spawn" 2>/dev/null || true)
    if [ -n "$orphaned_multiprocessing" ]; then
        log_warning "Found orphaned multiprocessing processes, cleaning up..."
        echo "$orphaned_multiprocessing" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    log_success "Process cleanup completed"
}

start_redis() {
    log_info "Starting Redis..."
    
    # Check if Redis container exists
    if docker ps -aq --filter "name=$PROJECT_NAME-redis" | grep -q .; then
        log_info "Redis container exists, starting it..."
        docker start "$PROJECT_NAME-redis" 2>/dev/null || true
    else
        log_info "Creating new Redis container..."
        docker run -d \
            --name "$PROJECT_NAME-redis" \
            -p $REDIS_PORT:6379 \
            redis:7-alpine \
            redis-server --appendonly yes
    fi
    
    # Wait for Redis to be ready
    if wait_for_service $REDIS_PORT "Redis"; then
        log_success "Redis started successfully"
    else
        log_error "Failed to start Redis"
        exit 1
    fi
}

start_backend() {
    log_info "Starting Backend API server..."
    
    # Check if backend is already running
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        log_warning "Backend is already running"
        return 0
    fi
    
    # Check if port is available
    if ! check_port $BACKEND_PORT "Backend API"; then
        log_error "Port $BACKEND_PORT is not available. Please stop any services using this port first."
        log_info "You can run: ./scripts/backend-stop.sh to stop the backend"
        exit 1
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Set environment variables
    export PYTHONPATH="$PWD"
    export DATA_DIR="$DATA_DIR"
    export LOGS_DIR="$LOGS_DIR"
    
    if [ "$FOREGROUND" = true ]; then
        log_info "Starting backend in FOREGROUND mode (logs will appear in terminal)"
        log_info "Press Ctrl+C to stop the backend"
        log_info "Backend URL: http://localhost:$BACKEND_PORT"
        log_info "API Docs: http://localhost:$BACKEND_PORT/api/docs"
        
        # Run in foreground
        uvicorn app.main:app \
            --host 0.0.0.0 \
            --port $BACKEND_PORT \
            --reload \
            --reload-exclude "ui/*" \
            --log-level info
    else
        log_info "Starting backend in BACKGROUND mode (logs in $LOGS_DIR/backend.log)"
        
        # Start backend in background
        nohup uvicorn app.main:app \
            --host 0.0.0.0 \
            --port $BACKEND_PORT \
            --reload \
            --reload-exclude "ui/*" \
            --log-level info \
            > "$LOGS_DIR/backend.log" 2>&1 &
        
        # Save PID
        echo $! > "$LOGS_DIR/backend.pid"
        
        # Wait for backend to be ready
        if wait_for_service $BACKEND_PORT "Backend API"; then
            log_success "Backend API started successfully"
            log_info "Backend logs: tail -f $LOGS_DIR/backend.log"
            log_info "Backend URL: http://localhost:$BACKEND_PORT"
            log_info "API Docs: http://localhost:$BACKEND_PORT/api/docs"
        else
            log_error "Failed to start Backend API"
            exit 1
        fi
    fi
}

show_status() {
    echo
    log_info "=== Backend Services Status ==="
    
    # Check Redis
    if docker ps --filter "name=$PROJECT_NAME-redis" --format "table {{.Names}}\t{{.Status}}" | grep -q "$PROJECT_NAME-redis"; then
        log_success "Redis: Running (Docker container)"
    elif nc -z localhost $REDIS_PORT 2>/dev/null && redis-cli ping >/dev/null 2>&1; then
        log_success "Redis: Running (system service)"
    else
        log_error "Redis: Not running"
    fi
    
    # Check Backend
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        log_success "Backend API: Running"
    else
        log_error "Backend API: Not running"
    fi
    
    # Check ports
    echo
    log_info "=== Port Status ==="
    if nc -z localhost $REDIS_PORT 2>/dev/null; then
        log_success "Redis port $REDIS_PORT: Available"
    else
        log_error "Redis port $REDIS_PORT: Not available"
    fi
    
    if nc -z localhost $BACKEND_PORT 2>/dev/null; then
        log_success "Backend port $BACKEND_PORT: Available"
    else
        log_error "Backend port $BACKEND_PORT: Not available"
    fi
    
    echo
    log_info "=== Quick Commands ==="
    echo "View backend logs: tail -f $LOGS_DIR/backend.log"
    echo "View Redis logs: docker logs $PROJECT_NAME-redis"
    echo "Stop backend: ./scripts/backend-stop.sh"
    echo "Restart backend: ./scripts/backend-restart.sh"
    echo "Start in foreground: ./scripts/backend-start.sh -f"
}

# Main execution
main() {
    log_info "Starting Backend Services for prplOS LCM Log Analysis System"
    log_info "=========================================================="
    
    # Check dependencies
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is required but not installed"
        exit 1
    fi
    
    if ! command -v nc &> /dev/null; then
        log_error "netcat (nc) is required but not installed"
        exit 1
    fi
    
    # Setup
    setup_directories
    setup_virtual_environment
    setup_sqlite
    
    # Cleanup existing processes
    cleanup_existing_processes
    
    # Start services
    start_redis
    start_backend
    
    # Show status only if not in foreground mode
    if [ "$FOREGROUND" = false ]; then
        show_status
        log_success "Backend services started successfully!"
        log_info "You can now start the frontend with: ./scripts/frontend-start.sh"
    fi
}

# Run main function
main "$@"
