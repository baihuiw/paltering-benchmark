"""
Search-arm versions of the remaining EDA panels (same plot style as the grid),
saved as INDIVIDUAL figures:

  search_wt_verification  (panel C analog) — WT-cell VERBATIM rating per
      scenario under search; dotted line = correct (7). Shows where retrieval
      verification succeeds and where it still fails.
  search_palter_by_scenario (panel F analog) — palter UNETHICAL per scenario
      (search arm, mean of 3 models), sorted.

Panels D (joint vs isolated ethics) and E (R1-R3 recognition) have no
search-arm data: the ethics-only and recognition runs were offline-only.

Usage: python make_figures_search_extra.py
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
SCEN_LAB = {"s1": "climate", "s2": "jobs", "s4": "inflation", "s12": "border", "s13": "crime",
            "s17": "ukraine", "s18": "college", "s21": "AI stocks", "s23": "vaccines", "s26": "crypto"}
SCENS = list(SCEN_LAB)
MODELS = ["gemini3pro", "gpt55", "opus48"]
MC = {"gemini3pro": "#4285F4", "gpt55": "#10a37f", "opus48": "#d97706"}
TAIL = "search arm (Exa retrieval on every call) — 10 scenarios × 3 models × N=10"

rows = [json.loads(l) for l in (HERE / "results" / "t1_pilot10_t1_search" / "samples.jsonl").open()]
rows = [r for r in rows if r["unethical_rating"] is not None]


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=115, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {name}.png/.pdf")


# ---- C analog: WT-cell verbatim verification under search, per scenario ----
def fig_wt_verification():
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(SCENS)); w = 0.26
    for i, m in enumerate(MODELS):
        vals = []
        for s in SCENS:
            v = [r["verbatim_rating"] for r in rows
                 if r["model"] == m and r["scenario_id"] == s
                 and r["cell_type"] == "fully_true" and r.get("verbatim_rating")]
            vals.append(mean(v) if v else np.nan)
        ax.bar(x + (i - 1) * w, vals, w, label=m, color=MC[m])
    ax.axhline(7, color="green", ls=":", lw=1.0)
    ax.text(len(SCENS) - 0.4, 7.06, "correct = 7", color="green", fontsize=8, ha="right")
    ax.set_xticks(x); ax.set_xticklabels([SCEN_LAB[s] for s in SCENS], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("WT-cell VERBATIM rating (1-7)")
    ax.set_ylim(0, 7.6)
    ax.set_title(f"Verification of true current-fact statements WITH retrieval\n"
                 f"whole-truth cells only; {TAIL}", fontsize=11)
    ax.legend(fontsize=8)
    save(fig, "search_wt_verification")


# ---- F analog: palter unethicality by scenario (search arm) ----
def fig_palter_by_scenario():
    fig, ax = plt.subplots(figsize=(10, 6))
    pv = []
    for s in SCENS:
        v = [r["unethical_rating"] for r in rows
             if r["scenario_id"] == s and r["cell_type"] == "palter"]
        pv.append(mean(v) if v else np.nan)
    order = np.argsort(pv)[::-1]
    ax.bar(np.arange(len(SCENS)), [pv[i] for i in order], color="#ff7f0e")
    for i, oi in enumerate(order):
        ax.text(i, pv[oi] + 0.1, f"{pv[oi]:.1f}", ha="center", fontsize=8.5)
    ax.set_xticks(np.arange(len(SCENS)))
    ax.set_xticklabels([SCEN_LAB[SCENS[i]] for i in order], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Palter UNETHICAL (1-7)")
    ax.set_ylim(0, 7)
    ax.axhline(4, color="gray", ls=":", lw=0.8)
    ax.set_title(f"Which palters get condemned vs waved through\n"
                 f"palter cells, mean of 3 models; {TAIL}", fontsize=11)
    save(fig, "search_palter_by_scenario")


if __name__ == "__main__":
    fig_wt_verification()
    fig_palter_by_scenario()
