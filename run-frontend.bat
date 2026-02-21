@echo off
echo ========================================
echo Starting Frontend Server
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Browser: http://localhost:5173
echo Backend: http://localhost:2024
echo.
echo Starting frontend server...
echo.

npm run dev

pause
