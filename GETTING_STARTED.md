# 🚀 Getting Started with ModelGuardian

Welcome! This guide will get you from zero to a running system in **5 minutes**.

---

## ⚡ Super Quick Start

**Just run this:**

```bash
# Windows
start.bat

# Mac/Linux
chmod +x start.sh && ./start.sh
```

**Then open:** http://localhost:3000

That's it! The system is now running. 🎉

---

## 📖 What Just Happened?

The startup script:
1. ✅ Checked Python & Node.js are installed
2. ✅ Created virtual environments
3. ✅ Installed all dependencies
4. ✅ Started 3 services:
   - **Model API** (http://localhost:5000)
   - **Monitor Service** (http://localhost:5001)
   - **Dashboard** (http://localhost:3000)
5. ✅ Generated baseline data

---

## 🎮 Try It Out

### 1. Send Some Traffic

```bash
python test_client.py --mode normal --count 50
```

**What you'll see:**
- Terminal shows predictions being made
- Dashboard shows requests coming in
- Charts start filling with data
- Total Inferences counter increases

### 2. Trigger Drift Detection

```bash
python test_client.py --mode drift --count 100
```

**What you'll see:**
- Drift scores climbing on dashboard
- Red alert appears when threshold exceeded
- "DRIFT DETECTED" status
- Automatic rollback kicks in
- Green "Healthy" status returns

**Timeline:**
- 0s: Start sending drift traffic
- 10-15s: Drift detected 🚨
- 30s: Rollback complete ✅

### 3. Test Adversarial Detection

```bash
python test_client.py --mode adversarial --count 20
```

**What you'll see:**
- Warning alerts for suspicious inputs
- Events logged in history panel
- System flags but doesn't rollback

---

## 🎯 What to Look At

### Dashboard Overview

```
┌─────────────────────────────────────────────────┐
│  ModelGuardian                    ● Connected   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Status   │ │ KS Score │ │ KL Div   │       │
│  │ Healthy  │ │  0.0453  │ │ 0.0872   │       │
│  └──────────┘ └──────────┘ └──────────┘       │
│                                                 │
│  📈 Drift Detection Over Time                  │
│  [Line chart showing KS and KL scores]         │
│                                                 │
│  📊 Prediction Distribution                    │
│  [Area chart showing fraud vs legitimate]      │
│                                                 │
│  🚨 Real-time Alerts      📋 Drift Events      │
│  [Alert list]             [Event history]      │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Key Elements:**

1. **Status Card** (top-left)
   - Green = Healthy ✅
   - Red = Drift Detected 🚨

2. **Drift Scores** (top)
   - KS Score: Watch for > 0.15
   - KL Divergence: Watch for > 0.2

3. **Charts** (middle)
   - Updates every 5 seconds
   - Shows last 30 data points

4. **Alerts** (bottom-left)
   - Red = Critical (drift)
   - Yellow = Warning (adversarial)
   - Green = Success (rollback)

5. **Events** (bottom-right)
   - Complete audit log
   - Timestamps and details

---

## 🧪 Test Modes Explained

### Normal Mode
```bash
python test_client.py --mode normal --count 100
```
- Sends legitimate traffic
- Uses baseline distribution
- Should not trigger drift
- **Use for:** Establishing normal behavior

### Drift Mode
```bash
python test_client.py --mode drift --count 100
```
- Sends shifted distribution
- Designed to exceed thresholds
- Triggers automatic rollback
- **Use for:** Testing drift detection

### Adversarial Mode
```bash
python test_client.py --mode adversarial --count 20
```
- Sends extreme/malicious inputs
- Triggers warnings but not rollback
- Tests input validation
- **Use for:** Security testing

### Continuous Mode
```bash
python test_client.py --mode continuous --duration 60
```
- Mixed traffic (80% normal, 15% drift, 5% adversarial)
- Runs for specified duration
- **Use for:** Stress testing

### Baseline Mode
```bash
python test_client.py --mode baseline
```
- Generates reference distribution
- Required before drift detection
- **Use for:** Initial setup or reset

### Health Check
```bash
python test_client.py --mode health
```
- Checks if services are running
- Shows version and status
- **Use for:** Troubleshooting

---

## 🎬 Demo Flow (5 minutes)

**Perfect for showing someone:**

```bash
# 1. Start system (takes 30 seconds)
start.bat

# 2. Open dashboard
# http://localhost:3000

# 3. Generate baseline (takes 10 seconds)
python test_client.py --mode baseline

# 4. Send normal traffic (takes 30 seconds)
python test_client.py --mode normal --count 50

# 5. Trigger drift (takes 60 seconds)
python test_client.py --mode drift --count 100
# Watch dashboard for red alert and auto-rollback!

# 6. Test adversarial detection (takes 20 seconds)
python test_client.py --mode adversarial --count 20
```

**Total time:** ~3 minutes  
**Wow factor:** High! 🚀

---

## 🛑 Stopping the System

```bash
# Windows
stop.bat

# Mac/Linux
./stop.sh
```

This cleanly shuts down all services.

---

## ❓ Quick Troubleshooting

### "Python not found"
**Fix:** Install Python 3.8+ from https://www.python.org/

### "Node not found"
**Fix:** Install Node.js 16+ from https://nodejs.org/

### "Port already in use"
**Fix:** Run `stop.bat` or `./stop.sh` first

### Dashboard shows "Disconnected"
**Fix:** Restart monitor service:
```bash
cd monitor
python monitor_service.py
```

### No drift detected
**Fix:** Make sure you:
1. Generated baseline first
2. Sent at least 30 drift requests
3. Waited 10-15 seconds

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.

---

## 📚 Learn More

**Quick Reference:**
- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - This guide in detail

**Detailed Guides:**
- [SETUP.md](SETUP.md) - Manual installation
- [DEMO.md](DEMO.md) - Full demonstration
- [ARCHITECTURE.md](ARCHITECTURE.md) - How it works

**Reference:**
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - What was built

---

## 🎯 Next Steps

1. **Explore the Dashboard**
   - Click the action buttons
   - Watch real-time updates
   - Check the charts

2. **Try Different Scenarios**
   - Mix of traffic types
   - Different request rates
   - Various drift intensities

3. **Check the Code**
   - `backend/app.py` - Model API
   - `monitor/monitor_service.py` - Drift detection
   - `dashboard/src/App.js` - UI

4. **Customize**
   - Adjust drift thresholds
   - Add new features
   - Integrate with your models

---

## 💡 Key Concepts

### What is Model Drift?
When a model's behavior changes over time, often due to changes in data distribution. Can cause poor predictions and business losses.

### How Does Detection Work?
Uses statistical tests:
- **KS Test:** Compares distributions
- **KL Divergence:** Measures information loss

### What Triggers Rollback?
When either metric exceeds threshold:
- KS statistic > 0.15
- KL divergence > 0.2

### Why Automatic Rollback?
Reduces detection-to-recovery time from hours to seconds, minimizing potential damage.

---

## 🏆 Success Indicators

You'll know it's working when:
- ✅ Dashboard shows "Connected"
- ✅ Status cards show metrics
- ✅ Charts populate with data
- ✅ Drift traffic triggers red alert
- ✅ System auto-recovers to green
- ✅ All under 30 seconds

---

## 🎓 Understanding the Dashboard

### Color Coding

**Green 🟢**
- Status: Healthy
- Meaning: All good!
- Action: None needed

**Yellow 🟡**
- Alert: Warning
- Meaning: Suspicious but not critical
- Action: Monitor

**Red 🔴**
- Status: Drift Detected
- Meaning: Model behavior changed significantly
- Action: Auto-rollback triggered

### Metrics Explained

**KS Score (Kolmogorov-Smirnov)**
- Measures: Distribution difference
- Range: 0 to 1
- Threshold: 0.15
- Higher = More drift

**KL Divergence (Kullback-Leibler)**
- Measures: Information loss
- Range: 0 to ∞
- Threshold: 0.2
- Higher = More drift

**Total Inferences**
- Count of predictions made
- Used for monitoring load
- Should increase steadily

---

## 🚀 Pro Tips

1. **Always generate baseline first**
   ```bash
   python test_client.py --mode baseline
   ```

2. **Watch terminal AND dashboard**
   - Terminal shows detailed logs
   - Dashboard shows visual status

3. **Use continuous mode for demos**
   ```bash
   python test_client.py --mode continuous --duration 120
   ```
   Shows system handling varied traffic

4. **Reset to start fresh**
   - Click "Reset Monitoring" in dashboard
   - Or restart services

5. **Check health if issues**
   ```bash
   python test_client.py --mode health
   ```

---

## 🎉 You're Ready!

You now have a fully functional ML monitoring system with:
- ✅ Real-time drift detection
- ✅ Automated rollback
- ✅ Beautiful dashboard
- ✅ Adversarial detection
- ✅ Complete observability

**Go break something (safely) and watch it auto-fix!** 🛡️

---

**Need help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Want to learn more?** Read [ARCHITECTURE.md](ARCHITECTURE.md)

**Ready to deploy?** See [SETUP.md](SETUP.md#production-deployment)
