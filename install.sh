#!/bin/bash

# YouTube Streaming Bot - Ubuntu Server 24 Setup Script
# Tested on Ubuntu Server 24.04 LTS

set -e

echo "🚀 YouTube Streaming Bot Installation Script"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y \
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
    lsb-release

# Install FFmpeg
print_status "Installing FFmpeg..."
sudo apt install -y ffmpeg

# Verify FFmpeg installation
if command -v ffmpeg &> /dev/null; then
    print_status "FFmpeg installed successfully: $(ffmpeg -version | head -n1)"
else
    print_error "FFmpeg installation failed"
    exit 1
fi

# Install Chrome/Chromium for bot functionality
print_status "Installing Chromium browser..."
sudo apt install -y chromium-browser

# Install Xvfb for headless display
print_status "Installing Xvfb for headless display..."
sudo apt install -y xvfb

# Install additional dependencies for video processing
print_status "Installing additional video processing libraries..."
sudo apt install -y \
    libavcodec-extra \
    libavformat-dev \
    libavfilter-dev \
    libavdevice-dev \
    x11-utils \
    pulseaudio \
    alsa-utils

# Create application directory
APP_DIR="$HOME/youtube-streaming-bot"
print_status "Creating application directory: $APP_DIR"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python packages
print_status "Installing Python dependencies..."
cat > requirements.txt << EOF
flask==2.3.3
google-api-python-client==2.110.0
google-auth-httplib2==0.1.1
google-auth-oauthlib==1.1.0
selenium==4.15.2
requests==2.31.0
beautifulsoup4==4.12.2
schedule==1.2.0
psutil==5.9.6
opencv-python==4.8.1.78
numpy==1.24.3
pyyaml==6.0.1
python-dotenv==1.0.0
ffmpeg-python==0.2.0
asyncio==3.4.3
aiohttp==3.9.0
websockets==12.0
gunicorn==21.2.0
supervisor==4.2.5
EOF

pip install -r requirements.txt

# Download ChromeDriver for Selenium
print_status "Installing ChromeDriver..."
CHROME_VERSION=$(chromium-browser --version | awk '{print $2}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Create directory structure
print_status "Creating directory structure..."
mkdir -p config src/{streaming,bot,api,dashboard} templates static/{css,js} logs

# Create systemd service file
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/youtube-streaming-bot.service > /dev/null << EOF
[Unit]
Description=YouTube Streaming Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python src/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create supervisor config for better process management
print_status "Creating supervisor configuration..."
sudo tee /etc/supervisor/conf.d/youtube-streaming-bot.conf > /dev/null << EOF
[program:youtube-streaming-bot]
command=$APP_DIR/venv/bin/python $APP_DIR/src/app.py
directory=$APP_DIR
user=$USER
autostart=true
autorestart=true
stderr_logfile=$APP_DIR/logs/error.log
stdout_logfile=$APP_DIR/logs/access.log
environment=PATH="$APP_DIR/venv/bin"
EOF

# Set up firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 5000/tcp  # Flask default port
sudo ufw --force enable

# Create startup script
print_status "Creating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

# Start virtual display for headless operation
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
XVFB_PID=$!

# Start the application
python src/app.py

# Cleanup
kill $XVFB_PID 2>/dev/null || true
EOF

chmod +x start.sh

# Create example configuration
print_status "Creating example configuration..."
cat > config/config.example.yaml << 'EOF'
# YouTube Streaming Bot Configuration

youtube:
  client_secrets_file: "config/client_secret.json"
  api_key: "YOUR_YOUTUBE_API_KEY"
  channel_id: "YOUR_CHANNEL_ID"
  
streaming:
  stream_key: "YOUR_YOUTUBE_STREAM_KEY"
  bitrate: 2500
  resolution: "1920x1080"
  fps: 30
  input_source: "testsrc"  # testsrc, webcam, screen
  
bot:
  comments:
    enabled: true
    min_delay: 30
    max_delay: 180
    accounts_file: "config/accounts.json"
    comments_file: "config/comments.json"
    
  viewers:
    enabled: true
    min_viewers: 5
    max_viewers: 25
    session_duration: 300
    
dashboard:
  host: "0.0.0.0"
  port: 5000
  debug: false
  secret_key: "change-this-secret-key"
  
logging:
  level: "INFO"
  file: "logs/app.log"
EOF

# Set permissions
chmod 755 "$APP_DIR"
chmod -R 755 logs config

print_status "Installation completed successfully!"
echo ""
print_warning "IMPORTANT NEXT STEPS:"
echo "1. Copy config.example.yaml to config.yaml and edit it"
echo "2. Set up YouTube API credentials in config/client_secret.json"
echo "3. Configure your YouTube stream key in config.yaml"
echo "4. Edit config/accounts.json with your bot accounts"
echo "5. Start the application with: ./start.sh"
echo ""
print_status "Installation directory: $APP_DIR"
print_status "To start manually: cd $APP_DIR && ./start.sh"
print_status "To start as service: sudo systemctl start youtube-streaming-bot"
echo ""
print_warning "Remember to configure your YouTube API credentials before starting!"
