#!/bin/bash
set -e

echo "[Phantom] ⏳ Activating virtual environment..."
source ./phantom-env/bin/activate

echo "[Phantom] 🔁 Exporting environment variables..."
export PHANTOM_ENV="local"
export AZURE_OPENAI_ENDPOINT="https://your-openai-endpoint.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-azure-api-key"
export AZURE_SEARCH_ENDPOINT="https://your-search-service.search.windows.net"
export AZURE_SEARCH_KEY="your-search-admin-key"
export POSTGRES_URL="postgresql://user:password@localhost:5432/phantom"
export REDIS_URL="redis://localhost:6379"
export PHANTOM_USE_POSTGRES=true
export PHANTOM_ENABLE_LIGHTRAG=true

echo "[Phantom] ✅ Environment ready."

echo "[Phantom] 🚀 Starting FastAPI backend..."
cd backend/app
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

cd ../../frontend
echo "[Phantom] 🌐 Starting Vite frontend..."
npm run dev &

wait $BACKEND_PID
