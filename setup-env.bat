@echo off
echo ========================================
echo API Key Setup
echo ========================================
echo.
echo This project requires API keys.
echo.
echo Get your API keys:
echo   1. Gemini API: https://makersuite.google.com/app/apikey
echo   2. Perplexity API: https://www.perplexity.ai/settings/api
echo.
echo ========================================
echo.

set /p GEMINI_KEY="Enter GEMINI_API_KEY: "
set /p PERPLEXITY_KEY="Enter PERPLEXITY_API_KEY: "

echo.
echo [1/2] Creating backend/.env...
(
echo GEMINI_API_KEY=%GEMINI_KEY%
echo PERPLEXITY_API_KEY=%PERPLEXITY_KEY%
echo HOST=0.0.0.0
echo PORT=8000
) > backend\.env

if exist backend\.env (
    echo backend\.env created successfully
) else (
    echo Failed to create backend\.env
    pause
    exit /b 1
)

echo.
echo [2/2] Creating .env for Docker...
(
echo GEMINI_API_KEY=%GEMINI_KEY%
echo PERPLEXITY_API_KEY=%PERPLEXITY_KEY%
echo LANGSMITH_API_KEY=
) > .env

if exist .env (
    echo .env created successfully
) else (
    echo Failed to create .env
    pause
    exit /b 1
)

echo.
echo ========================================
echo API keys configured!
echo ========================================
echo.
echo Next steps:
echo   1. Run install.bat
echo   2. Run run-all.bat
echo.
pause
