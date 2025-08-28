#!/bin/bash
# AIDEN LAUNCHER WITH VIRTUAL ENVIRONMENT
# This script launches Aiden using the virtual environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PYTHON="/Users/adammach/aiden-project/apps/replit-mvp/aiden_venv/bin/python"

echo "🤖 Starting Aiden with virtual environment..."
echo "🐍 Using Python: $VENV_PYTHON"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Launch Aiden
"$VENV_PYTHON" "$SCRIPT_DIR/superintelligence.py" "$@"
