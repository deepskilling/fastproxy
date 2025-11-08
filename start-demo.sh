#!/bin/bash

# ============================================================================
# FastProxy Demo Startup Script
# ============================================================================
# This script starts all three components of the FastProxy demo:
# 1. FastProxy (reverse proxy)
# 2. Management Backend API
# 3. Management Frontend UI
# ============================================================================

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    FastProxy Demo Startup                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if required commands exist
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 is not installed${NC}"
        echo "  Please install $1 and try again"
        exit 1
    fi
}

echo "📋 Checking prerequisites..."
check_command python3
check_command node
check_command npm
echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down all services..."
    
    if [ ! -z "$FASTPROXY_PID" ]; then
        kill $FASTPROXY_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    
    echo "✓ All services stopped"
    exit 0
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Check if ports are available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗ Port $1 is already in use${NC}"
        echo "  Please free up port $1 or stop the conflicting service"
        exit 1
    fi
}

echo "🔍 Checking if ports are available..."
check_port 8000
check_port 8001
check_port 3000
echo -e "${GREEN}✓ All ports available${NC}"
echo ""

# ============================================================================
# 1. Start Management Backend
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Starting Management Backend (FastAPI)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$SCRIPT_DIR/webapp/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing backend dependencies..."
    pip install -q -r requirements.txt
    touch venv/.installed
fi

# Start backend in background
echo "Starting backend server on port 8001..."
python main.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo -n "Waiting for backend to start"
for i in {1..30}; do
    if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Backend started successfully${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

if ! curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo ""
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Check backend.log for details"
    exit 1
fi
echo ""

# ============================================================================
# 2. Start Management Frontend
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 Starting Management Frontend (Next.js)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$SCRIPT_DIR/webapp/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a few minutes)..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local from example..."
    cp .env.example .env.local
fi

# Start frontend in background
echo "Starting frontend server on port 3000..."
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo -n "Waiting for frontend to start"
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Frontend started successfully${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo ""
    echo -e "${YELLOW}⚠ Frontend may still be starting...${NC}"
    echo "It can take up to 2 minutes for Next.js to compile"
fi
echo ""

# ============================================================================
# 3. Start FastProxy
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚡ Starting FastProxy (Reverse Proxy)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$SCRIPT_DIR"

# Activate FastProxy environment (if using conda)
if command -v conda &> /dev/null; then
    # Check if fastapi environment exists
    if conda env list | grep -q "^fastapi "; then
        echo "Activating conda environment: fastapi"
        eval "$(conda shell.bash hook)"
        conda activate fastapi
    fi
fi

# Or use venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start FastProxy
echo "Starting FastProxy on port 8000..."
if [ -f "config.demo.yaml" ]; then
    echo "Using demo configuration (config.demo.yaml)"
    python main.py > fastproxy.log 2>&1 &
else
    echo "Using default configuration (config.yaml)"
    python main.py > fastproxy.log 2>&1 &
fi
FASTPROXY_PID=$!

# Wait for FastProxy to start
echo -n "Waiting for FastProxy to start"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ FastProxy started successfully${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo -e "${RED}✗ FastProxy failed to start${NC}"
    echo "Check fastproxy.log for details"
    exit 1
fi
echo ""

# ============================================================================
# All Services Started
# ============================================================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ All Services Running                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 FastProxy Demo is now running!${NC}"
echo ""
echo "Access Points:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Main Application:${NC}"
echo "  🌐 http://localhost:8000"
echo ""
echo -e "${BLUE}Individual Services (for debugging):${NC}"
echo "  📱 Frontend:  http://localhost:3000"
echo "  🔧 Backend:   http://localhost:8001"
echo "  📚 API Docs:  http://localhost:8001/docs"
echo ""
echo "Logs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  FastProxy:  $SCRIPT_DIR/fastproxy.log"
echo "  Backend:    $SCRIPT_DIR/webapp/backend/backend.log"
echo "  Frontend:   $SCRIPT_DIR/webapp/frontend/frontend.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  • Use the web interface to manage proxy routes"
echo "  • Try adding a test route in the Routes page"
echo "  • View real-time logs in the Logs page"
echo "  • Press Ctrl+C to stop all services"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep script running and show logs
echo "📝 Showing FastProxy logs (Ctrl+C to stop all services):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -f fastproxy.log

