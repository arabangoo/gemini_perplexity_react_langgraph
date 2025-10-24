@echo off
echo ========================================
echo Starting Backend + Frontend
echo ========================================
echo.

cd /d C:\실제 경로

echo [1/2] Starting backend server...
start "Backend Server" cmd /k "cd /d C:\실제 경로\backend && echo Backend: http://localhost:8123 && langgraph dev --no-browser --allow-blocking"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting frontend server...
start "Frontend Server" cmd /k "cd /d C:\실제 경로\frontend && echo Frontend: http://localhost:5173 && npm run dev"

echo.
echo ========================================
echo Servers started!
echo ========================================
echo.
echo Backend: http://localhost:8123
echo Frontend: http://localhost:5173
echo.
echo Open http://localhost:5173 in your browser!
echo.
pause
