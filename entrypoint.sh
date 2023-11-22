#!/bin/sh

echo "waiting for postgres connection"
while ! nc -z db 5432; do
    sleep 0.1
done

echo "running db migrations"
alembic upgrade head

echo "starting the web-api"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --env-file .env.dev

# ‼️ In PRODCTION, use any of the two 👇🏽

# gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
# uvicorn app.main:app  --workers 4 --proxy-headers --host 0.0.0.0 --port 8000 --env-file .env
