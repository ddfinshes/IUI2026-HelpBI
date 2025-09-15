#!/bin/zsh
set -euo pipefail
export PYTHONUNBUFFERED=1
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
