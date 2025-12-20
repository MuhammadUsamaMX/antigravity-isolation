"""
Antigravity Isolation Manager - Configuration
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANTIGRAVITY_PROFILES_DIR = os.path.expanduser("~/Antigravity")
DESKTOP_ENTRIES_DIR = os.path.expanduser("~/.local/share/applications")

# Web server configuration
HOST = "127.0.0.1"
# Use port 5001 to avoid conflict with Chrome Isolation Manager (port 5000)
PORT = int(os.environ.get('ANTIGRAVITY_MANAGER_PORT', '5001'))
DEBUG = False

# Namespace isolation configuration
USE_NAMESPACE_ISOLATION = os.environ.get('ANTIGRAVITY_USE_NAMESPACES', 'true').lower() == 'true'
NAMESPACE_MODE = os.environ.get('ANTIGRAVITY_NAMESPACE_MODE', 'mount').lower()  # 'mount', 'user', 'full', 'none'
USE_NETWORK_NAMESPACE = os.environ.get('ANTIGRAVITY_USE_NET_NS', 'false').lower() == 'true'

# Check if unshare is available and permitted
# If not, disable namespace isolation automatically
if USE_NAMESPACE_ISOLATION and NAMESPACE_MODE != 'none':
    import subprocess
    try:
        # Test if unshare works (some environments don't allow it, especially from systemd)
        result = subprocess.run(
            ['unshare', '--mount', '--fork', 'true'],
            capture_output=True,
            timeout=2
        )
        if result.returncode != 0:
            # unshare not permitted, disable namespace isolation
            USE_NAMESPACE_ISOLATION = False
            print("⚠️  Namespace isolation not permitted, using directory-based isolation")
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        # unshare not available or not permitted
        USE_NAMESPACE_ISOLATION = False
        print("⚠️  Namespace isolation not available, using directory-based isolation")

# Ensure directories exist
os.makedirs(ANTIGRAVITY_PROFILES_DIR, exist_ok=True)
os.makedirs(DESKTOP_ENTRIES_DIR, exist_ok=True)

