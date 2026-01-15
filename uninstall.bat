@echo off
REM Quick Tasks Uninstaller
REM Removes the application and registry entries

setlocal

set APP_NAME=QuickTasks
set INSTALL_DIR=%LOCALAPPDATA%\QuickTasks

echo ========================================
echo Quick Tasks Uninstaller
echo ========================================
echo.

choice /c yn /m "Remove Quick Tasks from your computer?"
if errorlevel 2 goto :cancelled

REM Kill running process
echo Stopping Quick Tasks...
taskkill /f /im QuickTasks.exe > nul 2>&1

REM Remove from startup
echo Removing auto-start...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "%APP_NAME%" /f > nul 2>&1

REM Remove installation directory
echo Removing files...
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
    echo Removed: %INSTALL_DIR%
)

echo.
echo ========================================
echo Uninstall complete!
echo ========================================
echo.
goto :end

:cancelled
echo Uninstall cancelled.

:end
pause
