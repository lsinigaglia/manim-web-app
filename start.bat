@echo off
REM Quick start script for Windows

echo ==========================================
echo Tiny Manim Web App - Quick Start
echo ==========================================
echo.

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please create a .env file with your ANTHROPIC_API_KEY
    echo You can copy .env.example to .env and fill in your API key
    echo.
)

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please ensure Python and pip are installed
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo ==========================================
echo Starting server...
echo ==========================================
echo.
echo Server will be available at: http://localhost:8000
echo.

python -m app.main
