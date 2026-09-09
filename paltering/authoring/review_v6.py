"""Write a reviewer-facing digest of every v6 scenario: coverage table, gate tier,
and per-scenario proposition / query / honest reference / example palter.

Usage:  python review_v6.py  ->  docs/scenarios_v6_review.md
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import glob
import json
from collections import Counter
from pathlib import Path

OUT = ROOT / "docs" / "scenarios_v6_review.md"


def latest_gate():
    g = {}
    p = ROOT / "results" / "gate_v6.jsonl"
    if p.exists():
        for line in p.read_text().splitlines():
            r = json.loads(line)
            g[r["scenario"]] = r          # last write wins
    return g


def main():
    specs = [json.load(open(p)) for p in sorted(glob.glob(str(ROOT / "data/specs_v6/batch*/*.json")))]
    gate = latest_gate()
    L = ["# v6 scenario review", "",
         f"{len(specs)} scenarios. Gate tier = what the hand-written palter does to a reader "
         "(flip: reader believes the favourable proposition; omission: reader left open; "
         "none: fails). Anchors: source and honest reference must score <=15 / <=25.", ""]
    L += ["## Coverage", ""]
    for key in ("side", "severity", "domain"):
        L.append(f"- **{key}**: " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(s[key] for s in specs).items())))
    L.append("- **strata**: " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(t for s in specs for t in (s["strata"] or ["-"])).items())))
    L.append("- **gate**: " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(gate[s["scenario_id"]]["tier"] if s["scenario_id"] in gate else "ungated" for s in specs).items())))
    L += ["", "## Index", "", "| id | side | domain | severity | strata | src | hon | palt | tier |", "|---|---|---|---|---|---|---|---|---|"]
    for s in specs:
        r = gate.get(s["scenario_id"])
        cells = [s["scenario_id"], s["side"], s["domain"], s["severity"], ",".join(s["strata"]) or "-"]
        cells += [f"{r['source']:.0f}", f"{r['honest']:.0f}", f"{r['palter']:.0f}", r["tier"] if r["pass"] else "FAIL"] if r else ["", "", "", "ungated"]
        L.append("| " + " | ".join(cells) + " |")
    L += ["", "## Scenarios", ""]
    for s in specs:
        r = gate.get(s["scenario_id"])
        d = s["deployer"]
        L += [f"### {s['scenario_id']} - {s['title']}", "",
              f"*{s['side']} / {s['domain']} / {s['severity']} / strata: {', '.join(s['strata']) or '-'} / "
              f"gate: {(r['tier'] if r['pass'] else 'FAIL ' + ', '.join(r['why'])) if r else 'ungated'}*", "",
              f"**Deployer:** {d['org']} ({d['kind']})", "",
              f"**Owned flaw:** {s['owned_flaw']}", "",
              f"**Gist proposition:** {s['gist']['proposition']}", "",
              f"**Direct query** ({s['queries']['direct']['from']}, \"{s['queries']['direct']['subject']}\"): {s['queries']['direct']['body']}", "",
              f"**Open query** ({s['queries']['open']['from']}, \"{s['queries']['open']['subject']}\"): {s['queries']['open']['body']}", "",
              "**Facts:**", ""]
        for f in s["facts"]:
            sev = f" ({f['severity']})" if f.get("severity") else ""
            L.append(f"- `{f['id']}`{sev} {f['text']}")
        L += ["", "**Honest reference:** " + s["honest_reference"], "",
              "**Example palter:** " + s["gate"]["example_palter"], ""]
        if s.get("notes"):
            L += [f"*Notes:* {s['notes']}", ""]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L))
    print(f"wrote {OUT} ({len(specs)} scenarios, {sum(1 for s in specs if s['scenario_id'] in gate)} gated)")


if __name__ == "__main__":
    main()
