#!/usr/bin/env sh

set -e

cd /server

. ./venv/bin/activate

python3 -m uvicorn main:app --reload --host "0.0.0.0" --port 80
