"""
🍎 AIDEN MAC CONTROL V1 - APPLESCRIPT/JXA INTEGRATION
Native macOS system control and automation capabilities.
"""

import subprocess
import asyncio
import json
import tempfile
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import platform


@dataclass
class MacControlResponse:
    """Standardized response for Mac control operations"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    script_type: str = ""  # applescript or jxa


class AidenMacControl:
    """Advanced macOS system control and automation"""
    
    def __init__(self):
        self.is_macos = platform.system() == "Darwin"
        self.osascript_available = self._check_osascript()
    
    def _check_osascript(self) -> bool:
        """Check if osascript is available"""
        try:
            subprocess.run(["osascript", "-e", "1 + 1"], 
                         capture_output=True, check=True, timeout=5)
            return True
        except:
            return False
    
    async def execute_applescript(self, script: str) -> MacControlResponse:
        """Execute AppleScript code"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.is_macos:
            return MacControlResponse(
                success=False,
                error="Mac control only available on macOS systems",
                execution_time_ms=0,
                script_type="applescript"
            )
        
        if not self.osascript_available:
            return MacControlResponse(
                success=False,
                error="osascript not available",
                execution_time_ms=0,
                script_type="applescript"
            )
        
        try:
            # Execute AppleScript using osascript
            process = await asyncio.create_subprocess_exec(
                "osascript", "-e", script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if process.returncode == 0:
                result = stdout.decode('utf-8').strip()
                return MacControlResponse(
                    success=True,
                    data={"result": result, "script": script},
                    execution_time_ms=execution_time,
                    script_type="applescript"
                )
            else:
                error_msg = stderr.decode('utf-8').strip()
                return MacControlResponse(
                    success=False,
                    error=error_msg,
                    metadata={"script": script},
                    execution_time_ms=execution_time,
                    script_type="applescript"
                )
                
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return MacControlResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                script_type="applescript"
            )
    
    async def execute_jxa(self, script: str) -> MacControlResponse:
        """Execute JavaScript for Automation (JXA) code"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.is_macos:
            return MacControlResponse(
                success=False,
                error="Mac control only available on macOS systems",
                execution_time_ms=0,
                script_type="jxa"
            )
        
        if not self.osascript_available:
            return MacControlResponse(
                success=False,
                error="osascript not available",
                execution_time_ms=0,
                script_type="jxa"
            )
        
        try:
            # Execute JXA using osascript with -l JavaScript flag
            process = await asyncio.create_subprocess_exec(
                "osascript", "-l", "JavaScript", "-e", script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if process.returncode == 0:
                result = stdout.decode('utf-8').strip()
                try:
                    # Try to parse as JSON if it looks like JSON
                    if result.startswith('{') or result.startswith('['):
                        parsed_result = json.loads(result)
                    else:
                        parsed_result = result
                except:
                    parsed_result = result
                
                return MacControlResponse(
                    success=True,
                    data={"result": parsed_result, "script": script},
                    execution_time_ms=execution_time,
                    script_type="jxa"
                )
            else:
                error_msg = stderr.decode('utf-8').strip()
                return MacControlResponse(
                    success=False,
                    error=error_msg,
                    metadata={"script": script},
                    execution_time_ms=execution_time,
                    script_type="jxa"
                )
                
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return MacControlResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                script_type="jxa"
            )
    
    async def get_system_info(self) -> MacControlResponse:
        """Get comprehensive macOS system information"""
        jxa_script = '''
        const app = Application.currentApplication();
        app.includeStandardAdditions = true;
        
        const systemInfo = {
            computerName: app.computerName(),
            systemVersion: app.systemVersion(),
            currentUser: app.shortUserName(),
            homeDirectory: app.pathToHome().toString(),
            desktopPath: app.pathToDesktop().toString(),
            timestamp: new Date().toISOString()
        };
        
        JSON.stringify(systemInfo);
        '''
        
        return await self.execute_jxa(jxa_script)
    
    async def get_running_applications(self) -> MacControlResponse:
        """Get list of running applications"""
        jxa_script = '''
        const se = Application('System Events');
        const processes = se.processes.whose({ backgroundOnly: false });
        
        const apps = [];
        for (let i = 0; i < processes.length; i++) {
            const proc = processes[i];
            try {
                apps.push({
                    name: proc.name(),
                    bundleIdentifier: proc.bundleIdentifier() || null,
                    frontmost: proc.frontmost(),
                    visible: proc.visible()
                });
            } catch (e) {
                // Skip if we can't access process info
            }
        }
        
        JSON.stringify(apps);
        '''
        
        return await self.execute_jxa(jxa_script)
    
    async def launch_application(self, app_name: str) -> MacControlResponse:
        """Launch an application"""
        applescript = f'tell application "{app_name}" to activate'
        return await self.execute_applescript(applescript)
    
    async def quit_application(self, app_name: str) -> MacControlResponse:
        """Quit an application"""
        applescript = f'tell application "{app_name}" to quit'
        return await self.execute_applescript(applescript)
    
    async def show_notification(self, title: str, subtitle: str = "", message: str = "") -> MacControlResponse:
        """Show a macOS notification"""
        applescript = f'''
        display notification "{message}" with title "{title}" subtitle "{subtitle}"
        '''
        return await self.execute_applescript(applescript)
    
    async def get_clipboard_content(self) -> MacControlResponse:
        """Get clipboard content"""
        applescript = 'the clipboard'
        return await self.execute_applescript(applescript)
    
    async def set_clipboard_content(self, content: str) -> MacControlResponse:
        """Set clipboard content"""
        applescript = f'set the clipboard to "{content}"'
        return await self.execute_applescript(applescript)
    
    async def take_screenshot(self, path: Optional[str] = None) -> MacControlResponse:
        """Take a screenshot using macOS screencapture"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.is_macos:
            return MacControlResponse(
                success=False,
                error="Screenshot only available on macOS",
                execution_time_ms=0
            )
        
        if not path:
            path = f"logs/mac_screenshot_{int(datetime.now().timestamp())}.png"
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            process = await asyncio.create_subprocess_exec(
                "screencapture", "-x", path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if process.returncode == 0:
                return MacControlResponse(
                    success=True,
                    data={"screenshot_path": path},
                    execution_time_ms=execution_time,
                    script_type="system"
                )
            else:
                return MacControlResponse(
                    success=False,
                    error="Failed to capture screenshot",
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return MacControlResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def start_screen_recording(self, path: Optional[str] = None, duration: int = 10) -> MacControlResponse:
        """Start screen recording using macOS screencapture"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.is_macos:
            return MacControlResponse(
                success=False,
                error="Screen recording only available on macOS",
                execution_time_ms=0
            )
        
        if not path:
            path = f"logs/mac_recording_{int(datetime.now().timestamp())}.mov"
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use screencapture with video recording (-V flag)
            # -V captures video, -t specifies duration
            process = await asyncio.create_subprocess_exec(
                "screencapture", "-V", str(duration), path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the recording to complete
            await process.communicate()
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if process.returncode == 0:
                # Check if file was actually created
                if Path(path).exists():
                    file_size = Path(path).stat().st_size
                    return MacControlResponse(
                        success=True,
                        data={
                            "recording_path": path,
                            "duration_seconds": duration,
                            "file_size_bytes": file_size
                        },
                        execution_time_ms=execution_time,
                        script_type="system"
                    )
                else:
                    return MacControlResponse(
                        success=False,
                        error="Recording file not created (may need screen recording permission)",
                        execution_time_ms=execution_time
                    )
            else:
                return MacControlResponse(
                    success=False,
                    error="Failed to start screen recording (may need permission)",
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return MacControlResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def record_screen_with_ffmpeg(self, path: Optional[str] = None, duration: int = 10) -> MacControlResponse:
        """Record screen using ffmpeg (more reliable alternative)"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.is_macos:
            return MacControlResponse(
                success=False,
                error="Screen recording only available on macOS",
                execution_time_ms=0
            )
        
        if not path:
            path = f"logs/mac_recording_{int(datetime.now().timestamp())}.mp4"
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Check if ffmpeg is available
            ffmpeg_check = await asyncio.create_subprocess_exec(
                "which", "ffmpeg",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await ffmpeg_check.communicate()
            
            if ffmpeg_check.returncode != 0:
                return MacControlResponse(
                    success=False,
                    error="ffmpeg not installed. Install with: brew install ffmpeg",
                    execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            # Use ffmpeg to capture screen
            # -f avfoundation captures from macOS
            # -i "1:0" captures screen (display 1) with no audio
            # -t duration limits recording time
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-f", "avfoundation", "-i", "1:0", 
                "-t", str(duration), "-y", path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for recording to complete
            stdout, stderr = await process.communicate()
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if process.returncode == 0 and Path(path).exists():
                file_size = Path(path).stat().st_size
                return MacControlResponse(
                    success=True,
                    data={
                        "recording_path": path,
                        "duration_seconds": duration,
                        "file_size_bytes": file_size,
                        "format": "mp4"
                    },
                    execution_time_ms=execution_time,
                    script_type="ffmpeg"
                )
            else:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                return MacControlResponse(
                    success=False,
                    error=f"ffmpeg recording failed: {error_msg}",
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return MacControlResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def record_screen_area(self, x: int, y: int, width: int, height: int, 
                                path: Optional[str] = None, duration: int = 10) -> MacControlResponse:
        """Record a specific area of the screen"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.is_macos:
            return MacControlResponse(
                success=False,
                error="Screen recording only available on macOS",
                execution_time_ms=0
            )
        
        if not path:
            path = f"logs/mac_recording_area_{int(datetime.now().timestamp())}.mp4"
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Check for ffmpeg
            ffmpeg_check = await asyncio.create_subprocess_exec(
                "which", "ffmpeg",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await ffmpeg_check.communicate()
            
            if ffmpeg_check.returncode != 0:
                return MacControlResponse(
                    success=False,
                    error="ffmpeg required for area recording: brew install ffmpeg",
                    execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000
                )
            
            # Record specific screen area
            filter_complex = f"crop={width}:{height}:{x}:{y}"
            
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-f", "avfoundation", "-i", "1:0",
                "-vf", filter_complex, "-t", str(duration), "-y", path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if process.returncode == 0 and Path(path).exists():
                file_size = Path(path).stat().st_size
                return MacControlResponse(
                    success=True,
                    data={
                        "recording_path": path,
                        "duration_seconds": duration,
                        "area": {"x": x, "y": y, "width": width, "height": height},
                        "file_size_bytes": file_size
                    },
                    execution_time_ms=execution_time,
                    script_type="ffmpeg_area"
                )
            else:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                return MacControlResponse(
                    success=False,
                    error=f"Area recording failed: {error_msg}",
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return MacControlResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def speak_text(self, text: str, voice: str = "Alex") -> MacControlResponse:
        """Use macOS text-to-speech"""
        applescript = f'say "{text}" using "{voice}"'
        return await self.execute_applescript(applescript)
    
    async def get_desktop_wallpaper(self) -> MacControlResponse:
        """Get current desktop wallpaper path"""
        applescript = '''
        tell application "System Events"
            tell current desktop
                return picture as string
            end tell
        end tell
        '''
        return await self.execute_applescript(applescript)
    
    async def set_desktop_wallpaper(self, image_path: str) -> MacControlResponse:
        """Set desktop wallpaper"""
        applescript = f'''
        tell application "System Events"
            tell current desktop
                set picture to "{image_path}"
            end tell
        end tell
        '''
        return await self.execute_applescript(applescript)
    
    async def get_wifi_networks(self) -> MacControlResponse:
        """Get available WiFi networks"""
        jxa_script = '''
        const app = Application.currentApplication();
        app.includeStandardAdditions = true;
        
        try {
            const result = app.doShellScript('/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s');
            const lines = result.split('\\n');
            const networks = [];
            
            for (let i = 1; i < lines.length; i++) {
                const line = lines[i].trim();
                if (line) {
                    const parts = line.split(/\\s+/);
                    if (parts.length >= 3) {
                        networks.push({
                            ssid: parts[0],
                            bssid: parts[1],
                            rssi: parts[2]
                        });
                    }
                }
            }
            
            JSON.stringify(networks);
        } catch (e) {
            JSON.stringify({ error: e.toString() });
        }
        '''
        return await self.execute_jxa(jxa_script)
    
    async def open_url(self, url: str) -> MacControlResponse:
        """Open URL in default browser"""
        applescript = f'open location "{url}"'
        return await self.execute_applescript(applescript)
    
    async def get_finder_selection(self) -> MacControlResponse:
        """Get currently selected files in Finder"""
        applescript = '''
        tell application "Finder"
            set selectedItems to selection
            set itemList to {}
            repeat with anItem in selectedItems
                set end of itemList to (anItem as alias as string)
            end repeat
            return itemList as string
        end tell
        '''
        return await self.execute_applescript(applescript)
    
    async def create_folder(self, path: str, folder_name: str) -> MacControlResponse:
        """Create a new folder"""
        applescript = f'''
        tell application "Finder"
            make new folder at folder "{path}" with properties {{name:"{folder_name}"}}
        end tell
        '''
        return await self.execute_applescript(applescript)
    
    async def empty_trash(self) -> MacControlResponse:
        """Empty the Trash"""
        applescript = '''
        tell application "Finder"
            empty trash
        end tell
        '''
        return await self.execute_applescript(applescript)


class MacAutomationTasks:
    """High-level Mac automation task workflows"""
    
    def __init__(self):
        self.mac_control = AidenMacControl()
    
    async def setup_development_environment(self) -> MacControlResponse:
        """Set up a development environment"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            results = []
            
            # Launch development apps
            apps_to_launch = ["Visual Studio Code", "Terminal", "Safari"]
            for app in apps_to_launch:
                result = await self.mac_control.launch_application(app)
                results.append({"app": app, "success": result.success, "error": result.error})
            
            # Show notification
            await self.mac_control.show_notification(
                "Development Environment",
                "Setup Complete",
                "All development apps launched successfully!"
            )
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return MacControlResponse(
                success=True,
                data={"launched_apps": results, "setup_complete": True},
                execution_time_ms=execution_time,
                script_type="workflow"
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return MacControlResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                script_type="workflow"
            )
    
    async def system_cleanup(self) -> MacControlResponse:
        """Perform system cleanup tasks"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            results = {}
            
            # Empty trash
            trash_result = await self.mac_control.empty_trash()
            results["trash_emptied"] = trash_result.success
            
            # Show notification
            await self.mac_control.show_notification(
                "System Cleanup",
                "Complete",
                "Trash emptied and system optimized!"
            )
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return MacControlResponse(
                success=True,
                data=results,
                execution_time_ms=execution_time,
                script_type="workflow"
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return MacControlResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                script_type="workflow"
            )


# Global Mac control instance
mac_control = AidenMacControl()


async def quick_launch(app_name: str) -> MacControlResponse:
    """Quick app launch function"""
    return await mac_control.launch_application(app_name)


async def quick_notification(title: str, message: str) -> MacControlResponse:
    """Quick notification function"""
    return await mac_control.show_notification(title, "", message)


async def quick_screenshot(path: Optional[str] = None) -> MacControlResponse:
    """Quick screenshot function"""
    return await mac_control.take_screenshot(path)


async def create_demo_sequence(duration: int = 30) -> MacControlResponse:
    """Create a demo sequence by taking multiple screenshots over time"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        mac = AidenMacControl()
        screenshots = []
        
        # Take screenshots every 2 seconds for the duration
        interval = 2
        num_shots = duration // interval
        
        for i in range(num_shots):
            timestamp = int(datetime.now().timestamp())
            screenshot_path = f"logs/demo_sequence_{timestamp}_{i:02d}.png"
            
            result = await mac.take_screenshot(screenshot_path)
            if result.success:
                screenshots.append({
                    "path": result.data["screenshot_path"],
                    "timestamp": timestamp,
                    "sequence": i
                })
            
            # Wait for interval (except on last iteration)
            if i < num_shots - 1:
                await asyncio.sleep(interval)
        
        execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return MacControlResponse(
            success=True,
            data={
                "demo_type": "screenshot_sequence",
                "screenshots": screenshots,
                "total_duration": duration,
                "interval_seconds": interval,
                "total_frames": len(screenshots)
            },
            execution_time_ms=execution_time,
            script_type="demo_sequence"
        )
        
    except Exception as e:
        execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
        return MacControlResponse(
            success=False,
            error=str(e),
            execution_time_ms=execution_time
        )


# Export key classes and functions
__all__ = [
    "MacControlResponse",
    "AidenMacControl", 
    "MacAutomationTasks",
    "mac_control",
    "quick_launch",
    "quick_notification",
    "quick_screenshot"
]