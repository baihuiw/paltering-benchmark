"""
Draft zh/ja translations of scenario stimuli for the language study.

Translates user_question, background, true_gist, false_gist, and the four cell
statements with a strong model under strict fidelity rules (numbers, units,
hedges, and scope words preserved EXACTLY, so each statement keeps its
verbatim-truth status). Output mirrors the scenarios.json schema so
run_t1_judgment.py --lang zh|ja loads it directly.

Every entry carries "review": true and an "en_source" block; a side-by-side
markdown (review_translations_<lang>.md) is emitted for human review.
DO NOT run the language study until the review flags are cleared.

Usage:
    python translate_stimuli.py --langs zh ja --scenarios s1 s4 s12 s13 s18 s21 s23 s26
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))  # shared OpenRouter client at the repo root
sys.path.insert(0, str(Path(__file__).parent / "src"))  # this study's own modules
from client_async import acomplete, MODEL_REGISTRY  # noqa: E402

HERE = Path(__file__).parent
SCENARIOS = HERE / "data" / "scenarios.json"

LANG_NAMES = {"zh": "Simplified Chinese", "ja": "Japanese"}

PROMPT = """You are translating research stimuli for a cross-lingual study of how people judge misleading statements. Translate the fields below into {lang_name}.

STRICT RULES — the scientific validity depends on them:
1. Preserve every number, unit, date, percentage, and named entity EXACTLY. Do not convert units or localize numbers.
2. Preserve hedges, qualifiers, and scope words precisely ("most", "typical", "on average", "in some cases"). Each sentence's literal truth status must be IDENTICAL in translation — no strengthening, no softening.
3. Do not add, drop, or reorder claims. Translate meaning-for-meaning, not word-for-word, but keep every claim.
4. Register: user_question and the four statements are casual online-forum posts — natural, colloquial {lang_name} as a native forum user would write. background/true_gist/false_gist are neutral-informative prose.
5. Keep quotation or emphasis conventions natural for {lang_name}.

FIELDS TO TRANSLATE (JSON):
{payload}

Respond with ONLY a JSON object, no code fences, no commentary, with exactly these keys:
{{"user_question": "...", "background": "...", "true_gist": "...", "false_gist": "...", "statements": {{"fully_true": "...", "palter": "...", "truthy_falsehood": "...", "blatant_falsehood": "..."}}}}"""


def extract_json(text: str):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip(), flags=re.MULTILINE)
    start = t.find("{")
    if start < 0:
        return None
    try:
        return json.loads(t[start:])
    except json.JSONDecodeError:
        return None


async def translate_one(s, lang, translator, sem):
    cells = {c["cell_type"]: c["statement"] for c in s["cells"]}
    payload = json.dumps({
        "user_question": s["user_question"], "background": s["background"],
        "true_gist": s["true_gist"], "false_gist": s["false_gist"],
        "statements": cells,
    }, ensure_ascii=False, indent=1)
    prompt = PROMPT.format(lang_name=LANG_NAMES[lang], payload=payload)
    async with sem:
        text = await acomplete([{"role": "user", "content": prompt}], translator,
                               max_tokens=1600, temperature=0)
        parsed = extract_json(text)
        if parsed is None:  # one retry with a nudge
            text = await acomplete([{"role": "user", "content":
                                     prompt + "\n\nReturn ONLY the valid JSON object."}],
                                   translator, max_tokens=1600, temperature=0)
            parsed = extract_json(text)
    return s["scenario_id"], parsed, text


async def main_async(langs, scenario_ids, translator):
    scenarios = json.loads(SCENARIOS.read_text())
    subset = [s for s in scenarios if s["scenario_id"] in scenario_ids]
    if len(subset) != len(scenario_ids):
        sys.exit(f"missing scenarios: {set(scenario_ids) - {s['scenario_id'] for s in subset}}")
    sem = asyncio.Semaphore(8)

    for lang in langs:
        results = await asyncio.gather(*[translate_one(s, lang, translator, sem)
                                         for s in subset])
        out, failed = [], []
        md = [f"# Translation review — {LANG_NAMES[lang]} ({lang})",
              f"translator: {translator} | fidelity rules: numbers/hedges preserved exactly",
              "Check each pair: does the translation keep the SAME literal-truth status?", ""]
        by_id = {sid: (parsed, raw) for sid, parsed, raw in results}
        for s in subset:
            parsed, raw = by_id[s["scenario_id"]]
            if not parsed:
                failed.append(s["scenario_id"])
                continue
            t = copy.deepcopy(s)
            t["user_question"] = parsed["user_question"]
            t["background"] = parsed["background"]
            t["true_gist"] = parsed["true_gist"]
            t["false_gist"] = parsed["false_gist"]
            for c in t["cells"]:
                c["statement"] = parsed["statements"][c["cell_type"]]
                c.pop("note", None)
            t["lang"] = lang
            t["review"] = True
            t["en_source"] = {"user_question": s["user_question"],
                              "statements": {c["cell_type"]: c["statement"] for c in s["cells"]}}
            out.append(t)
            md.append(f"## {s['scenario_id']} — {s['title']}")
            md.append(f"**Q (en):** {s['user_question']}\n\n**Q ({lang}):** {parsed['user_question']}\n")
            for c in s["cells"]:
                md.append(f"**{c['cell_type']} (en):** {c['statement']}\n")
                md.append(f"**{c['cell_type']} ({lang}):** {parsed['statements'][c['cell_type']]}\n")
            md.append(f"**background ({lang}):** {parsed['background']}\n")
        (HERE / "data" / f"scenarios_{lang}.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2))
        (HERE / f"review_translations_{lang}.md").write_text("\n".join(md))
        print(f"[{lang}] wrote {len(out)} scenarios "
              f"(failed: {failed or 'none'}) -> data/scenarios_{lang}.json "
              f"+ review_translations_{lang}.md  [ALL review:true]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=["zh", "ja"], choices=["zh", "ja"])
    ap.add_argument("--scenarios", nargs="+", required=True)
    ap.add_argument("--translator", default="gpt56sol")
    args = ap.parse_args()
    if args.translator not in MODEL_REGISTRY:
        sys.exit(f"unknown translator {args.translator!r}")
    asyncio.run(main_async(args.langs, args.scenarios, args.translator))


if __name__ == "__main__":
    main()
