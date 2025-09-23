#!/bin/bash

# Backend Development Restart Script
# This script stops and then starts the backend services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    log_info "Restarting Backend Services for prplOS LCM Log Analysis System"
    log_info "============================================================="
    
    # Stop services
    log_info "Stopping backend services..."
    if ! ./scripts/backend-stop.sh; then
        log_warning "Stop script had issues, but continuing with restart..."
    fi
    
    # Wait a moment for cleanup
    sleep 3
    
    # Start services
    log_info "Starting backend services..."
    if ./scripts/backend-start.sh; then
        log_success "Backend services restarted successfully!"
    else
        log_error "Failed to restart backend services"
        exit 1
    fi
}

# Run main function
main "$@"
