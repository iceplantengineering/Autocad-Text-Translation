@echo off
echo AutoCAD DWG Translator - Local Test Environment
echo =============================================

echo Starting backend server...
start "Backend Server" cmd /k "cd /d D:\Users\ymj\Desktop\ZAItry\backend && python simple_app.py"

timeout /t 3 /nobreak

echo Starting frontend server...
start "Frontend Server" cmd /k "cd /d D:\Users\ymj\Desktop\ZAItry\frontend\simple-build && python -m http.server 3000"

echo.
echo Servers are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost:3000

echo.
echo Test Environment Ready!
echo - Backend: http://localhost:8001
echo - Frontend: http://localhost:3000
echo - API Health: http://localhost:8001/health
echo.
echo To test:
echo 1. Open http://localhost:3000 in your browser
echo 2. Upload a DWG file with Chinese text
echo 3. Monitor the translation progress
echo 4. Download the translated file
echo.
echo Note: This is a test version with mock translation service