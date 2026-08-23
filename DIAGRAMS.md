# ModelGuardian - Visual Diagrams

This document contains visual representations of the system architecture and data flows.

---

## 🏗️ System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                     │
│                                                                             │
│  ┌──────────────────┐                    ┌──────────────────────────┐     │
│  │  Test Client     │                    │    Web Browser           │     │
│  │  (Python)        │                    │    (Chrome/Firefox)      │     │
│  │                  │                    │                          │     │
│  │  • Normal Mode   │                    │  • Dashboard UI          │     │
│  │  • Drift Mode    │                    │  • Real-time Charts      │     │
│  │  • Adversarial   │                    │  • Alerts Panel          │     │
│  └────────┬─────────┘                    └─────────┬────────────────┘     │
│           │                                        │                       │
└───────────┼────────────────────────────────────────┼───────────────────────┘
            │                                        │
            │ HTTP POST                              │ HTTP + WebSocket
            │ /predict                               │
            │                                        │
┌───────────▼────────────────────────────────────────▼───────────────────────┐
│                           APPLICATION LAYER                                │
│                                                                             │
│  ┌────────────────────────────────────┐    ┌──────────────────────────┐   │
│  │       Model API Service            │    │     React Dashboard      │   │
│  │       (Flask - Port 5000)          │    │     (Port 3000)          │   │
│  │                                    │    │                          │   │
│  │  ┌──────────────────────────────┐ │    │  ┌────────────────────┐  │   │
│  │  │  REST API Endpoints          │ │    │  │  Components:       │  │   │
│  │  │  • GET  /health              │ │    │  │  • Status Cards    │  │   │
│  │  │  • POST /predict             │ │    │  │  • Drift Charts    │  │   │
│  │  │  • POST /baseline            │ │    │  │  • Alerts Panel    │  │   │
│  │  │  • POST /model/reload        │ │    │  │  • Events History  │  │   │
│  │  │  • GET  /model/info          │ │    │  │  • Action Buttons  │  │   │
│  │  └──────────────────────────────┘ │    │  └────────────────────┘  │   │
│  │                                    │    │                          │   │
│  │  ┌──────────────────────────────┐ │    │  ┌────────────────────┐  │   │
│  │  │  ML Model Engine             │ │    │  │  Real-time Updates │  │   │
│  │  │  • RandomForest Classifier   │ │    │  │  • Socket.IO Client│  │   │
│  │  │  • Feature Processing        │ │    │  │  • Recharts Viz    │  │   │
│  │  │  • Probability Calculation   │ │    │  │  • Axios HTTP      │  │   │
│  │  └──────────────────────────────┘ │    │  └────────────────────┘  │   │
│  │                                    │    │                          │   │
│  │  ┌──────────────────────────────┐ │    └──────────────────────────┘   │
│  │  │  Logging System              │ │                                    │
│  │  │  • JSONL File Logs           │ │                                    │
│  │  │  • Async HTTP to Monitor     │ │                                    │
│  │  └──────────┬───────────────────┘ │                                    │
│  └─────────────┼─────────────────────┘                                    │
│                │                                                           │
│                │ POST /log_inference                                       │
│                │ {timestamp, features, prediction, probability}            │
│                │                                                           │
│  ┌─────────────▼──────────────────────────────────────────────────────┐   │
│  │                  Monitor Service                                    │   │
│  │                  (Flask + SocketIO - Port 5001)                     │   │
│  │                                                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │  Data Collection & Storage                                    │ │   │
│  │  │  • Inference Logs (deque, maxlen=1000)                        │ │   │
│  │  │  • Baseline Data (1000 predictions)                           │ │   │
│  │  │  • Drift Events (audit trail)                                 │ │   │
│  │  │  • Model Health Status                                        │ │   │
│  │  └───────────────────────────────────────────────────────────────┘ │   │
│  │                                                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │  Drift Detection Engine (Background Thread)                   │ │   │
│  │  │  ┌─────────────────────────────────────────────────────────┐  │ │   │
│  │  │  │  Every 5 seconds:                                        │  │ │   │
│  │  │  │  1. Collect last 100 predictions                         │  │ │   │
│  │  │  │  2. Load baseline (1000 predictions)                     │  │ │   │
│  │  │  │  3. Run KS Test (scipy.stats.ks_2samp)                   │  │ │   │
│  │  │  │     • Compare cumulative distributions                   │  │ │   │
│  │  │  │     • Threshold: ks_statistic > 0.15                     │  │ │   │
│  │  │  │  4. Calculate KL Divergence                              │  │ │   │
│  │  │  │     • Create histograms (20 bins)                        │  │ │   │
│  │  │  │     • Compute: Σ p(x) * log(p(x)/q(x))                   │  │ │   │
│  │  │  │     • Threshold: kl_div > 0.2                            │  │ │   │
│  │  │  │  5. Drift Detected if either threshold exceeded          │  │ │   │
│  │  │  │  6. Trigger Rollback + Alert                             │  │ │   │
│  │  │  └─────────────────────────────────────────────────────────┘  │ │   │
│  │  └───────────────────────────────────────────────────────────────┘ │   │
│  │                                                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │  Adversarial Detection                                        │ │   │
│  │  │  • Pattern Matching (SQL injection, XSS, etc.)                │ │   │
│  │  │  • Range Checking (extreme values > 100 or < -100)            │ │   │
│  │  │  • String Analysis                                            │ │   │
│  │  └───────────────────────────────────────────────────────────────┘ │   │
│  │                                                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │  WebSocket Server                                             │ │   │
│  │  │  • Broadcast health_update (every 5s)                         │ │   │
│  │  │  • Emit drift_alert (when detected)                           │ │   │
│  │  │  • Emit adversarial_detected (when found)                     │ │   │
│  │  │  • Emit rollback_complete (after rollback)                    │ │   │
│  │  └───────────────────────────────────────────────────────────────┘ │   │
│  │                                                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │  Rollback Trigger                                             │ │   │
│  │  │  POST http://localhost:5000/model/reload                      │ │   │
│  │  │  {                                                            │ │   │
│  │  │    "version": "v1"                                            │ │   │
│  │  │  }                                                            │ │   │
│  │  └─────────────────────────┬─────────────────────────────────────┘ │   │
│  └────────────────────────────┼───────────────────────────────────────┘   │
│                               │                                           │
└───────────────────────────────┼───────────────────────────────────────────┘
                                │
                                │ HTTP POST /model/reload
                                │
                        ┌───────▼────────┐
                        │  Model API     │
                        │  Reload Model  │
                        │  Version v1    │
                        └────────────────┘


┌────────────────────────────────────────────────────────────────────────────┐
│                            STORAGE LAYER                                    │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐    │
│  │  Model Files     │  │  Inference Logs  │  │  Baseline Data       │    │
│  │  (Pickle)        │  │  (JSONL)         │  │  (JSON)              │    │
│  │                  │  │                  │  │                      │    │
│  │  • v1.pkl        │  │  • inference_*.  │  │  • baseline_v1.json  │    │
│  │  • v2.pkl        │  │    jsonl         │  │  • 1000 predictions  │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT LAYER                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        Docker Compose                                │  │
│  │                                                                      │  │
│  │  ┌──────────────────────┐         ┌──────────────────────┐         │  │
│  │  │  model-api           │         │  monitor             │         │  │
│  │  │  Container           │◄────────┤  Container           │         │  │
│  │  │                      │         │                      │         │  │
│  │  │  Port: 5000          │         │  Port: 5001          │         │  │
│  │  │  Volumes:            │         │                      │         │  │
│  │  │  • ./backend/models  │         │                      │         │  │
│  │  │  • ./backend/logs    │         │                      │         │  │
│  │  └──────────────────────┘         └──────────────────────┘         │  │
│  │                                                                      │  │
│  │                    Network: modelguardian                            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      CI/CD Pipeline                                  │  │
│  │                      (GitHub Actions)                                │  │
│  │                                                                      │  │
│  │  Trigger: Push to main                                               │  │
│  │  Steps:                                                              │  │
│  │  1. ✓ Checkout code                                                  │  │
│  │  2. ✓ Setup Python 3.9 + Node.js 16                                 │  │
│  │  3. ✓ Install dependencies                                           │  │
│  │  4. ✓ Build Docker images                                            │  │
│  │  5. ✓ Run tests                                                      │  │
│  │  6. ✓ Deploy containers                                              │  │
│  │  7. ✓ Health checks                                                  │  │
│  │  8. ✓ Cleanup                                                        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram - Normal Inference

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │
       │ 1. POST /predict
       │    {features: [0.5, -0.3, ...]}
       │
       ▼
┌──────────────────────────────────────────┐
│         Model API (Port 5000)            │
│                                          │
│  2. Validate Input                       │
│     └─ Check feature count (10)          │
│     └─ Reshape to (1, 10)                │
│                                          │
│  3. Run Inference                        │
│     └─ model.predict(features)           │
│     └─ model.predict_proba(features)     │
│     └─ Calculate latency                 │
│                                          │
│  4. Create Log Entry                     │
│     └─ {timestamp, features,             │
│         prediction, probability,         │
│         latency, request_id}             │
│                                          │
│  5. Write to File                        │
│     └─ logs/inference_YYYYMMDD.jsonl     │
│                                          │
│  6. Send to Monitor (async)              │
│     └─ POST /log_inference               │
│        Timeout: 1s                       │
│        Non-blocking                      │
│                                          │
└──────┬───────────────────────────────────┘
       │
       │ 7. Return Response
       │    {
       │      prediction: 0,
       │      probability: {fraud: 0.12, legitimate: 0.88},
       │      model_version: "v1",
       │      latency_ms: 23.45,
       │      request_id: "req_123"
       │    }
       │
       ▼
┌──────────────┐
│   Client     │
└──────────────┘

       Parallel Path (Non-blocking)
       
┌──────────────────────────────────────────┐
│      Monitor Service (Port 5001)         │
│                                          │
│  8. Receive Log Entry                    │
│     └─ POST /log_inference               │
│                                          │
│  9. Adversarial Check                    │
│     └─ Pattern matching                  │
│     └─ Range checking                    │
│     └─ If detected: emit alert           │
│                                          │
│  10. Store in Memory                     │
│      └─ inference_logs.append(data)      │
│      └─ deque with maxlen=1000           │
│                                          │
│  11. Background Thread (every 5s)        │
│      └─ Check if len(logs) >= 30         │
│      └─ Run drift detection              │
│                                          │
└──────────────────────────────────────────┘
```

---

## 🚨 Data Flow Diagram - Drift Detection & Rollback

```
┌────────────────────────────────────────────────────────────┐
│       Monitor Service - Background Thread                  │
│       (Runs every 5 seconds)                               │
└────────────────────────────────────────────────────────────┘
                       │
                       │ 1. Check if enough data
                       │    if len(inference_logs) < 30: skip
                       │
                       ▼
            ┌──────────────────────┐
            │  Data Collection     │
            │                      │
            │  • Get last 100      │
            │    predictions from  │
            │    inference_logs    │
            │                      │
            │  • Load baseline     │
            │    (1000 predictions)│
            └──────────┬───────────┘
                       │
                       │ 2. Statistical Analysis
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼                            ▼
┌────────────────────┐    ┌──────────────────────┐
│   KS Test          │    │  KL Divergence       │
│                    │    │                      │
│  scipy.stats.      │    │  1. Create           │
│  ks_2samp(         │    │     histograms       │
│    recent,         │    │     (20 bins)        │
│    baseline        │    │                      │
│  )                 │    │  2. Normalize        │
│                    │    │                      │
│  Returns:          │    │  3. Calculate:       │
│  • ks_statistic    │    │     Σ p*log(p/q)     │
│  • p_value         │    │                      │
│                    │    │  Returns:            │
│  Threshold:        │    │  • kl_divergence     │
│  ks_stat > 0.15    │    │                      │
│                    │    │  Threshold:          │
│                    │    │  kl_div > 0.2        │
└────────┬───────────┘    └──────────┬───────────┘
         │                           │
         └─────────────┬─────────────┘
                       │
                       │ 3. Evaluate Thresholds
                       │
                       ▼
            ┌──────────────────────┐
            │  Drift Decision      │
            │                      │
            │  if ks_stat > 0.15   │
            │     OR               │
            │     kl_div > 0.2:    │
            │                      │
            │     DRIFT = TRUE     │
            └──────────┬───────────┘
                       │
                       │ If DRIFT == TRUE
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌────────┐   ┌─────────┐   ┌──────────┐
    │ Update │   │ Emit    │   │ Trigger  │
    │ Health │   │ WebSocket│   │ Rollback │
    │ Status │   │ Alert   │   │ Webhook  │
    └────────┘   └────┬────┘   └─────┬────┘
                      │              │
                      │              │ 4. POST /model/reload
                      │              │    {version: "v1"}
                      │              │
                      ▼              ▼
         ┌──────────────────────────────────────┐
         │                                      │
         ▼                                      ▼
┌────────────────┐              ┌────────────────────────┐
│   Dashboard    │              │     Model API          │
│                │              │                        │
│  Receives:     │              │  5. Load Model v1      │
│  drift_alert   │              │     from pickle        │
│                │              │                        │
│  Displays:     │              │  6. Update metadata    │
│  • Red alert   │              │     • version = "v1"   │
│  • KS score    │              │     • loaded_at = now  │
│  • KL score    │              │     • inference_count=0│
│  • Status =    │              │                        │
│    "DRIFT      │              │  7. Return success     │
│     DETECTED"  │              │                        │
└────────┬───────┘              └───────────┬────────────┘
         │                                  │
         │                                  │ 8. POST /baseline
         │                                  │    (auto-triggered)
         │                                  │
         │                                  ▼
         │               ┌──────────────────────────────┐
         │               │  Generate New Baseline       │
         │               │                              │
         │               │  • Create 1000 predictions   │
         │               │  • Save to baseline_v1.json  │
         │               │  • Send to monitor service   │
         │               └──────────┬───────────────────┘
         │                          │
         │                          │ 9. Update Monitor
         │                          │
         │               ┌──────────▼───────────────────┐
         │               │  Monitor Service             │
         │               │                              │
         │               │  • Store new baseline        │
         │               │  • Reset drift_detected=False│
         │               │  • Update health status      │
         │               └──────────┬───────────────────┘
         │                          │
         │                          │ 10. Emit rollback_complete
         │                          │
         │◄─────────────────────────┘
         │
         │ Displays:
         │ • Green alert "Rollback complete"
         │ • Status = "Healthy"
         │ • Drift scores reset
         │
┌────────▼───────┐
│   Dashboard    │
│   (Updated)    │
└────────────────┘

Total Time: ~20-30 seconds from detection to recovery
```

---

## 📊 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         COMPONENT INTERACTIONS                      │
│                                                                     │
│   ┌──────────┐                                                     │
│   │  Client  │                                                     │
│   └────┬─────┘                                                     │
│        │                                                           │
│        │ ① HTTP POST /predict                                     │
│        │                                                           │
│        ▼                                                           │
│   ┌────────────────┐                                              │
│   │   Model API    │───────────② POST /log_inference────────┐    │
│   │   Port 5000    │                                         │    │
│   └────────┬───────┘                                         │    │
│            │                                                  │    │
│            │ ③ Response                                       │    │
│            │                                                  │    │
│            ▼                                                  ▼    │
│   ┌──────────┐                                    ┌──────────────┐│
│   │  Client  │                                    │   Monitor    ││
│   └──────────┘                                    │   Service    ││
│                                                   │   Port 5001  ││
│                                                   └──────┬───────┘│
│                                                          │        │
│               ④ WebSocket: health_update                 │        │
│               ⑤ WebSocket: drift_alert                   │        │
│               ⑥ WebSocket: rollback_complete             │        │
│                           │                              │        │
│                           │                              │        │
│                           ▼                              │        │
│                  ┌──────────────────┐                    │        │
│                  │    Dashboard     │                    │        │
│                  │    Port 3000     │                    │        │
│                  └──────────────────┘                    │        │
│                           │                              │        │
│                           │ ⑦ HTTP GET /drift_events     │        │
│                           │    HTTP GET /inference_logs  │        │
│                           └──────────────────────────────┘        │
│                                                                    │
│                                                                    │
│   When Drift Detected:                                            │
│                                                                    │
│   ┌──────────────┐                                                │
│   │   Monitor    │                                                │
│   │   Service    │                                                │
│   └──────┬───────┘                                                │
│          │                                                         │
│          │ ⑧ POST /model/reload {version: "v1"}                   │
│          │                                                         │
│          ▼                                                         │
│   ┌────────────────┐                                              │
│   │   Model API    │─────────⑨ POST /baseline ──────┐            │
│   │   (Reload)     │                                 │            │
│   └────────────────┘                                 │            │
│                                                      │            │
│                                                      ▼            │
│                                           ┌──────────────┐        │
│                                           │   Monitor    │        │
│                                           │   (Update    │        │
│                                           │   baseline)  │        │
│                                           └──────────────┘        │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Flow Diagram

```
┌────────────────────────────────────────────────────┐
│           Adversarial Input Detection              │
└────────────────────────────────────────────────────┘

     Client Request
          │
          │ POST /predict {features: [999, -999, ...]}
          │
          ▼
     ┌─────────────────┐
     │   Model API     │
     │                 │
     │  1. Accept      │
     │     request     │
     │                 │
     │  2. Process     │
     │     inference   │
     │                 │
     │  3. Log to      │
     │     monitor     │
     └────────┬────────┘
              │
              │ POST /log_inference
              │ {features: [999, -999, ...]}
              │
              ▼
     ┌─────────────────────────────────┐
     │      Monitor Service            │
     │                                 │
     │  4. Receive log entry           │
     │                                 │
     │  5. Run Adversarial Checks:     │
     │                                 │
     │     a) Pattern Matching         │
     │        • Check for:             │
     │          - "DROP TABLE"         │
     │          - "SELECT *"           │
     │          - "<script>"           │
     │          - "javascript:"        │
     │          - "../"                │
     │          - "eval("              │
     │                                 │
     │     b) Range Checking           │
     │        • if any feature > 100   │
     │        • if any feature < -100  │
     │        • Flag: extreme_values   │
     │                                 │
     │  6. If adversarial detected:    │
     │     • Log event                 │
     │     • Emit WebSocket alert      │
     │     • DO NOT trigger rollback   │
     │                                 │
     └────────┬────────────────────────┘
              │
              │ WebSocket: adversarial_detected
              │ {
              │   timestamp: "...",
              │   pattern: "extreme_values",
              │   type: "adversarial_input"
              │ }
              │
              ▼
     ┌─────────────────┐
     │   Dashboard     │
     │                 │
     │  7. Show        │
     │     WARNING     │
     │     alert       │
     │                 │
     │  8. Log in      │
     │     events      │
     │     history     │
     └─────────────────┘
```

---

## ⚡ Performance Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                Performance Optimization Points                  │
└────────────────────────────────────────────────────────────────┘

Request Flow with Timing:

Client
  │
  ├─[0ms] Send POST /predict
  │
  ▼
Model API
  │
  ├─[0-5ms] Network latency
  ├─[2ms] Input validation
  ├─[10-20ms] Model inference (RandomForest)
  ├─[1ms] Probability calculation
  ├─[2ms] Log creation
  ├─[1ms] File write (async)
  │
  ├─[1ms] HTTP to monitor (async, non-blocking, timeout 1s)
  │   └─► Monitor receives (doesn't block API response)
  │
  ├─[0-5ms] Network latency
  │
  └─[23-45ms TOTAL] Return response to client
         ▼
       Client receives result


Monitor Service (Background):
  │
  ├─[Every 5 seconds] Wake up monitoring thread
  │
  ├─[1ms] Collect recent predictions
  ├─[1ms] Load baseline
  ├─[5ms] Run KS test (scipy)
  ├─[3ms] Calculate KL divergence
  ├─[1ms] Evaluate thresholds
  │
  └─[~10ms] Complete drift check
      │
      └─► If drift: Trigger rollback (~5ms webhook)
              │
              └─► Model API reload (~5-10 seconds total)


Dashboard Updates:
  │
  ├─[Every 5 seconds] HTTP GET /drift_events
  ├─[Every 5 seconds] HTTP GET /inference_logs
  │   └─► [50-100ms] Round trip
  │
  ├─[Real-time] WebSocket updates
  │   └─► [10-50ms] Push notification
  │
  └─[50-100ms] React re-render + chart update


Bottlenecks & Optimizations:

✓ Model Inference: CPU-bound (~20ms)
  → Optimization: Use faster model or hardware acceleration

✓ Statistical Tests: CPU-bound (~8ms)
  → Already optimized with NumPy/SciPy

✓ Dashboard Polling: Network-bound (~100ms)
  → Mitigated with WebSocket for critical updates

✓ Rollback: Disk I/O (~5-10s)
  → Acceptable for recovery operation

✓ Log Writing: Disk I/O (~1ms async)
  → Non-blocking, doesn't affect response time
```

---

## 🎯 Deployment Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    Production Deployment                        │
└────────────────────────────────────────────────────────────────┘


Development (Local):
═══════════════════

   ┌─────────────────┐
   │  start.bat      │
   │  or start.sh    │
   └────────┬────────┘
            │
            └──► Starts 3 processes:
                 1. Model API (Python venv)
                 2. Monitor Service (Python venv)
                 3. Dashboard (npm)


Docker (Containerized):
════════════════════════

   ┌─────────────────────────────┐
   │   docker-compose up -d      │
   └──────────────┬──────────────┘
                  │
        ┌─────────┼─────────┐
        │                   │
        ▼                   ▼
   ┌─────────┐       ┌──────────┐
   │ model-  │       │ monitor  │
   │ api     │◄──────┤          │
   │ :5000   │       │ :5001    │
   └────┬────┘       └──────────┘
        │
        │ Volumes:
        ├─► ./backend/models
        ├─► ./backend/logs
        └─► ./backend/baselines


Production (Cloud - Recommended):
═════════════════════════════════

┌──────────────────────────────────────────┐
│         Load Balancer (HTTPS)            │
│         (nginx/ALB/Cloud LB)             │
└─────────────┬────────────────────────────┘
              │
      ┌───────┼───────┐
      │               │
      ▼               ▼
┌──────────┐    ┌──────────┐    Auto-scaling
│ API      │    │ API      │    (3+ instances)
│ Instance │    │ Instance │
│ 1        │    │ 2        │
└────┬─────┘    └────┬─────┘
     │               │
     └───────┬───────┘
             │
             ▼
    ┌─────────────────┐
    │ Monitor Service │  Single instance
    │ (Centralized)   │  (can be HA with leader election)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  PostgreSQL     │  Persistent storage
    │  or MongoDB     │  (replaces in-memory deque)
    └─────────────────┘
             │
             ▼
    ┌─────────────────┐
    │  S3 / Blob      │  Model storage
    │  Storage        │  Log archival
    └─────────────────┘


    Dashboard served from:
    ┌─────────────────┐
    │  CDN (CloudFront│  Static hosting
    │  Netlify, etc.) │  Fast global delivery
    └─────────────────┘
```

---

## 📈 Metrics & Monitoring Flow

```
┌────────────────────────────────────────────────────────┐
│              Observability Architecture                 │
└────────────────────────────────────────────────────────┘

┌──────────────┐
│ Model API    │
└──────┬───────┘
       │
       ├─► Metrics:
       │   • Request count
       │   • Latency (p50, p95, p99)
       │   • Error rate
       │   • Model version
       │   • Prediction distribution
       │
       ├─► Logs:
       │   • Inference logs (JSONL)
       │   • Error logs
       │   • Access logs
       │
       └─► Traces:
           • Request ID
           • Full request path
           • Timing breakdown

┌──────────────┐
│ Monitor      │
└──────┬───────┘
       │
       ├─► Metrics:
       │   • Drift scores (KS, KL)
       │   • Baseline staleness
       │   • Rollback count
       │   • Adversarial detection rate
       │   • Alert frequency
       │
       ├─► Logs:
       │   • Drift events
       │   • Rollback events
       │   • Adversarial detections
       │
       └─► Alerts:
           • Drift detected
           • Rollback triggered
           • Rollback failed

┌──────────────┐
│ Dashboard    │
└──────┬───────┘
       │
       └─► Metrics:
           • Page load time
           • WebSocket connection uptime
           • User interactions
           • Chart render time


All metrics can be exported to:

┌─────────────────┐
│  Prometheus     │  Metrics collection
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Grafana        │  Visualization
└─────────────────┘

Or cloud native:
┌─────────────────┐
│  CloudWatch     │  AWS
│  Azure Monitor  │  Azure
│  Cloud Logging  │  GCP
└─────────────────┘
```

---

## 🔄 State Machine Diagram - Model Health

```
┌────────────────────────────────────────────────────────┐
│          Model Health State Machine                     │
└────────────────────────────────────────────────────────┘

                    ┌──────────────┐
              ┌────▶│  STARTING    │
              │     └──────┬───────┘
              │            │
              │            │ Model loaded
              │            │ Baseline exists
              │            │
              │            ▼
              │     ┌──────────────┐
              │     │   HEALTHY    │◄──────────────┐
              │     │              │               │
              │     │ • Drift = 0  │               │
              │     │ • Status 🟢  │               │
              │     └──────┬───────┘               │
              │            │                       │
              │            │ Drift detected        │
              │            │ (KS > 0.15 OR         │
              │            │  KL > 0.2)            │
              │            │                       │
              │            ▼                       │
              │     ┌──────────────┐              │
              │     │  DEGRADED    │              │
              │     │              │              │
              │     │ • Drift 🚨   │              │
              │     │ • Status 🔴  │              │
              │     └──────┬───────┘              │
              │            │                       │
              │            │ Rollback triggered    │
              │            │                       │
              │            ▼                       │
              │     ┌──────────────┐              │
              │     │  RECOVERING  │              │
              │     │              │              │
              │     │ • Reloading  │              │
              │     │ • Status 🟡  │              │
              │     └──────┬───────┘              │
              │            │                       │
              │            │ Rollback success      │
              │            │ Baseline regenerated  │
              │            │                       │
              │            └───────────────────────┘
              │
              │ Rollback failed
              │
              ▼
       ┌──────────────┐
       │    FAILED    │
       │              │
       │ • Manual     │
       │   Required   │
       │ • Status 🔴  │
       └──────────────┘
              │
              │ Manual intervention
              │ Restart
              │
              └──────┘


State Transitions:

STARTING → HEALTHY
  • Condition: Model loaded, baseline exists
  • Duration: ~10 seconds

HEALTHY → DEGRADED
  • Condition: Drift detected
  • Duration: 10-15 seconds (detection time)
  • Trigger: Automatic

DEGRADED → RECOVERING
  • Condition: Rollback triggered
  • Duration: < 1 second
  • Trigger: Automatic

RECOVERING → HEALTHY
  • Condition: Rollback complete + baseline regenerated
  • Duration: 20-30 seconds
  • Trigger: Automatic

RECOVERING → FAILED
  • Condition: Rollback fails
  • Duration: 30 seconds (timeout)
  • Trigger: Error

FAILED → STARTING
  • Condition: Manual restart
  • Duration: Variable
  • Trigger: Manual
```

---

**Diagrams Version:** 1.0.0  
**Last Updated:** August 23, 2026  
**Tools Used:** ASCII Art for universal compatibility
