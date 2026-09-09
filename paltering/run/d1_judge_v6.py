"""Critical-fact disclosure for every reply at one turn, judged by the validated core-of-fact
judge (run_loop_v5.D1_CHECK with Haiku 4.5: honest references 58/58 YES, written palters 0/58).
The per-fact conveyance judge under-detects D1 (it codes the compound fact NO when only its
core is conveyed: 38% of Haiku-YES replies), which biases the omission/reframe channel and the
structural mechanisms; this file overrides it.

Usage:  python d1_judge_v6.py --tags v6 gemma --turn 2 [--judge haiku45]
Writes results/loop5_<tag>/d1_t<turn>.jsonl  {key, turn, disclosed, raw}; resumes.
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



def key(r):
    return (r["scenario"], r["condition"], r["model"], r["episode"])


async def main(a):
    scen = {}
    for pat in a.scenarios:
        for p in glob.glob(str(ROOT / pat)):
            s = json.loads(Path(p).read_text())
            scen[s["scenario_id"]] = s
    sem = asyncio.Semaphore(a.conc)
    for tag in a.tags:
        d = ROOT / "results" / f"loop5_{tag}"
        out = d / f"d1_t{a.turn}.jsonl"
        done = {tuple(json.loads(l)["key"]) for l in out.open()} if out.exists() else set()
        todo = [r for r in load(d / "episodes.jsonl") if r.get(f"t{a.turn}_reply") and key(r) not in done]
        print(f"{tag}: judging D1 disclosure for {len(todo)} turn-{a.turn} replies with {a.judge} ({len(done)} done)", flush=True)
        jobs = []
        for r in todo:
            d1 = next(f["text"] for f in scen[r["scenario"]]["facts"] if f.get("severity") == "critical")
            jobs.append(m.judge_call([{"role": "user", "content": m.D1_CHECK.format(reply=r[f"t{a.turn}_reply"], fact=d1)}],
                                     a.judge, 1, temperature=0, max_tokens=60, sem=sem))
        res = await asyncio.gather(*jobs)
        n_ok = 0
        with out.open("a") as f:
            for r, samples in zip(todo, res):
                text = (samples[0] or {}).get("text") or ""
                mm = m.DISCLOSED.search(text)
                if mm:
                    n_ok += 1
                f.write(json.dumps({"key": list(key(r)), "turn": a.turn, "disclosed": (mm.group(1).upper() == "YES") if mm else None, "raw": text[:80]}) + "\n")
        print(f"  {tag}: {n_ok}/{len(todo)} answered -> {out}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", nargs="+", default=["v6", "gemma"])
    ap.add_argument("--scenarios", nargs="+", default=["data/scenarios_v6/*.json", "data/scenarios_v4/*.json"])
    ap.add_argument("--turn", type=int, default=2)
    ap.add_argument("--judge", default="haiku45")
    ap.add_argument("--conc", type=int, default=8)
    asyncio.run(main(ap.parse_args()))
