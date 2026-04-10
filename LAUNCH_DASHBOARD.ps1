# ========================================
#   TurbuPredict Dashboard Launcher
# ========================================

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "   TURBULENCE PREDICTION DASHBOARD" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if results directory exists
if (-not (Test-Path "results")) {
    Write-Host "WARNING: Results directory not found!" -ForegroundColor Yellow
    Write-Host "Please run AirPort_main.py first to generate graphs." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

# Check if graph files exist
$graphCount = (Get-ChildItem -Path "results\*.png" -ErrorAction SilentlyContinue).Count

if ($graphCount -lt 5) {
    Write-Host "WARNING: Only $graphCount graph files found!" -ForegroundColor Yellow
    Write-Host "Expected at least 5 graphs." -ForegroundColor Yellow
    Write-Host "Please run AirPort_main.py to generate all graphs." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Opening dashboard in default browser..." -ForegroundColor Green
Write-Host ""

# Open dashboard
$dashboardPath = Join-Path $PSScriptRoot "dashboard\index.html"
Start-Process $dashboardPath

Write-Host ""
Write-Host "✓ Dashboard opened successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "TIP: If graphs don't appear, run AirPort_main.py first." -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
