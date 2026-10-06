#!/bin/sh

set -e

echo "Starting LogSight worker..."

python -m app.workers.consumer &

echo "Starting LogSight API..."

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"