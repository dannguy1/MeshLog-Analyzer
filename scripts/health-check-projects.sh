#!/bin/bash

# Project Management Health Check Script
# Validates configuration and data integrity

set -e

echo "🔍 Project Management Health Check"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check 1: Configuration file exists
echo ""
echo "1. Configuration Check"
echo "----------------------"

if [ -f ".env" ]; then
    print_status 0 ".env file exists"
    
    # Extract DATA_DIR from .env
    if grep -q "DATA_DIR=" .env; then
        DATA_DIR=$(grep "DATA_DIR=" .env | cut -d'=' -f2 | tr -d '"')
        print_status 0 "DATA_DIR configured: $DATA_DIR"
        
        # Check if DATA_DIR uses absolute path
        if [[ "$DATA_DIR" = /* ]]; then
            print_status 0 "DATA_DIR uses absolute path"
        else
            print_status 1 "DATA_DIR should use absolute path"
            print_warning "Consider changing DATA_DIR to absolute path in .env"
        fi
    else
        print_status 1 "DATA_DIR not found in .env"
        print_warning "Copy env.config to .env and configure DATA_DIR"
    fi
else
    print_status 1 ".env file not found"
    print_warning "Run: cp env.config .env"
    exit 1
fi

# Check 2: Data directory structure
echo ""
echo "2. Data Directory Structure"
echo "---------------------------"

if [ -d "$DATA_DIR" ]; then
    print_status 0 "DATA_DIR exists: $DATA_DIR"
    
    # Check permissions
    if [ -w "$DATA_DIR" ]; then
        print_status 0 "DATA_DIR is writable"
    else
        print_status 1 "DATA_DIR is not writable"
        print_warning "Run: sudo chown -R \$USER:\$USER $DATA_DIR"
    fi
    
    # Check subdirectories
    for dir in "uploads" "projects" "analysis" "logs" "temp" "backups"; do
        if [ -d "$DATA_DIR/$dir" ]; then
            print_status 0 "$dir/ directory exists"
        else
            print_status 1 "$dir/ directory missing"
            print_info "Will be created automatically when needed"
        fi
    done
else
    print_status 1 "DATA_DIR does not exist: $DATA_DIR"
    print_warning "Create directory: sudo mkdir -p $DATA_DIR && sudo chown \$USER:\$USER $DATA_DIR"
fi

# Check 3: Projects file
echo ""
echo "3. Projects Database"
echo "--------------------"

PROJECTS_FILE="$DATA_DIR/projects.json"
if [ -f "$PROJECTS_FILE" ]; then
    print_status 0 "projects.json exists"
    
    # Validate JSON
    if python3 -c "import json; json.load(open('$PROJECTS_FILE'))" 2>/dev/null; then
        PROJECT_COUNT=$(python3 -c "import json; print(len(json.load(open('$PROJECTS_FILE'))))" 2>/dev/null || echo "0")
        print_status 0 "projects.json is valid JSON ($PROJECT_COUNT projects)"
        
        # Check for empty file
        if [ "$PROJECT_COUNT" = "0" ]; then
            print_warning "No projects found - this may be normal for new installations"
            
            # Check if backup exists
            if [ -f "$PROJECTS_FILE.backup" ]; then
                BACKUP_COUNT=$(python3 -c "import json; print(len(json.load(open('$PROJECTS_FILE.backup'))))" 2>/dev/null || echo "0")
                if [ "$BACKUP_COUNT" != "0" ]; then
                    print_warning "Backup file has $BACKUP_COUNT projects - consider restoring"
                    print_info "To restore: cp $PROJECTS_FILE.backup $PROJECTS_FILE"
                fi
            fi
        fi
    else
        print_status 1 "projects.json is corrupted"
        
        # Check if backup exists for recovery
        if [ -f "$PROJECTS_FILE.backup" ]; then
            print_info "Backup file exists for recovery"
            print_info "To restore: cp $PROJECTS_FILE.backup $PROJECTS_FILE"
        else
            print_warning "No backup file found"
        fi
    fi
else
    print_status 1 "projects.json not found"
    print_info "Will be created automatically when first project is added"
fi

# Check 4: Backend process
echo ""
echo "4. Backend Service"
echo "------------------"

if pgrep -f "uvicorn.*main:app" > /dev/null; then
    print_status 0 "Backend process is running"
    
    # Test API endpoint
    if command -v curl > /dev/null; then
        if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
            print_status 0 "API health check passed"
        else
            print_status 1 "API health check failed"
            print_warning "Backend may be starting up or having issues"
        fi
    else
        print_info "curl not available - cannot test API"
    fi
else
    print_status 1 "Backend process not running"
    print_info "Start with: ./scripts/backend-start.sh"
fi

# Check 5: Disk space
echo ""
echo "5. Disk Space"
echo "-------------"

if [ -d "$DATA_DIR" ]; then
    DISK_USAGE=$(df "$DATA_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 80 ]; then
        print_status 0 "Disk usage: ${DISK_USAGE}%"
    elif [ "$DISK_USAGE" -lt 90 ]; then
        print_warning "Disk usage: ${DISK_USAGE}% (getting high)"
    else
        print_status 1 "Disk usage: ${DISK_USAGE}% (critically high)"
    fi
    
    # Show disk space details
    print_info "$(df -h "$DATA_DIR" | tail -1)"
fi

# Summary
echo ""
echo "6. Summary & Recommendations"
echo "=============================="

# Check if any critical issues exist
CRITICAL_ISSUES=0

if [ ! -f ".env" ]; then
    ((CRITICAL_ISSUES++))
fi

if [ ! -d "$DATA_DIR" ] || [ ! -w "$DATA_DIR" ]; then
    ((CRITICAL_ISSUES++))
fi

if [ -f "$PROJECTS_FILE" ] && ! python3 -c "import json; json.load(open('$PROJECTS_FILE'))" 2>/dev/null; then
    ((CRITICAL_ISSUES++))
fi

if [ "$CRITICAL_ISSUES" -eq 0 ]; then
    echo -e "${GREEN}🎉 System appears healthy!${NC}"
    echo ""
    echo "Next steps:"
    echo "• Review logs: tail -f $DATA_DIR/logs/app.log"
    echo "• Check projects: curl http://localhost:8000/api/v1/projects"
    echo "• Access UI: http://localhost:3000"
else
    echo -e "${RED}⚠️  Found $CRITICAL_ISSUES critical issue(s) that need attention${NC}"
    echo ""
    echo "Please address the issues above before proceeding."
fi

echo ""
echo "📚 For more help:"
echo "• Configuration: docs/DATA_DIR_CONFIGURATION.md"
echo "• Project Management: docs/PROJECT_MANAGEMENT_DESIGN.md"
echo "• Quick Reference: docs/PROJECT_MANAGEMENT_QUICK_REFERENCE.md"
