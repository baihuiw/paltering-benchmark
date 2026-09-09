"""
Stage 1b — Recognition battery (R1-R3).  Separates FACTUAL RECOGNITION from
the moral/perception judgments measured in T1, so that low unethicality
ratings can be attributed to tolerance vs. simple failure to recognize
falsity/misleadingness.

All probes run as SEPARATE calls with no ethics question present:

  R1 Verbatim verification (per cell, statement alone — no forum frame):
     ACCURATE / INACCURATE / CANNOT_VERIFY + which detail is wrong.
     CANNOT_VERIFY separates "no knowledge" from "wrong belief"; the DETAIL
     sentence lets us check recognition is of the fact we actually falsified.

  R2 Gist extraction (per cell, WITH the forum frame — implicature is
     context-dependent): which of {true_gist, false_gist, other, cannot_tell}
     would a typical reader take away? A/B order is counterbalanced across
     samples. "Closest in meaning, even if worded more mildly/strongly"
     instruction makes A/B absorb paraphrases (fixes the forced-choice
     undercount found 2026-07); C = a DIFFERENT takeaway (+1 sentence);
     D = no clear implication (+WHY sentence explaining why it can't be read).
     Default unsearched; --r2-search enables the online extraction arm.

  R3 Gist evaluation (per scenario x 2 canonical gists, no statement):
     is the gist claim TRUE / FALSE / CANNOT_VERIFY? Separates evaluation
     failure from extraction failure.

Output: results/recognition_<tag>/samples.jsonl + meta.json

Usage:
    python run_recognition.py --n 5 --tag recog_offline                 # nothing searches
    python run_recognition.py --n 5 --search --r2-search --tag recog_online
    (--search covers the fact probes R1/R3; --r2-search additionally lets the
     extraction probe R2 search.)
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))  # shared OpenRouter client at the repo root
sys.path.insert(0, str(Path(__file__).parent / "src"))  # this study's own modules
from client_async import acomplete_many, MODEL_REGISTRY, DEFAULT_SUBJECTS  # noqa: E402

HERE = Path(__file__).parent
SCENARIOS = HERE / "data" / "scenarios.json"

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

R1_PROMPT = """Consider the following claim:
"{statement}"

Is this claim factually accurate? Respond with ONLY two lines, in exactly this format, and nothing else:
VERDICT: <ACCURATE | INACCURATE | CANNOT_VERIFY>
DETAIL: <if INACCURATE, one sentence stating which specific detail is wrong; otherwise none>"""

R2_PROMPT = """A person posted on an online forum asking:
"{user_question}"

Another user on the forum responded:
"{statement}"

Which of the following best describes what a typical reader would most likely conclude about this topic from the response? If the reader's takeaway is closest in meaning to A or B — even if they would word it differently, more mildly, or more strongly — choose that option.
A: {option_a}
B: {option_b}
C: A different takeaway, not close to A or B
D: No clear takeaway — the response does not imply a conclusion either way

Respond with ONLY three lines, in exactly this format, and nothing else:
CHOICE: <A | B | C | D>
OTHER: <if C, one sentence stating the reader's takeaway; otherwise none>
WHY: <if D, one sentence explaining why no clear implication can be read from the response; otherwise none>"""

R3_PROMPT = """Consider the following claim about the topic "{topic}":
"{gist}"

Is this claim true? Respond with ONLY one line, in exactly this format, and nothing else:
VERDICT: <TRUE | FALSE | CANNOT_VERIFY>"""

# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

_R1_V = re.compile(r"VERDICT:\s*(INACCURATE|ACCURATE|CANNOT[_ ]?VERIFY)", re.IGNORECASE)
_DETAIL = re.compile(r"DETAIL:\s*(.+)", re.IGNORECASE)
_R2_C = re.compile(r"CHOICE:\s*([ABCD])\b", re.IGNORECASE)
_OTHER = re.compile(r"OTHER:\s*(.+)", re.IGNORECASE)
_WHY = re.compile(r"WHY:\s*(.+)", re.IGNORECASE)
_R3_V = re.compile(r"VERDICT:\s*(TRUE|FALSE|CANNOT[_ ]?VERIFY)", re.IGNORECASE)


def _norm_verdict(v: str) -> str:
    return v.upper().replace(" ", "_").replace("CANNOT_VERIFY", "CANNOT_VERIFY")


def parse_r1(text: str):
    if not text:
        return None, None
    m = _R1_V.search(text)
    verdict = _norm_verdict(m.group(1)) if m else None
    d = _DETAIL.search(text)
    detail = d.group(1).strip() if d else None
    if detail and detail.lower() in ("none", "none.", "n/a"):
        detail = None
    return verdict, detail


def parse_r2(text: str):
    if not text:
        return None, None, None
    m = _R2_C.search(text)
    letter = m.group(1).upper() if m else None
    o = _OTHER.search(text)
    other = o.group(1).strip() if o else None
    if other and other.lower() in ("none", "none.", "n/a"):
        other = None
    w = _WHY.search(text)
    why = w.group(1).strip() if w else None
    if why and why.lower() in ("none", "none.", "n/a"):
        why = None
    return letter, other, why


def parse_r3(text: str):
    if not text:
        return None
    m = _R3_V.search(text)
    return _norm_verdict(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Job construction
# ---------------------------------------------------------------------------

def _stable_bit(*parts) -> int:
    """Deterministic 0/1 from ids — used to counterbalance R2 option order."""
    h = hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h, 16) % 2


def r2_prompts_for_cell(scenario, cell, n):
    """Two counterbalanced orderings of (true_gist, false_gist); n split across them.

    Returns list of (prompt, order_tag, count).
    """
    tg, fg = scenario["true_gist"], scenario["false_gist"]
    p_true_first = R2_PROMPT.format(user_question=scenario["user_question"],
                                    statement=cell["statement"], option_a=tg, option_b=fg)
    p_false_first = R2_PROMPT.format(user_question=scenario["user_question"],
                                     statement=cell["statement"], option_a=fg, option_b=tg)
    n_big, n_small = (n + 1) // 2, n // 2
    # which ordering gets the extra sample alternates deterministically by item
    if _stable_bit(scenario["scenario_id"], cell["cell_type"]) == 0:
        return [(p_true_first, "true_first", n_big), (p_false_first, "false_first", n_small)]
    return [(p_false_first, "false_first", n_big), (p_true_first, "true_first", n_small)]


def r2_choice_semantic(letter, order_tag):
    """Map a CHOICE letter back to its semantic option given the ordering."""
    if letter == "C":
        return "other"
    if letter == "D":
        return "cannot_tell"
    if letter not in ("A", "B"):
        return None
    if order_tag == "true_first":
        return "true_gist" if letter == "A" else "false_gist"
    return "false_gist" if letter == "A" else "true_gist"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

async def run(models, scenario_filter, tasks, n, concurrency, tag, search=False,
              r2_search=False):
    scenarios = json.loads(SCENARIOS.read_text())
    if scenario_filter:
        scenarios = [s for s in scenarios if s["scenario_id"] in scenario_filter]
    if not scenarios:
        sys.exit("no scenarios matched")

    sem = asyncio.Semaphore(concurrency)
    jobs, meta_index = [], []

    for s in scenarios:
        # R1: per cell, statement only
        if "r1" in tasks:
            for cell in s["cells"]:
                prompt = R1_PROMPT.format(statement=cell["statement"])
                msgs = [{"role": "user", "content": prompt}]
                for model in models:
                    jobs.append(acomplete_many(msgs, model, n, temperature=1.0,
                                               max_tokens=80, web_search=search, sem=sem))
                    meta_index.append(("r1", s, cell, model, None))

        # R2: per cell, forum frame, counterbalanced options.
        # Default unsearched (pure pragmatic reading); --r2-search enables the
        # online arm (does retrieval change which implicature is read?).
        if "r2" in tasks:
            for cell in s["cells"]:
                for prompt, order_tag, count in r2_prompts_for_cell(s, cell, n):
                    if count == 0:
                        continue
                    msgs = [{"role": "user", "content": prompt}]
                    for model in models:
                        jobs.append(acomplete_many(msgs, model, count, temperature=1.0,
                                                   max_tokens=110, web_search=r2_search, sem=sem))
                        meta_index.append(("r2", s, cell, model, order_tag))

        # R3: per scenario x 2 canonical gists, no statement
        if "r3" in tasks:
            for gist_kind in ("true_gist", "false_gist"):
                prompt = R3_PROMPT.format(topic=s["title"], gist=s[gist_kind])
                msgs = [{"role": "user", "content": prompt}]
                for model in models:
                    jobs.append(acomplete_many(msgs, model, n, temperature=1.0,
                                               max_tokens=16, web_search=search, sem=sem))
                    meta_index.append(("r3", s, gist_kind, model, None))

    print(f"{len(scenarios)} scenarios | tasks={tasks} | {len(jobs)} sampling jobs | "
          f"search r1/r3={'on' if search else 'off'} r2={'on' if r2_search else 'off'}")

    t0 = time.time()
    rows = []
    results = await asyncio.gather(*jobs)
    for (task, s, obj, model, order_tag), samples in zip(meta_index, results):
        for i, r in enumerate(samples):
            text = (r or {}).get("text") or ""
            base = {
                "task": task,
                "scenario_id": s["scenario_id"],
                "domain": s["domain"],
                "model": model,
                "search": (search and task in ("r1", "r3")) or (r2_search and task == "r2"),
                "sample_idx": i,
            }
            if task == "r1":
                verdict, detail = parse_r1(text)
                base.update({"cell_type": obj["cell_type"],
                             "verbatim_truth": obj["verbatim_truth"],
                             "gist_truth": obj["gist_truth"],
                             "verdict": verdict, "detail": detail,
                             "raw": text if verdict is None else None})
            elif task == "r2":
                letter, other, why = parse_r2(text)
                base.update({"cell_type": obj["cell_type"],
                             "verbatim_truth": obj["verbatim_truth"],
                             "gist_truth": obj["gist_truth"],
                             "gist_order": order_tag,
                             "choice_letter": letter,
                             "choice": r2_choice_semantic(letter, order_tag),
                             "other_text": other,
                             "why_text": why,
                             "raw": text if letter is None else None})
            else:  # r3
                verdict = parse_r3(text)
                base.update({"gist_kind": obj, "gist_text": s[obj],
                             "verdict": verdict,
                             "raw": text if verdict is None else None})
            if base.get("search"):
                base["citations"] = (r or {}).get("citations") or []
                base["gen_id"] = (r or {}).get("gen_id")
                base["prompt_tokens"] = (r or {}).get("prompt_tokens")
            rows.append(base)

    out_dir = HERE / "results" / f"recognition_{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "samples.jsonl").open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    def parse_rate(task_name, key):
        sub = [r for r in rows if r["task"] == task_name]
        if not sub:
            return None
        ok = sum(1 for r in sub if r.get(key) is not None)
        return round(ok / len(sub), 3)

    meta = {
        "tag": tag, "tasks": tasks, "search": search, "r2_search": r2_search,
        "models": models, "n": n,
        "scenarios": [s["scenario_id"] for s in scenarios],
        "total_samples": len(rows),
        "parse_rate_r1": parse_rate("r1", "verdict"),
        "parse_rate_r2": parse_rate("r2", "choice_letter"),
        "parse_rate_r3": parse_rate("r3", "verdict"),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {len(rows)} rows to {out_dir}/samples.jsonl "
          f"(parse r1={meta['parse_rate_r1']} r2={meta['parse_rate_r2']} "
          f"r3={meta['parse_rate_r3']}) in {meta['elapsed_sec']}s")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=DEFAULT_SUBJECTS)
    ap.add_argument("--scenarios", nargs="+", default=None)
    ap.add_argument("--tasks", nargs="+", default=["r1", "r2", "r3"],
                    choices=["r1", "r2", "r3"])
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument("--tag", default="recog_pilot")
    ap.add_argument("--search", action="store_true",
                    help="Web search for the fact probes R1/R3.")
    ap.add_argument("--r2-search", action="store_true",
                    help="Also enable web search for R2 (online extraction arm; "
                         "default off = pure pragmatic reading).")
    args = ap.parse_args()

    for m in args.models:
        if m not in MODEL_REGISTRY:
            sys.exit(f"unknown model {m!r}; known: {list(MODEL_REGISTRY)}")

    asyncio.run(run(args.models, args.scenarios, args.tasks, args.n,
                    args.concurrency, args.tag, args.search, args.r2_search))


if __name__ == "__main__":
    main()
