@echo off
REM Quick Start Script for MathSearch (Windows)

echo =================================
echo MathSearch - Quick Start
echo =================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.8+ first
    pause
    exit /b 1
)

echo Python found
echo.

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed
echo.

REM Run the application
echo Starting MathSearch...
echo.
python main.py

pause
