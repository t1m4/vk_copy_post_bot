#!/bin/bash

if [[ $ENVIRONMENT == "local" ]]; then
    # start worker with auto-reloading
    watchfiles "celery --app=src.worker.celery worker --loglevel=INFO --beat" .
else
    celery --app src.worker.celery worker --loglevel=INFO --beat
fi
