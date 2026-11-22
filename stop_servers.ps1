# Stop Task Manager Servers (Ports 8000 and 8501)
Write-Host "Stopping Task Manager Servers..." -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow

$ports = @(8000, 8501)
$stoppedAny = $false

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            try {
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                Write-Host "✅ Stopped server process $procId on port $port" -ForegroundColor Green
                $stoppedAny = $true
            } catch {
                Write-Host "⚠️ Could not stop process $procId on port $port" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "ℹ️ Port $port is already free" -ForegroundColor Gray
    }
}

if ($stoppedAny) {
    Write-Host "✅ All servers stopped successfully." -ForegroundColor Green
} else {
    Write-Host "ℹ️ No running servers found on ports 8000 or 8501." -ForegroundColor Cyan
}
