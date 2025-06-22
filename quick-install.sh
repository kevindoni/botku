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
    ffmpeg \
    chromium-browser \
    xvfb \
    git \
    curl \
    unzip

# Verify installations
print_status "Verifying installations..."
python3 --version
ffmpeg -version | head -n1
chromium-browser --version

# Create virtual environment in current directory
print_status "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install ChromeDriver
print_status "Installing ChromeDriver..."
CHROME_VERSION=$(chromium-browser --version | awk '{print $2}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
curl -L -o /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
$SUDO_CMD unzip /tmp/chromedriver.zip -d /usr/local/bin/
$SUDO_CMD chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

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
