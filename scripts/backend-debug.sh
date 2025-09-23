#!/bin/bash

# Simplified Backend Start Script with Detailed Error Reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
REDIS_PORT=6379
DATA_DIR="./data"
LOGS_DIR="./logs"
VENV_DIR="./venv"

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

# Main execution
main() {
    log_info "Starting Backend with Detailed Error Reporting"
    log_info "============================================="
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found. Please run the full backend-start.sh first."
        exit 1
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Create logs directory
    mkdir -p "$LOGS_DIR"
    
    # Test Python import
    log_info "Testing Python imports..."
    if python -c "import fastapi, uvicorn; print('Basic imports OK')" 2>/dev/null; then
        log_success "Basic imports successful"
    else
        log_error "Basic imports failed"
        exit 1
    fi
    
    # Test app import
    log_info "Testing app imports..."
    if python -c "import app.main; print('App import OK')" 2>/dev/null; then
        log_success "App import successful"
    else
        log_error "App import failed - check the error above"
        exit 1
    fi
    
    # Start backend with detailed output
    log_info "Starting backend server..."
    log_info "Backend will be available at: http://localhost:$BACKEND_PORT"
    log_info "Press Ctrl+C to stop"
    
    # Start backend in foreground for debugging
    python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload --log-level debug
}

# Run main function
main "$@"
