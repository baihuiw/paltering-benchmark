"""
Swarmplot of UNETHICAL ratings by cell (4 conditions) x model, search arm,
with mean and 95% CI overlaid. No title (per request).

Usage: python make_figure_swarm.py
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = Path(__file__).parent
OUT = HERE / "results" / "figures"

CELLS = ["fully_true", "palter", "truthy_falsehood", "blatant_falsehood"]
CELL_LAB = {"fully_true": "Whole truth\n(V+ G+)", "palter": "Palter\n(V+ G-)",
            "truthy_falsehood": "Truthy falsehood\n(V- G+)", "blatant_falsehood": "Blatant falsehood\n(V- G-)"}
MODELS = ["gemini3pro", "gpt55", "opus48"]
MODEL_LAB = {"gemini3pro": "Gemini 3 Pro", "gpt55": "GPT-5.5", "opus48": "Opus 4.8"}
MC = {"Gemini 3 Pro": "#4285F4", "GPT-5.5": "#10a37f", "Opus 4.8": "#d97706"}

rows = [json.loads(l) for l in (HERE / "results" / "t1_pilot10_t1_search" / "samples.jsonl").open()]
df = pd.DataFrame([{
    "cell": CELL_LAB[r["cell_type"]],
    "model": MODEL_LAB[r["model"]],
    "unethical": r["unethical_rating"],
} for r in rows if r["unethical_rating"] is not None])
cell_order = [CELL_LAB[c] for c in CELLS]
model_order = [MODEL_LAB[m] for m in MODELS]

fig, ax = plt.subplots(figsize=(13.5, 6.5))
sns.swarmplot(data=df, x="cell", y="unethical", hue="model",
              order=cell_order, hue_order=model_order,
              palette=MC, dodge=True, size=1.55, alpha=0.55, ax=ax, legend=True)

# overlay mean + 95% CI at the dodged positions (hue groups span width 0.8)
width = 0.8
for i, cl in enumerate(cell_order):
    for j, ml in enumerate(model_order):
        v = df[(df.cell == cl) & (df.model == ml)]["unethical"].values
        m = v.mean()
        ci = 1.96 * v.std(ddof=1) / np.sqrt(len(v))
        xpos = i - width / 2 + width / len(model_order) * (j + 0.5)
        ax.errorbar(xpos, m, yerr=ci, fmt="none", ecolor="black", elinewidth=1.6,
                    capsize=4, capthick=1.6, zorder=6)
        ax.scatter([xpos], [m], s=52, color="black", edgecolors="white",
                   linewidths=1.0, zorder=7)

ax.set_ylabel("UNETHICAL rating  (1 = not at all, 7 = extremely unethical)", fontsize=10)
ax.set_xlabel("")
ax.set_ylim(0.5, 7.5)
ax.set_yticks(range(1, 8))
ax.axhline(4, color="gray", ls=":", lw=0.7)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[:3], labels[:3], fontsize=9, loc="upper left", frameon=True)

OUT.mkdir(parents=True, exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(OUT / f"search_swarm_unethical.{ext}", dpi=115, bbox_inches="tight")
print("✓ search_swarm_unethical.png/.pdf")
