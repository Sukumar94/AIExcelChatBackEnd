# Permanent API Startup Script for PowerShell
# Ensures clean database connection by killing stale processes

Write-Host "🔄 Killing any existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "⏳ Waiting 5 seconds for file locks to release..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🚀 Starting AI Excel Analytics Platform..." -ForegroundColor Green
Write-Host "📊 API running on http://localhost:8000" -ForegroundColor Cyan
Write-Host "📖 Docs at http://localhost:8000/docs" -ForegroundColor Cyan

python -m uvicorn main:app --host 0.0.0.0 --port 8000

Write-Host "❌ API stopped" -ForegroundColor Red
