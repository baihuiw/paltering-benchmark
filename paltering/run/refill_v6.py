"""Refill episodes with an empty turn. Reasoning models (Kimi K3, Gemini 3.8) sometimes spend the
whole token budget on hidden reasoning and return nothing, or a scratchpad cut off before the
email tool block; the runner's 3000-token retry is not always enough. Those episodes cluster in
the scenarios the models deliberate longest over, so they are re-run end to end with a larger
budget, swapped into episodes.jsonl, and re-scored on their own.

Usage:  python refill_v6.py --tag v6 [--models kimik3 gemini38flash] [--min-tokens 9000]
        (pass --reasoning off for the noreason tag, --arm <arm> for the arm tags)
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import argparse
import asyncio
import glob
import json
import sys
from pathlib import Path

sys.argv, _argv = ["x"], sys.argv
import paltering.run.run_loop_v5 as m  # noqa: E402
from paltering.run.run_loop import load  # noqa: E402
sys.argv = _argv

KEY = ("scenario", "condition", "model", "episode")
SCORE_FILES = ("reader", "falseclaim", "facts", "probes", "audit", "challenge")


def key(r):
    return tuple(r.get(k) for k in KEY)


def missing_turn(r):
    for t in (1, 2, 3, 4):
        if f"t{t}_user" in r and not r.get(f"t{t}_reply"):
            return t
    return None


async def main(a):
    d = ROOT / "results" / f"loop5_{a.tag}"
    rows = load(d / "episodes.jsonl")
    scen = {}
    for pat in a.scenarios:
        for p in glob.glob(str(ROOT / pat)):
            s = json.loads(Path(p).read_text())
            scen[s["scenario_id"]] = s
    todo = [r for r in rows if missing_turn(r) and (not a.models or r["model"] in a.models)]
    print(f"{len(rows)} episodes; {len(todo)} with an empty turn"
          + (f" for {a.models}" if a.models else "") + f"; re-running with >= {a.min_tokens} tokens")
    if not todo:
        return
    # runner settings for this tag
    m.TOOL_MODE = True
    m.SUBJECT_REASONING = a.reasoning
    m.ARM = a.arm or todo[0].get("arm", "base")
    m.D1_JUDGE = a.d1_judge
    orig_call = m.call

    async def big_call(msgs, model, sem, max_tokens, temperature=1.0):
        return await orig_call(msgs, model, sem, max(max_tokens, a.min_tokens), temperature)
    m.call = big_call

    sem = asyncio.Semaphore(a.conc)
    by_row = {key(r): i for i, r in enumerate(rows)}
    refilled, still = [], []
    for sid in sorted({r["scenario"] for r in todo}):
        s = scen[sid]
        rs = [r for r in todo if r["scenario"] == sid]
        m.MAX_TURN = 4 if any("t4_user" in r for r in rows if r["scenario"] == sid) else 3
        new = await asyncio.gather(*(m.episode(s, r["condition"], r["model"], r["episode"], sem) for r in rs))
        ok = [r for r in new if not missing_turn(r)]
        still += [key(r) for r in new if missing_turn(r)]
        for r in ok:
            rows[by_row[key(r)]] = r
        print(f"  {sid:24s} {len(ok)}/{len(rs)} complete after refill  (turns {m.MAX_TURN})", flush=True)
        if ok:
            keys = {key(r) for r in ok}
            for name in SCORE_FILES:               # drop stale score rows for these episodes
                p = d / f"{name}.jsonl"
                if p.exists():
                    keep = [x for x in load(p) if not (x.get("condition") and key(x) in keys)]
                    p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in keep))
            await m.score(s, ok, a.reader, a.judge, a.k, sem, d)
            refilled += ok
    (d / "episodes.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(f"\nrefilled {len(refilled)} episodes; still incomplete: {len(still)} {still[:6]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--scenarios", nargs="+", default=["data/scenarios_v6/*.json", "data/scenarios_v4/*.json"])
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--min-tokens", type=int, default=9000)
    ap.add_argument("--reasoning", choices=["on", "off"], default="on")
    ap.add_argument("--arm", default=None)
    ap.add_argument("--reader", default="qwen37plus")
    ap.add_argument("--judge", default="qwen37plus")
    ap.add_argument("--d1-judge", default="haiku45")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--conc", type=int, default=6)
    asyncio.run(main(ap.parse_args()))
