#!/bin/bash

echo "[STARTUP] FamilyGuard Python AI Server"

# Create venv if not exist
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "[SETUP] Installing dependencies..."
pip install -q -r requirements.txt

# Run
echo "[RUN] Starting server..."
python3 main.py