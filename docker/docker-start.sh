#!/bin/bash

# ============================================================================
# FastProxy Docker Demo Startup Script
# ============================================================================
# Starts the complete FastProxy demo stack using Docker Compose
# ============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           FastProxy Docker Demo Startup                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "  Please install Docker and try again"
    echo "  Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose is not installed${NC}"
        echo "  Please install Docker Compose and try again"
        exit 1
    fi
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

echo -e "${GREEN}✓ Docker and Docker Compose are available${NC}"
echo ""

# Check if containers are already running
if $COMPOSE_CMD -f docker-compose.demo.yml ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠ Some containers are already running${NC}"
    read -p "Do you want to stop and restart them? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping existing containers..."
        $COMPOSE_CMD -f docker-compose.demo.yml down
    else
        echo "Exiting..."
        exit 0
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Building Docker images..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
$COMPOSE_CMD -f docker-compose.demo.yml build

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting services..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
$COMPOSE_CMD -f docker-compose.demo.yml up -d

echo ""
echo -n "Waiting for services to be healthy"
for i in {1..60}; do
    if $COMPOSE_CMD -f docker-compose.demo.yml ps | grep -q "healthy"; then
        BACKEND_HEALTHY=$(docker inspect --format='{{.State.Health.Status}}' fastproxy-backend 2>/dev/null || echo "unknown")
        FASTPROXY_HEALTHY=$(docker inspect --format='{{.State.Health.Status}}' fastproxy 2>/dev/null || echo "unknown")
        
        if [ "$BACKEND_HEALTHY" = "healthy" ] && [ "$FASTPROXY_HEALTHY" = "healthy" ]; then
            echo ""
            echo -e "${GREEN}✓ All services are healthy${NC}"
            break
        fi
    fi
    echo -n "."
    sleep 2
done

echo ""
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Services Running                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 FastProxy Demo Stack is now running!${NC}"
echo ""
echo "Access Points:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Main Application:${NC}"
echo "  🌐 http://localhost:8000"
echo ""
echo -e "${BLUE}Individual Services:${NC}"
echo "  📱 Frontend:  http://localhost:3000"
echo "  🔧 Backend:   http://localhost:8001"
echo "  📚 API Docs:  http://localhost:8001/docs"
echo ""
echo "Useful Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  View logs:        $COMPOSE_CMD -f docker-compose.demo.yml logs -f"
echo "  Stop services:    $COMPOSE_CMD -f docker-compose.demo.yml down"
echo "  Restart services: $COMPOSE_CMD -f docker-compose.demo.yml restart"
echo "  Check status:     $COMPOSE_CMD -f docker-compose.demo.yml ps"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ask if user wants to view logs
read -p "Do you want to view the logs now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Showing logs (Ctrl+C to exit):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    $COMPOSE_CMD -f docker-compose.demo.yml logs -f
fi

