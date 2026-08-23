#!/bin/bash

# Automated Rollback Script
# Triggers when drift is detected

echo "🚨 Drift detected! Initiating rollback..."

# Get current model version
CURRENT_VERSION=$(curl -s http://localhost:5000/model/info | python -c "import sys, json; print(json.load(sys.stdin)['version'])")

echo "📊 Current version: $CURRENT_VERSION"

# Determine rollback version
if [ "$CURRENT_VERSION" == "v2" ]; then
    ROLLBACK_VERSION="v1"
else
    ROLLBACK_VERSION="v1"
fi

echo "⏮️  Rolling back to version: $ROLLBACK_VERSION"

# Trigger rollback via API
RESPONSE=$(curl -s -X POST http://localhost:5000/model/reload \
  -H "Content-Type: application/json" \
  -d "{\"version\": \"$ROLLBACK_VERSION\"}")

STATUS=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['status'])")

if [ "$STATUS" == "success" ]; then
    echo "✅ Rollback successful!"
    
    # Regenerate baseline for new version
    echo "📊 Regenerating baseline..."
    curl -s -X POST http://localhost:5000/baseline
    
    # Log rollback event
    echo "[$(date)] Rollback from $CURRENT_VERSION to $ROLLBACK_VERSION" >> rollback.log
    
    exit 0
else
    echo "❌ Rollback failed!"
    exit 1
fi
