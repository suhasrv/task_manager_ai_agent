# Start Frontend Server
Write-Host "Starting Frontend Server..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

$streamlitExe = Join-Path $PSScriptRoot "venv\Scripts\streamlit.exe"
if (-not (Test-Path $streamlitExe)) {
    Write-Host "❌ Virtual environment not found at $streamlitExe!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Virtual environment detected" -ForegroundColor Green
Write-Host "🚀 Starting Streamlit app on http://localhost:8501" -ForegroundColor Cyan
Write-Host ""

& $streamlitExe run frontend/app.py --server.port 8501


