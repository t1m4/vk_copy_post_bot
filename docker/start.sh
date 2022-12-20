#!/bin/bash

if [[ $ENVIRONMENT == "local" ]]; then
    # start worker with auto-reloading
    watchfiles "python main.py" .
else
    python main.py
fi
