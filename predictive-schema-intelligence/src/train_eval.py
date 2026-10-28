"""Train/evaluate models and rule baselines with pipeline-grouped CV.

Outputs (results/): cv_metrics.csv, summary_main.csv, oof_predictions.csv,
locto_metrics.csv, prevalence_sensitivity.csv, permutation_importance.csv,
error_analysis_*.csv, run_config.json
"""
from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

import config as C
import features as F
from baselines import RULES, r2_lineage_aware
from splits import group_folds

warnings.filterwarnings("ignore")

# Hyper-parameters fixed a priori (no tuning, to avoid optimistic bias on a small study).
def make_models(seed):
    return {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed)),
        "Decision Tree": DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, random_state=seed),
        "Random Forest": RandomForestClassifier(n_estimators=200, min_samples_leaf=2, random_state=seed, n_jobs=-1),
        "Gradient Boosting": HistGradientBoostingClassifier(random_state=seed),
    }


def metrics(y, pred, score=None):
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    out = dict(precision=prec, recall=rec, f1=f1, fpr=fp / (fp + tn) if fp + tn else 0.0,
               fnr=fn / (fn + tp) if fn + tp else 0.0, tn=tn, fp=fp, fn=fn, tp=tp, n=len(y), n_pos=int(y.sum()))
    if score is not None and 0 < y.sum() < len(y):
        out["pr_auc"] = average_precision_score(y, score)
        out["roc_auc"] = roc_auc_score(y, score)
    else:
        out["pr_auc"] = np.nan
        out["roc_auc"] = np.nan
    return out


def main():
    C.RESULTS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(C.DATA_DIR / "dataset.csv")
    assert not set(F.OUTCOME_COLUMNS) & set(c for fs in F.feature_sets(df.columns).values() for c in fs), "LEAKAGE"
    y = df["failed"].to_numpy().astype(int)
    fsets = F.feature_sets(df.columns)
    rows, oof = [], df[["pid", "cid", "change_type", "type_class", "failed", "first_error_type"]].copy()

    for seed in C.CV_SEEDS:
        folds = group_folds(df["pid"], C.CV_FOLDS, seed)
        if seed == C.CV_SEEDS[0]:
            oof["fold"] = folds
        for k in range(C.CV_FOLDS):
            te, tr = folds == k, folds != k
            for name, rule in RULES.items():
                pred = rule(df[te])
                rows.append(dict(model=name, feature_set="-", seed=seed, fold=k, **metrics(y[te], pred)))
                if seed == C.CV_SEEDS[0]:
                    oof.loc[te, f"{name}|-"] = pred
            for fs_name, cols in fsets.items():
                for mname, model in make_models(seed).items():
                    model.fit(df.loc[tr, cols], y[tr])
                    score = model.predict_proba(df.loc[te, cols])[:, 1]
                    pred = (score >= 0.5).astype(int)
                    rows.append(dict(model=mname, feature_set=fs_name, seed=seed, fold=k, **metrics(y[te], pred, score)))
                    if seed == C.CV_SEEDS[0]:
                        oof.loc[te, f"{mname}|{fs_name}"] = score
        print("done seed", seed, flush=True)

    cv = pd.DataFrame(rows)
    cv.to_csv(C.RESULTS_DIR / "cv_metrics.csv", index=False)
    oof.to_csv(C.RESULTS_DIR / "oof_predictions.csv", index=False)
    agg = cv.groupby(["model", "feature_set"])[["precision", "recall", "f1", "pr_auc", "roc_auc", "fpr", "fnr"]].agg(["mean", "std"])
    agg.columns = [f"{a}_{b}" for a, b in agg.columns]
    agg.reset_index().to_csv(C.RESULTS_DIR / "summary_main.csv", index=False)

    # ---------- Leave-one-change-type-out (pipeline-grouped, seed 0 folds) ----------
    folds0 = oof["fold"].to_numpy()
    lo_rows = []
    cols = fsets["S+D+P"]
    for ct in sorted(df["change_type"].unique()):
        held = (df["change_type"] == ct).to_numpy()
        preds = {m: np.zeros(len(df), dtype=int) for m in ["Logistic Regression", "Decision Tree", "Random Forest"]}
        for k in range(C.CV_FOLDS):
            te = (folds0 == k) & held
            tr = (folds0 != k) & ~held
            for m, model in make_models(C.CV_SEEDS[0]).items():
                if m not in preds:
                    continue
                model.fit(df.loc[tr, cols], y[tr])
                preds[m][te] = model.predict(df.loc[te, cols])
        for m, pr in preds.items():
            lo_rows.append(dict(held_out=ct, model=m, **metrics(y[held], pr[held])))
        lo_rows.append(dict(held_out=ct, model="Rule R2 (lineage-aware)", **metrics(y[held], r2_lineage_aware(df[held]))))
        lo_rows.append(dict(held_out=ct, model="Rule R1 (schema-only)", **metrics(y[held], RULES["Rule R1 (schema-only)"](df[held]))))
    pd.DataFrame(lo_rows).to_csv(C.RESULTS_DIR / "locto_metrics.csv", index=False)

    # ---------- Prevalence sensitivity (pooled out-of-fold, seed-0 folds) ----------
    prev_rows = []
    pos_idx, neg_idx = np.where(y == 1)[0], np.where(y == 0)[0]
    cands = {"Random Forest S+D+P": oof["Random Forest|S+D+P"].to_numpy(),
             "Random Forest S": oof["Random Forest|S"].to_numpy(),
             "Rule R2 (lineage-aware)": oof["Rule R2 (lineage-aware)|-"].to_numpy(),
             "Rule R1 (schema-only)": oof["Rule R1 (schema-only)|-"].to_numpy()}
    for target in [None, 0.2, 0.1, 0.05]:
        for s in range(C.PREVALENCE_SEEDS):
            rng = np.random.default_rng(1000 + s)
            if target is None:
                idx = np.arange(len(y))
            else:
                n_pos = int(round(target / (1 - target) * len(neg_idx)))
                idx = np.concatenate([neg_idx, rng.choice(pos_idx, size=min(n_pos, len(pos_idx)), replace=False)])
            for name, sc in cands.items():
                is_rule = name.startswith("Rule")
                pred = sc[idx].astype(int) if is_rule else (sc[idx] >= 0.5).astype(int)
                m = metrics(y[idx], pred, None if is_rule else sc[idx])
                prev_rows.append(dict(prevalence=("natural" if target is None else target), seed=s, model=name,
                                      actual_prevalence=y[idx].mean(), **{k_: m[k_] for k_ in ("precision", "recall", "f1", "pr_auc", "fpr")}))
            if target is None:
                break
    pd.DataFrame(prev_rows).to_csv(C.RESULTS_DIR / "prevalence_sensitivity.csv", index=False)

    # ---------- Permutation importance (Random Forest, S+D+P, per held-out fold) ----------
    imps = []
    for k in range(C.CV_FOLDS):
        te, tr = folds0 == k, folds0 != k
        rf = make_models(C.CV_SEEDS[0])["Random Forest"].fit(df.loc[tr, cols], y[tr])
        r = permutation_importance(rf, df.loc[te, cols], y[te], scoring="average_precision", n_repeats=5,
                                   random_state=C.CV_SEEDS[0])
        imps.append(pd.Series(r.importances_mean, index=cols))
    imp = pd.concat(imps, axis=1).mean(axis=1).sort_values(ascending=False)
    imp.rename("perm_importance_pr_auc").to_csv(C.RESULTS_DIR / "permutation_importance.csv")

    # ---------- Error analysis (pooled out-of-fold, seed-0 folds) ----------
    for name, col, thr in [("rf_sdp", "Random Forest|S+D+P", 0.5), ("r2", "Rule R2 (lineage-aware)|-", 0.5),
                           ("rf_s", "Random Forest|S", 0.5)]:
        pr = (oof[col] >= thr).astype(int)
        e = oof.assign(pred=pr, fn=((pr == 0) & (oof["failed"] == 1)).astype(int),
                       fp=((pr == 1) & (oof["failed"] == 0)).astype(int))
        e.groupby(["change_type", "type_class"])[["fn", "fp"]].agg(["sum"]).droplevel(1, axis=1).assign(
            n=e.groupby(["change_type", "type_class"]).size()).to_csv(C.RESULTS_DIR / f"error_analysis_{name}.csv")

    (C.RESULTS_DIR / "run_config.json").write_text(json.dumps({
        "global_seed": C.GLOBAL_SEED, "cv_seeds": list(C.CV_SEEDS), "cv_folds": C.CV_FOLDS,
        "n_rows_dataset": int(len(df)), "feature_sets": {k: len(v) for k, v in fsets.items()},
        "models": {k: str(v) for k, v in make_models(0).items()}}, indent=2))
    print(agg.round(3).to_string())


if __name__ == "__main__":
    main()
