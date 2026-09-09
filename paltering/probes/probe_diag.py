"""Diagnose and repair the intent probe.

The instructed contrast (honest-instructed vs favourable-impression-instructed) separates at
AUROC 1.0 from layer 8 and scores every base-prompt episode ~1.0: the probe reads the presence
of the instruction, not the intent. Three checks per layer, mean-over-reply pooling:
  1. instructed probe, episodes CENTRED to the contrast mean before scoring -> does the within-
     episode variation along that direction track behaviour (AUROC honest vs paltering, and
     Spearman with reader GIST) at turn 2?
  2. behaviour probe: trained on Gemma's own turn-2 replies (honest vs paltering, reader-based),
     GroupKFold by scenario -> is spontaneous paltering linearly decodable at all?
  3. cosine between the instructed direction and the behaviour direction (shared scaler).
Usage:  python probe_diag.py --tag gemma
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

from paltering.analysis.decode_paltering import classify



def lr():
    return LogisticRegression(C=0.5, max_iter=3000)


def main(a):
    d = ROOT / "results" / "gemma"
    ze, ie = np.load(d / "acts_episodes.npz"), json.load(open(d / "acts_episodes_index.json"))
    zc, ic = np.load(d / "acts_contrast.npz"), json.load(open(d / "acts_contrast_index.json"))
    yc = np.array([1 if r["label"] == "deceptive" else 0 for r in ic])
    C2 = classify(a.tag, 2)
    # turn-2 episode rows with a behavioural class
    rows = [(i, r, C2[(r["scenario"], r["condition"], r["model"], r["episode"])]) for i, r in enumerate(ie)
            if r["turn"] == 2 and (r["scenario"], r["condition"], r["model"], r["episode"]) in C2]
    keep = [(i, r, v) for i, r, v in rows if v["cls"] in ("honest", "paltering")]
    idx = np.array([i for i, _, _ in keep])
    yb = np.array([1 if v["cls"] == "paltering" else 0 for _, _, v in keep])
    G = np.array([v["G"] for _, _, v in keep])
    grp = np.array([r["scenario"] for _, r, _ in keep])
    press = np.array([r["condition"] != "C0_control" for _, r, _ in keep])
    print(f"turn-2 episodes with class: {len(keep)} (paltering {int(yb.sum())}, honest {int((1-yb).sum())}), {len(set(grp))} scenarios")
    layers = sorted(int(k.split("L")[1]) for k in ze.keys() if k.startswith("mean_L"))
    print(f"\n{'layer':>5s} | {'instructed, centred':^40s} | {'behaviour probe (grouped CV)':^30s} | cos")
    print(f"{'':>5s} | {'AUROC pal/hon':>13s} {'rho GIST':>9s} {'mean C0':>8s} {'mean C1+3':>9s} | {'AUROC all':>10s} {'AUROC C0':>9s} {'AUROC press':>11s} |")
    for L in layers:
        Xc, Xe = zc[f"mean_L{L}"], ze[f"mean_L{L}"][idx]
        # 1. instructed probe, centred scoring
        sc = StandardScaler().fit(Xc)
        clf = lr().fit(sc.transform(Xc), yc)
        Xe_c = Xe - Xe.mean(0, keepdims=True) + Xc.mean(0, keepdims=True)
        s = clf.decision_function(sc.transform(Xe_c))
        auc1 = roc_auc_score(yb, s)
        rho = spearmanr(s, G).correlation
        m0, m1 = s[~press].mean(), s[press].mean()
        # 2. behaviour probe, grouped CV
        def cv(mask):
            X, y, g = Xe[mask], yb[mask], grp[mask]
            if len(set(y)) < 2 or len(set(g)) < 5:
                return float("nan")
            pred = np.zeros(len(y))
            for tr, te in GroupKFold(n_splits=5).split(X, y, g):
                s2 = StandardScaler().fit(X[tr])
                pred[te] = lr().fit(s2.transform(X[tr]), y[tr]).decision_function(s2.transform(X[te]))
            return roc_auc_score(y, pred)
        auc_all, auc_c0, auc_pr = cv(np.ones(len(yb), bool)), cv(~press), cv(press)
        # 3. cosine between directions in a shared standardized space
        sh = StandardScaler().fit(np.vstack([Xc, Xe]))
        w_i = lr().fit(sh.transform(Xc), yc).coef_[0]
        w_b = lr().fit(sh.transform(Xe), yb).coef_[0]
        cos = float(w_i @ w_b / (np.linalg.norm(w_i) * np.linalg.norm(w_b)))
        print(f"{L:5d} | {auc1:13.3f} {rho:9.3f} {m0:8.2f} {m1:9.2f} | {auc_all:10.3f} {auc_c0:9.3f} {auc_pr:11.3f} | {cos:+.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="gemma")
    main(ap.parse_args())
