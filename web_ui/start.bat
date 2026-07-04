@echo off
REM Face Liveness Detection - Web UI Launcher
REM Windows batch script

echo.
echo ========================================
echo Face Liveness Detection - Web UI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip list | find "flask" >nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start backend
echo.
echo Starting Face Liveness Detection server...
echo.
echo OPEN THIS URL IN YOUR BROWSER:
echo ========================================
echo http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python backend.py
pause
