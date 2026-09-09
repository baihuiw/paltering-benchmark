"""
Build data/scenarios.json from stimuli/scenarios_v2.md (unified schema).

Parses the human-authored Markdown, validates structure, and writes JSON that
the T1/T2/T3 runners consume. Fails loudly with the offending scenario title.

Usage:
    python build_scenarios.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "stimuli" / "scenarios_v2.md"
OUT = HERE / "data" / "scenarios.json"

CELLS = ["fully_true", "palter", "truthy_falsehood", "blatant_falsehood"]
# (verbatim_truth, gist_truth) ground truth per cell
CELL_TRUTH = {
    "fully_true":        (True, True),
    "palter":            (True, False),
    "truthy_falsehood":  (False, True),
    "blatant_falsehood": (False, False),
}


def _strip_comment(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _field(block: str, label: str, *, required=True, scenario="?") -> str:
    """Extract a single-line 'Label: value' field from a block."""
    m = re.search(rf"^{re.escape(label)}:\s*(.+)$", block, flags=re.MULTILINE)
    if not m:
        if required:
            sys.exit(f"ERROR in scenario {scenario!r}: missing field '{label}:'")
        return ""
    return m.group(1).strip()


def _parse_cell(scenario_block: str, cell: str, scenario_title: str) -> dict:
    # Grab the text between "### cell" and the next "###" or "Production request:"
    pat = rf"###\s*{cell}\s*\n(.*?)(?=\n###|\nProduction request:|\Z)"
    m = re.search(pat, scenario_block, flags=re.DOTALL)
    if not m:
        sys.exit(f"ERROR in scenario {scenario_title!r}: missing cell '### {cell}'")
    body = m.group(1)
    statement = _field(body, "Statement", scenario=scenario_title)
    context = _field(body, "Context", required=False, scenario=scenario_title)
    # Review-only annotation (palter/truthy_falsehood cells): why the statement
    # is verbatim-true/false and how it misleads. NEVER sent to the model —
    # run_t1_judgment.build_prompt() uses only user_question + statement.
    note = _field(body, "Note", required=False, scenario=scenario_title)
    v, g = CELL_TRUTH[cell]
    return {
        "cell_type": cell,
        "verbatim_truth": v,
        "gist_truth": g,
        "statement": statement,
        "context": context,
        "note": note,
    }


def parse() -> list:
    if not SRC.exists():
        sys.exit(f"ERROR: {SRC} not found")
    # Leading "\n" guarantees a scenario header at the very start of the file
    # (e.g. if the preamble comment is missing) is still a valid split point.
    text = "\n" + _strip_comment(SRC.read_text())

    # Split into scenario blocks
    parts = re.split(r"\n##\s+Scenario\s+\d+:", text)
    headers = re.findall(r"\n##\s+Scenario\s+(\d+):\s*(.+)", text)
    # parts[0] is preamble; align with headers
    blocks = parts[1:]
    if len(blocks) != len(headers):
        sys.exit(f"ERROR: found {len(headers)} scenario headers but {len(blocks)} blocks")

    scenarios = []
    seen_ids = set()
    for (num, title), block in zip(headers, blocks):
        title = title.strip()
        sid = f"s{num}"
        if sid in seen_ids:
            sys.exit(f"ERROR: duplicate scenario id {sid}")
        seen_ids.add(sid)

        scenario = {
            "scenario_id": sid,
            "title": title,
            "domain": _field(block, "Domain", scenario=title),
            "background": _field(block, "Background", scenario=title),
            "true_gist": _field(block, "True gist", scenario=title),
            "false_gist": _field(block, "False gist", scenario=title),
            "user_question": _field(block, "User question", scenario=title),
            "production_request": _field(block, "Production request", scenario=title),
            "persona_true_gist": _field(block, "Persona true_gist", scenario=title),
            "persona_false_gist": _field(block, "Persona false_gist", scenario=title),
            "cells": [_parse_cell(block, c, title) for c in CELLS],
        }
        scenarios.append(scenario)

    return scenarios


def main():
    import argparse
    global SRC, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(SRC), help="stimuli markdown file")
    ap.add_argument("--out", default=str(OUT), help="output JSON path")
    args = ap.parse_args()
    SRC, OUT = Path(args.src), Path(args.out)

    scenarios = parse()
    # Validate non-empty fields
    for s in scenarios:
        for k, v in s.items():
            if k == "cells":
                continue
            if not v:
                sys.exit(f"ERROR: scenario {s['scenario_id']} has empty field {k!r}")
        for c in s["cells"]:
            if not c["statement"]:
                sys.exit(f"ERROR: scenario {s['scenario_id']} cell {c['cell_type']} has empty statement")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(scenarios, indent=2, ensure_ascii=False))
    print(f"✓ Parsed {len(scenarios)} scenarios ({len(scenarios) * 4} cells)")
    domains = {}
    for s in scenarios:
        domains[s["domain"]] = domains.get(s["domain"], 0) + 1
    print(f"✓ Domains: {dict(domains)}")
    print(f"✓ Wrote {OUT}")


if __name__ == "__main__":
    main()
