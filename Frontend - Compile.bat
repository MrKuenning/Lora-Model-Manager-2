@echo off
echo Compiling Vue Frontend for Production...
cd frontend
call npm run build
echo.
echo Build complete! You can now run Start Server.bat and navigate to http://localhost:8080
pause
