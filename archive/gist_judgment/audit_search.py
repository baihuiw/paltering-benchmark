"""
Audit whether web search actually ran on a search-arm run.

Two independent checks per sampled call:
  1. prompt_tokens from the run's own rows — a bare T1 prompt is ~250-350
     tokens; with injected search results it jumps to ~900-1500+. Inflated
     prompt = results were injected into the context.
  2. The OpenRouter generation endpoint (GET /api/v1/generation?id=...) —
     authoritative per-call record: actual total cost (includes the search
     fee) and native token counts.

Usage:
    python audit_search.py --tag pilot1_t1_search --sample 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent


def _key() -> str:
    k = os.environ.get("OPENROUTER_API_KEY")
    if k:
        return k
    for line in (HERE / ".env").read_text().splitlines():
        if line.strip().startswith("OPENROUTER_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no OPENROUTER_API_KEY")


def fetch_generation(gen_id: str, key: str) -> dict:
    req = urllib.request.Request(
        f"https://openrouter.ai/api/v1/generation?id={gen_id}",
        headers={"Authorization": f"Bearer {key}"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="t1 run tag (e.g., pilot1_t1_search)")
    ap.add_argument("--sample", type=int, default=6, help="how many calls to audit via the API")
    args = ap.parse_args()

    path = HERE / "results" / f"t1_{args.tag}" / "samples.jsonl"
    if not path.exists():
        path = HERE / "results" / f"recognition_{args.tag}" / "samples.jsonl"
    rows = [json.loads(l) for l in path.open()]

    # Check 1: prompt-token inflation, from the run's own logs
    with_pt = [r for r in rows if r.get("prompt_tokens")]
    print(f"rows: {len(rows)} | rows with prompt_tokens logged: {len(with_pt)}")
    if with_pt:
        by_model = {}
        for r in with_pt:
            by_model.setdefault(r["model"], []).append(r["prompt_tokens"])
        print("\nCheck 1 — prompt tokens per model (bare prompt ~250-350; >800 => results injected):")
        for m, v in sorted(by_model.items()):
            print(f"  {m:14} min={min(v):5d}  mean={sum(v)/len(v):7.0f}  max={max(v):5d}  (n={len(v)})")
    else:
        print("(no prompt_tokens in this run — it predates the logging update)")

    # Check 2: generation endpoint audit on a sample of calls
    gen_rows = [r for r in rows if r.get("gen_id")]
    if not gen_rows:
        print("\n(no gen_ids in this run — re-run with the updated client to enable Check 2)")
        return
    key = _key()
    step = max(1, len(gen_rows) // args.sample)
    picked = gen_rows[::step][: args.sample]
    print(f"\nCheck 2 — generation-endpoint audit on {len(picked)} sampled calls:")
    print(f"  {'model':14} {'cell':18} {'tok_in':>7} {'tok_out':>8} {'cost($)':>9}  websearch")
    for r in picked:
        try:
            g = fetch_generation(r["gen_id"], key)
        except Exception as e:
            print(f"  {r['model']:14} fetch failed: {str(e)[:60]}")
            continue
        n_results = g.get("num_search_results")
        cost = g.get("total_cost")
        flag = f"{n_results} results" if n_results else ("fee-in-cost?" if (cost or 0) > 0.02 else "-")
        print(f"  {r['model']:14} {r.get('cell_type','?'):18} "
              f"{g.get('tokens_prompt') or g.get('native_tokens_prompt') or '?':>7} "
              f"{g.get('tokens_completion') or g.get('native_tokens_completion') or '?':>8} "
              f"{cost if cost is not None else '?':>9}  {flag}")
        time.sleep(0.3)


if __name__ == "__main__":
    main()
