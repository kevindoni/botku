#!/bin/bash

# YouTube Streaming Bot - Root Installation Script
# For Ubuntu Server 24.04 LTS when running as root

set -e

echo "🚀 YouTube Streaming Bot Installation (Root Mode)"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verify running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    wget \
    curl \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ffmpeg \
    xvfb \
    libavcodec-extra \
    libavformat-dev \
    libavfilter-dev \
    libavdevice-dev \
    x11-utils \
    pulseaudio \
    alsa-utils \
    supervisor \
    nginx \
    build-essential \
    python3-setuptools \
    xdg-utils \
    desktop-file-utils

# Handle Chromium installation properly
print_status "Setting up Chromium browser..."
if snap list chromium >/dev/null 2>&1; then
    print_warning "Removing snap version of Chromium..."
    snap remove chromium
fi

# Install chromium from apt repository  
apt install -y chromium-browser

# Verify FFmpeg installation
if command -v ffmpeg &> /dev/null; then
    print_status "FFmpeg installed successfully: $(ffmpeg -version | head -n1)"
else
    print_error "FFmpeg installation failed"
    exit 1
fi

# Create a non-root user for the application
APP_USER="botuser"
if ! id "$APP_USER" &>/dev/null; then
    print_status "Creating user '$APP_USER'..."
    useradd -m -s /bin/bash $APP_USER
    usermod -aG sudo $APP_USER
fi

# Set up application directory
APP_DIR="/home/$APP_USER/botku"
print_status "Setting up application directory: $APP_DIR"

# Copy current directory contents to app directory
cp -r /root/botku/* $APP_DIR/ 2>/dev/null || {
    print_warning "Could not copy from /root/botku, creating fresh structure..."
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    # Clone the repository if not already present
    if [ ! -f "requirements.txt" ]; then
        print_status "Cloning repository..."
        git clone https://github.com/kevindoni/botku.git temp_repo
        cp -r temp_repo/* .
        rm -rf temp_repo
    fi
}

# Set ownership
chown -R $APP_USER:$APP_USER $APP_DIR

# Switch to botuser for Python setup
print_status "Setting up Python environment as user '$APP_USER'..."
su - $APP_USER << 'EOSU'
cd ~/botku

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs config chrome_profiles screenshots

# Set up configuration files
if [ ! -f "config/config.yaml" ]; then
    echo "Setting up configuration files..."
    cp config/config.example.yaml config/config.yaml
    cp config/client_secrets.example.json config/client_secrets.json
    cp .env.example .env
fi

# Make scripts executable
chmod +x *.sh

echo "Python environment setup completed!"
EOSU

# Download ChromeDriver for Selenium
print_status "Installing ChromeDriver..."
# Get Chrome version safely
CHROME_VERSION=$(chromium-browser --version 2>/dev/null | awk '{print $2}' | cut -d'.' -f1 2>/dev/null || echo "120")
print_status "Detected Chrome version: $CHROME_VERSION"

# Get ChromeDriver version with error handling
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION" 2>/dev/null || echo "120.0.6099.109")
print_status "Using ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download and install ChromeDriver
CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
if wget -O /tmp/chromedriver.zip "$CHROMEDRIVER_URL" 2>/dev/null; then
    unzip -o /tmp/chromedriver.zip -d /usr/local/bin/
    chmod +x /usr/local/bin/chromedriver
    rm -f /tmp/chromedriver.zip
    print_status "ChromeDriver installed successfully"
else
    print_warning "ChromeDriver download failed, trying apt installation..."
    apt install -y chromium-chromedriver 2>/dev/null || {
        print_error "Could not install ChromeDriver automatically"
    }
fi

# Create systemd service file
print_status "Creating systemd service..."
cat > /etc/systemd/system/botku.service << EOF
[Unit]
Description=YouTube Streaming Bot
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/src/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Set up firewall
print_status "Configuring firewall..."
ufw allow ssh
ufw allow 5000/tcp  # Flask default port
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable botku

print_status "Installation completed successfully!"
echo ""
print_warning "IMPORTANT NEXT STEPS:"
echo "1. Edit configuration: nano $APP_DIR/config/config.yaml"
echo "2. Set up YouTube API credentials in $APP_DIR/config/client_secrets.json"
echo "3. Configure your YouTube stream key in config.yaml"
echo "4. Edit $APP_DIR/config/accounts.json with your bot accounts"
echo ""
print_status "To start the service:"
echo "  systemctl start botku"
echo ""
print_status "To check service status:"
echo "  systemctl status botku"
echo ""
print_status "To view logs:"
echo "  journalctl -u botku -f"
echo ""
print_status "Application directory: $APP_DIR"
print_status "Application user: $APP_USER"
echo ""
print_warning "Remember to configure your YouTube API credentials before starting!"
