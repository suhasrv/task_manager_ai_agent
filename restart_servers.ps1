# ==============================================================================
# Task Manager Agent - PowerShell Script to Kill & Restart All Servers
# ==============================================================================

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectDir

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Stopping processes on ports 8000 and 8501..." -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

$pids = Get-NetTCPConnection -LocalPort 8000, 8501 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($pids) {
    foreach ($p in $pids) {
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped process $p" -ForegroundColor Green
    }
} else {
    Write-Host "Ports 8000 and 8501 are already clear." -ForegroundColor Gray
}

Start-Sleep -Seconds 1

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Starting FastAPI Backend and Streamlit Frontend..." -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectDir'; Write-Host 'FastAPI Backend running on http://127.0.0.1:8000' -ForegroundColor Green; .\venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectDir'; Write-Host 'Streamlit Frontend running on http://localhost:8501' -ForegroundColor Green; .\venv\Scripts\streamlit.exe run frontend/app.py --server.port 8501"

Write-Host "✅ Both servers launched in separate windows!" -ForegroundColor Green
Write-Host "Backend:  http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Gray
