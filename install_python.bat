@echo off
REM Script to verify and install Python for CK3 Character Manager

setlocal enabledelayedexpansion

title CK3 Character Manager - Python Verification

echo.
echo ================================================
echo CK3 Character Manager - Python Verification
echo ================================================
echo.

REM Check if Python exists in common installation paths
if exist "C:\Program Files\Python314\python.exe" (
    echo [OK] Python 3.14 is installed!
    "C:\Program Files\Python314\python.exe" --version
    echo.
    echo Press any key to continue...
    pause >nul
    goto :eof
)

if exist "C:\Program Files\Python313\python.exe" (
    echo [OK] Python 3.13 is installed!
    "C:\Program Files\Python313\python.exe" --version
    echo.
    echo Press any key to continue...
    pause >nul
    goto :eof
)

if exist "C:\Program Files\Python312\python.exe" (
    echo [OK] Python 3.12 is installed!
    "C:\Program Files\Python312\python.exe" --version
    echo.
    echo Press any key to continue...
    pause >nul
    goto :eof
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python314\python.exe" (
    echo [OK] Python 3.14 is installed!
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python314\python.exe" --version
    echo.
    echo Press any key to continue...
    pause >nul
    goto :eof
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe" (
    echo [OK] Python 3.13 is installed!
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe" --version
    echo.
    echo Press any key to continue...
    pause >nul
    goto :eof
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    echo [OK] Python 3.12 is installed!
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" --version
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
