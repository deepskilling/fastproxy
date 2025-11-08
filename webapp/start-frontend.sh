#!/bin/bash

echo "🚀 Starting FastProxy Management Frontend..."

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚙️  Creating .env.local from example..."
    cp .env.example .env.local
fi

# Start the frontend server
echo "✅ Frontend starting on http://localhost:3000"
npm run dev

