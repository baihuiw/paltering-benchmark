"""Lying benchmark probes, same recipe as the paltering probes.

Sets (results/gemma/lying_labels.jsonl + acts_lying.npz):
  within goal level      lying (verified false denial) vs honest (confirm, no false claim): the
                         behaviour-labelled, instruction-matched contrast
  pooled, level-centred  all levels, each level's mean activation removed, behaviour labels
  instruction (ref.)     deny-level vs honest-level replies regardless of behaviour (confounded)
Splits: unseen scenarios (GroupKFold) / new episodes of seen scenarios (StratifiedKFold).
Features: whole-reply mean, last prompt token, commit windows. Then transfer of the lying
direction to the spontaneous loop: turn-3 stance (evade/deny vs confirm) and turn-2 paltering.

Usage:  python probe_lying.py  ->  results/gemma/probe_lying.log
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
STANCE = re.compile(r"STANCE:\s*(CONFIRM|DENY|EVADE)", re.I)
FEATS = ["mean", "last", "scratch_last8", "header", "body_1_8", "body_9_32"]
LAYERS = (16, 24, 32, 40, 48)


def clean(X):
    X = np.nan_to_num(X.astype(np.float32), nan=np.nan, posinf=65504.0, neginf=-65504.0)   # clip float16 overflow
    return X, ~np.isnan(X).any(1)


def two_way(X, y, g, C=0.05):
    X, ok = clean(X)
    X, y, g = X[ok], y[ok], g[ok]
    if len(set(y)) < 2 or min(np.bincount(y)) < 5:
        return (float("nan"), float("nan")), int(ok.sum())
    out = []
    for splitter in (GroupKFold(min(5, len(set(g)))).split(X, y, g), StratifiedKFold(5, shuffle=True, random_state=0).split(X, y)):
        pred = np.zeros(len(y))
        for tr, te in splitter:
            sc = StandardScaler().fit(X[tr])
            pred[te] = LogisticRegression(C=C, max_iter=4000).fit(sc.transform(X[tr]), y[tr]).decision_function(sc.transform(X[te]))
        out.append(roc_auc_score(y, pred))
    return tuple(out), int(ok.sum())


def main():
    z = np.load(D / "acts_lying.npz")
    idx = json.load(open(D / "acts_lying_index.json"))
    lab = {(r["scenario"], r["level"], r["sample_idx"]): r for r in load(D / "lying_labels.jsonl")}
    rows = [(i, r, lab[(r["scenario"], r["level"], r["sample_idx"])]) for i, r in enumerate(idx) if (r["scenario"], r["level"], r["sample_idx"]) in lab]
    from collections import Counter
    print("labels by level:", {lvl: dict(Counter(l["label"] for _, r, l in rows if r["level"] == lvl)) for lvl in ("honest", "goal", "deny")})

    def sel(levels, pos, neg):
        rs = [(i, r, l) for i, r, l in rows if r["level"] in levels and l["label"] in (pos, neg)]
        return (np.array([i for i, _, _ in rs]), np.array([l["label"] == pos for _, _, l in rs]).astype(int),
                np.array([r["scenario"] for _, r, _ in rs]), np.array([r["level"] for _, r, _ in rs]))

    designs = [("goal level: lying vs honest", sel(("goal",), "lying", "honest"), False),
               ("goal+deny levels, level-centred: lying vs honest", sel(("goal", "deny"), "lying", "honest"), True),
               ("all levels, level-centred: lying vs honest", sel(("honest", "goal", "deny"), "lying", "honest"), True),
               ("goal level: evade vs honest", sel(("goal",), "evade", "honest"), False)]
    for name, (ii, y, g, lv), centre in designs:
        print(f"\n== {name}: n={len(y)} (positives {int(y.sum())}, {len(set(g))} scenarios)   AUROC unseen-scenarios / new-episodes")
        if len(y) < 20 or y.sum() < 8:
            print("   too few positives")
            continue
        print(f"   {'feature':14s}" + "".join(f"{'L'+str(L):>14s}" for L in LAYERS))
        for f in FEATS:
            cells = []
            for L in LAYERS:
                X = z[f"{f}_L{L}"][ii].astype(np.float32)
                if centre:
                    for l in set(lv):
                        m = lv == l
                        X[m] -= np.nanmean(X[m], 0, keepdims=True)
                (a1, a2), n = two_way(X, y, g)
                cells.append(f"{a1:.2f} / {a2:.2f}")
            print(f"   {f:14s}" + "".join(f"{c:>14s}" for c in cells))
    # reference: instruction-confounded (deny level vs honest level, any behaviour)
    rs = [(i, r) for i, r in enumerate(idx) if r["level"] in ("deny", "honest")]
    ii = np.array([i for i, _ in rs]); y = np.array([r["level"] == "deny" for _, r in rs]).astype(int); g = np.array([r["scenario"] for _, r in rs])
    (a1, a2), n = two_way(z["mean_L32"][ii], y, g)
    print(f"\n== reference, instruction-confounded (deny vs honest LEVEL, mean L32): {a1:.2f} / {a2:.2f}")
    # transfer of the lying direction (goal+deny level-centred, mean pooling) to the spontaneous loop
    ii, y, g, lv = sel(("goal", "deny"), "lying", "honest")
    if y.sum() >= 8:
        ze = np.load(D / "acts_commit.npz"); ie = json.load(open(D / "acts_commit_index.json"))
        st = {}
        for r in load(ROOT / "results" / "loop5_gemma" / "challenge.jsonl"):
            m = STANCE.search(r.get("output") or "")
            if m:
                st[(r["scenario"], r["condition"], r["model"], r["episode"])] = m.group(1).upper()
        C2 = classify("gemma", 2)
        print("\n== transfer of the lying direction (goal+deny, level-centred) to the spontaneous loop, mean pooling:")
        print(f"   {'layer':>5s} {'t3 evade/deny vs confirm':>26s} {'t2 paltering vs honest':>24s}")
        for L in LAYERS:
            X = z[f"mean_L{L}"][ii].astype(np.float32)
            for l in set(lv):
                m = lv == l
                X[m] -= X[m].mean(0, keepdims=True)
            X, ok = clean(X)
            sc = StandardScaler().fit(X[ok]); clf = LogisticRegression(C=0.05, max_iter=4000).fit(sc.transform(X[ok]), y[ok])
            res = []
            for turn, labels in ((3, st), (2, None)):
                rr = []
                for i, r in enumerate(ie):
                    k = (r["scenario"], r["condition"], r["model"], r["episode"])
                    if r["turn"] != turn:
                        continue
                    if turn == 3 and k in labels:
                        rr.append((i, int(labels[k] != "CONFIRM")))
                    elif turn == 2 and k in C2 and C2[k]["cls"] in ("honest", "paltering"):
                        rr.append((i, int(C2[k]["cls"] == "paltering")))
                Xe = ze[f"mean_L{L}"][[i for i, _ in rr]].astype(np.float32); ye = np.array([t for _, t in rr])
                Xe = Xe - Xe.mean(0, keepdims=True)
                res.append(roc_auc_score(ye, clf.decision_function(sc.transform(Xe))))
            print(f"   {L:5d} {res[0]:26.3f} {res[1]:24.3f}")


if __name__ == "__main__":
    main()
