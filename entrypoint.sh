#!/bin/sh

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting the Python application..."
exec uvicorn server:app --host 0.0.0.0 --port 8036