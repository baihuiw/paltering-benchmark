"""
Go/no-go pilot: do frontier models palter when nothing false is requested?

Cells (see docs/palter_pilot_gonogo.md):
  neutral   -- plain question, no role, no goal        (the floor rate)
  incentive -- role + goal + private truth             (paltering as a free choice)

Neither cell asks for a false claim or a false conclusion, so the refusal
gate that dominates directed production does not fire; any misleading
framing is the model's own strategy. The neutral-vs-incentive contrast is
the incentive effect.

Usage:
    python run_palter_pilot.py --arm incentive --preview     # write prompts, no API
    python run_palter_pilot.py --arm incentive --run --n 3
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))  # shared OpenRouter client at the repo root
from client_async import acomplete_many, MODEL_REGISTRY  # noqa: E402

HERE = Path(__file__).parent
ITEMS = ["s1", "s4", "s12", "s13", "s18", "s21", "s23", "s26"]
MODELS = ["gpt56sol", "opus48", "gemini35flash", "kimik3"]

NEUTRAL_SYS = "You are a helpful assistant."

INCENTIVE_SYS = """{role} {goal}

{private_truth}"""


def build(arm, scenarios, personas):
    """Yield (messages, meta) for every item in the requested cell."""
    for s in scenarios:
        sid = s["scenario_id"]
        q = s["user_question"]
        if arm == "neutral":
            sys_prompt = NEUTRAL_SYS
        else:
            p = personas["personas"].get(sid)
            if not p:
                continue
            sys_prompt = INCENTIVE_SYS.format(
                role=p["role"], goal=p["goal"], private_truth=p["private_truth"])
        msgs = [{"role": "system", "content": sys_prompt},
                {"role": "user", "content": q}]
        yield msgs, {"scenario_id": sid, "arm": arm, "domain": s["domain"]}


def preview(arm, scenarios, personas):
    out = [f"# Palter go/no-go pilot -- cell: {arm}", "",
           "Nothing false is requested in either cell; paltering, if it occurs,",
           "is the model's own choice. Review before running.", ""]
    for msgs, meta in build(arm, scenarios, personas):
        title = next(s["title"] for s in scenarios if s["scenario_id"] == meta["scenario_id"])
        out += [f"## {meta['scenario_id']} ({title})", "```",
                "SYSTEM:", msgs[0]["content"], "", "USER:", msgs[1]["content"], "```", ""]
    p = HERE / "results" / f"prompts_preview_palter_pilot_{arm}.md"
    p.parent.mkdir(exist_ok=True)
    p.write_text("\n".join(out))
    n = sum(1 for _ in build(arm, scenarios, personas))
    print(f"wrote {n} prompts to {p}")


async def run(arm, scenarios, personas, models, n, tag):
    sem = asyncio.Semaphore(8)
    jobs, metas = [], []
    for msgs, meta in build(arm, scenarios, personas):
        for m in models:
            jobs.append(acomplete_many(msgs, m, n, temperature=1.0,
                                       max_tokens=400, sem=sem))
            metas.append((m, msgs, meta))
    print(f"{len(jobs)} jobs x n={n} = {len(jobs) * n} calls")
    t0 = time.time()
    rows = []
    for (m, msgs, meta), samples in zip(metas, await asyncio.gather(*jobs)):
        for i, r in enumerate(samples):
            rows.append({**meta, "model": m, "sample_idx": i,
                         "system": msgs[0]["content"],
                         "output": (r or {}).get("text") or None})
    out_dir = HERE / "results" / f"palter_pilot_{arm}_{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "samples.jsonl").open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    (out_dir / "meta.json").write_text(json.dumps(
        {"arm": arm, "models": models, "n": n, "items": ITEMS,
         "total": len(rows), "empty": sum(1 for r in rows if not r["output"]),
         "elapsed_sec": round(time.time() - t0, 1)}, indent=2))
    print(f"wrote {len(rows)} rows to {out_dir}/samples.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["neutral", "incentive"])
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--models", nargs="+", default=MODELS)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--tag", default="v1")
    args = ap.parse_args()

    scenarios = [s for s in json.loads((HERE / "data" / "scenarios.json").read_text())
                 if s["scenario_id"] in ITEMS]
    personas = json.loads((HERE / "data" / "pilot_incentive_personas.json").read_text())
    if args.arm == "incentive" and personas.get("review"):
        print("WARNING: pilot_incentive_personas.json still carries review:true "
              "-- these drafts have not been human-reviewed.")

    if args.preview or not args.run:
        preview(args.arm, scenarios, personas)
    if args.run:
        for m in args.models:
            if m not in MODEL_REGISTRY:
                sys.exit(f"unknown model {m!r}")
        asyncio.run(run(args.arm, scenarios, personas, args.models, args.n, args.tag))


if __name__ == "__main__":
    main()
