#!/usr/bin/env bash
# Start n8n locally. Ships the two flags that trip everyone up on first run.
set -euo pipefail

PORT="${N8N_PORT:-5678}"

# Without this, n8n refuses to set its login cookie over plain http://localhost
# and you get stuck on a login screen that never logs you in.
export N8N_SECURE_COOKIE=false

# Opt out of telemetry.
export N8N_DIAGNOSTICS_ENABLED=false

# Keep data in ~/.n8n by default; override N8N_USER_FOLDER to sandbox a test run.
export N8N_USER_FOLDER="${N8N_USER_FOLDER:-$HOME/.n8n}"

command -v n8n >/dev/null || { echo "n8n not installed. Run: npm install -g n8n"; exit 1; }

echo "n8n starting on http://localhost:$PORT  (data: $N8N_USER_FOLDER)"
N8N_PORT="$PORT" n8n start
