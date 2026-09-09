"""Merge the authored marketplace + misinfo scenarios into one run-ready file,
trimmed to N each. Writes data/full_run_200.json in the misuse_v2 schema so
run_misuse_v2.py --data data/full_run_200.json works unchanged.

Usage:
    python merge_full_run.py --n 100
"""
import argparse
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100, help="scenarios kept per domain")
    ap.add_argument("--market", default="data/full_marketplace_scenarios_full100.json")
    ap.add_argument("--misinfo", default="data/full_misinfo_scenarios_full100.json")
    ap.add_argument("--out", default="data/full_run_200.json")
    a = ap.parse_args()

    merged = []
    for path in (a.market, a.misinfo):
        d = json.loads((HERE / path).read_text())
        scen = d["scenarios"][:a.n]
        merged += scen
        c = Counter(s.get("catch_trial", False) for s in scen)
        dom = scen[0]["domain"] if scen else "?"
        print(f"{dom:12s}: kept {len(scen)}  (catch {c[True]}, real {c[False]})")

    ids = [s["id"] for s in merged]
    assert len(ids) == len(set(ids)), "duplicate scenario ids across domains"
    out = {"review": True, "n_per_domain": a.n, "total": len(merged),
           "catch_trials": sum(1 for s in merged if s.get("catch_trial")),
           "scenarios": merged}
    (HERE / a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"\nwrote {len(merged)} scenarios ({out['catch_trials']} catch) -> {a.out}")
    print("run with:  python run_misuse_v2.py --stage t1 --data "
          f"{a.out} --models opus5 gpt56sol gemini35flash --rungs R0 R1 R2 --n 3 --tag full")


if __name__ == "__main__":
    main()
