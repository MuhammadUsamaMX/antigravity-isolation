"""
Namespace Manager - Handle Linux namespace isolation for Antigravity profiles
Provides stronger isolation using mount, PID, user, and UTS namespaces
"""
import os
import subprocess
import ctypes
import ctypes.util
from ctypes import c_int, c_void_p, c_char_p

# Linux namespace constants
CLONE_NEWNS = 0x00020000      # Mount namespace
CLONE_NEWPID = 0x20000000     # PID namespace
CLONE_NEWUSER = 0x10000000    # User namespace
CLONE_NEWUTS = 0x04000000     # UTS namespace (hostname)
CLONE_NEWIPC = 0x08000000     # IPC namespace
CLONE_NEWNET = 0x40000000     # Network namespace (usually disabled for browsers)

# For unshare syscall
libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
libc.unshare.argtypes = [c_int]
libc.unshare.restype = c_int

class NamespaceManager:
    """Manage Linux namespaces for profile isolation"""
    
    def __init__(self, use_network_namespace=False):
        """
        Initialize namespace manager
        
        Args:
            use_network_namespace: If True, use network namespace (may break browser functionality)
        """
        self.use_network_namespace = use_network_namespace
        self._check_namespace_support()
    
    def _check_namespace_support(self):
        """Check if namespaces are supported on this system"""
        try:
            # Check if unshare command exists
            result = subprocess.run(['which', 'unshare'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError("unshare command not found. Install util-linux package.")
            
            # Check if we have necessary capabilities
            # User namespaces typically don't require root, but others might
            try:
                result = subprocess.run(['unshare', '--help'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode != 0:
                    raise RuntimeError("unshare command not working properly")
            except Exception as e:
                print(f"⚠️  Warning: Namespace support check failed: {e}")
        except Exception as e:
            print(f"⚠️  Warning: {e}")
    
    def create_namespace_command(self, profile_name, profile_dir, command, env=None):
        """
        Create a command that runs in isolated namespaces
        IMPORTANT: Preserves host browser authentication by maintaining access to:
        - X11/Wayland display server
        - D-Bus session bus (for browser communication)
        - Network access to localhost
        
        Args:
            profile_name: Name of the profile
            profile_dir: Profile directory path
            command: Command to run (list of strings)
            env: Environment variables dict
            
        Returns:
            List of command arguments with unshare wrapper
        """
        # Build unshare command with namespace flags
        unshare_flags = []
        
        # Mount namespace - isolate filesystem view
        unshare_flags.append('--mount')
        
        # PID namespace - isolate process tree
        unshare_flags.append('--pid')
        
        # User namespace - isolate UID/GID (doesn't require root)
        unshare_flags.append('--user')
        
        # UTS namespace - isolate hostname
        unshare_flags.append('--uts')
        
        # CRITICAL: We do NOT use IPC namespace to preserve D-Bus access for browser authentication
        # IPC namespace would break D-Bus communication with host browser
        # This ensures Antigravity can authenticate using the host browser
        
        # Network namespace (optional - usually disabled for browsers)
        # Network namespace breaks browser authentication, so we skip it by default
        if self.use_network_namespace:
            unshare_flags.append('--net')
        
        # Build the full command
        # We use unshare with --fork to create a new process in the namespace
        # and --mount-proc to mount a new /proc in the PID namespace
        unshare_cmd = ['unshare'] + unshare_flags + [
            '--fork',
            '--mount-proc',  # Mount new /proc for PID namespace
            '--',
        ]
        
        # Create setup script that preserves browser authentication
        setup_script = """
# Preserve host browser authentication access
# 1. Ensure X11/Wayland display access
# 2. Preserve D-Bus session bus access
# 3. Maintain network access to localhost

# Get display from environment or use default
DISPLAY_VAR="${DISPLAY:-:0}"
WAYLAND_VAR="${WAYLAND_DISPLAY:-}"

# Preserve X11 access
if [ -n "$DISPLAY_VAR" ]; then
    export DISPLAY="$DISPLAY_VAR"
    # Ensure X11 socket is accessible
    if [ -S "/tmp/.X11-unix/X${DISPLAY_VAR#:}" ]; then
        # X11 socket exists, access should work
        :
    fi
fi

# Preserve Wayland access
if [ -n "$WAYLAND_VAR" ]; then
    export WAYLAND_DISPLAY="$WAYLAND_VAR"
fi

# Preserve D-Bus session bus for browser authentication
if [ -n "$DBUS_SESSION_BUS_ADDRESS" ]; then
    export DBUS_SESSION_BUS_ADDRESS
elif [ -S "/run/user/$(id -u)/bus" ]; then
    export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
fi

# Preserve XAUTHORITY for X11 authentication
if [ -n "$XAUTHORITY" ] && [ -f "$XAUTHORITY" ]; then
    export XAUTHORITY
elif [ -f "$HOME/.Xauthority" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
fi

# Set environment variables
"""
        
        # Add environment variable exports if provided
        if env:
            for key, value in env.items():
                # Escape special characters in values
                escaped_value = value.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
                setup_script += f'export {key}="{escaped_value}"\n'
        
        # Add the actual command
        setup_script += '\n# Run command with preserved browser authentication\n'
        setup_script += 'exec ' + ' '.join(f'"{arg}"' for arg in command) + '\n'
        
        # Use bash -c to run the script
        unshare_cmd.extend(['bash', '-c', setup_script])
        
        return unshare_cmd
    
    def create_mount_namespace_only(self, profile_name, profile_dir, command, env=None):
        """
        Create a simpler mount namespace isolation (less aggressive, more compatible)
        This only isolates the filesystem view using mount namespace
        IMPORTANT: Preserves host browser authentication
        
        Args:
            profile_name: Name of the profile
            profile_dir: Profile directory path
            command: Command to run (list of strings)
            env: Environment variables dict
            
        Returns:
            List of command arguments with unshare wrapper
        """
        # Use only mount namespace for better compatibility
        # This creates a private mount namespace where we can bind mount
        # the profile directory to appear as the home directory
        
        unshare_cmd = ['unshare', '--mount', '--fork', '--']
        
        # Create a script that:
        # 1. Preserves browser authentication access
        # 2. Bind mounts profile_dir to a temporary location
        # 3. Sets up the environment
        # 4. Runs the command
        
        # Build bind mount setup with browser authentication preservation
        bind_mount_script = f"""
# Preserve host browser authentication access
DISPLAY_VAR="${{DISPLAY:-:0}}"
WAYLAND_VAR="${{WAYLAND_DISPLAY:-}}"

if [ -n "$DISPLAY_VAR" ]; then
    export DISPLAY="$DISPLAY_VAR"
fi

if [ -n "$WAYLAND_VAR" ]; then
    export WAYLAND_DISPLAY="$WAYLAND_VAR"
fi

# Preserve D-Bus session bus for browser authentication
if [ -n "$DBUS_SESSION_BUS_ADDRESS" ]; then
    export DBUS_SESSION_BUS_ADDRESS
elif [ -S "/run/user/$(id -u)/bus" ]; then
    export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
fi

# Preserve XAUTHORITY for X11 authentication
if [ -n "$XAUTHORITY" ] && [ -f "$XAUTHORITY" ]; then
    export XAUTHORITY
elif [ -f "$HOME/.Xauthority" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
fi

# Create bind mount for profile isolation
PROFILE_DIR="{profile_dir}"
BIND_MOUNT="/tmp/antigravity-ns-{profile_name}"

# Create bind mount point
mkdir -p "$BIND_MOUNT"

# Bind mount profile directory (if not already mounted)
if ! mountpoint -q "$BIND_MOUNT" 2>/dev/null; then
    mount --bind "$PROFILE_DIR" "$BIND_MOUNT" 2>/dev/null || true
fi

# Set environment variables
"""
        
        if env:
            for key, value in env.items():
                # Escape special characters in values
                escaped_value = value.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
                bind_mount_script += f'export {key}="{escaped_value}"\n'
        
        # Add the actual command
        bind_mount_script += '\n# Run command with preserved browser authentication\n'
        bind_mount_script += 'exec ' + ' '.join(f'"{arg}"' for arg in command) + '\n'
        
        # Use bash -c to run the script
        unshare_cmd.extend(['bash', '-c', bind_mount_script])
        
        return unshare_cmd
    
    def create_user_namespace_only(self, profile_name, profile_dir, command, env=None):
        """
        Create user namespace isolation (lightweight, no root required)
        This provides UID/GID isolation without requiring root privileges
        IMPORTANT: Preserves host browser authentication
        
        Args:
            profile_name: Name of the profile
            profile_dir: Profile directory path
            command: Command to run (list of strings)
            env: Environment variables dict
            
        Returns:
            List of command arguments with unshare wrapper
        """
        # User namespace doesn't require root and provides basic isolation
        unshare_cmd = ['unshare', '--user', '--fork', '--']
        
        # Create setup script that preserves browser authentication
        setup_script = """
# Preserve host browser authentication access
DISPLAY_VAR="${DISPLAY:-:0}"
WAYLAND_VAR="${WAYLAND_DISPLAY:-}"

if [ -n "$DISPLAY_VAR" ]; then
    export DISPLAY="$DISPLAY_VAR"
fi

if [ -n "$WAYLAND_VAR" ]; then
    export WAYLAND_DISPLAY="$WAYLAND_VAR"
fi

# Preserve D-Bus session bus for browser authentication
if [ -n "$DBUS_SESSION_BUS_ADDRESS" ]; then
    export DBUS_SESSION_BUS_ADDRESS
elif [ -S "/run/user/$(id -u)/bus" ]; then
    export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
fi

# Preserve XAUTHORITY for X11 authentication
if [ -n "$XAUTHORITY" ] && [ -f "$XAUTHORITY" ]; then
    export XAUTHORITY
elif [ -f "$HOME/.Xauthority" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
fi

# Set environment variables
"""
        
        if env:
            for key, value in env.items():
                # Escape special characters in values
                escaped_value = value.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
                setup_script += f'export {key}="{escaped_value}"\n'
        
        # Add the actual command
        setup_script += '\n# Run command with preserved browser authentication\n'
        setup_script += 'exec ' + ' '.join(f'"{arg}"' for arg in command) + '\n'
        
        unshare_cmd.extend(['bash', '-c', setup_script])
        
        return unshare_cmd
    
    def get_namespace_info(self, pid):
        """
        Get namespace information for a process
        
        Args:
            pid: Process ID
            
        Returns:
            Dict with namespace information
        """
        info = {}
        
        try:
            # Read namespace IDs from /proc
            for ns_type in ['mnt', 'pid', 'user', 'uts', 'ipc', 'net']:
                ns_path = f'/proc/{pid}/ns/{ns_type}'
                if os.path.exists(ns_path):
                    try:
                        # Read the namespace ID (it's a symlink)
                        ns_id = os.readlink(ns_path)
                        info[ns_type] = ns_id
                    except:
                        pass
        except:
            pass
        
        return info
    
    def is_in_namespace(self, pid):
        """
        Check if a process is running in a namespace
        
        Args:
            pid: Process ID
            
        Returns:
            True if process is in a namespace, False otherwise
        """
        try:
            # Check if process has different namespace IDs than init (PID 1)
            proc_info = self.get_namespace_info(pid)
            init_info = self.get_namespace_info(1)
            
            # Compare namespace IDs
            for ns_type in proc_info:
                if ns_type in init_info:
                    if proc_info[ns_type] != init_info[ns_type]:
                        return True
            
            return False
        except:
            return False

