@echo off
echo AutoCAD DWG Translator - Local Test Environment
echo =============================================

echo Checking for existing servers...
netstat -ano | findstr :8002 > nul
if %errorlevel% equ 0 (
    echo Warning: Port 8002 is already in use. Please stop existing server first.
    echo Run: taskkill /F /PID [PID]
    netstat -ano | findstr :8002
    pause
    exit /b 1
)

netstat -ano | findstr :3000 > nul
if %errorlevel% equ 0 (
    echo Warning: Port 3000 is already in use. Please stop existing server first.
    echo Run: taskkill /F /PID [PID]
    netstat -ano | findstr :3000
    pause
    exit /b 1
)

echo Starting backend server...
start "Backend Server" cmd /k "cd /d D:\Users\ymj\Desktop\ZAItry\backend && python debug_app.py"

timeout /t 5 /nobreak

echo Starting frontend server...
start "Frontend Server" cmd /k "cd /d D:\Users\ymj\Desktop\ZAItry\frontend\simple-build && python -m http.server 3000"

timeout /t 3 /nobreak

echo.
echo Servers are starting...
echo Backend: http://localhost:8002
echo Frontend: http://localhost:3000
echo.
echo Testing connectivity...
curl -s http://localhost:8002/health > nul
if %errorlevel% equ 0 (
    echo [OK] Backend server is responding
) else (
    echo [ERROR] Backend server is not responding
)

curl -s -I http://localhost:3000 > nul
if %errorlevel% equ 0 (
    echo [OK] Frontend server is responding
) else (
    echo [ERROR] Frontend server is not responding
)

echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost:3000

echo.
echo ============================================
echo Test Environment Ready!
echo ============================================
echo - Backend: http://localhost:8002
echo - Frontend: http://localhost:3000
echo - API Health: http://localhost:8002/health
echo.
echo Test Files Available:
echo - IEA Plastic Painting Line Layout.dxf (test_files/)
echo.
echo To test:
echo 1. Open http://localhost:3000 in your browser
echo 2. Upload a DWG/DXF file with Chinese text
echo 3. Monitor the translation progress
echo 4. Download the translated file
echo.
echo Note: This version uses enhanced translation service
echo ============================================
echo.
pause