"""Recipe sweep for the spontaneous-paltering probe (Gemma activations already on disk).

Everything is scenario-grouped 5-fold CV. Dimensions swept:
  data      turn 2 only | turns 1-3
  labels    all (paltering vs honest) | sharp (reader GIST >= 50 vs GIST < 10)
  features  mean_L | last_L | mean+last | mean concat over layers 24/32/40 | delta (t2 - t1 mean, same episode)
  centring  none | per-scenario (subtract the scenario's mean activation)
  model     logistic regression (C) | mass-mean direction | ridge regression on GIST (AUROC at the label)
Then a temporal check for the best few: train on turn 2, test on turn 3.

Usage:  python probe_recipe.py  ->  results/gemma/probe_recipe.log
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import json
import statistics as st
from itertools import product
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

from paltering.analysis.decode_paltering import classify

D = ROOT / "results" / "gemma"
LAYERS = (8, 16, 24, 32, 40, 48, 56, 61)


def load():
    z = np.load(D / "acts_episodes.npz")
    idx = json.load(open(D / "acts_episodes_index.json"))
    C = {t: classify("gemma", t) for t in (1, 2, 3)}
    rows = []
    for i, r in enumerate(idx):
        k = (r["scenario"], r["condition"], r["model"], r["episode"])
        if r["turn"] in C and k in C[r["turn"]]:
            v = C[r["turn"]][k]
            rows.append({"i": i, "turn": r["turn"], "scenario": r["scenario"], "ep": k, "cls": v["cls"], "G": v["G"]})
    return z, rows


def features(z, rows, kind, L):
    ii = np.array([r["i"] for r in rows])
    if kind == "mean":
        return z[f"mean_L{L}"][ii]
    if kind == "last":
        return z[f"last_L{L}"][ii]
    if kind == "mean+last":
        return np.hstack([z[f"mean_L{L}"][ii], z[f"last_L{L}"][ii]])
    if kind == "concat":
        return np.hstack([z[f"mean_L{l}"][ii] for l in (24, 32, 40)])
    raise ValueError(kind)


def center_by_scenario(X, rows):
    X = X.copy()
    by = {}
    for j, r in enumerate(rows):
        by.setdefault(r["scenario"], []).append(j)
    for js in by.values():
        X[js] -= X[js].mean(0, keepdims=True)
    return X


def cv_auroc(X, y, g, model, G=None):
    pred = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g):
        sc = StandardScaler().fit(X[tr])
        Xtr, Xte = sc.transform(X[tr]), sc.transform(X[te])
        if model.startswith("lr"):
            C = float(model.split(":")[1])
            pred[te] = LogisticRegression(C=C, max_iter=4000).fit(Xtr, y[tr]).decision_function(Xte)
        elif model == "massmean":
            w = Xtr[y[tr] == 1].mean(0) - Xtr[y[tr] == 0].mean(0)
            pred[te] = Xte @ w
        elif model == "ridge":
            pred[te] = Ridge(alpha=1000.0).fit(Xtr, G[tr]).predict(Xte)
    return roc_auc_score(y, pred), pred


def main():
    z, rows = load()
    out = []
    print(f"{len(rows)} classified turn-1..3 replies")
    configs = []
    for data, labels, kind, centre, model in product(("t2", "t123"), ("all", "sharp"), ("mean", "last", "mean+last", "concat"),
                                                     ("none", "scenario"), ("lr:0.5", "lr:0.05", "massmean", "ridge")):
        configs.append((data, labels, kind, centre, model))
    print(f"{len(configs)} configurations x layers; scenario-grouped 5-fold CV\n")
    best = []
    for data, labels, kind, centre, model in configs:
        rs = [r for r in rows if (r["turn"] == 2 if data == "t2" else r["turn"] in (1, 2, 3))]
        if labels == "all":
            rs = [r for r in rs if r["cls"] in ("honest", "paltering")]
            y = np.array([r["cls"] == "paltering" for r in rs]).astype(int)
        else:
            rs = [r for r in rs if (r["cls"] == "paltering" and r["G"] >= 50) or (r["cls"] == "honest" and r["G"] < 10)]
            y = np.array([r["cls"] == "paltering" for r in rs]).astype(int)
        if kind == "delta":
            continue
        g = np.array([r["scenario"] for r in rs])
        Gv = np.array([r["G"] for r in rs])
        layer_list = [None] if kind == "concat" else LAYERS
        res = {}
        for L in layer_list:
            X = features(z, rs, kind, L)
            if centre == "scenario":
                X = center_by_scenario(X, rs)
            auc, _ = cv_auroc(X, y, g, model, Gv)
            res[L] = auc
        Lb = max(res, key=res.get)
        best.append((res[Lb], data, labels, kind, centre, model, Lb, int(y.sum()), len(y)))
    best.sort(reverse=True)
    print(f"{'AUROC':>6s}  {'data':5s} {'labels':6s} {'feat':10s} {'centre':9s} {'model':9s} {'layer':>5s} {'n_pal':>6s} {'n':>5s}")
    for b in best[:25]:
        print(f"{b[0]:6.3f}  {b[1]:5s} {b[2]:6s} {b[3]:10s} {b[4]:9s} {b[5]:9s} {str(b[6]):>5s} {b[7]:6d} {b[8]:5d}")
    print("\nbaseline (turn 2, all, mean, none, lr:0.5):", [f"{b[0]:.3f}" for b in best if b[1:6] == ("t2", "all", "mean", "none", "lr:0.5")])
    # delta features: t2 - t1 of the same episode (mean pooling), all labels at t2
    print("\nwithin-episode delta (t2 mean - t1 mean), turn-2 labels:")
    t1 = {r["ep"]: r["i"] for r in rows if r["turn"] == 1}
    rs = [r for r in rows if r["turn"] == 2 and r["cls"] in ("honest", "paltering") and r["ep"] in t1]
    y = np.array([r["cls"] == "paltering" for r in rs]).astype(int)
    g = np.array([r["scenario"] for r in rs])
    for L in LAYERS:
        X = z[f"mean_L{L}"][[r["i"] for r in rs]] - z[f"mean_L{L}"][[t1[r["ep"]] for r in rs]]
        for model in ("lr:0.5", "massmean"):
            auc, _ = cv_auroc(X, y, g, model)
            print(f"  layer {L:2d} {model:9s} AUROC {auc:.3f}")
    # temporal check for the top-3 turn-2-trainable configs: train on turn 2, test on turn 3
    print("\ntemporal check (train turn 2 -> test turn 3) for the top configurations trained on turn 2:")
    top = [b for b in best if b[1] == "t2"][:3]
    for b in top:
        _, data, labels, kind, centre, model, L, _, _ = b
        def prep(turn):
            rs = [r for r in rows if r["turn"] == turn and r["cls"] in ("honest", "paltering")]
            if labels == "sharp":
                rs = [r for r in rs if (r["cls"] == "paltering" and r["G"] >= 50) or (r["cls"] == "honest" and r["G"] < 10)]
            X = features(z, rs, kind, L)
            if centre == "scenario":
                X = center_by_scenario(X, rs)
            return X, np.array([r["cls"] == "paltering" for r in rs]).astype(int), np.array([r["G"] for r in rs])
        X2, y2, G2 = prep(2)
        X3, y3, G3 = prep(3)
        sc = StandardScaler().fit(X2)
        if model.startswith("lr"):
            pred = LogisticRegression(C=float(model.split(":")[1]), max_iter=4000).fit(sc.transform(X2), y2).decision_function(sc.transform(X3))
        elif model == "massmean":
            Xt = sc.transform(X2)
            pred = sc.transform(X3) @ (Xt[y2 == 1].mean(0) - Xt[y2 == 0].mean(0))
        else:
            pred = Ridge(alpha=1000.0).fit(sc.transform(X2), G2).predict(sc.transform(X3))
        print(f"  {labels:6s} {kind:10s} {centre:9s} {model:9s} L{L}: CV {b[0]:.3f} -> turn-3 test AUROC {roc_auc_score(y3, pred):.3f}, rho with GIST {spearmanr(pred, G3).correlation:+.3f}")


if __name__ == "__main__":
    main()
