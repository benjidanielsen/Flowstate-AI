#!/bin/bash
# Flowstate-AI Production Deployment Script
# This script deploys the Flowstate-AI system to production

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"
ENV_FILE="$PROJECT_ROOT/.env.production"

echo -e "${GREEN}=== Flowstate-AI Production Deployment ===${NC}"
echo "Project Root: $PROJECT_ROOT"
echo "Docker Directory: $DOCKER_DIR"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Check for environment file
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: .env.production file not found${NC}"
    echo "Please copy .env.production.template to .env.production and configure it"
    exit 1
fi

# Validate critical environment variables
echo -e "${YELLOW}Validating environment configuration...${NC}"
set -a
source "$ENV_FILE"
set +a

if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}Error: DATABASE_URL not set in .env.production${NC}"
    exit 1
fi

if [ -z "${JWT_SECRET:-}" ] || [ "${JWT_SECRET}" = "CHANGE_ME_RANDOM_SECRET_MIN_32_CHARS" ]; then
    echo -e "${RED}Error: JWT_SECRET not properly configured in .env.production${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Pull latest images
echo -e "${YELLOW}Pulling latest Docker images...${NC}"
cd "$DOCKER_DIR"
docker compose -f "$PROJECT_ROOT/docker-compose.production.yml" pull

# Build custom images
echo -e "${YELLOW}Building application images...${NC}"
docker compose -f "$PROJECT_ROOT/docker-compose.production.yml" build --no-cache

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker compose -f "$PROJECT_ROOT/docker-compose.production.yml" down || true

# Start database and wait for it to be ready
echo -e "${YELLOW}Starting database...${NC}"
docker compose -f "$PROJECT_ROOT/docker-compose.production.yml" up -d postgres redis

echo "Waiting for database to be ready..."
sleep 10

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
if command -v dbmate &> /dev/null; then
    cd "$PROJECT_ROOT"
    dbmate up
else
    echo -e "${YELLOW}Warning: dbmate not found, skipping migrations${NC}"
    echo "Please run migrations manually or install dbmate"
fi

# Start all services
echo -e "${YELLOW}Starting all services...${NC}"
cd "$DOCKER_DIR"
docker compose -f "$PROJECT_ROOT/docker-compose.production.yml" up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 15

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/health || echo "000")
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health || echo "000")
WORKER_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")

echo "Backend Health: $BACKEND_HEALTH"
echo "Frontend Health: $FRONTEND_HEALTH"
echo "Python Worker Health: $WORKER_HEALTH"

if [ "$BACKEND_HEALTH" = "200" ] && [ "$FRONTEND_HEALTH" = "200" ] && [ "$WORKER_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ All services are healthy${NC}"
else
    echo -e "${YELLOW}Warning: Some services may not be fully healthy yet${NC}"
    echo "Check logs with: docker-compose logs -f"
fi

# Display running containers
echo ""
echo -e "${YELLOW}Running containers:${NC}"
docker compose -f "$PROJECT_ROOT/docker-compose.production.yml" ps

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Services are available at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:3001"
echo "  Python Worker: http://localhost:8000"
echo ""
echo "To view logs: cd $DOCKER_DIR && docker-compose logs -f"
echo "To stop services: cd $DOCKER_DIR && docker-compose down"
echo ""

