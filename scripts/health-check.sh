#!/bin/bash

# Flowstate-AI Health Check Script
# Checks the health of all services and reports status

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🏥 Flowstate-AI Health Check${NC}"
echo "=============================="
echo ""

# Function to check HTTP endpoint
check_http() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_status" ]; then
            echo -e "${GREEN}✓${NC} $name is healthy (HTTP $response)"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} $name returned HTTP $response (expected $expected_status)"
            return 1
        fi
    else
        echo -e "${RED}❌${NC} $name is unreachable"
        return 1
    fi
}

# Function to check Docker container
check_docker() {
    local name=$1
    local container=$2
    
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")
        if [ "$status" = "healthy" ]; then
            echo -e "${GREEN}✓${NC} $name container is healthy"
            return 0
        elif [ "$status" = "unknown" ]; then
            echo -e "${YELLOW}⚠${NC} $name container is running (no health check configured)"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} $name container status: $status"
            return 1
        fi
    else
        echo -e "${RED}❌${NC} $name container is not running"
        return 1
    fi
}

# Function to check process
check_process() {
    local name=$1
    local process=$2
    
    if pgrep -f "$process" > /dev/null; then
        echo -e "${GREEN}✓${NC} $name process is running"
        return 0
    else
        echo -e "${RED}❌${NC} $name process is not running"
        return 1
    fi
}

# Determine if running in Docker or local
if docker ps &> /dev/null; then
    MODE="docker"
else
    MODE="local"
fi

echo "Mode: $MODE"
echo ""

HEALTH_STATUS=0

# Check services based on mode
if [ "$MODE" = "docker" ]; then
    echo "Checking Docker containers..."
    check_docker "Backend" "flowstate-backend" || HEALTH_STATUS=1
    check_docker "Frontend" "flowstate-frontend" || HEALTH_STATUS=1
    check_docker "Python Worker" "flowstate-python-worker" || HEALTH_STATUS=1
    check_docker "PostgreSQL" "flowstate-postgres" || HEALTH_STATUS=1
    check_docker "Redis" "flowstate-redis" || HEALTH_STATUS=1
    
    echo ""
    echo "Checking HTTP endpoints..."
    check_http "Backend API" "http://localhost:3001/health" || HEALTH_STATUS=1
    check_http "Frontend" "http://localhost:5173" || HEALTH_STATUS=1
    check_http "Python Worker" "http://localhost:8000/health" || HEALTH_STATUS=1
else
    echo "Checking local processes..."
    check_process "Backend" "node.*backend" || HEALTH_STATUS=1
    check_process "Frontend" "vite" || HEALTH_STATUS=1
    check_process "Python Worker" "uvicorn" || HEALTH_STATUS=1
    
    echo ""
    echo "Checking HTTP endpoints..."
    check_http "Backend API" "http://localhost:3001/health" || HEALTH_STATUS=1
    check_http "Frontend" "http://localhost:5173" || HEALTH_STATUS=1
    check_http "Python Worker" "http://localhost:8000/health" || HEALTH_STATUS=1
fi

echo ""
echo "=============================="
if [ $HEALTH_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ All services are healthy${NC}"
else
    echo -e "${RED}❌ Some services are unhealthy${NC}"
fi
echo ""

exit $HEALTH_STATUS

