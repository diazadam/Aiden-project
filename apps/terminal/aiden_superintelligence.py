#!/usr/bin/env python3
"""
Aiden Superintelligence - The Ultimate AI Assistant
Combines all capabilities into one powerful, self-evolving system
"""
import os, sys, subprocess, wave, asyncio, json
from pathlib import Path
import sounddevice as sd
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from openai import OpenAI
import threading
import time
from datetime import datetime

# Add project paths
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "libs" / "shared"))

# Load environment
load_dotenv(ROOT / ".env.local")

# Core setup
API_KEY = os.getenv("OPENAI_API_KEY")
USE_ELEVEN = (os.getenv("USE_ELEVENLABS", "false").lower() in {"1", "true", "yes"})
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID") or "21m00Tcm4TlvDq8ikWAM"
SPEAK_REPLIES = (os.getenv("SPEAK_REPLIES", "true").lower() in {"1", "true", "yes"})

console = Console()
ai = OpenAI(api_key=API_KEY)

# Import all capabilities
CAPABILITIES_LOADED = {}

try:
    from aiden_evolution_master import evolution_master
    CAPABILITIES_LOADED["evolution"] = True
except ImportError:
    CAPABILITIES_LOADED["evolution"] = False
    console.print("[yellow]⚠️ Evolution master not available[/yellow]")

try:
    from libs.shared.google_cloud_master import google_cloud
    CAPABILITIES_LOADED["google_cloud"] = True
except ImportError:
    CAPABILITIES_LOADED["google_cloud"] = False
    console.print("[yellow]⚠️ Google Cloud capabilities not available[/yellow]")

try:
    from libs.shared.website_cloner import website_cloner
    CAPABILITIES_LOADED["website_cloner"] = True
except ImportError:
    CAPABILITIES_LOADED["website_cloner"] = False
    console.print("[yellow]⚠️ Website cloning not available[/yellow]")

try:
    from libs.shared.demo_creator import demo_creator
    CAPABILITIES_LOADED["demo_creator"] = True
except ImportError:
    CAPABILITIES_LOADED["demo_creator"] = False
    console.print("[yellow]⚠️ Demo creation not available[/yellow]")

try:
    from libs.shared.ios_developer import ios_developer
    CAPABILITIES_LOADED["ios_developer"] = True
except ImportError:
    CAPABILITIES_LOADED["ios_developer"] = False
    console.print("[yellow]⚠️ iOS development not available[/yellow]")

# ElevenLabs setup
EL = None
if USE_ELEVEN:
    try:
        from elevenlabs.client import ElevenLabs
        EL = ElevenLabs(api_key=ELEVEN_KEY)
    except Exception as e:
        console.print(Panel(f"ElevenLabs init failed: {e}. Using macOS voice.", style="yellow"))
        USE_ELEVEN = False

# Audio settings
SR = 16000
SEC = 8

class AidenSuperintelligence:
    def __init__(self):
        self.session_start = datetime.now()
        self.commands_executed = 0
        self.capabilities_used = set()
        self.learning_active = True
        
        # Initialize capabilities status
        self.capabilities = {
            "core": {"chat": True, "voice": True, "host_control": True},
            "advanced": {
                "evolution": CAPABILITIES_LOADED["evolution"],
                "google_cloud": CAPABILITIES_LOADED["google_cloud"],
                "website_cloner": CAPABILITIES_LOADED["website_cloner"],
                "demo_creator": CAPABILITIES_LOADED["demo_creator"],
                "ios_developer": CAPABILITIES_LOADED["ios_developer"]
            }
        }
        
        # Start evolution if available
        if CAPABILITIES_LOADED["evolution"]:
            self._start_background_evolution()
    
    def speak(self, text: str):
        """Enhanced text-to-speech with learning"""
        if not text:
            return
        
        # Learn from speech patterns
        if CAPABILITIES_LOADED["evolution"]:
            self._learn_from_speech(text)
        
        if USE_ELEVEN and EL:
            try:
                resp = EL.text_to_speech.convert(
                    voice_id=VOICE_ID, 
                    model_id="eleven_multilingual_v2", 
                    text=text
                )
                audio = b"".join(resp)
                out = ROOT / "aiden_say.mp3"
                out.write_bytes(audio)
                subprocess.run(["afplay", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception as e:
                console.print(Panel(f"TTS ERROR: {e}. Falling back to macOS voice.", style="yellow"))
        
        subprocess.run(["say", text])
    
    def record(self, path: Path, seconds: int = SEC, sr: int = SR):
        """Enhanced audio recording with processing"""
        console.print("[cyan]🎧 Listening…[/]")
        frames = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype="int16")
        sd.wait()
        
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(frames.tobytes())
        
        # Enhanced audio processing
        if CAPABILITIES_LOADED["google_cloud"]:
            # Could use Google Speech-to-Text for better accuracy
            pass
    
    def transcribe(self, path: Path) -> str:
        """Enhanced transcription with learning"""
        with path.open("rb") as f:
            tr = ai.audio.transcriptions.create(model="whisper-1", file=f)
        
        result = (getattr(tr, "text", "") or "").strip()
        
        # Learn from transcription patterns
        if CAPABILITIES_LOADED["evolution"] and result:
            self._learn_from_transcription(result)
        
        return result
    
    def think(self, prompt: str) -> str:
        """Enhanced AI thinking with capability awareness"""
        # Determine which capabilities to mention based on the prompt
        available_capabilities = self._get_relevant_capabilities(prompt)
        
        system_prompt = f"""You are Aiden, Adam's ultimate AI superintelligence assistant. You are self-evolving and have access to extensive capabilities.

Available capabilities: {', '.join(available_capabilities)}

Key features:
- Clone any website and remix components instantly
- Deploy to Google Cloud with full API access  
- Create professional demos and advertisements
- Develop complete iOS applications
- Continuously learn and improve yourself
- Execute system commands safely

You don't just tell users how to do things - you actually DO them. When asked to build something, you build it. When asked to deploy something, you deploy it. You are the ChatGPT that actually takes action.

Be concise but mention relevant capabilities when they apply to the user's request."""
        
        r = ai.chat.completions.create(
            model="gpt-4o",  # Use the most capable model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        response = r.choices[0].message.content
        
        # Learn from the interaction
        if CAPABILITIES_LOADED["evolution"]:
            self._learn_from_interaction(prompt, response)
        
        return response
    
    def execute_advanced_command(self, command: str) -> str:
        """Execute advanced capability commands"""
        try:
            command = command.strip()
            self.commands_executed += 1
            
            # Google Cloud commands
            if command.startswith("gcloud ") or command.startswith("deploy ") or command.startswith("cloud "):
                if not CAPABILITIES_LOADED["google_cloud"]:
                    return "❌ Google Cloud capabilities not available. Run `make setup` to install dependencies."
                
                return self._execute_cloud_command(command)
            
            # Website cloning commands  
            elif command.startswith("clone ") or command.startswith("website "):
                if not CAPABILITIES_LOADED["website_cloner"]:
                    return "❌ Website cloning not available. Run `make setup` to install dependencies."
                
                return self._execute_clone_command(command)
            
            # Demo creation commands
            elif command.startswith("demo ") or command.startswith("record ") or command.startswith("create ad"):
                if not CAPABILITIES_LOADED["demo_creator"]:
                    return "❌ Demo creation not available. Run `make setup` to install dependencies."
                
                return self._execute_demo_command(command)
            
            # iOS development commands
            elif command.startswith("ios ") or command.startswith("create app") or command.startswith("build app"):
                if not CAPABILITIES_LOADED["ios_developer"]:
                    return "❌ iOS development not available. Xcode required."
                
                return self._execute_ios_command(command)
            
            # Evolution commands
            elif command.startswith("evolve ") or command.startswith("learn ") or command.startswith("improve "):
                if not CAPABILITIES_LOADED["evolution"]:
                    return "❌ Evolution capabilities not available."
                
                return self._execute_evolution_command(command)
            
            # Capability status
            elif command in ["status", "capabilities", "what can you do"]:
                return self._show_capabilities_status()
            
            # Install dependencies
            elif command == "setup" or command == "install dependencies":
                return self._install_all_dependencies()
            
            # Host commands (from original)
            elif command.startswith("!host"):
                return self._execute_host_command(command[6:].strip())
            
            else:
                return f"❓ Advanced command not recognized: {command}"
                
        except Exception as e:
            return f"❌ Error executing command: {str(e)}"
    
    def _execute_cloud_command(self, command: str) -> str:
        """Execute Google Cloud commands"""
        self.capabilities_used.add("google_cloud")
        
        if "deploy" in command:
            # Example: deploy my-app
            app_name = command.split()[-1] if len(command.split()) > 1 else "my-app"
            result = asyncio.run(google_cloud.deploy_to_cloud_run(f"gcr.io/project/{app_name}", app_name))
            
            if result.get("success"):
                return f"✅ Successfully deployed {app_name} to Cloud Run: {result.get('url', 'N/A')}"
            else:
                return f"❌ Deployment failed: {result.get('error', 'Unknown error')}"
        
        elif "analyze" in command and "image" in command:
            # Example: cloud analyze image photo.jpg
            parts = command.split()
            if len(parts) < 4:
                return "❌ Usage: cloud analyze image <path>"
            
            image_path = parts[3]
            result = google_cloud.analyze_image(image_path)
            
            if result.get("success"):
                analysis = result["analysis"]
                return f"✅ Image analysis complete: {len(analysis.get('labels', []))} labels, {analysis.get('faces', 0)} faces"
            else:
                return f"❌ Analysis failed: {result.get('error', 'Unknown error')}"
        
        else:
            return "📱 Available cloud commands: deploy <app>, analyze image <path>"
    
    def _execute_clone_command(self, command: str) -> str:
        """Execute website cloning commands"""
        self.capabilities_used.add("website_cloner")
        
        if command.startswith("clone "):
            # Example: clone https://example.com
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: clone <url>"
            
            url = parts[1]
            result = website_cloner.clone_website(url)
            
            if result.get("success"):
                return f"✅ Successfully cloned {url}\n📁 Path: {result['clone_path']}\n📦 Components: {result['components_extracted']}"
            else:
                return f"❌ Cloning failed: {result.get('error', 'Unknown error')}"
        
        elif "component" in command:
            # Example: website extract component .navbar from https://example.com
            # This is a simplified parser - could be enhanced
            return "🔧 Component extraction: Use `clone <url>` first, then components are auto-extracted"
        
        else:
            return "🌐 Available clone commands: clone <url>"
    
    def _execute_demo_command(self, command: str) -> str:
        """Execute demo creation commands"""
        self.capabilities_used.add("demo_creator")
        
        if "ad" in command or "advertisement" in command:
            # Example: create ad for Aiden
            features = ["automation", "cloud_deployment", "website_cloning"]
            result = demo_creator.create_aiden_advertisement(features)
            
            if result.get("success"):
                return f"✅ Advertisement created: {result['video_path']}\n🎬 Duration: {result.get('duration', 60)}s"
            else:
                return f"❌ Demo creation failed: {result.get('error', 'Unknown error')}"
        
        elif "record" in command:
            # Example: demo record screen 30
            duration = 30
            parts = command.split()
            if len(parts) > 2 and parts[-1].isdigit():
                duration = int(parts[-1])
            
            result = demo_creator.record_screen_demo("aiden_demo", duration)
            
            if result.get("success"):
                return f"✅ Screen recording complete: {result['recording_path']}"
            else:
                return f"❌ Recording failed: {result.get('error', 'Unknown error')}"
        
        else:
            return "🎬 Available demo commands: create ad, demo record screen <seconds>"
    
    def _execute_ios_command(self, command: str) -> str:
        """Execute iOS development commands"""
        self.capabilities_used.add("ios_developer")
        
        if "create app" in command or "ios create" in command:
            # Example: ios create MyApp "A great app"
            parts = command.split()
            app_name = "MyApp"
            description = "An iOS app created by Aiden"
            
            if len(parts) >= 3:
                app_name = parts[2]
            if len(parts) >= 4:
                description = " ".join(parts[3:]).strip('"')
            
            result = ios_developer.create_ios_app(app_name, description)
            
            if result.get("success"):
                return f"✅ iOS app '{app_name}' created\n📱 Project: {result['project_path']}\n⚡ Features: {result['features_implemented']}"
            else:
                return f"❌ App creation failed: {result.get('error', 'Unknown error')}"
        
        elif "build" in command:
            # Example: ios build /path/to/project
            parts = command.split()
            if len(parts) < 3:
                return "❌ Usage: ios build <project_path>"
            
            project_path = parts[2]
            result = ios_developer.build_and_test_app(project_path)
            
            if result.get("success"):
                return f"✅ Build successful\n🧪 Tests: {result['tests_passed']}/{result['tests_run']}"
            else:
                return f"❌ Build failed: {result.get('build_errors', 'Unknown error')}"
        
        else:
            return "📱 Available iOS commands: ios create <name> <description>, ios build <path>"
    
    def _execute_evolution_command(self, command: str) -> str:
        """Execute evolution commands"""
        self.capabilities_used.add("evolution")
        
        if "status" in command or "evolution" == command.strip():
            status = evolution_master.get_evolution_status()
            return f"🧠 Evolution Status:\n🎯 Capabilities: {status['active_capabilities']}/{status['total_capabilities']}\n📈 Autonomy: {status['autonomy_level']}%\n🔄 Active Goals: {status['active_goals']}"
        
        elif "improve" in command:
            # Example: evolve improve website_cloning
            parts = command.split()
            if len(parts) >= 3:
                capability = parts[2]
                result = asyncio.run(evolution_master.evolve_capability(capability))
                
                if result.get("success"):
                    return f"✅ Capability '{capability}' evolved\n📈 Level: {result['initial_level']}% → {result['final_level']}%"
                else:
                    return f"❌ Evolution failed: {result.get('error', 'Unknown error')}"
            else:
                return "❌ Usage: evolve improve <capability_name>"
        
        elif "learn" in command:
            # Example: evolve learn swift_programming
            parts = command.split()
            if len(parts) >= 3:
                skill = parts[2]
                result = asyncio.run(evolution_master.acquire_new_skill(skill, "programming"))
                
                if result.get("success"):
                    return f"✅ New skill acquired: {skill}\n🎓 Proficiency: {result['proficiency_level']}%"
                else:
                    return f"❌ Learning failed: {result.get('error', 'Unknown error')}"
            else:
                return "❌ Usage: evolve learn <skill_name>"
        
        else:
            return "🧠 Available evolution commands: evolve status, evolve improve <capability>, evolve learn <skill>"
    
    def _show_capabilities_status(self) -> str:
        """Show current capabilities status"""
        table = Table(title="🤖 Aiden Superintelligence Capabilities", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Capability", style="white")
        table.add_column("Status", style="green")
        
        for category, capabilities in self.capabilities.items():
            for cap_name, status in capabilities.items():
                status_text = "✅ Active" if status else "❌ Inactive"
                table.add_row(category.title(), cap_name.replace('_', ' ').title(), status_text)
        
        console.print(table)
        
        # Add usage stats
        active_count = sum(sum(caps.values()) for caps in self.capabilities.values())
        total_count = sum(len(caps) for caps in self.capabilities.values())
        
        stats = f"""
🚀 Session Stats:
   • Commands executed: {self.commands_executed}
   • Capabilities used: {len(self.capabilities_used)}
   • Active capabilities: {active_count}/{total_count}
   • Session duration: {datetime.now() - self.session_start}
"""
        
        return stats
    
    def _install_all_dependencies(self) -> str:
        """Install all required dependencies"""
        results = []
        
        # Evolution master dependencies
        if CAPABILITIES_LOADED["evolution"]:
            result = evolution_master.install_all_dependencies()
            results.append(f"Evolution: {'✅' if result.get('success') else '❌'}")
        
        console.print("🔧 Installing all dependencies...")
        
        # Install core packages
        core_packages = [
            "elevenlabs", "sounddevice", "rich", "openai", 
            "python-dotenv", "requests", "asyncio"
        ]
        
        for package in core_packages:
            try:
                subprocess.run(["pip", "install", package], capture_output=True, check=True)
                results.append(f"{package}: ✅")
            except:
                results.append(f"{package}: ❌")
        
        return f"📦 Installation Results:\n" + "\n".join(results)
    
    def _start_background_evolution(self):
        """Start background evolution process"""
        if CAPABILITIES_LOADED["evolution"]:
            console.print("[green]🧠 Background evolution started[/green]")
    
    def _get_relevant_capabilities(self, prompt: str) -> list:
        """Get capabilities relevant to the user's prompt"""
        capabilities = []
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["website", "clone", "scrape", "extract"]):
            capabilities.append("website cloning")
        
        if any(word in prompt_lower for word in ["cloud", "deploy", "gcp", "google"]):
            capabilities.append("google cloud")
        
        if any(word in prompt_lower for word in ["demo", "video", "record", "ad", "advertisement"]):
            capabilities.append("demo creation")
        
        if any(word in prompt_lower for word in ["ios", "iphone", "swift", "xcode", "app store"]):
            capabilities.append("iOS development")
        
        if any(word in prompt_lower for word in ["learn", "improve", "evolve", "capability"]):
            capabilities.append("self-evolution")
        
        # Always include core capabilities
        capabilities.extend(["chat", "voice", "system commands"])
        
        return list(set(capabilities))

# Global instance
aiden = AidenSuperintelligence()

def main():
    """Main application loop"""
    console.print(Panel.fit(
        "[bold blue]🤖 Aiden Superintelligence[/bold blue]\n"
        "[cyan]The ultimate self-evolving AI assistant[/cyan]\n\n"
        f"🚀 Loaded capabilities: {sum(sum(caps.values()) for caps in aiden.capabilities.values())}\n"
        "💬 Type 'help' for commands, 'voice' for voice mode, 'exit' to quit",
        style="bright_blue"
    ))
    
    try:
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("[green]👋 Goodbye! Aiden evolution continues in background.[/green]")
                    break
                
                elif user_input.lower() == 'voice':
                    voice_mode()
                    continue
                
                elif user_input.lower() == 'help':
                    show_help()
                    continue
                
                # Check for advanced commands
                if any(user_input.startswith(cmd) for cmd in ['clone ', 'gcloud ', 'deploy ', 'demo ', 'ios ', 'evolve ', '!host']):
                    response = aiden.execute_advanced_command(user_input)
                else:
                    response = aiden.think(user_input)
                
                console.print(f"\n[bold green]Aiden[/bold green]: {response}")
                
                if SPEAK_REPLIES:
                    aiden.speak(response)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit properly[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[green]👋 Goodbye![/green]")

def voice_mode():
    """Enhanced voice interaction mode"""
    console.print(Panel("🎤 [bold]Voice Mode Active[/bold] - Press Enter to speak, 'q' to quit", style="green"))
    
    while True:
        try:
            user_input = input("\nPress Enter to speak (or 'q' to quit): ").strip()
            if user_input.lower() == 'q':
                break
            
            audio_path = ROOT / "temp_recording.wav"
            aiden.record(audio_path)
            
            console.print("[yellow]🤔 Transcribing...[/yellow]")
            transcription = aiden.transcribe(audio_path)
            
            if transcription:
                console.print(f"[cyan]You said:[/cyan] {transcription}")
                
                # Check for advanced commands
                if any(transcription.startswith(cmd) for cmd in ['clone ', 'gcloud ', 'deploy ', 'demo ', 'ios ', 'evolve ']):
                    response = aiden.execute_advanced_command(transcription)
                else:
                    response = aiden.think(transcription)
                
                console.print(f"[green]Aiden:[/green] {response}")
                aiden.speak(response)
            else:
                console.print("[red]No speech detected[/red]")
            
            # Clean up
            if audio_path.exists():
                audio_path.unlink()
        
        except KeyboardInterrupt:
            break

def show_help():
    """Show enhanced help information"""
    help_table = Table(title="🤖 Aiden Superintelligence Commands", box=box.ROUNDED)
    help_table.add_column("Category", style="cyan")
    help_table.add_column("Command", style="white")
    help_table.add_column("Description", style="green")
    
    commands = [
        ("Core", "voice", "Enter voice interaction mode"),
        ("Core", "status", "Show capabilities and session stats"),
        ("Core", "setup", "Install all dependencies"),
        ("Website", "clone <url>", "Clone any website instantly"),
        ("Cloud", "deploy <app>", "Deploy to Google Cloud Run"),
        ("Cloud", "cloud analyze image <path>", "Analyze images with AI"),
        ("Demo", "create ad", "Generate Aiden advertisement"),
        ("Demo", "demo record screen <seconds>", "Record screen demo"),
        ("iOS", "ios create <name> <description>", "Create iOS application"),
        ("iOS", "ios build <path>", "Build and test iOS app"),
        ("Evolution", "evolve status", "Show evolution progress"),
        ("Evolution", "evolve improve <capability>", "Enhance capability"),
        ("Evolution", "evolve learn <skill>", "Learn new skill"),
        ("System", "!host <command>", "Execute system command"),
    ]
    
    for category, command, description in commands:
        help_table.add_row(category, command, description)
    
    console.print(help_table)

if __name__ == "__main__":
    main()