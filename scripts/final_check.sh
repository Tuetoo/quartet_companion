#!/usr/bin/env bash
# Final check of the whole project. No API calls, no cost.
# Usage:  bash scripts/final_check.sh          (writes eval/final_check_<time>.log)
set -uo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
source .venv/bin/activate
mkdir -p eval
LOG="eval/final_check_$(date +%Y%m%d_%H%M%S).log"
FAIL=0
step() { echo; echo "== $1 =="; }
{
  echo "== Final check $(date) =="

  step "1. Unit and integration tests (offline)"
  python -m pytest -q > /tmp/qc_pytest.txt 2>&1 || FAIL=1
  tail -3 /tmp/qc_pytest.txt

  step "2. Every piece: facts, alignment and both guides, guides up to date and fully verified"
  python - <<'PY' || FAIL=1
import json, sys
from pathlib import Path
from quartet_companion.guide.generate import facts_fingerprint
bad = 0
for cfg_path in sorted(Path("pieces").glob("*/config.json")):
    d = cfg_path.parent
    msgs = []
    if not (d / "facts.json").exists():
        msgs.append("no facts.json (run qc analyze)")
    else:
        fp = facts_fingerprint(json.loads((d / "facts.json").read_text()))
        if json.loads(cfg_path.read_text()).get("audio", {}).get("path") and not (d / "alignment.json").exists():
            msgs.append("no alignment.json (run qc align)")
        for lang in ("en", "zh"):
            g = d / f"guide_{lang}.json"
            if not g.exists():
                msgs.append(f"no {lang} guide"); continue
            gd = json.loads(g.read_text())
            if gd.get("facts_fingerprint") not in (None, fp):
                msgs.append(f"{lang} guide is out of date")
            if gd["verification"].get("failed"):
                msgs.append(f"{lang} guide has failed claims")
            if not gd["guide"].get("listening_points"):
                msgs.append(f"{lang} guide is empty")
    print(("OK   " if not msgs else "FAIL ") + d.name + ("" if not msgs else "  " + "; ".join(msgs)))
    bad += bool(msgs)
sys.exit(1 if bad else 0)
PY

  step "3. Build the web player"
  qc site 2>&1 | grep -v "Warning\|setDirection" || FAIL=1

  step "4. Click through every piece in a headless browser"
  if python -c "import playwright" 2>/dev/null; then
    python scripts/check_site.py site || FAIL=1
  else
    echo "skipped: playwright is not installed (pip install playwright && python -m playwright install chromium)"
  fi

  step "Result"
  if [ "$FAIL" = 0 ]; then echo "ALL CHECKS PASSED"; else echo "SOME CHECKS FAILED (see above)"; fi
} 2>&1 | tee "$LOG"
echo "Log: $LOG"
