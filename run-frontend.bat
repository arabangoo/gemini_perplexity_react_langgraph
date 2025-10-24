@echo off
echo ========================================
echo Starting Frontend Server
echo ========================================
echo.

cd /d C:\git_clone\gemini-react-langgraph-fullstack\frontend

echo Browser: http://localhost:5173
echo Backend: http://localhost:8123
echo.
echo Starting frontend server...
echo.

npm run dev

pause
