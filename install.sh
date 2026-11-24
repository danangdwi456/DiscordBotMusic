#!/bin/bash

# Discord Music Bot - Auto Installer
# Supports: Ubuntu/Debian, macOS

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎵 Discord Music Bot - Auto Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "✅ Detected OS: $OS"
echo ""

# Check Python
echo "📦 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "   Install: sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION"
echo ""

# Check FFmpeg
echo "📦 Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found. Installing..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo apt update
        sudo apt install -y ffmpeg
    elif [[ "$OS" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew not found. Install from: https://brew.sh"
            exit 1
        fi
        brew install ffmpeg
    fi
    
    echo "✅ FFmpeg installed"
else
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | awk '{print $3}')
    echo "✅ FFmpeg $FFMPEG_VERSION"
fi
echo ""

# Install Python packages
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All packages installed"
else
    echo "❌ Failed to install packages"
    exit 1
fi
echo ""

# Setup environment
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Discord token!"
    echo "   Run: nano .env"
else
    echo "ℹ️  .env already exists"
fi
echo ""

# Check token
if grep -q "your_bot_token_here" .env 2>/dev/null; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ⚠️  NEXT STEPS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Get your Discord bot token:"
    echo "   https://discord.com/developers/applications"
    echo ""
    echo "2. Edit .env file:"
    echo "   nano .env"
    echo ""
    echo "3. Replace 'your_bot_token_here' with your token"
    echo ""
    echo "4. Run the bot:"
    echo "   python3 bot.py"
    echo ""
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ INSTALLATION COMPLETE!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Run the bot:"
    echo "  python3 bot.py"
    echo ""
fi
