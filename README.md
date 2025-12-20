# 🔒 Antigravity Isolation Manager

<div align="center">

![Antigravity Isolation Manager](https://img.shields.io/badge/Antigravity-Isolation-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Linux-orange?style=for-the-badge&logo=linux)

**A complete web-based solution for managing isolated Antigravity application profiles on Linux**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

---

## 🌟 Overview

Antigravity Isolation Manager is a powerful, production-ready web application that allows you to run multiple isolated Antigravity application instances on Linux. Each profile runs natively with complete data isolation, while maintaining seamless desktop integration.

**Note**: Antigravity uses the host browser for authentication, so profiles run natively (not in Docker containers) to ensure proper browser integration.

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
- Each profile uses a separate data directory
- Filesystem isolation (only profile directory used)
- No access to other profile data
- Native execution for proper browser authentication
- Profile size monitoring in the dashboard

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
- ✅ Native execution (uses host browser for authentication)
- ✅ Profile data isolation
- ✅ Export/Import Profiles - Backup and restore profiles easily (ZIP format)
- ✅ Automatic Desktop Entry Creation
- ✅ Process management and monitoring

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
6. 🎉 Open `http://localhost:5000` automatically

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
│   ├── app.py                 # Flask web application
│   ├── config.py              # Configuration
│   ├── process_manager.py     # Native process lifecycle
│   ├── desktop_manager.py      # Desktop entry management
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
- **Service Management**: systemd
- **Desktop Integration**: .desktop files + XDG standards

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

## 🔐 Security Features

- ✅ Native execution (proper browser authentication)
- ✅ Filesystem isolation (only profile directory used)
- ✅ Web interface bound to localhost only
- ✅ No cross-profile data contamination
- ✅ Process isolation per profile

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

## 📞 Support

- 🐛 **Issues**: Create an issue for support
- 💬 **Discussions**: Use GitHub Discussions
- 📧 **Email**: Create an issue for support

---

<div align="center">

**Made with ❤️ for privacy-conscious Linux users**

[⬆ Back to Top](#-antigravity-isolation-manager)

</div>

