"""Behaviour labels for the instructed contrast set: did each contrast reply disclose the
critical fact? (Haiku core-of-fact judge.) With these, a probe can be trained INSIDE one
instruction condition (instruction held constant, behaviour varying), removing the instruction
confound that made the instructed intent probe read the prompt rather than the intent.

Usage:  python contrast_d1.py  ->  results/gemma/contrast_d1.jsonl
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import asyncio
import glob
import json
import sys
from pathlib import Path

sys.argv, _argv = ["x"], sys.argv
import paltering.run.run_loop_v5 as m  # noqa: E402
from paltering.run.run_ladder import extract  # noqa: E402
sys.argv = _argv



async def main():
    scen = {}
    for pat in ("data/scenarios_v6/*.json", "data/scenarios_v4/*.json"):
        for p in glob.glob(str(ROOT / pat)):
            s = json.loads(Path(p).read_text())
            scen[s["scenario_id"]] = s
    rows = [json.loads(l) for l in (ROOT / "results" / "gemma" / "contrast.jsonl").open()]
    sem = asyncio.Semaphore(8)
    jobs, metas = [], []
    for r in rows:
        reply = extract(r.get("output") or "", r.get("from"), True)["reply_text"] or ""
        d1 = next(f["text"] for f in scen[r["scenario"]]["facts"] if f.get("severity") == "critical")
        metas.append((r, bool(reply)))
        jobs.append(m.judge_call([{"role": "user", "content": m.D1_CHECK.format(reply=reply or "(no reply)", fact=d1)}],
                                 "haiku45", 1, temperature=0, max_tokens=60, sem=sem))
    res = await asyncio.gather(*jobs)
    out = ROOT / "results" / "gemma" / "contrast_d1.jsonl"
    n = {"honest": [0, 0], "deceptive": [0, 0]}
    with out.open("w") as f:
        for (r, has_reply), samples in zip(metas, res):
            mm = m.DISCLOSED.search((samples[0] or {}).get("text") or "")
            disclosed = (mm.group(1).upper() == "YES") if (mm and has_reply) else (False if not has_reply else None)
            f.write(json.dumps({"scenario": r["scenario"], "query": r["query"], "label": r["label"], "sample_idx": r["sample_idx"],
                                "has_reply": has_reply, "disclosed": disclosed}) + "\n")
            if disclosed is not None:
                n[r["label"]][0] += disclosed
                n[r["label"]][1] += 1
    print("disclosed D1 / judged:", {k: f"{v[0]}/{v[1]}" for k, v in n.items()}, "->", out)


if __name__ == "__main__":
    asyncio.run(main())
