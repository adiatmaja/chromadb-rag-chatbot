#!/bin/bash
# =============================================================================
# Docker Deployment Helper Script for RAG Product Search System
# =============================================================================
# This script helps manage Docker deployment with common operations.
#
# Usage:
#   ./deploy.sh build      # Build Docker image
#   ./deploy.sh start      # Start container
#   ./deploy.sh stop       # Stop container
#   ./deploy.sh restart    # Restart container
#   ./deploy.sh logs       # View logs
#   ./deploy.sh shell      # Access container shell
#   ./deploy.sh index      # Index all data
#   ./deploy.sh status     # Check container status
#   ./deploy.sh clean      # Clean up containers and images

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Container name
CONTAINER_NAME="rag-product-search"
IMAGE_NAME="rag-product-search:latest"

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose is not installed. Some features may not work."
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env file not found"
        if [ -f ".env.example" ]; then
            log_info "Creating .env from .env.example"
            cp .env.example .env
            log_success ".env file created. Please edit it with your configuration."
            log_warning "Deployment paused. Edit .env and run again."
            exit 0
        else
            log_error ".env.example not found. Cannot create .env file."
            exit 1
        fi
    fi
}

# Build Docker image
build() {
    log_info "Building Docker image: $IMAGE_NAME"
    docker build -t "$IMAGE_NAME" .
    log_success "Docker image built successfully"
}

# Start container
start() {
    check_env

    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_info "Container exists. Starting..."
        docker-compose start
    else
        log_info "Starting new container..."
        docker-compose up -d
    fi

    log_success "Container started"
    log_info "View logs with: ./deploy.sh logs"
}

# Stop container
stop() {
    log_info "Stopping container..."
    docker-compose stop
    log_success "Container stopped"
}

# Restart container
restart() {
    log_info "Restarting container..."
    docker-compose restart
    log_success "Container restarted"
}

# View logs
logs() {
    log_info "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f rag
}

# Access container shell
shell() {
    log_info "Accessing container shell..."
    docker-compose exec rag bash
}

# Index all data
index_data() {
    log_info "Indexing all data..."

    log_info "1/3: Parsing intent data..."
    docker-compose exec -T rag python scripts/indexing/parse_intent_data.py

    log_info "2/3: Indexing intent data..."
    docker-compose exec -T rag python scripts/indexing/index_intent.py

    log_info "3/3: Indexing product data..."
    docker-compose exec -T rag python scripts/indexing/index_products.py

    log_success "All data indexed successfully"
    log_info "To index FAQ data (requires ClickHouse):"
    log_info "  docker-compose exec rag python scripts/indexing/index_faq.py"
}

# Check container status
status() {
    log_info "Container Status:"
    echo ""

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_success "Container is running"
        echo ""
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""

        # Health check
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")
        if [ "$HEALTH" = "healthy" ]; then
            log_success "Health status: $HEALTH"
        elif [ "$HEALTH" = "unknown" ]; then
            log_info "Health status: Not configured"
        else
            log_warning "Health status: $HEALTH"
        fi

    elif docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_warning "Container exists but is not running"
        echo ""
        docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}"
    else
        log_info "Container does not exist"
    fi
}

# Clean up
clean() {
    log_warning "This will remove containers and images. Data volumes will be preserved."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Stopping and removing containers..."
        docker-compose down

        log_info "Removing image..."
        docker rmi "$IMAGE_NAME" 2>/dev/null || log_info "Image not found"

        log_success "Cleanup complete"
        log_info "Data in database/ and data/ directories preserved"
    else
        log_info "Cleanup cancelled"
    fi
}

# Run demo
demo() {
    log_info "Running demo workflow..."
    docker-compose run --rm rag python scripts/demo/demo_full_workflow.py
}

# Test stock reader
test_stock() {
    log_info "Testing stock reader..."
    docker-compose run --rm rag python -m src.utils.stock_reader
}

# Show usage
usage() {
    echo "RAG Product Search - Docker Deployment Helper"
    echo ""
    echo "Usage: ./deploy.sh <command>"
    echo ""
    echo "Commands:"
    echo "  build       Build Docker image"
    echo "  start       Start container (create if doesn't exist)"
    echo "  stop        Stop container"
    echo "  restart     Restart container"
    echo "  logs        View container logs"
    echo "  shell       Access container shell"
    echo "  index       Index all data (intent, product)"
    echo "  status      Check container status"
    echo "  demo        Run demo workflow"
    echo "  test        Test stock reader"
    echo "  clean       Remove containers and images (preserves data)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh build && ./deploy.sh start"
    echo "  ./deploy.sh index"
    echo "  ./deploy.sh logs"
}

# Main script
main() {
    check_docker

    case "${1:-}" in
        build)
            build
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs
            ;;
        shell)
            shell
            ;;
        index)
            index_data
            ;;
        status)
            status
            ;;
        demo)
            demo
            ;;
        test)
            test_stock
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: ${1:-}"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
