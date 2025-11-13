#!/usr/bin/env bash

# Community Kit VPS - Systemd Service Installation Script
# This script installs and configures the systemd service and timer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/community_kit"
SERVICE_FILE="community-kit-vps.service"
TIMER_FILE="community-kit-vps.timer"
SYSTEMD_DIR="/etc/systemd/system"

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║        Community Kit VPS - Systemd Service Installer                  ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[ERROR]${NC} This script must be run as root"
    echo "Please run: sudo $0"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} Running as root"

# Check if service files exist
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} Service file not found: $SERVICE_FILE"
    exit 1
fi

if [ ! -f "$TIMER_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} Timer file not found: $TIMER_FILE"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} Service files found"

# Ask for installation directory
echo ""
read -p "Install directory [default: /opt/community_kit]: " USER_INSTALL_DIR
INSTALL_DIR="${USER_INSTALL_DIR:-$INSTALL_DIR}"

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}[*]${NC} Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
fi

# Copy project files if not already in install directory
CURRENT_DIR=$(pwd)
if [ "$CURRENT_DIR" != "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}[*]${NC} Copying project files to $INSTALL_DIR"
    
    # Copy essential files
    cp -r get_repo_data_vps.py "$INSTALL_DIR/"
    cp -r community_kit_downloader_vps.sh "$INSTALL_DIR/"
    cp -r requirements.txt "$INSTALL_DIR/"
    cp -r tracked_repos.txt "$INSTALL_DIR/"
    
    # Copy config if it exists, otherwise copy example
    if [ -f "config.env" ]; then
        cp config.env "$INSTALL_DIR/"
    else
        cp config.env.example "$INSTALL_DIR/config.env"
        echo -e "${YELLOW}[!]${NC} Config copied from example - please edit $INSTALL_DIR/config.env"
    fi
    
    # Create reports directory
    mkdir -p "$INSTALL_DIR/reports"
    
    echo -e "${GREEN}[✓]${NC} Files copied to $INSTALL_DIR"
else
    echo -e "${GREEN}[✓]${NC} Already in installation directory"
fi

# Update service file with actual install directory
echo -e "${YELLOW}[*]${NC} Configuring service files for $INSTALL_DIR"
sed -i "s|/opt/community_kit|$INSTALL_DIR|g" "$SERVICE_FILE"

# Install Python dependencies
echo -e "${YELLOW}[*]${NC} Installing Python dependencies"
python3 -m pip install -r "$INSTALL_DIR/requirements.txt" > /dev/null 2>&1 || {
    echo -e "${RED}[ERROR]${NC} Failed to install Python dependencies"
    exit 1
}
echo -e "${GREEN}[✓]${NC} Python dependencies installed"

# Check if config.env exists and is configured
if [ ! -f "$INSTALL_DIR/config.env" ]; then
    echo -e "${RED}[ERROR]${NC} Configuration file not found: $INSTALL_DIR/config.env"
    echo "Please create config.env from config.env.example and configure it"
    exit 1
fi

# Check if Tor is installed (optional)
if command -v tor >/dev/null 2>&1; then
    echo -e "${GREEN}[✓]${NC} Tor is installed"
    
    # Check if Tor is running
    if systemctl is-active --quiet tor; then
        echo -e "${GREEN}[✓]${NC} Tor service is running"
    else
        echo -e "${YELLOW}[!]${NC} Tor is installed but not running"
        read -p "Start Tor service now? [Y/n]: " START_TOR
        if [[ $START_TOR =~ ^[Yy]$ ]] || [[ -z $START_TOR ]]; then
            systemctl start tor
            systemctl enable tor
            echo -e "${GREEN}[✓]${NC} Tor service started and enabled"
        fi
    fi
else
    echo -e "${YELLOW}[!]${NC} Tor is not installed (optional for hidden service support)"
fi

# Copy service files to systemd directory
echo -e "${YELLOW}[*]${NC} Installing systemd service and timer"
cp "$SERVICE_FILE" "$SYSTEMD_DIR/"
cp "$TIMER_FILE" "$SYSTEMD_DIR/"
echo -e "${GREEN}[✓]${NC} Service files installed to $SYSTEMD_DIR"

# Reload systemd daemon
echo -e "${YELLOW}[*]${NC} Reloading systemd daemon"
systemctl daemon-reload
echo -e "${GREEN}[✓]${NC} Systemd daemon reloaded"

# Enable and start the timer
echo -e "${YELLOW}[*]${NC} Enabling and starting the timer"
systemctl enable community-kit-vps.timer
systemctl start community-kit-vps.timer
echo -e "${GREEN}[✓]${NC} Timer enabled and started"

# Show status
echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                    Installation Complete!                              ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Service Status:${NC}"
systemctl status community-kit-vps.timer --no-pager || true
echo ""
echo -e "${GREEN}Next Run:${NC}"
systemctl list-timers community-kit-vps.timer --no-pager || true
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "Useful Commands:"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "  View timer status:"
echo "    systemctl status community-kit-vps.timer"
echo ""
echo "  View service status:"
echo "    systemctl status community-kit-vps.service"
echo ""
echo "  View logs:"
echo "    journalctl -u community-kit-vps.service -f"
echo ""
echo "  Run manually now:"
echo "    systemctl start community-kit-vps.service"
echo ""
echo "  Stop the timer:"
echo "    systemctl stop community-kit-vps.timer"
echo ""
echo "  Disable the timer:"
echo "    systemctl disable community-kit-vps.timer"
echo ""
echo "  View next scheduled runs:"
echo "    systemctl list-timers"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}[!]${NC} Make sure to configure $INSTALL_DIR/config.env with your tokens"
echo -e "${YELLOW}[!]${NC} The scanner will run every 2 hours automatically"
echo -e "${YELLOW}[!]${NC} Reports will be saved to $INSTALL_DIR/reports/"
echo ""
