#!/bin/bash

# Development server startup script

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=1
export APP_ENV=development

# Create logs directory
mkdir -p logs

echo "🚀 Starting YouTube Streaming Bot in development mode..."
echo "📊 Dashboard: http://localhost:5000"
echo "🔧 Debug mode: ON"
echo "Press Ctrl+C to stop"

# Start the application
python src/app.py
