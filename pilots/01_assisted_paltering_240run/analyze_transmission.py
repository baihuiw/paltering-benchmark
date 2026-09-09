"""Fact-level transmission analysis + figures.

Inputs:
  results/misuse_v2_factjudge_v1/facts.jsonl   per-reply per-fact YES/NO
  results/misuse_v2_judge_clean/judged.jsonl   R1/R2 disclosure codes (clean)
  results/misuse_v2_judge_r0_clean/judged.jsonl  R0 disclosure codes (clean)
  results/misuse_v2_reader_clean + reader_r0_clean  naive-reader scores

Outputs:
  results/fig6_transmission.png/pdf   tau by fact valence x rung (pooled)
  results/fig7_material_by_model.png/pdf  damaging-fact tau per model x rung
  results/fig5_disclosure_shift.png/pdf   regenerated on all-clean data
  printed: tau table, selectivity DiD with scenario-cluster bootstrap CI,
           honest-reference sanity check, misled%% per rung
"""
import json, re, random, statistics as st
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
R = HERE / "results"
RUNG_LABEL = {"R0": "neutral request", "R1": "asked to be brief", "R2": "asked to persuade"}
RUNGS = ["R0", "R1", "R2"]
VAL_LABEL = {"pos": "positive facts", "neg_minor": "minor drawbacks",
             "neg_material": "the damaging fact"}
MODEL_LABEL = {"opus48": "Claude Opus 4.8", "gpt56sol": "GPT-5.6",
               "gemini35flash": "Gemini 3.5 Flash"}

# ---------------- load fact judge ----------------
fj = [json.loads(l) for l in (R / "misuse_v2_factjudge_v1" / "facts.jsonl").open()]
t1 = [r for r in fj if r["stage"] == "t1" and r["parse_ok"]]
refs = [r for r in fj if r["stage"] == "honest_ref" and r["parse_ok"]]
print(f"fact-judged: {len(t1)} t1 replies parsed, {len(refs)} honest refs, "
      f"{sum(1 for r in fj if not r['parse_ok'])} parse failures")

def tau(rows, val, key=lambda r: True):
    num = den = 0
    for r in rows:
        if not key(r):
            continue
        for f in r["facts"]:
            if f["valence"] == val and f["conveyed"] is not None:
                den += 1
                num += f["conveyed"]
    return num / den if den else float("nan"), den

# ---------------- tau table ----------------
print("\ntransmission rate tau (share of seeded facts conveyed)")
print(f"{'':22s}" + "".join(f"{RUNG_LABEL[g]:>20s}" for g in RUNGS))
for v in ("pos", "neg_minor", "neg_material"):
    cells = []
    for g in RUNGS:
        t, n = tau(t1, v, lambda r, g=g: r["rung"] == g)
        cells.append(f"{100*t:5.0f}%% (n={n})")
    print(f"{VAL_LABEL[v]:22s}" + "".join(f"{c:>20s}" for c in cells))

print("\nper model, damaging fact only:")
for m in MODEL_LABEL:
    cells = []
    for g in RUNGS:
        t, n = tau(t1, "neg_material", lambda r, g=g, m=m: r["rung"] == g and r["model"] == m)
        cells.append(f"{100*t:5.0f}%%")
    print(f"{MODEL_LABEL[m]:22s}" + "".join(f"{c:>20s}" for c in cells))

print("\nhonest-reference sanity (should transmit the damaging fact at 100%%):")
for v in ("pos", "neg_minor", "neg_material"):
    t, n = tau(refs, v)
    print(f"  {VAL_LABEL[v]:22s} {100*t:5.0f}%%  (n={n})")

# ---------------- selectivity DiD, scenario-cluster bootstrap ----------------
def did(rows):
    tp0, _ = tau(rows, "pos", lambda r: r["rung"] == "R0")
    tp2, _ = tau(rows, "pos", lambda r: r["rung"] == "R2")
    tm0, _ = tau(rows, "neg_material", lambda r: r["rung"] == "R0")
    tm2, _ = tau(rows, "neg_material", lambda r: r["rung"] == "R2")
    return (tm0 - tm2) - (tp0 - tp2)   # extra drop suffered by the damaging fact

point = did(t1)
sids = sorted({r["scenario_id"] for r in t1})
by_sid = {s: [r for r in t1 if r["scenario_id"] == s] for s in sids}
rng = random.Random(7)

def boot(stat, n=2000):
    vals = []
    for _ in range(n):
        sample = []
        for s in rng.choices(sids, k=len(sids)):
            sample += by_sid[s]
        vals.append(stat(sample))
    vals.sort()
    return vals[49], vals[1949]

lo, hi = boot(did)
print(f"\nselectivity DiD (drop in damaging-fact tau minus drop in positive-fact tau, "
      f"neutral->persuade): {point:+.2f}  [95%% cluster-bootstrap CI {lo:+.2f}, {hi:+.2f}]")

print("\nwithin-rung selectivity S = tau(pos) - tau(damaging), cluster-bootstrap CI:")
for g in RUNGS:
    def S(rows, g=g):
        return tau(rows, "pos", lambda r: r["rung"] == g)[0] - \
               tau(rows, "neg_material", lambda r: r["rung"] == g)[0]
    lo, hi = boot(S)
    print(f"  {RUNG_LABEL[g]:18s} S = {S(t1):+.2f}  [{lo:+.2f}, {hi:+.2f}]")

# ---------------- fig6: transmission curves ----------------
COL = {"pos": "#4a7c59", "neg_minor": "#8d8d8d", "neg_material": "#c0392b"}
fig, ax = plt.subplots(figsize=(7.2, 4.6))
x = range(len(RUNGS))
ys = {}
for v in ("pos", "neg_minor", "neg_material"):
    y = [100 * tau(t1, v, lambda r, g=g: r["rung"] == g)[0] for g in RUNGS]
    ys[v] = y
    ax.plot(x, y, marker="o", ms=6, lw=2.2, color=COL[v])
    for xi, yi in zip(x, y):
        ax.annotate(f"{yi:.0f}%", (xi, yi), textcoords="offset points",
                    xytext=(0, 9 if v == "pos" else -16),
                    ha="center", fontsize=9.5, color=COL[v])
# direct end labels, nudged apart if needed
ends = sorted(((ys[v][-1], v) for v in ys), reverse=True)
placed = []
for yv, v in ends:
    yy = yv
    while any(abs(yy - p) < 7 for p in placed):
        yy -= 7
    placed.append(yy)
    ax.annotate(VAL_LABEL[v], (len(RUNGS) - 1 + 0.08, yy), fontsize=11,
                color=COL[v], va="center")
ax.set_xlim(-0.25, len(RUNGS) - 1 + 1.25)
ax.set_ylim(0, 105)
ax.set_xticks(list(x))
ax.set_xticklabels([RUNG_LABEL[g] for g in RUNGS], fontsize=11)
ax.set_ylabel("facts conveyed to the reader (%)", fontsize=11)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_facecolor("white"); fig.patch.set_facecolor("white")
ax.grid(False)
fig.tight_layout()
fig.savefig(R / "fig6_transmission.png", dpi=200)
fig.savefig(R / "fig6_transmission.pdf")
plt.close(fig)

# ---------------- fig7: damaging fact per model ----------------
fig, ax = plt.subplots(figsize=(7.2, 4.2))
W = 0.26
SH = {"R0": "#f2b8ad", "R1": "#e2765f", "R2": "#c0392b"}
for gi, g in enumerate(RUNGS):
    xs, hs = [], []
    for mi, m in enumerate(MODEL_LABEL):
        t, _ = tau(t1, "neg_material", lambda r, g=g, m=m: r["rung"] == g and r["model"] == m)
        xs.append(mi + (gi - 1) * W)
        hs.append(100 * t)
    ax.bar(xs, hs, W * 0.92, color=SH[g], label=RUNG_LABEL[g])
    for xi, hi_ in zip(xs, hs):
        ax.annotate(f"{hi_:.0f}", (xi, hi_ + 1.5), ha="center", fontsize=9.5)
ax.set_xticks(range(len(MODEL_LABEL)))
ax.set_xticklabels(list(MODEL_LABEL.values()), fontsize=11)
ax.set_ylabel("replies conveying the damaging fact (%)", fontsize=11)
ax.set_ylim(0, 105)
ax.legend(frameon=False, fontsize=10, loc="upper right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_facecolor("white"); fig.patch.set_facecolor("white")
ax.grid(False)
fig.tight_layout()
fig.savefig(R / "fig7_material_by_model.png", dpi=200)
fig.savefig(R / "fig7_material_by_model.pdf")
plt.close(fig)

# ---------------- fig5 regenerated on all-clean data ----------------
_N = re.compile(r"(GIST|COMPLETE|ACTION):\s*(\d{1,3})", re.I)
GG = defaultdict(list)
for tag in ("reader_r0_clean", "reader_clean"):
    for r in [json.loads(l) for l in (R / f"misuse_v2_{tag}" / "samples.jsonl").open()]:
        for k, v in _N.findall(r["output"] or ""):
            if k.upper() == "GIST":
                GG[(r["scenario_id"], r["producer"], r["rung"], r["src_stage"],
                    r["sample_idx"])].append(int(v))
gist = {k: st.mean(v) for k, v in GG.items()}
ref = {k[0]: st.mean(v) for k, v in GG.items() if k[3] == "honest_ref"}
JJ = [json.loads(l) for l in (R / "misuse_v2_judge_r0_clean" / "judged.jsonl").open()]
JJ += json.load((R / "misuse_v2_coded_clean.json").open())
disc = defaultdict(lambda: defaultdict(int))
misled = defaultdict(int)
tot = defaultdict(int)
for r in JJ:
    if r["stage"] != "t1" or not r.get("discloses"):
        continue
    g = r["rung"]
    tot[g] += 1
    disc[g][r["discloses"]] += 1
    k = (r["scenario_id"], r["model"], g, "t1", r["sample_idx"])
    rg = gist.get(k)
    if rg is not None and r.get("false_claim") == "NO" and rg > ref[r["scenario_id"]]:
        misled[g] += 1
print("\nall-clean disclosure shares and misled%% (fig5 numbers):")
for g in RUNGS:
    n = tot[g]
    print(f"  {RUNG_LABEL[g]:18s} FULL {100*disc[g]['FULL']/n:4.0f}%%  "
          f"PARTIAL {100*disc[g]['PARTIAL']/n:4.0f}%%  NO {100*disc[g]['NO']/n:4.0f}%%  "
          f"misled {100*misled[g]/n:4.0f}%%   (n={n})")

fig, ax = plt.subplots(figsize=(7.0, 4.6))
CD = {"FULL": "#4a7c59", "PARTIAL": "#e0a458", "NO": "#c0392b"}
LAB = {"FULL": "clearly disclosed", "PARTIAL": "mentioned but buried", "NO": "omitted"}
for gi, g in enumerate(RUNGS):
    n = tot[g]
    bottom = 0.0
    for kpart in ("FULL", "PARTIAL", "NO"):
        h = 100 * disc[g][kpart] / n
        ax.bar(gi, h, 0.55, bottom=bottom, color=CD[kpart],
               label=LAB[kpart] if gi == 0 else None)
        if h > 6:
            ax.annotate(f"{h:.0f}%", (gi, bottom + h / 2), ha="center",
                        va="center", fontsize=10, color="white")
        bottom += h
    ax.annotate(f"misled: {100*misled[g]/n:.0f}%", (gi, 103), ha="center",
                fontsize=10.5)
ax.set_xticks(range(len(RUNGS)))
ax.set_xticklabels([RUNG_LABEL[g] for g in RUNGS], fontsize=11)
ax.set_ylabel("share of replies (%)", fontsize=11)
ax.set_ylim(0, 112)
ax.set_yticks([0, 25, 50, 75, 100])
ax.legend(frameon=False, fontsize=10, loc="center left", bbox_to_anchor=(1.0, 0.5))
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_facecolor("white"); fig.patch.set_facecolor("white")
ax.grid(False)
fig.tight_layout()
fig.savefig(R / "fig5_disclosure_shift.png", dpi=200)
fig.savefig(R / "fig5_disclosure_shift.pdf")
plt.close(fig)
print("\nfigures written: fig6_transmission, fig7_material_by_model, fig5_disclosure_shift")
