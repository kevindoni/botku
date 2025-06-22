#!/bin/bash

# Fix ChromeDriver installation script

echo "🔧 ChromeDriver Fix Script"
echo "=========================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Determine sudo command
if [ "$EUID" -eq 0 ]; then
    SUDO_CMD=""
else
    SUDO_CMD="sudo"
fi

# Fix snap chromium issues
print_status "Fixing Chromium installation..."
if snap list chromium >/dev/null 2>&1; then
    print_warning "Removing snap version of Chromium..."
    $SUDO_CMD snap remove chromium
fi

# Install chromium from apt
$SUDO_CMD apt update
$SUDO_CMD apt install -y chromium-browser xdg-utils desktop-file-utils

# Install ChromeDriver manually
print_status "Installing ChromeDriver manually..."

# Create temp directory
mkdir -p /tmp/chromedriver-install
cd /tmp/chromedriver-install

# Download latest stable ChromeDriver
CHROMEDRIVER_VERSION="120.0.6099.109"
print_status "Downloading ChromeDriver version: $CHROMEDRIVER_VERSION"

wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"

if [ $? -eq 0 ]; then
    unzip chromedriver.zip
    $SUDO_CMD mv chromedriver /usr/local/bin/
    $SUDO_CMD chmod +x /usr/local/bin/chromedriver
    print_status "ChromeDriver installed successfully"
else
    print_error "Download failed, trying alternative method..."
    
    # Alternative: install from Ubuntu repository
    $SUDO_CMD apt install -y chromium-chromedriver
    
    # Create symlink if needed
    if [ ! -f "/usr/local/bin/chromedriver" ] && [ -f "/usr/bin/chromedriver" ]; then
        $SUDO_CMD ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver
    fi
fi

# Cleanup
cd /
rm -rf /tmp/chromedriver-install

# Verify installation
print_status "Verifying installations..."
if command -v chromium-browser >/dev/null 2>&1; then
    echo "✅ Chromium: $(chromium-browser --version 2>/dev/null | head -n1 || echo 'Installed')"
else
    echo "❌ Chromium: Not found"
fi

if command -v chromedriver >/dev/null 2>&1; then
    echo "✅ ChromeDriver: $(chromedriver --version 2>/dev/null | head -n1 || echo 'Installed')"
else
    echo "❌ ChromeDriver: Not found"
fi

print_status "ChromeDriver fix completed!"
echo ""
print_warning "If you still have issues, try running the application with:"
echo "export DISPLAY=:99"
echo "Xvfb :99 -screen 0 1920x1080x24 &"
echo "python src/app.py"
