"""
Desktop Entry Manager - Handle .desktop file creation and management
Manages desktop entries for namespace-isolated Antigravity profiles
"""
import os
from config import DESKTOP_ENTRIES_DIR

class DesktopEntryManager:
    def __init__(self, launcher_script_path):
        self.launcher_script_path = os.path.abspath(launcher_script_path)
    
    def get_desktop_file_path(self, profile_name):
        """Get desktop entry file path"""
        return os.path.join(DESKTOP_ENTRIES_DIR, f"antigravity-{profile_name}.desktop")
    
    def create_desktop_entry(self, profile_name):
        """Create a .desktop file for the profile"""
        desktop_file = self.get_desktop_file_path(profile_name)
        
        content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Antigravity ({profile_name})
Comment=Isolated Antigravity Profile: {profile_name}
Exec={self.launcher_script_path} {profile_name}
Icon=antigravity
Terminal=false
Categories=Network;WebBrowser;
StartupWMClass=antigravity-{profile_name}
"""
        
        with open(desktop_file, 'w') as f:
            f.write(content)
        
        # Make executable
        os.chmod(desktop_file, 0o755)
        
        # Update desktop database
        os.system(f'update-desktop-database {DESKTOP_ENTRIES_DIR} > /dev/null 2>&1')
        
        return {"status": "created", "path": desktop_file}
    
    def remove_desktop_entry(self, profile_name):
        """Remove desktop entry file"""
        desktop_file = self.get_desktop_file_path(profile_name)
        
        if os.path.exists(desktop_file):
            os.remove(desktop_file)
            os.system(f'update-desktop-database {DESKTOP_ENTRIES_DIR} > /dev/null 2>&1')
            return {"status": "removed"}
        
        return {"status": "not_found"}
    
    def desktop_entry_exists(self, profile_name):
        """Check if desktop entry exists"""
        return os.path.exists(self.get_desktop_file_path(profile_name))



