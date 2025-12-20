"""
Antigravity Isolation Manager - Configuration
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANTIGRAVITY_PROFILES_DIR = os.path.expanduser("~/Antigravity")
DESKTOP_ENTRIES_DIR = os.path.expanduser("~/.local/share/applications")

# Docker configuration
DOCKER_IMAGE_NAME = "isolated-antigravity"
CONTAINER_PREFIX = "antigravity-"

# Web server configuration
HOST = "127.0.0.1"
# Use port 5001 to avoid conflict with Chrome Isolation Manager (port 5000)
PORT = int(os.environ.get('ANTIGRAVITY_MANAGER_PORT', '5001'))
DEBUG = False

# Ensure directories exist
os.makedirs(ANTIGRAVITY_PROFILES_DIR, exist_ok=True)
os.makedirs(DESKTOP_ENTRIES_DIR, exist_ok=True)

