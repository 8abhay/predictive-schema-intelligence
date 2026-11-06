"""Build result tables (markdown) and figures from saved experiment outputs. No numbers are typed by hand."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_curve

import config as C
from train_eval import metrics

R = C.RESULTS_DIR
FIG = R / "figures"
FIG.mkdir(exist_ok=True)


def pm(m, s, d=3):
    return f"{m:.{d}f} ± {s:.{d}f}"


def md(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def main():
    meta = json.loads((C.DATA_DIR / "dataset_meta.json").read_text())
    df = pd.read_csv(C.DATA_DIR / "dataset.csv")
    s = pd.read_csv(R / "summary_main.csv")
    oof = pd.read_csv(R / "oof_predictions.csv")
    T = {}

    # T1 dataset
    t = pd.DataFrame({"change_type": list(meta["n_by_change_type"]),
                      "executed": list(meta["n_by_change_type"].values())})
    t["failure_rate"] = t.change_type.map(meta["failure_rate_by_change_type"]).map(lambda x: f"{x:.3f}")
    t["migration_rejected"] = t.change_type.map(lambda c: meta["rejected_by_change_type"].get(c, 0))
    T["dataset"] = md(t)

    # T2 main comparison
    rows = []
    for _, r in s.iterrows():
        rows.append({"Method": r.model, "Features": r.feature_set,
                     "Precision": pm(r.precision_mean, r.precision_std), "Recall": pm(r.recall_mean, r.recall_std),
                     "F1": pm(r.f1_mean, r.f1_std),
                     "PR-AUC": "-" if pd.isna(r.pr_auc_mean) else pm(r.pr_auc_mean, r.pr_auc_std),
                     "ROC-AUC": "-" if pd.isna(r.roc_auc_mean) else pm(r.roc_auc_mean, r.roc_auc_std),
                     "FPR": pm(r.fpr_mean, r.fpr_std), "FNR": pm(r.fnr_mean, r.fnr_std)})
    order = {"Always-fail": 0, "Rule R1 (schema-only)": 1, "Rule R2 (lineage-aware)": 2, "Logistic Regression": 3,
             "Decision Tree": 4, "Random Forest": 5, "Gradient Boosting": 6}
    t = pd.DataFrame(rows)
    t["o"] = t.Method.map(order)
    t["fo"] = t.Features.map({"-": 0, "S": 1, "S+D": 2, "S+D+P": 3})
    T["main"] = md(t.sort_values(["o", "fo"]).drop(columns=["o", "fo"]))

    # T3 pooled confusion + type_change subset
    y = oof["failed"].to_numpy()
    cm_rows, sub_rows = [], []
    methods = {"Rule R1 (schema-only)": ("Rule R1 (schema-only)|-", True), "Rule R2 (lineage-aware)": ("Rule R2 (lineage-aware)|-", True),
               "Random Forest (S)": ("Random Forest|S", False), "Random Forest (S+D)": ("Random Forest|S+D", False),
               "Random Forest (S+D+P)": ("Random Forest|S+D+P", False)}
    tc = (oof["change_type"] == "type_change").to_numpy()
    for name, (col, is_rule) in methods.items():
        pred = oof[col].to_numpy().astype(int) if is_rule else (oof[col].to_numpy() >= 0.5).astype(int)
        sc = None if is_rule else oof[col].to_numpy()
        m = metrics(y, pred, sc)
        cm_rows.append({"Method": name, "TN": m["tn"], "FP": m["fp"], "FN": m["fn"], "TP": m["tp"],
                        "Precision": f"{m['precision']:.3f}", "Recall": f"{m['recall']:.3f}", "F1": f"{m['f1']:.3f}"})
        mt = metrics(y[tc], pred[tc], None if sc is None else sc[tc])
        sub_rows.append({"Method": name, "n": mt["n"], "failures": mt["n_pos"], "TN": mt["tn"], "FP": mt["fp"],
                         "FN": mt["fn"], "TP": mt["tp"], "Precision": f"{mt['precision']:.3f}",
                         "Recall": f"{mt['recall']:.3f}", "F1": f"{mt['f1']:.3f}"})
    T["pooled"] = md(pd.DataFrame(cm_rows))
    T["typechange"] = md(pd.DataFrame(sub_rows))

    # T4 LOCTO
    l = pd.read_csv(R / "locto_metrics.csv")
    l = l[l.model.isin(["Random Forest", "Decision Tree", "Logistic Regression", "Rule R2 (lineage-aware)"])]
    piv = l.pivot(index="held_out", columns="model", values="f1").round(3)
    piv["failures"] = l.drop_duplicates("held_out").set_index("held_out")["n_pos"]
    piv["n"] = l.drop_duplicates("held_out").set_index("held_out")["n"]
    T["locto"] = md(piv.reset_index())

    # T5 prevalence
    p = pd.read_csv(R / "prevalence_sensitivity.csv")
    g = p.groupby(["prevalence", "model"])[["precision", "recall", "f1", "pr_auc"]].mean().round(3).reset_index()
    T["prevalence"] = md(g)

    # T6 robustness
    r = pd.read_csv(R / "robustness_lineage_summary.csv")
    rr = pd.DataFrame({"Hidden-job prob. q": r.q, "Method": r.model, "Precision": [pm(a, b) for a, b in zip(r.precision_mean, r.precision_std)],
                       "Recall": [pm(a, b) for a, b in zip(r.recall_mean, r.recall_std)],
                       "F1": [pm(a, b) for a, b in zip(r.f1_mean, r.f1_std)],
                       "PR-AUC": ["-" if pd.isna(a) else pm(a, b) for a, b in zip(r.pr_auc_mean, r.pr_auc_std)]})
    T["robust"] = md(rr)

    # T7 importance
    imp = pd.read_csv(R / "permutation_importance.csv").head(10)
    imp.columns = ["feature", "perm_importance_pr_auc"]
    imp["perm_importance_pr_auc"] = imp["perm_importance_pr_auc"].map(lambda x: f"{x:.4f}")
    T["importance"] = md(imp)


    # T8 calibration (Brier score, pooled out-of-fold, seed-0 folds)
    prev = float(y.mean())
    cal = [{"Predictor": "Constant prevalence (reference)", "Brier score": f"{np.mean((prev - y) ** 2):.4f}"}]
    for col, lab in [("Logistic Regression|S+D", "Logistic Regression (S+D)"), ("Decision Tree|S+D", "Decision Tree (S+D)"),
                     ("Random Forest|S", "Random Forest (S)"), ("Random Forest|S+D+P", "Random Forest (S+D+P)"),
                     ("Gradient Boosting|S+D+P", "Gradient Boosting (S+D+P)")]:
        cal.append({"Predictor": lab, "Brier score": f"{np.mean((oof[col].to_numpy() - y) ** 2):.4f}"})
    T["calibration"] = md(pd.DataFrame(cal))

    (R / "tables.md").write_text("\n\n".join(f"<!-- {k} -->\n{v}" for k, v in T.items()))
    json.dump(T, open(R / "tables.json", "w"), indent=1)

    # ---------- figures ----------
    plt.rcParams.update({"font.size": 9})
    # F1: failure rate by change type
    fr = df.groupby("change_type")["failed"].agg(["mean", "size"]).sort_values("mean")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.barh(fr.index, fr["mean"], color="#4c72b0")
    for i, (m, n) in enumerate(zip(fr["mean"], fr["size"])):
        ax.text(m + 0.01, i, f"{m:.2f} (n={n})", va="center")
    ax.set_xlim(0, 1.15); ax.set_xlabel("Observed pipeline-failure rate")
    fig.tight_layout(); fig.savefig(FIG / "fig1_failure_rate_by_change_type.png", dpi=200); plt.close(fig)

    # F2: PR curves (pooled OOF)
    fig, ax = plt.subplots(figsize=(5, 3.6))
    for col, lab in [("Random Forest|S+D+P", "RF (S+D+P)"), ("Random Forest|S", "RF (S)"),
                     ("Logistic Regression|S+D", "LR (S+D)"), ("Decision Tree|S+D", "DT (S+D)")]:
        pr, rc, _ = precision_recall_curve(y, oof[col]); ax.plot(rc, pr, label=lab)
    for col, lab, mk in [("Rule R1 (schema-only)|-", "Rule R1", "s"), ("Rule R2 (lineage-aware)|-", "Rule R2", "^")]:
        m = metrics(y, oof[col].to_numpy().astype(int)); ax.scatter(m["recall"], m["precision"], marker=mk, s=45, label=lab, zorder=5)
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.set_ylim(0.3, 1.02); ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout(); fig.savefig(FIG / "fig2_pr_curves.png", dpi=200); plt.close(fig)

    # F3: F1 by feature set x model
    fig, ax = plt.subplots(figsize=(5.5, 3.2)); w = 0.2
    models = ["Logistic Regression", "Decision Tree", "Random Forest", "Gradient Boosting"]
    for i, fs in enumerate(["S", "S+D", "S+D+P"]):
        sub = s[s.feature_set == fs].set_index("model").loc[models]
        ax.bar(np.arange(4) + (i - 1) * w, sub.f1_mean, w, yerr=sub.f1_std, label=fs, capsize=2)
    r2 = s[s.model == "Rule R2 (lineage-aware)"].f1_mean.iloc[0]
    ax.axhline(r2, color="k", ls="--", lw=1, label="Rule R2")
    ax.set_xticks(range(4)); ax.set_xticklabels(["LR", "DT", "RF", "GB"]); ax.set_ylabel("F1 (mean ± sd, 15 folds)")
    ax.set_ylim(0.5, 1.05); ax.legend(fontsize=7, ncol=4, loc="lower right")
    fig.tight_layout(); fig.savefig(FIG / "fig3_f1_by_feature_set.png", dpi=200); plt.close(fig)

    # F4: robustness
    fig, ax = plt.subplots(figsize=(5, 3.2))
    for m_ in ["Random Forest", "Decision Tree", "Logistic Regression", "Rule R2 (lineage-aware)", "Rule R1 (schema-only)"]:
        sub = r[r.model == m_]; ax.errorbar(sub.q, sub.f1_mean, yerr=sub.f1_std, marker="o", ms=3, capsize=2, label=m_)
    ax.set_xlabel("Probability q that a downstream job is missing from lineage"); ax.set_ylabel("F1")
    ax.legend(fontsize=6.5); fig.tight_layout(); fig.savefig(FIG / "fig4_lineage_robustness.png", dpi=200); plt.close(fig)

    # F5: confusion matrix RF S+D+P and R2
    fig, axs = plt.subplots(1, 2, figsize=(6, 2.8))
    for ax, (col, lab, rule) in zip(axs, [("Random Forest|S+D+P", "RF (S+D+P)", False), ("Rule R2 (lineage-aware)|-", "Rule R2", True)]):
        pred = oof[col].to_numpy().astype(int) if rule else (oof[col].to_numpy() >= 0.5).astype(int)
        cm = confusion_matrix(y, pred, labels=[0, 1]); ax.imshow(cm, cmap="Blues")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, cm[i, j], ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1]); ax.set_xticklabels(["pred ok", "pred fail"]); ax.set_yticklabels(["ok", "fail"]); ax.set_title(lab)
    fig.tight_layout(); fig.savefig(FIG / "fig5_confusion_matrices.png", dpi=200); plt.close(fig)
    print("report built")


if __name__ == "__main__":
    main()
