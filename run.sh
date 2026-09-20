#!/bin/bash
# Launcher script for S&P 500 Arbitrage & Reconstitution Engine Web Application

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Use virtualenv python
if [ -f "$DIR/../learning/.venv/bin/streamlit" ]; then
    STREAMLIT="$DIR/../learning/.venv/bin/streamlit"
elif command -v streamlit &> /dev/null; then
    STREAMLIT="streamlit"
else
    echo "Error: Streamlit not found!"
    exit 1
fi

PORT=8502
echo "Starting S&P 500 Arbitrage Web Application on port $PORT..."
"$STREAMLIT" run app.py --server.port $PORT --server.headless true
