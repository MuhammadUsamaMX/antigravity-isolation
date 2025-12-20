# Host Browser Authentication

This document explains how the Antigravity Isolation Manager ensures all profiles are authenticated by the host browser, even when using namespace-level isolation.

## Overview

Antigravity uses the host browser for authentication. This means that even with namespace isolation, each profile must maintain access to:

1. **D-Bus Session Bus** - For browser communication
2. **X11/Wayland Display** - For GUI and browser interaction
3. **XAUTHORITY** - For X11 authentication
4. **Network Access** - For localhost browser communication

## Implementation Details

### Namespace Isolation Considerations

When using namespace isolation, we must be careful to preserve browser authentication:

#### ✅ What We Do

1. **Preserve D-Bus Access**
   - We do **NOT** use IPC namespace in full isolation mode
   - IPC namespace would break D-Bus communication with the host browser
   - D-Bus session bus address is explicitly preserved in environment

2. **Preserve Display Access**
   - X11/Wayland display variables are preserved
   - XAUTHORITY is set to allow X11 authentication
   - X11 socket access is maintained

3. **Preserve Network Access**
   - Network namespace is disabled by default (breaks browser functionality)
   - Localhost communication is maintained

#### ❌ What We Avoid

1. **IPC Namespace in Full Mode**
   - Would break D-Bus communication
   - Browser authentication requires D-Bus

2. **Network Namespace**
   - Disabled by default
   - Would break localhost browser communication

### Code Implementation

#### Namespace Manager

All namespace creation methods preserve browser authentication:

```python
# In create_namespace_command, create_mount_namespace_only, create_user_namespace_only:
# 1. Preserve DISPLAY and WAYLAND_DISPLAY
# 2. Preserve DBUS_SESSION_BUS_ADDRESS
# 3. Preserve XAUTHORITY
```

#### Process Manager

The process manager ensures browser authentication is set up:

```python
# Preserve D-Bus session bus for browser authentication
if 'DBUS_SESSION_BUS_ADDRESS' not in env:
    dbus_socket = f'/run/user/{os.getuid()}/bus'
    if os.path.exists(dbus_socket):
        env['DBUS_SESSION_BUS_ADDRESS'] = f'unix:path={dbus_socket}'

# Preserve XAUTHORITY for X11 authentication
if 'XAUTHORITY' not in env:
    xauth_file = os.path.expanduser('~/.Xauthority')
    if os.path.exists(xauth_file):
        env['XAUTHORITY'] = xauth_file
```

#### Launcher Script

The launcher script preserves browser authentication:

```bash
# Preserve host browser authentication - CRITICAL for Antigravity
export DISPLAY="${DISPLAY:-:0}"
export WAYLAND_DISPLAY

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
```

## Namespace Modes and Browser Authentication

### Mount Namespace Mode (`mount`)
- ✅ **Browser Authentication**: Fully preserved
- ✅ **D-Bus Access**: Maintained
- ✅ **Display Access**: Maintained
- ✅ **Recommended**: Yes, best balance of isolation and compatibility

### User Namespace Mode (`user`)
- ✅ **Browser Authentication**: Fully preserved
- ✅ **D-Bus Access**: Maintained
- ✅ **Display Access**: Maintained
- ✅ **Recommended**: Yes, lightweight isolation

### Full Namespace Mode (`full`)
- ✅ **Browser Authentication**: Fully preserved
- ⚠️ **IPC Namespace**: **NOT used** (preserves D-Bus)
- ✅ **D-Bus Access**: Maintained (IPC namespace disabled)
- ✅ **Display Access**: Maintained
- ✅ **Recommended**: Yes, maximum isolation while preserving browser auth

### No Namespace Mode (`none`)
- ✅ **Browser Authentication**: Fully preserved
- ✅ **D-Bus Access**: Native access
- ✅ **Display Access**: Native access
- ✅ **Recommended**: Yes, maximum compatibility

## Verification

To verify browser authentication is working:

1. **Check D-Bus Access**:
   ```bash
   echo $DBUS_SESSION_BUS_ADDRESS
   # Should show: unix:path=/run/user/[UID]/bus
   ```

2. **Check X11 Access**:
   ```bash
   echo $DISPLAY
   echo $XAUTHORITY
   xhost
   ```

3. **Test Browser Communication**:
   - Launch an Antigravity profile
   - Attempt to authenticate
   - Should successfully use host browser for authentication

## Troubleshooting

### Browser Authentication Fails

1. **Check D-Bus**:
   ```bash
   ls -la /run/user/$(id -u)/bus
   # Should exist and be accessible
   ```

2. **Check X11**:
   ```bash
   xhost
   # Should allow local connections
   ```

3. **Check Environment Variables**:
   ```bash
   env | grep -E "(DISPLAY|WAYLAND|DBUS|XAUTHORITY)"
   ```

4. **Disable Namespace Isolation** (if needed):
   ```bash
   export ANTIGRAVITY_USE_NAMESPACES=false
   # or
   export ANTIGRAVITY_NAMESPACE_MODE=none
   ```

### D-Bus Connection Errors

If you see D-Bus connection errors:

1. Ensure IPC namespace is NOT used in full mode
2. Check that `DBUS_SESSION_BUS_ADDRESS` is set correctly
3. Verify D-Bus socket exists: `/run/user/[UID]/bus`

## Summary

All Antigravity profiles are authenticated by the host browser, regardless of namespace isolation mode. The system explicitly preserves:

- ✅ D-Bus session bus access
- ✅ X11/Wayland display access
- ✅ XAUTHORITY for X11 authentication
- ✅ Network access to localhost

This ensures that namespace isolation provides security benefits without breaking browser authentication functionality.

