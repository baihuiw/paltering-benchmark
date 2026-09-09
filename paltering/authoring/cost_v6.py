"""Cost projection for the v6 full run, from measured smoke-run token counts and live
OpenRouter prices. Hidden reasoning tokens are not visible in stored outputs; a contingency
is added on subject output.

Usage:  python cost_v6.py [--smoke loop5_smoke_v6]
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import argparse
import json
import sys
import urllib.request
from pathlib import Path

from client_async import MODEL_REGISTRY  # noqa: E402

CONTINGENCY = 1.25          # hidden reasoning tokens on subject output


def prices():
    data = json.load(urllib.request.urlopen("https://openrouter.ai/api/v1/models"))["data"]
    return {m["id"]: (float(m["pricing"]["prompt"]) * 1e6, float(m["pricing"]["completion"]) * 1e6) for m in data}


def episode_tokens(rows, model, turns):
    """(input, output) tokens per episode for the first `turns` turns, chars/4, averaged over rows."""
    ins, outs = [], []
    for r in (x for x in rows if x["model"] == model):
        hist = inp = out = 0
        for t in range(1, turns + 1):
            u, o = r.get(f"t{t}_user") or "", r.get(f"t{t}_output") or ""
            inp += (hist + len(u)) / 4
            hist += len(u) + len(o)
            out += len(o) / 4
        ins.append(inp)
        outs.append(out)
    return (sum(ins) / len(ins), sum(outs) / len(outs)) if ins else (None, None)


def scoring_tokens(turns, k):
    """Approximate judge/reader tokens per episode (qwen), plus the haiku D1 check (4-turn only)."""
    q_in = q_out = 0
    for t in range(1, turns + 1):
        q_in += k * 900 + 20 * 0; q_out += k * 20                # readers
        q_in += 1200; q_out += 120                                # per-fact conveyance judge
        if t >= 2:
            q_in += 2500 + 1500 * t; q_out += 200                 # false-claim judge sees facts + transcript so far
        if t in (2, 4):
            q_in += 6 * 700 + 1500; q_out += 6 * 250 + 400        # 6 tactic probes + scratchpad audit
        if t == 3:
            q_in += 900; q_out += 200                             # point-blank stance judge
    return q_in, q_out


def main(a):
    P = prices()
    rows = [json.loads(l) for l in (ROOT / "pilots/04_loop_v4_v5" / "results" / a.smoke / "episodes.jsonl").read_text().splitlines()]
    main_models = ["sonnet5", "gpt56luna", "gemini38flash", "deepseekv4pro", "kimik3"]
    cont_models = ["gpt56sol", "gemini35flash"]
    qin, qout = P[MODEL_REGISTRY["qwen37plus"]["slug"]]
    hin, hout = P[MODEL_REGISTRY["haiku45"]["slug"]]
    print(f"prices $/M (in/out): " + "  ".join(f"{m} {P[MODEL_REGISTRY[m]['slug']][0]:.2f}/{P[MODEL_REGISTRY[m]['slug']][1]:.2f}"
                                             for m in main_models + cont_models + ["qwen37plus", "haiku45"]))

    def ep_cost(model, turns, k=3):
        proxy = model if any(r["model"] == model for r in rows) else {"gpt56sol": "sonnet5", "gemini35flash": "gemini38flash"}[model]
        ti, to = episode_tokens(rows, proxy, turns)
        pin, pout = P[MODEL_REGISTRY[model]["slug"]]
        subj = (ti * pin + to * CONTINGENCY * pout) / 1e6
        si, so = scoring_tokens(turns, k)
        score = (si * qin + so * qout) / 1e6 + ((700 * hin + 20 * hout) / 1e6 if turns == 4 else 0)
        return subj, score

    print(f"\nper-episode cost (subject + scoring), 4 turns / 3 turns:")
    for m in main_models + cont_models:
        s4, c4 = ep_cost(m, 4)
        s3, c3 = ep_cost(m, 3)
        print(f"  {m:14s} 4t ${s4:.3f}+${c4:.3f}   3t ${s3:.3f}+${c3:.3f}")

    n = 4
    stages = [
        ("main-t4   15 scen x 3 conds x 5 models x n=4, 4 turns", 15 * 3 * n, main_models, 4),
        ("main      48 scen x 3 conds x 5 models x n=4, 3 turns", 48 * 3 * n, main_models, 3),
        ("continuity 10 scen x 3 conds x 2 models, 3 turns", 10 * 3 * n, cont_models, 3),
        ("honesty   20 scen x C3 x 5 models, 3 turns", 20 * 1 * n, main_models, 3),
        ("goal      20 scen x C1,C3 x 5 models, 3 turns", 20 * 2 * n, main_models, 3),
        ("assisted  20 scen x 3 conds x 5 models, 3 turns", 20 * 3 * n, main_models, 3),
        ("noreason  20 scen x 3 conds x 5 models, 3 turns (output ~halved: no hidden reasoning)", 20 * 3 * n, main_models, 3),
    ]
    print("\nstage totals:")
    grand = 0
    for label, per_model_eps, models, turns in stages:
        tot = 0
        for m in models:
            s, c = ep_cost(m, turns)
            if label.startswith("noreason"):
                s = s / CONTINGENCY
            tot += per_model_eps * (s + c)
        grand += tot
        print(f"  {label:78s} ${tot:7.0f}")
    print(f"  {'TOTAL':78s} ${grand:7.0f}   (main run only: ${sum(sum(per * sum(ep_cost(m, t)) for m in ms) for _, per, ms, t in stages[:2]):.0f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", default="loop5_smoke_v6")
    main(ap.parse_args())
