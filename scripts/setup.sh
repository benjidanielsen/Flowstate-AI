#!/bin/bash
set -e

# Flowstate-AI Automated Setup Script
# This script automates the initial setup of the Flowstate-AI development environment

echo "🚀 Flowstate-AI Automated Setup"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on supported OS
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ Unsupported OS. This script supports Linux and macOS only.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} OS check passed"

# Check for required tools
echo ""
echo "Checking required tools..."

check_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}❌${NC} $1 is not installed"
        return 1
    fi
}

MISSING_TOOLS=0

check_tool "node" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool "npm" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool "python3" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool "pip3" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool "docker" || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool "docker-compose" || echo -e "${YELLOW}⚠${NC} docker-compose not found, checking for 'docker compose'..."
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌${NC} docker compose is not available"
    MISSING_TOOLS=$((MISSING_TOOLS + 1))
else
    echo -e "${GREEN}✓${NC} docker compose is available"
fi

if [ $MISSING_TOOLS -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ Missing $MISSING_TOOLS required tool(s). Please install them and try again.${NC}"
    exit 1
fi

# Check Node.js version
echo ""
echo "Checking Node.js version..."
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo -e "${RED}❌ Node.js version 20 or higher is required. Current version: $(node -v)${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js version $(node -v) is compatible"

# Check Python version
echo ""
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo -e "${RED}❌ Python 3.11 or higher is required. Current version: $(python3 --version)${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python3 --version) is compatible"

# Install backend dependencies
echo ""
echo "Installing backend dependencies..."
cd backend
if [ ! -d "node_modules" ]; then
    npm install
    echo -e "${GREEN}✓${NC} Backend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Backend node_modules already exists, skipping..."
fi
cd ..

# Install frontend dependencies
echo ""
echo "Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Frontend node_modules already exists, skipping..."
fi
cd ..

# Install Python worker dependencies
echo ""
echo "Installing Python worker dependencies..."
cd python-worker
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    echo -e "${GREEN}✓${NC} Python worker dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Python worker venv already exists, skipping..."
fi
cd ..

# Install root Python dependencies
echo ""
echo "Installing root Python dependencies..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    echo -e "${GREEN}✓${NC} Root Python dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Root venv already exists, skipping..."
fi

# Create .env files if they don't exist
echo ""
echo "Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    cat > backend/.env << 'EOF'
NODE_ENV=development
PORT=3001
DATABASE_URL=sqlite:./dev.db
JWT_SECRET=your-secret-key-change-this-in-production
CORS_ORIGIN=http://localhost:5173
EOF
    echo -e "${GREEN}✓${NC} Created backend/.env"
else
    echo -e "${YELLOW}⚠${NC} backend/.env already exists"
fi

if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:3001
EOF
    echo -e "${GREEN}✓${NC} Created frontend/.env"
else
    echo -e "${YELLOW}⚠${NC} frontend/.env already exists"
fi

if [ ! -f "python-worker/.env" ]; then
    cat > python-worker/.env << 'EOF'
DATABASE_URL=sqlite:../backend/dev.db
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✓${NC} Created python-worker/.env"
else
    echo -e "${YELLOW}⚠${NC} python-worker/.env already exists"
fi

if [ ! -f "docker/.env.shared" ]; then
    cat > docker/.env.shared << 'EOF'
# Shared environment variables for Docker Compose
NODE_ENV=development
DATABASE_URL=postgresql://flowstate:flowstate@postgres:5432/flowstate
REDIS_URL=redis://redis:6379
EOF
    echo -e "${GREEN}✓${NC} Created docker/.env.shared"
else
    echo -e "${YELLOW}⚠${NC} docker/.env.shared already exists"
fi

# Initialize database
echo ""
echo "Initializing database..."
cd backend
if [ ! -f "dev.db" ]; then
    npm run migrate || echo -e "${YELLOW}⚠${NC} Database migration failed (this is okay if migrations don't exist yet)"
    echo -e "${GREEN}✓${NC} Database initialized"
else
    echo -e "${YELLOW}⚠${NC} Database already exists"
fi
cd ..

# Build Docker images
echo ""
echo "Building Docker images..."
docker compose -f docker/compose.yml build
echo -e "${GREEN}✓${NC} Docker images built"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Review and update .env files with your configuration"
echo "2. Start the development environment:"
echo "   - Local: npm run dev (in backend and frontend directories)"
echo "   - Docker: docker compose -f docker/compose.yml up"
echo "3. Access the application:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:3001"
echo "   - Godmode Dashboard: http://localhost:5000"
echo ""
echo "For more information, see README.md and docs/"
echo ""

