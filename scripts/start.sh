#!/usr/bin/env bash
set -euo pipefail

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting application..."
exec uv run gunicorn src.main:app \
    -w "${WORKERS:-4}" \
    -k uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${PORT:-8000}" \
    --access-logfile - \
    --error-logfile - \
    --timeout 120 \
    --graceful-timeout 30
