#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environment
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# ==================== Backend (Python) ====================
echo "[session-start] Installing backend dependencies..."
cd "$PROJECT_DIR/backend"

# Use existing venv if available, otherwise use system pip
if [ -d "/root/.venv" ]; then
  /root/.venv/bin/pip install -r requirements.txt --quiet 2>/dev/null || true
elif command -v pip3 &>/dev/null; then
  pip3 install -r requirements.txt --quiet 2>/dev/null || true
fi

# Set PYTHONPATH for backend imports
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PYTHONPATH=\"$PROJECT_DIR/backend\"" >> "$CLAUDE_ENV_FILE"
fi

# ==================== Frontend (Node.js) ====================
echo "[session-start] Installing frontend dependencies..."
cd "$PROJECT_DIR/frontend"

# npm install is idempotent and leverages cached node_modules
npm install --prefer-offline --no-audit --no-fund 2>/dev/null || true

echo "[session-start] Dependencies installed successfully."
