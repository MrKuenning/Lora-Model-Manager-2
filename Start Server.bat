@echo off
title LMM Server
echo Starting Lora Model Manager Backend (Flask + SQLite)...

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

:: Install requirements
echo Installing dependencies...
python -m pip install -r backend\requirements.txt

:: Start the server
echo Starting server...
python run.py

pause
