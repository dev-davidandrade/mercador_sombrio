#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
printf '\nAcesse http://127.0.0.1:8000\n'
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
