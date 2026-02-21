@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

echo Memory: MemorySaver (volatile)
echo API Keys: Gemini + Perplexity
echo Server: http://localhost:2024
echo.
echo Starting backend server...
echo.

langgraph dev --no-browser --allow-blocking

pause
