"""
Process Manager - Handle native Antigravity process lifecycle operations
"""
import os
import subprocess
import psutil
import signal
import time
from config import (ANTIGRAVITY_PROFILES_DIR, 
                   USE_NAMESPACE_ISOLATION, NAMESPACE_MODE, USE_NETWORK_NAMESPACE)
from desktop_entry_manager import DesktopEntryManager
from namespace_manager import NamespaceManager

class ProcessManager:
    def __init__(self):
        # Initialize desktop entry manager for creating desktop entries
        launcher_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       'scripts', 'antigravity-launcher.sh')
        self.desktop_mgr = DesktopEntryManager(launcher_script)
        self.antigravity_command = self._find_antigravity_command()
        
        # Initialize namespace manager if namespace isolation is enabled
        self.use_namespaces = USE_NAMESPACE_ISOLATION and NAMESPACE_MODE != 'none'
        if self.use_namespaces:
            try:
                self.namespace_mgr = NamespaceManager(use_network_namespace=USE_NETWORK_NAMESPACE)
                print(f"✅ Namespace isolation enabled (mode: {NAMESPACE_MODE})")
            except Exception as e:
                print(f"⚠️  Failed to initialize namespace manager: {e}")
                print("   Falling back to directory-based isolation")
                self.use_namespaces = False
                self.namespace_mgr = None
        else:
            self.namespace_mgr = None
    
    def _find_antigravity_command(self):
        """Find the Antigravity executable"""
        # Common locations for Antigravity
        possible_paths = [
            '/usr/bin/antigravity',
            '/usr/local/bin/antigravity',
            os.path.expanduser('~/.local/bin/antigravity'),
        ]
        
        # Check if antigravity is in PATH
        try:
            result = subprocess.run(['which', 'antigravity'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
        
        # Check common paths
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # Default fallback
        return 'antigravity'
    
    def get_profile_dir(self, profile_name):
        """Get profile directory path"""
        return os.path.join(ANTIGRAVITY_PROFILES_DIR, profile_name)
    
    def get_config_dir(self, profile_name):
        """Get Antigravity config directory for profile"""
        # Antigravity typically stores config in ~/.config/antigravity or similar
        # We'll use a profile-specific subdirectory
        profile_dir = self.get_profile_dir(profile_name)
        return os.path.join(profile_dir, '.config')
    
    def _get_process_by_profile(self, profile_name):
        """Find running Antigravity process for a profile"""
        profile_dir = os.path.abspath(self.get_profile_dir(profile_name))
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info.get('name', '') or ''
                if 'antigravity' in proc_name.lower():
                    # Check command line for --user-data-dir flag
                    cmdline = proc.info.get('cmdline') or []
                    cmdline_str = ' '.join(cmdline)
                    
                    # Look for --user-data-dir in command line
                    if '--user-data-dir' in cmdline_str:
                        # Find the value after --user-data-dir
                        for i, arg in enumerate(cmdline):
                            if arg == '--user-data-dir' and i + 1 < len(cmdline):
                                data_dir = os.path.abspath(os.path.expanduser(cmdline[i + 1]))
                                if data_dir == profile_dir:
                                    return proc
                            elif arg.startswith('--user-data-dir='):
                                # Handle --user-data-dir=path format
                                data_dir = os.path.abspath(os.path.expanduser(arg.split('=', 1)[1]))
                                if data_dir == profile_dir:
                                    return proc
                    
                    # Also check environment variables for ANTIGRAVITY_HOME
                    try:
                        environ = proc.environ()
                        if environ:
                            home_dir = environ.get('ANTIGRAVITY_HOME')
                            if home_dir and os.path.abspath(os.path.expanduser(home_dir)) == profile_dir:
                                return proc
                    except (psutil.AccessDenied, KeyError, AttributeError):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return None
    
    def container_status(self, profile_name):
        """Get process status (compatible API for namespace-isolated processes)"""
        proc = self._get_process_by_profile(profile_name)
        if proc:
            try:
                if proc.is_running():
                    return "running"
                else:
                    return "exited"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return "not_found"
        return "not_found"
    
    def start_container(self, profile_name):
        """Start an Antigravity process for the profile"""
        profile_dir = self.get_profile_dir(profile_name)
        config_dir = self.get_config_dir(profile_name)
        downloads_dir = os.path.join(profile_dir, "Downloads")
        
        # Create directories if they don't exist
        os.makedirs(profile_dir, exist_ok=True)
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Check if process already running
        proc = self._get_process_by_profile(profile_name)
        if proc:
            try:
                if proc.is_running():
                    return {"status": "already_running"}
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Create desktop entry if it doesn't exist
        if not self.desktop_mgr.desktop_entry_exists(profile_name):
            try:
                self.desktop_mgr.create_desktop_entry(profile_name)
                print(f"✅ Created desktop entry for profile: {profile_name}")
            except Exception as e:
                print(f"⚠️  Failed to create desktop entry: {e}")
        
        # Launch Antigravity with profile-specific configuration
        # Antigravity is an Electron app and uses --user-data-dir flag for data isolation
        # When launched from systemd, we need to get the user's display session
        env = os.environ.copy()
        
        # Get the actual user's display (not systemd's)
        # Try to get DISPLAY from the user's session
        user = os.getenv('USER') or os.getenv('LOGNAME') or os.getlogin()
        
        # Try to get DISPLAY from active user sessions
        try:
            import pwd
            user_info = pwd.getpwnam(user)
            # Check for common display locations
            for display_var in ['DISPLAY', 'WAYLAND_DISPLAY']:
                # Try to get from systemd user session
                result = subprocess.run(
                    ['systemctl', '--user', 'show-environment'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith(f'{display_var}='):
                            env[display_var] = line.split('=', 1)[1]
                            break
        except:
            pass
        
        # Fallback to default display
        if 'DISPLAY' not in env:
            env['DISPLAY'] = ':0'
        
        # CRITICAL: Preserve host browser authentication
        # Antigravity uses the host browser for authentication, so we must preserve:
        # 1. D-Bus session bus access (for browser communication)
        # 2. XAUTHORITY for X11 authentication
        # 3. Wayland display access
        
        # Preserve D-Bus session bus for browser authentication
        if 'DBUS_SESSION_BUS_ADDRESS' not in env:
            # Try to get D-Bus address from user session
            dbus_socket = f'/run/user/{os.getuid()}/bus'
            if os.path.exists(dbus_socket):
                env['DBUS_SESSION_BUS_ADDRESS'] = f'unix:path={dbus_socket}'
            else:
                # Try to get from systemd user session
                try:
                    result = subprocess.run(
                        ['systemctl', '--user', 'show-environment'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line.startswith('DBUS_SESSION_BUS_ADDRESS='):
                                env['DBUS_SESSION_BUS_ADDRESS'] = line.split('=', 1)[1]
                                break
                except:
                    pass
        
        # Preserve XAUTHORITY for X11 authentication
        if 'XAUTHORITY' not in env:
            xauth_file = os.path.expanduser('~/.Xauthority')
            if os.path.exists(xauth_file):
                env['XAUTHORITY'] = xauth_file
        
        # Try both ANTIGRAVITY_HOME (if supported) and --user-data-dir (Electron standard)
        env['ANTIGRAVITY_HOME'] = profile_dir
        
        # Launch Antigravity with --user-data-dir flag (Electron/Chromium standard)
        # Use dbus-launch or run in user session to ensure window appears
        base_cmd = [
            self.antigravity_command,
            '--user-data-dir', profile_dir
        ]
        
        # Apply namespace isolation if enabled
        if self.use_namespaces and self.namespace_mgr:
            try:
                if NAMESPACE_MODE == 'full':
                    # Full namespace isolation (mount, PID, user, UTS, IPC)
                    cmd = self.namespace_mgr.create_namespace_command(
                        profile_name, profile_dir, base_cmd, env
                    )
                elif NAMESPACE_MODE == 'mount':
                    # Mount namespace only (filesystem isolation)
                    cmd = self.namespace_mgr.create_mount_namespace_only(
                        profile_name, profile_dir, base_cmd, env
                    )
                elif NAMESPACE_MODE == 'user':
                    # User namespace only (UID/GID isolation)
                    cmd = self.namespace_mgr.create_user_namespace_only(
                        profile_name, profile_dir, base_cmd, env
                    )
                else:
                    # Fallback to no namespace
                    cmd = base_cmd
            except Exception as e:
                print(f"⚠️  Failed to create namespace command: {e}")
                print("   Falling back to directory-based isolation")
                cmd = base_cmd
        else:
            cmd = base_cmd
        
        try:
            log_file = os.path.join(profile_dir, 'antigravity.log')
            
            # Best approach: Use the launcher script which runs in user session
            # Get the launcher script path
            launcher_script = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'scripts', 'antigravity-launcher.sh'
            )
            
            # If launcher script exists, use it - it will launch in user's session
            if os.path.exists(launcher_script):
                try:
                    # Get the logged-in user
                    result = subprocess.run(
                        ['who'], capture_output=True, text=True, timeout=2
                    )
                    session_user = None
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line.strip():
                                parts = line.split()
                                if parts:
                                    session_user = parts[0]
                                    break
                    
                    # Try to execute launcher script as the logged-in user
                    if session_user:
                        try:
                            # Use runuser to execute as the logged-in user
                            runuser_cmd = [
                                'runuser', '-u', session_user, '--',
                                'bash', launcher_script, profile_name
                            ]
                            process = subprocess.Popen(
                                runuser_cmd,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                start_new_session=True
                            )
                            time.sleep(1)
                            if process.poll() is None or process.returncode == 0:
                                return {"status": "created", "pid": "launcher-script"}
                        except (FileNotFoundError, PermissionError):
                            # Fallback: try su
                            try:
                                su_cmd = ['su', '-', session_user, '-c', 
                                         f'bash {launcher_script} {profile_name}']
                                process = subprocess.Popen(
                                    su_cmd,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    start_new_session=True
                                )
                                time.sleep(1)
                                if process.poll() is None or process.returncode == 0:
                                    return {"status": "created", "pid": "launcher-script"}
                            except:
                                pass
                except:
                    pass
            
            # Fallback: Direct launch (may not show window if launched from systemd)
            with open(log_file, 'a') as log:
                # Ensure X11 access for browser authentication
                # XAUTHORITY and DBUS_SESSION_BUS_ADDRESS should already be set above
                if env.get('DISPLAY', '').startswith(':'):
                    # Double-check XAUTHORITY is set (for browser authentication)
                    if 'XAUTHORITY' not in env:
                        xauth_file = os.path.expanduser('~/.Xauthority')
                        if os.path.exists(xauth_file):
                            env['XAUTHORITY'] = xauth_file
                    # Allow X11 access (required for browser authentication)
                    try:
                        subprocess.run(['xhost', '+local:'], timeout=1, 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except:
                        pass
                
                # For namespace isolation, we need to pass env differently
                # Namespace commands handle env internally
                if self.use_namespaces and NAMESPACE_MODE in ['full', 'mount', 'user']:
                    # Namespace manager handles environment internally
                    process = subprocess.Popen(
                        cmd,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                        cwd=profile_dir
                    )
                else:
                    # Standard launch with environment
                    process = subprocess.Popen(
                        cmd,
                        env=env,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                        cwd=profile_dir
                    )
            
            # Give it a moment to start
            import time
            time.sleep(1)
            
            # Check if it's still running
            if process.poll() is None:
                return {"status": "created", "pid": process.pid}
            else:
                # Process exited, try to read error from log
                error_msg = "Process exited immediately"
                try:
                    if os.path.exists(log_file):
                        with open(log_file, 'r') as f:
                            last_lines = f.readlines()[-5:]
                            if last_lines:
                                error_msg = f"Process exited: {''.join(last_lines).strip()}"
                except:
                    pass
                return {"status": "failed", "error": error_msg}
                
        except FileNotFoundError:
            return {"status": "failed", "error": f"Antigravity not found at {self.antigravity_command}"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def stop_container(self, profile_name):
        """Stop a process"""
        proc = self._get_process_by_profile(profile_name)
        if proc:
            try:
                # Terminate gracefully first
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    proc.kill()
                return {"status": "stopped"}
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                return {"status": "not_found", "error": str(e)}
        return {"status": "not_found"}
    
    def remove_container(self, profile_name):
        """Stop and cleanup process (compatible API for namespace-isolated processes)"""
        return self.stop_container(profile_name)
    
    def get_profile_size(self, profile_name):
        """Get profile directory size in MB"""
        profile_dir = self.get_profile_dir(profile_name)
        if not os.path.exists(profile_dir):
            return 0
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(profile_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        
        return round(total_size / (1024 * 1024), 2)  # Convert to MB

