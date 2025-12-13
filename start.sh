#!/bin/bash
set -e

echo "Seeding database with products..."
cd /app
python -m Backend.seed

echo "Starting uvicorn server..."
exec uvicorn Backend.main:app --host 0.0.0.0 --port ${PORT:-10000}
