# 🔒 Antigravity Isolation Manager

<div align="center">

![Antigravity Isolation Manager](https://img.shields.io/badge/Antigravity-Isolation-blue?style=for-the-badge)
![HyperOS UI](https://img.shields.io/badge/UI-HyperOS%20Glass-purple?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Linux-orange?style=for-the-badge&logo=linux)

**A complete web-based solution for managing isolated Antigravity application profiles on Linux with HyperOS Glass UI**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Namespace Isolation](NAMESPACE_ISOLATION.md) • [Browser Authentication](BROWSER_AUTHENTICATION.md)

</div>

---

## 🌟 Overview

Antigravity Isolation Manager is a powerful, production-ready web application that allows you to run multiple isolated Antigravity application instances on Linux. Each profile runs natively with complete data isolation, while maintaining seamless desktop integration and a state-of-the-art **HyperOS Glass UI/UX layout**.

**Note**: Antigravity uses the host browser for authentication. All profiles are authenticated by the host browser, ensuring proper authentication even with namespace-level isolation. The system preserves D-Bus session bus access, X11/Wayland display access, and XAUTHORITY to maintain browser authentication functionality.

Perfect for:
- 🏢 **Work/Personal Separation** - Keep work and personal Antigravity instances completely isolated
- 🔐 **Privacy & Security** - Contain potentially risky activities with built-in path-traversal & Zip Slip protection
- 👥 **Multi-Account Management** - Different profiles for different accounts
- 🧪 **Testing & Development** - Clean environments for development
- 🛡️ **Enhanced Security** - Kernel-isolated data with safe archive import/export

## ✨ Features

### 🎨 HyperOS Glass UI / UX
- **HyperOS Glass Design System** featuring hyper-rounded superellipses and frosted glass backdrop blur
- **Light & Pitch Black OLED Dark Modes** with instant toggle and `localStorage` persistence
- Intuitive, responsive interface with real-time profile status auto-refresh (every 5s)
- Glowing ambient backdrop reflections and smooth 60fps micro-animations
- Accessible ARIA labels and keyboard focus indicators
- Modern profile cards with storage monitoring and desktop integration status

### 🔐 Complete Isolation & Security
- **Path Traversal & Zip Slip Protection** - Safe verification of profile imports (`os.path.commonpath` validation)
- **Namespace-Level Isolation** - Kernel-level isolation using Linux namespaces
  - Mount namespace: Isolated filesystem view
  - PID namespace: Isolated process tree
  - User namespace: Isolated UID/GID mapping
  - UTS namespace: Isolated hostname
- Separate data directory and downloads path per profile
- Native execution for proper host browser authentication
- Profile size monitoring in the dashboard

### 🖥️ Desktop Integration
- Profiles appear as native apps in your application menu
- Desktop entries: `Antigravity (ProfileName)`
- **Auto-creation** - Desktop entries created automatically when profiles are created or imported
- Click any profile icon to launch its isolated instance

### 💾 Persistent Storage
- Profile data stored in `~/Antigravity/[ProfileName]` by default
- Custom profile locations supported
- Export/Import profiles as compressed `.zip` or `.tar.gz` archives with path traversal prevention

## 📋 Requirements

- **OS**: Ubuntu 20.04+ (or Debian-based Linux)
- **Antigravity**: Antigravity application installed
- **Python**: 3.8+ (with `flask`, `psutil`)
- **RAM**: 4GB minimum

## 🚀 Installation

```bash
# Clone repository and run installer
git clone <repository-url>
cd antigravity-isolation-linux
./install.sh
```

Access the dashboard at `http://localhost:5001`.

## 📖 Usage

1. **Dashboard**: Open `http://localhost:5001`
2. **Toggle Theme**: Click the theme toggle icon in the top header to switch between OLED Dark mode and Frosted Light mode.
3. **Create Profile**: Click "+ New Profile", enter profile name (alphanumeric, `-`, `_`), and click Create.
4. **Import Profile**: Click "Import" to restore profile archives (`.zip` or `.tar.gz`) safely.

## 📄 License

MIT License.
