@echo off
REM Automated Rollback Script for Windows
REM Triggers when drift is detected

echo 🚨 Drift detected! Initiating rollback...

REM Get current model version
curl -s http://localhost:5000/model/info > temp_version.json
echo 📊 Checking current version...

REM Trigger rollback to v1
echo ⏮️  Rolling back to version: v1

curl -s -X POST http://localhost:5000/model/reload ^
  -H "Content-Type: application/json" ^
  -d "{\"version\": \"v1\"}" > temp_rollback.json

echo ✅ Rollback command sent!

REM Regenerate baseline
echo 📊 Regenerating baseline...
curl -s -X POST http://localhost:5000/baseline > temp_baseline.json

REM Log rollback event
echo [%date% %time%] Rollback executed >> rollback.log

echo ✅ Rollback complete!

REM Cleanup
del temp_*.json

exit /b 0
