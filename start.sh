#!/bin/bash

# YouTube Streaming Bot Startup Script
# For Ubuntu Server 24.04 LTS

# Configuration
APP_DIR="/home/$USER/youtube-streaming-bot"
VENV_PATH="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} YouTube Streaming Bot${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Change to app directory
cd "$APP_DIR" || {
    print_error "Application directory not found: $APP_DIR"
    exit 1
}

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    print_error "Virtual environment not found: $VENV_PATH"
    print_warning "Please run the installation script first"
    exit 1
fi

print_header

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Check if config file exists
if [ ! -f "config/config.yaml" ]; then
    print_warning "Configuration file not found!"
    print_warning "Copying example configuration..."
    cp config/config.example.yaml config/config.yaml
    print_warning "Please edit config/config.yaml before starting the application"
fi

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Set up virtual display for headless operation
print_status "Setting up virtual display..."
export DISPLAY=:99
if ! pgrep -f "Xvfb :99" > /dev/null; then
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    XVFB_PID=$!
    print_status "Virtual display started (PID: $XVFB_PID)"
else
    print_status "Virtual display already running"
fi

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    print_error "FFmpeg not found! Please install FFmpeg"
    exit 1
fi

# Check if ChromeDriver is available
if ! command -v chromedriver &> /dev/null; then
    print_warning "ChromeDriver not found in PATH"
    print_warning "Bot functionality may not work properly"
fi

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    if [ ! -z "$XVFB_PID" ]; then
        kill $XVFB_PID 2>/dev/null || true
        print_status "Virtual display stopped"
    fi
    print_status "Application stopped"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Start the application
print_status "Starting YouTube Streaming Bot..."
print_status "Dashboard will be available at: http://localhost:5000"
print_status "Press Ctrl+C to stop the application"
echo ""

# Run the main application
python src/app.py
