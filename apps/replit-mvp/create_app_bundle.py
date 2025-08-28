#!/usr/bin/env python3
"""
Create a macOS Application Bundle for Aiden Control Tower
"""

import os
import shutil
from pathlib import Path

def create_macos_app():
    """Create a macOS .app bundle for Aiden Control Tower"""
    
    app_name = "Aiden Control Tower"
    bundle_path = Path(f"{app_name}.app")
    
    # Create app bundle structure
    contents_path = bundle_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Create directories
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>aiden_launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.aiden.controltower</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>"""
    
    with open(contents_path / "Info.plist", "w") as f:
        f.write(info_plist)
    
    # Create launcher script
    launcher_script = f"""#!/bin/bash
cd "{Path(__file__).parent.absolute()}"
python3 launch_aiden.py
"""
    
    launcher_path = macos_path / "aiden_launcher"
    with open(launcher_path, "w") as f:
        f.write(launcher_script)
    
    # Make executable
    os.chmod(launcher_path, 0o755)
    
    # Create icon (basic text-based icon)
    icon_script = """#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# Simple icon window
root = tk.Tk()
root.title("🧠 Aiden Control Tower")
root.geometry("300x200")
root.configure(bg='#0a0e1a')

# Main label
label = tk.Label(root, text="🧠\\nAiden\\nControl Tower", 
                font=('Arial', 20, 'bold'), 
                fg='white', bg='#0a0e1a')
label.pack(expand=True)

# Launch button
def launch_aiden():
    root.destroy()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    launcher_path = os.path.join(script_dir, 'launch_aiden.py')
    subprocess.run([sys.executable, launcher_path])

launch_btn = tk.Button(root, text="🚀 Launch Control Tower", 
                      command=launch_aiden,
                      font=('Arial', 12, 'bold'),
                      bg='#4f63d2', fg='white',
                      padx=20, pady=10)
launch_btn.pack(pady=20)

root.mainloop()
"""
    
    with open(resources_path / "aiden_icon.py", "w") as f:
        f.write(icon_script)
    
    print(f"✅ Created macOS app bundle: {bundle_path}")
    print(f"📍 Location: {bundle_path.absolute()}")
    print("🖱️  Double-click the .app to launch Aiden Control Tower")
    
    return bundle_path

if __name__ == "__main__":
    create_macos_app()