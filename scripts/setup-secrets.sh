#!/bin/bash
# Flowstate-AI Secrets Management Script
# Generates secure secrets and creates environment files

set -e
set -u

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}=== Flowstate-AI Secrets Setup ===${NC}"
echo ""

# Function to generate random secret
generate_secret() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Function to generate UUID
generate_uuid() {
    if command -v uuidgen &> /dev/null; then
        uuidgen
    else
        cat /proc/sys/kernel/random/uuid
    fi
}

# Check if .env.production already exists
ENV_FILE="$PROJECT_ROOT/.env.production"
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Warning: .env.production already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Existing file preserved."
        exit 0
    fi
    # Backup existing file
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}Backed up existing file${NC}"
fi

# Generate secrets
echo -e "${YELLOW}Generating secure secrets...${NC}"
JWT_SECRET=$(generate_secret 64)
SESSION_SECRET=$(generate_secret 64)
POSTGRES_PASSWORD=$(generate_secret 32)
REDIS_PASSWORD=$(generate_secret 32)

# Get user input for configurable values
echo ""
echo "Please provide the following configuration values:"
echo "(Press Enter to use default values shown in brackets)"
echo ""

read -p "Domain name [localhost]: " DOMAIN_NAME
DOMAIN_NAME=${DOMAIN_NAME:-localhost}

read -p "Frontend port [3000]: " FRONTEND_PORT
FRONTEND_PORT=${FRONTEND_PORT:-3000}

read -p "Backend port [3001]: " BACKEND_PORT
BACKEND_PORT=${BACKEND_PORT:-3001}

read -p "Python worker port [8000]: " PYTHON_WORKER_PORT
PYTHON_WORKER_PORT=${PYTHON_WORKER_PORT:-8000}

read -p "PostgreSQL port [5432]: " POSTGRES_PORT
POSTGRES_PORT=${POSTGRES_PORT:-5432}

read -p "Redis port [6379]: " REDIS_PORT
REDIS_PORT=${REDIS_PORT:-6379}

read -p "OpenAI API Key (optional, press Enter to skip): " OPENAI_API_KEY

# Construct CORS origin
if [ "$DOMAIN_NAME" = "localhost" ]; then
    CORS_ORIGIN="http://localhost:${FRONTEND_PORT}"
else
    CORS_ORIGIN="https://${DOMAIN_NAME},http://${DOMAIN_NAME}"
fi

# Construct API URL
if [ "$DOMAIN_NAME" = "localhost" ]; then
    VITE_API_URL="http://localhost:${BACKEND_PORT}"
else
    VITE_API_URL="https://${DOMAIN_NAME}/api"
fi

# Create .env.production file
echo -e "${YELLOW}Creating .env.production file...${NC}"

cat > "$ENV_FILE" << EOF
# Flowstate-AI Production Environment Configuration
# Generated on: $(date)
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

# Application
NODE_ENV=production
APP_NAME=Flowstate-AI
APP_VERSION=1.0.0

# Domain Configuration
DOMAIN_NAME=${DOMAIN_NAME}

# Database Configuration
POSTGRES_DB=flowstate_ai
POSTGRES_USER=flowstate
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_PORT=${POSTGRES_PORT}
DATABASE_URL=postgresql://flowstate:${POSTGRES_PASSWORD}@postgres:5432/flowstate_ai
DB_POOL_MIN=2
DB_POOL_MAX=10
DB_SSL=false

# Redis Configuration
REDIS_PORT=${REDIS_PORT}
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
REDIS_DB=0

# Backend API
BACKEND_PORT=${BACKEND_PORT}
BACKEND_HOST=0.0.0.0
JWT_SECRET="${JWT_SECRET}"
JWT_EXPIRY=7d
SESSION_SECRET="${SESSION_SECRET}"

# Frontend
FRONTEND_PORT=${FRONTEND_PORT}
VITE_API_URL=${VITE_API_URL}

# Python Worker
PYTHON_WORKER_PORT=${PYTHON_WORKER_PORT}
PYTHONUNBUFFERED=1
OPENAI_API_KEY=${OPENAI_API_KEY}

# AI Configuration
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000

# Logging
LOG_LEVEL=info
LOG_FORMAT=json

# Security
CORS_ORIGIN=${CORS_ORIGIN}
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Email (Optional - configure as needed)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@flowstate.ai

# External Integrations (Optional)
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
EOF

# Set restrictive permissions
chmod 600 "$ENV_FILE"

echo -e "${GREEN}✓ .env.production file created successfully${NC}"
echo ""

# Create secrets summary file (without sensitive values)
SUMMARY_FILE="$PROJECT_ROOT/.secrets-summary.txt"
cat > "$SUMMARY_FILE" << EOF
Flowstate-AI Secrets Summary
Generated on: $(date)

This file contains metadata about generated secrets.
The actual secret values are stored in .env.production

Generated Secrets:
- JWT_SECRET: 64 characters
- SESSION_SECRET: 64 characters
- POSTGRES_PASSWORD: 32 characters
- REDIS_PASSWORD: 32 characters

Configuration:
- Domain: ${DOMAIN_NAME}
- Frontend Port: ${FRONTEND_PORT}
- Backend Port: ${BACKEND_PORT}
- Python Worker Port: ${PYTHON_WORKER_PORT}
- PostgreSQL Port: ${POSTGRES_PORT}
- Redis Port: ${REDIS_PORT}
- OpenAI API Key: $([ -n "$OPENAI_API_KEY" ] && echo "Configured" || echo "Not configured")

IMPORTANT SECURITY NOTES:
1. .env.production contains sensitive secrets - NEVER commit to version control
2. File permissions set to 600 (owner read/write only)
3. Backup .env.production securely
4. Rotate secrets regularly
5. Use different secrets for different environments

Next Steps:
1. Review .env.production and adjust any optional settings
2. Ensure .env.production is in .gitignore
3. Run deployment: ./scripts/deploy-production.sh
EOF

echo -e "${YELLOW}Security Checklist:${NC}"
echo "✓ Secrets generated with cryptographically secure random data"
echo "✓ File permissions set to 600 (owner read/write only)"
echo "✓ Summary created at: $SUMMARY_FILE"
echo ""
echo -e "${RED}IMPORTANT:${NC}"
echo "1. NEVER commit .env.production to version control"
echo "2. Backup .env.production securely (encrypted storage recommended)"
echo "3. Rotate secrets regularly (every 90 days recommended)"
echo "4. Use different secrets for different environments"
echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo "Review .env.production and run: ./scripts/deploy-production.sh"
echo ""

