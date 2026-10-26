#!/usr/bin/env bash
# One-time setup on macOS (also works on Linux).
# Usage:  bash scripts/setup_mac.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-python3}"
"$PY" - <<'PYCHECK'
import sys
if sys.version_info < (3, 10):
    sys.exit(f"Python 3.10+ is needed, found {sys.version.split()[0]}. Try: PYTHON=/path/to/python3.11 bash scripts/setup_mac.sh")
print("Python", sys.version.split()[0], "OK")
PYCHECK

if [ ! -d .venv ]; then
  echo "Creating virtual environment in .venv ..."
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q --upgrade pip
echo "Installing packages (first time takes a few minutes) ..."
python -m pip install -q -e ".[dev]"

if [ ! -d data/ABC/notes ]; then
  echo "Downloading the ABC dataset (expert harmony labels, ~20 MB) ..."
  git clone -q --depth 1 https://github.com/DCMLab/ABC.git data/ABC
fi

echo "Running the tests ..."
python -m pytest -q
echo
echo "Setup finished. Next time, start with:  source .venv/bin/activate"
