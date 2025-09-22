#!/bin/bash

# Start FastAPI backend server

set -e

echo "🚀 Starting FastAPI Backend Server"

# Activate virtual environment
source venv/bin/activate

# Load environment variables
export $(cat env/.env | grep -v '^#' | xargs)

# Start uvicorn server
echo "📡 Starting API server on http://0.0.0.0:8001"
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8001
