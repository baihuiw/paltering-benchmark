"""
Generate a human-readable preview of every T1 prompt exactly as the models
will receive it.

Writes results/prompts_preview_t1_<context>.md with all scenarios x 4 cells.
Re-run after any edit to stimuli/scenarios_v2.md (and after build_scenarios.py).

Usage:
    python preview_prompts.py                 # cold (primary arm)
    python preview_prompts.py --context informed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_t1_judgment import build_prompt  # noqa: E402
from run_recognition import R1_PROMPT, R3_PROMPT, r2_prompts_for_cell  # noqa: E402

HERE = Path(__file__).parent
CELL_ORDER = ["fully_true", "palter", "truthy_falsehood", "blatant_falsehood"]
CELL_TAG = {
    "fully_true": "WHOLE TRUTH (V+ G+)",
    "palter": "PALTER (V+ G-)",
    "truthy_falsehood": "TRUTHY FALSEHOOD (V- G+)",
    "blatant_falsehood": "BLATANT FALSEHOOD (V- G-)",
}


def write_recognition_preview(scenarios, out_path):
    lines = [
        "# Recognition battery (R1-R3) prompt preview",
        "",
        f"- **Scenarios:** {len(scenarios)}   "
        f"**Prompts:** R1 {len(scenarios) * 4} + R2 {len(scenarios) * 4} (x2 orderings) + R3 {len(scenarios) * 2}",
        "- R1/R3 can run with `--search`; R2 never searches (pure pragmatic reading).",
        "- R2's A/B option order is counterbalanced across samples; one ordering shown.",
        "",
    ]
    for s in scenarios:
        lines.append("---")
        lines.append(f"## {s['scenario_id']}: {s['title']}  [{s['domain']}]")
        cells = {c["cell_type"]: c for c in s["cells"]}
        for ct in CELL_ORDER:
            lines.append(f"\n### {s['scenario_id']} / {CELL_TAG[ct]} — R1 (verbatim verification)\n")
            lines.append("```text")
            lines.append(R1_PROMPT.format(statement=cells[ct]["statement"]))
            lines.append("```")
            lines.append(f"\n### {s['scenario_id']} / {CELL_TAG[ct]} — R2 (gist extraction)\n")
            lines.append("```text")
            lines.append(r2_prompts_for_cell(s, cells[ct], 2)[0][0])
            lines.append("```")
        for kind in ("true_gist", "false_gist"):
            lines.append(f"\n### {s['scenario_id']} — R3 (gist evaluation: {kind})\n")
            lines.append("```text")
            lines.append(R3_PROMPT.format(topic=s["title"], gist=s[kind]))
            lines.append("```")
        lines.append("")
    out_path.write_text("\n".join(lines))
    print(f"✓ wrote recognition preview to {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="t1", choices=["t1", "recognition"])
    ap.add_argument("--context", default="cold", choices=["cold", "informed"])
    ap.add_argument("--data", default=str(HERE / "data" / "scenarios.json"),
                    help="scenario JSON to render (e.g., data/scenarios_euvsdisinfo.json)")
    ap.add_argument("--scenarios", nargs="+", default=None,
                    help="only render these scenario ids, e.g. s19 s20 s21")
    ap.add_argument("--no-notes", action="store_true",
                    help="omit the review-only Note lines; show only what the model receives")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    scenarios = json.loads(Path(args.data).read_text())
    if args.scenarios:
        keep = set(args.scenarios)
        scenarios = [s for s in scenarios if s["scenario_id"] in keep]
    set_tag = Path(args.data).stem.replace("scenarios", "").strip("_") or "main"

    if args.task == "recognition":
        out_path = Path(args.output) if args.output else (
            HERE / "results" / f"prompts_preview_recognition{'_' + set_tag if set_tag != 'main' else ''}.md"
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_recognition_preview(scenarios, out_path)
        return

    suffix = f"_{set_tag}" if set_tag != "main" else ""
    out_path = Path(args.output) if args.output else (
        HERE / "results" / f"prompts_preview_t1_{args.context}{suffix}.md"
    )

    lines = [f"# T1 prompts — {len(scenarios)} scenarios × 4 cells", ""]
    for s in scenarios:
        lines.append(f"## {s['scenario_id']}: {s['title']}  [{s['domain']}]")
        lines.append("")
        cells = {c["cell_type"]: c for c in s["cells"]}
        for ct in CELL_ORDER:
            lines.append(f"### {s['scenario_id']} / {CELL_TAG[ct]}")
            lines.append("")
            lines.append("```text")
            lines.append(build_prompt(s, cells[ct], args.context))
            lines.append("```")
            lines.append("")
            if cells[ct].get("note") and not args.no_notes:
                lines.append(f"**Note (review only — not sent to the model):** {cells[ct]['note']}")
                lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    print(f"✓ wrote {len(scenarios) * 4} prompts to {out_path}")


if __name__ == "__main__":
    main()
