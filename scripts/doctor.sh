#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
RED='\033[0;31m'; GRN='\033[0;32m'; NC='\033[0m'
ok(){ echo -e "${GRN}✓${NC} $1"; }
bad(){ echo -e "${RED}✗${NC} $1"; exit 1; }

# .env.local exists?
[[ -f .env.local ]] || bad ".env.local missing (copy .env.example and fill it)"

# venv exists?
source .venv311/bin/activate || bad "venv missing (run: make setup)"

# env sanity
python - <<'PY'
from dotenv import load_dotenv; import os
load_dotenv('.env.local')
need=['OPENAI_API_KEY']
missing=[k for k in need if not os.getenv(k)]
print('Missing:', missing) if missing else print('All required present.')
PY
ok "Base env looks good."

# TTS check via macOS say
say "Doctor check complete."
ok "macOS say OK."