# Namespace-Level Isolation

This document explains the namespace-level isolation feature for Antigravity Isolation Manager.

## Overview

Linux namespaces provide kernel-level isolation between processes. This implementation adds namespace support to provide stronger isolation than directory-based separation alone.

## Namespace Types

The system supports multiple namespace isolation modes:

### 1. **Mount Namespace** (`mount`)
- **Isolation**: Filesystem view
- **Benefits**: Each profile sees an isolated filesystem view
- **Compatibility**: High - works well with browsers
- **Requirements**: No special privileges needed

### 2. **User Namespace** (`user`)
- **Isolation**: UID/GID mapping
- **Benefits**: Process runs with isolated user/group IDs
- **Compatibility**: High - doesn't require root
- **Requirements**: No special privileges needed

### 3. **Full Namespace Isolation** (`full`)
- **Isolation**: Mount + PID + User + UTS + IPC namespaces
- **Benefits**: Maximum isolation
- **Compatibility**: Medium - may have issues with some desktop environments
- **Requirements**: May require root for some namespace types

### 4. **No Namespace** (`none`)
- **Isolation**: Directory-based only (original behavior)
- **Benefits**: Maximum compatibility
- **Compatibility**: Highest

## Configuration

Namespace isolation is controlled by environment variables:

### Enable/Disable Namespaces

```bash
# Enable namespace isolation (default: true)
export ANTIGRAVITY_USE_NAMESPACES=true

# Disable namespace isolation
export ANTIGRAVITY_USE_NAMESPACES=false
```

### Set Namespace Mode

```bash
# Mount namespace only (recommended)
export ANTIGRAVITY_NAMESPACE_MODE=mount

# User namespace only
export ANTIGRAVITY_NAMESPACE_MODE=user

# Full namespace isolation
export ANTIGRAVITY_NAMESPACE_MODE=full

# Disable namespaces (directory-based only)
export ANTIGRAVITY_NAMESPACE_MODE=none
```

### Network Namespace (Advanced)

```bash
# Enable network namespace (usually not recommended for browsers)
export ANTIGRAVITY_USE_NET_NS=true
```

**Warning**: Network namespaces can break browser functionality as they isolate the network stack. Only enable if you understand the implications.

## Usage Examples

### Example 1: Enable Mount Namespace Isolation

```bash
export ANTIGRAVITY_USE_NAMESPACES=true
export ANTIGRAVITY_NAMESPACE_MODE=mount
./install.sh
```

### Example 2: Use Full Isolation

```bash
export ANTIGRAVITY_USE_NAMESPACES=true
export ANTIGRAVITY_NAMESPACE_MODE=full
./install.sh
```

### Example 3: Disable Namespace Isolation

```bash
export ANTIGRAVITY_USE_NAMESPACES=false
# or
export ANTIGRAVITY_NAMESPACE_MODE=none
./install.sh
```

## How It Works

### Process Launch Flow

1. **Profile Creation**: Profile directory created at `~/Antigravity/[ProfileName]`

2. **Namespace Creation**: When starting a profile:
   - System calls `unshare` with appropriate namespace flags
   - Creates isolated namespace(s) for the process
   - Launches Antigravity within the namespace

3. **Isolation**: Process runs with:
   - Isolated filesystem view (mount namespace)
   - Isolated process tree (PID namespace)
   - Isolated UID/GID (user namespace)
   - Isolated hostname (UTS namespace)
   - Isolated IPC (IPC namespace)

### Technical Details

The namespace isolation is implemented in:

- **`app/namespace_manager.py`**: Core namespace management logic
- **`app/process_manager.py`**: Integration with process launching
- **`scripts/antigravity-launcher.sh`**: Shell script support for desktop entries

## Benefits of Namespace Isolation

1. **Stronger Security**: Processes cannot see or access other profiles' data
2. **Process Isolation**: Each profile has its own process tree
3. **Filesystem Isolation**: Each profile sees an isolated filesystem view
4. **Resource Isolation**: Better separation of resources

## Limitations

1. **Desktop Integration**: Full namespace isolation may interfere with desktop environment integration
2. **X11/Wayland**: Some namespace modes may require additional configuration for display access
3. **Network**: Network namespaces can break browser functionality
4. **Root Requirements**: Some namespace types may require root privileges

## Troubleshooting

### Namespace Isolation Not Working

1. **Check if unshare is available**:
   ```bash
   which unshare
   ```

2. **Install util-linux if missing**:
   ```bash
   sudo apt install util-linux  # Debian/Ubuntu
   sudo dnf install util-linux # Fedora/RHEL
   ```

3. **Check namespace support**:
   ```bash
   unshare --help
   ```

### Process Won't Start with Namespaces

1. **Try mount namespace only** (most compatible):
   ```bash
   export ANTIGRAVITY_NAMESPACE_MODE=mount
   ```

2. **Disable namespace isolation**:
   ```bash
   export ANTIGRAVITY_NAMESPACE_MODE=none
   ```

3. **Check logs**:
   ```bash
   cat ~/Antigravity/[ProfileName]/antigravity.log
   ```

### Desktop Entry Not Working

If desktop entries don't work with namespace isolation:

1. The launcher script automatically detects namespace settings
2. Check environment variables are set correctly
3. Try disabling namespace isolation for desktop entries

## Recommendations

- **For Most Users**: Use `mount` namespace mode (good balance of isolation and compatibility)
- **For Maximum Security**: Use `full` namespace mode (may require additional configuration)
- **For Maximum Compatibility**: Use `none` (directory-based isolation only)

## See Also

- [Linux Namespaces Documentation](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [unshare(1) Manual](https://man7.org/linux/man-pages/man1/unshare.1.html)

