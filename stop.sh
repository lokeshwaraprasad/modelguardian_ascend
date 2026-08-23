#!/bin/bash

# ModelGuardian Stop Script for Linux/Mac

echo "============================================"
echo "🛑 Stopping ModelGuardian Services"
echo "============================================"
echo ""

mkdir -p pids

# Stop services
if [ -f "pids/api.pid" ]; then
    kill $(cat pids/api.pid) 2>/dev/null
    rm pids/api.pid
    echo "✅ Model API stopped"
fi

if [ -f "pids/monitor.pid" ]; then
    kill $(cat pids/monitor.pid) 2>/dev/null
    rm pids/monitor.pid
    echo "✅ Monitor Service stopped"
fi

if [ -f "pids/dashboard.pid" ]; then
    kill $(cat pids/dashboard.pid) 2>/dev/null
    rm pids/dashboard.pid
    echo "✅ Dashboard stopped"
fi

# Fallback: kill by port
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo ""
echo "✅ All services stopped"
