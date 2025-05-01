@echo off
echo ===================================
echo BGTANK Launcher Fix Utility
echo ===================================
echo.
echo Attempting to launch BGTANK properly...
echo.

:: Check if Python is in PATH
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found in PATH.
    echo Please install Python and make sure it's added to your PATH.
    pause
    exit /b 1
)

:: Ensure we're in the correct directory (where the batch file is located)
cd /d "%~dp0"

:: Check if launcher.py exists
if not exist "launcher.py" (
    echo ERROR: launcher.py not found in the current directory.
    echo Please make sure this fix.bat file is in the same directory as launcher.py.
    pause
    exit /b 1
)

echo Found launcher.py, starting application...
echo.

:: Launch the launcher script
python launcher.py

:: Capture the exit code
set EXIT_CODE=%ERRORLEVEL%

:: If there was an error, provide additional information
if %EXIT_CODE% neq 0 (
    echo.
    echo ===================================
    echo Launch failed with exit code: %EXIT_CODE%
    echo.
    echo If the problem persists, try:
    echo 1. Reinstalling Python
    echo 2. Running as administrator
    echo 3. Checking your internet connection
    echo 4. Install git from: https://git-scm.com/downloads
    echo ===================================
)

:: Wait for user input before closing
pause
exit /b %EXIT_CODE%