import numpy as np
import pandas as pd
import features as F
import schema_generator as G
import execute as X
from baselines import r1_schema_only, r2_lineage_aware
from splits import group_folds


def test_no_outcome_column_is_a_feature():
    pipelines, changes = G.generate(2, 3, 40, 5)
    p = pipelines[0]
    con = X.open_pipeline(p)
    rec = X.run_change(con, p, changes[0])
    row = F.build_row(p, changes[0], rec)
    row.update({k: rec[k] for k in F.OUTCOME_COLUMNS})
    df = pd.DataFrame([row])
    all_feats = {c for cols in F.feature_sets(df.columns).values() for c in cols}
    assert not all_feats & set(F.OUTCOME_COLUMNS)


def test_features_do_not_depend_on_execution_outcome():
    pipelines, changes = G.generate(2, 3, 40, 5)
    p, ch = pipelines[0], changes[0]
    rec = {"p_null_rate": 0.1, "p_cast_fail_rate": 0.0}
    a = F.build_row(p, ch, {**rec, "failed": 1, "n_failed_jobs": 9})
    b = F.build_row(p, ch, {**rec, "failed": 0, "n_failed_jobs": 0})
    assert a == b


def test_group_folds_never_split_a_pipeline():
    groups = np.repeat(np.arange(50), 20)
    folds = group_folds(groups, 5, seed=1)
    for g in range(50):
        assert len(set(folds[groups == g])) == 1
    assert set(folds) == {0, 1, 2, 3, 4}


def test_rule_baselines_basic_semantics():
    cols = F.feature_sets(pd.DataFrame(columns=["s_a"]))  # smoke
    base = {"s_change_drop_column": 0, "s_change_rename_column": 0, "s_change_add_column": 0,
            "s_change_type_change": 0, "s_change_nullability_relax": 0, "s_tc_widening": 0,
            "d_n_direct": 0, "d_n_positional": 0, "d_role_notnull_target": 0}
    drop_ref = pd.DataFrame([{**base, "s_change_drop_column": 1, "d_n_direct": 2}])
    drop_unref = pd.DataFrame([{**base, "s_change_drop_column": 1}])
    assert r1_schema_only(drop_ref)[0] == 1 and r1_schema_only(drop_unref)[0] == 1
    assert r2_lineage_aware(drop_ref)[0] == 1 and r2_lineage_aware(drop_unref)[0] == 0
    widen = pd.DataFrame([{**base, "s_change_type_change": 1, "s_tc_widening": 1, "d_n_direct": 3}])
    assert r1_schema_only(widen)[0] == 0 and r2_lineage_aware(widen)[0] == 0
