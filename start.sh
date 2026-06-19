#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== WorkOrders Agent ==="
echo ""

# Kill any previous instance
lsof -t -i:8000 | xargs kill -9 2>/dev/null || true

echo "Iniciando backend (FastAPI) en http://localhost:8000 ..."
cd "$ROOT/backend"
python3 -m uvicorn main:app --port 8000 --log-level info &
BACKEND_PID=$!

sleep 2s

echo "Iniciando frontend (Vue) en http://localhost:5173 ..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Aplicacion lista:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo ""
echo "Presiona Ctrl+C para detener."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
