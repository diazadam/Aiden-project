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

echo
echo "=== Cloud Services ==="

# Supabase connection check
python - <<'PY'
import os
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.getenv('SUPABASE_URL', '').rstrip('/') + '/rest/v1' if os.getenv('SUPABASE_URL') else None
service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_JWT')
print('Supabase URL:', url or '(missing)')
print('Service Role Key:', 'configured' if service_key else '(missing)')
if url and service_key:
    print('✓ Supabase configuration looks good')
else:
    print('⚠️  Supabase not fully configured')
PY

# GCP credentials check  
python - <<'PY'
import os, pathlib, json
from dotenv import load_dotenv
load_dotenv('.env.local')
sa_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or os.getenv('GCP_SA_PATH', './gcp_service_account.json')
sa_b64 = os.getenv('GCP_SA_JSON_BASE64')
project = os.getenv('GCP_PROJECT_ID')

print('GCP Project:', project or '(missing)')
print('SA Path:', sa_path if pathlib.Path(sa_path).exists() else f'{sa_path} (not found)')
print('SA Base64:', 'configured' if sa_b64 else '(missing)')

if project and (pathlib.Path(sa_path).exists() or sa_b64):
    print('✓ GCP configuration looks good')
else:
    print('⚠️  GCP not fully configured')
PY

echo
ok "Cloud services check complete."