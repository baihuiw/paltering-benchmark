"""Resumable refill for the tactic judge.

The one-shot pass degrades after ~1300 calls: rows 0-1300 parsed at 93%, rows
1300+ at 0.7%, with the endpoint healthy before and after. Long-running asyncio
sessions appear to lose their connection pool / get throttled, and because the
original script wrote only at the end, a late failure silently wasted the run.

This version processes in CHUNKS and rewrites the file after every chunk, so:
  - progress is visible while it runs
  - a failure costs at most one chunk
  - re-running simply continues from wherever it stopped (idempotent)

Usage:
    python refill_tactics.py                 # process all unparsed rows
    python refill_tactics.py --chunk 200     # smaller chunks
"""
import argparse
import asyncio
import json
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))  # shared OpenRouter client at the repo root
from client_async import acomplete_many  # noqa: E402
from judge_tactics import PROMPT, KEYS, LINE  # reuse the validated prompt

HERE = Path(__file__).parent
R = HERE / "results"
OUT = R / "tactic_judge" / "tactics.jsonl"


def load_replies():
    reply = {}
    for d in ("misuse_v2_t1_full_clean", "misuse_v2_t1_sonnet_clean"):
        p = R / d / "samples.jsonl"
        if p.exists():
            for r in (json.loads(l) for l in p.open()):
                if r.get("output"):
                    reply.setdefault((r["scenario_id"], r["model"], r["rung"]), r["output"])
    return reply


async def do_chunk(rows, idxs, scen, reply, judge, conc):
    sem = asyncio.Semaphore(conc)
    jobs, keep = [], []
    for i in idxs:
        r = rows[i]
        txt = reply.get((r["sid"], r["model"], r["rung"]))
        if txt is None:
            continue
        s = scen[r["sid"]]
        jobs.append(acomplete_many(
            [{"role": "user", "content": PROMPT.format(doc=s["document"],
                                                       fact=s["buried_fact"], reply=txt)}],
            judge, 1, temperature=0, max_tokens=450, sem=sem))
        keep.append(i)
    fixed = 0
    for i, samples in zip(keep, await asyncio.gather(*jobs)):
        txt = (samples[0] or {}).get("text") or ""
        d, q = {}, {}
        for k, v, quote in LINE.findall(txt):
            d[k.upper()] = v.upper() == "YES"
            q[k.upper()] = quote.strip()
        if all(d.get(k) is not None for k in KEYS):
            rows[i].update({k.lower(): d[k] for k in KEYS})
            rows[i]["quotes"] = {k.lower(): q.get(k, "") for k in KEYS if d.get(k)}
            rows[i]["parse_ok"] = True
            fixed += 1
    return fixed


async def main(chunk, judge, conc, max_chunks):
    scen = {s["id"]: s for s in json.loads((HERE / "data/full_run_240.json").read_text())["scenarios"]}
    reply = load_replies()
    rows = [json.loads(l) for l in OUT.open()]
    if not OUT.with_suffix(".jsonl.bak").exists():
        shutil.copy(OUT, OUT.with_suffix(".jsonl.bak"))

    todo = [i for i, r in enumerate(rows) if not r.get("parse_ok")]
    print(f"{len(todo)} unparsed of {len(rows)}; chunk={chunk}, conc={conc}", flush=True)
    t0 = time.time()
    done = 0
    for c in range(0, len(todo), chunk):
        if max_chunks and c // chunk >= max_chunks:
            print("hit --max-chunks, stopping (re-run to continue)", flush=True)
            break
        batch = todo[c:c + chunk]
        fixed = await do_chunk(rows, batch, scen, reply, judge, conc)
        done += fixed
        with OUT.open("w") as f:                     # rewrite after EVERY chunk
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        ok = sum(1 for r in rows if r.get("parse_ok"))
        print(f"  chunk {c//chunk+1}: +{fixed}/{len(batch)} -> {ok}/{len(rows)} parsed "
              f"({100*ok/len(rows):.1f}%)  [{time.time()-t0:.0f}s]", flush=True)
        if fixed == 0:
            print("  chunk returned nothing - endpoint likely degraded; stopping. "
                  "Re-run later to continue.", flush=True)
            break
    ok = sum(1 for r in rows if r.get("parse_ok"))
    print(f"\nrefilled {done} this run -> {ok}/{len(rows)} parsed "
          f"({100*ok/len(rows):.1f}%) in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk", type=int, default=300)
    ap.add_argument("--judge", default="deepseekv4pro")
    ap.add_argument("--conc", type=int, default=4)
    ap.add_argument("--max-chunks", type=int, default=0)
    a = ap.parse_args()
    asyncio.run(main(a.chunk, a.judge, a.conc, a.max_chunks))
