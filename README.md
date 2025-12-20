# 🔒 Antigravity Isolation Manager

<div align="center">

![Antigravity Isolation Manager](https://img.shields.io/badge/Antigravity-Isolation-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Linux-orange?style=for-the-badge&logo=linux)

**A complete web-based solution for managing isolated Antigravity application profiles on Linux**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Namespace Isolation](NAMESPACE_ISOLATION.md) • [Browser Authentication](BROWSER_AUTHENTICATION.md)

</div>

---

## 🌟 Overview

Antigravity Isolation Manager is a powerful, production-ready web application that allows you to run multiple isolated Antigravity application instances on Linux. Each profile runs natively with complete data isolation, while maintaining seamless desktop integration.

**Note**: Antigravity uses the host browser for authentication. All profiles are authenticated by the host browser, ensuring proper authentication even with namespace-level isolation. The system preserves D-Bus session bus access, X11/Wayland display access, and XAUTHORITY to maintain browser authentication functionality.

Perfect for:
- 🏢 **Work/Personal Separation** - Keep work and personal Antigravity instances completely isolated
- 🔐 **Privacy & Security** - Contain potentially risky activities
- 👥 **Multi-Account Management** - Different profiles for different accounts
- 🧪 **Testing & Development** - Clean environments for development
- 🛡️ **Enhanced Security** - Isolated data with no cross-contamination

## ✨ Features

### 🌐 Modern Web Dashboard
- **Completely revamped modern UI** with dark theme and glassmorphism effects
- Intuitive, responsive interface for managing all your profiles
- Real-time status updates (auto-refresh every 5s)
- Beautiful gradient backgrounds and smooth animations
- Toast notifications and modal dialogs (no browser alerts)
- Modern profile cards with status indicators and storage usage
- React-like component architecture for maintainability

### 🔐 Complete Isolation
- **Namespace-Level Isolation** - Kernel-level isolation using Linux namespaces
  - Mount namespace: Isolated filesystem view
  - PID namespace: Isolated process tree
  - User namespace: Isolated UID/GID mapping
  - UTS namespace: Isolated hostname
  - Configurable isolation modes (mount, user, full, none)
- Each profile uses a separate data directory
- Filesystem isolation (only profile directory used)
- No access to other profile data
- Native execution for proper browser authentication
- Profile size monitoring in the dashboard
- **Browser Authentication Preserved** - All profiles authenticated by host browser
  - D-Bus session bus access maintained
  - X11/Wayland display access preserved
  - XAUTHORITY preserved for X11 authentication
  - See [Browser Authentication Documentation](BROWSER_AUTHENTICATION.md) for details

### 🖥️ Desktop Integration
- Profiles appear as native apps in your application menu
- Desktop entries: "Antigravity (ProfileName)"
- **Auto-creation** - Desktop entries created automatically when profiles are created
- Click any profile icon to automatically start its instance
- Seamless window integration with your desktop environment

### 💾 Persistent Storage
- Profile data stored in `~/Antigravity/[ProfileName]` by default
- Custom profile locations supported
- Downloads folder automatically created
- Profile size monitoring in the dashboard

### 🎨 Modern UI/UX Design
- **Completely revamped modern interface** with dark theme
- Glassmorphism effects and backdrop blur
- Animated gradient backgrounds
- Smooth animations and transitions
- Modern card designs with hover effects
- Elegant modal dialogs with confirmation popups
- Auto-dismissing toast notifications
- Professional React-like component structure

### ⚙️ One-Command Installation
- Automated setup with dependency checking
- Systemd service integration (auto-starts on boot)
- Opens web interface automatically after installation

### 🔊 Full Feature Support
- ✅ **Namespace-Level Isolation** - Kernel-level process isolation (see [Namespace Isolation Documentation](NAMESPACE_ISOLATION.md))
- ✅ Native execution (uses host browser for authentication)
- ✅ **Browser Authentication** - All profiles authenticated by host browser (see [Browser Authentication Documentation](BROWSER_AUTHENTICATION.md))
- ✅ Profile data isolation
- ✅ Export/Import Profiles - Backup and restore profiles easily (ZIP format)
- ✅ Automatic Desktop Entry Creation
- ✅ Process management and monitoring
- ✅ Real-time profile status and size monitoring

## 📋 Requirements

- **OS**: Ubuntu 20.04+ (or Debian-based Linux)
- **Antigravity**: Antigravity application installed (see installation instructions)
- **Python**: 3.8+
- **RAM**: 4GB minimum
- **Storage**: 32GB free space

## 🚀 Installation

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd antigravity-isolation-linux

# Run the installer
./install.sh
```

The installer will:
1. ✅ Check system requirements
2. 📦 Install Python dependencies (Flask, psutil)
3. 📁 Copy files to `~/.local/share/antigravity-isolation-manager`
4. 🔧 Set up systemd service
5. 🌐 Start the web interface
6. 🎉 Open `http://localhost:5001` automatically

**Installation Location**: `~/.local/share/antigravity-isolation-manager`

After installation, you can safely delete the cloned repository - the application runs from the installation directory.

### Installing Antigravity

If Antigravity is not installed, follow these steps:

**For deb-based Linux distributions (eg. Debian, Ubuntu):**

```bash
# 1. Add the repository to sources.list.d
sudo mkdir -p /etc/apt/keyrings

curl -fsSL https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | \
  sudo gpg --dearmor --yes -o /etc/apt/keyrings/antigravity-repo-key.gpg

echo "deb [signed-by=/etc/apt/keyrings/antigravity-repo-key.gpg] https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/ antigravity-debian main" | \
  sudo tee /etc/apt/sources.list.d/antigravity.list > /dev/null

# 2. Update the package cache
sudo apt update

# 3. Install the package
sudo apt install antigravity
```

**For rpm-based Linux distributions (eg. Red Hat, Fedora, SUSE):**

```bash
# 1. Add the repository to /etc/yum.repos.d
sudo tee /etc/yum.repos.d/antigravity.repo << EOL
[antigravity-rpm]
name=Antigravity RPM Repository
baseurl=https://us-central1-yum.pkg.dev/projects/antigravity-auto-updater-dev/antigravity-rpm
enabled=1
gpgcheck=0
EOL

# 2. Update the package cache
sudo dnf makecache

# 3. Install the package
sudo dnf install antigravity
```

### Uninstallation

```bash
# From the cloned repository directory
./uninstall.sh
```

This will remove:
- Application files from `~/.local/share/antigravity-isolation-manager`
- Systemd service
- Desktop entries
- Running Antigravity processes

**Note**: Your profile data in `~/Antigravity` will be preserved. To remove it:
```bash
rm -rf ~/Antigravity
```

## 📖 Usage

### Web Interface

1. **Open the Dashboard**
   ```
   http://localhost:5001
   ```

2. **Create a Profile**
   - Click "➕ Create New Profile"
   - Enter a name (e.g., "Work", "Personal", "Project1")
   - Optionally specify a custom location
   - Click "Create"

3. **Manage Profiles**
   - **Start**: Click "▶️ Start" to launch the application
   - **Stop**: Click "⏹️ Stop" to stop the process
   - **Delete**: Click "🗑️ Delete" to remove the profile

### Desktop Integration

After creating a profile, find it in your application menu:

```
Applications → Antigravity (ProfileName)
```

Click to launch - the process auto-starts if not running!

### Command Line

```bash
# View service status
sudo systemctl status antigravity-manager.service

# View logs
sudo journalctl -u antigravity-manager.service -f

# Restart service
sudo systemctl restart antigravity-manager.service

# Stop service
sudo systemctl stop antigravity-manager.service

# List all Antigravity processes
ps aux | grep antigravity
```

## 🏗️ Architecture

```
antigravity-isolation/
├── app/
│   ├── app.py                      # Flask web application
│   ├── config.py                   # Configuration
│   ├── process_manager.py          # Native process lifecycle with namespace isolation
│   ├── namespace_manager.py        # Linux namespace isolation management
│   ├── desktop_entry_manager.py    # Desktop entry management
│   ├── static/
│   │   ├── css/style.css      # UI styling
│   │   ├── js/app.js          # Frontend logic
│   │   └── images/            # Background images
│   └── templates/
│       └── index.html         # Dashboard
├── scripts/
│   └── antigravity-launcher.sh # Desktop entry launcher
├── systemd/
│   └── antigravity-manager.service # System service
├── install.sh                 # Automated installer
├── uninstall.sh               # Automated uninstaller
└── README.md                  # This file
```

### Technology Stack

- **Backend**: Python 3 + Flask
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Process Management**: psutil for native process handling
- **Isolation**: Linux namespaces (mount, PID, user, UTS) with automatic fallback - See [Namespace Isolation Documentation](NAMESPACE_ISOLATION.md)
- **Browser Authentication**: Preserved via D-Bus, X11/Wayland - See [Browser Authentication Documentation](BROWSER_AUTHENTICATION.md)
- **Service Management**: systemd (waits for graphical session)
- **Desktop Integration**: .desktop files + XDG standards
- **Robustness**: Automatic fallback to directory-based isolation when namespace isolation isn't available

## 🔧 Configuration

### Profile Storage
- **Default Location**: `~/Antigravity/[ProfileName]`
- **Custom Location**: Specify during profile creation
- **Downloads**: `~/Antigravity/[ProfileName]/Downloads`

### Web Interface
- **Host**: `127.0.0.1` (localhost only)
- **Port**: `5001` (configurable via `ANTIGRAVITY_MANAGER_PORT` environment variable)
- **Auto-refresh**: Every 5 seconds

### Desktop Entries
- **Location**: `~/.local/share/applications/`
- **Format**: `antigravity-[ProfileName].desktop`

### Namespace Isolation

Namespace isolation is enabled by default and can be configured via environment variables:

```bash
# Enable/disable namespace isolation (default: true)
export ANTIGRAVITY_USE_NAMESPACES=true

# Set isolation mode: mount, user, full, or none (default: mount)
export ANTIGRAVITY_NAMESPACE_MODE=mount

# Enable network namespace (not recommended, breaks browser functionality)
export ANTIGRAVITY_USE_NET_NS=false
```

**Available Modes:**
- `mount` - Mount namespace only (recommended, best compatibility)
- `user` - User namespace only (lightweight isolation)
- `full` - Full namespace isolation (mount + PID + user + UTS, IPC disabled for browser auth)
- `none` - No namespace isolation (directory-based only)

**Automatic Fallback**: If namespace isolation is not permitted (e.g., when running from systemd without proper capabilities), the system automatically falls back to directory-based isolation. This ensures profiles always start successfully.

For detailed information, see [Namespace Isolation Documentation](NAMESPACE_ISOLATION.md).

### Browser Authentication

All profiles are authenticated by the host browser, regardless of namespace isolation mode. The system preserves:
- D-Bus session bus access
- X11/Wayland display access
- XAUTHORITY for X11 authentication
- Network access to localhost

For detailed information, see [Browser Authentication Documentation](BROWSER_AUTHENTICATION.md).

## 🔐 Security Features

- ✅ **Namespace-Level Isolation** - Kernel-level process isolation
  - Mount namespace: Isolated filesystem view
  - PID namespace: Isolated process tree
  - User namespace: Isolated UID/GID mapping
  - UTS namespace: Isolated hostname
- ✅ Native execution (proper browser authentication)
- ✅ **Browser Authentication Preserved** - All profiles use host browser for authentication
- ✅ Filesystem isolation (only profile directory used)
- ✅ Web interface bound to localhost only
- ✅ No cross-profile data contamination
- ✅ Process isolation per profile
- ✅ IPC namespace disabled in full mode to preserve D-Bus for browser authentication

## 🐛 Troubleshooting

### Service won't start
```bash
# Check service status
sudo systemctl status antigravity-manager.service

# View detailed logs
sudo journalctl -u antigravity-manager.service -n 50
```

### Antigravity not found
```bash
# Check if Antigravity is installed
which antigravity

# Check if it's in PATH
echo $PATH

# Install Antigravity (see installation instructions above)
```

### Process won't start
```bash
# Check if Antigravity is installed correctly
antigravity --version

# Check logs
sudo journalctl -u antigravity-manager.service -f

# Verify profile directory exists
ls -la ~/Antigravity/

# Check profile-specific logs
cat ~/Antigravity/[ProfileName]/antigravity.log
```

### Profiles not starting after reboot
The service is configured to wait for the graphical session to be ready. If profiles still don't start:

```bash
# Check if service is waiting for graphical session
sudo systemctl status antigravity-manager.service

# Verify graphical session is active
loginctl list-sessions

# Restart the service
sudo systemctl restart antigravity-manager.service
```

### Namespace isolation errors
If you see "Operation not permitted" errors, the system automatically falls back to directory-based isolation. This is normal and expected when running from systemd. To explicitly disable namespace isolation:

```bash
export ANTIGRAVITY_USE_NAMESPACES=false
# or
export ANTIGRAVITY_NAMESPACE_MODE=none
```

### Desktop entry not appearing
```bash
# Update desktop database
update-desktop-database ~/.local/share/applications

# Log out and log back in
```

## 📝 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles` | List all profiles |
| POST | `/api/profiles` | Create new profile |
| DELETE | `/api/profiles/<name>` | Delete profile |
| POST | `/api/profiles/<name>/start` | Start process |
| POST | `/api/profiles/<name>/stop` | Stop process |
| GET | `/api/profiles/<name>/status` | Get status |
| GET | `/api/profiles/<name>/export` | Export profile |
| POST | `/api/profiles/import` | Import profile |

### Example: Create Profile

```bash
curl -X POST http://localhost:5001/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "Work", "location": "/custom/path"}'
```

### Example: Start Profile

```bash
curl -X POST http://localhost:5001/api/profiles/Work/start
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [psutil](https://github.com/giampaolo/psutil) - Process management
- [Antigravity](https://antigravity.com/) - Application
- Love ❤️ - The secret ingredient

## 📚 Additional Documentation

- **[Namespace Isolation Guide](NAMESPACE_ISOLATION.md)** - Complete guide to namespace-level isolation
- **[Browser Authentication Guide](BROWSER_AUTHENTICATION.md)** - How browser authentication is preserved

## 📞 Support

- 🐛 **Issues**: Create an issue for support
- 💬 **Discussions**: Use GitHub Discussions
- 📧 **Email**: Create an issue for support

---

<div align="center">

**Made with ❤️ for privacy-conscious Linux users**

[⬆ Back to Top](#-antigravity-isolation-manager)

</div>

