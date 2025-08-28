#!/usr/bin/env python3
"""
🚀 AIDEN CONTROL TOWER LAUNCHER
==============================

Easy launcher script for the Aiden SuperIntelligence Control Tower.
This script will:
1. Start the server
2. Open the Control Tower in your browser
3. Show you the URL to share with others
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

def print_banner():
    print("🧠 AIDEN SUPERINTELLIGENCE CONTROL TOWER")
    print("=" * 50)
    print("🚀 Starting your AI automation platform...")
    print("=" * 50)

def check_dependencies():
    """Check if virtual environment and dependencies exist"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        return False
    return True

def start_server():
    """Start the Aiden server"""
    print("🔧 Starting Aiden SuperIntelligence server...")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent)
    
    # Start server in background
    try:
        if sys.platform.startswith('win'):
            # Windows
            subprocess.Popen([
                "venv\\Scripts\\python", "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", "8001", "--reload"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # macOS/Linux
            subprocess.Popen([
                "venv/bin/python", "-m", "uvicorn", "main:app",
                "--host", "0.0.0.0", "--port", "8001", "--reload"
            ])
        
        print("✅ Server starting...")
        
        # Wait for server to start
        print("⏳ Waiting for server to initialize...")
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def open_control_tower():
    """Open the Control Tower in the default browser"""
    url = "http://localhost:8001"
    print(f"🌐 Opening Control Tower at: {url}")
    
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"📍 Please manually open: {url}")
        return False

def show_info():
    """Show access information"""
    print("\n" + "=" * 50)
    print("🎯 AIDEN CONTROL TOWER IS NOW RUNNING!")
    print("=" * 50)
    print("🔗 Local Access: http://localhost:8001")
    print("🌍 Network Access: http://YOUR_IP:8001")
    print("📱 Mobile Access: Use your computer's IP address")
    print("\n🎮 Available Features:")
    print("• 🎓 Teach Aiden New Automation Patterns")
    print("• 🎯 Create Custom Business Solutions")
    print("• 🌐 AI Website Builder & Deployment")
    print("• 📊 Business Intelligence Reports")
    print("• 🤖 Chat with Specialized AI Assistants")
    print("\n💡 Tip: Bookmark http://localhost:8001 for easy access!")
    print("🔄 To restart: Just run this script again")
    print("=" * 50)

def main():
    print_banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    if start_server():
        time.sleep(2)  # Give server more time to start
        open_control_tower()
        show_info()
        
        print("\n🎉 Aiden Control Tower is ready!")
        print("💻 Keep this terminal open to keep the server running")
        print("🛑 Press Ctrl+C to stop the server")
        
        try:
            # Keep script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down Aiden Control Tower...")
            print("✅ Server stopped successfully!")
    else:
        print("❌ Failed to start Aiden Control Tower")
        sys.exit(1)

if __name__ == "__main__":
    main()