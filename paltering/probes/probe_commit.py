"""Commit-point probes for spontaneous paltering (acts_commit: turn-2/3 episodes).

For each window (last scratchpad tokens, tool-call header, body tokens 1-8 / 9-32 / 33-96) and
the whole-reply mean, at every captured layer: AUROC honest vs paltering under two splits,
unseen scenarios (GroupKFold) and new episodes of seen scenarios (StratifiedKFold). Then the
per-token curve over the first 16 body tokens at layers 24 and 40.

Usage:  python probe_commit.py [--turn 2]  ->  results/gemma/probe_commit.log
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler

from paltering.analysis.decode_paltering import classify

D = ROOT / "results" / "gemma"
WINDOWS = ["scratch_last8", "header", "body_1_8", "body_9_32", "body_33_96", "mean", "last"]


def auroc_two_ways(X, y, g, C=0.05):
    X = np.nan_to_num(X.astype(np.float32), nan=np.nan, posinf=65504.0, neginf=-65504.0)   # clip float16 overflow in the massive-activation dim
    ok = ~np.isnan(X).any(1)
    X, y, g = X[ok], y[ok], g[ok]
    out = []
    for splitter in (GroupKFold(5).split(X, y, g), StratifiedKFold(5, shuffle=True, random_state=0).split(X, y)):
        pred = np.zeros(len(y))
        for tr, te in splitter:
            sc = StandardScaler().fit(X[tr])
            pred[te] = LogisticRegression(C=C, max_iter=4000).fit(sc.transform(X[tr]), y[tr]).decision_function(sc.transform(X[te]))
        out.append(roc_auc_score(y, pred))
    return out, int(ok.sum())


def main(a):
    z = np.load(D / "acts_commit.npz")
    idx = json.load(open(D / "acts_commit_index.json"))
    C = classify("gemma", a.turn)
    rows = [(i, r, C[(r["scenario"], r["condition"], r["model"], r["episode"])]) for i, r in enumerate(idx)
            if r["turn"] == a.turn and (r["scenario"], r["condition"], r["model"], r["episode"]) in C]
    rows = [(i, r, v) for i, r, v in rows if v["cls"] in ("honest", "paltering")]
    ii = np.array([i for i, _, _ in rows])
    y = np.array([v["cls"] == "paltering" for _, _, v in rows]).astype(int)
    g = np.array([r["scenario"] for _, r, _ in rows])
    layers = sorted({int(k.split("L")[1]) for k in z.keys() if k.startswith("mean_L")})
    print(f"turn {a.turn}: {len(y)} replies (paltering {int(y.sum())}), {len(set(g))} scenarios; AUROC unseen-scenarios / new-episodes")
    print(f"{'window':14s}" + "".join(f"{'L'+str(L):>14s}" for L in layers))
    for w in WINDOWS:
        cells = []
        for L in layers:
            X = z[f"{w}_L{L}"][ii]
            (a1, a2), n = auroc_two_ways(X, y, g)
            cells.append(f"{a1:.2f} / {a2:.2f}")
        print(f"{w:14s}" + "".join(f"{c:>14s}" for c in cells))
    print("\nper-token, first 16 body tokens (AUROC unseen-scenarios / new-episodes):")
    for L in (24, 40):
        if f"tokens_L{L}" not in z:
            continue
        T = z[f"tokens_L{L}"][ii]
        line = f"  L{L:<3d}"
        for t in range(T.shape[1]):
            (a1, a2), n = auroc_two_ways(T[:, t, :], y, g)
            line += f" t{t+1}:{a1:.2f}/{a2:.2f}"
        print(line)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--turn", type=int, default=2)
    main(ap.parse_args())
