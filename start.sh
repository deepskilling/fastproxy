#!/bin/bash

# FastProxy Quick Start Script

echo "🚀 FastProxy - Starting Server"
echo "==============================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt -q

# Create audit directory if it doesn't exist
mkdir -p audit

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting FastProxy server on http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

