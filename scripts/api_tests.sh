#!/usr/bin/env bash
# Run every step that calls the Claude API, and keep a log.
# Needs ANTHROPIC_API_KEY in .env. Usage:  bash scripts/api_tests.sh [piece ...]
set -uo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
source .venv/bin/activate
mkdir -p eval
LOG="eval/api_run_$(date +%Y%m%d_%H%M%S).log"
PIECES=("$@")
if [ ${#PIECES[@]} -eq 0 ]; then
  PIECES=($(ls pieces))
fi
echo "Writing log to $LOG"
{
  echo "== API run $(date) =="
  echo "== live API test (about 1 minute, no output until it ends) =="
  python -m pytest -q -m api 2>&1 | tail -3
  for p in "${PIECES[@]}"; do
    echo "== guide $p ($(date +%H:%M)), about 1-2 minutes =="
    qc guide "$p" --lang en zh
  done
  echo "== ask =="
  qc ask op18no5_3 "Where does the viola carry the tune?"
  qc ask op18no5_3 "这个乐章的第四变奏有什么特别？"
  qc ask op18no5_3 "When did Beethoven write this?"
  qc site
  echo "== done $(date) =="
} 2>&1 | tee "$LOG"
