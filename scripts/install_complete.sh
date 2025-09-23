#!/bin/bash

# prplOS LCM Log Analysis System - Complete Installation Script
# This script sets up the complete development environment with all fixes

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
FRONTEND_PORT=3000
REDIS_PORT=6379
DATA_DIR="./data"
LOGS_DIR="./logs"
VENV_DIR="./venv"
UI_DIR="./ui"

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
    log_info "Checking system dependencies..."
    
    # Check for required system packages
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("pip3")
    fi
    
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v nc &> /dev/null; then
        missing_deps+=("netcat")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing system dependencies: ${missing_deps[*]}"
        log_info "Please install the missing dependencies and run this script again."
        log_info "On Ubuntu/Debian: sudo apt-get install python3 python3-pip nodejs npm docker.io netcat"
        log_info "On CentOS/RHEL: sudo yum install python3 python3-pip nodejs npm docker netcat"
        exit 1
    fi
    
    log_success "All system dependencies are available"
}

setup_directories() {
    log_info "Setting up project directories..."
    
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$DATA_DIR/extracted"
    mkdir -p "$DATA_DIR/uploads"
    mkdir -p "$LOGS_DIR"
    
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
    
    log_info "Upgrading pip and setuptools..."
    pip install --upgrade pip setuptools wheel
    
    log_success "Virtual environment ready"
}

install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    source "$VENV_DIR/bin/activate"
    
    # Install minimal requirements first
    if pip install -r requirements-minimal.txt; then
        log_success "Minimal dependencies installed successfully"
    else
        log_warning "Minimal dependencies failed, trying core packages individually..."
        pip install fastapi uvicorn pydantic pydantic-settings redis pandas numpy plotly python-multipart python-dotenv pyyaml structlog fastapi-cors websockets httpx aiofiles python-dateutil pytz scikit-learn joblib matplotlib seaborn
    fi
    
    # Install additional dependencies
    log_info "Installing additional dependencies..."
    pip install matplotlib seaborn
    
    log_success "Python dependencies installed"
}

setup_database() {
    log_info "Setting up SQLite database..."
    
    source "$VENV_DIR/bin/activate"
    
    # Remove existing database if it exists
    if [ -f "$DATA_DIR/prplos_analysis.db" ]; then
        log_info "Removing existing database..."
        rm -f "$DATA_DIR/prplos_analysis.db"
    fi
    
    # Create database using the fixed schema
    log_info "Creating database with schema..."
    sqlite3 "$DATA_DIR/prplos_analysis.db" < scripts/sqlite_schema_fixed.sql
    
    log_success "Database setup completed"
}

setup_frontend() {
    log_info "Setting up frontend dependencies..."
    
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

create_startup_scripts() {
    log_info "Creating startup scripts..."
    
    # Make all scripts executable
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x install.sh quick_setup.sh 2>/dev/null || true
    
    log_success "Startup scripts created"
}

test_backend() {
    log_info "Testing backend startup..."
    
    source "$VENV_DIR/bin/activate"
    
    # Test import
    if python -c "import app.main; print('Backend import successful')" 2>/dev/null; then
        log_success "Backend imports successful"
    else
        log_error "Backend import failed"
        return 1
    fi
    
    # Test minimal app
    if python -c "import app.main_minimal; print('Minimal app import successful')" 2>/dev/null; then
        log_success "Minimal app imports successful"
    else
        log_warning "Minimal app import failed"
    fi
    
    log_success "Backend test completed"
}

show_installation_summary() {
    echo
    log_info "=== Installation Summary ==="
    
    # Check Python environment
    if [ -d "$VENV_DIR" ]; then
        log_success "Python virtual environment: ✓"
    else
        log_error "Python virtual environment: ✗"
    fi
    
    # Check database
    if [ -f "$DATA_DIR/prplos_analysis.db" ]; then
        log_success "SQLite database: ✓"
        local db_size=$(du -h "$DATA_DIR/prplos_analysis.db" | cut -f1)
        echo "  Size: $db_size"
    else
        log_error "SQLite database: ✗"
    fi
    
    # Check frontend
    if [ -d "$UI_DIR/node_modules" ]; then
        log_success "Frontend dependencies: ✓"
    else
        log_error "Frontend dependencies: ✗"
    fi
    
    # Check directories
    if [ -d "$DATA_DIR" ] && [ -d "$LOGS_DIR" ]; then
        log_success "Project directories: ✓"
    else
        log_error "Project directories: ✗"
    fi
    
    echo
    log_info "=== Quick Start Commands ==="
    echo "Start backend: ./scripts/backend-start.sh"
    echo "Start frontend: ./scripts/frontend-start.sh"
    echo "Start both: ./dev-start.sh"
    echo "Stop all: ./dev-stop.sh"
    echo "Check status: ./dev-status.sh"
    echo "Clean up: ./scripts/cleanup.sh"
    
    echo
    log_info "=== Access URLs ==="
    echo "Frontend: http://localhost:$FRONTEND_PORT"
    echo "Backend API: http://localhost:$BACKEND_PORT"
    echo "API Docs: http://localhost:$BACKEND_PORT/api/docs"
    echo "Health Check: http://localhost:$BACKEND_PORT/health"
    
    echo
    log_info "=== Troubleshooting ==="
    echo "If backend fails to start: ./quick_setup.sh"
    echo "If database issues: rm -f data/prplos_analysis.db && sqlite3 data/prplos_analysis.db < scripts/sqlite_schema_fixed.sql"
    echo "If frontend issues: cd ui && npm install"
}

# Main execution
main() {
    log_info "🚀 prplOS LCM Log Analysis System - Complete Installation"
    log_info "========================================================="
    
    # Check dependencies
    check_dependencies
    
    # Setup
    setup_directories
    setup_virtual_environment
    install_python_dependencies
    setup_database
    setup_frontend
    create_startup_scripts
    
    # Test
    test_backend
    
    # Show summary
    show_installation_summary
    
    log_success "🎉 Installation completed successfully!"
    log_info "You can now start the application with: ./scripts/backend-start.sh"
}

# Run main function
main "$@"
