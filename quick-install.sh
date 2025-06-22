#!/bin/bash

# Quick Installation Script for YouTube Streaming Bot
# Works with both root and non-root users

set -e

echo "🚀 YouTube Streaming Bot - Quick Install"
echo "======================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Determine installation mode
if [ "$EUID" -eq 0 ]; then
    SUDO_CMD=""
    print_warning "Running as root"
else
    SUDO_CMD="sudo"
    print_status "Running as regular user"
fi

# Update system
print_status "Updating system..."
$SUDO_CMD apt update

# Install essential packages
print_status "Installing packages..."
$SUDO_CMD apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    build-essential \
    ffmpeg \
    xvfb \
    git \
    curl \
    unzip \
    pkg-config \
    libhdf5-dev \
    libopencv-dev \
    xdg-utils \
    ca-certificates \
    wget

# Remove snap chromium if installed and install apt version
print_status "Setting up Chromium browser..."
if snap list chromium >/dev/null 2>&1; then
    print_warning "Removing snap version of Chromium..."
    $SUDO_CMD snap remove chromium
fi

# Install chromium from apt repository
$SUDO_CMD apt install -y chromium-browser

# Fix chromium issues by installing proper desktop environment tools
$SUDO_CMD apt install -y \
    desktop-file-utils \
    xdg-user-dirs

# Verify installations
print_status "Verifying installations..."
python3 --version
ffmpeg -version | head -n1
chromium-browser --version

# Create virtual environment in current directory
print_status "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install setuptools first
pip install --upgrade pip setuptools wheel

# Install system packages for Python dependencies
print_status "Installing system packages for Python dependencies..."
$SUDO_CMD apt install -y \
    python3-numpy \
    python3-opencv \
    libopencv-dev \
    python3-scipy

# Install Python packages with fallback for problematic ones
print_status "Installing Python dependencies..."
pip install --no-cache-dir flask==2.3.3
pip install --no-cache-dir flask-socketio==5.3.6
pip install --no-cache-dir eventlet==0.33.3
pip install --no-cache-dir google-api-python-client==2.110.0
pip install --no-cache-dir google-auth-httplib2==0.1.1
pip install --no-cache-dir google-auth-oauthlib==1.1.0
pip install --no-cache-dir selenium==4.15.2
pip install --no-cache-dir requests==2.31.0
pip install --no-cache-dir beautifulsoup4==4.12.2
pip install --no-cache-dir schedule==1.2.0
pip install --no-cache-dir psutil==5.9.6

# Install NumPy and OpenCV separately to avoid conflicts
print_status "Installing NumPy and OpenCV..."
pip install --no-cache-dir "numpy>=1.21.0"
pip install --no-cache-dir "opencv-python>=4.5.0"

pip install --no-cache-dir pyyaml==6.0.1
pip install --no-cache-dir python-dotenv==1.0.0
pip install --no-cache-dir ffmpeg-python==0.2.0
pip install --no-cache-dir aiohttp==3.9.0
pip install --no-cache-dir websockets==12.0
pip install --no-cache-dir gunicorn==21.2.0

# Install ChromeDriver
print_status "Installing ChromeDriver..."
# Get Chrome version more safely
CHROME_VERSION=""
if command -v chromium-browser >/dev/null 2>&1; then
    # Try to get version without running the browser
    CHROME_VERSION=$(chromium-browser --version 2>/dev/null | awk '{print $2}' | cut -d'.' -f1 2>/dev/null || echo "120")
else
    CHROME_VERSION="120"  # Default fallback
fi

print_status "Detected Chrome version: $CHROME_VERSION"

# Download ChromeDriver with proper error handling
CHROMEDRIVER_VERSION=""
if [ ! -z "$CHROME_VERSION" ]; then
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION" 2>/dev/null || echo "")
fi

# Fallback to latest stable if version detection fails
if [ -z "$CHROMEDRIVER_VERSION" ]; then
    print_warning "Using fallback ChromeDriver version..."
    CHROMEDRIVER_VERSION="120.0.6099.109"
fi

print_status "Downloading ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download and install ChromeDriver
CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
if curl -L -f -o /tmp/chromedriver.zip "$CHROMEDRIVER_URL" 2>/dev/null; then
    $SUDO_CMD unzip -o /tmp/chromedriver.zip -d /usr/local/bin/
    $SUDO_CMD chmod +x /usr/local/bin/chromedriver
    rm -f /tmp/chromedriver.zip
    print_status "ChromeDriver installed successfully"
else
    print_warning "ChromeDriver download failed, trying alternative method..."
    # Alternative: install via apt if available
    $SUDO_CMD apt install -y chromium-chromedriver 2>/dev/null || {
        print_error "Could not install ChromeDriver. You may need to install it manually."
    }
fi

# Create directories
print_status "Creating directories..."
mkdir -p logs config chrome_profiles screenshots

# Setup configuration files
print_status "Setting up configuration..."
if [ ! -f "config/config.yaml" ]; then
    cp config/config.example.yaml config/config.yaml
    print_status "Created config/config.yaml from template"
fi

if [ ! -f "config/client_secrets.json" ]; then
    cp config/client_secrets.example.json config/client_secrets.json
    print_status "Created config/client_secrets.json from template"
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Created .env from template"
fi

# Make scripts executable
chmod +x *.sh

# Setup firewall (if needed)
if command -v ufw >/dev/null 2>&1; then
    print_status "Configuring firewall..."
    $SUDO_CMD ufw allow 5000/tcp
fi

print_status "Installation completed successfully!"
echo ""
print_warning "NEXT STEPS:"
echo "1. Edit config/config.yaml with your settings"
echo "2. Add YouTube API credentials to config/client_secrets.json"
echo "3. Configure stream key in config.yaml"
echo "4. Run: ./start.sh"
echo ""
print_status "To start manually: python src/app.py"
print_status "To start with script: ./start.sh"
echo ""
print_warning "Don't forget to configure YouTube credentials!"
