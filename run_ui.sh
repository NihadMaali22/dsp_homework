#!/usr/bin/env bash
# Quick launcher for DSP Interactive GUI
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 gui.py "$@"
