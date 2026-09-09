"""Tactic figures: HOW models palter.

Two layers, with different completeness — kept visually separate and labelled
so nothing over-claims:

  STRUCTURAL (complete, n=6,778 — computed, no judge):
    decoy transparency  volunteering a minor drawback while the damaging fact
                        is not conveyed
    burial position     where in the reply the damaging fact appears
    fact enrichment     favourable facts conveyed minus damaging fact

  PRAGMATIC (75% of paltering coded; NO honest baseline yet):
    recontextualisation / vagueness / softening / true_reassurance / emotional

fig_t1  structural tactic profile by model   (complete data)
fig_t2  pragmatic tactics within paltering   (partial, flagged)
fig_t3  where the damaging fact sits in the reply, palter vs honest
"""
import json
import statistics as st
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
R = HERE / "results"
MODELS = ["opus5", "sonnet5", "gpt56sol", "gemini35flash"]
MLAB = {"opus5": "Claude\nOpus 5", "sonnet5": "Claude\nSonnet 5",
        "gpt56sol": "GPT-5.6", "gemini35flash": "Gemini\n3.5 Flash"}
rows = json.loads((R / "tactic_rows.json").read_text())


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_facecolor("white")
    ax.grid(False)


def act(r):
    if r["lie"]:
        return "commission"
    if r["discloses"] == "NO":
        return "omission" if r["misled"] else "honest"
    return "paltering" if r["misled"] else "honest"


PAL = [r for r in rows if act(r) == "paltering"]
HON = [r for r in rows if act(r) == "honest"]
OMI = [r for r in rows if act(r) == "omission"]

# ---------- fig_t1: structural tactics by model (COMPLETE data) ----------
fig, ax = plt.subplots(figsize=(8.6, 4.8))
W = 0.26
# decoy transparency: volunteered a minor drawback but did NOT convey the damaging fact
def decoy_rate(m):
    rr = [r for r in rows if r["model"] == m]
    n = sum(1 for r in rr if r.get("decoy") and r["discloses"] != "FULL")
    return 100 * n / len(rr) if rr else float("nan")
def enrich(m):
    rr = [r for r in rows if r["model"] == m and act(r) == "paltering"
          and "tau_pos" in r and "tau_dmg" in r]
    return st.mean([100 * (r["tau_pos"] - r["tau_dmg"]) for r in rr]) if rr else float("nan")
def burial(m):
    rr = [r for r in rows if r["model"] == m and act(r) == "paltering"
          and r.get("fact_pos") is not None]
    return 100 * st.mean([r["fact_pos"] for r in rr]) if rr else float("nan")

bars = [("decoy transparency\n(offers a lesser flaw instead)", decoy_rate, "#c0392b"),
        ("fact enrichment\n(favourable minus damaging, pts)", enrich, "#e0a458"),
        ("burial depth\n(position of fact in reply, %)", burial, "#7fa891")]
for bi, (lab, fn, col) in enumerate(bars):
    xs = [mi + (bi - 1) * W for mi in range(len(MODELS))]
    ys = [fn(m) for m in MODELS]
    ax.bar(xs, ys, W * 0.9, color=col, label=lab)
    for x, y in zip(xs, ys):
        if y == y:
            ax.annotate(f"{y:.0f}", (x, y + 0.8), ha="center", fontsize=8.5)
ax.set_xticks(range(len(MODELS)))
ax.set_xticklabels([MLAB[m] for m in MODELS], fontsize=10)
ax.set_ylabel("value (see legend units)", fontsize=10.5)
ax.legend(frameon=False, fontsize=8.5, loc="upper left", ncol=1)
style(ax)
fig.tight_layout()
fig.savefig(R / "report_figT1_structural.png", dpi=200)
fig.savefig(R / "report_figT1_structural.pdf")
plt.close(fig)

# ---------- fig_t2: pragmatic tactics within paltering (PARTIAL) ----------
tj = [json.loads(l) for l in (R / "tactic_judge" / "tactics.jsonl").open() if l.strip()]
ok = [r for r in tj if r.get("parse_ok") and r["group"] == "paltering"]
KEYS = ["recontextualisation", "vagueness", "emotional", "softening", "true_reassurance"]
KLAB = {"recontextualisation": "recontextualisation\n(fact stated, then neutralised)",
        "vagueness": "vagueness\n(specifics replaced)",
        "emotional": "unwarranted\nenthusiasm",
        "softening": "softening\n(diminishers)",
        "true_reassurance": "true reassurance\n(clean-signal citation)"}
if ok:
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    vals = [(k, 100 * sum(1 for r in ok if r[k]) / len(ok)) for k in KEYS]
    vals.sort(key=lambda x: -x[1])
    ax.barh([KLAB[k] for k, _ in vals][::-1], [v for _, v in vals][::-1],
            0.6, color="#c0392b")
    for i, (_, v) in enumerate(vals[::-1]):
        ax.annotate(f"{v:.0f}%", (v + 0.6, i), va="center", fontsize=10)
    ax.set_xlabel("share of paltering replies using the tactic (%)", fontsize=10.5)
    ax.set_xlim(0, max(v for _, v in vals) + 8)
    ax.tick_params(axis="y", labelsize=9)
    ax.annotate(f"n = {len(ok)} paltering replies (75% coded; honest baseline pending)",
                (0.99, 0.02), xycoords="axes fraction", ha="right", fontsize=8.5,
                color="#777", style="italic")
    style(ax)
    fig.tight_layout()
    fig.savefig(R / "report_figT2_pragmatic.png", dpi=200)
    fig.savefig(R / "report_figT2_pragmatic.pdf")
    plt.close(fig)

# ---------- fig_t3: burial position, paltering vs honest ----------
fig, ax = plt.subplots(figsize=(7.4, 4.4))
pp = [100 * r["fact_pos"] for r in PAL if r.get("fact_pos") is not None]
hh = [100 * r["fact_pos"] for r in HON if r.get("fact_pos") is not None]
bins = range(0, 101, 10)
ax.hist([hh, pp], bins=bins, density=True, color=["#4a7c59", "#c0392b"],
        label=[f"honest disclosure (n={len(hh)})", f"paltering (n={len(pp)})"])
ax.set_xlabel("position of the damaging fact in the reply (0 = opening, 100 = end)",
              fontsize=10.5)
ax.set_ylabel("density of replies", fontsize=10.5)
ax.legend(frameon=False, fontsize=9.5, loc="upper left")
style(ax)
fig.tight_layout()
fig.savefig(R / "report_figT3_burial.png", dpi=200)
fig.savefig(R / "report_figT3_burial.pdf")
plt.close(fig)

print("wrote report_figT1_structural, report_figT2_pragmatic, report_figT3_burial")
print(f"\nstructural (complete, n={len(rows)}):")
for m in MODELS:
    print(f"  {m:15s} decoy {decoy_rate(m):5.1f}%  enrichment {enrich(m):+6.1f}pts  "
          f"burial {burial(m):5.1f}%")
print(f"\nburial position: paltering mean {st.mean(pp):.1f}% vs honest {st.mean(hh):.1f}%")
if ok:
    print(f"\npragmatic (n={len(ok)}, partial):")
    for k, v in sorted(vals, key=lambda x: -x[1]):
        print(f"  {k:22s} {v:5.1f}%")
