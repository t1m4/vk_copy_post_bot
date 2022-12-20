#!/bin/bash

mypy src main.py
black src tests main.py --check
flake8 src tests main.py
isort src tests main.py --check-only
autoflake --remove-all-unused-imports --recursive --check  src tests main.py | grep 'Unused imports/variables detected'
