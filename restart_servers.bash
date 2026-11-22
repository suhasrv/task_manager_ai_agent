#!/usr/bin/env bash

# ==============================================================================
# Task Manager Agent Studio - Kill & Restart All Servers (.bash script)
# ==============================================================================

# Ensure script runs from the repository root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "=================================================="
echo "⚡ Step 1: Stopping all running servers (8000 & 8501)..."
echo "=================================================="

# Function to terminate any process bound to a specific port
kill_port() {
    local port=$1
    echo "Checking port $port..."

    # If running on Windows (Git Bash / MSYS / PowerShell available)
    if command -v powershell.exe &>/dev/null; then
        powershell.exe -NoProfile -Command "
            \$pids = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique;
            if (\$pids) {
                foreach (\$p in \$pids) {
                    Stop-Process -Id \$p -Force -ErrorAction SilentlyContinue;
                    Write-Host \"Stopped PID \$p on port $port\";
                }
            } else {
                Write-Host \"Port $port is clear.\";
            }
        "
    # If running on Linux / WSL / macOS
    elif command -v fuser &>/dev/null; then
        fuser -k "${port}/tcp" 2>/dev/null || true
    elif command -v lsof &>/dev/null; then
        local pid
        pid=$(lsof -ti :"$port")
        if [ -n "$pid" ]; then
            kill -9 "$pid" 2>/dev/null || true
            echo "Killed PID $pid on port $port"
        fi
    fi
}

kill_port 8000
kill_port 8501

sleep 1

echo "=================================================="
echo "🚀 Step 2: Starting Backend & Frontend Servers..."
echo "=================================================="

# Locate Virtual Environment binaries
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

echo "Using Python: $PYTHON_BIN"

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
echo "   - Backend PID:      $BACKEND_PID"
echo "   - Frontend PID:     $FRONTEND_PID"
echo "=================================================="
echo "Press Ctrl+C at any time to gracefully terminate both servers."

# Trap interrupt signals (Ctrl+C) to terminate both background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down all servers..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    kill_port 8000
    kill_port 8501
    echo "All servers stopped."
    exit 0
}

trap cleanup INT TERM EXIT

wait
