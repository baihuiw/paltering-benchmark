"""Strip model wrappers from t1 replies before scoring.

Models often wrap the drafted message in commentary aimed at the REQUESTER
("Here's a reply you can send:" ... "Let me know if you want it shorter").
In the pilot, Opus did this ~98% of the time, GPT ~0% -- a differential that
biases the reader and judge unless removed: they must score the message the
counterparty would receive, not the assistant's note to its user.

Writes results/misuse_v2_t1_{tag}_clean/samples.jsonl with
    output      = the drafted message only
    output_full = the original, preserved

Usage:
    python clean_full_run.py --tag full
"""
import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).parent


def extract_draft(text):
    """Return just the message the counterparty would receive.
    Same logic as fix_misuse_v2.extract_draft (kept identical on purpose so
    pilot and full-run texts are treated the same way)."""
    if not text:
        return text
    t = text.strip()
    parts = t.split("\n---\n") if "\n---\n" in t else t.split("---")
    if len(parts) >= 3:
        cand = parts[1].strip()
        if len(cand) > 30:
            return cand
    t = re.sub(r"^(here'?s|here is|sure[,!]?|happy to help[,!]?|of course[,!]?)[^\n]*\n+",
               "", t, flags=re.I)
    lines = t.split("\n\n")
    while lines and re.search(
            r"\b(let me know|want me to|i (kept|left|added|included|can)|feel free|"
            r"you (may|might|could) (want|add|mention)|happy to (adjust|tweak|revise|shorten)|"
            r"note:|i'?ve (kept|left))\b", lines[-1], re.I):
        lines.pop()
    return "\n\n".join(lines).strip() or t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="full")
    a = ap.parse_args()
    src = HERE / "results" / f"misuse_v2_t1_{a.tag}" / "samples.jsonl"
    if not src.exists():
        raise SystemExit(f"missing {src}")
    rows = [json.loads(l) for l in src.open()]
    dst = HERE / "results" / f"misuse_v2_t1_{a.tag}_clean"
    dst.mkdir(parents=True, exist_ok=True)
    changed = 0
    by_model = {}
    with (dst / "samples.jsonl").open("w") as f:
        for r in rows:
            draft = extract_draft(r.get("output"))
            if draft != (r.get("output") or "").strip():
                changed += 1
                by_model[r["model"]] = by_model.get(r["model"], 0) + 1
            f.write(json.dumps({**r, "output": draft, "output_full": r.get("output")},
                               ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows -> {dst.name}  ({changed} had wrappers stripped)")
    tot = {}
    for r in rows:
        tot[r["model"]] = tot.get(r["model"], 0) + 1
    for m in sorted(tot):
        print(f"  {m:16s} {100*by_model.get(m,0)/tot[m]:5.1f}% stripped "
              f"({by_model.get(m,0)}/{tot[m]})")


if __name__ == "__main__":
    main()
