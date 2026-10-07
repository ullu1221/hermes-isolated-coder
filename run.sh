#!/usr/bin/env bash
set -eo pipefail
cd "$(dirname "$0")"

[ -f .env ] && set -a && source .env && set +a

if [ ! -d ".venv" ]; then
  echo "==> Bootstrapping virtualenv and dependencies..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q -r requirements.txt
  echo "==> Virtualenv ready."
fi

source .venv/bin/activate

TASK="${1:-}"
if [ -z "$TASK" ]; then
  echo "Usage: ./run.sh <task description>"
  exit 1
fi

python3 skills/delegated_coder.py "$TASK"
