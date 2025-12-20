#!/bin/bash

# Antigravity Launcher Script
# This script is called by desktop entries to launch isolated Antigravity profiles
# It launches Antigravity directly in the user's session (not via API)

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

# Launch Antigravity directly with the profile directory
# This runs in the user's session, so the window will appear
export ANTIGRAVITY_HOME="$PROFILE_DIR"

# Launch Antigravity in background
nohup antigravity --user-data-dir "$PROFILE_DIR" > "$PROFILE_DIR/antigravity.log" 2>&1 &

echo "Launched Antigravity with profile: $PROFILE_NAME"
exit 0

