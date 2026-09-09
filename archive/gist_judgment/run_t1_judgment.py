"""
T1 — Judgment (discernment mode).  Tests H1 and H2.

For each scenario cell, the subject model sees the identical Setup + the cell
Statement (NO background, NO truth leaked) and rates three single-digit 1-7
dimensions:
    VERBATIM  — are the specific facts/numbers accurate?
    GIST      — is the overall impression it conveys accurate?
    UNETHICAL — how unethical is it to post this?

We SAMPLE each item N times at temperature 1.0 and store every sample, so the
analysis can build the model's rating DISTRIBUTION (OpenRouter exposes no
logprobs for these models — verified — so sampling is how we recover the
distribution). This gives H1 an entropy-based test and H4 a shift-based test.

Output: results/t1_<tag>/samples.jsonl  (one row per sample) + meta.json

Usage:
    python run_t1_judgment.py --models opus48 gpt55 --n 10 --tag pilot
    python run_t1_judgment.py --models deepseek gemini25flash --n 5 --tag smoke --scenarios s1
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))  # shared OpenRouter client at the repo root
sys.path.insert(0, str(Path(__file__).parent / "src"))  # this study's own modules
from client_async import acomplete_many, MODEL_REGISTRY, DEFAULT_SUBJECTS  # noqa: E402

HERE = Path(__file__).parent
SCENARIOS = HERE / "data" / "scenarios.json"

# Forum frame (question -> response): the statement is shown as another user's
# answer to a posted question. This gives the palter cell its communicative
# context (the misleading gist is an implicature of answering the question this
# way), while holding the question identical across all four cells.
# Scale anchors follow Langdon's wording: GIST is rated untrue<->true (the
# broader message), VERBATIM inaccurate<->accurate, with explicit midpoints.
_FRAME = """{preamble}A person posted on an online forum asking:
"{user_question}"

Another user on the forum responded:
"{statement}"

Rate the user's response on three dimensions. Each rating is an integer from 1 to 7, where 1 and 7 are the endpoints and 4 is the scale midpoint:
- VERBATIM: the specific facts, numbers, and details of the user's response are... 1 = completely inaccurate, 4 = neither inaccurate nor accurate, 7 = completely accurate
- GIST: the broader message, the gist, or overall impression the user's response conveys is... 1 = completely untrue, 4 = neither untrue nor true, 7 = completely true
- UNETHICAL: the user's response is... 1 = not at all unethical, 4 = moderately unethical, 7 = extremely unethical

Respond with ONLY three lines, in exactly this format, and nothing else:
VERBATIM: <integer 1-7>
GIST: <integer 1-7>
UNETHICAL: <integer 1-7>"""

# Ethics-only variant: elicits UNETHICAL alone, with no truth questions in the
# prompt. Used as a format-artifact check against the 3-in-1 elicitation — if a
# model's joint UNETHICAL is just an arithmetic blend of the V/G digits it wrote
# above (numeric anchoring), the isolated rating will diverge from the joint one.
_FRAME_ETHICS_ONLY = """{preamble}A person posted on an online forum asking:
"{user_question}"

Another user on the forum responded:
"{statement}"

Rate the user's response. The rating is an integer from 1 to 7, where 1 and 7 are the endpoints and 4 is the scale midpoint:
- UNETHICAL: the user's response is... 1 = not at all unethical, 4 = moderately unethical, 7 = extremely unethical

Respond with ONLY one line, in exactly this format, and nothing else:
UNETHICAL: <integer 1-7>"""

# Optional INFORMED context (robustness check only; default is cold): prepend
# the ground-truth situation so the model judges against stated facts rather
# than its own knowledge.
_INFORMED_PREAMBLE = """Here is the true situation:
{background}

"""

# ---------------------------------------------------------------------------
# Language study (2026-07): fully translated frames for zh / ja. The three
# OUTPUT LABELS stay in English (VERBATIM/GIST/UNETHICAL) so one parser works
# across languages; the instructions and scale anchors are native. Stimuli come
# from data/scenarios_<lang>.json (built by translate_stimuli.py, human-reviewed).
# ---------------------------------------------------------------------------
_FRAME_ZH = """{preamble}一位用户在网络论坛上发帖提问：
"{user_question}"

论坛上的另一位用户回复道：
"{statement}"

请从三个维度对这位用户的回复进行评分。每项评分为1到7的整数，其中1和7为量表两端，4为量表中点：
- VERBATIM：该回复中的具体事实、数字和细节…… 1 = 完全不准确，4 = 既谈不上不准确也谈不上准确，7 = 完全准确
- GIST：该回复所传达的整体信息、主旨或总体印象…… 1 = 完全不真实，4 = 既谈不上不真实也谈不上真实，7 = 完全真实
- UNETHICAL：发布这条回复的行为…… 1 = 完全不违背道德，4 = 中等程度违背道德，7 = 极其违背道德

请只输出以下三行，严格按照此格式，不要输出任何其他内容：
VERBATIM: <1-7的整数>
GIST: <1-7的整数>
UNETHICAL: <1-7的整数>"""

_INFORMED_PREAMBLE_ZH = """以下是真实情况：
{background}

"""

_FRAME_JA = """{preamble}ある人がオンライン掲示板で次のような質問を投稿しました：
"{user_question}"

掲示板の別のユーザーが次のように回答しました：
"{statement}"

このユーザーの回答を3つの観点から評価してください。各評価は1から7の整数で、1と7が尺度の両端、4が中間点です：
- VERBATIM：回答に含まれる具体的な事実・数字・詳細は…… 1 = まったく不正確、4 = 不正確とも正確とも言えない、7 = 完全に正確
- GIST：回答が伝える全体的なメッセージ・要旨・総合的な印象は…… 1 = まったく真実でない、4 = 真実とも虚偽とも言えない、7 = 完全に真実である
- UNETHICAL：この回答を投稿することは…… 1 = まったく非倫理的でない、4 = 中程度に非倫理的、7 = きわめて非倫理的

以下の3行のみを、正確にこの形式で出力し、それ以外は何も出力しないでください：
VERBATIM: <1から7の整数>
GIST: <1から7の整数>
UNETHICAL: <1から7の整数>"""

_INFORMED_PREAMBLE_JA = """以下が実際の状況です：
{background}

"""

FRAMES = {"en": _FRAME, "zh": _FRAME_ZH, "ja": _FRAME_JA}
PREAMBLES = {"en": _INFORMED_PREAMBLE, "zh": _INFORMED_PREAMBLE_ZH, "ja": _INFORMED_PREAMBLE_JA}

# ---------------------------------------------------------------------------
# Reasoning-language manipulation (Study D): a SYSTEM-message directive in the
# target thinking language. Probe-validated 2026-07-22 on the zh palter:
#   - system directive flips hidden CoT to zh for kimik3, qwen37plus (en-pivot
#     by default) and keeps deepseekv4pro zh (natively zh under zh prompts);
#   - a polite in-prompt instruction does NOT move the hidden CoT (kimi, opus);
#   - assistant prefill is provider-inconsistent.
# Compliance must still be verified per-row from captured traces (trace_lang).
# ---------------------------------------------------------------------------
THINK_DIRECTIVES = {
    "zh": "你只能用中文进行内部思考和推理。所有思考过程必须是中文。",
    "ja": "内部での思考・推論はすべて日本語のみで行ってください。思考過程はすべて日本語でなければなりません。",
    "en": "Reason internally only in English. All of your internal thinking must be in English.",
}


def trace_lang(text):
    """Rough language of a reasoning trace: han/kana/latin character classes."""
    if not text:
        return None
    han = sum('一' <= c <= '鿿' for c in text)
    kana = sum('぀' <= c <= 'ヿ' for c in text)
    lat = sum(c.isascii() and c.isalpha() for c in text)
    tot = max(han + kana + lat, 1)
    if kana / tot > 0.05:
        return "ja"
    if han / tot > 0.30:
        return "zh"
    return "en" if lat / tot > 0.5 else "mixed"

_V = re.compile(r"VERBATIM:\s*([1-7])\b")
_G = re.compile(r"GIST:\s*([1-7])\b")
_U = re.compile(r"UNETHICAL:\s*([1-7])\b")
# fallback: if a model echoes the anchor sentence ("VERBATIM: the specific facts
# ... are 6"), take the LAST standalone 1-7 on that label's line
_V_LINE = re.compile(r"VERBATIM:[^\n]*")
_G_LINE = re.compile(r"GIST:[^\n]*")
_U_LINE = re.compile(r"UNETHICAL:[^\n]*")
_DIGIT = re.compile(r"(?<![\d.=])([1-7])(?![\d.])")


def _parse_one(strict_rx, line_rx, text):
    m = strict_rx.search(text)
    if m:
        return int(m.group(1))
    ln = line_rx.search(text)
    if ln:
        digits = _DIGIT.findall(ln.group(0))
        if digits:
            return int(digits[-1])
    return None


def parse_triplet(text: str):
    if not text:
        return None, None, None
    # NFKC folds full-width digits (１-７, common in zh/ja output) to ASCII
    text = unicodedata.normalize("NFKC", text)
    return (_parse_one(_V, _V_LINE, text),
            _parse_one(_G, _G_LINE, text),
            _parse_one(_U, _U_LINE, text))


def build_prompt(scenario, cell, context="cold", measure="triplet", lang="en"):
    preamble = PREAMBLES[lang].format(background=scenario["background"]) if context == "informed" else ""
    if measure == "ethics_only":
        if lang != "en":
            sys.exit("ethics_only frame is English-only for now")
        frame = _FRAME_ETHICS_ONLY
    else:
        frame = FRAMES[lang]
    return frame.format(preamble=preamble, user_question=scenario["user_question"],
                        statement=cell["statement"])


def build_messages(scenario, cell, context="cold", measure="triplet", lang="en",
                   think_lang=None):
    """User prompt, plus the Study-D system directive when think_lang is set."""
    prompt = build_prompt(scenario, cell, context, measure, lang)
    msgs = [{"role": "user", "content": prompt}]
    if think_lang:
        msgs.insert(0, {"role": "system", "content": THINK_DIRECTIVES[think_lang]})
    return msgs


async def run(models, scenario_filter, n, concurrency, tag,
              context="cold", search=False, measure="triplet", lang="en",
              think_lang=None, capture_reasoning=False):
    scen_path = SCENARIOS if lang == "en" else HERE / "data" / f"scenarios_{lang}.json"
    if not scen_path.exists():
        sys.exit(f"{scen_path} missing — run translate_stimuli.py and human-review it first")
    scenarios = json.loads(scen_path.read_text())
    if lang != "en" and any(s.get("review") for s in scenarios):
        print(f"WARNING: {scen_path.name} still carries review:true flags — "
              "these translations have not been human-reviewed.")
    if scenario_filter:
        scenarios = [s for s in scenarios if s["scenario_id"] in scenario_filter]
    if not scenarios:
        sys.exit("no scenarios matched")

    sem = asyncio.Semaphore(concurrency)
    # Build the full task list: one acomplete_many per (scenario, cell, model)
    jobs = []
    meta_index = []
    for s in scenarios:
        for cell in s["cells"]:
            msgs = build_messages(s, cell, context, measure, lang, think_lang)
            for model in models:
                jobs.append(acomplete_many(msgs, model, n, temperature=1.0, max_tokens=30,
                                           web_search=search,
                                           capture_reasoning=capture_reasoning, sem=sem))
                meta_index.append((s, cell, model))

    print(f"{len(scenarios)} scenarios × 4 cells × {len(models)} models × N={n} "
          f"= {len(jobs) * n} samples ({len(jobs)} sampling jobs)")

    t0 = time.time()
    rows = []
    # gather preserves order, so results align with meta_index
    results = await asyncio.gather(*jobs)
    for (s, cell, model), samples in zip(meta_index, results):
        for i, r in enumerate(samples):
            text = (r or {}).get("text") or ""
            v, g, u = parse_triplet(text)
            row = {
                "scenario_id": s["scenario_id"],
                "domain": s["domain"],
                "cell_type": cell["cell_type"],
                "verbatim_truth": cell["verbatim_truth"],
                "gist_truth": cell["gist_truth"],
                "model": model,
                "context": context,
                "search": search,
                "measure": measure,
                "lang": lang,
                "sample_idx": i,
                "verbatim_rating": v,
                "gist_rating": g,
                "unethical_rating": u,
                "raw": text if (v is None or g is None or u is None) else None,
            }
            if think_lang or capture_reasoning:
                trace = (r or {}).get("reasoning")
                row["think_lang"] = think_lang
                row["reasoning_lang"] = trace_lang(trace)
                row["reasoning"] = trace
            if search:
                row["citations"] = (r or {}).get("citations") or []
                row["gen_id"] = (r or {}).get("gen_id")
                row["prompt_tokens"] = (r or {}).get("prompt_tokens")
            rows.append(row)

    out_dir = HERE / "results" / f"t1_{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "samples.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    parsed_ok = sum(1 for r in rows if r["unethical_rating"] is not None)
    meta = {
        "tag": tag, "context": context, "search": search, "measure": measure,
        "lang": lang, "think_lang": think_lang, "capture_reasoning": capture_reasoning,
        "models": models, "n": n,
        "scenarios": [s["scenario_id"] for s in scenarios],
        "total_samples": len(rows),
        "parsed_ok": parsed_ok,
        "parse_rate": round(parsed_ok / len(rows), 3) if rows else 0,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {len(rows)} rows to {out_dir}/samples.jsonl "
          f"({parsed_ok} parsed, {meta['parse_rate']:.0%}) in {meta['elapsed_sec']}s")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=DEFAULT_SUBJECTS)
    ap.add_argument("--scenarios", nargs="+", default=None, help="scenario ids e.g. s1 s2")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--tag", default="pilot")
    ap.add_argument("--context", default="cold", choices=["cold", "informed"],
                    help="cold (default) = response only, model judges from its own knowledge; "
                         "informed = prepend the true situation (robustness check).")
    ap.add_argument("--search", action="store_true",
                    help="Enable OpenRouter web search: the model retrieves live results "
                         "before answering (extra $0.012/call at 3 results; citations logged).")
    ap.add_argument("--measure", default="triplet", choices=["triplet", "ethics_only"],
                    help="triplet (default) = V+G+U in one response; ethics_only = UNETHICAL "
                         "alone in an isolated call (format-artifact check for numeric anchoring).")
    ap.add_argument("--lang", default="en", choices=["en", "zh", "ja"],
                    help="prompt language; zh/ja load data/scenarios_<lang>.json and use "
                         "fully translated frames (output labels stay English for parsing).")
    ap.add_argument("--think-lang", default=None, choices=["en", "zh", "ja"],
                    help="Study D: instruct the model to REASON in this language "
                         "(instruction written in the prompt language). Implies "
                         "--capture-reasoning so compliance can be verified.")
    ap.add_argument("--capture-reasoning", action="store_true",
                    help="store the hidden chain-of-thought + its detected language "
                         "per row (opus48/gemini35flash/kimik3 expose it; gpt56sol "
                         "does not). No extra cost — traces are billed anyway.")
    args = ap.parse_args()

    for m in args.models:
        if m not in MODEL_REGISTRY:
            sys.exit(f"unknown model {m!r}; known: {list(MODEL_REGISTRY)}")

    asyncio.run(run(args.models, args.scenarios, args.n, args.concurrency, args.tag,
                    args.context, args.search, args.measure, args.lang,
                    args.think_lang, args.capture_reasoning or bool(args.think_lang)))


if __name__ == "__main__":
    main()
