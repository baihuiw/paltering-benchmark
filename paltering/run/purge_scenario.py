"""Move one scenario's rows out of a loop results dir (backed up), so the
runner will regenerate it.
Usage: python purge_scenario.py <results_dir_name> <scenario_id> <suffix>
   e.g. python purge_scenario.py loop5_v5 m2_northstar_plan bak_empty"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import json
import sys
from pathlib import Path

dirname, sid, suffix = sys.argv[1], sys.argv[2], sys.argv[3]
d = ROOT / "results" / dirname
for name in ("episodes", "reader", "falseclaim", "facts", "probes", "audit", "challenge"):
    p = d / f"{name}.jsonl"
    if not p.exists():
        continue
    rows = [json.loads(l) for l in p.open()]
    gone = [r for r in rows if r.get("scenario") == sid]
    keep = [r for r in rows if r.get("scenario") != sid]
    (d / f"{name}.{suffix}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in gone))
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep))
    print(f"{name}: kept {len(keep)}, backed up {len(gone)} {sid} rows -> {name}.{suffix}.jsonl")
