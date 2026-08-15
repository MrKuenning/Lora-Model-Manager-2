@echo off
title AI Lora Model Manager
cd /d "%~dp0"

echo ============================================================
echo               AI LORA MODEL MANAGER
echo ============================================================
echo.

echo Starting backend server...
echo.

:: Detect Python executable (prefer local venv if available)
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" "%~dp0run.py"
) else (
    python "%~dp0run.py" 2>nul
    if %ERRORLEVEL% neq 0 (
        py -3 "%~dp0run.py" 2>nul
        if %ERRORLEVEL% neq 0 (
            echo.
            echo [ERROR] Python is not installed or not in your PATH.
            echo Please run 'Lora Manager - Install.bat' to set up the environment.
            echo.
            pause
            exit /b 1
        )
    )
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo Server stopped with an error code: %ERRORLEVEL%
    pause
)
