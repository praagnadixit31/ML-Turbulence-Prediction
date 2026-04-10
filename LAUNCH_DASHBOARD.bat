@echo off
REM ========================================
REM   TurbuPredict Dashboard Launcher
REM ========================================

echo.
echo =======================================
echo   TURBULENCE PREDICTION DASHBOARD
echo =======================================
echo.

REM Check if results directory exists
if not exist "results\" (
    echo WARNING: Results directory not found!
    echo Please run AirPort_main.py first to generate graphs.
    echo.
    pause
    exit /b
)

REM Check if graph files exist
set GRAPH_COUNT=0
for %%f in (results\*.png) do set /a GRAPH_COUNT+=1

if %GRAPH_COUNT% LSS 5 (
    echo WARNING: Only %GRAPH_COUNT% graph files found!
    echo Expected at least 5 graphs.
    echo Please run AirPort_main.py to generate all graphs.
    echo.
    pause
)

echo Opening dashboard in default browser...
echo.
start dashboard\index.html

echo.
echo ✓ Dashboard opened successfully!
echo.
echo TIP: If graphs don't appear, run AirPort_main.py first.
echo.
pause
