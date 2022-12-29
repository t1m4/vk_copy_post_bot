#!/bin/bash

if [[ $ENVIRONMENT == "local" ]]; then
    # start worker with auto-reloading
    watchfiles "celery --app=src.worker.celery worker --concurrency=1 --loglevel=INFO --beat" .
else
    celery --app src.worker.celery worker --concurrency=1 --loglevel=INFO --beat
fi
