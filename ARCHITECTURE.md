# ModelGuardian - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          User / Client                           │
│                     (Test Client / Browser)                      │
└───────────────┬─────────────────────────────────┬───────────────┘
                │                                 │
                │ HTTP                           │ HTTP/WebSocket
                │                                 │
        ┌───────▼────────┐              ┌────────▼──────────┐
        │   Model API    │              │    Dashboard      │
        │  (Port 5000)   │              │   (Port 3000)     │
        │                │              │                   │
        │  - Flask API   │              │  - React SPA      │
        │  - ML Model    │              │  - Real-time UI   │
        │  - Logging     │              │  - Charts         │
        └───────┬────────┘              └────────┬──────────┘
                │                                 │
                │ Inference Logs                  │ Live Updates
                │ (HTTP POST)                     │ (WebSocket)
                │                                 │
        ┌───────▼─────────────────────────────────▼──────────┐
        │          Monitor Service (Port 5001)               │
        │                                                    │
        │  - Drift Detection Engine                         │
        │  - Statistical Analysis (KS, KL)                  │
        │  - Adversarial Detection                          │
        │  - WebSocket Server                               │
        │  - Rollback Trigger                               │
        └───────┬────────────────────────────────────────────┘
                │
                │ Rollback Command
                │ (HTTP POST Webhook)
                │
        ┌───────▼────────┐
        │   Model API    │
        │  Reload Model  │
        └────────────────┘
```

## Component Details

### 1. Model API Service

**Technology Stack:**
- Python 3.9
- Flask 2.3.3
- scikit-learn 1.3.0
- NumPy 1.24.3

**Responsibilities:**
- Serve ML model predictions via REST API
- Log all inference requests and results
- Support multiple model versions
- Handle model reloading for rollback
- Generate baseline data

**Key Endpoints:**
- `GET /health` - Health check
- `POST /predict` - Make prediction
- `POST /baseline` - Generate baseline
- `POST /model/reload` - Reload model version
- `GET /model/info` - Get model metadata

**Data Flow:**
1. Receive prediction request
2. Extract features (10-dimensional vector)
3. Run inference using RandomForest model
4. Calculate prediction probability
5. Log inference data
6. Send log to monitor service (async)
7. Return prediction to client

**Model Versioning:**
- v1: Baseline model (stable)
- v2: Alternative model (for testing drift)
- Stored as pickle files in `models/` directory

### 2. Monitor Service

**Technology Stack:**
- Python 3.9
- Flask 2.3.3
- Flask-SocketIO 5.3.4
- SciPy 1.11.2
- NumPy 1.24.3

**Responsibilities:**
- Receive and store inference logs
- Perform statistical drift detection
- Detect adversarial inputs
- Trigger automated rollbacks
- Broadcast real-time updates to dashboard

**Drift Detection Algorithm:**

```python
# Every 5 seconds:
1. Collect recent predictions (last 100)
2. Load baseline predictions
3. Run Kolmogorov-Smirnov test:
   - Compare cumulative distributions
   - Calculate KS statistic
   - Threshold: 0.15
4. Calculate KL Divergence:
   - Create histograms (20 bins)
   - Compute KL divergence
   - Threshold: 0.2
5. If either threshold exceeded:
   - Log drift event
   - Broadcast alert via WebSocket
   - Trigger rollback webhook
```

**Adversarial Detection:**
- Pattern matching for injection attacks
- Range checking for extreme values
- String analysis for malicious inputs

**Data Structures:**
```python
inference_logs = deque(maxlen=1000)  # Rolling window
baseline_data = {
    'predictions': [...],  # 1000 baseline predictions
    'version': 'v1',
    'timestamp': '...'
}
drift_events = [...]  # Audit trail
model_health = {
    'status': 'healthy',
    'drift_score_ks': 0.0,
    'drift_score_kl': 0.0,
    'drift_detected': False
}
```

### 3. Dashboard

**Technology Stack:**
- React 18.2.0
- Recharts 2.8.0 (charts)
- Socket.IO Client 4.7.2
- Axios 1.5.0
- Lucide React (icons)

**Components:**

```
App
├── Header
│   ├── Logo
│   └── ConnectionStatus
├── StatsGrid
│   ├── ModelStatusCard
│   ├── KSScoreCard
│   ├── KLDivergenceCard
│   └── TotalInferencesCard
├── ChartsGrid
│   ├── DriftChart (LineChart)
│   └── PredictionDistribution (AreaChart)
└── BottomGrid
    ├── AlertsPanel
    ├── DriftEventsHistory
    └── ActionButtons
```

**Real-time Updates:**
- WebSocket connection to monitor service
- Receives health updates every 5 seconds
- Instant drift alerts and rollback notifications
- < 2 second latency requirement

**User Actions:**
- Generate baseline data
- Reset monitoring state
- Refresh dashboard data
- View alert history

### 4. CI/CD Integration

**GitHub Actions Workflow:**
```yaml
Trigger: Push to main branch
Steps:
1. Checkout code
2. Setup Python + Node.js
3. Install dependencies
4. Build Docker images
5. Run tests
6. Deploy containers
7. Health checks
8. Cleanup
```

**Rollback Scripts:**
- `rollback.sh` (Linux/Mac)
- `rollback.bat` (Windows)
- Triggered automatically by monitor service
- Can be invoked manually for testing

## Data Flow Diagrams

### Normal Inference Flow

```
Client
  │
  ├─[POST /predict]─────────────────┐
  │                                  │
  ▼                                  ▼
Model API                      [features: array]
  │                                  │
  ├─[Load Model v1]                 │
  ├─[Run Inference]◄────────────────┘
  │     │
  │     └─[prediction, probability]
  │
  ├─[Log to File]
  │
  ├─[POST /log_inference]───────────┐
  │                                  │
  └─[Return Response]                ▼
                              Monitor Service
                                     │
                                     ├─[Store in deque]
                                     └─[No action needed]
```

### Drift Detection Flow

```
Monitor Service (Background Loop)
  │
  ├─[Every 5 seconds]
  │
  ├─[Collect last 100 predictions]
  │
  ├─[Load baseline data]
  │
  ├─[Run KS Test]
  │    │
  │    └─[ks_statistic = 0.18] ◄─ THRESHOLD EXCEEDED!
  │
  ├─[Calculate KL Divergence]
  │    │
  │    └─[kl_div = 0.23] ◄─ THRESHOLD EXCEEDED!
  │
  ├─[Drift Detected = True]
  │
  ├─[Emit WebSocket Alert]──────────► Dashboard
  │                                      │
  │                                      └─[Show Red Alert]
  │
  ├─[POST /model/reload]────────────► Model API
  │                                      │
  │                                      ├─[Reload v1]
  │                                      ├─[Generate Baseline]
  │                                      └─[Success Response]
  │
  └─[Log Rollback Event]
```

### Adversarial Detection Flow

```
Client sends malicious input
  │
  ├─[features: [999, -999, ...]]
  │
  ▼
Model API
  │
  ├─[Log inference]
  │
  ├─[POST /log_inference]───────────┐
  │                                  │
  └─[Return prediction]              ▼
                              Monitor Service
                                     │
                                     ├─[Check patterns]
                                     │   │
                                     │   └─[Detect: extreme_values]
                                     │
                                     ├─[Log adversarial event]
                                     │
                                     └─[Emit WebSocket Alert]
                                            │
                                            ▼
                                        Dashboard
                                            │
                                            └─[Show Warning Alert]
```

## Deployment Architecture

### Docker Compose Setup

```
┌────────────────────────────────────────────────────┐
│                 Docker Network                     │
│                 (modelguardian)                    │
│                                                    │
│  ┌──────────────────┐      ┌──────────────────┐  │
│  │  model-api       │      │     monitor      │  │
│  │  Container       │◄─────┤    Container     │  │
│  │                  │      │                  │  │
│  │  Port: 5000      │      │  Port: 5001      │  │
│  │  Volume: models/ │      │                  │  │
│  │  Volume: logs/   │      │                  │  │
│  └──────────────────┘      └──────────────────┘  │
│                                                    │
└────────────────────────────────────────────────────┘
         │                            │
         │ Exposed                    │ Exposed
         │ Port 5000                  │ Port 5001
         │                            │
         ▼                            ▼
    Host Machine
         │
         │ Dashboard runs on host (Port 3000)
         ▼
    Browser (User)
```

### Production Deployment (Recommended)

```
┌─────────────────────────────────────────────────┐
│              Load Balancer / Nginx              │
│                    (HTTPS)                      │
└───────────────┬─────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐
│ API 1 │  │ API 2 │  │ API 3 │  (Auto-scaling)
└───┬───┘  └───┬───┘  └───┬───┘
    │          │          │
    └──────────┼──────────┘
               │
        ┌──────▼──────┐
        │   Monitor   │ (Single instance)
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │  Dashboard  │ (Static hosting)
        └─────────────┘
```

## Performance Characteristics

### Latency Breakdown

**Prediction Request:**
- Network: ~5ms
- Model inference: ~10-20ms
- Logging: ~2ms (async)
- Response: ~5ms
- **Total: ~20-30ms** ✅

**Drift Detection:**
- Data collection: ~1ms
- KS test: ~5ms
- KL divergence: ~3ms
- Decision: ~1ms
- **Total: ~10ms every 5 seconds** ✅

**Rollback:**
- Webhook call: ~5ms
- Model reload: ~100-200ms
- Baseline generation: ~2-5s
- **Total: ~5-10 seconds** ✅ (< 30s requirement)

**Dashboard Update:**
- WebSocket latency: ~10ms
- React render: ~50ms
- Chart update: ~100ms
- **Total: ~160ms** ✅ (< 2s requirement)

### Throughput

**Single Instance:**
- Model API: ~100-200 req/s
- Monitor Service: ~500 log writes/s
- Dashboard: Real-time (WebSocket)

**Bottlenecks:**
- Model inference (CPU-bound)
- Statistical calculations (CPU-bound)
- Network I/O (minimal)

**Scaling:**
- Horizontal: Multiple API instances behind load balancer
- Vertical: More CPU for faster inference
- Caching: Redis for baseline data

## Security Considerations

### Current Implementation

**API Security:**
- CORS enabled for development
- Input validation on all endpoints
- Error handling without info leakage

**Adversarial Detection:**
- Pattern matching for common attacks
- Range checking for data anomalies
- Logging of suspicious activity

### Production Hardening

**Recommended:**
1. Add authentication (JWT tokens)
2. Rate limiting per client
3. HTTPS encryption
4. Input sanitization
5. Secret management (environment variables)
6. Network isolation (VPC)
7. Audit logging
8. Anomaly-based intrusion detection

## Monitoring & Observability

### Logs

**Model API:**
- `logs/inference_YYYYMMDD.jsonl` - All predictions
- Console output - Request/response logs

**Monitor Service:**
- Console output - Drift events
- WebSocket broadcasts - Real-time alerts

### Metrics

**Tracked:**
- Total inferences
- Drift scores (KS, KL)
- Rollback events
- Adversarial detections
- Latency measurements

**Exportable to:**
- Prometheus (add exporter)
- CloudWatch (AWS)
- Datadog
- Custom dashboards

## Extensibility

### Adding New Models

```python
# backend/app.py
def create_custom_model(version='v3'):
    # Your model training logic
    model = YourMLModel()
    return model
```

### Custom Drift Metrics

```python
# monitor/monitor_service.py
def custom_drift_metric(recent, baseline):
    # Your statistical test
    score = your_calculation(recent, baseline)
    return score > YOUR_THRESHOLD
```

### Dashboard Customization

```javascript
// dashboard/src/App.js
// Add new components, charts, or metrics
// Recharts library supports many chart types
```

## Testing Strategy

### Unit Tests
- Model prediction logic
- Drift detection algorithms
- API endpoint handlers

### Integration Tests
- End-to-end inference flow
- Drift detection → Rollback
- WebSocket communication

### Load Tests
- 100+ req/min sustained
- Concurrent users
- Memory leak detection

### Manual Testing
- `test_client.py` for scenario testing
- Dashboard interaction testing
- Rollback verification

## Future Enhancements

**Potential Features:**
1. Multi-model comparison
2. A/B testing framework
3. Feature drift detection (input data)
4. Explainability integration (SHAP, LIME)
5. Automated model retraining
6. Slack/email notifications
7. Database persistence (PostgreSQL)
8. Time-series forecasting for drift prediction
9. Canary deployments
10. Blue-green deployment support

---

**Architecture Version:** 1.0.0  
**Last Updated:** August 23, 2026  
**Maintained by:** ModelGuardian Team
