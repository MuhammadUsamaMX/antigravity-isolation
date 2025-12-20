#!/bin/bash

# Antigravity Launcher Script
# This script is called by desktop entries to launch isolated Antigravity profiles
# It launches Antigravity directly in the user's session (not via API)
# Supports namespace-level isolation if enabled

PROFILE_NAME="$1"

if [ -z "$PROFILE_NAME" ]; then
    echo "Usage: $0 [ProfileName]"
    exit 1
fi

# Profile directory
PROFILE_DIR="$HOME/Antigravity/$PROFILE_NAME"

# Create directories if they don't exist
mkdir -p "$PROFILE_DIR"
mkdir -p "$PROFILE_DIR/Downloads"

# Check if Antigravity is already running for this profile
if pgrep -f "antigravity.*--user-data-dir.*$PROFILE_DIR" > /dev/null; then
    echo "Antigravity is already running for profile: $PROFILE_NAME"
    exit 0
fi

# Check if namespace isolation is enabled
USE_NAMESPACES="${ANTIGRAVITY_USE_NAMESPACES:-true}"
NAMESPACE_MODE="${ANTIGRAVITY_NAMESPACE_MODE:-mount}"

# Launch Antigravity directly with the profile directory
# This runs in the user's session, so the window will appear
export ANTIGRAVITY_HOME="$PROFILE_DIR"

# Preserve host browser authentication - CRITICAL for Antigravity
# Antigravity uses the host browser for authentication, so we must preserve:
# 1. X11/Wayland display access
# 2. D-Bus session bus access
# 3. XAUTHORITY for X11 authentication

# Preserve DISPLAY
if [ -z "$DISPLAY" ]; then
    export DISPLAY=":0"
fi

# Preserve Wayland display
if [ -n "$WAYLAND_DISPLAY" ]; then
    export WAYLAND_DISPLAY
fi

# Preserve D-Bus session bus for browser authentication
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    if [ -S "/run/user/$(id -u)/bus" ]; then
        export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
    fi
fi

# Preserve XAUTHORITY for X11 authentication
if [ -z "$XAUTHORITY" ] && [ -f "$HOME/.Xauthority" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
fi

# Build base command
BASE_CMD="antigravity --user-data-dir \"$PROFILE_DIR\""

# Apply namespace isolation if enabled
# NOTE: We do NOT use IPC namespace in full mode to preserve D-Bus access
if [ "$USE_NAMESPACES" = "true" ] && [ "$NAMESPACE_MODE" != "none" ]; then
    if command -v unshare >/dev/null 2>&1; then
        case "$NAMESPACE_MODE" in
            "full")
                # Full namespace isolation (without IPC to preserve D-Bus for browser auth)
                # IPC namespace would break D-Bus communication with host browser
                CMD="unshare --mount --pid --user --uts --fork --mount-proc -- bash -c 'export DISPLAY=\"$DISPLAY\"; export WAYLAND_DISPLAY=\"$WAYLAND_DISPLAY\"; export DBUS_SESSION_BUS_ADDRESS=\"$DBUS_SESSION_BUS_ADDRESS\"; export XAUTHORITY=\"$XAUTHORITY\"; $BASE_CMD'"
                ;;
            "mount")
                # Mount namespace only (filesystem isolation)
                CMD="unshare --mount --fork -- bash -c 'export DISPLAY=\"$DISPLAY\"; export WAYLAND_DISPLAY=\"$WAYLAND_DISPLAY\"; export DBUS_SESSION_BUS_ADDRESS=\"$DBUS_SESSION_BUS_ADDRESS\"; export XAUTHORITY=\"$XAUTHORITY\"; $BASE_CMD'"
                ;;
            "user")
                # User namespace only (UID/GID isolation)
                CMD="unshare --user --fork -- bash -c 'export DISPLAY=\"$DISPLAY\"; export WAYLAND_DISPLAY=\"$WAYLAND_DISPLAY\"; export DBUS_SESSION_BUS_ADDRESS=\"$DBUS_SESSION_BUS_ADDRESS\"; export XAUTHORITY=\"$XAUTHORITY\"; $BASE_CMD'"
                ;;
            *)
                # Fallback to no namespace
                CMD="$BASE_CMD"
                ;;
        esac
    else
        echo "⚠️  Warning: unshare not found, falling back to directory-based isolation"
        CMD="$BASE_CMD"
    fi
else
    CMD="$BASE_CMD"
fi

# Launch Antigravity in background
nohup bash -c "$CMD" > "$PROFILE_DIR/antigravity.log" 2>&1 &

echo "Launched Antigravity with profile: $PROFILE_NAME (namespace mode: ${NAMESPACE_MODE:-none})"
exit 0

