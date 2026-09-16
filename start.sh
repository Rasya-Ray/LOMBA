#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "Starting FamilyGuard AI..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

echo "Starting FastAPI..."

python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000