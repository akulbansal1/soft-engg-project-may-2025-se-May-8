#!/bin/bash

# Railway deployment script
# echo "Running database migrations..."
# alembic upgrade head

echo "Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
