#!/usr/bin/env python3
"""
Create desktop shortcuts for Aiden Control Tower
"""

import os
import platform
from pathlib import Path

def create_desktop_shortcut():
    """Create a desktop shortcut for Aiden Control Tower"""
    
    system = platform.system()
    desktop_path = Path.home() / "Desktop"
    project_path = Path(__file__).parent.absolute()
    
    if system == "Darwin":  # macOS
        # Create an AppleScript app
        shortcut_path = desktop_path / "Aiden Control Tower.app"
        
        applescript_content = f'''
tell application "Terminal"
    do script "cd '{project_path}' && python3 launch_aiden.py"
    activate
end tell
'''
        
        # Create the app bundle structure
        contents_path = shortcut_path / "Contents"
        macos_path = contents_path / "MacOS"
        resources_path = contents_path / "Resources"
        
        macos_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)
        
        # Create Info.plist
        info_plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.aiden.desktop.launcher</string>
    <key>CFBundleName</key>
    <string>Aiden Control Tower</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>'''
        
        with open(contents_path / "Info.plist", "w") as f:
            f.write(info_plist)
        
        # Create launcher script
        launcher_script = f'''#!/bin/bash
cd "{project_path}"
python3 launch_aiden.py
'''
        
        launcher_path = macos_path / "launcher"
        with open(launcher_path, "w") as f:
            f.write(launcher_script)
        
        os.chmod(launcher_path, 0o755)
        
        print(f"✅ Created macOS desktop shortcut: {shortcut_path}")
        
    elif system == "Windows":
        # Create Windows batch file
        batch_content = f'''@echo off
cd /d "{project_path}"
python launch_aiden.py
pause
'''
        
        shortcut_path = desktop_path / "Aiden Control Tower.bat"
        with open(shortcut_path, "w") as f:
            f.write(batch_content)
        
        print(f"✅ Created Windows desktop shortcut: {shortcut_path}")
        
    else:  # Linux
        # Create .desktop file
        desktop_entry = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Aiden Control Tower
Comment=Launch Aiden SuperIntelligence Control Tower
Exec=python3 "{project_path}/launch_aiden.py"
Icon={project_path}/aiden_icon.png
Path={project_path}
Terminal=true
Categories=Development;
'''
        
        shortcut_path = desktop_path / "aiden-control-tower.desktop"
        with open(shortcut_path, "w") as f:
            f.write(desktop_entry)
        
        os.chmod(shortcut_path, 0o755)
        
        print(f"✅ Created Linux desktop shortcut: {shortcut_path}")
    
    return shortcut_path

def create_dock_alias():
    """Create a dock alias for quick access (macOS)"""
    if platform.system() == "Darwin":
        print("\n🍎 To add Aiden Control Tower to your Dock:")
        print("1. Open the created desktop app")
        print("2. While it's running, right-click the icon in the Dock")
        print("3. Select 'Options' → 'Keep in Dock'")
        print("4. Now you can launch Aiden anytime from the Dock!")

if __name__ == "__main__":
    print("🚀 Creating Aiden Control Tower Desktop Shortcut")
    print("=" * 50)
    
    try:
        shortcut_path = create_desktop_shortcut()
        print(f"📍 Shortcut created at: {shortcut_path}")
        print("\n🎯 How to use:")
        print("• Double-click the desktop shortcut to launch Aiden")
        print("• The Control Tower will open in your browser automatically")
        print("• Bookmark http://localhost:8001 for quick browser access")
        
        create_dock_alias()
        
        print("\n✅ Setup complete! You can now easily launch Aiden Control Tower!")
        
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        print("You can still launch manually with: python3 launch_aiden.py")