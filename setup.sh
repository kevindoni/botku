#!/bin/bash

# Super Quick Setup for YouTube Streaming Bot
# Use this if virtual environment is missing or corrupted

echo "⚡ Super Quick Setup for YouTube Streaming Bot"
echo "============================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Installing..."
    if [ "$EUID" -eq 0 ]; then
        apt update && apt install -y python3 python3-pip python3-venv
    else
        sudo apt update && sudo apt install -y python3 python3-pip python3-venv
    fi
fi

# Remove existing venv if corrupted
if [ -d "venv" ]; then
    print_warning "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies one by one for better error handling
print_status "Installing essential packages..."
pip install --no-cache-dir flask==2.3.3
pip install --no-cache-dir flask-socketio==5.3.6
pip install --no-cache-dir requests==2.31.0
pip install --no-cache-dir pyyaml==6.0.1
pip install --no-cache-dir python-dotenv==1.0.0

print_status "Installing additional packages..."
pip install --no-cache-dir google-api-python-client==2.110.0 || print_warning "Google API client installation failed"
pip install --no-cache-dir google-auth-httplib2==0.1.1 || print_warning "Google auth httplib2 installation failed"
pip install --no-cache-dir google-auth-oauthlib==1.1.0 || print_warning "Google auth oauthlib installation failed"
pip install --no-cache-dir beautifulsoup4==4.12.2 || print_warning "BeautifulSoup installation failed"
pip install --no-cache-dir schedule==1.2.0 || print_warning "Schedule installation failed"
pip install --no-cache-dir psutil==5.9.6 || print_warning "Psutil installation failed"
pip install --no-cache-dir ffmpeg-python==0.2.0 || print_warning "FFmpeg Python installation failed"
pip install --no-cache-dir aiohttp==3.9.0 || print_warning "Aiohttp installation failed"
pip install --no-cache-dir websockets==12.0 || print_warning "Websockets installation failed"
pip install --no-cache-dir gunicorn==21.2.0 || print_warning "Gunicorn installation failed"

# Install potentially problematic packages
print_status "Installing optional packages..."
pip install --no-cache-dir "numpy>=1.21.0" || print_warning "NumPy installation failed"

# Use gevent instead of eventlet for Python 3.12 compatibility
pip install --no-cache-dir gevent==23.9.1 || print_warning "Gevent installation failed"

pip install --no-cache-dir "opencv-python>=4.5.0" || print_warning "OpenCV installation failed"
pip install --no-cache-dir selenium==4.15.2 || print_warning "Selenium installation failed"

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs config chrome_profiles screenshots static/uploads templates

# Copy configuration files if they don't exist
if [ ! -f "config/config.yaml" ] && [ -f "config/config.example.yaml" ]; then
    print_status "Creating configuration file..."
    cp config/config.example.yaml config/config.yaml
    print_warning "Please edit config/config.yaml with your YouTube API credentials"
fi

if [ ! -f "config/client_secrets.json" ] && [ -f "config/client_secrets.example.json" ]; then
    print_status "Creating client secrets file..."
    cp config/client_secrets.example.json config/client_secrets.json
    print_warning "Please edit config/client_secrets.json with your credentials"
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    print_status "Creating environment file..."
    cp .env.example .env
    print_warning "Please edit .env with your environment settings"
fi

# Make scripts executable
chmod +x *.sh

print_status "Setup completed successfully!"
echo ""
print_warning "NEXT STEPS:"
echo "1. Edit config/config.yaml with your YouTube API credentials"
echo "2. Edit config/client_secrets.json with your Google credentials"
echo "3. Run: ./run.sh (or ./start.sh)"
echo ""
print_status "🔗 Useful links:"
echo "- Google Cloud Console: https://console.cloud.google.com/"
echo "- YouTube Data API: https://developers.google.com/youtube/v3"
echo ""
print_status "To start the application: ./run.sh"
echo "💡 For help, check docs/troubleshooting.md"
