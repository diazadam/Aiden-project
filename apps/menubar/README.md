# 🤖 Aiden Menu Bar App

Launch Aiden superintelligence directly from your macOS menu bar! Get instant access to all of Aiden's powerful capabilities with just a click.

## 🚀 Quick Install

```bash
cd ~/aiden-project/apps/menubar
./install_menubar.sh
```

Then start Aiden in your menu bar:

```bash
python3 aiden_menubar.py
```

## ✨ Features

### 🚀 **Quick Actions** (one-click access)
- **Clone Website** - Enter any URL to clone instantly
- **Deploy to Cloud** - Deploy apps to Google Cloud Run  
- **Create iOS App** - Build complete iOS applications
- **Generate Demo** - Create professional demo videos
- **Build Website** - AI-powered website generation

### 💬 **Chat Interfaces**
- **Chat with Aiden** - Open web chat interface
- **Voice Mode** - Talk to Aiden using your voice
- **Control Tower** - Full web dashboard
- **Superintelligence** - Terminal with all capabilities

### ⚡ **Capabilities Overview**
- **🌐 Website Cloning** - Clone any site, extract components
- **☁️ Google Cloud APIs** - Vision AI, Speech AI, Cloud Run, BigQuery
- **🎬 Demo Creation** - Screen recording, ads, tutorials
- **📱 iOS Development** - SwiftUI apps, App Store ready
- **🧠 Self Evolution** - Continuous learning and improvement

### 🔧 **Tools & Management**
- **Restart Control Tower** - Fix any issues
- **Open Project Folder** - Quick Finder access
- **Copy API Endpoint** - For integrations  
- **View Logs** - Debug and monitor
- **Install Dependencies** - One-click setup
- **Status Monitor** - Real-time health check

## 🎯 **How It Works**

The menu bar app provides instant access to all Aiden capabilities:

1. **🤖 Status Indicator** - Shows if Aiden is online (✅❌⚠️)
2. **⚡ Quick Actions** - Common tasks with simple dialogs
3. **🌐 Web Interfaces** - Opens Control Tower in browser
4. **🎤 Voice Mode** - Launches terminal voice interface  
5. **🧠 Superintelligence** - Full AI capabilities in terminal

## 🔄 **Auto-Start on Login**

To have Aiden start automatically when you log in:

```bash
launchctl load ~/Library/LaunchAgents/com.aiden.menubar.plist
```

## 🎮 **Usage Examples**

### Clone a website:
1. Click 🤖 Aiden in menu bar
2. Quick Actions → Clone Website  
3. Enter URL (e.g., `https://stripe.com`)
4. Aiden clones it instantly!

### Deploy to cloud:
1. Menu bar → Quick Actions → Deploy to Cloud
2. Enter app name (e.g., `my-awesome-app`) 
3. Aiden deploys to Google Cloud Run!

### Create iOS app:
1. Menu bar → Quick Actions → Create iOS App
2. Enter app name (e.g., `RestaurantApp`)
3. Complete iOS project generated!

### Chat with Aiden:
1. Menu bar → Chat with Aiden
2. Web interface opens
3. Full conversational AI access!

## 🛠️ **Requirements**

- macOS 10.9+
- Python 3.11+
- Aiden project installed

**Dependencies** (auto-installed):
- `rumps` - macOS menu bar framework
- `PyQt5` - GUI toolkit  
- `requests` - HTTP client

## 🎨 **Menu Structure**

```
🤖 Aiden ✅
├── 🚀 Quick Actions
│   ├── Clone Website
│   ├── Deploy to Cloud
│   ├── Create iOS App
│   ├── Generate Demo Video
│   └── Build Website
├── ─────────────────
├── 💬 Chat with Aiden
├── 🎤 Voice Mode
├── 🌐 Open Control Tower  
├── 🧠 Run Superintelligence
├── ─────────────────
├── ⚡ Capabilities
│   ├── 🌐 Website Cloning
│   ├── ☁️ Google Cloud APIs
│   ├── 🎬 Demo Creation
│   ├── 📱 iOS Development
│   └── 🧠 Self Evolution
├── ─────────────────
├── 🔧 Tools
│   ├── 🔄 Restart Control Tower
│   ├── 📁 Open Project Folder
│   ├── 📋 Copy API Endpoint
│   ├── 🔍 View Logs
│   └── 🛠️ Install Dependencies
├── ─────────────────
├── 📊 Status
├── ⚙️ Settings
├── ─────────────────
└── ❌ Quit Aiden
```

## 🚨 **Troubleshooting**

### Menu bar app won't start:
```bash
# Install dependencies
pip install rumps PyQt5 requests

# Run directly
python3 aiden_menubar.py
```

### Control Tower not responding:
1. Menu bar → Tools → Restart Control Tower
2. Or manually: `make run-ctl` in project directory

### Missing capabilities:
1. Menu bar → Tools → Install Dependencies
2. Wait for terminal installation to complete

## 🎉 **Pro Tips**

1. **⌘+Space** then type "Aiden" to find the app quickly
2. **Right-click** menu bar icon for context menu (on supported versions)
3. **Status colors**: ✅ Online, ❌ Offline, ⚠️ Issues
4. **Notifications** show progress for long-running tasks
5. **Clipboard integration** - commands are auto-copied for quick pasting

---

**🤖 Aiden Menu Bar** - Your AI superintelligence, always one click away!