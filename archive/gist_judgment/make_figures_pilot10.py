"""
EDA figure for the 10-scenario pilot (3 frontier models, N=10, 4 arms).

Panels:
  A  UNETHICAL by cell x model (T1 offline)
  B  Perception map: VERBATIM x GIST means vs ground truth (T1 offline)
  C  Retrieval effect: WT-cell VERBATIM offline vs search, per scenario
  D  Scaffolding: joint vs isolated UNETHICAL (PA & TF)
  E  Palter decomposition: R2 extraction vs R3 evaluation
  F  Palter heterogeneity: per-scenario palter UNETHICAL (offline)

Usage: python make_figures_pilot10.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
CELLS = ["fully_true", "palter", "truthy_falsehood", "blatant_falsehood"]
CELL_LAB = {"fully_true": "Whole\ntruth", "palter": "Palter", "truthy_falsehood": "Truthy\nfalsehood",
            "blatant_falsehood": "Blatant\nfalsehood"}
CELL_C = {"fully_true": "#2ca02c", "palter": "#ff7f0e",
          "truthy_falsehood": "#1f77b4", "blatant_falsehood": "#d62728"}
GT = {"fully_true": (6.7, 6.7), "palter": (6.7, 1.3), "truthy_falsehood": (1.3, 6.7),
      "blatant_falsehood": (1.3, 1.3)}
MODELS = ["gemini3pro", "gpt55", "opus48"]
MC = {"gemini3pro": "#4285F4", "gpt55": "#10a37f", "opus48": "#d97706"}
SCEN_LAB = {"s1": "climate", "s2": "jobs", "s4": "inflation", "s12": "border", "s13": "crime",
            "s17": "ukraine", "s18": "college", "s21": "AI stocks", "s23": "vaccines", "s26": "crypto"}


def load_t1(tag):
    return [json.loads(l) for l in (HERE / "results" / f"t1_{tag}" / "samples.jsonl").open()]


off = [r for r in load_t1("pilot10_t1_offline") if r["unethical_rating"] is not None]
srch = [r for r in load_t1("pilot10_t1_search") if r["unethical_rating"] is not None]
iso = [r for r in load_t1("pilot10_t1_ethicsonly") if r["unethical_rating"] is not None]
recog = [json.loads(l) for l in (HERE / "results" / "recognition_pilot10_recog" / "samples.jsonl").open()]


def cm(rows, m, c, key):
    v = [r[key] for r in rows if r["model"] == m and r["cell_type"] == c and r.get(key) is not None]
    return mean(v) if v else np.nan


fig, axes = plt.subplots(2, 3, figsize=(19, 11))
(axA, axB, axC), (axD, axE, axF) = axes

# ---- A: unethical by cell x model (offline) ----
x = np.arange(len(CELLS)); w = 0.26
for i, m in enumerate(MODELS):
    vals = [cm(off, m, c, "unethical_rating") for c in CELLS]
    axA.bar(x + (i - 1) * w, vals, w, label=m, color=MC[m])
axA.set_xticks(x); axA.set_xticklabels([CELL_LAB[c] for c in CELLS], fontsize=9)
axA.set_ylabel("Mean UNETHICAL (1-7)"); axA.set_ylim(0, 7)
axA.axhline(4, color="gray", ls=":", lw=0.7)
axA.set_title("A. Moral judgment by cell (offline, 10 scenarios)", fontsize=11)
axA.legend(fontsize=8)

# ---- B: perception map (offline) ----
axB.axhline(4, color="gray", lw=0.7); axB.axvline(4, color="gray", lw=0.7)
axB.set_xlim(0.5, 7.5); axB.set_ylim(0.5, 7.5)
for c in CELLS:
    gx, gy = GT[c]
    axB.scatter([gx], [gy], marker="D", s=200, facecolors="none",
                edgecolors=CELL_C[c], linewidths=2, zorder=5)
    xs = [cm(off, m, c, "verbatim_rating") for m in MODELS]
    ys = [cm(off, m, c, "gist_rating") for m in MODELS]
    axB.scatter(xs, ys, s=46, color=CELL_C[c], alpha=0.9, edgecolors="white",
                linewidths=0.5, label=CELL_LAB[c].replace("\n", " "))
axB.set_xlabel("Perceived VERBATIM accuracy"); axB.set_ylabel("Perceived GIST truth")
axB.set_title("B. Perception map (dots=models, ◇=ground truth)", fontsize=11)
axB.legend(fontsize=7.5, loc="center")

# ---- C: retrieval effect on WT verbatim per scenario ----
scens = list(SCEN_LAB)
def wt_v(rows, sid):
    v = [r["verbatim_rating"] for r in rows
         if r["scenario_id"] == sid and r["cell_type"] == "fully_true" and r.get("verbatim_rating")]
    return mean(v) if v else np.nan
xo = [wt_v(off, s) for s in scens]; xs_ = [wt_v(srch, s) for s in scens]
xi = np.arange(len(scens))
axC.bar(xi - 0.2, xo, 0.4, label="offline", color="#9aa5b1")
axC.bar(xi + 0.2, xs_, 0.4, label="search", color="#2563eb")
axC.set_xticks(xi); axC.set_xticklabels([SCEN_LAB[s] for s in scens], rotation=45, ha="right", fontsize=8)
axC.set_ylabel("WT-cell VERBATIM rating"); axC.set_ylim(0, 7.4)
axC.axhline(7, color="green", ls=":", lw=0.8)
axC.set_title("C. Retrieval fixes current-fact verification\n(whole-truth cells; dotted line = correct)", fontsize=11)
axC.legend(fontsize=8)

# ---- D: scaffolding joint vs isolated (PA, TF) ----
pairs = [("palter", "PA"), ("truthy_falsehood", "TF")]
xi = np.arange(len(MODELS))
for j, (cell, lab) in enumerate(pairs):
    jv = [cm(off, m, cell, "unethical_rating") for m in MODELS]
    iv = [cm(iso, m, cell, "unethical_rating") for m in MODELS]
    o = (j - 0.5) * 0.44
    axD.bar(xi + o - 0.1, jv, 0.2, color=CELL_C[cell], label=f"{lab} joint (V/G asked first)")
    axD.bar(xi + o + 0.1, iv, 0.2, color=CELL_C[cell], alpha=0.45, hatch="//",
            label=f"{lab} isolated (ethics alone)")
axD.set_xticks(xi); axD.set_xticklabels(MODELS, fontsize=9)
axD.set_ylabel("Mean UNETHICAL (1-7)"); axD.set_ylim(0, 5.5)
axD.set_title("D. Truth-scaffolding effect: joint vs isolated ethics", fontsize=11)
axD.legend(fontsize=7.2, ncol=2)

# ---- E: palter decomposition ----
ext, knf, r1pa = [], [], []
for m in MODELS:
    r2 = [r for r in recog if r["task"] == "r2" and r["model"] == m
          and r["cell_type"] == "palter" and r.get("choice")]
    ext.append(100 * sum(1 for r in r2 if r["choice"] == "false_gist") / len(r2))
    r3 = [r for r in recog if r["task"] == "r3" and r["model"] == m
          and r["gist_kind"] == "false_gist" and r.get("verdict")]
    knf.append(100 * sum(1 for r in r3 if r["verdict"] == "FALSE") / len(r3))
    r1 = [r for r in recog if r["task"] == "r1" and r["model"] == m
          and r["cell_type"] == "palter" and r.get("verdict")]
    r1pa.append(100 * sum(1 for r in r1 if r["verdict"] == "ACCURATE") / len(r1))
xi = np.arange(len(MODELS))
axE.bar(xi - 0.27, r1pa, 0.27, label="R1: palter facts rated accurate (correct)", color="#6b7280")
axE.bar(xi, ext, 0.27, label="R2: extracted misleading implicature", color="#ff7f0e")
axE.bar(xi + 0.27, knf, 0.27, label="R3: knows implied gist is false", color="#7c3aed")
axE.set_xticks(xi); axE.set_xticklabels(MODELS, fontsize=9)
axE.set_ylabel("%"); axE.set_ylim(0, 105)
axE.set_title("E. Palter decomposition: blindness = extraction, not evaluation", fontsize=11)
axE.legend(fontsize=7.2)

# ---- F: palter heterogeneity by scenario ----
pv = []
for s in scens:
    v = [r["unethical_rating"] for r in off
         if r["scenario_id"] == s and r["cell_type"] == "palter"]
    pv.append(mean(v) if v else np.nan)
order = np.argsort(pv)[::-1]
axF.bar(np.arange(len(scens)), [pv[i] for i in order], color="#ff7f0e")
axF.set_xticks(np.arange(len(scens)))
axF.set_xticklabels([SCEN_LAB[scens[i]] for i in order], rotation=45, ha="right", fontsize=8)
axF.set_ylabel("Palter UNETHICAL (1-7)"); axF.set_ylim(0, 7)
axF.axhline(4, color="gray", ls=":", lw=0.7)
axF.set_title("F. Which palters get condemned vs waved through\n(offline, mean of 3 models)", fontsize=11)

fig.suptitle("Stage 1 pilot EDA — 10 scenarios × 3 frontier models × N=10  "
             "(T1 offline/search/ethics-only + R1-R3 recognition; 6,600 calls, $69.60)",
             fontsize=13, y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.97])
out = HERE / "results" / "figures"; out.mkdir(parents=True, exist_ok=True)
for ext_ in ("png", "pdf"):
    p = out / f"pilot10_eda.{ext_}"
    fig.savefig(p, dpi=100, bbox_inches="tight")
    print(f"✓ wrote {p}")
