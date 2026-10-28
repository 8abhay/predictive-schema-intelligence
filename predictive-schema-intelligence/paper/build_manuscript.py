"""Fill paper/manuscript_template.md with numbers/tables computed from results/ (nothing typed by hand)."""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
R, D = ROOT / "results", ROOT / "data"
meta = json.loads((D / "dataset_meta.json").read_text())
T = json.loads((R / "tables.json").read_text())
s = pd.read_csv(R / "summary_main.csv").set_index(["model", "feature_set"])
rob = pd.read_csv(R / "robustness_lineage_summary.csv").set_index(["model", "q"])
oof = pd.read_csv(R / "oof_predictions.csv")
cfg = json.loads((R / "run_config.json").read_text())


def f1(m, fs):
    r = s.loc[(m, fs)]
    return f"{r.f1_mean:.3f} ± {r.f1_std:.3f}"


def rf1(m, q):
    r = rob.loc[(m, q)]
    return f"{r.f1_mean:.3f}"


y = oof["failed"].to_numpy()
r2 = oof["Rule R2 (lineage-aware)|-"].to_numpy().astype(int)
rf = (oof["Random Forest|S+D+P"].to_numpy() >= 0.5).astype(int)
tc = (oof["change_type"] == "type_change").to_numpy()
V = {
    "N_PIPE": meta["n_pipelines"], "N_ROWS": meta["n_rows"], "N_CHANGES": meta["n_changes_total"],
    "N_EXEC": meta["n_executed"], "N_REJ": meta["n_migration_rejected"],
    "FAIL_RATE": f"{100*meta['failure_rate']:.1f}%", "DUCKDB": meta["duckdb_version"],
    "FP_CS": f"{cfg['feature_sets']['S']}", "FP_SD": f"{cfg['feature_sets']['S+D']}", "FP_SDP": f"{cfg['feature_sets']['S+D+P']}",
    "AF_F1": f1("Always-fail", "-"), "R1_F1": f1("Rule R1 (schema-only)", "-"), "R2_F1": f1("Rule R2 (lineage-aware)", "-"),
    "LR_S": f1("Logistic Regression", "S"), "LR_SD": f1("Logistic Regression", "S+D"),
    "DT_S": f1("Decision Tree", "S"), "DT_SD": f1("Decision Tree", "S+D"),
    "RF_S": f1("Random Forest", "S"), "RF_SD": f1("Random Forest", "S+D"), "RF_SDP": f1("Random Forest", "S+D+P"),
    "GB_S": f1("Gradient Boosting", "S"), "GB_SDP": f1("Gradient Boosting", "S+D+P"),
    "R2_FP": int(((r2 == 1) & (y == 0)).sum()), "R2_FN": int(((r2 == 0) & (y == 1)).sum()),
    "R2_FP_TC": int(((r2 == 1) & (y == 0) & tc).sum()),
    "RF_FP": int(((rf == 1) & (y == 0)).sum()), "RF_FN": int(((rf == 0) & (y == 1)).sum()),
    "N_TC_FAIL": int(((y == 1) & tc).sum()), "N_TC": int(tc.sum()), "N_POOLED": len(y),
    "ROB_RF_25": rf1("Random Forest", 0.25), "ROB_RF_50": rf1("Random Forest", 0.5), "ROB_RF_75": rf1("Random Forest", 0.75),
    "ROB_R2_25": rf1("Rule R2 (lineage-aware)", 0.25), "ROB_R2_50": rf1("Rule R2 (lineage-aware)", 0.5),
    "ROB_R2_75": rf1("Rule R2 (lineage-aware)", 0.75),
}
txt = (Path(__file__).parent / "manuscript_template.md").read_text()
txt = re.sub(r"\{\{table:(\w+)\}\}", lambda m: T[m.group(1)], txt)
txt = re.sub(r"\{\{(\w+)\}\}", lambda m: str(V[m.group(1)]), txt)
(Path(__file__).parent / "manuscript.md").write_text(txt)
print("manuscript.md written;", len(txt.split()), "words")
