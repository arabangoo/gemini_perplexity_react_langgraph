@echo off
echo ========================================
echo Installing dependencies...
echo ========================================
echo.

cd /d C:\git_clone\gemini-react-langgraph-fullstack

echo [1/2] Installing backend...
cd backend
pip install -e .
if %errorlevel% neq 0 (
    echo Backend installation failed!
    pause
    exit /b 1
)
echo Backend installation complete.
cd ..

echo.
echo [2/2] Installing frontend...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo Frontend installation failed!
    pause
    exit /b 1
)
echo Frontend installation complete.
cd ..

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo To run:
echo   run-all.bat (recommended)
echo.
pause
