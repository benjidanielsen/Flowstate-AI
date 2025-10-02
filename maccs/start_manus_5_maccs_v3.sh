#!/bin/bash

REPO_PATH="$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")"

echo "Starting Manus #5 MACCS v3.0 in background..."

# Run the deployment script once to ensure DB is initialized and old data migrated
# This is idempotent, so it's safe to run every time the main loop starts.
python3.11 "$REPO_PATH/maccs/deploy_maccs_v3.py" manus_5 "$REPO_PATH"

# Start the main loop in the background, redirecting output to a log file
nohup python3.11 "$REPO_PATH/maccs/manus_5_main.py" > "$REPO_PATH/maccs/manus_5_maccs_v3.log" 2>&1 &

echo "Manus #5 MACCS v3.0 started. Check log: $REPO_PATH/maccs/manus_5_maccs_v3.log"

