"""
Analyze T1 samples for H1 and H2.

H1 (dissociation): the model tracks VERBATIM truth more reliably than GIST truth.
    Operationalized two ways:
      (a) Accuracy: does the mean rating land on the correct side of the scale
          (>4 when ground truth is True, <4 when False)?
      (b) Precision: entropy of the sampled rating distribution. Lower entropy
          on the verbatim channel than the gist channel = verbatim tracked more
          reliably. Reported per cell, focus on the CONFLICT cells (palter,
          truthy_falsehood) where the two channels disagree.

H2 (verbatim-literalism): unethicality is driven by VERBATIM falsity, not gist.
    We print mean UNETHICAL by cell and a simple additive decomposition:
      effect of verbatim-false  vs  effect of gist-false.
    Human pattern (Langdon): gist-false drives condemnation (palter ~ blatant
    high; truthy_falsehood low). Model-literal pattern: verbatim-false drives it
    (truthy_falsehood ~ blatant high; palter low).

Usage:
    python analyze_t1.py --tag pilot
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

HERE = Path(__file__).parent
CELL_ORDER = ["fully_true", "palter", "truthy_falsehood", "blatant_falsehood"]
CELL_SHORT = {"fully_true": "WT", "palter": "PA", "truthy_falsehood": "TF", "blatant_falsehood": "BF"}


def entropy(vals):
    """Shannon entropy (bits) of a list of 1-7 integer ratings."""
    if not vals:
        return None
    counts = defaultdict(int)
    for v in vals:
        counts[v] += 1
    n = len(vals)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def load(tag, scenario_filter=None):
    p = HERE / "results" / f"t1_{tag}" / "samples.jsonl"
    if not p.exists():
        raise SystemExit(f"no samples at {p}")
    rows = [json.loads(l) for l in p.open()]
    if scenario_filter:
        rows = [r for r in rows if r["scenario_id"] in scenario_filter]
    return rows


def report(tag, scenario_filter=None):
    rows = load(tag, scenario_filter)
    scope = ",".join(scenario_filter) if scenario_filter else "all scenarios"
    print(f"\n[scope: {scope}]")
    models = sorted({r["model"] for r in rows})

    # group by (model, cell)
    def grp(model, cell, key):
        return [r[key] for r in rows
                if r["model"] == model and r["cell_type"] == cell and r[key] is not None]

    print("\n" + "=" * 78)
    print("H1 — VERBATIM vs GIST tracking (mean rating; entropy in bits)")
    print("   ground truth: WT=(V+,G+) PA=(V+,G-) TF=(V-,G+) BF=(V-,G-);  >4 = 'true'")
    print("=" * 78)
    for model in models:
        print(f"\n  {model}")
        print(f"    {'cell':6} {'verbatim (H)':>16} {'gist (H)':>16}   ground(V,G)")
        for cell in CELL_ORDER:
            vr = grp(model, cell, "verbatim_rating")
            gr = grp(model, cell, "gist_rating")
            gt = {"fully_true": "(+,+)", "palter": "(+,-)",
                  "truthy_falsehood": "(-,+)", "blatant_falsehood": "(-,-)"}[cell]
            if vr and gr:
                print(f"    {CELL_SHORT[cell]:6} {mean(vr):6.2f} (H={entropy(vr):.2f}) "
                      f"{mean(gr):6.2f} (H={entropy(gr):.2f})   {gt}")
    # H1 summary: mean entropy verbatim vs gist on conflict cells
    print("\n  H1 test — mean entropy on conflict cells (palter+truthy), lower = more reliable:")
    for model in models:
        vents, gents = [], []
        for cell in ["palter", "truthy_falsehood"]:
            ev = entropy(grp(model, cell, "verbatim_rating"))
            eg = entropy(grp(model, cell, "gist_rating"))
            if ev is not None:
                vents.append(ev)
            if eg is not None:
                gents.append(eg)
        if vents and gents:
            flag = "✓ verbatim more reliable" if mean(vents) < mean(gents) else "✗ gist more reliable"
            print(f"    {model:14} verbatim H={mean(vents):.2f}  gist H={mean(gents):.2f}   {flag}")

    print("\n" + "=" * 78)
    print("H2 — UNETHICAL rating by cell (1=fine to post, 7=very unethical)")
    print("   human pattern: PA≈BF high, TF low.  literal pattern: TF≈BF high, PA low.")
    print("=" * 78)
    print(f"\n    {'model':14} {'WT':>6} {'PA':>6} {'TF':>6} {'BF':>6}   "
          f"{'v-false eff':>11} {'g-false eff':>11}  verdict")
    for model in models:
        m = {c: (mean(grp(model, c, "unethical_rating")) if grp(model, c, "unethical_rating") else float('nan'))
             for c in CELL_ORDER}
        # additive effects: avg unethical when verbatim-false minus when verbatim-true
        v_false = mean([m["truthy_falsehood"], m["blatant_falsehood"]])
        v_true = mean([m["fully_true"], m["palter"]])
        g_false = mean([m["palter"], m["blatant_falsehood"]])
        g_true = mean([m["fully_true"], m["truthy_falsehood"]])
        v_eff = v_false - v_true
        g_eff = g_false - g_true
        verdict = "verbatim-literal" if v_eff > g_eff else "gist-driven (human-like)"
        print(f"    {model:14} {m['fully_true']:6.2f} {m['palter']:6.2f} "
              f"{m['truthy_falsehood']:6.2f} {m['blatant_falsehood']:6.2f}   "
              f"{v_eff:>11.2f} {g_eff:>11.2f}  {verdict}")
    print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="pilot")
    ap.add_argument("--scenarios", nargs="+", default=None)
    args = ap.parse_args()
    report(args.tag, args.scenarios)
