#!/bin/bash

echo "🚀 Starting Enhanced Spotify App - Frontend"
echo "==========================================="
echo ""

cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🎵 Starting Vite dev server..."
echo "Frontend will be available at: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
