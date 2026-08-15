@echo off
title AI Lora Model Manager
cd /d "%~dp0"

echo ============================================================
echo               AI LORA MODEL MANAGER
echo ============================================================
echo.

:: Detect Python executable (prefer local venv if available)
if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
) else (
    python --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        py -3 --version >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            set "PYTHON_EXE=py -3"
        ) else (
            echo [ERROR] Python is not installed or not in your PATH.
            echo Please run 'install.bat' to set up the environment.
            echo.
            pause
            exit /b 1
        )
    )
)

:: Start the server
echo Starting backend server...
echo.
%PYTHON_EXE% run.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Server stopped with an error code: %ERRORLEVEL%
    pause
)
