"""
Visualize the complete T1 pilot cell (scenario s1, 6 models, N=10 = 240 samples).

Produces TWO separate figures:
  H2 (t1_<tag>_<scen>_h2.png): mean UNETHICAL rating by cell x model — the
     verbatim-literal inversion of the human pattern.
  H1 (t1_<tag>_<scen>_h1.png): verbatim x gist PERCEPTION MAP (mirrors Langdon
     Fig 1) — where each model places each cell vs. ground truth.

Usage: python make_figures.py --tag pilot --scenarios s1
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from statistics import mean
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
CELLS = ["fully_true", "palter", "truthy_falsehood", "blatant_falsehood"]
CELL_LABEL = {"fully_true": "Whole truth\n(V+ G+)", "palter": "Palter\n(V+ G−)",
              "truthy_falsehood": "Truthy falsehood\n(V− G+)", "blatant_falsehood": "Blatant falsehood\n(V− G−)"}
CELL_C = {"fully_true": "#2ca02c", "palter": "#ff7f0e",
          "truthy_falsehood": "#1f77b4", "blatant_falsehood": "#d62728"}
# ground-truth position in (verbatim, gist) space, on the 1-7 scale
GT = {"fully_true": (7, 7), "palter": (7, 1), "truthy_falsehood": (1, 7), "blatant_falsehood": (1, 1)}


def load(tag, scen):
    rows = [json.loads(l) for l in (HERE / "results" / f"t1_{tag}" / "samples.jsonl").open()]
    rows = [r for r in rows if r["unethical_rating"] is not None]
    if scen:
        rows = [r for r in rows if r["scenario_id"] in scen]
    return rows


def cellmean(rows, model, cell, key):
    v = [r[key] for r in rows if r["model"] == model and r["cell_type"] == cell and r[key] is not None]
    return mean(v) if v else float("nan")


def make_h2(rows, models, n_per, tag, scen_tag):
    mcolors = plt.cm.tab10(np.linspace(0, 1, len(models)))
    fig, ax = plt.subplots(figsize=(9, 6))
    x = np.arange(len(CELLS)); w = 0.8 / len(models)
    for i, m in enumerate(models):
        vals = [cellmean(rows, m, c, "unethical_rating") for c in CELLS]
        ax.bar(x + i * w - 0.4 + w / 2, vals, w, label=m, color=mcolors[i])
    ax.set_xticks(x); ax.set_xticklabels([CELL_LABEL[c] for c in CELLS], fontsize=10)
    ax.set_ylabel("Mean UNETHICAL rating  (1 = fine to post, 7 = very unethical)", fontsize=10)
    ax.set_ylim(0, 7.5)
    ax.set_title(f"H2 — Unethicality by cell ({len(models)} models)\n"
                 "Human pattern: palter HIGH, truthy LOW.  Literal pattern: the inverse.", fontsize=11)
    ax.legend(fontsize=8, ncol=2, loc="upper left")
    ax.axhline(4, color="gray", ls=":", lw=0.8)
    fig.suptitle(f"Gist-Verbatim T1 — {tag} [{scen_tag}], "
                 f"{len(models)} models × N={n_per} = {len(rows)} samples", fontsize=11, y=1.0)
    fig.tight_layout()
    out = HERE / "results" / "figures"; out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        p = out / f"t1_{tag}_{scen_tag}_h2.{ext}"
        fig.savefig(p, dpi=125, bbox_inches="tight")
        print(f"✓ wrote {p}")
    plt.close(fig)


def make_h1(rows, models, n_per, tag, scen_tag):
    fig, ax = plt.subplots(figsize=(7.5, 7))
    ax.axhline(4, color="gray", lw=0.8); ax.axvline(4, color="gray", lw=0.8)
    ax.set_xlim(0.5, 7.5); ax.set_ylim(0.5, 7.5)
    ax.set_xlabel("Perceived VERBATIM accuracy (1–7)", fontsize=10)
    ax.set_ylabel("Perceived GIST accuracy (1–7)", fontsize=10)
    ax.set_title("H1 — Verbatim × Gist perception map\n"
                 "◆ = ground truth;  ● = model perception (mean).", fontsize=11)
    # ground-truth targets (nudged off the boundary for visibility)
    for c in CELLS:
        gx, gy = GT[c]
        gxx = 6.7 if gx == 7 else 1.3; gyy = 6.7 if gy == 7 else 1.3
        ax.scatter([gxx], [gyy], marker="D", s=220, facecolors="none",
                   edgecolors=CELL_C[c], linewidths=2.2, zorder=5)
    # model perceptions (jittered so overlapping model dots separate)
    for c in CELLS:
        xs = [cellmean(rows, m, c, "verbatim_rating") for m in models]
        ys = [cellmean(rows, m, c, "gist_rating") for m in models]
        jit = (np.random.RandomState(1).rand(len(models)) - 0.5) * 0.28
        ax.scatter(np.array(xs) + jit, np.array(ys) + jit, s=48, color=CELL_C[c],
                   alpha=0.85, edgecolors="white", linewidths=0.5,
                   label=CELL_LABEL[c].replace("\n", " "))
    ax.legend(fontsize=8, loc="center left")
    ax.text(7.35, 7.35, "top-right = 'whole truth'", fontsize=7.5, ha="right", color="gray", style="italic")
    ax.text(7.35, 0.7, "bottom-right = paltering", fontsize=7.5, ha="right", color="gray", style="italic")
    fig.suptitle(f"Gist-Verbatim T1 — {tag} [{scen_tag}], "
                 f"{len(models)} models × N={n_per} = {len(rows)} samples", fontsize=11, y=1.0)
    fig.tight_layout()
    out = HERE / "results" / "figures"; out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        p = out / f"t1_{tag}_{scen_tag}_h1.{ext}"
        fig.savefig(p, dpi=125, bbox_inches="tight")
        print(f"✓ wrote {p}")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="pilot")
    ap.add_argument("--scenarios", nargs="+", default=None,
                    help="scenario ids to include; omit for ALL scenarios in the run")
    args = ap.parse_args()
    rows = load(args.tag, args.scenarios)
    models = sorted({r["model"] for r in rows})
    n_scen = len({r["scenario_id"] for r in rows})
    n_per = len(rows) // (len(models) * 4)
    scen_tag = "_".join(args.scenarios) if args.scenarios else f"all{n_scen}scen"
    make_h2(rows, models, n_per, args.tag, scen_tag)
    make_h1(rows, models, n_per, args.tag, scen_tag)


if __name__ == "__main__":
    main()
