#!/bin/bash
# prplOS LCM Log Analysis System - Production Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="prplos-lcm-log-analysis"
COMPOSE_FILE="docker compose.yml"
ENV_FILE="env.production"
AGENT_COMPOSE_FILE="docker-compose.agent.yml"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker with Compose support."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p data/WNC/LCM-Logs-Data
    mkdir -p logs
    mkdir -p uploads
    mkdir -p analysis_results
    
    log_success "Directories created"
}

# Deploy with agent engine integration
deploy_agent() {
    log_info "Building and deploying $PROJECT_NAME with Agent Engine integration..."
    
    # Check if agent compose file exists
    if [ ! -f "$AGENT_COMPOSE_FILE" ]; then
        log_error "Agent compose file $AGENT_COMPOSE_FILE not found"
        exit 1
    fi
    
    # Check if agent project exists
    AGENT_PROJECT_PATH="../wnc-log-agents"
    if [ ! -d "$AGENT_PROJECT_PATH" ]; then
        log_warning "Agent project not found at $AGENT_PROJECT_PATH"
        log_warning "Please ensure the wnc-log-agents project is in the correct location"
        log_warning "You can also modify the AGENT_PROJECT_PATH variable in this script"
        exit 1
    fi
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker compose -f $COMPOSE_FILE -f $AGENT_COMPOSE_FILE down --remove-orphans
    
    # Build agent service image
    log_info "Building agent service image..."
    cd "$AGENT_PROJECT_PATH"
    docker build -t wnc-log-agents .
    cd - > /dev/null
    
    # Build images
    log_info "Building Docker images..."
    docker compose -f $COMPOSE_FILE -f $AGENT_COMPOSE_FILE build --no-cache
    
    # Start services
    log_info "Starting services..."
    docker compose -f $COMPOSE_FILE -f $AGENT_COMPOSE_FILE up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Test agent connectivity
    log_info "Testing agent connectivity..."
    max_attempts=10
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec prplos_backend curl -f http://wnc-log-agents:8001/health > /dev/null 2>&1; then
            log_success "Agent service is healthy and accessible"
            break
        else
            log_warning "Attempt $attempt/$max_attempts: Agent service not ready yet..."
            sleep 5
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Agent service is not accessible after $max_attempts attempts"
        log_info "Checking agent service logs..."
        docker logs wnc-log-agents --tail 20
        exit 1
    fi
    
    # Check service health
    check_service_health
    
    log_success "Agent-integrated deployment completed successfully!"
}

# Check service health
check_service_health() {
    log_info "Checking service health..."
    
    # Check Redis
    if docker compose -f $COMPOSE_FILE exec -T redis redis-cli ping | grep -q "PONG"; then
        log_success "Redis is healthy"
    else
        log_error "Redis is not healthy"
        return 1
    fi
    
    # Check Backend
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Backend is healthy"
    else
        log_error "Backend is not healthy"
        return 1
    fi
    
    # Check Frontend
    if curl -f http://localhost/health &> /dev/null; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend is not healthy"
        return 1
    fi
}

# Show deployment info
show_deployment_info() {
    echo ""
    log_success "🎉 Deployment Complete!"
    echo ""
    echo "📊 Service Information:"
    echo "  🌐 Frontend: http://localhost"
    echo "  🔧 Backend API: http://localhost:8000"
    echo "  📊 Backend Health: http://localhost:8000/health"
    echo "  📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🐳 Docker Services:"
    docker compose -f $COMPOSE_FILE ps
    echo ""
    echo "📝 Useful Commands:"
    echo "  View logs: docker compose -f $COMPOSE_FILE logs -f"
    echo "  Stop services: docker compose -f $COMPOSE_FILE down"
    echo "  Restart services: docker compose -f $COMPOSE_FILE restart"
    echo "  Scale workers: docker compose -f $COMPOSE_FILE up -d --scale celery_worker=3"
    echo ""
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    docker compose -f $COMPOSE_FILE down --remove-orphans
    docker system prune -f
    log_success "Cleanup completed"
}

# Main execution
main() {
    echo "🚀 prplOS LCM Log Analysis System - Production Deployment"
    echo "=================================================="
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_directories
            deploy
            show_deployment_info
            ;;
        "deploy-agent")
            check_prerequisites
            create_directories
            deploy_agent
            show_deployment_info
            ;;
        "stop")
            log_info "Stopping services..."
            docker compose -f $COMPOSE_FILE down
            log_success "Services stopped"
            ;;
        "restart")
            log_info "Restarting services..."
            docker compose -f $COMPOSE_FILE restart
            log_success "Services restarted"
            ;;
        "logs")
            docker compose -f $COMPOSE_FILE logs -f
            ;;
        "status")
            docker compose -f $COMPOSE_FILE ps
            ;;
        "cleanup")
            cleanup
            ;;
        "health")
            check_service_health
            ;;
        *)
            echo "Usage: $0 {deploy|deploy-agent|stop|restart|logs|status|cleanup|health}"
            echo ""
            echo "Commands:"
            echo "  deploy       - Deploy the application (default)"
            echo "  deploy-agent - Deploy with agent engine integration"
            echo "  stop         - Stop all services"
            echo "  restart      - Restart all services"
            echo "  logs         - View service logs"
            echo "  status       - Show service status"
            echo "  cleanup      - Clean up containers and images"
            echo "  health       - Check service health"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
