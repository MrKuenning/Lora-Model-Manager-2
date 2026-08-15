@echo off
setlocal enabledelayedexpansion
title AI Lora Model Manager - Installation & Setup
cd /d "%~dp0"

echo ============================================================
echo        AI LORA MODEL MANAGER - INSTALLATION & SETUP
echo ============================================================
echo.

:: 1. Check for Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    py -3 --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo.
        echo [ERROR] Python is not installed or not in your system PATH.
        echo.
        echo Please download and install Python 3.8 or higher from:
        echo   https://www.python.org/downloads/
        echo.
        echo IMPORTANT: When installing, make sure to check the box:
        echo   "Add Python to PATH"
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py -3
    )
) else (
    set PYTHON_CMD=python
)

for /f "tokens=2 delims= " %%v in ('!PYTHON_CMD! --version 2^>^&1') do set PY_VER=%%v
echo Found Python !PY_VER!
echo.

:: 2. Set up Python Virtual Environment (venv)
echo [2/4] Setting up Python virtual environment...
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment in .\venv ...
    !PYTHON_CMD! -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [WARNING] Could not create virtual environment. Falling back to system Python.
        set VENV_PYTHON=!PYTHON_CMD!
        set VENV_PIP=!PYTHON_CMD! -m pip
    ) else (
        echo Virtual environment created successfully.
        set VENV_PYTHON="%~dp0venv\Scripts\python.exe"
        set VENV_PIP="%~dp0venv\Scripts\pip.exe"
    )
) else (
    echo Existing virtual environment found.
    set VENV_PYTHON="%~dp0venv\Scripts\python.exe"
    set VENV_PIP="%~dp0venv\Scripts\pip.exe"
)
echo.

:: 3. Install backend dependencies
echo [3/4] Installing / verifying backend dependencies...
!VENV_PIP! install -r backend\requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies from backend\requirements.txt
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

:: 4. Ensure config.json exists before running wizard
if not exist "backend\config.json" (
    if exist "backend\config-example.json" (
        copy "backend\config-example.json" "backend\config.json" >nul
    )
)

:: 5. Run Initial Setup Wizard
echo [4/4] Starting initial configuration wizard...
echo.
!VENV_PYTHON! backend\setup_wizard.py
echo.

echo ============================================================
echo             INSTALLATION COMPLETE!
echo ============================================================
echo You can launch Lora Model Manager anytime by running:
echo   "Start Server.bat"
echo.

set /p START_CHOICE="Would you like to start the server now? (Y/n): "
if /i "%START_CHOICE%"=="n" (
    echo.
    echo Exiting setup. Run 'Start Server.bat' whenever you're ready!
    pause
    exit /b 0
)

echo.
echo Starting Lora Model Manager Server...
start "" http://localhost:8080
!VENV_PYTHON! run.py

pause
