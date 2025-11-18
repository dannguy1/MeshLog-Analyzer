#!/bin/bash

# prplOS LCM Log Analysis System - Development Environment Restart Script

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of scripts directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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
    
    # Change to project root directory (scripts expect to be run from project root)
    cd "$PROJECT_ROOT" || {
        print_status $RED "Failed to change to project root directory: $PROJECT_ROOT"
        exit 1
    }
    
    # Stop all services first
    print_status $BLUE "Stopping all services..."
    "$SCRIPT_DIR/dev-stop.sh"
    
    # Wait for services to fully stop and verify port 8000 is free
    print_status $BLUE "Waiting for services to fully stop..."
    sleep 3
    
    # Verify port 8000 is free before starting (critical for restart)
    if command -v lsof >/dev/null 2>&1; then
        local port_check=0
        local max_port_checks=10
        while [ $port_check -lt $max_port_checks ]; do
            local port_pids=$(lsof -ti:8000 2>/dev/null || true)
            if [ -z "$port_pids" ]; then
                print_status $GREEN "Port 8000 is free, ready to start backend"
                break
            else
                print_status $YELLOW "Port 8000 still in use (check $((port_check + 1))/$max_port_checks), waiting..."
                sleep 1
                port_check=$((port_check + 1))
                # If still in use after multiple checks, force kill
                if [ $port_check -eq $max_port_checks ]; then
                    print_status $YELLOW "Force killing processes on port 8000..."
                    echo "$port_pids" | xargs -r kill -9 >/dev/null 2>&1
                    sleep 2
                fi
            fi
        done
    fi
    
    # Start services in the specified mode
    print_status $BLUE "Starting services in $MODE mode..."
    if [ "$MODE" = "background" ]; then
        "$SCRIPT_DIR/dev-start.sh" -b
    else
        "$SCRIPT_DIR/dev-start.sh" -f
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
