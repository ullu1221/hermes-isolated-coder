#!/usr/bin/env bash
set -eo pipefail
cd "$(dirname "$0")"

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
fi

if [ ! -d ".venv" ] && [ ! -f "/.dockerenv" ]; then
  echo "==> Bootstrapping local virtualenv and npm dependencies..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q -r requirements.txt
  npm install --silent
fi

[ -f ".venv/bin/activate" ] && source .venv/bin/activate

TASK="${1:-}"
if [ -z "$TASK" ]; then
  echo "Usage: ./run.sh <task description>"
  exit 1
fi

python3 skills/delegated_coder.py "$TASK"
