#!/usr/bin/env bash
# Launcher script for S&P 500 Arbitrage & Reconstitution Engine Web Application
set -eu
(set -o pipefail 2>/dev/null) && set -o pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

VENV_DIR="$DIR/.venv"
REQ_FILE="$DIR/requirements.txt"
HASH_FILE="$VENV_DIR/.requirements.sha256"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating local virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# POSIX-compatible activation
. "$VENV_DIR/bin/activate"

# Hash-gated dependency installation (offline-safe when already synced)
if [ -f "$REQ_FILE" ]; then
    REQ_HASH="$(python -c "import hashlib, pathlib; print(hashlib.sha256(pathlib.Path('$REQ_FILE').read_bytes()).hexdigest())")"
    OLD_HASH=""
    if [ -f "$HASH_FILE" ]; then
        OLD_HASH="$(cat "$HASH_FILE")"
    fi
    if [ "$REQ_HASH" != "$OLD_HASH" ] || ! python -c "import streamlit, pandas" >/dev/null 2>&1; then
        echo "Syncing dependencies from requirements.txt..."
        python -m pip install -r "$REQ_FILE"
        printf "%s" "$REQ_HASH" > "$HASH_FILE"
    fi
fi

# Probe for a free local port starting at 8502 (no kill -9)
PORT="$(python -c "
import socket
for port in range(8502, 8552):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', port)) != 0:
            print(port)
            break
")"

if [ -z "$PORT" ]; then
    echo "Error: Could not find a free port in range 8502-8551." >&2
    exit 1
fi

echo "Starting S&P 500 Arbitrage Web Application on http://localhost:$PORT ..."
exec streamlit run app.py --server.port "$PORT" --server.headless true
