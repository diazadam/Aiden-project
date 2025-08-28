# 🤖 Aiden Project

**One clean repo for all Adam's AI assistants**

## Quick Start

```bash
cd ~/aiden-project
make setup
make run-chat    # terminal chat
make run-voice   # press Enter to speak
```

## Structure

```
apps/
  terminal/      # Main chat/voice agent
  host/          # Local executor (future)
libs/
  shared/        # Common utilities
ops/
  n8n/          # Automation workflows
_archive/        # All old projects (safe)
```

## Commands

- `make setup` — Create Python 3.11 venv & install deps
- `make doctor` — Test configuration
- `make run-chat` — Start terminal chat mode
- `make run-voice` — Start voice mode (press Enter to speak)

## Configuration

All secrets are in `.env.local` (gitignored). Copy `.env.example` to get started.

Includes keys for: OpenAI, Anthropic, ElevenLabs, Supabase, Google AI, Pinecone, LangChain, Cursor.

---

> 🏃‍♂️ **TL;DR:** `make setup && make run-chat`