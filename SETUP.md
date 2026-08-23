# ModelGuardian - Complete Setup Guide

## Prerequisites

### Required Software
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Docker** (Optional) - [Download](https://www.docker.com/products/docker-desktop/)

### Check Prerequisites
```bash
python --version   # Should show 3.8+
node --version     # Should show 16+
npm --version      # Should be included with Node.js
```

## Quick Start (Automated)

### Windows
```cmd
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

This will:
1. Install all dependencies
2. Start all services
3. Generate baseline data
4. Open the dashboard in your browser

## Manual Setup

### 1. Backend Setup (Model API)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

The Model API will be available at `http://localhost:5000`

### 2. Monitor Service Setup

```bash
cd monitor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the service
python monitor_service.py
```

The Monitor Service will be available at `http://localhost:5001`

### 3. Dashboard Setup

```bash
cd dashboard

# Install dependencies
npm install

# Start the dashboard
npm start
```

The Dashboard will be available at `http://localhost:3000`

## Docker Setup (Alternative)

### Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Initial Configuration

### 1. Generate Baseline Data

After all services are running, generate baseline data:

```bash
python test_client.py --mode baseline
```

This creates a reference distribution for drift detection.

### 2. Verify System Health

```bash
python test_client.py --mode health
```

Expected output:
```
✅ Model API: healthy
   Version: v1
   Inference count: 0
✅ Monitor Service: healthy
```

## Testing the System

### 1. Send Normal Traffic

```bash
python test_client.py --mode normal --count 100
```

This sends 100 normal prediction requests.

### 2. Trigger Drift Detection

```bash
python test_client.py --mode drift --count 100
```

This sends drifted data that will trigger:
- Drift alert in the dashboard
- Automated rollback
- Baseline regeneration

### 3. Test Adversarial Detection

```bash
python test_client.py --mode adversarial --count 20
```

This sends adversarial inputs with extreme values.

### 4. Continuous Mixed Traffic

```bash
python test_client.py --mode continuous --duration 60
```

Runs mixed traffic (normal + drift + adversarial) for 60 seconds.

## Dashboard Features

### Main Views

1. **Model Status Card**
   - Shows current health status
   - Displays drift detection state
   - Real-time updates via WebSocket

2. **Drift Metrics**
   - KS (Kolmogorov-Smirnov) Test Score
   - KL (Kullback-Leibler) Divergence
   - Thresholds: KS > 0.15, KL > 0.2

3. **Real-time Charts**
   - Drift score over time
   - Prediction distribution
   - Live updates every 5 seconds

4. **Alerts Panel**
   - Drift detection alerts
   - Adversarial input warnings
   - Rollback notifications
   - Color-coded by severity

5. **Event History**
   - Complete audit log
   - Drift events with scores
   - Rollback actions

### Dashboard Actions

- **Generate Baseline**: Create new baseline from current model
- **Reset Monitoring**: Clear all monitoring state
- **Refresh Data**: Manually refresh dashboard data

## API Reference

### Model API (Port 5000)

#### Health Check
```bash
GET /health
```

#### Make Prediction
```bash
POST /predict
Content-Type: application/json

{
  "features": [1.2, -0.5, 0.8, ...],  # 10 features
  "request_id": "optional_id"
}
```

#### Generate Baseline
```bash
POST /baseline
```

#### Reload Model (Rollback)
```bash
POST /model/reload
Content-Type: application/json

{
  "version": "v1"
}
```

### Monitor Service (Port 5001)

#### Get Model Health
```bash
GET /model_health
```

#### Get Drift Events
```bash
GET /drift_events?limit=50
```

#### Get Inference Logs
```bash
GET /inference_logs?limit=100
```

#### Reset Monitoring
```bash
POST /reset
```

## Understanding Drift Detection

### Kolmogorov-Smirnov (KS) Test
- Compares two probability distributions
- Measures maximum difference between cumulative distributions
- Threshold: 0.15
- **Triggers when**: Model output distribution shifts significantly

### Kullback-Leibler (KL) Divergence
- Measures how one distribution differs from another
- Quantifies information loss
- Threshold: 0.2
- **Triggers when**: Model behavior diverges from baseline

### When Drift is Detected
1. Alert is sent to dashboard (< 2s latency)
2. Rollback is triggered automatically (< 30s)
3. Model reverts to version v1
4. New baseline is generated
5. Monitoring continues

## Rollback System

### Automatic Rollback
- Triggered when drift exceeds thresholds
- Uses HTTP webhook to model API
- Reloads previous model version
- Regenerates baseline automatically

### Manual Rollback

Windows:
```cmd
cd cicd
rollback.bat
```

Linux/Mac:
```bash
cd cicd
chmod +x rollback.sh
./rollback.sh
```

## Performance Benchmarks

### Target Metrics
- **Drift Detection Latency**: < 15 seconds ✅
- **Rollback Time**: < 30 seconds ✅
- **Request Throughput**: 100+ req/min ✅
- **Dashboard Update Latency**: < 2 seconds ✅

### Verification
```bash
# Test throughput
python test_client.py --mode continuous --duration 60
# Should show ~600 requests = 10 req/s
```

## Troubleshooting

### Services Won't Start

**Problem**: Port already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

**Problem**: Python packages not installed
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Dashboard Not Loading

**Problem**: CORS errors
- Ensure all services are running
- Check browser console for errors
- Verify API URLs in dashboard code

**Problem**: WebSocket connection failed
- Check if monitor service is running on port 5001
- Verify firewall settings

### Drift Not Detected

**Problem**: Not enough data
- Send at least 30 requests before drift detection
- Wait 5-15 seconds for monitoring loop

**Problem**: Baseline not set
```bash
python test_client.py --mode baseline
```

### Rollback Fails

**Problem**: Model API not responding
- Check API health: `curl http://localhost:5000/health`
- Restart API service

**Problem**: Version not found
- Only v1 and v2 are available by default
- Check models/ directory

## File Structure

```
ModelGuardian/
├── backend/              # ML Model API
│   ├── app.py           # Flask API server
│   ├── requirements.txt
│   ├── models/          # Trained models
│   ├── logs/            # Inference logs
│   └── baselines/       # Baseline data
├── monitor/             # Monitoring Service
│   ├── monitor_service.py  # Drift detection
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/           # React Dashboard
│   ├── src/
│   │   ├── App.js      # Main component
│   │   └── App.css     # Styles
│   ├── public/
│   └── package.json
├── cicd/               # CI/CD Scripts
│   ├── rollback.sh
│   └── rollback.bat
├── test_client.py      # Test client
├── docker-compose.yml  # Docker setup
├── start.bat          # Windows startup
├── start.sh           # Linux/Mac startup
├── stop.bat           # Windows stop
└── stop.sh            # Linux/Mac stop
```

## Advanced Features

### Adding New Model Versions

1. Create model in `backend/app.py`:
```python
def create_fraud_detection_model(version='v3'):
    # Custom model logic
    model = RandomForestClassifier(...)
    return model
```

2. Save model:
```bash
curl -X POST http://localhost:5000/model/reload \
  -H "Content-Type: application/json" \
  -d '{"version": "v3"}'
```

### Custom Drift Thresholds

Edit `monitor/monitor_service.py`:
```python
DRIFT_THRESHOLD_KS = 0.15  # Adjust sensitivity
DRIFT_THRESHOLD_KL = 0.2   # Adjust sensitivity
```

### Adversarial Pattern Detection

Add patterns in `monitor/monitor_service.py`:
```python
ADVERSARIAL_PATTERNS = [
    'DROP TABLE',
    'SELECT *',
    '<script>',
    # Add your patterns
]
```

## CI/CD Integration

### GitHub Actions
The `.github/workflows/deploy.yml` file provides:
- Automated testing
- Docker image building
- Health checks
- Automated deployment

### Webhook Integration
Configure external systems to trigger rollback:
```bash
curl -X POST http://localhost:5000/model/reload \
  -H "Content-Type: application/json" \
  -d '{"version": "v1"}'
```

## Production Deployment

### Recommended Setup
1. Use Docker Compose for orchestration
2. Deploy behind a reverse proxy (nginx)
3. Enable HTTPS with SSL certificates
4. Set up monitoring alerts (email, Slack)
5. Configure log aggregation (ELK stack)
6. Set up database for persistent storage

### Security Considerations
- Add authentication to APIs
- Rate limiting for endpoints
- Input validation and sanitization
- Secure WebSocket connections
- Environment variable management

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review this setup guide
3. Check service health endpoints
4. Restart services with stop/start scripts

## License

MIT License - See LICENSE file for details
