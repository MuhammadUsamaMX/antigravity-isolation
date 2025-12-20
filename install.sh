#!/bin/bash

# Antigravity Isolation Manager - Automated Installer
# For Ubuntu/Debian-based Linux systems

set -e

echo "🚀 Antigravity Isolation Manager - Installation Script"
echo "======================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="$HOME/.local/share/antigravity-isolation-manager"

# Get the directory where the script is located (source directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Please do not run this script as root${NC}"
    echo "Run it as your regular user. It will ask for sudo when needed."
    exit 1
fi

echo "📋 Checking system requirements..."
echo ""

# Check for Antigravity
if ! command -v antigravity &> /dev/null; then
    echo -e "${YELLOW}⚠️  Antigravity is not installed or not in PATH${NC}"
    echo "Please install Antigravity first:"
    echo ""
    echo "For deb-based distributions (Debian, Ubuntu):"
    echo "  sudo mkdir -p /etc/apt/keyrings"
    echo "  curl -fsSL https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/antigravity-repo-key.gpg"
    echo "  echo \"deb [signed-by=/etc/apt/keyrings/antigravity-repo-key.gpg] https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/ antigravity-debian main\" | sudo tee /etc/apt/sources.list.d/antigravity.list > /dev/null"
    echo "  sudo apt update"
    echo "  sudo apt install antigravity"
    echo ""
    echo "For rpm-based distributions (Red Hat, Fedora, SUSE):"
    echo "  sudo tee /etc/yum.repos.d/antigravity.repo << EOL"
    echo "  [antigravity-rpm]"
    echo "  name=Antigravity RPM Repository"
    echo "  baseurl=https://us-central1-yum.pkg.dev/projects/antigravity-auto-updater-dev/antigravity-rpm"
    echo "  enabled=1"
    echo "  gpgcheck=0"
    echo "  EOL"
    echo "  sudo dnf makecache"
    echo "  sudo dnf install antigravity"
    echo ""
    read -p "Press Enter to continue anyway (you can install Antigravity later)..."
else
    echo -e "${GREEN}✅ Antigravity found: $(antigravity --version 2>/dev/null || echo 'installed')${NC}"
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip
else
    echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip3 not found, installing...${NC}"
    sudo apt install -y python3-pip
fi

echo -e "${GREEN}✅ pip3 found${NC}"

# Check for psutil (required for process management)
if ! python3 -c "import psutil" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  psutil not found, installing...${NC}"
    pip3 install --user psutil || sudo pip3 install psutil
fi

echo -e "${GREEN}✅ psutil found${NC}"

echo ""
echo "📦 Installing Python dependencies..."

# Check if packages are already installed via apt
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing python3-flask..."
    sudo apt update
    sudo apt install -y python3-flask || pip3 install --user flask
else
    echo -e "${GREEN}✅ Python packages already installed${NC}"
fi

echo ""
echo "📁 Creating installation directory..."

# Remove old installation if exists
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  Existing installation found at $INSTALL_DIR${NC}"
    echo "Removing old installation..."
    rm -rf "$INSTALL_DIR"
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "📋 Copying application files..."
cp -r "$SCRIPT_DIR/app" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
mkdir -p "$INSTALL_DIR/scripts"
cp "$SCRIPT_DIR/scripts/antigravity-launcher.sh" "$INSTALL_DIR/scripts/"
chmod +x "$INSTALL_DIR/scripts/antigravity-launcher.sh"

echo -e "${GREEN}✅ Files copied to $INSTALL_DIR${NC}"

echo ""
echo "📁 Setting up directories..."
mkdir -p ~/Antigravity
mkdir -p ~/.local/share/applications

echo ""
echo "🔧 Installing systemd service..."

# Create systemd service file with correct paths
SERVICE_FILE="/tmp/antigravity-manager-$USER.service"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Antigravity Isolation Manager Web Interface
After=network.target
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR/app
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
# Wait for user session to be ready (D-Bus, X11/Wayland available)
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/python3 $INSTALL_DIR/app/app.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Install the service
sudo cp "$SERVICE_FILE" /etc/systemd/system/antigravity-manager.service
rm "$SERVICE_FILE"

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable antigravity-manager.service
sudo systemctl start antigravity-manager.service

echo ""
echo "⏳ Waiting for service to start..."
sleep 3

# Check if service is running
if systemctl is-active --quiet antigravity-manager.service; then
    echo -e "${GREEN}✅ Service is running!${NC}"
else
    echo -e "${RED}❌ Service failed to start${NC}"
    echo "Check logs with: sudo journalctl -u antigravity-manager.service -n 50"
    exit 1
fi

echo ""
echo "======================================================"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "======================================================"
echo ""
echo "📍 Installation Directory: $INSTALL_DIR"
echo "🌐 Web Interface: http://localhost:5001"
echo "📁 Profiles Directory: ~/Antigravity"
echo ""
echo "Quick Start:"
echo "  1. Open http://localhost:5001 in your browser"
echo "  2. Create a new profile"
echo "  3. Launch it from your application menu!"
echo ""
echo "Useful Commands:"
echo "  • View logs: sudo journalctl -u antigravity-manager.service -f"
echo "  • Restart service: sudo systemctl restart antigravity-manager.service"
echo "  • Stop service: sudo systemctl stop antigravity-manager.service"
echo "  • Uninstall: Run ./uninstall.sh from the source directory"
echo ""
echo "Opening web interface in 3 seconds..."
sleep 3

# Try to open the browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5001 &
elif command -v gnome-open &> /dev/null; then
    gnome-open http://localhost:5001 &
fi

echo ""
echo "🎉 Enjoy your isolated Antigravity profiles!"

