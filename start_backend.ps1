# Start Backend Server
Write-Host "Starting Backend Server..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

$pythonExe = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "❌ Virtual environment not found at $pythonExe!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Virtual environment detected" -ForegroundColor Green
Write-Host "🚀 Starting FastAPI server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

& $pythonExe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload


