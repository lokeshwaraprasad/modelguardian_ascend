@echo off
REM ModelGuardian Stop Script for Windows

echo ============================================
echo 🛑 Stopping ModelGuardian Services
echo ============================================
echo.

REM Stop services by window title
taskkill /FI "WINDOWTITLE eq ModelGuardian API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq ModelGuardian Monitor*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq ModelGuardian Dashboard*" /F >nul 2>&1

REM Also kill by port (fallback)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo ✅ All services stopped
echo.
pause
