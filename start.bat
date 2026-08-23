@echo off
REM ModelGuardian Startup Script for Windows

echo ============================================
echo 🛡️  ModelGuardian - Starting All Services
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Install backend dependencies
echo [1/5] Installing backend dependencies...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
cd ..
echo ✅ Backend dependencies installed
echo.

REM Install monitor dependencies
echo [2/5] Installing monitor dependencies...
cd monitor
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
cd ..
echo ✅ Monitor dependencies installed
echo.

REM Install dashboard dependencies
echo [3/5] Installing dashboard dependencies...
cd dashboard
if not exist "node_modules" (
    echo Installing npm packages... (this may take a few minutes)
    call npm install
)
cd ..
echo ✅ Dashboard dependencies installed
echo.

REM Start services
echo [4/5] Starting services...
echo.

REM Start Model API
echo Starting Model API on port 5000...
start "ModelGuardian API" cmd /k "cd backend && venv\Scripts\activate.bat && python app.py"
timeout /t 3 >nul

REM Start Monitor Service
echo Starting Monitor Service on port 5001...
start "ModelGuardian Monitor" cmd /k "cd monitor && venv\Scripts\activate.bat && python monitor_service.py"
timeout /t 3 >nul

REM Start Dashboard
echo Starting Dashboard on port 3000...
start "ModelGuardian Dashboard" cmd /k "cd dashboard && npm start"
timeout /t 5 >nul

echo.
echo ============================================
echo ✅ All services started successfully!
echo ============================================
echo.
echo 📊 Services:
echo   • Model API:    http://localhost:5000
echo   • Monitor:      http://localhost:5001
echo   • Dashboard:    http://localhost:3000
echo.
echo [5/5] Generating baseline data...
timeout /t 10 >nul

REM Generate initial baseline
python test_client.py --mode baseline
echo.

echo 🚀 ModelGuardian is ready!
echo.
echo 📖 Next steps:
echo   1. Open http://localhost:3000 in your browser
echo   2. Run test traffic: python test_client.py --mode normal
echo   3. Trigger drift: python test_client.py --mode drift
echo.
echo Press any key to exit this window (services will continue running)
pause >nul
