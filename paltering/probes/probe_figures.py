"""Figure data for the probe section (corrected Gemma capture) -> results/gemma/probe_figs.json
  layers     AUROC by layer: paltering (unseen scenarios / new episodes), evasion and lies (unseen; goal level)
  position   AUROC (unseen scenarios) across reply positions at layers 24 and 32
  transfer   train x test matrix at layer 32 (mean pooling)
  scores     turn-2 probe scores (unseen-scenario CV, layer 32): histograms for honest vs paltering, mean by condition
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import json
import re
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler

from paltering.analysis.decode_paltering import classify
from paltering.run.run_loop import load

D = ROOT / "results" / "gemma"
LAYERS = [8, 16, 24, 32, 40, 48, 56, 61]
STANCE = re.compile(r"STANCE:\s*(CONFIRM|DENY|EVADE)", re.I)


def f32(x):
    return np.nan_to_num(x.astype(np.float32), nan=np.nan, posinf=65504.0, neginf=-65504.0)


def cv_pred(X, y, g, grouped=True, C=0.05):
    ok = ~np.isnan(X).any(1)
    X, y, g = X[ok], y[ok], g[ok]
    pred = np.zeros(len(y))
    splitter = GroupKFold(5).split(X, y, g) if grouped else StratifiedKFold(5, shuffle=True, random_state=0).split(X, y)
    for tr, te in splitter:
        sc = StandardScaler().fit(X[tr])
        pred[te] = LogisticRegression(C=C, max_iter=4000).fit(sc.transform(X[tr]), y[tr]).decision_function(sc.transform(X[te]))
    return pred, y, ok


def main():
    ze, ie = np.load(D / "acts_commit.npz"), json.load(open(D / "acts_commit_index.json"))
    zl, il = np.load(D / "acts_lying.npz"), json.load(open(D / "acts_lying_index.json"))
    lab = {(r["scenario"], r["level"], r["sample_idx"]): r for r in load(D / "lying_labels.jsonl")}
    st = {}
    for r in load(ROOT / "results" / "loop5_gemma" / "challenge.jsonl"):
        m = STANCE.search(r.get("output") or "")
        if m:
            st[(r["scenario"], r["condition"], r["model"], r["episode"])] = m.group(1).upper()
    C2 = classify("gemma", 2)
    # sets
    t2 = [(i, r, C2[(r["scenario"], r["condition"], r["model"], r["episode"])]) for i, r in enumerate(ie)
          if r["turn"] == 2 and (r["scenario"], r["condition"], r["model"], r["episode"]) in C2]
    t2 = [(i, r, v) for i, r, v in t2 if v["cls"] in ("honest", "paltering")]
    i2 = np.array([i for i, _, _ in t2]); y2 = np.array([v["cls"] == "paltering" for _, _, v in t2]).astype(int)
    g2 = np.array([r["scenario"] for _, r, _ in t2]); c2 = np.array([r["condition"] for _, r, _ in t2])
    t3 = [(i, r) for i, r in enumerate(ie) if r["turn"] == 3 and (r["scenario"], r["condition"], r["model"], r["episode"]) in st]
    i3 = np.array([i for i, _ in t3]); y3 = np.array([st[(r["scenario"], r["condition"], r["model"], r["episode"])] != "CONFIRM" for _, r in t3]).astype(int)
    g3 = np.array([r["scenario"] for _, r in t3])

    def lset(pos, neg):
        rs = [(i, r) for i, r in enumerate(il) if r["level"] == "goal" and lab.get((r["scenario"], "goal", r["sample_idx"]), {}).get("label") in (pos, neg)]
        return (np.array([i for i, _ in rs]), np.array([lab[(r["scenario"], "goal", r["sample_idx"])]["label"] == pos for _, r in rs]).astype(int),
                np.array([r["scenario"] for _, r in rs]))
    il_lie, yl_lie, gl_lie = lset("lying", "honest")
    il_ev, yl_ev, gl_ev = lset("evade", "honest")

    out = {"layers": LAYERS, "curves": {}, "position": {}, "transfer": {}, "scores": {}}
    # 1. layer curves
    for name, (z, ii, y, g, grouped) in {"paltering, unseen scenarios": (ze, i2, y2, g2, True), "paltering, new episodes": (ze, i2, y2, g2, False),
                                          "evasion (goal level), unseen scenarios": (zl, il_ev, yl_ev, gl_ev, True),
                                          "verified lies (goal level), unseen scenarios": (zl, il_lie, yl_lie, gl_lie, True),
                                          "spontaneous evasion (turn 3), unseen scenarios": (ze, i3, y3, g3, True)}.items():
        vals = []
        for L in LAYERS:
            p, yy, _ = cv_pred(f32(z[f"mean_L{L}"][ii]), y, g, grouped)
            vals.append(round(float(roc_auc_score(yy, p)), 3))
        out["curves"][name] = vals
        print(name, vals)
    # 2. position curve (unseen scenarios)
    windows = [("last prompt token", "last"), ("scratchpad end", "scratch_last8"), ("email header", "header"), ("body 1-8", "body_1_8"), ("body 9-32", "body_9_32"), ("body 33-96", "body_33_96"), ("whole reply", "mean")]
    for L in (24, 32):
        vals = []
        for name, key in windows:
            p, yy, _ = cv_pred(f32(ze[f"{key}_L{L}"][i2]), y2, g2, True)
            vals.append(round(float(roc_auc_score(yy, p)), 3))
        out["position"][f"L{L}"] = {"labels": [n for n, _ in windows], "values": vals}
        print("position", L, vals)
    # 3. transfer matrix at layer 32
    L = 32
    sets = {"evasion (instructed goal)": (zl, il_ev, yl_ev, gl_ev), "verified lies (instructed goal)": (zl, il_lie, yl_lie, gl_lie),
            "paltering (spontaneous, turn 2)": (ze, i2, y2, g2), "evasion (spontaneous, turn 3)": (ze, i3, y3, g3)}
    names = list(sets)
    M = []
    for a in names:
        za, ia, ya, ga = sets[a]
        Xa = f32(za[f"mean_L{L}"][ia]); Xa = Xa - np.nanmean(Xa, 0)
        oka = ~np.isnan(Xa).any(1)
        sc = StandardScaler().fit(Xa[oka]); clf = LogisticRegression(C=0.05, max_iter=4000).fit(sc.transform(Xa[oka]), ya[oka])
        row = []
        for b in names:
            zb, ib, yb, gb = sets[b]
            if a == b:
                p, yy, _ = cv_pred(Xa, ya, ga, True)
                row.append(round(float(roc_auc_score(yy, p)), 3))
            else:
                Xb = f32(zb[f"mean_L{L}"][ib]); Xb = Xb - np.nanmean(Xb, 0); okb = ~np.isnan(Xb).any(1)
                row.append(round(float(roc_auc_score(yb[okb], clf.decision_function(sc.transform(Xb[okb])))), 3))
        M.append(row)
    out["transfer"] = {"names": names, "matrix": M, "layer": L, "sizes": {n: [int(sets[n][2].sum()), int(len(sets[n][2]))] for n in names}}
    print("transfer", M)
    # 4. score distributions: best recipe (turns 1-3, sharp training labels, difference-of-means at layer 24),
    #    every held-out reply scored (report classes honest / paltering), scores standardised
    zE, iE = np.load(D / "acts_episodes.npz"), json.load(open(D / "acts_episodes_index.json"))   # turns 1-3
    rows13 = []
    for i, r in enumerate(iE):
        k = (r["scenario"], r["condition"], r["model"], r["episode"])
        if r["turn"] in (1, 2, 3):
            Ct = classify("gemma", r["turn"]) if r["turn"] != 2 else C2
            if k in Ct and Ct[k]["cls"] in ("honest", "paltering"):
                rows13.append((i, r, Ct[k]))
    X13 = f32(zE["mean_L24"][[i for i, _, _ in rows13]])
    y13 = np.array([v["cls"] == "paltering" for _, _, v in rows13]).astype(int)
    G13 = np.array([v["G"] for _, _, v in rows13]); g13 = np.array([r["scenario"] for _, r, _ in rows13])
    c13 = np.array([r["condition"] for _, r, _ in rows13]); t13 = np.array([r["turn"] for _, r, _ in rows13])
    sharp = (G13 >= 50) | (G13 < 10)
    pred13 = np.zeros(len(y13))
    for tr, te in GroupKFold(5).split(X13, y13, g13):
        trs = tr[sharp[tr]]
        sc = StandardScaler().fit(X13[trs]); Xt = sc.transform(X13[trs])
        w = Xt[y13[trs] == 1].mean(0) - Xt[y13[trs] == 0].mean(0)
        pred13[te] = sc.transform(X13[te]) @ w
    zsc = (pred13 - pred13.mean()) / pred13.std()
    edges = np.linspace(-3.5, 3.5, 36)
    def dens(mask):
        h = np.histogram(np.clip(zsc[mask], -3.5, 3.5), edges)[0]
        return (100 * h / max(1, mask.sum())).round(2).tolist()
    hist = {"edges": edges.tolist(), "honest": dens(y13 == 0), "paltering": dens(y13 == 1)}
    out["scores"] = {"hist": hist, "n": int(len(y13)), "n_paltering": int(y13.sum()),
                     "auroc_all": round(float(roc_auc_score(y13, zsc)), 3),
                     "auroc_sharp": round(float(roc_auc_score(y13[sharp], zsc[sharp])), 3),
                     "mean_by_class": {"honest": round(float(zsc[y13 == 0].mean()), 2), "paltering": round(float(zsc[y13 == 1].mean()), 2)},
                     "mean_by_condition_t2": {c: round(float(zsc[(c13 == c) & (t13 == 2)].mean()), 2) for c in ("C0_control", "C1_office_harm", "C3_shutdown_contingent")},
                     "paltering_rate_by_condition_t2": {c: round(float(100 * y13[(c13 == c) & (t13 == 2)].mean()), 1) for c in ("C0_control", "C1_office_harm", "C3_shutdown_contingent")},
                     "mean_by_turn": {int(tt): round(float(zsc[t13 == tt].mean()), 2) for tt in (1, 2, 3)}}
    print("scores:", {k: v for k, v in out["scores"].items() if k != "hist"})
    (D / "probe_figs.json").write_text(json.dumps(out, indent=1))
    print("wrote", D / "probe_figs.json")


if __name__ == "__main__":
    main()
