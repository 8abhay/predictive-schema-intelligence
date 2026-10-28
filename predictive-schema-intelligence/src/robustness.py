"""Lineage-incompleteness robustness check.

Real lineage catalogs are rarely complete. Here each downstream job is HIDDEN from the
dependency features with probability q (labels are unchanged: hidden jobs still run and can still fail).
Models are trained and tested on the degraded features; rule R2 is recomputed on them too.
"""
import copy
import json

import numpy as np
import pandas as pd

import config as C
import features as F
import schema_generator as G
from baselines import RULES
from splits import group_folds
from train_eval import make_models, metrics

QS = [0.0, 0.25, 0.5, 0.75]


def degraded_frame(pipelines, changes, base_df, q, seed):
    rng = np.random.default_rng(seed)
    hidden_p = {}
    for p in pipelines:
        keep = [j for j in p.jobs if rng.random() >= q]
        pc = copy.copy(p)
        pc.jobs = keep
        hidden_p[p.pid] = pc
    keys = set(zip(base_df.pid, base_df.cid))
    rows = []
    for ch in changes:
        if (ch.pid, ch.cid) in keys:
            rows.append({"pid": ch.pid, "cid": ch.cid, **F.dependency_features(hidden_p[ch.pid], ch)})
    d = pd.DataFrame(rows)
    out = base_df[["pid", "cid", "failed"] + [c for c in base_df.columns if c.startswith("s_")]].merge(d, on=["pid", "cid"])
    return out


def main():
    base = pd.read_csv(C.DATA_DIR / "dataset.csv")
    pipelines, changes = G.generate(C.GLOBAL_SEED, C.N_PIPELINES, C.N_ROWS, C.CHANGES_PER_PIPELINE)
    rows = []
    for q in QS:
        df = degraded_frame(pipelines, changes, base, q, seed=7000 + int(q * 100))
        cols = F.feature_sets(df.columns)["S+D"]
        y = df["failed"].to_numpy().astype(int)
        for seed in C.CV_SEEDS:
            folds = group_folds(df["pid"], C.CV_FOLDS, seed)
            for k in range(C.CV_FOLDS):
                te, tr = folds == k, folds != k
                for rn in ["Rule R1 (schema-only)", "Rule R2 (lineage-aware)"]:
                    rows.append(dict(q=q, model=rn, seed=seed, fold=k, **metrics(y[te], RULES[rn](df[te]))))
                for mn, m in make_models(seed).items():
                    if mn == "Gradient Boosting":
                        continue
                    m.fit(df.loc[tr, cols], y[tr])
                    sc = m.predict_proba(df.loc[te, cols])[:, 1]
                    rows.append(dict(q=q, model=mn, seed=seed, fold=k, **metrics(y[te], (sc >= 0.5).astype(int), sc)))
        print("q =", q, "done", flush=True)
    r = pd.DataFrame(rows)
    r.to_csv(C.RESULTS_DIR / "robustness_lineage_cv.csv", index=False)
    s = r.groupby(["q", "model"])[["precision", "recall", "f1", "pr_auc"]].agg(["mean", "std"])
    s.columns = [f"{a}_{b}" for a, b in s.columns]
    s.reset_index().to_csv(C.RESULTS_DIR / "robustness_lineage_summary.csv", index=False)
    print(s.round(3).to_string())


if __name__ == "__main__":
    main()
