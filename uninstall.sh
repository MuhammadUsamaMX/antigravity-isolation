#!/bin/bash

# Antigravity Isolation Manager - Uninstaller
# Removes all installed components

set -e

echo "🗑️  Antigravity Isolation Manager - Uninstaller"
echo "================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="$HOME/.local/share/antigravity-isolation-manager"

# Confirm uninstallation
echo -e "${YELLOW}⚠️  This will remove:${NC}"
echo "  • Antigravity Isolation Manager application"
echo "  • Systemd service"
echo "  • Desktop entries for all profiles"
echo "  • Running Antigravity processes (will be stopped)"
echo ""
echo -e "${YELLOW}⚠️  Your profile data in ~/Antigravity will NOT be deleted${NC}"
echo ""
read -p "Are you sure you want to uninstall? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo ""
echo "🛑 Stopping and disabling service..."
if systemctl is-active --quiet antigravity-manager.service; then
    sudo systemctl stop antigravity-manager.service
    echo -e "${GREEN}✅ Service stopped${NC}"
fi

if systemctl is-enabled --quiet antigravity-manager.service 2>/dev/null; then
    sudo systemctl disable antigravity-manager.service
    echo -e "${GREEN}✅ Service disabled${NC}"
fi

echo ""
echo "🗑️  Removing systemd service..."
if [ -f "/etc/systemd/system/antigravity-manager.service" ]; then
    sudo rm /etc/systemd/system/antigravity-manager.service
    sudo systemctl daemon-reload
    echo -e "${GREEN}✅ Service file removed${NC}"
fi

echo ""
echo "🛑 Stopping Antigravity processes..."
# Find and stop all Antigravity processes managed by this tool
if command -v psutil &> /dev/null || python3 -c "import psutil" 2>/dev/null; then
    python3 << 'PYTHON_SCRIPT'
import psutil
import os

profile_dir = os.path.expanduser("~/Antigravity")
if os.path.exists(profile_dir):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if profile_dir in cmdline or '--profile' in cmdline:
                    print(f"  Stopping process {proc.info['pid']}...")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
PYTHON_SCRIPT
    echo -e "${GREEN}✅ Processes stopped${NC}"
else
    echo -e "${YELLOW}⚠️  psutil not available - skipping process cleanup${NC}"
fi

echo ""
echo "📁 Removing desktop entries..."
DESKTOP_ENTRIES=$(find ~/.local/share/applications -name "antigravity-*.desktop" 2>/dev/null || true)
if [ -n "$DESKTOP_ENTRIES" ]; then
    echo "$DESKTOP_ENTRIES" | while read entry; do
        echo "  Removing $(basename "$entry")..."
        rm "$entry"
    done
    update-desktop-database ~/.local/share/applications > /dev/null 2>&1 || true
    echo -e "${GREEN}✅ Desktop entries removed${NC}"
else
    echo "  No desktop entries found"
fi

echo ""
echo "📂 Removing installation directory..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✅ Installation directory removed${NC}"
else
    echo "  Installation directory not found"
fi

echo ""
echo "================================================"
echo -e "${GREEN}✅ Uninstallation Complete!${NC}"
echo "================================================"
echo ""
echo "Your profile data is still available at: ~/Antigravity"
echo ""
echo "To completely remove all data, run:"
echo "  rm -rf ~/Antigravity"
echo ""
echo "To reinstall, run ./install.sh"



