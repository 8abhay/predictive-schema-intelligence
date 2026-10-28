"""Rule-based baselines. Defined BEFORE any experiment was run; never tuned on labels.

R1 (schema-only, Avro/registry-style): breaking if drop, rename, or a non-widening type change.
R2 (lineage-aware): R1-style logic restricted to changes that touch something downstream.
   - drop_column:   breaking if the column is explicitly referenced OR a positional (SELECT *) job exists
   - rename_column: breaking if the column is explicitly referenced
   - add_column:    breaking if a positional (SELECT *) job exists (column-count mismatch)
   - type_change:   breaking if non-widening AND (explicitly referenced OR positional job exists)
   - nullability_relax: breaking if a NOT NULL downstream target reads the column OR a positional job exists
                        (positional targets mirror source constraints)
   - nullability_tighten: not breaking
"""
import numpy as np


def r1_schema_only(df):
    return ((df["s_change_drop_column"] == 1) | (df["s_change_rename_column"] == 1) |
            ((df["s_change_type_change"] == 1) & (df["s_tc_widening"] == 0))).astype(int).to_numpy()


def r2_lineage_aware(df):
    ref = df["d_n_direct"] > 0
    pos = df["d_n_positional"] > 0
    out = np.zeros(len(df), dtype=int)
    out |= ((df["s_change_drop_column"] == 1) & (ref | pos)).to_numpy()
    out |= ((df["s_change_rename_column"] == 1) & ref).to_numpy()
    out |= ((df["s_change_add_column"] == 1) & pos).to_numpy()
    out |= ((df["s_change_type_change"] == 1) & (df["s_tc_widening"] == 0) & (ref | pos)).to_numpy()
    out |= ((df["s_change_nullability_relax"] == 1) & ((df["d_role_notnull_target"] > 0) | pos)).to_numpy()
    return out.astype(int)


def always_fail(df):
    return np.ones(len(df), dtype=int)


RULES = {"Rule R1 (schema-only)": r1_schema_only,
         "Rule R2 (lineage-aware)": r2_lineage_aware,
         "Always-fail": always_fail}
