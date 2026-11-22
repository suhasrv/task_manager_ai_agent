#!/usr/bin/env bash

# ==============================================================================
# Task Manager Agent - Server Restart & Watchdog Script (Bash)
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "=================================================="
echo "⚡ Task Manager Agent: Killing old servers..."
echo "=================================================="

# Kill any existing processes listening on ports 8000 and 8501
kill_port() {
    local port=$1
    if command -v powershell.exe &>/dev/null; then
        powershell.exe -NoProfile -Command "
            \$pids = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique;
            if (\$pids) {
                foreach (\$p in \$pids) {
                    Stop-Process -Id \$p -Force -ErrorAction SilentlyContinue;
                    Write-Host \"Killed process \$p on port $port\";
                }
            } else {
                Write-Host \"Port $port is free.\";
            }
        "
    elif command -v fuser &>/dev/null; then
        fuser -k "${port}/tcp" 2>/dev/null || true
    fi
}

kill_port 8000
kill_port 8501

sleep 1

echo "=================================================="
echo "🚀 Starting fresh backend and frontend servers..."
echo "=================================================="

# Determine Python and Streamlit binaries
if [ -f "./venv/Scripts/python.exe" ]; then
    PYTHON_BIN="./venv/Scripts/python.exe"
    STREAMLIT_BIN="./venv/Scripts/streamlit.exe"
elif [ -f "./venv/bin/python" ]; then
    PYTHON_BIN="./venv/bin/python"
    STREAMLIT_BIN="./venv/bin/streamlit"
else
    PYTHON_BIN="python"
    STREAMLIT_BIN="streamlit"
fi

# 1. Start FastAPI Backend in background
echo "Starting FastAPI Backend on http://127.0.0.1:8000..."
"$PYTHON_BIN" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 2

# 2. Start Streamlit Frontend in background
echo "Starting Streamlit Frontend on http://localhost:8501..."
"$STREAMLIT_BIN" run frontend/app.py --server.port 8501 &
FRONTEND_PID=$!

echo "=================================================="
echo "✅ Both servers are online!"
echo "   - FastAPI Backend:  http://127.0.0.1:8000/docs"
echo "   - Streamlit Studio: http://localhost:8501"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo "=================================================="
echo "Press Ctrl+C at any time to stop both servers."

# Trap Ctrl+C (SIGINT) and cleanup
trap "echo ''; echo '🛑 Stopping all servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; kill_port 8000; kill_port 8501; echo 'Servers stopped.'; exit 0" INT TERM EXIT

wait
