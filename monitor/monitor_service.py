"""
Monitoring Service
Detects drift and triggers rollbacks
"""
import os
import json
import time
import numpy as np
from datetime import datetime, timedelta
from collections import deque
from threading import Thread, Lock
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests
from scipy import stats

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
DRIFT_THRESHOLD_KS = 0.15  # Kolmogorov-Smirnov test threshold
DRIFT_THRESHOLD_KL = 0.2   # KL divergence threshold
WINDOW_SIZE = 100          # Number of recent predictions to analyze
CHECK_INTERVAL = 5         # Seconds between drift checks
ROLLBACK_URL = os.getenv('ROLLBACK_URL', 'http://localhost:5000/model/reload')

# Data storage
inference_logs = deque(maxlen=1000)
baseline_data = {}
drift_events = []
model_health = {
    'status': 'healthy',
    'drift_score_ks': 0.0,
    'drift_score_kl': 0.0,
    'last_check': None,
    'total_inferences': 0,
    'drift_detected': False
}
data_lock = Lock()

# Adversarial detection patterns
ADVERSARIAL_PATTERNS = [
    'DROP TABLE', 'SELECT *', '<script>', 'javascript:',
    '../', 'eval(', 'exec(', '__import__'
]

def calculate_kl_divergence(p, q, epsilon=1e-10):
    """Calculate KL divergence between two distributions"""
    p = np.array(p) + epsilon
    q = np.array(q) + epsilon
    
    # Normalize
    p = p / np.sum(p)
    q = q / np.sum(q)
    
    return np.sum(p * np.log(p / q))

def detect_drift(recent_predictions, baseline_predictions):
    """Detect drift using KS test and KL divergence"""
    if len(recent_predictions) < 30:  # Need minimum samples
        return False, 0.0, 0.0
    
    # Kolmogorov-Smirnov test
    ks_statistic, ks_pvalue = stats.ks_2samp(recent_predictions, baseline_predictions)
    
    # KL divergence (using histograms)
    hist_recent, bins = np.histogram(recent_predictions, bins=20, range=(0, 1), density=True)
    hist_baseline, _ = np.histogram(baseline_predictions, bins=bins, density=True)
    
    kl_div = calculate_kl_divergence(hist_recent, hist_baseline)
    
    # Determine if drift detected
    drift_detected = ks_statistic > DRIFT_THRESHOLD_KS or kl_div > DRIFT_THRESHOLD_KL
    
    return drift_detected, ks_statistic, kl_div

def detect_adversarial_input(features):
    """Simple adversarial input detection"""
    # Convert features to string for pattern matching
    feature_str = str(features)
    
    for pattern in ADVERSARIAL_PATTERNS:
        if pattern.lower() in feature_str.lower():
            return True, pattern
    
    # Check for unusual feature ranges (outside typical bounds)
    features_array = np.array(features)
    if np.any(np.abs(features_array) > 100):  # Abnormal value
        return True, 'extreme_values'
    
    return False, None

def trigger_rollback(drift_score_ks, drift_score_kl):
    """Trigger model rollback"""
    print(f"🚨 DRIFT DETECTED! KS={drift_score_ks:.4f}, KL={drift_score_kl:.4f}")
    
    drift_event = {
        'timestamp': datetime.utcnow().isoformat(),
        'drift_score_ks': float(drift_score_ks),
        'drift_score_kl': float(drift_score_kl),
        'action': 'rollback_triggered',
        'rollback_to': 'v1'
    }
    
    with data_lock:
        drift_events.append(drift_event)
        model_health['drift_detected'] = True
    
    # Broadcast to dashboard
    socketio.emit('drift_alert', drift_event)
    
    # Trigger rollback
    try:
        response = requests.post(
            ROLLBACK_URL,
            json={'version': 'v1'},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Rollback successful")
            drift_event['rollback_status'] = 'success'
            socketio.emit('rollback_complete', {'status': 'success'})
        else:
            print(f"❌ Rollback failed: {response.text}")
            drift_event['rollback_status'] = 'failed'
    except Exception as e:
        print(f"❌ Rollback error: {e}")
        drift_event['rollback_status'] = 'error'

def monitor_loop():
    """Background monitoring loop"""
    while True:
        time.sleep(CHECK_INTERVAL)
        
        if not baseline_data.get('predictions'):
            continue
        
        with data_lock:
            if len(inference_logs) < 30:
                continue
            
            # Get recent predictions
            recent_predictions = [log['probability'] for log in list(inference_logs)[-WINDOW_SIZE:]]
            baseline_predictions = baseline_data['predictions']
            
            # Detect drift
            drift_detected, ks_score, kl_score = detect_drift(recent_predictions, baseline_predictions)
            
            # Update health status
            model_health['drift_score_ks'] = float(ks_score)
            model_health['drift_score_kl'] = float(kl_score)
            model_health['last_check'] = datetime.utcnow().isoformat()
            model_health['total_inferences'] = len(inference_logs)
            
            if drift_detected and not model_health['drift_detected']:
                trigger_rollback(ks_score, kl_score)
            elif not drift_detected:
                model_health['status'] = 'healthy'
                model_health['drift_detected'] = False
        
        # Broadcast current health
        socketio.emit('health_update', model_health)

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'monitor'})

@app.route('/log_inference', methods=['POST'])
def log_inference():
    """Receive inference log from model API"""
    try:
        data = request.get_json()
        
        # Check for adversarial input
        is_adversarial, pattern = detect_adversarial_input(data['features'])
        
        if is_adversarial:
            adversarial_event = {
                'timestamp': data['timestamp'],
                'pattern': pattern,
                'features': data['features'][:3],  # Log only first 3 features
                'type': 'adversarial_input'
            }
            with data_lock:
                drift_events.append(adversarial_event)
            socketio.emit('adversarial_detected', adversarial_event)
            print(f"⚠️  Adversarial input detected: {pattern}")
        
        # Store log
        with data_lock:
            inference_logs.append(data)
        
        return jsonify({'status': 'logged'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/baseline', methods=['POST'])
def set_baseline():
    """Set baseline for drift detection"""
    try:
        data = request.get_json()
        
        with data_lock:
            baseline_data['predictions'] = data['predictions']
            baseline_data['version'] = data['version']
            baseline_data['timestamp'] = data['timestamp']
            
            # Reset drift detection
            model_health['drift_detected'] = False
            model_health['status'] = 'healthy'
        
        print(f"✅ Baseline set: {len(data['predictions'])} samples for version {data['version']}")
        
        return jsonify({
            'status': 'success',
            'baseline_size': len(data['predictions'])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/model_health', methods=['GET'])
def get_model_health():
    """Get current model health status"""
    with data_lock:
        return jsonify(model_health)

@app.route('/drift_events', methods=['GET'])
def get_drift_events():
    """Get drift event history"""
    limit = request.args.get('limit', 50, type=int)
    with data_lock:
        return jsonify(drift_events[-limit:])

@app.route('/inference_logs', methods=['GET'])
def get_inference_logs():
    """Get recent inference logs"""
    limit = request.args.get('limit', 100, type=int)
    with data_lock:
        return jsonify(list(inference_logs)[-limit:])

@app.route('/reset', methods=['POST'])
def reset_monitoring():
    """Reset monitoring state"""
    with data_lock:
        inference_logs.clear()
        drift_events.clear()
        model_health['drift_detected'] = False
        model_health['status'] = 'healthy'
        model_health['drift_score_ks'] = 0.0
        model_health['drift_score_kl'] = 0.0
    
    return jsonify({'status': 'reset'})

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print('📡 Dashboard connected')
    emit('health_update', model_health)

if __name__ == '__main__':
    print("🚀 Starting Monitor Service...")
    
    # Start monitoring thread
    monitor_thread = Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
