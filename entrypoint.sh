#!/bin/sh
set -e

RUN_MIGRATION="echo running migrations...;alembic upgrade head"

if [ "$1" = "production" ]
then
    # Assumes the PROD database engine is MySQL 🤭
    eval ${RUN_MIGRATION}

    # ‼️ In PRODCTION, use any of the two 👇🏽
    uvicorn app.main:app  --workers 4 --proxy-headers --host 0.0.0.0 --port 8000 --env-file .env
    # gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
else
    echo "waiting for postgres connection"
    while ! nc -z db 5432; do
        sleep 0.1
    done

    eval ${RUN_MIGRATION}

    echo "starting the web-api"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --env-file .env.dev
fi
