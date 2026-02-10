@echo off
echo ============================================
echo Executive Intelligence - Screenshot Tool
echo ============================================
echo.

REM Check if server is running
curl -s http://127.0.0.1:5100 > nul 2>&1
if errorlevel 1 (
    echo [WARNING] Server not detected at http://127.0.0.1:5100
    echo Starting server...
    start /B python web\app.py
    echo Waiting for server to start...
    timeout /t 5 /nobreak > nul
)

REM Run screenshot tool
echo.
echo Running screenshot capture...
python scripts\capture_screenshots.py %*

echo.
echo Screenshots saved to: screenshots\
pause
