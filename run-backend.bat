@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
echo.

cd /d C:\git_clone\gemini-react-langgraph-fullstack\backend

echo Memory: MemorySaver (volatile)
echo API Keys: Gemini + Perplexity
echo Server: http://localhost:8123
echo.
echo Starting backend server...
echo.

langgraph dev --no-browser --allow-blocking

pause
