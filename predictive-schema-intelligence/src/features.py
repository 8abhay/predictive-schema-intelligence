"""Feature engineering.

PREDICTION TIME: after the schema change is *proposed* and before any
downstream job runs. Available: the change description, the declared/static
lineage of downstream jobs, and a profile of the CURRENT (pre-change) data.
NOT available (and never used): job outcomes, error messages, failed-job counts.
"""
from __future__ import annotations

from schema_generator import CHANGE_TYPES, TYPES, type_class

ROLES = ["select", "group", "measure", "filter", "string_fn", "date_fn", "join_key", "notnull_target"]
TYPE_CLASSES = ["none", "widening", "narrowing", "to_string", "from_string", "other"]

# Columns that describe execution outcomes: forbidden as model inputs.
OUTCOME_COLUMNS = ["failed", "n_failed_jobs", "first_error_type", "first_error_msg", "status"]


def schema_features(p, ch) -> dict:
    f = {}
    for t in CHANGE_TYPES:
        f[f"s_change_{t}"] = int(ch.change_type == t)
    for t in TYPES + ["none"]:
        f[f"s_old_{t}"] = int((ch.old_type or "none") == t)
        f[f"s_new_{t}"] = int((ch.new_type or "none") == t)
    cls = type_class(ch.old_type, ch.new_type) if ch.change_type == "type_change" else "none"
    for c in TYPE_CLASSES:
        f[f"s_tc_{c}"] = int(cls == c)
    f["s_old_nullable"] = int(bool(ch.old_nullable)) if ch.old_nullable is not None else 1
    f["s_new_nullable"] = int(bool(ch.new_nullable)) if ch.new_nullable is not None else 0
    names = [c.name for c in p.columns]
    f["s_pos_frac"] = (names.index(ch.col) / len(names)) if ch.col in names else 1.0
    f["s_n_cols"] = len(names)
    return f


def dependency_features(p, ch) -> dict:
    jobs, col = p.jobs, ch.col
    direct = [j for j in jobs if col in j.uses]
    f = {"d_n_jobs": len(jobs), "d_n_direct": len(direct),
         "d_n_positional": sum(j.positional for j in jobs)}
    for r in ROLES:
        f[f"d_role_{r}"] = sum(1 for j in jobs if r in j.uses.get(col, []))
    affected = {j.jid for j in direct}
    grew = True
    while grew:
        grew = False
        for j in jobs:
            if j.depends_on in affected and j.jid not in affected:
                affected.add(j.jid)
                grew = True
    f["d_n_affected"] = len(affected)
    depth = {}
    for j in jobs:
        depth[j.jid] = 1 + (depth.get(j.depends_on, 0) if j.depends_on is not None else 0)
    f["d_max_depth"] = max(depth.values()) if depth else 0
    return f


def profile_features(rec) -> dict:
    return {"p_null_rate": rec["p_null_rate"], "p_cast_fail_rate": rec["p_cast_fail_rate"]}


def build_row(p, ch, rec) -> dict:
    """Only (pipeline, change, pre-change profile) go in; outcomes cannot leak."""
    prof = {k: rec[k] for k in ("p_null_rate", "p_cast_fail_rate")}
    row = {"pid": ch.pid, "cid": ch.cid, "change_type": ch.change_type,
           "type_class": type_class(ch.old_type, ch.new_type) if ch.change_type == "type_change" else "none"}
    row.update(schema_features(p, ch))
    row.update(dependency_features(p, ch))
    row.update(prof)
    return row


def feature_sets(columns) -> dict:
    S = [c for c in columns if c.startswith("s_")]
    D = [c for c in columns if c.startswith("d_")]
    P = [c for c in columns if c.startswith("p_")]
    return {"S": S, "S+D": S + D, "S+D+P": S + D + P}
