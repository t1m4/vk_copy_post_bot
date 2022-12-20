#/bin/bash

export $(grep -v --regex='^#.*' .env | xargs)
export PYTHONPATH="${PYTHONPATH}:`pwd`"