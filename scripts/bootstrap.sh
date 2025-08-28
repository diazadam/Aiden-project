#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
make setup
echo "✓ Env ready. Copy .env.example to .env.local and fill your keys."