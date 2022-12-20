#!/bin/bash

mypy src main.py
black src tests main.py
flake8 src tests main.py
autoflake --remove-all-unused-imports --recursive --in-place src tests main.py
isort src tests main.py
