@echo off
setlocal enabledelayedexpansion
title AI Lora Model Manager - Update
cd /d "%~dp0"

echo ============================================================
echo           AI LORA MODEL MANAGER - UPDATE
echo ============================================================
echo.

:: 1. Check for Git
echo [1/3] Checking for Git...
git --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Git is not installed or not found in your system PATH.
    echo Please install Git from: https://git-scm.com/downloads
    echo or download the latest release zip from GitHub.
    echo.
    pause
    exit /b 1
)

:: 2. Pull latest commits from GitHub
echo [2/3] Pulling latest updates from GitHub...
echo.
git pull origin main
if %ERRORLEVEL% neq 0 (
    echo.
    echo [NOTICE] 'git pull origin main' encountered an issue. Trying 'git pull'...
    git pull
    if %ERRORLEVEL% neq 0 (
        echo.
        echo [WARNING] Failed to pull updates automatically.
        echo If you have modified tracked files locally, please resolve conflicts or stash your changes.
        echo.
        pause
        exit /b 1
    )
)
echo.
echo Repository updated successfully.
echo.

:: 3. Update backend dependencies
echo [3/3] Checking and updating backend dependencies...
if exist "%~dp0venv\Scripts\pip.exe" (
    "%~dp0venv\Scripts\pip.exe" install -r "%~dp0backend\requirements.txt"
) else (
    python "%~dp0run.py" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        python -m pip install -r "%~dp0backend\requirements.txt"
    ) else (
        py -3 -m pip install -r "%~dp0backend\requirements.txt"
    )
)

if %ERRORLEVEL% neq 0 (
    echo [WARNING] Dependency update encountered an issue.
) else (
    echo Dependencies are up to date.
)
echo.

echo ============================================================
echo                 UPDATE COMPLETE!
echo ============================================================
echo.

set /p START_CHOICE="Would you like to start Lora Model Manager now? (Y/n): "
if /i "%START_CHOICE%"=="n" (
    echo.
    echo Exiting. Run 'Lora Manager - Start Server.bat' whenever you're ready!
    pause
    exit /b 0
)

echo.
echo Starting Lora Model Manager...
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" "%~dp0run.py"
) else (
    python "%~dp0run.py" 2>nul || py -3 "%~dp0run.py"
)

pause
