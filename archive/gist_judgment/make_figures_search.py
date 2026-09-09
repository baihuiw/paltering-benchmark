"""
Individual figures for the SEARCH-ARM results (t1_pilot10_t1_search):
10 scenarios x 3 frontier models x N=10, Exa retrieval injected on every call.

One analysis per file (PNG + PDF each), varied plot types:
  1 search_likert_unethical   — 100% stacked distribution of UNETHICAL (Likert)
  2 search_perception_map     — scatter: perceived V x G vs ground truth
  3 search_heatmap_scenarios  — heatmaps: scenario x cell mean UNETHICAL per model
  4 search_dumbbell_vg        — dumbbell: perceived VERBATIM vs GIST per cell/model
  5 search_judgment_drivers   — regression scatters: what predicts condemnation

Usage: python make_figures_search.py
"""
from __future__ import annotations
import json
from pathlib import Path
from statistics import mean
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "results" / "figures"
TAG = "pilot10_t1_search"

CELLS = ["fully_true", "palter", "truthy_falsehood", "blatant_falsehood"]
CELL_LAB = {"fully_true": "Whole truth (V+ G+)", "palter": "Palter (V+ G-)",
            "truthy_falsehood": "Truthy falsehood (V- G+)", "blatant_falsehood": "Blatant falsehood (V- G-)"}
CELL_C = {"fully_true": "#2ca02c", "palter": "#ff7f0e",
          "truthy_falsehood": "#1f77b4", "blatant_falsehood": "#d62728"}
MODELS = ["gemini3pro", "gpt55", "opus48"]
MODEL_LAB = {"gemini3pro": "Gemini 3 Pro", "gpt55": "GPT-5.5", "opus48": "Opus 4.8"}
MMARK = {"gemini3pro": "o", "gpt55": "s", "opus48": "^"}
SCEN_LAB = {"s1": "climate", "s2": "jobs", "s4": "inflation", "s12": "border", "s13": "crime",
            "s17": "ukraine", "s18": "college", "s21": "AI stocks", "s23": "vaccines", "s26": "crypto"}
SCENS = list(SCEN_LAB)

rows = [json.loads(l) for l in (HERE / "results" / f"t1_{TAG}" / "samples.jsonl").open()]
rows = [r for r in rows if r["unethical_rating"] is not None]
TITLE_TAIL = "search arm (Exa retrieval on every call) — 10 scenarios × 3 models × N=10"


def sel(m=None, c=None, s=None):
    out = rows
    if m: out = [r for r in out if r["model"] == m]
    if c: out = [r for r in out if r["cell_type"] == c]
    if s: out = [r for r in out if r["scenario_id"] == s]
    return out


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=115, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {name}.png/.pdf")


# ------------------------------------------------------------------ fig 1
# Likert-style 100% stacked distribution of UNETHICAL ratings
def fig_likert():
    fig, ax = plt.subplots(figsize=(10.5, 7.6))
    colors = plt.cm.RdYlGn_r(np.linspace(0.08, 0.92, 7))
    yticks, ylabels = [], []
    y = 0
    for c in CELLS:
        # cell header row (label above the block, inside the axis)
        ax.text(0.5, y, CELL_LAB[c], fontsize=10, fontweight="bold",
                ha="left", va="center", color=CELL_C[c])
        y += 1
        for m in MODELS:
            vals = [r["unethical_rating"] for r in sel(m, c)]
            n = len(vals)
            left = 0.0
            for k in range(1, 8):
                p = 100 * sum(1 for v in vals if v == k) / n
                if p:
                    ax.barh(y, p, left=left, color=colors[k - 1], edgecolor="white", height=0.78)
                left += p
            yticks.append(y); ylabels.append(MODEL_LAB[m])
            y += 1
        y += 0.5
    ax.set_yticks(yticks); ax.set_yticklabels(ylabels, fontsize=8.5)
    ax.set_xlim(0, 100); ax.set_ylim(y - 0.8, -0.8)
    ax.set_xlabel("% of samples giving each UNETHICAL rating")
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[k]) for k in range(7)]
    ax.legend(handles, [f"{k}" for k in range(1, 8)], title="rating (1 = fine ... 7 = extremely unethical)",
              ncol=7, fontsize=8, title_fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.07))
    ax.set_title(f"Distribution of moral judgments by cell\n{TITLE_TAIL}", fontsize=11)
    save(fig, "search_likert_unethical")


# ------------------------------------------------------------------ fig 2
# Perception map: scenario-level dots + model means vs ground truth
def fig_map():
    fig, ax = plt.subplots(figsize=(8, 7.5))
    ax.axhline(4, color="gray", lw=0.7); ax.axvline(4, color="gray", lw=0.7)
    GT = {"fully_true": (6.75, 6.75), "palter": (6.75, 1.25),
          "truthy_falsehood": (1.25, 6.75), "blatant_falsehood": (1.25, 1.25)}
    for c in CELLS:
        # small dots: each scenario x model mean
        xs, ys = [], []
        for s in SCENS:
            for m in MODELS:
                sub = sel(m, c, s)
                v = [r["verbatim_rating"] for r in sub if r["verbatim_rating"]]
                g = [r["gist_rating"] for r in sub if r["gist_rating"]]
                if v and g:
                    xs.append(mean(v)); ys.append(mean(g))
        ax.scatter(xs, ys, s=16, color=CELL_C[c], alpha=0.35, linewidths=0)
        # big marker: overall cell mean
        allv = [r["verbatim_rating"] for r in sel(c=c) if r["verbatim_rating"]]
        allg = [r["gist_rating"] for r in sel(c=c) if r["gist_rating"]]
        ax.scatter([mean(allv)], [mean(allg)], s=180, color=CELL_C[c],
                   edgecolors="black", linewidths=1.2, zorder=6, label=CELL_LAB[c])
        gx, gy = GT[c]
        ax.scatter([gx], [gy], marker="D", s=260, facecolors="none",
                   edgecolors=CELL_C[c], linewidths=2.2, zorder=5)
        ax.annotate("", xy=(mean(allv), mean(allg)), xytext=(gx, gy),
                    arrowprops=dict(arrowstyle="->", color=CELL_C[c], alpha=0.55, lw=1.4))
    ax.set_xlim(0.5, 7.5); ax.set_ylim(0.5, 7.5)
    ax.set_xlabel("Perceived VERBATIM accuracy (1-7)")
    ax.set_ylabel("Perceived GIST truth (1-7)")
    ax.set_title(f"Perception map: where models place each cell in truth-space\n"
                 f"◇ = ground truth, arrow = misperception; small dots = per-scenario means\n{TITLE_TAIL}",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="center")
    save(fig, "search_perception_map")


# ------------------------------------------------------------------ fig 3
# Heatmaps: scenario x cell mean UNETHICAL, one panel per model
def fig_heatmap():
    fig, axes = plt.subplots(1, 3, figsize=(15, 6.2), sharey=True)
    for ax, m in zip(axes, MODELS):
        M = np.zeros((len(SCENS), len(CELLS)))
        for i, s in enumerate(SCENS):
            for j, c in enumerate(CELLS):
                vals = [r["unethical_rating"] for r in sel(m, c, s)]
                M[i, j] = mean(vals) if vals else np.nan
        im = ax.imshow(M, cmap="RdYlGn_r", vmin=1, vmax=7, aspect="auto")
        ax.set_xticks(range(len(CELLS)))
        ax.set_xticklabels(["WT", "PA", "TF", "BF"], fontsize=10)
        ax.set_yticks(range(len(SCENS)))
        ax.set_yticklabels([SCEN_LAB[s] for s in SCENS], fontsize=9)
        for i in range(len(SCENS)):
            for j in range(len(CELLS)):
                ax.text(j, i, f"{M[i, j]:.1f}", ha="center", va="center",
                        fontsize=8, color="black")
        ax.set_title(MODEL_LAB[m], fontsize=11)
    cbar = fig.colorbar(im, ax=axes, shrink=0.85, pad=0.015)
    cbar.set_label("mean UNETHICAL (1-7)")
    fig.suptitle(f"Scenario × cell moral-judgment heatmap — {TITLE_TAIL}", fontsize=12)
    save(fig, "search_heatmap_scenarios")


# ------------------------------------------------------------------ fig 4
# Dumbbell: perceived VERBATIM vs GIST per cell x model (the dissociation view)
def fig_dumbbell():
    fig, ax = plt.subplots(figsize=(9, 6.8))
    y = 0
    yticks, ylabels = [], []
    for c in CELLS:
        for m in MODELS:
            sub = sel(m, c)
            v = mean([r["verbatim_rating"] for r in sub if r["verbatim_rating"]])
            g = mean([r["gist_rating"] for r in sub if r["gist_rating"]])
            ax.plot([v, g], [y, y], color=CELL_C[c], lw=2.2, alpha=0.6, zorder=2)
            ax.scatter([v], [y], s=95, color=CELL_C[c], marker="o", zorder=3,
                       edgecolors="black", linewidths=0.6)
            ax.scatter([g], [y], s=95, color=CELL_C[c], marker="s", zorder=3,
                       edgecolors="black", linewidths=0.6, alpha=0.55)
            yticks.append(y); ylabels.append(MODEL_LAB[m])
            y += 1
        y += 0.8
    y = 0
    for c in CELLS:
        ax.text(7.65, y + 1.0, CELL_LAB[c], fontsize=9, fontweight="bold",
                va="center", color=CELL_C[c])
        y += 3.8
    ax.axvline(4, color="gray", ls=":", lw=0.8)
    ax.set_yticks(yticks); ax.set_yticklabels(ylabels, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0.5, 7.5)
    ax.set_xlabel("rating (1-7)")
    ax.scatter([], [], marker="o", color="gray", label="perceived VERBATIM accuracy")
    ax.scatter([], [], marker="s", color="gray", alpha=0.55, label="perceived GIST truth")
    ax.legend(fontsize=8.5, loc="lower right")
    ax.set_title(f"Verbatim-gist dissociation per cell: circle = VERBATIM, square = GIST\n"
                 f"conflict cells (PA, TF) should show wide gaps if dimensions are tracked separately\n{TITLE_TAIL}",
                 fontsize=10.5)
    save(fig, "search_dumbbell_vg")


# ------------------------------------------------------------------ fig 5
# What drives condemnation: U vs perceived V and U vs perceived G
def fig_drivers():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
    # aggregate to scenario x cell x model means
    pts = []
    for s in SCENS:
        for c in CELLS:
            for m in MODELS:
                sub = sel(m, c, s)
                v = [r["verbatim_rating"] for r in sub if r["verbatim_rating"]]
                g = [r["gist_rating"] for r in sub if r["gist_rating"]]
                u = [r["unethical_rating"] for r in sub]
                if v and g and u:
                    pts.append((mean(v), mean(g), mean(u), c, m))
    for ax, xi, lab in ((axes[0], 0, "perceived VERBATIM accuracy"),
                        (axes[1], 1, "perceived GIST truth")):
        xs = np.array([p[xi] for p in pts]); us = np.array([p[2] for p in pts])
        for c in CELLS:
            for m in MODELS:
                px = [p[xi] for p in pts if p[3] == c and p[4] == m]
                pu = [p[2] for p in pts if p[3] == c and p[4] == m]
                ax.scatter(px, pu, s=42, color=CELL_C[c], marker=MMARK[m],
                           alpha=0.75, edgecolors="white", linewidths=0.4)
        b, a = np.polyfit(xs, us, 1)
        xx = np.linspace(1, 7, 10)
        r = np.corrcoef(xs, us)[0, 1]
        ax.plot(xx, a + b * xx, color="black", lw=1.6, ls="--")
        ax.text(0.03, 0.05, f"pooled r = {r:.2f}   slope = {b:.2f}",
                transform=ax.transAxes, fontsize=10)
        ax.set_xlabel(lab); ax.set_xlim(0.5, 7.5); ax.set_ylim(0.5, 7.5)
    axes[0].set_ylabel("mean UNETHICAL (1-7)")
    cell_handles = [plt.Line2D([], [], marker="o", ls="", color=CELL_C[c],
                               label=CELL_LAB[c].split(" (")[0]) for c in CELLS]
    model_handles = [plt.Line2D([], [], marker=MMARK[m], ls="", color="gray",
                                label=MODEL_LAB[m]) for m in MODELS]
    axes[0].legend(handles=cell_handles, fontsize=8, loc="upper left")
    axes[1].legend(handles=model_handles, fontsize=8, loc="upper right")
    fig.suptitle(f"What drives condemnation: each dot = one scenario × cell × model\n{TITLE_TAIL}",
                 fontsize=11.5)
    save(fig, "search_judgment_drivers")


if __name__ == "__main__":
    fig_likert()
    fig_map()
    fig_heatmap()
    fig_dumbbell()
    fig_drivers()
