#!/usr/bin/env python3
"""
Aiden Menu Bar App
Launch Aiden superintelligence from your macOS menu bar
"""
import sys, os, subprocess, threading, time, json, requests
from pathlib import Path
import webbrowser
from datetime import datetime

# Add project paths
ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

try:
    import rumps
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QLabel
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont, QIcon
    MENUBAR_DEPS_AVAILABLE = True
except ImportError:
    MENUBAR_DEPS_AVAILABLE = False

class AidenMenuBarApp(rumps.App):
    def __init__(self):
        super(AidenMenuBarApp, self).__init__(
            "🤖 Aiden",
            icon=None,
            template=True,
            quit_button=None
        )
        
        # Configuration
        self.aiden_port = 8001
        self.aiden_url = f"http://localhost:{self.aiden_port}"
        self.control_tower_running = False
        self.superintelligence_process = None
        
        # Menu structure
        self.menu = [
            "🚀 Quick Actions",
            None,  # Separator
            "💬 Chat with Aiden",
            "🎤 Voice Mode", 
            "🌐 Open Control Tower",
            "🧠 Run Superintelligence",
            None,
            "⚡ Capabilities",
            None,
            "🔧 Tools",
            None,
            "📊 Status",
            "⚙️ Settings",
            None,
            "❌ Quit Aiden"
        ]
        
        # Build menu
        self._build_menu()
        
        # Check initial status
        self._check_status()
        
        # Start status monitor
        self._start_status_monitor()
    
    def _build_menu(self):
        """Build the menu structure"""
        
        # Quick Actions submenu
        quick_actions = rumps.MenuItem("🚀 Quick Actions")
        quick_actions_menu = [
            rumps.MenuItem("Clone Website", callback=self.quick_clone_website),
            rumps.MenuItem("Deploy to Cloud", callback=self.quick_deploy_cloud),
            rumps.MenuItem("Create iOS App", callback=self.quick_create_ios_app),
            rumps.MenuItem("Generate Demo Video", callback=self.quick_create_demo),
            rumps.MenuItem("Build Website", callback=self.quick_build_website),
        ]
        for item in quick_actions_menu:
            quick_actions.add(item)
        
        # Capabilities submenu
        capabilities = rumps.MenuItem("⚡ Capabilities")
        capabilities_menu = [
            rumps.MenuItem("🌐 Website Cloning", callback=self.show_website_cloning),
            rumps.MenuItem("☁️ Google Cloud APIs", callback=self.show_google_cloud),
            rumps.MenuItem("🎬 Demo Creation", callback=self.show_demo_creation),
            rumps.MenuItem("📱 iOS Development", callback=self.show_ios_development),
            rumps.MenuItem("🧠 Self Evolution", callback=self.show_evolution),
        ]
        for item in capabilities_menu:
            capabilities.add(item)
        
        # Tools submenu
        tools = rumps.MenuItem("🔧 Tools")
        tools_menu = [
            rumps.MenuItem("🔄 Restart Control Tower", callback=self.restart_control_tower),
            rumps.MenuItem("📁 Open Project Folder", callback=self.open_project_folder),
            rumps.MenuItem("📋 Copy API Endpoint", callback=self.copy_api_endpoint),
            rumps.MenuItem("🔍 View Logs", callback=self.view_logs),
            rumps.MenuItem("🛠️ Install Dependencies", callback=self.install_dependencies),
        ]
        for item in tools_menu:
            tools.add(item)
        
        # Add all menu items
        self.menu.add(quick_actions)
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("💬 Chat with Aiden", callback=self.open_chat))
        self.menu.add(rumps.MenuItem("🎤 Voice Mode", callback=self.open_voice_mode))
        self.menu.add(rumps.MenuItem("🌐 Open Control Tower", callback=self.open_control_tower))
        self.menu.add(rumps.MenuItem("🧠 Run Superintelligence", callback=self.run_superintelligence))
        self.menu.add(rumps.separator)
        self.menu.add(capabilities)
        self.menu.add(rumps.separator)
        self.menu.add(tools)
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("📊 Status", callback=self.show_status))
        self.menu.add(rumps.MenuItem("⚙️ Settings", callback=self.show_settings))
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("❌ Quit Aiden", callback=self.quit_app))
    
    def _check_status(self):
        """Check if Control Tower is running"""
        try:
            response = requests.get(f"{self.aiden_url}/api/health", timeout=2)
            if response.status_code == 200:
                self.control_tower_running = True
                self.title = "🤖 Aiden ✅"
            else:
                self.control_tower_running = False
                self.title = "🤖 Aiden ⚠️"
        except:
            self.control_tower_running = False
            self.title = "🤖 Aiden ❌"
    
    def _start_status_monitor(self):
        """Start background status monitoring"""
        def monitor():
            while True:
                time.sleep(30)  # Check every 30 seconds
                self._check_status()
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    # Quick Action callbacks
    def quick_clone_website(self, _):
        """Quick clone website action"""
        url = rumps.Window(
            "🌐 Clone Website",
            "Enter the website URL to clone:",
            default_text="https://",
            ok="Clone",
            cancel="Cancel",
            dimensions=(400, 24)
        ).run()
        
        if url.clicked and url.text:
            self._execute_aiden_command(f"clone {url.text}")
    
    def quick_deploy_cloud(self, _):
        """Quick deploy to cloud action"""
        app_name = rumps.Window(
            "☁️ Deploy to Cloud",
            "Enter app name to deploy:",
            default_text="my-app",
            ok="Deploy",
            cancel="Cancel",
            dimensions=(400, 24)
        ).run()
        
        if app_name.clicked and app_name.text:
            self._execute_aiden_command(f"deploy {app_name.text}")
    
    def quick_create_ios_app(self, _):
        """Quick create iOS app action"""
        app_name = rumps.Window(
            "📱 Create iOS App", 
            "Enter app name:",
            default_text="MyAwesomeApp",
            ok="Create",
            cancel="Cancel",
            dimensions=(400, 24)
        ).run()
        
        if app_name.clicked and app_name.text:
            self._execute_aiden_command(f"ios create {app_name.text}")
    
    def quick_create_demo(self, _):
        """Quick create demo action"""
        if rumps.alert("🎬 Create Demo Video", "Create a professional demo showcasing Aiden's capabilities?", ok="Create Demo", cancel="Cancel"):
            self._execute_aiden_command("create ad")
    
    def quick_build_website(self, _):
        """Quick build website action"""
        business_name = rumps.Window(
            "🌐 Build Website",
            "Enter your business name:",
            default_text="My Business",
            ok="Build",
            cancel="Cancel", 
            dimensions=(400, 24)
        ).run()
        
        if business_name.clicked and business_name.text:
            webbrowser.open(f"{self.aiden_url}/app/")
            rumps.notification("🌐 Website Builder", "Control Tower opened", "Use the AI Website Builder card to create your site", sound=True)
    
    # Main action callbacks
    def open_chat(self, _):
        """Open chat interface"""
        if not self.control_tower_running:
            self._ensure_control_tower()
        
        if self.control_tower_running:
            webbrowser.open(f"{self.aiden_url}/app/")
            rumps.notification("💬 Aiden Chat", "Chat interface opened", "Start chatting with Aiden in your browser", sound=True)
        else:
            rumps.alert("❌ Error", "Control Tower is not running. Please check the status.")
    
    def open_voice_mode(self, _):
        """Open voice mode"""
        try:
            subprocess.Popen([
                "open", "-a", "Terminal", 
                str(ROOT / "apps" / "terminal" / "run_voice.sh")
            ])
            rumps.notification("🎤 Voice Mode", "Voice interface starting", "Speak with Aiden using your voice", sound=True)
        except Exception as e:
            rumps.alert("❌ Error", f"Failed to start voice mode: {e}")
    
    def open_control_tower(self, _):
        """Open Control Tower web interface"""
        if not self.control_tower_running:
            self._ensure_control_tower()
        
        if self.control_tower_running:
            webbrowser.open(self.aiden_url)
            rumps.notification("🌐 Control Tower", "Web interface opened", "Full Aiden capabilities available", sound=True)
        else:
            rumps.alert("❌ Error", "Failed to start Control Tower")
    
    def run_superintelligence(self, _):
        """Run Aiden Superintelligence in terminal"""
        if self.superintelligence_process and self.superintelligence_process.poll() is None:
            rumps.alert("⚠️ Already Running", "Aiden Superintelligence is already running in terminal")
            return
        
        try:
            # Create run script
            run_script = ROOT / "run_superintelligence.sh"
            run_script.write_text(f"""#!/bin/bash
cd {ROOT}
export TERM=xterm-256color
echo "🤖 Starting Aiden Superintelligence..."
echo "Press Ctrl+C to exit"
echo ""
make run-super
""")
            run_script.chmod(0o755)
            
            subprocess.Popen([
                "open", "-a", "Terminal", str(run_script)
            ])
            
            rumps.notification("🧠 Superintelligence", "Terminal interface starting", "Full AI capabilities in terminal", sound=True)
        except Exception as e:
            rumps.alert("❌ Error", f"Failed to start superintelligence: {e}")
    
    # Capability showcase callbacks
    def show_website_cloning(self, _):
        """Show website cloning capabilities"""
        rumps.alert(
            "🌐 Website Cloning",
            "Clone any website instantly:\n\n• Full HTML/CSS/JS extraction\n• Component-based remixing\n• Framework conversion (React/Vue)\n• Responsive design analysis\n• Asset downloading\n\nTry: 'clone https://stripe.com'",
            ok="Got it"
        )
    
    def show_google_cloud(self, _):
        """Show Google Cloud capabilities"""
        rumps.alert(
            "☁️ Google Cloud APIs",
            "Full Google Cloud integration:\n\n• Vision AI & Speech AI\n• Cloud Run deployment\n• BigQuery analytics\n• Cloud Functions\n• Storage & monitoring\n• Document AI\n\nTry: 'deploy my-app'",
            ok="Got it"
        )
    
    def show_demo_creation(self, _):
        """Show demo creation capabilities"""
        rumps.alert(
            "🎬 Demo Creation",
            "Professional video creation:\n\n• Screen recording\n• Automated advertisements\n• Tutorial videos\n• Product showcases\n• Social media content\n• Voice-over generation\n\nTry: 'create ad'",
            ok="Got it"
        )
    
    def show_ios_development(self, _):
        """Show iOS development capabilities"""
        rumps.alert(
            "📱 iOS Development",
            "Complete iOS app creation:\n\n• SwiftUI applications\n• App Store ready projects\n• UI cloning from existing apps\n• Feature implementation\n• Build and test automation\n• Deployment preparation\n\nTry: 'ios create MyApp'",
            ok="Got it"
        )
    
    def show_evolution(self, _):
        """Show evolution capabilities"""
        rumps.alert(
            "🧠 Self Evolution",
            "Continuous self-improvement:\n\n• Autonomous learning\n• Skill acquisition\n• Performance optimization\n• Code enhancement\n• Knowledge expansion\n• Adaptation to usage\n\nTry: 'evolve status'",
            ok="Got it"
        )
    
    # Tools callbacks
    def restart_control_tower(self, _):
        """Restart Control Tower"""
        try:
            # Kill existing process
            subprocess.run(["pkill", "-f", "uvicorn.*main:app"], capture_output=True)
            time.sleep(2)
            
            # Start new process
            self._start_control_tower()
            
            rumps.notification("🔄 Control Tower", "Restarted successfully", "Web interface is ready", sound=True)
        except Exception as e:
            rumps.alert("❌ Error", f"Failed to restart Control Tower: {e}")
    
    def open_project_folder(self, _):
        """Open project folder in Finder"""
        subprocess.Popen(["open", str(ROOT)])
    
    def copy_api_endpoint(self, _):
        """Copy API endpoint to clipboard"""
        subprocess.run(["pbcopy"], input=self.aiden_url.encode())
        rumps.notification("📋 Copied", "API endpoint copied to clipboard", self.aiden_url, sound=False)
    
    def view_logs(self, _):
        """View application logs"""
        logs_dir = ROOT / "logs"
        if logs_dir.exists():
            subprocess.Popen(["open", str(logs_dir)])
        else:
            rumps.alert("📁 No Logs", "No log files found yet")
    
    def install_dependencies(self, _):
        """Install missing dependencies"""
        if rumps.alert(
            "🛠️ Install Dependencies",
            "Install all required dependencies for maximum Aiden capabilities?",
            ok="Install",
            cancel="Cancel"
        ):
            try:
                # Run in background
                def install():
                    subprocess.run([
                        "osascript", "-e", 
                        f'tell app "Terminal" to do script "cd {ROOT} && make setup && echo \\"\\nDependencies installed! You can close this window.\\" && read -p \\"Press Enter to close\\""'
                    ])
                
                threading.Thread(target=install, daemon=True).start()
                rumps.notification("🛠️ Installing", "Dependencies installation started", "Check Terminal for progress", sound=True)
            except Exception as e:
                rumps.alert("❌ Error", f"Failed to start installation: {e}")
    
    def show_status(self, _):
        """Show current status"""
        status_text = f"""🤖 Aiden Status Report

Control Tower: {"✅ Running" if self.control_tower_running else "❌ Stopped"}
Port: {self.aiden_port}
URL: {self.aiden_url}

Superintelligence: {"✅ Available" if (ROOT / "apps" / "terminal" / "aiden_superintelligence.py").exists() else "❌ Missing"}

Project Directory: {ROOT}
"""
        rumps.alert("📊 Status", status_text, ok="OK")
    
    def show_settings(self, _):
        """Show settings"""
        rumps.alert(
            "⚙️ Settings",
            f"Aiden Menu Bar v1.0\n\nProject: {ROOT}\nPort: {self.aiden_port}\n\nTo modify settings:\n• Edit configuration files\n• Use Control Tower interface\n• Check documentation",
            ok="OK"
        )
    
    def quit_app(self, _):
        """Quit the application"""
        if rumps.alert("❌ Quit Aiden", "Stop all Aiden services and quit?", ok="Quit", cancel="Cancel"):
            # Stop Control Tower
            subprocess.run(["pkill", "-f", "uvicorn.*main:app"], capture_output=True)
            
            # Stop any superintelligence processes
            if self.superintelligence_process:
                self.superintelligence_process.terminate()
            
            rumps.quit_application()
    
    # Helper methods
    def _ensure_control_tower(self):
        """Ensure Control Tower is running"""
        if not self.control_tower_running:
            self._start_control_tower()
            time.sleep(3)  # Give it time to start
            self._check_status()
    
    def _start_control_tower(self):
        """Start Control Tower in background"""
        try:
            subprocess.Popen([
                "make", "run-ctl"
            ], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Failed to start Control Tower: {e}")
            return False
    
    def _execute_aiden_command(self, command):
        """Execute an Aiden command via API"""
        try:
            if not self.control_tower_running:
                self._ensure_control_tower()
            
            if self.control_tower_running:
                webbrowser.open(f"{self.aiden_url}/app/")
                rumps.notification("⚡ Command Ready", f"Command: {command}", "Paste this into the chat interface", sound=True)
                # Copy command to clipboard
                subprocess.run(["pbcopy"], input=command.encode())
            else:
                rumps.alert("❌ Error", "Control Tower not available")
        except Exception as e:
            rumps.alert("❌ Error", f"Failed to execute command: {e}")

def create_voice_run_script():
    """Create voice mode run script"""
    run_script = ROOT / "apps" / "terminal" / "run_voice.sh"
    run_script.write_text(f"""#!/bin/bash
cd {ROOT / "apps" / "terminal"}
echo "🎤 Starting Aiden Voice Mode..."
echo "Press Ctrl+C to exit"
echo ""
../../.venv311/bin/python aiden_superintelligence.py
""")
    run_script.chmod(0o755)

def install_menubar_dependencies():
    """Install required dependencies for menu bar app"""
    try:
        subprocess.run([
            "pip", "install", "rumps", "PyQt5", "requests"
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    if not MENUBAR_DEPS_AVAILABLE:
        print("Installing menu bar dependencies...")
        if install_menubar_dependencies():
            print("✅ Dependencies installed! Please run the script again.")
            return
        else:
            print("❌ Failed to install dependencies. Please install manually:")
            print("pip install rumps PyQt5 requests")
            return
    
    # Create necessary scripts
    create_voice_run_script()
    
    # Start the app
    app = AidenMenuBarApp()
    app.run()

if __name__ == "__main__":
    main()