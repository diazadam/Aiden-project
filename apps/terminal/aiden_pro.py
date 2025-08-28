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
            {"role":"system","content":"You are Aiden, Adam's concise terminal copilot."},
            {"role":"user","content":prompt}
        ],
        temperature=0.6
    )
    return r.choices[0].message.content

def chat_loop():
    console.print(Panel("🤖 Aiden CHAT mode. Type 'exit' to quit.", style="bold green"))
    while True:
        try: msg = input("\nYou: ").strip()
        except (EOFError,KeyboardInterrupt): print(); break
        if msg.lower() in {"exit","quit","q"}: break
        if not msg: continue
        reply = think(msg); console.print(Panel(reply, title="Aiden"))
        if SPEAK_REPLIES: speak(reply)

def voice_loop():
    console.print(Panel("🎤 VOICE mode — Press ENTER to speak", style="bold green"))
    while True:
        try: input("🔸 Press ENTER… ")
        except (EOFError,KeyboardInterrupt): print(); break
        wav = ROOT/"command.wav"; record(wav)
        text = transcribe(wav)
        if not text: speak("I didn't catch that."); continue
        console.print(Panel(text, title="You", style="cyan"))
        reply = think(text); console.print(Panel(reply, title="Aiden", style="magenta")); speak(reply)

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--voice", action="store_true"); args=ap.parse_args()
    if args.voice: voice_loop()
    else: chat_loop()