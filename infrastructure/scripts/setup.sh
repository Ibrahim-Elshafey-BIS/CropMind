#!/bin/bash
# infrastructure/scripts/setup.sh
# CropMind Setup Script

set -e

echo "🌾 CropMind - Setup Script"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created. Please edit it with your values.${NC}"
fi

# Load environment variables
source .env

# Build Docker images
echo ""
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose -f infrastructure/docker/docker-compose.yml build
echo -e "${GREEN}✅ Docker images built${NC}"

# Start services
echo ""
echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f infrastructure/docker/docker-compose.yml up -d
echo -e "${GREEN}✅ Services started${NC}"

# Wait for database to be ready
echo ""
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
sleep 10

# Run database migrations
echo ""
echo -e "${YELLOW}Running database migrations...${NC}"
docker exec cropmind_backend alembic upgrade head
echo -e "${GREEN}✅ Migrations completed${NC}"

# Seed database
echo ""
echo -e "${YELLOW}Seeding database...${NC}"
bash infrastructure/scripts/seed_db.sh
echo -e "${GREEN}✅ Database seeded${NC}"

# Show status
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ CropMind Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Services:"
echo "  Backend API:     http://localhost:8000"
echo "  API Docs:        http://localhost:8000/docs"
echo "  AI Engine:       http://localhost:8001"
echo "  CV Service:      http://localhost:8002"
echo "  n8n:             http://localhost:5678"
echo "  Nginx:           http://localhost"
echo ""
echo "To check logs: docker-compose -f infrastructure/docker/docker-compose.yml logs -f"
echo "To stop:       docker-compose -f infrastructure/docker/docker-compose.yml down"
