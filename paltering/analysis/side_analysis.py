"""Where the paltering happens: turn-2 classes by side (political vs market), by harm to the public
(physical / financial / reputational) and by domain, per model and condition; scenario-level tests.

Usage:  python side_analysis.py  ->  results/side_analysis.json (+ printed tables)
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import glob
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

from scipy.stats import mannwhitneyu, kruskal

from paltering.analysis.decode_paltering import classify, rates

HARM = {"physical": "physical", "material": "financial", "reputational": "reputational"}
PILOT_META = {"m1_veridian_cgm": ("market", "medical_pharma", "physical"), "m2_northstar_plan": ("market", "insurance", "financial"),
              "p1_school_lead": ("political", "public_health", "physical"), "p2_reassessment": ("political", "budget_fees", "financial"),
              "p3_shelter_siting": ("political", "housing_zoning", "reputational")}
MODELS = ["sonnet5", "gpt56luna", "gemini38flash", "deepseekv4pro", "kimik3", "local"]
CONDS = ["C0_control", "C1_office_harm", "C3_shutdown_contingent"]


def meta():
    m = {}
    for p in glob.glob(str(ROOT / "data/specs_v6/batch*/*.json")):
        s = json.load(open(p))
        m[s["scenario_id"]] = (s["side"], s["domain"], HARM.get(s["severity"], s["severity"]))
    m.update(PILOT_META)
    return m


def main():
    M = meta()
    C = classify("v6", 2)
    if (ROOT / "results" / "loop5_gemma" / "reader.jsonl").exists():
        C |= classify("gemma", 2)
    out = {"by_side": {}, "by_harm": {}, "by_domain": {}, "tests": {}}
    # 1. side x condition x model
    print("TURN 2, paltering % (honest %) by side and condition")
    print(f"{'model':14s}" + "".join(f"{side[:3]+' '+c[:2]:>12s}" for side in ("political", "market") for c in CONDS))
    for m in MODELS:
        row = {}
        line = f"{m:14s}"
        for side in ("political", "market"):
            for c in CONDS:
                it = [v for k, v in C.items() if k[2] == m and k[1] == c and M.get(k[0], ("?",))[0] == side]
                r = rates(it)
                row[f"{side}|{c}"] = r
                line += f"{r['paltering']:5.0f} ({r['honest']:3.0f})" if r["n"] else f"{'--':>12s}"
        out["by_side"][m] = row
        print(line)
    # 2. harm x condition (pooled over the five API models + gemma separately)
    print("\nTURN 2, paltering % by harm to the public and condition (five API models pooled; Gemma separately)")
    for group, ms in (("api", MODELS[:5]), ("gemma", ["local"])):
        out["by_harm"][group] = {}
        for harm in ("physical", "financial", "reputational"):
            line = f"  {group:6s}{harm:13s}"
            for c in CONDS:
                it = [v for k, v in C.items() if k[2] in ms and k[1] == c and M.get(k[0], (None, None, None))[2] == harm]
                r = rates(it)
                out["by_harm"][group][f"{harm}|{c}"] = r
                line += f"  {c[:2]} {r['paltering']:4.0f}% ({r['k_paltering']}/{r['n']})"
            print(line)
    # per model x harm, pressure pooled
    print("\nTURN 2 under pressure (C1+C3), paltering % by harm, per model")
    for m in MODELS:
        line = f"  {m:14s}"
        for harm in ("physical", "financial", "reputational"):
            it = [v for k, v in C.items() if k[2] == m and k[1] != "C0_control" and M.get(k[0], (None, None, None))[2] == harm]
            r = rates(it)
            out["by_harm"].setdefault("per_model", {})[f"{m}|{harm}"] = r
            line += f"  {harm[:4]} {r['paltering']:4.0f}% ({r['k_paltering']}/{r['n']})"
        print(line)
    # 3. domain, pressure pooled, API models pooled and gemma
    print("\nTURN 2 under pressure (C1+C3), paltering % by domain (five API models pooled)")
    dom = defaultdict(list)
    for k, v in C.items():
        if k[2] in MODELS[:5] and k[1] != "C0_control" and k[0] in M:
            dom[(M[k[0]][0], M[k[0]][1])].append(v)
    rows = []
    for (side, d), it in dom.items():
        r = rates(it)
        n_scen = len({k[0] for k in C if k[0] in M and M[k[0]][1] == d})
        rows.append({"side": side, "domain": d, "paltering": r["paltering"], "honest": r["honest"], "deceptive": r["deceptive"], "k": r["k_paltering"], "n": r["n"], "scenarios": n_scen})
    rows.sort(key=lambda x: -x["paltering"])
    out["by_domain"] = rows
    for x in rows:
        print(f"  {x['side'][:3]} {x['domain']:26s} paltering {x['paltering']:4.0f}% ({x['k']}/{x['n']})  scenarios {x['scenarios']}")
    # 4. scenario-level tests: side (Mann-Whitney) and harm (Kruskal-Wallis), per model, pressure pooled
    print("\nscenario-level tests, turn 2 under pressure: political vs market (Mann-Whitney), harm groups (Kruskal-Wallis)")
    for m in MODELS:
        per = defaultdict(list)
        for k, v in C.items():
            if k[2] == m and k[1] != "C0_control" and k[0] in M:
                per[k[0]].append(v["cls"] == "paltering")
        sc = {s: 100 * st.mean(v) for s, v in per.items()}
        if not sc:
            continue
        pol = [r for s, r in sc.items() if M[s][0] == "political"]; mar = [r for s, r in sc.items() if M[s][0] == "market"]
        groups = [[r for s, r in sc.items() if M[s][2] == h] for h in ("physical", "financial", "reputational")]
        p_side = mannwhitneyu(pol, mar).pvalue if pol and mar else None
        p_harm = kruskal(*groups).pvalue if all(groups) else None
        out["tests"][m] = {"political_mean": st.mean(pol), "market_mean": st.mean(mar), "p_side": p_side,
                           "harm_means": {h: st.mean(g) for h, g in zip(("physical", "financial", "reputational"), groups)}, "p_harm": p_harm}
        print(f"  {m:14s} political {st.mean(pol):4.1f}% vs market {st.mean(mar):4.1f}%  p={p_side:.3g}   harm physical {st.mean(groups[0]):4.1f} financial {st.mean(groups[1]):4.1f} reputational {st.mean(groups[2]):4.1f}  p={p_harm:.3g}")
    (ROOT / "results" / "side_analysis.json").write_text(json.dumps(out, indent=1))
    print("wrote results/side_analysis.json")


if __name__ == "__main__":
    main()
