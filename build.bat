@echo off
REM Quick Tasks Build Script
REM Builds the application into a standalone Windows executable

echo ========================================
echo Quick Tasks - Build Script
echo ========================================
echo.

REM Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

REM Check/install PyInstaller
pip show pyinstaller > nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build
echo Building executable...
pyinstaller quick_tasks.spec --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)

echo.
echo ========================================
echo Build complete!
echo Executable: dist\QuickTasks.exe
echo ========================================

REM Copy credentials template if not in dist
if not exist "dist\config" mkdir "dist\config"
echo.
echo IMPORTANT: Copy your credentials.json to dist\config\
echo.

pause
