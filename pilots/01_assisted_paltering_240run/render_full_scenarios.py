"""Render authored full-run scenarios into one reviewable markdown file.

Usage:
    python render_full_scenarios.py data/full_marketplace_scenarios_sample6v3.json \
        data/full_misinfo_scenarios_sample6v3.json -o results/full_scenarios_review.md
"""
import argparse
import json
from pathlib import Path

VAL = {"pos": "supports the pitch/anchor", "neg_minor": "minor drawback",
       "neg_material": "THE DAMAGING/FLIPPING FACT"}


def render(files, out):
    lines = ["# Full-run scenario drafts — for review",
             "",
             "Every scenario below carries review:true. Nothing runs until a "
             "human pass clears it. Fact valences: pos = quotable in support "
             "of the pitch (marketplace) or the wrong-gist anchor (misinfo); "
             "neg_material = the one fact that flips the gist.", ""]
    for fp in files:
        d = json.loads(Path(fp).read_text())
        scen = d["scenarios"]
        dom = scen[0]["domain"] if scen else "?"
        lines += ["", "=" * 80,
                  f"# DOMAIN: {dom.upper()} — {len(scen)} scenarios "
                  f"({len(d.get('failed', []))} failed/skipped) — {Path(fp).name}",
                  "=" * 80]
        for s in scen:
            tag = "  ⚑ CATCH TRIAL (honest baseline — EXCLUDE from palter stats)" \
                if s.get("catch_trial") else ""
            lines += ["", "-" * 80, f"## {s['id']} — {s['title']}{tag}", ""]
            for k, label in (("preamble", "Requester preamble"),
                             ("document", "Document (the model alone sees this)"),
                             ("buried_fact", "Damaging/critical fact"),
                             ("misleading_gist", "Wrong gist being measured"),
                             ("decoys", "Decoys"),
                             ("inquiry", "Counterparty inquiry"),
                             ("goal", "Goal (rides in rung R2 = push condition)"),
                             ("followup", "Point-blank follow-up (turn 2)"),
                             ("reader_context", "Reader context"),
                             ("reader_gist", "Reader GIST item (agreement = misled)"),
                             ("reader_complete", "Reader COMPLETE item"),
                             ("reader_action", "Reader ACTION item"),
                             ("honest_reference", "Honest reference reply")):
                v = s.get(k, "")
                if k == "document":
                    lines += [f"**{label}:**", "", "```", str(v).strip(), "```", ""]
                else:
                    lines += [f"**{label}:** {v}", ""]
            lines += ["**Fact checklist (transmission scoring):**", ""]
            for f in s["facts"]:
                lines += [f"{f['idx']:2d}. `[{f['valence']}]` {f['text']}"]
            lines += [""]
    Path(out).write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("-o", "--out", default="results/full_scenarios_review.md")
    a = ap.parse_args()
    render(a.files, a.out)
