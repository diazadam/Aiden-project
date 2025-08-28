#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

NOW=$(date +"%Y-%m-%d %H:%M")
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "(no git)")

summary() {
  echo "## Latest Summary (auto-generated ${NOW})"
  echo
  echo "### Branch"
  echo "- ${BRANCH}"
  echo
  echo "### Changes (last 24h)"
  git log --since='24 hours ago' --pretty=format:'- %h %ad %s (%an)' --date=short 2>/dev/null || echo "- (no git history yet)"
  echo
  echo "### Diff Stats (last commit)"
  git diff --stat HEAD~1..HEAD 2>/dev/null || echo "(no diff - initialize git with: git init && git add . && git commit -m 'Initial commit')"
  echo
  echo "### TODO snapshot"
  if [[ -f TODO.md ]]; then
    sed -n '1,20p' TODO.md
  else
    echo "(create TODO.md)"
  fi
}

# Print to stdout (caller can redirect into HANDOFF.md between markers)
summary