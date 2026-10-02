from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data" / "analysis.json").read_text(encoding="utf-8"))
ok = [r for r in data if r.get("status") == "ok"]
if not ok:
    raise SystemExit("Validation failed: no successful DART financial records were collected.")
required = ["year", "period", "status"]
for i, r in enumerate(data):
    missing = [k for k in required if k not in r]
    if missing:
        raise SystemExit(f"Validation failed at row {i}: missing {missing}")
print(f"Validation passed: {len(ok)} successful records / {len(data)} total records.")
