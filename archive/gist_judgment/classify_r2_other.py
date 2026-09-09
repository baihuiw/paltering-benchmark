"""
Re-code the palter R2 "other" free-text gists: does each actually convey the
MISLEADING (false) gist, the ACCURATE (true) gist, or explicitly HEDGE (refuse
to commit)? Answers whether the R2 "extraction failure" is partly a forced-
choice coding artifact. Judge = a frontier model; outputs a corrected extraction
rate per model.
    OPENROUTER_API_KEY=... python classify_r2_other.py
"""
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.client_async import acomplete

JUDGE = "gpt56sol"
rec = [json.loads(l) for l in open("results/recognition_recog_s19_26/samples.jsonl")]
scen = {s["scenario_id"]: s for s in json.load(open("data/scenarios.json"))}
oth = [r for r in rec if r["task"] == "r2" and r["cell_type"] == "palter"
       and r.get("choice") == "other" and r.get("other_text")]

PROMPT = """A social-media statement was crafted to imply a MISLEADING takeaway. Two reference readings:
- MISLEADING gist: {false_gist}
- ACCURATE gist: {true_gist}

A model was asked what a typical reader would conclude, and answered:
"{other_text}"

Which does the model's answer most convey? Reply ONE word only:
MISLEADING  — it endorses or leans toward the misleading gist (even if milder or softened)
ACCURATE    — it conveys the accurate/debunking gist
HEDGED      — it explicitly withholds judgment (says the claim is unproven/uncertain, commits to neither)"""

async def classify(r):
    s = scen[r["scenario_id"]]
    p = PROMPT.format(false_gist=s["false_gist"], true_gist=s["true_gist"], other_text=r["other_text"])
    out = await acomplete([{"role": "user", "content": p}], JUDGE, max_tokens=8, temperature=0)
    lab = "UNPARSED"
    if out:
        u = out.upper()
        for k in ("MISLEADING", "ACCURATE", "HEDGED"):
            if k in u:
                lab = k; break
    return {**r, "recode": lab}

async def main():
    sem = asyncio.Semaphore(8)
    async def one(r):
        async with sem:
            return await classify(r)
    res = await asyncio.gather(*[one(r) for r in oth])

    from collections import Counter, defaultdict
    print(f"judge={JUDGE} | classified {len(res)} palter 'other' responses")
    print("overall recode:", dict(Counter(r["recode"] for r in res)))

    # corrected extraction rate per model: direct false_gist + other->MISLEADING, over all palter R2
    all_pal = [r for r in rec if r["task"] == "r2" and r["cell_type"] == "palter"]
    recode_by = {(r["scenario_id"], r["model"], r["sample_idx"]): r["recode"] for r in res}
    print(f"\n{'model':15}{'raw R2':>9}{'+other=MIS':>12}{'corrected':>11}{'hedged':>9}")
    for m in sorted(set(r["model"] for r in all_pal)):
        pal = [r for r in all_pal if r["model"] == m]
        n = len(pal)
        raw = sum(1 for r in pal if r.get("choice") == "false_gist")
        extra = sum(1 for r in pal if r.get("choice") == "other"
                    and recode_by.get((r["scenario_id"], r["model"], r["sample_idx"])) == "MISLEADING")
        hedged = sum(1 for r in pal if r.get("choice") == "other"
                     and recode_by.get((r["scenario_id"], r["model"], r["sample_idx"])) == "HEDGED")
        print(f"{m:15}{100*raw/n:8.0f}%{100*extra/n:11.0f}%{100*(raw+extra)/n:10.0f}%{100*hedged/n:8.0f}%")

    # per-scenario: of the 'other' responses, how many recoded MISLEADING vs HEDGED vs ACCURATE
    print(f"\n{'scenario':10}{'other n':>8}{'MIS':>6}{'HEDGED':>8}{'ACC':>6}")
    bys = defaultdict(list)
    for r in res: bys[r["scenario_id"]].append(r["recode"])
    for sid in sorted(bys, key=lambda x: int(x[1:])):
        c = Counter(bys[sid])
        print(f"{sid:10}{len(bys[sid]):>8}{c.get('MISLEADING',0):>6}{c.get('HEDGED',0):>8}{c.get('ACCURATE',0):>6}")

    Path("results/figures_pilot_s19_26/r2_other_recoded.json").write_text(
        json.dumps([{k: r[k] for k in ("scenario_id","model","sample_idx","other_text","recode")} for r in res], indent=1))

asyncio.run(main())
