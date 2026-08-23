#!/bin/bash

# ModelGuardian Startup Script for Linux/Mac

echo "============================================"
echo "🛡️  ModelGuardian - Starting All Services"
echo "============================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Install backend dependencies
echo "[1/5] Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
deactivate
cd ..
echo "✅ Backend dependencies installed"
echo ""

# Install monitor dependencies
echo "[2/5] Installing monitor dependencies..."
cd monitor
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
deactivate
cd ..
echo "✅ Monitor dependencies installed"
echo ""

# Install dashboard dependencies
echo "[3/5] Installing dashboard dependencies..."
cd dashboard
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages... (this may take a few minutes)"
    npm install
fi
cd ..
echo "✅ Dashboard dependencies installed"
echo ""

# Start services
echo "[4/5] Starting services..."
echo ""

# Start Model API
echo "Starting Model API on port 5000..."
cd backend
source venv/bin/activate
python app.py > ../logs/api.log 2>&1 &
API_PID=$!
echo $API_PID > ../pids/api.pid
deactivate
cd ..
sleep 3

# Start Monitor Service
echo "Starting Monitor Service on port 5001..."
cd monitor
source venv/bin/activate
python monitor_service.py > ../logs/monitor.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > ../pids/monitor.pid
deactivate
cd ..
sleep 3

# Start Dashboard
echo "Starting Dashboard on port 3000..."
cd dashboard
npm start > ../logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > ../pids/dashboard.pid
cd ..
sleep 5

echo ""
echo "============================================"
echo "✅ All services started successfully!"
echo "============================================"
echo ""
echo "📊 Services:"
echo "   • Model API:    http://localhost:5000"
echo "   • Monitor:      http://localhost:5001"
echo "   • Dashboard:    http://localhost:3000"
echo ""
echo "[5/5] Generating baseline data..."
sleep 10

# Generate initial baseline
python3 test_client.py --mode baseline
echo ""

echo "🚀 ModelGuardian is ready!"
echo ""
echo "📖 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Run test traffic: python3 test_client.py --mode normal"
echo "   3. Trigger drift: python3 test_client.py --mode drift"
echo ""
echo "To stop all services, run: ./stop.sh"
