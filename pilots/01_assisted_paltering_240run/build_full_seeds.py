"""Extract validated seeds for the two full-run domains.

MARKETPLACE (target 100)
  Source: Machine-Bullshit BullshitEval (input/bullshit_eval/dataset.json,
  2,400 rows = assistant frames x question types). Frames carry role + item +
  situation but NO ground-truth facts -- exactly what we add: our documents.
  We dedupe to distinct assistants, drop frames that cannot carry a private
  document (no concrete item/service), and sample 100 diverse frames.

MISINFO (target ~1000 with buffer)
  a) AVeriTeC (pminervini/averitec, train+dev, 3,568 labelled): real-world
     claims + QA-decomposed evidence + justification. Keep labels
     Refuted / Conflicting Evidence/Cherrypicking, >=4 QA pairs.
     The claim is the wrong-gist ANCHOR; the QA evidence composes the
     whole-truth document; each QA pair is a candidate seeded fact.
  b) PUBHEALTH (Jezzarax/pubhealth-converted : pubhealth_source): health
     claims + journalist explanation (the validated truth) + main_text.
     Keep labels mixture / false with substantial explanations.

Output:
  data/full_marketplace_seeds.json
  data/full_misinfo_seeds.json

Both are SEEDS, not runnable scenarios: the authoring step
(build_full_scenarios.py) turns them into misuse_v2-schema scenarios and
every draft carries review:true until a human pass.
"""
import json
import random
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
MB = Path("/Users/wangbaihui/Machine-Bullshit")
rng = random.Random(20260816)

# ---------------------------------------------------------------- marketplace
rows = json.loads((MB / "input" / "bullshit_eval" / "dataset.json").read_text())
frames = {}
for r in rows:
    sp = r["sys_prompt"].strip()
    frames.setdefault(sp, {"sys_prompt": sp, "situation": r["situation"],
                           "questions": []})
    frames[sp]["questions"].append({"q_type": r["q_type"], "question": r["question"]})
print(f"bullshit_eval: {len(rows)} rows -> {len(frames)} distinct assistant frames")

# a frame can carry a private document only if it sells/promotes a concrete
# item or service; drop pure-advice frames (no seller, nothing to conceal)
DROP = re.compile(r"\b(tutor|therap|meditat|coach(?!ing service)|horoscope|"
                  r"fortune|joke|trivia|weather|translat)\b", re.I)
kept = [f for sp, f in frames.items() if not DROP.search(sp)]
print(f"after concreteness filter: {len(kept)}")

# item noun for grouping/diversity: crude extraction from the sys_prompt tail
def item_of(sp):
    m = re.search(r"(?:sell|promot|market|advertis|recommend|offer)\w*\s+(?:an?\s+|the\s+)?(.+?)(?:\.|$)", sp, re.I)
    return (m.group(1) if m else sp[-40:]).strip().lower()[:48]

for f in kept:
    f["item_hint"] = item_of(f["sys_prompt"])

rng.shuffle(kept)
seen_items, market = set(), []
for f in kept:                       # greedy diversity pass, then backfill
    if f["item_hint"] not in seen_items:
        market.append(f)
        seen_items.add(f["item_hint"])
for f in kept:
    if len(market) >= 100:
        break
    if f not in market:
        market.append(f)
market = market[:100]
out = {"source": "Machine-Bullshit BullshitEval (Liang et al. 2025)",
       "note": "frames only; documents, fact checklists and reader items are "
               "authored by build_full_scenarios.py and carry review:true",
       "seeds": market}
(HERE / "data" / "full_marketplace_seeds.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False))
print(f"marketplace seeds: {len(market)} -> data/full_marketplace_seeds.json")

# ------------------------------------------------------------------- misinfo
from datasets import load_dataset  # noqa: E402

misinfo = []

# --- AVeriTeC
av_labels = Counter()
for split in ("train", "dev"):
    ds = load_dataset("pminervini/averitec", split=split)
    for r in ds:
        av_labels[r["label"]] += 1
        if r["label"] not in ("Refuted", "Conflicting Evidence/Cherrypicking"):
            continue
        qs = r["questions"] or []
        qa = []
        for q in qs:
            for a in (q.get("answers") or []):
                txt = (a.get("answer") or "").strip()
                if a.get("boolean_explanation"):
                    txt = f"{txt} — {a['boolean_explanation'].strip()}"
                if txt:
                    qa.append({"question": q.get("question", "").strip(),
                               "answer": txt[:600]})
                break                      # first answer per question
        if len(qa) < 4:
            continue
        just = (r.get("justification") or "").strip()
        if len(just) < 40:
            continue
        misinfo.append({
            "source": "averitec", "split": split,
            "anchor_claim": r["claim"].strip(),
            "label": r["label"],
            "speaker": r.get("speaker"), "claim_date": r.get("claim_date"),
            "truth_summary": just,
            "evidence_qa": qa[:10],
            "fact_check_url": r.get("fact_checking_article"),
        })
print(f"averitec labels: {dict(av_labels)}")
print(f"averitec kept: {sum(1 for m in misinfo if m['source']=='averitec')}")

# --- PUBHEALTH (via datasets-server rows API: local pyarrow cannot read
# this repo's parquet -- "Repetition level histogram size mismatch")
import urllib.request

def hf_rows(dataset, config, split):
    offset = 0
    while True:
        u = ("https://datasets-server.huggingface.co/rows?"
             f"dataset={urllib.parse.quote(dataset, safe='')}&config={config}"
             f"&split={split}&offset={offset}&length=100")
        for attempt in range(5):
            try:
                with urllib.request.urlopen(u, timeout=60) as f:
                    d = json.load(f)
                break
            except Exception:
                if attempt == 4:
                    raise
                import time as _t
                _t.sleep(4 * (attempt + 1))
        rows_ = d.get("rows", [])
        if not rows_:
            return
        for r in rows_:
            yield r["row"]
        offset += len(rows_)
        if offset >= d.get("num_rows_total", 0):
            return

import urllib.parse
ph_labels = Counter()
for r in hf_rows("Jezzarax/pubhealth-converted", "pubhealth_source", "train"):
    lab = (r.get("label") or "").strip().lower()
    ph_labels[lab] += 1
    if lab not in ("mixture", "false"):
        continue
    exp = (r.get("explanation") or "").strip()
    if len(exp) < 400:                       # need substance for a document
        continue
    main = (r.get("main_text") or "").strip()
    misinfo.append({
        "source": "pubhealth", "split": "train",
        "anchor_claim": r["claim"].strip(),
        "label": lab,
        "speaker": None, "claim_date": r.get("date_published"),
        "truth_summary": exp[:2500],
        "evidence_qa": [],                    # explanation carries the truth
        "main_text_excerpt": main[:2500],
        "subjects": r.get("subjects"),
    })
print(f"pubhealth labels: {dict(ph_labels)}")
print(f"pubhealth kept: {sum(1 for m in misinfo if m['source']=='pubhealth')}")

# dedupe near-identical anchors, shuffle, cap with buffer
seen, dedup = set(), []
for m in misinfo:
    k = re.sub(r"\W+", "", m["anchor_claim"].lower())[:80]
    if k in seen:
        continue
    seen.add(k)
    dedup.append(m)
rng.shuffle(dedup)
out = {"targets": {"final_scenarios": 1000, "buffer": len(dedup)},
       "note": "seeds only; scenario authoring adds document, fact checklist "
               "(same 6/3/1-style portion design), reader items, honest "
               "reference; drafts carry review:true",
       "seeds": dedup}
(HERE / "data" / "full_misinfo_seeds.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False))
print(f"misinfo seeds total after dedupe: {len(dedup)} -> data/full_misinfo_seeds.json")
