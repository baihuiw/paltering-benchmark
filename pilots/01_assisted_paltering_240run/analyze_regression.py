"""Fact-level logistic regression: is the damaging fact dropped MORE than
positives once we hold the reply's information density constant?

Unit of analysis: one (fact, reply) pair. Outcome: conveyed (0/1).

The key control is `load_loo` -- the share of the reply's OTHER nine facts
that were conveyed. Leave-one-out is essential: using the reply's total
transmission would put the outcome on both sides of the equation. With
load_loo in the model, the valence coefficient answers precisely the
reviewer's objection: "given a reply that carried this much information
overall, was the damaging fact still less likely to be included than a
positive fact?"

Also controls fact statement length (the statability confound) and reply
length, with scenario and model fixed effects. Inference: cluster bootstrap
by scenario (6 clusters -- coarse, reported honestly alongside model SEs).
"""
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = Path(__file__).parent
R = HERE / "results"
FACTS = json.loads((HERE / "data" / "misuse_v2_facts.json").read_text())

# ---------- assemble the fact-level frame ----------
text = {}
for tag in ("t1_clean", "t1_r0_clean"):
    for r in [json.loads(l) for l in (R / f"misuse_v2_{tag}" / "samples.jsonl").open()]:
        text[(r["scenario_id"], r["model"], r["rung"], r["sample_idx"])] = r["output"] or ""

rows = []
for r in [json.loads(l) for l in (R / "misuse_v2_factjudge_v1" / "facts.jsonl").open()]:
    if r["stage"] != "t1" or not r["parse_ok"]:
        continue
    key = (r["scenario_id"], r["model"], r["rung"], r["sample_idx"])
    reply_words = len(text.get(key, "").split())
    conv = {f["idx"]: bool(f["conveyed"]) for f in r["facts"]}
    total = sum(conv.values())
    fl = {f["idx"]: f for f in FACTS[r["scenario_id"]]}
    for f in r["facts"]:
        rows.append({
            "reply_id": "|".join(map(str, key)),
            "scenario": r["scenario_id"], "model": r["model"], "rung": r["rung"],
            "fact_idx": f["idx"], "valence": f["valence"],
            "conveyed": int(bool(f["conveyed"])),
            # leave-one-out information density of this reply
            "load_loo": (total - int(bool(f["conveyed"]))) / (len(r["facts"]) - 1),
            "fact_words": len(fl[f["idx"]]["text"].split()),
            "reply_words": reply_words,
        })
df = pd.DataFrame(rows)
print(f"{len(df)} fact-reply observations from {df.reply_id.nunique()} replies, "
      f"{df.scenario.nunique()} scenarios\n")

# ---------- design matrix ----------
SCEN = sorted(df.scenario.unique())
MODS = sorted(df.model.unique())
FW_M, FW_S = df.fact_words.mean(), df.fact_words.std()
RW_M, RW_S = df.reply_words.mean(), df.reply_words.std()

def design(d, interact=False):
    """Fixed column set so bootstrap replicates stay comparable; constant
    columns (a scenario absent from a resample) are dropped by name."""
    X = pd.DataFrame(index=d.index)
    X["minor"] = (d.valence == "neg_minor").astype(float)
    X["damaging"] = (d.valence == "neg_material").astype(float)
    X["brief"] = (d.rung == "R1").astype(float)
    X["persuade"] = (d.rung == "R2").astype(float)
    X["load_loo"] = d.load_loo.astype(float)
    X["fact_words"] = (d.fact_words - FW_M) / FW_S
    X["reply_words"] = (d.reply_words - RW_M) / RW_S
    for s in SCEN[1:]:
        X[f"sc_{s}"] = (d.scenario == s).astype(float)
    for m in MODS[1:]:
        X[f"md_{m}"] = (d.model == m).astype(float)
    if interact:
        X["damaging_x_brief"] = X.damaging * X.brief
        X["damaging_x_persuade"] = X.damaging * X.persuade
    X["const"] = 1.0
    return X.loc[:, (X.nunique() > 1) | (X.columns == "const")]

def fit(d, interact=False):
    X = design(d, interact)
    res = sm.Logit(d.conveyed.values, X.values).fit(disp=0)
    return res, list(X.columns)

KEEP = ["minor", "damaging", "brief", "persuade", "load_loo",
        "fact_words", "reply_words", "damaging_x_brief", "damaging_x_persuade"]

for interact in (False, True):
    res, cols = fit(df, interact)
    # cluster bootstrap by scenario
    sids = sorted(df.scenario.unique())
    rng = random.Random(11)
    boots = {k: [] for k in KEEP}
    nrep = 0
    for _ in range(400):
        parts = [df[df.scenario == s] for s in rng.choices(sids, k=len(sids))]
        try:
            b, bcols = fit(pd.concat(parts, ignore_index=True), interact)
        except Exception:
            continue
        nrep += 1
        for k in KEEP:
            if k in bcols:
                boots[k].append(b.params[bcols.index(k)])
    title = "WITH valence x rung interaction" if interact else "MAIN EFFECTS"
    print("=" * 78)
    print(f"{title}   (n={len(df)}, {nrep} bootstrap reps)")
    print(f"{'term':22s}{'beta':>9s}{'OR':>8s}{'model SE':>10s}{'cluster 95% CI':>24s}")
    for k in KEEP:
        if k not in cols:
            continue
        i = cols.index(k)
        lo, hi = np.percentile(boots[k], [2.5, 97.5]) if boots[k] else (np.nan, np.nan)
        print(f"{k:22s}{res.params[i]:+9.3f}{np.exp(res.params[i]):8.2f}"
              f"{res.bse[i]:10.3f}   [{lo:+6.2f}, {hi:+6.2f}]")
    print()

# ---------- plain-language contrast ----------
res, cols = fit(df)
b = res.params[cols.index("damaging")]
print("interpretation of the `damaging` coefficient:")
print(f"  holding the reply's overall information density constant (load_loo),")
print(f"  plus fact length, reply length, scenario and model, the odds that the")
print(f"  damaging fact is conveyed are exp({b:+.3f}) = {np.exp(b):.2f}x the odds")
print(f"  for a positive fact -- a {100*(1-np.exp(b)):.0f}% reduction in odds.")
