#!/usr/bin/env bash
# ===============================================================================
#   INDUSTRIAL SAFETY INTELLIGENCE & INCIDENT ANALYTICS PLATFORM
#   Technical Evaluation Submission for YottaFlex.ai
# ===============================================================================

set -e

echo "==============================================================================="
echo "  INDUSTRIAL SAFETY INTELLIGENCE & INCIDENT ANALYTICS PLATFORM"
echo "  Starting All Services..."
echo "==============================================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed. Please install Python 3.11+."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed. Please install Node.js 18+."
    exit 1
fi

# Setup Virtualenv
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment at ./venv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Verify Database
if [ ! -f "industrial_safety.db" ]; then
    echo "[2/4] Database not found. Running migrations and seeding..."
    alembic -c backend/alembic.ini upgrade head
    python -m generator.generate --seed 20261022 --load-db
else
    echo "[2/4] Database industrial_safety.db verified."
fi

# Trap to kill background processes on exit
cleanup() {
    echo "Stopping services..."
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT

# Start Backend
echo "[3/4] Starting FastAPI backend on http://localhost:8000 ..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Frontend
echo "[4/4] Starting React frontend on http://localhost:5173 ..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run dev -- --host 0.0.0.0 --port 5173 &
cd ..

echo "==============================================================================="
echo "  SERVICES RUNNING!"
echo "  - Frontend UI:     http://localhost:5173"
echo "  - Backend Swagger: http://localhost:8000/docs"
echo "  - Health Check:    http://localhost:8000/api/health"
echo "==============================================================================="
echo "Press Ctrl+C to stop all services."
wait
