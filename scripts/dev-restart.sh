#!/bin/bash

# prplOS LCM Log Analysis System - Development Environment Restart Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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
    echo "prplOS LCM Log Analysis System - Development Environment Restart Script"
    echo ""
    echo "Usage:"
    echo "  $0 [-b|--background] [-f|--foreground] [-h|--help]"
    echo ""
    echo "Options:"
    echo "  -b, --background    Restart services in background mode"
    echo "  -f, --foreground   Restart services in foreground mode (default)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Restart in foreground mode"
    echo "  $0 -f              # Restart in foreground mode"
    echo "  $0 -b              # Restart in background mode"
    echo ""
}

# Function to restart services
restart_services() {
    print_status $PURPLE "Restarting prplOS LCM Log Analysis System Development Environment"
    print_status $BLUE "Mode: $MODE"
    
    # Stop all services first
    print_status $BLUE "Stopping all services..."
    ./dev-stop.sh
    
    # Wait a moment for services to fully stop
    sleep 2
    
    # Start services in the specified mode
    print_status $BLUE "Starting services in $MODE mode..."
    if [ "$MODE" = "background" ]; then
        ./dev-start.sh -b
    else
        ./dev-start.sh -f
    fi
    
    print_status $GREEN "Restart completed successfully!"
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
restart_services
