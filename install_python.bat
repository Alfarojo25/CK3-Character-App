@echo off
REM Script to verify and install Python for CK3 Character Manager
REM This batch file checks if Python is installed, and if not, provides installation instructions

setlocal enabledelayedexpansion

title CK3 Character Manager - Python Verification

echo.
echo ================================================
echo CK3 Character Manager - Python Verification
echo ================================================
echo.

REM Refresh the system PATH
set "PATH=%PATH%;C:\Program Files\Python314;C:\Program Files\Python313;C:\Program Files\Python312;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python314;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312"

REM Check if Python is installed by running a test script
python -c "import sys; print('Python version:', sys.version)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python is installed!
    for /f "tokens=*" %%A in ('python --version 2^>^&1') do echo %%A
    echo.
    echo Press any key to continue...
    pause >nul
    goto :eof
)

REM Try python3 as alternative
python3 -c "import sys; print('Python version:', sys.version)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python 3 is installed!
    for /f "tokens=*" %%A in ('python3 --version 2^>^&1') do echo %%A
    echo.
    echo Press any key to continue...
    pause >nul
    goto :eof
)

echo [ERROR] Python is not installed on this system
echo.
echo Installing Python...
echo.

REM Check if we have internet connection
timeout /t 2 /nobreak >nul

REM Try to use winget (Windows Package Manager)
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using Windows Package Manager to install Python...
    echo.
    winget install -e --id Python.Python.3.14
    if %errorlevel% equ 0 (
        echo.
        echo [OK] Python installed successfully!
        python --version
        pause
        goto :eof
    )
)

REM If winget failed or not available, try chocolatey
choco --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using Chocolatey to install Python...
    echo.
    choco install python -y
    if %errorlevel% equ 0 (
        echo.
        echo [OK] Python installed successfully!
        refreshenv
        python --version
        pause
        goto :eof
    )
)

REM If all automatic methods failed, show manual installation instructions
echo.
echo [INFO] Automatic installation failed or not possible
echo.
echo Please install Python manually:
echo.
echo 1. Go to https://www.python.org/downloads/windows/
echo 2. Download Python 3.14 or newer
echo 3. Run the installer
echo 4. IMPORTANT: Check "Add Python to PATH" during installation
echo 5. Complete the installation
echo 6. Run this script again
echo.
pause
