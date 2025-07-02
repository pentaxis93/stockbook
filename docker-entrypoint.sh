#!/bin/bash
set -e

echo "Starting StockBook application..."

# Create necessary directories if they don't exist
mkdir -p /app/data/database /app/data/backups /app/logs

# The FastAPI app will handle database initialization on startup
echo "Starting FastAPI server..."
exec "$@"