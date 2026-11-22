@echo off
REM ==============================================================================
REM Task Manager Agent - Windows Batch Script to Kill and Restart All Servers
REM ==============================================================================

echo ==================================================
echo [1/3] Killing existing processes on ports 8000 and 8501...
echo ==================================================

powershell -NoProfile -Command "$pids = Get-NetTCPConnection -LocalPort 8000, 8501 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if ($pids) { foreach ($p in $pids) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue; Write-Host 'Stopped PID:' $p } } else { Write-Host 'Ports 8000 and 8501 are already clear.' }"

timeout /t 1 /nobreak >nul

echo ==================================================
echo [2/3] Launching FastAPI Backend (Port 8000)...
echo ==================================================
start "Task Manager - FastAPI Backend" cmd /k "cd /d %~dp0 && .\venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

timeout /t 2 /nobreak >nul

echo ==================================================
echo [3/3] Launching Streamlit Frontend (Port 8501)...
echo ==================================================
start "Task Manager - Streamlit Studio" cmd /k "cd /d %~dp0 && .\venv\Scripts\streamlit.exe run frontend/app.py --server.port 8501"

echo ==================================================
echo Done! Both servers launched in separate windows.
echo - Backend:  http://127.0.0.1:8000/docs
echo - Frontend: http://localhost:8501
echo ==================================================
pause
