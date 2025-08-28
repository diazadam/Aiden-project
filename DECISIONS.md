# DECISIONS — Source of Truth

Record any irreversible choices here (versions, libraries, structure, providers).

## Stack
- Python: 3.11.x (via .venv311)
- TTS: macOS `say` fallback; ElevenLabs optional (USE_ELEVENLABS=true/false)
- LLMs: OpenAI by default (gpt-4o-mini); Anthropic available
- Audio: sounddevice for recording, wave for file handling
- UI: rich for terminal panels and formatting

## Structure
- Root: `~/aiden-project`
- Apps: `apps/terminal` (chat/voice agent), `apps/host` (future executor)
- Shared libs: `libs/shared` (future common utilities)
- Ops: `ops/n8n` (automation workflows)
- Archive: `_archive/` (all old projects, safely preserved)

## Conventions
- Secrets in `.env.local` (gitignored). Template in `.env.example`.
- Dependencies pinned in requirements.txt
- Python path: ROOT = Path(__file__).resolve().parents[2] for apps
- Single source-of-truth repo; old code archived, never deleted
- Make targets for common operations (setup, doctor, run-chat, run-voice)

## API Keys Consolidated
- OpenAI: Primary LLM (from AidenAlpha project)
- Anthropic: Secondary LLM available
- ElevenLabs: TTS with voice ID dXtC3XhB9GtPusIpNtQx
- Supabase: Database with dedicated project tcafbgregptuaxxoiony
- Google AI: Available for future use
- Pinecone, LangChain, Cursor: All keys preserved

## Voice Configuration
- Sample rate: 16000 Hz
- Recording length: 8 seconds default
- Voice ID: dXtC3XhB9GtPusIpNtQx (from consolidated config)
- Fallback: macOS `say` always available