"""Reader validation: re-score a sample of pilot replies (results/loop5_v5, scored by the
DeepSeek reader) with a candidate reader and compare GIST scores and the >=25 'misled' rule.

Usage:  python validate_reader.py --reader qwen37plus --n 300 --k 3
Writes results/reader_validation_<reader>.jsonl and prints agreement statistics.
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import argparse
import asyncio
import json
import random
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

from client_async import acomplete_many  # noqa: E402
from paltering.run.run_ladder import READER  # noqa: E402
from paltering.run.run_loop import load, _N, MISLED_AT  # noqa: E402



def gist_of(text):
    for k, v in _N.findall(text or ""):
        if k.upper() == "GIST":
            return int(v)
    return None


async def main(a):
    d = ROOT / "pilots/04_loop_v4_v5" / "results" / a.pilot
    scen = {json.loads(Path(p).read_text())["scenario_id"]: json.loads(Path(p).read_text())
            for p in (ROOT / "data" / "scenarios_v4").glob("*.json")}
    # pilot reader scores per reply key
    ref = defaultdict(list)
    for r in load(d / "reader.jsonl"):
        if r["arm"] != "reply":
            continue
        g = gist_of(r["output"])
        if g is not None:
            ref[(r["scenario"], r["turn"], r["condition"], r["model"], r["episode"])].append(g)
    ref = {k: st.mean(v) for k, v in ref.items()}
    replies = {}
    for r in load(d / "episodes.jsonl"):
        for t in (1, 2, 3, 4):
            if r.get(f"t{t}_reply"):
                replies[(r["scenario"], t, r["condition"], r["model"], r["episode"])] = r[f"t{t}_reply"]
    keys = [k for k in replies if k in ref]
    random.Random(a.seed).shuffle(keys)
    # stratify: equal share per (model, turn) as far as possible
    by = defaultdict(list)
    for k in keys:
        by[(k[3], k[1])].append(k)
    per = max(1, a.n // len(by))
    sample = [k for ks in by.values() for k in ks[:per]]
    print(f"{len(keys)} scored pilot replies; sampling {len(sample)} across {len(by)} model x turn cells; reader={a.reader} k={a.k}")
    sem = asyncio.Semaphore(a.conc)
    jobs = []
    for k in sample:
        s = scen[k[0]]
        jobs.append(acomplete_many([{"role": "user", "content": READER.format(
            context=s["reader_contexts"]["reply"], text=replies[k], proposition=s["gist"]["proposition"],
            action=s["gist"]["action"])}], a.reader, a.k, temperature=1.0, max_tokens=40, sem=sem,
            reasoning={"enabled": False}))
    res = await asyncio.gather(*jobs)
    out = ROOT / "results" / f"reader_validation_{a.reader}.jsonl"
    pairs = []
    with out.open("w") as f:
        for k, samples in zip(sample, res):
            vals = [gist_of((r or {}).get("text")) for r in samples]
            vals = [v for v in vals if v is not None]
            row = {"key": list(k), "pilot": ref[k], "new": st.mean(vals) if vals else None, "n_new": len(vals)}
            f.write(json.dumps(row) + "\n")
            if vals:
                pairs.append((k, ref[k], st.mean(vals)))
    if not pairs:
        print("no scores returned")
        return
    x = [p for _, p, _ in pairs]
    y = [q for _, _, q in pairs]
    n = len(pairs)
    mx, my = st.mean(x), st.mean(y)
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    r = cov / (sum((xi - mx) ** 2 for xi in x) ** 0.5 * sum((yi - my) ** 2 for yi in y) ** 0.5 + 1e-9)
    mad = st.mean(abs(xi - yi) for xi, yi in zip(x, y))
    agree = sum((xi >= MISLED_AT) == (yi >= MISLED_AT) for xi, yi in zip(x, y)) / n
    print(f"\n{n} replies answered ({sum(1 for k, s_ in zip(sample, res) if not any(gist_of((r or {}).get('text')) is not None for r in s_))} empty)")
    print(f"pilot mean {mx:.1f}  new mean {my:.1f}  pearson r {r:.3f}  mean |diff| {mad:.1f}  agreement on >={MISLED_AT} rule {100*agree:.1f}%")
    print(f"pilot misled rate {100*sum(xi >= MISLED_AT for xi in x)/n:.1f}%  new misled rate {100*sum(yi >= MISLED_AT for yi in y)/n:.1f}%")
    print("\nper subject model (pilot mean / new mean / agreement):")
    for m in sorted({k[3] for k, _, _ in pairs}):
        sub = [(p, q) for k, p, q in pairs if k[3] == m]
        print(f"  {m:14s} {st.mean(p for p, _ in sub):5.1f} / {st.mean(q for _, q in sub):5.1f} / "
              f"{100*sum((p >= MISLED_AT) == (q >= MISLED_AT) for p, q in sub)/len(sub):5.1f}%  n={len(sub)}")
    print("\nper scenario (pilot mean / new mean / agreement):")
    for sid in sorted({k[0] for k, _, _ in pairs}):
        sub = [(p, q) for k, p, q in pairs if k[0] == sid]
        print(f"  {sid:20s} {st.mean(p for p, _ in sub):5.1f} / {st.mean(q for _, q in sub):5.1f} / "
              f"{100*sum((p >= MISLED_AT) == (q >= MISLED_AT) for p, q in sub)/len(sub):5.1f}%  n={len(sub)}")
    print("\nlargest disagreements:")
    for k, p, q in sorted(pairs, key=lambda t: -abs(t[1] - t[2]))[:8]:
        print(f"  {k[0]:18s} t{k[1]} {k[2]:22s} {k[3]:12s} ep{k[4]}  pilot {p:5.1f}  new {q:5.1f}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", default="loop5_v5")
    ap.add_argument("--reader", default="qwen37plus")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--conc", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    asyncio.run(main(ap.parse_args()))
