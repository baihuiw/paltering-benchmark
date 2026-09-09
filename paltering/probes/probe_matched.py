"""Instruction-matched intent probe.

Within ONE instruction condition of the contrast set, replies vary in behaviour (the favourable-
instructed model sometimes discloses the critical fact anyway; the honesty-instructed one
sometimes omits it). Training on disclosed-vs-omitted within a condition holds the instruction
constant, so the direction cannot be "is the honesty instruction present". Three trainings:
  fav      within favourable-instructed replies
  hon      within honesty-instructed replies
  both     both conditions, each centred to its own mean (instruction offset removed)
Each direction is evaluated (a) by scenario-grouped CV inside its training set and (b) applied
to the spontaneous turn-2 / turn-3 replies: AUROC paltering vs honest, Spearman with reader GIST.

Usage:  python probe_matched.py  (needs results/gemma/contrast_d1.jsonl from contrast_d1.py)
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

from paltering.analysis.decode_paltering import classify

D = ROOT / "results" / "gemma"
LAYERS = (8, 16, 24, 32, 40, 48, 56, 61)


def cv(X, y, g):
    if len(set(g)) < 5 or y.sum() < 5 or (1 - y).sum() < 5:
        return float("nan")
    pred = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g):
        sc = StandardScaler().fit(X[tr])
        pred[te] = LogisticRegression(C=0.5, max_iter=4000).fit(sc.transform(X[tr]), y[tr]).decision_function(sc.transform(X[te]))
    return roc_auc_score(y, pred)


def main():
    zc, ic = np.load(D / "acts_contrast.npz"), json.load(open(D / "acts_contrast_index.json"))
    lab = {(r["scenario"], r["query"], r["label"], r["sample_idx"]): r["disclosed"] for r in map(json.loads, (D / "contrast_d1.jsonl").open())}
    rows = [(i, r, lab.get((r["scenario"], r["query"], r["label"], r["sample_idx"]))) for i, r in enumerate(ic)]
    rows = [(i, r, d) for i, r, d in rows if d is not None]
    for cond in ("honest", "deceptive"):
        n = [d for _, r, d in rows if r["label"] == cond]
        print(f"contrast {cond:9s}: {len(n)} judged, disclosed D1 in {100*sum(n)/len(n):.0f}%")
    ze, ie = np.load(D / "acts_episodes.npz"), json.load(open(D / "acts_episodes_index.json"))
    C = {t: classify("gemma", t) for t in (2, 3)}
    ep = [(i, r, C[r["turn"]][(r["scenario"], r["condition"], r["model"], r["episode"])]) for i, r in enumerate(ie)
          if r["turn"] in C and (r["scenario"], r["condition"], r["model"], r["episode"]) in C[r["turn"]]]
    ep = [(i, r, v) for i, r, v in ep if v["cls"] in ("honest", "paltering")]
    ei = np.array([i for i, _, _ in ep]); ey = np.array([v["cls"] == "paltering" for _, _, v in ep]).astype(int); eG = np.array([v["G"] for _, _, v in ep])
    et = np.array([r["turn"] for _, r, _ in ep])
    print(f"spontaneous replies: {len(ep)} (paltering {int(ey.sum())}); turn 2: {int((et==2).sum())}, turn 3: {int((et==3).sum())}\n")
    print(f"{'train':6s} {'layer':>5s} {'CV in-set':>9s} | {'AUROC t2':>8s} {'rho t2':>7s} | {'AUROC t3':>8s} {'rho t3':>7s}")
    for train in ("fav", "hon", "both"):
        for L in LAYERS:
            if train == "both":
                parts = []
                for cond in ("honest", "deceptive"):
                    sel = [(i, d) for i, r, d in rows if r["label"] == cond]
                    X = zc[f"mean_L{L}"][[i for i, _ in sel]]
                    parts.append((X - X.mean(0, keepdims=True), np.array([0 if d else 1 for _, d in sel]), np.array([ic[i]["scenario"] for i, _ in sel])))
                X = np.vstack([p[0] for p in parts]); y = np.concatenate([p[1] for p in parts]); g = np.concatenate([p[2] for p in parts])
                Xmean = np.zeros(X.shape[1])
            else:
                cond = "deceptive" if train == "fav" else "honest"
                sel = [(i, d) for i, r, d in rows if r["label"] == cond]
                X = zc[f"mean_L{L}"][[i for i, _ in sel]]
                y = np.array([0 if d else 1 for _, d in sel])      # 1 = critical fact NOT disclosed (the paltering behaviour)
                g = np.array([ic[i]["scenario"] for i, _ in sel])
                Xmean = X.mean(0)
            auc_in = cv(X, y, g)
            sc = StandardScaler().fit(X)
            clf = LogisticRegression(C=0.5, max_iter=4000).fit(sc.transform(X), y)
            Xe = ze[f"mean_L{L}"][ei]
            Xe = Xe - Xe.mean(0, keepdims=True) + Xmean          # centre the episodes to the training set
            s = clf.decision_function(sc.transform(Xe))
            r2 = (roc_auc_score(ey[et == 2], s[et == 2]), spearmanr(s[et == 2], eG[et == 2]).correlation)
            r3 = (roc_auc_score(ey[et == 3], s[et == 3]), spearmanr(s[et == 3], eG[et == 3]).correlation)
            print(f"{train:6s} {L:5d} {auc_in:9.3f} | {r2[0]:8.3f} {r2[1]:+7.3f} | {r3[0]:8.3f} {r3[1]:+7.3f}")


if __name__ == "__main__":
    main()
