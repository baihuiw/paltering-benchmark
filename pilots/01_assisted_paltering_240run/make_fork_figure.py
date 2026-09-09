"""Figure for the teacher-forced fork result (Llama-3.3-70B FP8).

Plots delta = mean per-token logprob(honest) - logprob(evasive) for each of the
18 continuation pairs across the three request conditions, with the paired mean
overlaid. The paired within-phrasing shift is the estimand; the per-pair LEVELS
are confounded with each pair's honest/evasive token-count gap (r = +0.64), so
the y-axis is drawn relative to each pair's own neutral value.
"""
import json
import random
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).parent / "results"
rows = json.loads((R / "forks_llama33_70b_fp8" / "scores.json").read_text())["rows"]
RUNGS = ["R0", "R1", "R2"]
LABEL = {"R0": "neutral request", "R1": "asked to be brief", "R2": "asked to persuade"}

idx = {(r["scenario_id"], r["pair"], r["rung"]): r["delta_mean"] for r in rows}
keys = sorted({(r["scenario_id"], r["pair"]) for r in rows})
sids = sorted({k[0] for k in keys})

# each pair re-centred on its own neutral value: this is exactly the paired
# estimand, and it removes the length confound that affects the levels
traj = {k: [idx[(k[0], k[1], g)] - idx[(k[0], k[1], "R0")] for g in RUNGS] for k in keys}

rng = random.Random(3)
def boot(g):
    vals = []
    for _ in range(4000):
        s = []
        for sid in rng.choices(sids, k=len(sids)):
            s += [traj[(sid, p)][RUNGS.index(g)] for p in range(3)]
        vals.append(st.mean(s))
    vals.sort()
    return vals[99], vals[3899]

fig, ax = plt.subplots(figsize=(7.2, 4.8))
x = range(len(RUNGS))
for k in keys:
    ax.plot(x, traj[k], color="#b6bcc4", lw=1.0, alpha=0.85, zorder=1)
mean = [st.mean([traj[k][i] for k in keys]) for i in range(len(RUNGS))]
ax.plot(x, mean, color="#c0392b", lw=2.8, marker="o", ms=7, zorder=3)

for i, g in enumerate(RUNGS):
    if g == "R0":
        continue
    lo, hi = boot(g)
    ax.plot([i, i], [lo, hi], color="#c0392b", lw=2.4, alpha=0.45,
            solid_capstyle="butt", zorder=2)
    off = (0, 24) if g == "R1" else (16, 0)
    ha = "center" if g == "R1" else "left"
    ax.annotate(f"{mean[i]:+.2f}  [{lo:+.2f}, {hi:+.2f}]", (i, mean[i]),
                textcoords="offset points", xytext=off, fontsize=9.5,
                color="#c0392b", va="center", ha=ha)

ax.axhline(0, color="#444", lw=1.0, ls=(0, (4, 3)), zorder=0)
ax.set_xlim(-0.18, 2.75)
ax.set_xticks(list(x))
ax.set_xticklabels([LABEL[g] for g in RUNGS], fontsize=11)
ax.set_ylabel("shift toward the honest branch\n(per-token logprob, vs. neutral)",
              fontsize=10.5)
ax.annotate("each grey line = one continuation pair (18 pairs, 6 scenarios)",
            (0.0, ax.get_ylim()[1]), textcoords="offset points", xytext=(0, -14),
            fontsize=9, color="#6b7178")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_facecolor("white")
fig.patch.set_facecolor("white")
ax.grid(False)
fig.tight_layout()
fig.savefig(R / "fig8_fork_logits.png", dpi=200)
fig.savefig(R / "fig8_fork_logits.pdf")
print("wrote fig8_fork_logits.png/pdf")
for i, g in enumerate(RUNGS):
    if g == "R0":
        continue
    lo, hi = boot(g)
    print(f"  R0 -> {g}: {mean[i]:+.4f}  [{lo:+.4f}, {hi:+.4f}]")
