@echo off
echo AutoCAD DWG Translator - Stop Servers
echo =========================================

echo Checking for running servers...

netstat -ano | findstr :8002 > nul
if %errorlevel% equ 0 (
    echo Found backend server on port 8002
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
        echo Stopping backend server (PID: %%a)
        wmic process where "processid=%%a" delete > nul 2>&1
    )
) else (
    echo No backend server found on port 8002
)

netstat -ano | findstr :3000 > nul
if %errorlevel% equ 0 (
    echo Found frontend server on port 3000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        echo Stopping frontend server (PID: %%a)
        wmic process where "processid=%%a" delete > nul 2>&1
    )
) else (
    echo No frontend server found on port 3000
)

timeout /t 2 /nobreak

echo.
echo Checking if servers are stopped...

netstat -ano | findstr :8002 > nul
if %errorlevel% equ 0 (
    echo [ERROR] Backend server is still running
) else (
    echo [OK] Backend server stopped
)

netstat -ano | findstr :3000 > nul
if %errorlevel% equ 0 (
    echo [ERROR] Frontend server is still running
) else (
    echo [OK] Frontend server stopped
)

echo.
echo Server shutdown completed!
echo.
pause