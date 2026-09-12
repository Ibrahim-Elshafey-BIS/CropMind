#!/bin/bash
# infrastructure/scripts/seed_db.sh
# CropMind Database Seed Script

set -e

echo "🌱 CropMind - Database Seed Script"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if containers are running
if ! docker ps | grep -q "cropmind_db"; then
    echo -e "${RED}❌ Database container is not running. Run setup.sh first.${NC}"
    exit 1
fi

# Run seed files
echo -e "${YELLOW}Running seed files...${NC}"

SEED_DIR="data/seeds"

for seed_file in farms_seed.sql crops_seed.sql transactions_seed.sql; do
    echo -e "  Seeding: $seed_file"
    docker exec -i cropmind_db psql -U ${POSTGRES_USER:-cropmind} -d ${POSTGRES_DB:-cropmind} < "$SEED_DIR/$seed_file" 2>/dev/null || {
        echo -e "${RED}  ❌ Failed to seed $seed_file${NC}"
    }
done

echo ""
echo -e "${GREEN}✅ Database seeding completed!${NC}"
