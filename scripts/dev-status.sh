#!/bin/bash

# prplOS LCM Log Analysis System - Development Environment Status Script

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
POSTGRES_PORT=5432
REDIS_PORT=6379

# PID files
PID_DIR="./pids"
BACKEND_PID="$PID_DIR/backend.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"
REDIS_PID="$PID_DIR/redis.pid"

# SQLite Configuration
SQLITE_DB_PATH="./data/prplos_analysis.db"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to print help
print_help() {
    echo "prplOS LCM Log Analysis System - Development Environment Status Script"
    echo ""
    echo "Usage:"
    echo "  $0 [-h|--help]"
    echo ""
    echo "This script shows the status of all development services:"
    echo "  - Backend (FastAPI)"
    echo "  - Frontend (React)"
    echo "  - PostgreSQL"
    echo "  - Redis"
    echo ""
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

# Function to check service status
check_service_status() {
    local pid_file=$1
    local service_name=$2
    local port=$3
    local url=$4
    
    echo -n "  $service_name: "
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        
        # Check if it's a Docker container
        if [[ "$pid" == docker-* ]]; then
            local container_id=${pid#docker-}
            if docker ps -q --filter id="$container_id" >/dev/null 2>&1; then
                echo -e "${GREEN}Running (Docker)${NC}"
                echo "    Container ID: $container_id"
                echo "    Port: $port"
                if [ -n "$url" ]; then
                    echo "    URL: $url"
                fi
            else
                echo -e "${RED}Stopped (Docker container not found)${NC}"
            fi
        else
            # Regular process
            if ps -p "$pid" > /dev/null 2>&1; then
                echo -e "${GREEN}Running${NC}"
                echo "    PID: $pid"
                echo "    Port: $port"
                if [ -n "$url" ]; then
                    echo "    URL: $url"
                fi
            else
                echo -e "${RED}Stopped (Process not found)${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}Not started${NC}"
    fi
}

# Function to check port availability
check_port_status() {
    local port=$1
    local service_name=$2
    
    if check_port "$port" "$service_name"; then
        echo -e "    Port $port: ${GREEN}Available${NC}"
    else
        echo -e "    Port $port: ${RED}Not available${NC}"
    fi
}

# Function to check service health
check_service_health() {
    local port=$1
    local service_name=$2
    local health_url=$3
    
    if [ -n "$health_url" ] && check_port "$port" "$service_name"; then
        echo -n "    Health check: "
        if curl -s --max-time 5 "$health_url" >/dev/null 2>&1; then
            echo -e "${GREEN}Healthy${NC}"
        else
            echo -e "${YELLOW}Unresponsive${NC}"
        fi
    fi
}

# Function to show system information
show_system_info() {
    print_status $PURPLE "System Information"
    echo "  OS: $(uname -s) $(uname -r)"
    echo "  Python: $(python3 --version 2>/dev/null || echo 'Not installed')"
    echo "  Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
    echo "  Docker: $(docker --version 2>/dev/null || echo 'Not installed')"
    echo "  SQLite: $(sqlite3 --version 2>/dev/null || echo 'Not installed')"
    echo "  Redis: $(redis-server --version 2>/dev/null || echo 'Not installed')"
    echo ""
}

# Function to show SQLite database status
show_sqlite_status() {
    print_status $PURPLE "SQLite Database Status"
    
    if [ -f "$SQLITE_DB_PATH" ]; then
        echo -e "  Database: ${GREEN}Exists${NC}"
        echo "  Path: $SQLITE_DB_PATH"
        
        # Get file size
        local size=$(du -h "$SQLITE_DB_PATH" 2>/dev/null | cut -f1)
        echo "  Size: $size"
        
        # Check if we can connect to the database
        if command -v sqlite3 >/dev/null 2>&1; then
            local table_count=$(sqlite3 "$SQLITE_DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0")
            echo "  Tables: $table_count"
            
            # Get row counts for main tables
            local tables=("projects" "analyses" "applications" "log_entries" "time_series_data" "anomalies" "predictions" "alerts")
            for table in "${tables[@]}"; do
                local count=$(sqlite3 "$SQLITE_DB_PATH" "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "0")
                echo "    $table: $count rows"
            done
        else
            echo "  SQLite3: Not installed (cannot query database)"
        fi
    else
        echo -e "  Database: ${RED}Not found${NC}"
        echo "  Expected path: $SQLITE_DB_PATH"
        echo "  Run './dev-start.sh' to create the database"
    fi
    echo ""
}

# Function to show service status
show_service_status() {
    print_status $PURPLE "Service Status"
    
    check_service_status "$BACKEND_PID" "Backend (FastAPI)" "$BACKEND_PORT" "http://0.0.0.0:$BACKEND_PORT"
    check_port_status "$BACKEND_PORT" "Backend"
    check_service_health "$BACKEND_PORT" "Backend" "http://0.0.0.0:$BACKEND_PORT/api/v1/health"
    echo ""
    
    check_service_status "$FRONTEND_PID" "Frontend (React)" "$FRONTEND_PORT" "http://0.0.0.0:$FRONTEND_PORT"
    check_port_status "$FRONTEND_PORT" "Frontend"
    echo ""
    
    check_service_status "$REDIS_PID" "Redis" "$REDIS_PORT"
    check_port_status "$REDIS_PORT" "Redis"
    echo ""
}

# Function to show Docker containers
show_docker_containers() {
    print_status $PURPLE "Docker Containers"
    
    local containers=$(docker ps --filter name="${PROJECT_NAME}-*" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null)
    
    if [ -n "$containers" ]; then
        echo "$containers"
    else
        echo "  No project containers running"
    fi
    echo ""
}

# Function to show log files
show_log_files() {
    print_status $PURPLE "Log Files"
    
    local log_dir="./logs"
    if [ -d "$log_dir" ]; then
        for log_file in "$log_dir"/*.log; do
            if [ -f "$log_file" ]; then
                local filename=$(basename "$log_file")
                local size=$(du -h "$log_file" | cut -f1)
                local lines=$(wc -l < "$log_file" 2>/dev/null || echo "0")
                local last_modified=$(stat -c %y "$log_file" 2>/dev/null | cut -d' ' -f1,2 || echo "Unknown")
                echo "  $filename: $size, $lines lines, modified: $last_modified"
            fi
        done
    else
        echo "  No log directory found"
    fi
    echo ""
}

# Function to show recent log entries
show_recent_logs() {
    print_status $PURPLE "Recent Log Entries"
    
    local log_file="./logs/app.log"
    if [ -f "$log_file" ]; then
        echo "  Last 5 entries from app.log:"
        tail -5 "$log_file" | while IFS= read -r line; do
            echo "    $line"
        done
    else
        echo "  No app.log file found"
    fi
    echo ""
}

# Function to show quick actions
show_quick_actions() {
    print_status $PURPLE "Quick Actions"
    echo "  Start services:     ./dev-start.sh [-b|-f]"
    echo "  Stop services:      ./dev-stop.sh"
    echo "  Restart services:   ./dev-restart.sh [-b|-f]"
    echo "  View logs:          tail -f logs/*.log"
    echo "  Check health:       curl http://0.0.0.0:$BACKEND_PORT/api/v1/health"
    echo "  Frontend dev:       cd ui && npm run dev"
    echo "  Backend dev:        source venv/bin/activate && uvicorn app.main:app --reload"
    echo ""
}

# Function to show main status
show_status() {
    print_status $PURPLE "prplOS LCM Log Analysis System - Development Environment Status"
    echo ""
    
    show_system_info
    show_sqlite_status
    show_service_status
    show_docker_containers
    show_log_files
    show_recent_logs
    show_quick_actions
    
    print_status $CYAN "Status check completed!"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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
show_status
