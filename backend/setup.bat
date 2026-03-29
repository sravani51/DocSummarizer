@echo off
echo Installing DocSummarizer Backend...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    exit /b 1
)

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To run the server:
echo   1. Make sure you're in the backend directory
echo   2. Run: python app.py
echo.
echo The API will be available at: http://localhost:5000
echo.
