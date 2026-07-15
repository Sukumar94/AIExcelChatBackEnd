@echo off
REM Permanent API Startup Script - Ensures clean database connection

echo Killing any existing Python processes...
taskkill /F /IM python.exe /T >nul 2>&1

echo Waiting for file locks to release...
timeout /t 3 /nobreak

echo Starting AI Excel Analytics Platform...
python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause
