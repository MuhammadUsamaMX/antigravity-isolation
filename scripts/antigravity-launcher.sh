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

# Test if unshare is available and permitted
# If not, disable namespace isolation automatically
if [ "$USE_NAMESPACES" = "true" ] && [ "$NAMESPACE_MODE" != "none" ]; then
    if ! command -v unshare >/dev/null 2>&1; then
        USE_NAMESPACES="false"
    elif ! unshare --mount --fork true 2>/dev/null; then
        # unshare not permitted, disable namespace isolation
        USE_NAMESPACES="false"
        echo "⚠️  Namespace isolation not permitted, using directory-based isolation" >> "$PROFILE_DIR/antigravity.log"
    fi
fi

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

# Apply namespace isolation if enabled and permitted
# NOTE: We do NOT use IPC namespace in full mode to preserve D-Bus access
if [ "$USE_NAMESPACES" = "true" ] && [ "$NAMESPACE_MODE" != "none" ]; then
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
    CMD="$BASE_CMD"
fi

# Launch Antigravity in background
# If namespace command fails, it will fall back to direct launch
nohup bash -c "$CMD" >> "$PROFILE_DIR/antigravity.log" 2>&1 &
LAUNCH_PID=$!

# Wait a moment and check if the command actually started
sleep 1
if ! kill -0 $LAUNCH_PID 2>/dev/null; then
    # Command failed, check if it was a namespace error
    if [ -s "$PROFILE_DIR/antigravity.log" ] && grep -q "Operation not permitted\|unshare failed" "$PROFILE_DIR/antigravity.log" 2>/dev/null; then
        echo "⚠️  Namespace isolation failed, retrying without namespaces..." >> "$PROFILE_DIR/antigravity.log"
        # Retry without namespace isolation
        nohup bash -c "$BASE_CMD" >> "$PROFILE_DIR/antigravity.log" 2>&1 &
    fi
fi

echo "Launched Antigravity with profile: $PROFILE_NAME (namespace mode: ${NAMESPACE_MODE:-none})"
exit 0

