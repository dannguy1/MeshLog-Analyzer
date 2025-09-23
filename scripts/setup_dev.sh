#!/bin/bash

# prplOS LCM Log Analysis System - Development Setup Script

set -e

echo "🚀 Setting up prplOS LCM Log Analysis System development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3.11+ is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 18+ is required but not installed"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Some features may not work"
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed"
        exit 1
    fi
    
    print_success "System requirements check passed"
}

# Setup Python environment
setup_python() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Created virtual environment"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    print_success "Python environment setup complete"
}

# Setup Node.js environment
setup_node() {
    print_status "Setting up Node.js environment..."
    
    cd ui
    
    # Install dependencies
    npm install
    
    cd ..
    
    print_success "Node.js environment setup complete"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Start PostgreSQL and Redis with Docker
    if command -v docker &> /dev/null; then
        docker-compose up -d postgres redis
        
        # Wait for services to be ready
        print_status "Waiting for database services to be ready..."
        sleep 10
        
        # Run database migrations
        source venv/bin/activate
        python scripts/setup_db.py
        
        print_success "Database setup complete"
    else
        print_warning "Docker not available. Please manually start PostgreSQL and Redis"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data
    mkdir -p logs
    mkdir -p temp
    mkdir -p ui/src/components
    mkdir -p ui/src/pages
    mkdir -p ui/src/store
    mkdir -p ui/src/services
    mkdir -p ui/src/utils
    mkdir -p ui/src/types
    mkdir -p ui/src/__tests__
    
    print_success "Directories created"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
    else
        print_status ".env file already exists"
    fi
    
    print_success "Environment variables setup complete"
}

# Setup pre-commit hooks
setup_pre_commit() {
    print_status "Setting up pre-commit hooks..."
    
    source venv/bin/activate
    pre-commit install
    
    print_success "Pre-commit hooks setup complete"
}

# Run initial tests
run_tests() {
    print_status "Running initial tests..."
    
    source venv/bin/activate
    
    # Backend tests
    pytest tests/ -v --tb=short
    
    # Frontend tests
    cd ui
    npm test -- --passWithNoTests
    cd ..
    
    print_success "Initial tests completed"
}

# Main setup function
main() {
    print_status "Starting development environment setup..."
    
    check_requirements
    create_directories
    setup_env
    setup_python
    setup_node
    setup_database
    setup_pre_commit
    
    print_success "Development environment setup complete!"
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Start backend server: uvicorn app.main:app --reload --port 8000"
    echo "3. Start frontend server: cd ui && npm run dev"
    echo "4. Open browser: http://localhost:3000"
    echo ""
    echo "For more information, see docs/implementation_plan.md"
}

# Run main function
main "$@"
