# ModelGuardian - Troubleshooting Guide

This guide covers common issues and their solutions.

---

## Installation Issues

### Problem: "Python not found"

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Install Python 3.8+ from https://www.python.org/
2. During installation, check "Add Python to PATH"
3. Restart terminal/command prompt
4. Verify: `python --version`

**Alternative:**
- Try `python3` instead of `python` on Linux/Mac
- Use `py` on Windows if installed via Microsoft Store

---

### Problem: "Node.js not found"

**Symptoms:**
```
'node' is not recognized as an internal or external command
```

**Solution:**
1. Install Node.js 16+ from https://nodejs.org/
2. Choose LTS (Long Term Support) version
3. Restart terminal
4. Verify: `node --version` and `npm --version`

---

### Problem: pip install fails with "permission denied"

**Symptoms:**
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solution (Windows):**
```cmd
pip install --user -r requirements.txt
```

**Solution (Linux/Mac):**
```bash
pip install --user -r requirements.txt
# OR
sudo pip install -r requirements.txt
```

**Best Practice:**
Use virtual environments (already included in start scripts):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

---

### Problem: npm install fails

**Symptoms:**
```
npm ERR! code EACCES
npm ERR! syscall access
```

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install

# If still fails, update npm
npm install -g npm@latest
```

---

## Service Startup Issues

### Problem: Port already in use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```
or
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution (Windows):**
```cmd
# Find process using the port
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual process ID)
taskkill /F /PID <PID>

# Or use stop script
stop.bat
```

**Solution (Linux/Mac):**
```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9

# For all ports
lsof -ti:5000 | xargs kill -9
lsof -ti:5001 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Or use stop script
./stop.sh
```

---

### Problem: Services start but immediately crash

**Check Logs:**

**Windows:**
```cmd
# Check if services are running
tasklist | findstr python
tasklist | findstr node

# Check error messages in terminal windows
```

**Linux/Mac:**
```bash
# Check logs
tail -f logs/api.log
tail -f logs/monitor.log
tail -f logs/dashboard.log
```

**Common Causes:**
1. Missing dependencies - Run installation again
2. Port conflicts - Stop conflicting services
3. Python/Node version incompatibility - Upgrade to required versions

---

### Problem: "Module not found" error

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Make sure virtual environment is activated
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Connection Issues

### Problem: Dashboard shows "Disconnected"

**Symptoms:**
- Red dot in header
- "Disconnected" status
- No real-time updates

**Solution:**

1. **Check Monitor Service:**
```bash
curl http://localhost:5001/health
```
Expected: `{"status": "healthy", "service": "monitor"}`

2. **Check Browser Console:**
- Open Developer Tools (F12)
- Look for WebSocket errors
- Common error: `WebSocket connection failed`

3. **Fix:**
```bash
# Restart monitor service
cd monitor
python monitor_service.py
```

4. **Firewall Issue:**
- Add exception for ports 5000, 5001, 3000
- Disable firewall temporarily to test

---

### Problem: Dashboard loads but shows no data

**Symptoms:**
- Dashboard displays but charts are empty
- No stats showing

**Solution:**

1. **Check API Connection:**
```bash
curl http://localhost:5000/health
curl http://localhost:5001/model_health
```

2. **Generate Baseline:**
```bash
python test_client.py --mode baseline
```

3. **Send Test Traffic:**
```bash
python test_client.py --mode normal --count 50
```

4. **Check CORS:**
- Ensure CORS is enabled in backend/app.py
- Should have: `CORS(app)`

---

### Problem: CORS errors in browser

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**

1. **Check Service URLs:**
In `dashboard/src/App.js`, verify:
```javascript
const API_URL = 'http://localhost:5000';
const MONITOR_URL = 'http://localhost:5001';
```

2. **Restart Services:**
All services must be running for CORS to work properly.

3. **Browser Cache:**
```
Ctrl + Shift + Delete (Clear cache)
Hard refresh: Ctrl + F5
```

---

## Drift Detection Issues

### Problem: Drift not detected when expected

**Symptoms:**
- Sending drift traffic but no alerts
- Drift scores stay low

**Checklist:**

1. **Baseline Exists:**
```bash
# Generate baseline first
python test_client.py --mode baseline

# Verify baseline created
ls backend/baselines/
# Should see: baseline_v1.json
```

2. **Enough Data:**
- Need minimum 30 predictions for detection
- Send more requests:
```bash
python test_client.py --mode drift --count 100
```

3. **Wait for Detection:**
- Monitor service checks every 5 seconds
- Wait 10-15 seconds after sending drift traffic

4. **Check Thresholds:**
In `monitor/monitor_service.py`:
```python
DRIFT_THRESHOLD_KS = 0.15  # Increase if too sensitive
DRIFT_THRESHOLD_KL = 0.2   # Increase if too sensitive
```

5. **Check Monitor Service:**
```bash
curl http://localhost:5001/model_health
```
Should show drift_score_ks and drift_score_kl values.

---

### Problem: Too many false positive drift alerts

**Symptoms:**
- Drift detected during normal traffic
- Frequent rollbacks

**Solution:**

1. **Increase Thresholds:**
Edit `monitor/monitor_service.py`:
```python
DRIFT_THRESHOLD_KS = 0.20  # Was 0.15
DRIFT_THRESHOLD_KL = 0.25  # Was 0.2
```

2. **Regenerate Baseline:**
```bash
python test_client.py --mode baseline
```
Use more diverse baseline data.

3. **Increase Window Size:**
```python
WINDOW_SIZE = 200  # Was 100
```
Larger window = more stable detection.

---

## Rollback Issues

### Problem: Rollback not triggered

**Symptoms:**
- Drift detected but no rollback
- Alert appears but model not reloaded

**Solution:**

1. **Check Rollback URL:**
In `monitor/monitor_service.py`:
```python
ROLLBACK_URL = 'http://localhost:5000/model/reload'
```

2. **Test Rollback Manually:**
```bash
curl -X POST http://localhost:5000/model/reload \
  -H "Content-Type: application/json" \
  -d '{"version": "v1"}'
```

3. **Check Monitor Logs:**
Look for rollback attempt messages:
```
🚨 DRIFT DETECTED! KS=0.1834, KL=0.2456
✅ Rollback successful
```

---

### Problem: Rollback fails with error

**Symptoms:**
```
❌ Rollback failed: Connection refused
```

**Solution:**

1. **Ensure API is Running:**
```bash
curl http://localhost:5000/health
```

2. **Check Model Files:**
```bash
ls backend/models/
# Should see: fraud_model_v1.pkl
```

3. **Manual Rollback:**
```bash
cd cicd
rollback.bat  # Windows
./rollback.sh  # Linux/Mac
```

---

## Performance Issues

### Problem: High latency (> 100ms per prediction)

**Possible Causes:**

1. **CPU Overload:**
- Check CPU usage
- Close other applications
- Reduce request rate

2. **Too Many Logs:**
- Log files getting large
- Clean up: `rm backend/logs/*.jsonl`

3. **Model Size:**
- Large models take longer
- Consider model optimization

**Benchmark:**
```bash
# Test throughput
python test_client.py --mode continuous --duration 60
# Should show 10+ req/s
```

---

### Problem: Dashboard slow or laggy

**Solutions:**

1. **Reduce Update Frequency:**
In `dashboard/src/App.js`:
```javascript
const interval = setInterval(() => {
    fetchDriftEvents();
    fetchInferenceLogs();
}, 10000);  // Changed from 5000 to 10000 (10 seconds)
```

2. **Limit Data Points:**
```javascript
setDriftHistory(prev => [...prev.slice(-20), newPoint]);
// Reduced from -30 to -20
```

3. **Browser:**
- Close other tabs
- Update browser
- Disable extensions

---

## Testing Issues

### Problem: test_client.py fails

**Symptoms:**
```
ConnectionError: Failed to connect to localhost:5000
```

**Solution:**

1. **Check Services Running:**
```bash
curl http://localhost:5000/health
```

2. **Check Python Dependencies:**
```bash
pip install requests numpy
```

3. **Firewall:**
- Allow Python through firewall
- Try with firewall disabled

---

### Problem: "No baseline data" error

**Symptoms:**
```
Monitor service not detecting drift - no baseline
```

**Solution:**
```bash
# Generate baseline
python test_client.py --mode baseline

# Verify
curl http://localhost:5001/baseline
```

---

## Docker Issues

### Problem: Docker build fails

**Symptoms:**
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**Solution:**

1. **Update Docker:**
- Ensure Docker Desktop is running
- Update to latest version

2. **Clean Build:**
```bash
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
```

3. **Check Dockerfile:**
- Verify paths in Dockerfile
- Ensure requirements.txt exists

---

### Problem: Container exits immediately

**Check Logs:**
```bash
docker-compose logs model-api
docker-compose logs monitor
```

**Common Issues:**
- Port conflicts (5000/5001 already used)
- Missing environment variables
- Incorrect paths in docker-compose.yml

**Solution:**
```bash
# Stop conflicting services
docker-compose down

# Rebuild
docker-compose build

# Start with logs
docker-compose up
```

---

## Database/Storage Issues

### Problem: Out of disk space

**Symptoms:**
```
OSError: [Errno 28] No space left on device
```

**Solution:**

1. **Clean Logs:**
```bash
# Windows
del /Q backend\logs\*.jsonl

# Linux/Mac
rm backend/logs/*.jsonl
```

2. **Clean Models:**
```bash
# Keep only v1, delete others
rm backend/models/fraud_model_v2.pkl
```

3. **Docker Cleanup:**
```bash
docker system prune -a --volumes
```

---

## Common Errors and Fixes

### Error: "ImportError: DLL load failed"

**Windows Issue:**
- Install Visual C++ Redistributable
- https://aka.ms/vs/17/release/vc_redist.x64.exe

### Error: "sqlite3.OperationalError: database is locked"

**Solution:**
- Close any open database connections
- Restart services

### Error: "Permission denied: '/app/models'"

**Docker Volume Issue:**
```bash
# Fix permissions
chmod -R 755 backend/models/
chmod -R 755 backend/logs/
```

### Error: "WebSocket connection to 'ws://localhost:5001/' failed"

**Solution:**
1. Check if monitor service is running
2. Try different browser
3. Check browser console for specific error
4. Restart monitor service with WebSocket debug:
```bash
socketio.run(app, debug=True, log_output=True)
```

---

## Reset Everything

If nothing works, complete reset:

### Windows:
```cmd
# Stop all services
stop.bat

# Delete virtual environments
rmdir /S /Q backend\venv
rmdir /S /Q monitor\venv

# Delete node modules
rmdir /S /Q dashboard\node_modules

# Delete generated files
del /Q backend\models\*.pkl
del /Q backend\logs\*.jsonl
del /Q backend\baselines\*.json

# Start fresh
start.bat
```

### Linux/Mac:
```bash
# Stop all services
./stop.sh

# Clean up
rm -rf backend/venv
rm -rf monitor/venv
rm -rf dashboard/node_modules
rm -rf backend/models/*.pkl
rm -rf backend/logs/*.jsonl
rm -rf backend/baselines/*.json
rm -rf pids/
rm -rf logs/

# Start fresh
./start.sh
```

---

## Getting Help

### Check Documentation
1. README.md - Overview
2. SETUP.md - Detailed setup
3. DEMO.md - Feature demonstration
4. ARCHITECTURE.md - System design

### Debug Mode

**Enable verbose logging:**

Backend (backend/app.py):
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

Monitor (monitor/monitor_service.py):
```python
socketio.run(app, host='0.0.0.0', port=5001, debug=True)
```

### Collect Debug Info

```bash
# System info
python --version
node --version
npm --version

# Service status
curl http://localhost:5000/health
curl http://localhost:5001/health

# Port usage
netstat -ano | findstr :5000  # Windows
lsof -i :5000                  # Linux/Mac

# Process list
tasklist | findstr python      # Windows
ps aux | grep python           # Linux/Mac
```

### Report Issues

If you need to report an issue, include:
1. Operating system and version
2. Python version
3. Node.js version
4. Error messages (full stack trace)
5. Steps to reproduce
6. What you've already tried

---

## Preventive Maintenance

### Regular Cleanup

**Weekly:**
```bash
# Clean old logs
find backend/logs -name "*.jsonl" -mtime +7 -delete

# Docker cleanup
docker system prune -f
```

**Monthly:**
```bash
# Update dependencies
pip install --upgrade -r backend/requirements.txt
pip install --upgrade -r monitor/requirements.txt
npm update --prefix dashboard
```

### Health Checks

Create a health check script (`health_check.sh`):
```bash
#!/bin/bash

echo "Checking ModelGuardian Health..."

curl -f http://localhost:5000/health || echo "❌ API down"
curl -f http://localhost:5001/health || echo "❌ Monitor down"
curl -f http://localhost:3000 || echo "❌ Dashboard down"

echo "✅ Health check complete"
```

---

**Last Updated:** August 23, 2026  
**Version:** 1.0.0
