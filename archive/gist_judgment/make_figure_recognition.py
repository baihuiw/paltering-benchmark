"""
Recognition profile, redesigned for readability.

Three panels, each a plain-English question, ONE uniform color code everywhere:
  green = answered correctly
  gray  = said it cannot tell / "something else"
  red   = answered wrongly

  Panel 1  "Can it verify the specific facts?"   (R1, WITH web search)
  Panel 2  "Does it see what the reply implies?" (R2, offline by design)
  Panel 3  "Does it know which gist is true?"    (R3, offline)

Usage: python make_figure_recognition.py
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "results" / "figures"

CELLS = ["fully_true", "palter", "truthy_falsehood", "blatant_falsehood"]
CELL_FULL = {"fully_true": "Whole truth", "palter": "Palter",
             "truthy_falsehood": "Truthy falsehood", "blatant_falsehood": "Blatant falsehood"}
MODELS = ["gemini3pro", "gpt55", "opus48"]
MODEL_LAB = {"gemini3pro": "Gemini", "gpt55": "GPT-5.5", "opus48": "Opus"}

C_RIGHT, C_UNSURE, C_WRONG = "#2e7d32", "#bdbdbd", "#c62828"

r1s = [json.loads(l) for l in (HERE / "results" / "recognition_pilot10_r1_search" / "samples.jsonl").open()]
off = [json.loads(l) for l in (HERE / "results" / "recognition_pilot10_recog" / "samples.jsonl").open()]


def pct3(right, unsure, wrong):
    n = right + unsure + wrong
    if n == 0:
        return 0, 0, 0
    return 100 * right / n, 100 * unsure / n, 100 * wrong / n


def r1_row(m, c):
    sub = [r for r in r1s if r["task"] == "r1" and r["model"] == m
           and r["cell_type"] == c and r.get("verdict")]
    if not sub:
        return 0, 0, 0
    want = "ACCURATE" if sub[0]["verbatim_truth"] else "INACCURATE"
    right = sum(1 for r in sub if r["verdict"] == want)
    unsure = sum(1 for r in sub if r["verdict"] == "CANNOT_VERIFY")
    return pct3(right, unsure, len(sub) - right - unsure)


def r2_row(m, c):
    sub = [r for r in off if r["task"] == "r2" and r["model"] == m
           and r["cell_type"] == c and r.get("choice")]
    if not sub:
        return 0, 0, 0
    want = "true_gist" if sub[0]["gist_truth"] else "false_gist"
    right = sum(1 for r in sub if r["choice"] == want)
    unsure = sum(1 for r in sub if r["choice"] == "other")
    return pct3(right, unsure, len(sub) - right - unsure)


def r3_row(m, kind):
    sub = [r for r in off if r["task"] == "r3" and r["model"] == m
           and r["gist_kind"] == kind and r.get("verdict")]
    if not sub:
        return 0, 0, 0
    want = "TRUE" if kind == "true_gist" else "FALSE"
    right = sum(1 for r in sub if r["verdict"] == want)
    unsure = sum(1 for r in sub if r["verdict"] == "CANNOT_VERIFY")
    return pct3(right, unsure, len(sub) - right - unsure)


def draw_panel(ax, blocks, title):
    """blocks: list of (block_label, [(row_label, (right, unsure, wrong)), ...])"""
    y = 0
    yticks, ylabels = [], []
    for blab, rows_ in blocks:
        ax.text(1, y, blab, fontsize=10, fontweight="bold", ha="left", va="center")
        y += 1
        for rlab, (g, u, w) in rows_:
            ax.barh(y, g, color=C_RIGHT, height=0.72)
            ax.barh(y, u, left=g, color=C_UNSURE, height=0.72)
            ax.barh(y, w, left=g + u, color=C_WRONG, height=0.72)
            for val, left in ((g, 0), (u, g), (w, g + u)):
                if val >= 14:
                    ax.text(left + val / 2, y, f"{val:.0f}", ha="center", va="center",
                            fontsize=7.5, color="white", fontweight="bold")
            yticks.append(y); ylabels.append(rlab)
            y += 1
        y += 0.45
    ax.set_yticks(yticks); ax.set_yticklabels(ylabels, fontsize=8.5)
    ax.set_ylim(y - 0.7, -0.7)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of samples", fontsize=9)
    ax.set_title(title, fontsize=10.5)


fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16.5, 7),
                                    gridspec_kw={"width_ratios": [1, 1, 0.72]})

draw_panel(ax1,
           [(CELL_FULL[c], [(MODEL_LAB[m], r1_row(m, c)) for m in MODELS]) for c in CELLS],
           "1. Can it verify the specific facts?\n(R1, WITH web search — partial data)")
draw_panel(ax2,
           [(CELL_FULL[c], [(MODEL_LAB[m], r2_row(m, c)) for m in MODELS]) for c in CELLS],
           "2. Does it see what the reply implies to a reader?\n(R2 gist extraction, offline by design)")
draw_panel(ax3,
           [("The TRUE gist  (is it true?)", [(MODEL_LAB[m], r3_row(m, "true_gist")) for m in MODELS]),
            ("The FALSE gist  (is it false?)", [(MODEL_LAB[m], r3_row(m, "false_gist")) for m in MODELS])],
           "3. Does it know which gist is true?\n(R3 gist evaluation, offline)")

handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (C_RIGHT, C_UNSURE, C_WRONG)]
fig.legend(handles, ["answered correctly", "said it can't tell / 'something else'", "answered wrongly"],
           ncol=3, fontsize=10, loc="lower center", bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Do the models recognize the truth of the items?   "
             "(10 scenarios × 3 frontier models; R1 n≈20/bar until full re-run)",
             fontsize=12.5, y=0.99)
fig.tight_layout(rect=[0, 0.04, 1, 0.96])
OUT.mkdir(parents=True, exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(OUT / f"recognition_profile.{ext}", dpi=112, bbox_inches="tight")
print("✓ recognition_profile.png/.pdf")
