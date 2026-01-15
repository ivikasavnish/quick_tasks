@echo off
REM Quick Tasks Installer
REM Copies the application to Program Files and sets up auto-start

setlocal

set APP_NAME=QuickTasks
set INSTALL_DIR=%LOCALAPPDATA%\QuickTasks
set EXE_NAME=QuickTasks.exe

echo ========================================
echo Quick Tasks Installer
echo ========================================
echo.

REM Check if we have the built executable
if not exist "dist\%EXE_NAME%" (
    echo ERROR: dist\%EXE_NAME% not found!
    echo Please run build.bat first.
    pause
    exit /b 1
)

REM Check for credentials
if not exist "config\credentials.json" (
    echo WARNING: config\credentials.json not found!
    echo You will need to add this file before using the app.
    echo.
)

REM Create installation directory
echo Installing to: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\config" mkdir "%INSTALL_DIR%\config"

REM Copy files
echo Copying files...
copy /y "dist\%EXE_NAME%" "%INSTALL_DIR%\" > nul

REM Copy credentials if exists
if exist "config\credentials.json" (
    copy /y "config\credentials.json" "%INSTALL_DIR%\config\" > nul
    echo Copied credentials.json
)

REM Copy icon if exists
if exist "resources\icon.ico" (
    if not exist "%INSTALL_DIR%\resources" mkdir "%INSTALL_DIR%\resources"
    copy /y "resources\icon.ico" "%INSTALL_DIR%\resources\" > nul
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Location: %INSTALL_DIR%
echo.

REM Ask about auto-start
choice /c yn /m "Enable auto-start with Windows?"
if errorlevel 2 goto :skip_autostart

REM Add to registry startup
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "%APP_NAME%" /t REG_SZ /d "\"%INSTALL_DIR%\%EXE_NAME%\"" /f > nul
echo Auto-start enabled.
goto :done

:skip_autostart
echo Auto-start skipped. Enable later via tray menu.

:done
echo.

REM Ask to launch now
choice /c yn /m "Launch Quick Tasks now?"
if errorlevel 2 goto :end

start "" "%INSTALL_DIR%\%EXE_NAME%"
echo.
echo Quick Tasks is running in your system tray.
echo Press Ctrl+Shift+P to add a task!

:end
echo.
pause
