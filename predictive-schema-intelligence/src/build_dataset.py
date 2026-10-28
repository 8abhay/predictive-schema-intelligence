"""Generate synthetic pipelines, execute every schema change in DuckDB, write data/dataset.csv."""
import json
import sys
import time
from collections import Counter

import duckdb
import pandas as pd

import config as C
import execute as X
import features as F
import schema_generator as G


def build(seed=C.GLOBAL_SEED, n_pipelines=C.N_PIPELINES, n_rows=C.N_ROWS, k=C.CHANGES_PER_PIPELINE, verbose=True):
    pipelines, changes = G.generate(seed, n_pipelines, n_rows, k)
    by_pid = {}
    for ch in changes:
        by_pid.setdefault(ch.pid, []).append(ch)
    rows, outcomes = [], []
    t0 = time.time()
    for p in pipelines:
        con = X.open_pipeline(p)
        X.baseline_ok(con, p)  # raises if the generated pipeline is invalid with no change
        for ch in by_pid[p.pid]:
            rec = X.run_change(con, p, ch)
            outcomes.append(rec)
            if rec["status"] == "executed":
                row = F.build_row(p, ch, rec)
                row.update({k_: rec[k_] for k_ in F.OUTCOME_COLUMNS})
                rows.append(row)
        con.close()
        if verbose and p.pid % 100 == 0:
            print(f"pipeline {p.pid}/{n_pipelines}  {time.time()-t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    meta = {
        "seed": seed, "n_pipelines": n_pipelines, "n_rows": n_rows, "changes_per_pipeline": k,
        "fingerprint": G.fingerprint(pipelines, changes),
        "duckdb_version": duckdb.__version__,
        "n_changes_total": len(changes),
        "n_executed": int((pd.DataFrame(outcomes)["status"] == "executed").sum()),
        "n_migration_rejected": int((pd.DataFrame(outcomes)["status"] == "migration_rejected").sum()),
        "failure_rate": float(df["failed"].mean()),
        "failure_rate_by_change_type": df.groupby("change_type")["failed"].mean().round(4).to_dict(),
        "n_by_change_type": df["change_type"].value_counts().to_dict(),
        "rejected_by_change_type": dict(Counter(
            ch.change_type for ch, o in zip(changes, outcomes) if o["status"] == "migration_rejected")),
    }
    return df, meta


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else C.N_PIPELINES
    df, meta = build(n_pipelines=n)
    out_csv = C.DATA_DIR / ("dataset.csv" if n == C.N_PIPELINES else f"dataset_smoke_{n}.csv")
    df.to_csv(out_csv, index=False)
    (C.DATA_DIR / ("dataset_meta.json" if n == C.N_PIPELINES else f"dataset_smoke_{n}_meta.json")).write_text(
        json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
