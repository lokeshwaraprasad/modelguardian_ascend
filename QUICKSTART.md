# ModelGuardian - Quick Start Guide

Get ModelGuardian running in 5 minutes!

## 🚀 One-Command Start

### Windows
```cmd
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

That's it! The script will:
1. ✅ Check prerequisites
2. ✅ Install all dependencies
3. ✅ Start all services
4. ✅ Generate baseline
5. ✅ Open dashboard at http://localhost:3000

## 📊 Test It Out

### 1. Send Normal Traffic
```bash
python test_client.py --mode normal --count 50
```

### 2. Trigger Drift Alert
```bash
python test_client.py --mode drift --count 100
```

Watch the dashboard - you'll see:
- 🚨 Drift alert appears
- 📈 Drift scores rise above thresholds
- ✅ Automatic rollback in < 30 seconds

### 3. Test Adversarial Detection
```bash
python test_client.py --mode adversarial --count 20
```

## 🎯 What You'll See

**Dashboard (http://localhost:3000)**
- Real-time model health status
- Drift detection charts
- Live alerts and notifications
- Prediction distribution graphs

**Model API (http://localhost:5000)**
- Fraud detection predictions
- Model version management
- Health checks

**Monitor Service (http://localhost:5001)**
- Drift detection engine
- Rollback triggers
- Event logging

## 🛑 Stop Services

### Windows
```cmd
stop.bat
```

### Linux/Mac
```bash
./stop.sh
```

## 📖 Next Steps

- Read [SETUP.md](SETUP.md) for detailed configuration
- Read [DEMO.md](DEMO.md) for full feature demonstration
- Check [README.md](README.md) for architecture overview

## ❓ Troubleshooting

**Port already in use?**
```bash
# Run stop script first
stop.bat  # or ./stop.sh
```

**Services won't start?**
- Ensure Python 3.8+ and Node.js 16+ are installed
- Check if ports 5000, 5001, 3000 are available

**Dashboard not loading?**
- Wait 10-15 seconds for services to fully start
- Check if all services are running
- Try refreshing the browser

## ✅ System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **RAM**: 2GB minimum
- **Disk**: 500MB for dependencies

## 🎓 Learn More

**Key Concepts:**
- **Drift Detection**: Statistical analysis of model behavior changes
- **KS Test**: Measures distribution differences
- **KL Divergence**: Quantifies information loss
- **Automatic Rollback**: Returns to stable model version

**Performance Targets:**
- Drift Detection: < 15 seconds ✅
- Rollback Time: < 30 seconds ✅
- Throughput: 100+ requests/min ✅
- Dashboard Updates: < 2 seconds ✅

Enjoy using ModelGuardian! 🛡️
