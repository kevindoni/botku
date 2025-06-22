#!/bin/bash

# Auto-setup script untuk YouTube Streaming Bot
# Script ini akan mengonfigurasi virtual environment dan dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Setting up YouTube Streaming Bot..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs config static/uploads templates

# Copy configuration files if they don't exist
if [ ! -f "config/config.yaml" ]; then
    echo "⚙️ Creating configuration file..."
    cp config/config.example.yaml config/config.yaml
    echo "⚠️ Please edit config/config.yaml with your YouTube API credentials"
fi

if [ ! -f ".env" ]; then
    echo "🔐 Creating environment file..."
    cp .env.example .env
    echo "⚠️ Please edit .env with your environment settings"
fi

# Make start script executable
chmod +x start.sh

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit config/config.yaml with your YouTube API credentials"
echo "2. Edit .env with your environment settings"
echo "3. Run: ./start.sh"
echo ""
echo "🔗 Useful links:"
echo "- Google Cloud Console: https://console.cloud.google.com/"
echo "- YouTube Data API: https://developers.google.com/youtube/v3"
echo ""
echo "💡 For help, check docs/troubleshooting.md"
