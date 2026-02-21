@echo off
echo ========================================
echo Starting Backend + Frontend (venv)
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Starting backend server (with venv)...
start "Backend Server" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\activate.bat && echo Backend: http://localhost:2024 && langgraph dev"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting frontend server...
start "Frontend Server" cmd /k "cd /d "%~dp0frontend" && echo Frontend: http://localhost:5173 && npm run dev"

echo.
echo ========================================
echo Servers started!
echo ========================================
echo.
echo Backend: http://localhost:2024
echo Frontend: http://localhost:5173
echo.
echo Open http://localhost:5173 in your browser!
echo.
pause
