#!/usr/bin/env python3
import os, subprocess, wave
from pathlib import Path
import sounddevice as sd
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]  # project root
load_dotenv(ROOT/".env.local")

API_KEY = os.getenv("OPENAI_API_KEY")
USE_ELEVEN = (os.getenv("USE_ELEVENLABS","false").lower() in {"1","true","yes"})
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID   = os.getenv("ELEVENLABS_VOICE_ID") or "21m00Tcm4TlvDq8ikWAM"
SPEAK_REPLIES = (os.getenv("SPEAK_REPLIES","true").lower() in {"1","true","yes"})

console = Console()
ai = OpenAI(api_key=API_KEY)

EL = None
if USE_ELEVEN:
    try:
        from elevenlabs.client import ElevenLabs
        EL = ElevenLabs(api_key=ELEVEN_KEY)
    except Exception as e:
        console.print(Panel(f"ElevenLabs init failed: {e}. Using macOS voice.", style="yellow"))
        USE_ELEVEN=False

SR=16000; SEC=8

def speak(text:str):
    if not text: return
    if USE_ELEVEN and EL:
        try:
            resp = EL.text_to_speech.convert(voice_id=VOICE_ID, model_id="eleven_multilingual_v2", text=text)
            audio = b"".join(resp)
            out = ROOT/"aiden_say.mp3"; out.write_bytes(audio)
            subprocess.run(["afplay", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception as e:
            console.print(Panel(f"TTS ERROR: {e}. Falling back to macOS voice.", style="yellow"))
    subprocess.run(["say", text])

def record(path:Path, seconds:int=SEC, sr:int=SR):
    console.print("[cyan]🎧 Listening…[/]")
    frames = sd.rec(int(seconds*sr), samplerate=sr, channels=1, dtype="int16"); sd.wait()
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(frames.tobytes())

def transcribe(path:Path)->str:
    with path.open("rb") as f:
        tr = ai.audio.transcriptions.create(model="whisper-1", file=f)
    return (getattr(tr,"text","") or "").strip()

def think(prompt:str)->str:
    r = ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"You are Aiden, Adam's concise terminal copilot. If the user wants to run a host command, suggest using !host run 'command' format."},
            {"role":"user","content":prompt}
        ],
        temperature=0.6
    )
    return r.choices[0].message.content

def execute_host_command(command: str, dry_run: bool = True) -> str:
    """Execute a host command using the host executor"""
    try:
        # Parse command and parameters
        # Handle multi-word command names like "open finder"
        if command.startswith("open finder"):
            cmd_name = "open finder"
            params = command[12:].strip().split()  # Remove "open finder" prefix
        elif command.startswith("open cursor"):
            cmd_name = "open cursor"
            params = command[12:].strip().split()  # Remove "open cursor" prefix
        elif command.startswith("open vscode"):
            cmd_name = "open vscode"
            params = command[12:].strip().split()  # Remove "open vscode" prefix
        elif command.startswith("open safari"):
            cmd_name = "open safari"
            params = command[12:].strip().split()  # Remove "open safari" prefix
        elif command.startswith("list files"):
            cmd_name = "list files"
            params = command[10:].strip().split()  # Remove "list files" prefix
        elif command.startswith("create dir"):
            cmd_name = "create dir"
            params = command[11:].strip().split()  # Remove "create dir" prefix
        elif command.startswith("copy file"):
            cmd_name = "copy file"
            params = command[10:].strip().split()  # Remove "copy file" prefix
        elif command.startswith("move file"):
            cmd_name = "move file"
            params = command[10:].strip().split()  # Remove "move file" prefix
        elif command.startswith("kill process"):
            cmd_name = "kill process"
            params = command[13:].strip().split()  # Remove "kill process" prefix
        elif command.startswith("show processes"):
            cmd_name = "show processes"
            params = command[15:].strip().split()  # Remove "show processes" prefix
        elif command.startswith("git clone"):
            cmd_name = "git clone"
            params = command[10:].strip().split()  # Remove "git clone" prefix
        elif command.startswith("git pull"):
            cmd_name = "git pull"
            params = command[9:].strip().split()  # Remove "git pull" prefix
        elif command.startswith("git status"):
            cmd_name = "git status"
            params = command[11:].strip().split()  # Remove "git status" prefix
        elif command.startswith("git add"):
            cmd_name = "git add"
            params = command[8:].strip().split()  # Remove "git add" prefix
        elif command.startswith("git commit"):
            cmd_name = "git commit"
            params = command[11:].strip().split()  # Remove "git commit" prefix
        elif command.startswith("npm dev"):
            cmd_name = "npm dev"
            params = command[8:].strip().split()  # Remove "npm dev" prefix
        elif command.startswith("npm install"):
            cmd_name = "npm install"
            params = command[12:].strip().split()  # Remove "npm install" prefix
        elif command.startswith("python script"):
            cmd_name = "python script"
            params = command[14:].strip().split()  # Remove "python script" prefix
        elif command.startswith("python run"):
            cmd_name = "python run"
            params = command[11:].strip().split()  # Remove "python run" prefix
        elif command.startswith("aiden chat"):
            cmd_name = "aiden chat"
            params = command[11:].strip().split()  # Remove "aiden chat" prefix
        elif command.startswith("aiden voice"):
            cmd_name = "aiden voice"
            params = command[12:].strip().split()  # Remove "aiden voice" prefix
        elif command.startswith("aiden doctor"):
            cmd_name = "aiden doctor"
            params = command[13:].strip().split()  # Remove "aiden doctor" prefix
        else:
            # Default parsing for single-word commands
            parts = command.split()
            cmd_name = parts[0]
            params = parts[1:] if len(parts) > 1 else []
        
        cmd = [ROOT/".venv311/bin/python", str(ROOT/"apps/host/host.py"), "run", cmd_name] + params
        if dry_run:
            cmd.append("--dry-run")
        
        # Set PIN for non-interactive execution
        env = os.environ.copy()
        env["CLI_PIN"] = os.getenv("AIDEN_PIN", "2188")
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=ROOT)
        return result.stdout + (result.stderr if result.stderr else "")
    except Exception as e:
        return f"Error executing host command: {e}"

def chat_loop():
    console.print(Panel("🤖 Aiden CHAT mode. Type 'exit' to quit. Use !host run 'command' for host operations.", style="bold green"))
    while True:
        try: msg = input("\nYou: ").strip()
        except (EOFError,KeyboardInterrupt): print(); break
        if msg.lower() in {"exit","quit","q"}: break
        if not msg: continue
        
        # Check for host commands
        if msg.startswith("!host run "):
            command = msg[10:].strip("'\"")  # Remove !host run and quotes
            console.print(Panel(f"Executing host command: {command}", title="Host Executor", style="yellow"))
            result = execute_host_command(command, dry_run=False)
            console.print(Panel(result, title="Result", style="blue"))
            if SPEAK_REPLIES: speak("Host command executed")
        elif msg.startswith("!host dry "):
            command = msg[11:].strip("'\"")  # Remove !host dry and quotes
            console.print(Panel(f"Dry run for host command: {command}", title="Host Executor", style="yellow"))
            result = execute_host_command(command, dry_run=True)
            console.print(Panel(result, title="Dry Run Result", style="blue"))
        else:
            reply = think(msg); console.print(Panel(reply, title="Aiden"))
            if SPEAK_REPLIES: speak(reply)

def voice_loop():
    console.print(Panel("🎤 VOICE mode — Press ENTER to speak. Say 'open finder' or similar for host commands.", style="bold green"))
    while True:
        try: input("🔸 Press ENTER… ")
        except (EOFError,KeyboardInterrupt): print(); break
        wav = ROOT/"command.wav"; record(wav)
        text = transcribe(wav)
        if not text: speak("I didn't catch that."); continue
        console.print(Panel(text, title="You", style="cyan"))
        
        # Check if this is a host command request
        if any(keyword in text.lower() for keyword in ["open", "start", "run", "launch", "find", "show"]):
            # Suggest host command format
            reply = f"I heard: '{text}'. To execute this as a host command, type: !host run '{text}' in chat mode."
            console.print(Panel(reply, title="Aiden", style="magenta"))
            speak(reply)
        else:
            reply = think(text); console.print(Panel(reply, title="Aiden", style="magenta")); speak(reply)

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--voice", action="store_true"); args=ap.parse_args()
    if args.voice: voice_loop()
    else: chat_loop()