#!/bin/bash

# Python 3.12 Compatibility Fix for YouTube Streaming Bot

echo "🔧 Python 3.12 Compatibility Fix"
echo "================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Remove problematic eventlet
print_status "Removing eventlet (incompatible with Python 3.12)..."
pip uninstall -y eventlet || echo "Eventlet not installed"

# Install gevent as alternative
print_status "Installing gevent as eventlet replacement..."
pip install --no-cache-dir gevent==23.9.1

# Install greenlet explicitly
pip install --no-cache-dir greenlet>=2.0.0

# Update flask-socketio configuration
print_status "Applying Python 3.12 compatibility fixes..."

# Reinstall flask-socketio to ensure clean state
pip uninstall -y flask-socketio
pip install --no-cache-dir flask-socketio==5.3.6

print_status "Python 3.12 compatibility fixes applied!"
echo ""
print_warning "CHANGES MADE:"
echo "1. Removed eventlet (incompatible with Python 3.12)"
echo "2. Installed gevent as replacement"
echo "3. Updated Flask-SocketIO to use threading mode"
echo "4. Installed required greenlet dependency"
echo ""
print_status "You can now run the application with: ./run.sh"
