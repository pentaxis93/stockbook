#!/bin/bash
set -e

echo "Starting StockBook application..."

# Create necessary directories if they don't exist
mkdir -p /app/data/database /app/data/backups /app/logs

# Check if database exists, if not initialize it
if [ ! -f "$DATABASE_PATH" ]; then
    echo "Database not found. Initializing database..."
    python -c "import os; from src.infrastructure.persistence.database_connection import DatabaseConnection; db = DatabaseConnection(os.environ['DATABASE_PATH']); db.initialize_schema()"
    echo "Database initialized successfully."
fi

# Run any pending migrations (placeholder for future use)
# python -m src.infrastructure.database.migrations

echo "Starting FastAPI server..."
exec "$@"