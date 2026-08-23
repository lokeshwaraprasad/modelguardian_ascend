"""
Test client for ModelGuardian
Simulates normal traffic, drift, and adversarial inputs
"""
import requests
import numpy as np
import time
import argparse
from datetime import datetime

API_URL = 'http://localhost:5000'

def generate_normal_features():
    """Generate normal feature distribution"""
    return np.random.randn(10).tolist()

def generate_drifted_features():
    """Generate drifted feature distribution"""
    # Shift mean and increase variance to simulate drift
    return (np.random.randn(10) * 2 + 1.5).tolist()

def generate_adversarial_features():
    """Generate adversarial/extreme features"""
    features = np.random.randn(10).tolist()
    # Inject extreme values
    features[0] = 999.0
    features[1] = -999.0
    return features

def send_request(features, request_id=None):
    """Send prediction request"""
    payload = {
        'features': features,
        'request_id': request_id or f'req_{int(time.time() * 1000)}'
    }
    
    try:
        response = requests.post(f'{API_URL}/predict', json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Prediction: {data['prediction']} "
                  f"(Fraud prob: {data['probability']['fraud']:.4f}) "
                  f"- Latency: {data['latency_ms']:.2f}ms")
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def run_normal_traffic(count=100, delay=0.1):
    """Send normal traffic"""
    print(f"\n🚀 Sending {count} normal requests...\n")
    
    for i in range(count):
        features = generate_normal_features()
        send_request(features, f'normal_{i}')
        time.sleep(delay)
    
    print(f"\n✅ Completed {count} normal requests\n")

def run_drift_traffic(count=100, delay=0.1):
    """Send drifted traffic to trigger drift detection"""
    print(f"\n⚠️  Sending {count} DRIFTED requests to trigger alerts...\n")
    
    for i in range(count):
        features = generate_drifted_features()
        send_request(features, f'drift_{i}')
        time.sleep(delay)
    
    print(f"\n⚠️  Completed {count} drifted requests - Check dashboard for drift alert!\n")

def run_adversarial_traffic(count=20, delay=0.5):
    """Send adversarial inputs"""
    print(f"\n🔴 Sending {count} ADVERSARIAL requests...\n")
    
    for i in range(count):
        features = generate_adversarial_features()
        send_request(features, f'adversarial_{i}')
        time.sleep(delay)
    
    print(f"\n🔴 Completed {count} adversarial requests\n")

def generate_baseline():
    """Generate baseline for drift detection"""
    print("\n📊 Generating baseline data...\n")
    
    try:
        response = requests.post(f'{API_URL}/baseline', timeout=10)
        
        if response.status_code == 200:
            print("✅ Baseline generated successfully!")
            print(f"   Details: {response.json()}")
        else:
            print(f"❌ Failed to generate baseline: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_continuous_traffic(duration=60):
    """Run continuous mixed traffic"""
    print(f"\n🔄 Running continuous traffic for {duration} seconds...\n")
    
    start_time = time.time()
    request_count = 0
    
    while time.time() - start_time < duration:
        # 80% normal, 15% drifted, 5% adversarial
        rand = np.random.random()
        
        if rand < 0.80:
            features = generate_normal_features()
            req_type = 'normal'
        elif rand < 0.95:
            features = generate_drifted_features()
            req_type = 'drift'
        else:
            features = generate_adversarial_features()
            req_type = 'adversarial'
        
        send_request(features, f'{req_type}_{request_count}')
        request_count += 1
        time.sleep(0.1)
    
    print(f"\n✅ Completed {request_count} requests in {duration}s "
          f"({request_count/duration:.1f} req/s)\n")

def check_health():
    """Check API health"""
    print("\n🏥 Checking system health...\n")
    
    try:
        # Check model API
        response = requests.get(f'{API_URL}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model API: {data['status']}")
            print(f"   Version: {data['model_version']}")
            print(f"   Inference count: {data['inference_count']}")
        else:
            print(f"❌ Model API: Not responding")
        
        # Check monitor service
        monitor_response = requests.get('http://localhost:5001/health', timeout=5)
        if monitor_response.status_code == 200:
            print(f"✅ Monitor Service: healthy")
        else:
            print(f"❌ Monitor Service: Not responding")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='ModelGuardian Test Client')
    parser.add_argument('--mode', type=str, default='normal',
                       choices=['normal', 'drift', 'adversarial', 'continuous', 'baseline', 'health'],
                       help='Test mode')
    parser.add_argument('--count', type=int, default=100,
                       help='Number of requests to send')
    parser.add_argument('--delay', type=float, default=0.1,
                       help='Delay between requests (seconds)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration for continuous mode (seconds)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🛡️  ModelGuardian Test Client")
    print("="*60)
    
    if args.mode == 'health':
        check_health()
    elif args.mode == 'baseline':
        generate_baseline()
    elif args.mode == 'normal':
        run_normal_traffic(args.count, args.delay)
    elif args.mode == 'drift':
        run_drift_traffic(args.count, args.delay)
    elif args.mode == 'adversarial':
        run_adversarial_traffic(args.count, args.delay)
    elif args.mode == 'continuous':
        run_continuous_traffic(args.duration)
    
    print("="*60)
    print("✅ Test completed!")
    print("="*60)

if __name__ == '__main__':
    main()
