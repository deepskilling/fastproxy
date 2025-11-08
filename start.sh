#!/bin/bash

# FastProxy Quick Start Script

echo "🚀 FastProxy - Starting Server"
echo "==============================="

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if fastapi environment exists
if ! conda env list | grep -q "^fastapi "; then
    echo "📦 Creating conda environment 'fastapi'..."
    conda create -n fastapi python=3.11 -y
fi

# Activate conda environment
echo "🔌 Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate fastapi

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

