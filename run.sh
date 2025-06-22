#!/bin/bash

# Simple run script for YouTube Streaming Bot

echo "🚀 Starting YouTube Streaming Bot..."

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run installation script first."
    echo "Try: chmod +x quick-install.sh && ./quick-install.sh"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if app.py exists
if [ ! -f "src/app.py" ]; then
    echo "❌ Application not found at src/app.py"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Set up display for headless operation
export DISPLAY=:99
if ! pgrep Xvfb > /dev/null; then
    echo "🖥️  Starting virtual display..."
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    XVFB_PID=$!
    sleep 2
fi

# Start the application
echo "🎬 Starting YouTube Streaming Bot..."
echo "Dashboard will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping application..."
    if [ ! -z "$XVFB_PID" ]; then
        kill $XVFB_PID 2>/dev/null
    fi
    pkill -f Xvfb 2>/dev/null
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Run the application
python src/app.py

# Cleanup when done
cleanup
