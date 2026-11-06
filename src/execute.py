"""Execute downstream jobs in DuckDB after applying a schema change.

The label (failed = 1) is OBSERVED: at least one downstream SQL job raised an
exception. Outcome fields (n_failed_jobs, first_error_*) are post-execution
information and must never be used as model features.
"""
from __future__ import annotations

import duckdb

from config import POST_CHANGE_BATCH


def _lit(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def _src_ddl(p):
    return ", ".join(f"{c.name} {c.dtype}{'' if c.nullable else ' NOT NULL'}" for c in p.columns)


def open_pipeline(p) -> duckdb.DuckDBPyConnection:
    """One in-memory DB per pipeline; base data kept in main.base_src."""
    con = duckdb.connect(":memory:")
    con.execute(f"CREATE TABLE main.base_src ({_src_ddl(p)})")
    values = ",".join("(" + ",".join(_lit(v) if not (c.dtype == "DATE" and v is not None) else f"DATE '{v}'"
                                     for c, v in zip(p.columns, row)) + ")" for row in p.rows)
    con.execute(f"INSERT INTO main.base_src VALUES {values}")
    return con


def _fresh_run_schema(con, p):
    con.execute("DROP SCHEMA IF EXISTS run CASCADE")
    con.execute("CREATE SCHEMA run")
    con.execute("SET schema = 'run'")
    con.execute(f"CREATE TABLE src ({_src_ddl(p)})")
    con.execute("INSERT INTO src SELECT * FROM main.base_src")
    for j in p.jobs:
        for stmt in j.aux_ddl:
            con.execute(stmt)


def baseline_ok(con, p) -> bool:
    """Sanity check: with NO schema change every job must succeed."""
    _fresh_run_schema(con, p)
    for j in p.jobs:
        con.execute(j.sql)
    return True


def profile(con, ch) -> dict:
    """Pre-change data profile (available before the pipeline runs)."""
    out = {"p_null_rate": 0.0, "p_cast_fail_rate": 0.0}
    if ch.change_type == "add_column":
        return out
    c = ch.col
    r = con.execute(f"SELECT AVG(CASE WHEN {c} IS NULL THEN 1.0 ELSE 0.0 END) FROM src").fetchone()[0]
    out["p_null_rate"] = float(r or 0.0)
    if ch.change_type == "type_change":
        r = con.execute(
            f"SELECT AVG(CASE WHEN {c} IS NOT NULL AND TRY_CAST({c} AS {ch.new_type}) IS NULL THEN 1.0 "
            f"WHEN {c} IS NOT NULL THEN 0.0 END) FROM src").fetchone()[0]
        out["p_cast_fail_rate"] = float(r or 0.0)
    return out


def _apply_change(con, ch):
    t = "ALTER TABLE src "
    if ch.change_type == "drop_column":
        con.execute(t + f"DROP COLUMN {ch.col}")
    elif ch.change_type == "rename_column":
        con.execute(t + f"RENAME COLUMN {ch.col} TO {ch.new_name}")
    elif ch.change_type == "add_column":
        con.execute(t + f"ADD COLUMN {ch.col} {ch.new_type}")
    elif ch.change_type == "type_change":
        con.execute(t + f"ALTER COLUMN {ch.col} SET DATA TYPE {ch.new_type} USING TRY_CAST({ch.col} AS {ch.new_type})")
    elif ch.change_type == "nullability_relax":
        con.execute(t + f"ALTER COLUMN {ch.col} DROP NOT NULL")
        # upstream producer starts emitting NULLs in the relaxed column
        con.execute(f"INSERT INTO src SELECT * REPLACE (CAST(NULL AS {ch.old_type}) AS {ch.col}) "
                    f"FROM src LIMIT {POST_CHANGE_BATCH}")
    elif ch.change_type == "nullability_tighten":
        con.execute(t + f"ALTER COLUMN {ch.col} SET NOT NULL")
    else:
        raise ValueError(ch.change_type)


def run_change(con, p, ch) -> dict:
    _fresh_run_schema(con, p)
    rec = {"pid": ch.pid, "cid": ch.cid}
    rec.update(profile(con, ch))
    try:
        _apply_change(con, ch)
    except Exception as e:  # the DB refused the migration itself -> excluded from dataset
        rec.update(status="migration_rejected", failed=None, n_failed_jobs=None,
                   first_error_type=type(e).__name__, first_error_msg=str(e)[:120])
        return rec
    n_failed, first_type, first_msg = 0, "", ""
    for j in p.jobs:
        try:
            con.execute(j.sql)
        except Exception as e:
            n_failed += 1
            if not first_type:
                first_type, first_msg = type(e).__name__, str(e).split("\n")[0][:120]
    rec.update(status="executed", failed=int(n_failed > 0), n_failed_jobs=n_failed,
               first_error_type=first_type, first_error_msg=first_msg)
    return rec
