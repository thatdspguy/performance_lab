#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# --- PATH augmentation for Windows (Git Bash) ---
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "mingw"* || "$OSTYPE" == "cygwin" ]]; then
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  if [[ -n "$LOCALAPPDATA" ]]; then
    export PATH="$LOCALAPPDATA/Programs/uv:$PATH"
  fi
  if [[ -n "$PROGRAMFILES" ]]; then
    export PATH="$PROGRAMFILES/nodejs:$PATH"
  fi
  if [[ -n "$APPDATA" ]]; then
    export PATH="$APPDATA/npm:$PATH"
  fi
fi

# --- Dependency checks ---
if ! command -v uv &>/dev/null; then
  echo "Error: 'uv' is not installed or not on PATH."
  echo "Install it: https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

if ! command -v npm &>/dev/null; then
  echo "Error: 'npm' is not installed or not on PATH."
  echo "Install Node.js: https://nodejs.org/"
  exit 1
fi

# --- Start Grafana (Docker) ---
if command -v docker &>/dev/null; then
  echo "Starting Grafana (Docker Compose)..."
  cd "$ROOT"
  docker compose up -d 2>&1 | sed 's/^/  /'
else
  echo "Warning: Docker not found. Skipping Grafana. Install Docker to enable dashboards."
fi

# --- Install dependencies ---
echo ""
echo "Installing Python dependencies..."
cd "$ROOT"
uv sync --quiet

echo "Installing frontend dependencies..."
cd "$ROOT/frontend"
npm install --silent

# --- Cleanup on exit ---
cleanup() {
  echo ""
  echo "Shutting down..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  echo "Done."
}
trap cleanup EXIT INT TERM

# --- Start backend ---
echo ""
echo "Starting backend on http://localhost:8001 ..."
cd "$ROOT"
uv run uvicorn backend.main:app --reload --port 8001 &
BACKEND_PID=$!

# --- Start frontend ---
echo "Starting frontend on http://localhost:5173 ..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================================"
echo "  Performance Lab is running"
echo "================================================"
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8001"
echo "  API docs:  http://localhost:8001/docs"
echo "  Grafana:   http://localhost:3000"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

wait
