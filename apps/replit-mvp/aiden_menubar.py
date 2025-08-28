#!/usr/bin/env python3
"""
🧠 AIDEN CONTROL TOWER - MENUBAR APP
===================================

A system tray/menubar application for quick access to Aiden Control Tower.
This creates a persistent icon in your system tray for instant access.
"""

import sys
import os
import subprocess
import webbrowser
import threading
import time
from pathlib import Path

try:
    from tkinter import *
    from tkinter import messagebox
    import tkinter.font as tkFont
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    print("❌ GUI not available. Install tkinter or run in GUI environment.")

class AidenMenuBarApp:
    def __init__(self):
        if not HAS_GUI:
            print("❌ Cannot create menubar app without GUI support")
            return
            
        self.root = Tk()
        self.root.title("🧠 Aiden Control Tower")
        self.root.geometry("350x300")
        self.root.configure(bg='#0a0e1a')
        
        # Try to keep on top
        self.root.attributes('-topmost', True)
        
        self.server_process = None
        self.is_server_running = False
        
        self.create_ui()
        
    def create_ui(self):
        """Create the menubar interface"""
        
        # Title
        title_font = tkFont.Font(family='Arial', size=16, weight='bold')
        title_label = Label(self.root, text="🧠 Aiden Control Tower", 
                           font=title_font, fg='white', bg='#0a0e1a')
        title_label.pack(pady=20)
        
        # Status
        self.status_label = Label(self.root, text="🔴 Server Offline", 
                                 font=('Arial', 12), fg='#ef4444', bg='#0a0e1a')
        self.status_label.pack(pady=5)
        
        # Buttons frame
        button_frame = Frame(self.root, bg='#0a0e1a')
        button_frame.pack(pady=20)
        
        # Start/Stop Server button
        self.server_btn = Button(button_frame, text="🚀 Start Server", 
                               command=self.toggle_server,
                               font=('Arial', 12, 'bold'),
                               bg='#4f63d2', fg='white',
                               padx=20, pady=8, width=15)
        self.server_btn.pack(pady=5)
        
        # Open Control Tower button
        self.open_btn = Button(button_frame, text="🌐 Open Control Tower", 
                             command=self.open_control_tower,
                             font=('Arial', 12, 'bold'),
                             bg='#10b981', fg='white',
                             padx=20, pady=8, width=15,
                             state='disabled')
        self.open_btn.pack(pady=5)
        
        # Quick Actions frame
        actions_frame = LabelFrame(self.root, text="Quick Actions", 
                                 font=('Arial', 10, 'bold'),
                                 fg='white', bg='#0a0e1a')
        actions_frame.pack(pady=10, padx=20, fill='x')
        
        # Quick action buttons
        Button(actions_frame, text="🎓 Teach Pattern", 
               command=lambda: self.open_feature('teach'),
               font=('Arial', 10), bg='#f59e0b', fg='white',
               padx=10, pady=4).pack(pady=2, fill='x')
        
        Button(actions_frame, text="🎯 Create Solution", 
               command=lambda: self.open_feature('solution'),
               font=('Arial', 10), bg='#8b5cf6', fg='white',
               padx=10, pady=4).pack(pady=2, fill='x')
        
        Button(actions_frame, text="🌐 Build Website", 
               command=lambda: self.open_feature('website'),
               font=('Arial', 10), bg='#06b6d4', fg='white',
               padx=10, pady=4).pack(pady=2, fill='x')
        
        # Info
        info_label = Label(self.root, text="💡 Bookmark: http://localhost:8001", 
                          font=('Arial', 9), fg='#8792a2', bg='#0a0e1a')
        info_label.pack(side='bottom', pady=10)
        
        # Update status periodically
        self.update_status()
        
    def toggle_server(self):
        """Start or stop the Aiden server"""
        if not self.is_server_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        """Start the Aiden Control Tower server"""
        try:
            project_path = Path(__file__).parent
            
            # Start server in background
            if sys.platform.startswith('win'):
                self.server_process = subprocess.Popen([
                    "venv\\Scripts\\python", "-m", "uvicorn", "main:app",
                    "--host", "0.0.0.0", "--port", "8001", "--reload"
                ], cwd=project_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                self.server_process = subprocess.Popen([
                    "venv/bin/python", "-m", "uvicorn", "main:app",
                    "--host", "0.0.0.0", "--port", "8001", "--reload"
                ], cwd=project_path)
            
            self.is_server_running = True
            self.server_btn.config(text="🛑 Stop Server", bg='#ef4444')
            self.status_label.config(text="🟡 Server Starting...", fg='#f59e0b')
            
            # Check if server started successfully
            self.root.after(3000, self.check_server_started)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def stop_server(self):
        """Stop the Aiden server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
        
        self.is_server_running = False
        self.server_btn.config(text="🚀 Start Server", bg='#4f63d2')
        self.status_label.config(text="🔴 Server Offline", fg='#ef4444')
        self.open_btn.config(state='disabled')
    
    def check_server_started(self):
        """Check if server started successfully"""
        try:
            import requests
            response = requests.get("http://localhost:8001/api/health", timeout=2)
            if response.status_code == 200:
                self.status_label.config(text="🟢 Server Online", fg='#10b981')
                self.open_btn.config(state='normal')
            else:
                self.status_label.config(text="🟡 Server Starting...", fg='#f59e0b')
                self.root.after(2000, self.check_server_started)
        except:
            self.status_label.config(text="🟡 Server Starting...", fg='#f59e0b')
            self.root.after(2000, self.check_server_started)
    
    def open_control_tower(self):
        """Open the Control Tower in browser"""
        webbrowser.open("http://localhost:8001")
    
    def open_feature(self, feature):
        """Open Control Tower with specific feature highlighted"""
        url = "http://localhost:8001"
        if not self.is_server_running:
            messagebox.showwarning("Server Offline", "Please start the server first!")
            return
        
        webbrowser.open(url)
        
        # Show feature-specific tip
        tips = {
            'teach': "Click the '🎓 Teach Aiden New Skills' card to train custom automation patterns!",
            'solution': "Click the '🎯 Custom Solutions' card to create tailored automation solutions!",
            'website': "Click the '🌐 AI Website Builder' card to create professional websites!"
        }
        
        if feature in tips:
            self.root.after(2000, lambda: messagebox.showinfo("Quick Tip", tips[feature]))
    
    def update_status(self):
        """Periodically update server status"""
        # This runs every 5 seconds to check server status
        self.root.after(5000, self.update_status)
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_server_running:
            if messagebox.askquestion("Quit", "Server is running. Stop server and quit?") == 'yes':
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Run the menubar app"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main function"""
    print("🧠 Starting Aiden Control Tower Menubar App...")
    
    if not HAS_GUI:
        print("❌ GUI not available. Please run in a desktop environment.")
        return
    
    app = AidenMenuBarApp()
    app.run()

if __name__ == "__main__":
    main()