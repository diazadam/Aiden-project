#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 /absolute/path/to/aiden_power_stack_v2.zip /absolute/path/to/Aiden-project"
  exit 1
fi

ZIP_PATH="$1"
REPO_ROOT="$2"
APP_ROOT="$REPO_ROOT/apps/replit-mvp"
TMP_DIR="$(mktemp -d -t aiden_stack_XXXX)"
BACKUP_DIR="$REPO_ROOT/.import_backups/$(date +%Y%m%d_%H%M%S)"

echo "→ Unzipping $ZIP_PATH to $TMP_DIR"
unzip -q "$ZIP_PATH" -d "$TMP_DIR"

# Try to locate a source folder inside the ZIP that contains 'brain/', 'skills/', 'public/' etc.
SRC="$TMP_DIR"
if [[ -d "$TMP_DIR/apps/replit-mvp" ]]; then
  SRC="$TMP_DIR/apps/replit-mvp"
elif [[ -d "$TMP_DIR/replit-mvp" ]]; then
  SRC="$TMP_DIR/replit-mvp"
fi

mkdir -p "$APP_ROOT" "$BACKUP_DIR"

echo "→ Backing up replaced files to $BACKUP_DIR"
rsync -avh --backup --backup-dir="$BACKUP_DIR" \
  --exclude ".DS_Store" --exclude "__pycache__" \
  "$SRC/" "$APP_ROOT/"

echo "→ Ensuring package inits exist"
touch "$APP_ROOT/brain/__init__.py" || true
touch "$APP_ROOT/skills/__init__.py" || true
mkdir -p "$APP_ROOT/skills/_sandboxed" && touch "$APP_ROOT/skills/_sandboxed/__init__.py" || true

echo "✅ Import complete. Backups (if any): $BACKUP_DIR"
echo "Next: run scripts/verify_power_stack.py /path/to/Aiden-project"