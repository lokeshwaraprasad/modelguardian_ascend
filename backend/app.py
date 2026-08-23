"""
ML Model API Service
Serves fraud detection model with inference logging
"""
import os
import json
import time
import numpy as np
import pickle
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

app = Flask(__name__)
CORS(app)

# Configuration
MODEL_VERSION = os.getenv('MODEL_VERSION', 'v1')
MONITOR_SERVICE_URL = os.getenv('MONITOR_SERVICE_URL', 'http://localhost:5001')
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Global model storage
current_model = None
model_metadata = {
    'version': MODEL_VERSION,
    'loaded_at': None,
    'inference_count': 0
}

def create_fraud_detection_model(version='v1'):
    """Create a fraud detection model"""
    # Generate training data
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_classes=2,
        random_state=42 if version == 'v1' else 100  # Different seed for v2
    )
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X, y)
    
    return model

def load_model(version='v1'):
    """Load or create model"""
    global current_model, model_metadata
    
    model_path = f'models/fraud_model_{version}.pkl'
    os.makedirs('models', exist_ok=True)
    
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            current_model = pickle.load(f)
    else:
        current_model = create_fraud_detection_model(version)
        with open(model_path, 'wb') as f:
            pickle.dump(current_model, f)
    
    model_metadata['version'] = version
    model_metadata['loaded_at'] = datetime.utcnow().isoformat()
    model_metadata['inference_count'] = 0
    
    print(f"✅ Model {version} loaded successfully")

def log_inference(request_data, prediction, probability, latency):
    """Log inference data to monitoring service"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'model_version': model_metadata['version'],
        'features': request_data.get('features', []),
        'prediction': int(prediction),
        'probability': float(probability),
        'latency_ms': latency,
        'request_id': request_data.get('request_id', str(time.time()))
    }
    
    # Write to local log
    log_file = os.path.join(LOG_DIR, f"inference_{datetime.utcnow().strftime('%Y%m%d')}.jsonl")
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Send to monitor service (non-blocking)
    try:
        requests.post(
            f'{MONITOR_SERVICE_URL}/log_inference',
            json=log_entry,
            timeout=1
        )
    except Exception as e:
        print(f"⚠️  Failed to send log to monitor: {e}")
    
    return log_entry

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_version': model_metadata['version'],
        'loaded_at': model_metadata['loaded_at'],
        'inference_count': model_metadata['inference_count']
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Inference endpoint"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        # Validate input
        if 'features' not in data:
            return jsonify({'error': 'Missing features'}), 400
        
        features = np.array(data['features']).reshape(1, -1)
        
        # Check feature dimension
        if features.shape[1] != 10:
            return jsonify({'error': f'Expected 10 features, got {features.shape[1]}'}), 400
        
        # Make prediction
        prediction = current_model.predict(features)[0]
        probability = current_model.predict_proba(features)[0]
        
        # Calculate latency
        latency = (time.time() - start_time) * 1000
        
        # Log inference
        log_entry = log_inference(data, prediction, probability[1], latency)
        
        # Update counter
        model_metadata['inference_count'] += 1
        
        return jsonify({
            'prediction': int(prediction),
            'probability': {
                'fraud': float(probability[1]),
                'legitimate': float(probability[0])
            },
            'model_version': model_metadata['version'],
            'latency_ms': latency,
            'request_id': log_entry['request_id']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify(model_metadata)

@app.route('/model/reload', methods=['POST'])
def reload_model():
    """Reload model (for rollback)"""
    data = request.get_json()
    version = data.get('version', 'v1')
    
    try:
        load_model(version)
        return jsonify({
            'status': 'success',
            'message': f'Model reloaded to version {version}',
            'metadata': model_metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/baseline', methods=['POST'])
def generate_baseline():
    """Generate baseline predictions for drift detection"""
    try:
        # Generate baseline data
        X_baseline, _ = make_classification(
            n_samples=1000,
            n_features=10,
            n_informative=8,
            n_redundant=2,
            n_classes=2,
            random_state=42
        )
        
        predictions = current_model.predict_proba(X_baseline)[:, 1]
        
        baseline_data = {
            'version': model_metadata['version'],
            'timestamp': datetime.utcnow().isoformat(),
            'predictions': predictions.tolist(),
            'features': X_baseline.tolist()
        }
        
        # Save baseline
        os.makedirs('baselines', exist_ok=True)
        with open(f'baselines/baseline_{model_metadata["version"]}.json', 'w') as f:
            json.dump(baseline_data, f)
        
        # Send to monitor service
        requests.post(
            f'{MONITOR_SERVICE_URL}/baseline',
            json=baseline_data,
            timeout=5
        )
        
        return jsonify({
            'status': 'success',
            'baseline_size': len(predictions),
            'version': model_metadata['version']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting ML Model API Service...")
    load_model(MODEL_VERSION)
    app.run(host='0.0.0.0', port=5000, debug=False)
