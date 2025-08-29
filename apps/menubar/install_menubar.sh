#!/bin/bash
echo "🤖 Installing Aiden Menu Bar App..."

# Check if we're in the right directory
if [ ! -f "../../Makefile" ]; then
    echo "❌ Please run this script from the apps/menubar directory"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install rumps PyQt5 requests

# Make the script executable
chmod +x aiden_menubar.py

# Create launch agent plist for auto-start (optional)
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/com.aiden.menubar.plist"

mkdir -p "$PLIST_DIR"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aiden.menubar</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/aiden_menubar.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/aiden_menubar.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/aiden_menubar_error.log</string>
</dict>
</plist>
EOF

# Create desktop shortcut
APPLICATIONS_DIR="$HOME/Applications"
mkdir -p "$APPLICATIONS_DIR"

cat > "$APPLICATIONS_DIR/Aiden Menu Bar.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch_aiden</string>
    <key>CFBundleIdentifier</key>
    <string>com.aiden.menubar</string>
    <key>CFBundleName</key>
    <string>Aiden Menu Bar</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.9</string>
</dict>
</plist>
EOF

mkdir -p "$APPLICATIONS_DIR/Aiden Menu Bar.app/Contents/MacOS"
cat > "$APPLICATIONS_DIR/Aiden Menu Bar.app/Contents/MacOS/launch_aiden" << EOF
#!/bin/bash
cd "$(dirname "$0")/../../../.."
$(pwd)/aiden_menubar.py
EOF

chmod +x "$APPLICATIONS_DIR/Aiden Menu Bar.app/Contents/MacOS/launch_aiden"

echo ""
echo "✅ Aiden Menu Bar App installed successfully!"
echo ""
echo "🚀 To start Aiden in your menu bar:"
echo "   python3 aiden_menubar.py"
echo ""
echo "🔄 To start automatically on login:"
echo "   launchctl load ~/Library/LaunchAgents/com.aiden.menubar.plist"
echo ""
echo "📱 You can also find 'Aiden Menu Bar' in your Applications folder"
echo ""
echo "🤖 Features available from your menu bar:"
echo "   • Quick website cloning"
echo "   • One-click cloud deployment" 
echo "   • iOS app creation"
echo "   • Demo video generation"
echo "   • Voice mode access"
echo "   • Control Tower web interface"
echo "   • Status monitoring"
echo ""