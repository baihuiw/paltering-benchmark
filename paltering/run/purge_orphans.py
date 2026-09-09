"""Drop score rows whose episode no longer exists in episodes.jsonl (orphans left behind when
an episode file is rewritten while another process appends to it). Run BEFORE re-running the
missing cells so their fresh scores do not mix with stale ones.

Usage:  python purge_orphans.py --tag v6_goal
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import argparse
import json
from pathlib import Path

from paltering.run.run_loop import load

FILES = ("reader", "falseclaim", "facts", "probes", "audit", "challenge", "falseclaim_verified")


def main(a):
    d = ROOT / "results" / f"loop5_{a.tag}"
    keys = {(r["scenario"], r["condition"], r["model"], r["episode"]) for r in load(d / "episodes.jsonl")}
    for name in FILES:
        p = d / f"{name}.jsonl"
        if not p.exists():
            continue
        rows = load(p)
        keep = [r for r in rows if not r.get("condition") or (r["scenario"], r["condition"], r["model"], r["episode"]) in keys]
        if len(keep) != len(rows):
            p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep))
        print(f"  {name:22s} kept {len(keep)}/{len(rows)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    main(ap.parse_args())
