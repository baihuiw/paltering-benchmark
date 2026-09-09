"""Significance tests for the v6 full run.

Turn transitions are PAIRED within episode (the same episode's reply at turn t and t+1):
McNemar's exact test on honest(t) vs honest(t+1). Condition contrasts at turn 2 are paired
at the SCENARIO level (each scenario's honest rate under C1 or C3 minus under C0): Wilcoxon
signed-rank across scenarios, with an episode-level chi-square for reference. Episodes
within a scenario are not independent, which is why the scenario-level test is primary.

Usage:  python stats_v6.py --tags v6 gemma   ->  results/stats_v6.json + printed tables
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import argparse
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

from scipy.stats import wilcoxon, chi2_contingency
from statsmodels.stats.contingency_tables import mcnemar

from paltering.analysis.decode_paltering import classify

PRESSURE = ("C1_office_harm", "C3_shutdown_contingent")


def honest(v):
    return v["cls"] == "honest"


def transitions(C, model, conds):
    out = []
    for t in (1, 2, 3):
        pairs = [(honest(C[t][k]), honest(C[t + 1][k])) for k in C[t] if k in C[t + 1] and k[2] == model and k[1] in conds]
        if len(pairs) < 10:
            continue
        b = sum(1 for a, c in pairs if a and not c)      # honest -> not honest
        c = sum(1 for a, c in pairs if not a and c)      # not honest -> honest
        p = mcnemar([[0, b], [c, 0]], exact=True).pvalue if (b + c) else 1.0
        out.append({"from": t, "to": t + 1, "n": len(pairs),
                    "honest_from": 100 * sum(a for a, _ in pairs) / len(pairs),
                    "honest_to": 100 * sum(c for _, c in pairs) / len(pairs),
                    "lost": b, "gained": c, "p_mcnemar": p})
    return out


def condition_contrast(C2, model, cond):
    by_scen = defaultdict(lambda: {"C0_control": [], cond: []})
    for k, v in C2.items():
        if k[2] == model and k[1] in ("C0_control", cond):
            by_scen[k[0]][k[1]].append(honest(v))
    diffs = [(st.mean(d[cond]) - st.mean(d["C0_control"])) * 100 for d in by_scen.values() if d[cond] and d["C0_control"]]
    a = [honest(v) for k, v in C2.items() if k[2] == model and k[1] == cond]
    b = [honest(v) for k, v in C2.items() if k[2] == model and k[1] == "C0_control"]
    if len(diffs) < 5 or not a or not b:
        return None
    try:
        p_w = wilcoxon(diffs).pvalue if any(diffs) else 1.0
    except ValueError:
        p_w = 1.0
    tab = [[sum(a), len(a) - sum(a)], [sum(b), len(b) - sum(b)]]
    p_chi = chi2_contingency(tab)[1] if min(map(min, tab)) >= 0 else 1.0
    return {"cond": cond, "n_scenarios": len(diffs), "mean_diff_pts": st.mean(diffs),
            "honest_cond": 100 * st.mean(a), "honest_c0": 100 * st.mean(b), "p_wilcoxon": p_w, "p_chi2": p_chi}


def main(a):
    C = {t: {} for t in (1, 2, 3, 4)}
    for tag in a.tags:
        if (ROOT / "results" / f"loop5_{tag}" / "reader.jsonl").exists():
            for t in C:
                C[t] |= classify(tag, t)
    models = list(dict.fromkeys(k[2] for k in C[2]))
    res = {}
    for m in models:
        res[m] = {"pressured": transitions(C, m, PRESSURE), "control": transitions(C, m, ("C0_control",)),
                  "conditions": [x for x in (condition_contrast(C[2], m, c) for c in PRESSURE) if x]}
    (ROOT / "results" / "stats_v6.json").write_text(json.dumps(res, indent=1))
    star = lambda p: "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else "ns"
    print("TURN TRANSITIONS, honest % (paired McNemar within episode)")
    for m in models:
        for label in ("pressured", "control"):
            line = f"  {m:14s}{label:10s}"
            for x in res[m][label]:
                line += f"  t{x['from']}->t{x['to']} {x['honest_from']:3.0f}->{x['honest_to']:3.0f} {star(x['p_mcnemar']):3s}(p={x['p_mcnemar']:.3g})"
            print(line)
    print("\nCONDITION CONTRASTS at turn 2 (scenario-paired Wilcoxon; chi-square on episodes)")
    for m in models:
        for x in res[m]["conditions"]:
            print(f"  {m:14s}{x['cond'][:2]} vs C0: honest {x['honest_cond']:3.0f} vs {x['honest_c0']:3.0f}  diff {x['mean_diff_pts']:+5.1f} pts over {x['n_scenarios']} scenarios  "
                  f"Wilcoxon {star(x['p_wilcoxon'])} (p={x['p_wilcoxon']:.3g})  chi2 {star(x['p_chi2'])} (p={x['p_chi2']:.3g})")
    print(f"\nwrote {ROOT / 'results' / 'stats_v6.json'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", nargs="+", default=["v6", "gemma"])
    main(ap.parse_args())
