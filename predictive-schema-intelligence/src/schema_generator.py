"""Synthetic pipeline + schema-change generator.

EVERYTHING produced here is SYNTHETIC. No production data is used.
Failure labels are NOT assigned here: they come from actually executing the
downstream SQL jobs in DuckDB (see execute.py).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta

import numpy as np

TYPES = ["INTEGER", "BIGINT", "DOUBLE", "VARCHAR", "DATE", "BOOLEAN"]
NUMERIC = {"INTEGER", "BIGINT", "DOUBLE"}
TRANSITIONS = {
    "INTEGER": ["BIGINT", "DOUBLE", "VARCHAR"],
    "BIGINT": ["INTEGER", "DOUBLE", "VARCHAR"],
    "DOUBLE": ["INTEGER", "BIGINT", "VARCHAR"],
    "VARCHAR": ["INTEGER", "DOUBLE", "DATE"],
    "DATE": ["VARCHAR"],
    "BOOLEAN": ["INTEGER", "VARCHAR"],
}
# Avro-style numeric promotions treated as "widening" (compatible) by rule baselines.
WIDENING = {("INTEGER", "BIGINT"), ("INTEGER", "DOUBLE"), ("BIGINT", "DOUBLE")}
CHANGE_TYPES = ["drop_column", "rename_column", "add_column", "type_change",
                "nullability_relax", "nullability_tighten"]
JOB_KINDS = ["proj", "agg", "filter", "strfn", "datefn", "join", "load_notnull",
             "star_insert", "chain"]
WORDS = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
         "india", "juliet", "kilo", "lima"]


def type_class(old, new) -> str:
    if old is None or new is None or old == new:
        return "none"
    if (old, new) in WIDENING:
        return "widening"
    if new == "VARCHAR":
        return "to_string"
    if old == "VARCHAR":
        return "from_string"
    if old in NUMERIC and new in NUMERIC:
        return "narrowing"
    return "other"


@dataclass
class Column:
    name: str
    dtype: str
    nullable: bool
    null_rate: float
    vkind: str | None = None   # for VARCHAR: text | numstr | mixed
    code: bool = False         # low-cardinality integer (0..49), usable as join key


@dataclass
class Job:
    jid: int
    kind: str
    sql: str
    uses: dict                 # column -> list of roles (static lineage)
    depends_on: int | None = None
    positional: bool = False   # reads source columns by position (SELECT *)
    aux_ddl: list = field(default_factory=list)


@dataclass
class Pipeline:
    pid: int
    columns: list
    jobs: list
    rows: list                 # list of row lists (python values)

    def col(self, name):
        return next(c for c in self.columns if c.name == name)


@dataclass
class Change:
    pid: int
    cid: int
    change_type: str
    col: str | None
    old_type: str | None
    new_type: str | None
    old_nullable: bool | None
    new_nullable: bool | None
    new_name: str | None


def _make_columns(rng):
    n_cols = int(rng.integers(6, 13))
    required = ["INTEGER", "DOUBLE", "VARCHAR", "DATE"]
    extra = [str(t) for t in rng.choice(TYPES, size=n_cols - 1 - len(required))]
    types = required + extra
    rng.shuffle(types)
    cols = [Column("id", "BIGINT", False, 0.0)]
    for i, t in enumerate(types, start=1):
        t = str(t)
        nullable = bool(rng.random() < 0.5)
        null_rate = float(rng.choice([0.0, 0.05, 0.2])) if nullable else 0.0
        vkind = str(rng.choice(["text", "numstr", "mixed"], p=[0.5, 0.3, 0.2])) if t == "VARCHAR" else None
        code = bool(t in ("INTEGER", "BIGINT") and rng.random() < 0.5)
        cols.append(Column(f"{t[:3].lower()}_{i}", t, nullable, null_rate, vkind, code))
    return cols


def _make_rows(cols, rng, n_rows):
    rows = []
    for r in range(n_rows):
        row = []
        for c in cols:
            if c.name == "id":
                row.append(r + 1)
                continue
            if c.nullable and rng.random() < c.null_rate:
                row.append(None)
                continue
            if c.dtype in ("INTEGER", "BIGINT"):
                row.append(int(rng.integers(0, 50)) if c.code else int(rng.integers(0, 1000)))
            elif c.dtype == "DOUBLE":
                row.append(round(float(rng.uniform(0, 1000)), 2))
            elif c.dtype == "VARCHAR":
                if c.vkind == "text":
                    row.append(str(rng.choice(WORDS)))
                elif c.vkind == "numstr":
                    row.append(str(int(rng.integers(0, 1000))))
                else:
                    row.append("n/a" if rng.random() < 0.15 else str(int(rng.integers(0, 1000))))
            elif c.dtype == "DATE":
                row.append((date(2020, 1, 1) + timedelta(days=int(rng.integers(0, 1500)))).isoformat())
            else:
                row.append(bool(rng.random() < 0.5))
        rows.append(row)
    return rows


def _ddl_cols(cols):
    return ", ".join(f"{c.name} {c.dtype}{'' if c.nullable else ' NOT NULL'}" for c in cols)


def _make_jobs(cols, rng):
    n_jobs = int(rng.integers(3, 9))
    by_type = lambda *ts: [c for c in cols if c.dtype in ts]
    jobs = []
    star_used = False
    attempts = 0
    while len(jobs) < n_jobs and attempts < 60:
        attempts += 1
        j = len(jobs)
        kind = str(rng.choice(JOB_KINDS))
        out = f"out_{j}"
        if kind == "proj":
            sel = [cols[int(i)].name for i in rng.choice(len(cols), size=int(rng.integers(2, 5)), replace=False)]
            jobs.append(Job(j, kind, f"CREATE TABLE {out} AS SELECT {', '.join(sel)} FROM src",
                            {n: ["select"] for n in sel}))
        elif kind == "agg":
            gp = [c for c in cols if c.dtype != "DOUBLE"]
            g = gp[int(rng.integers(0, len(gp)))]
            m_pool = [c for c in by_type("DOUBLE", "INTEGER", "BIGINT") if c.name != g.name]
            if not m_pool:
                continue
            m = m_pool[int(rng.integers(0, len(m_pool)))]
            jobs.append(Job(j, kind, f"CREATE TABLE {out} AS SELECT {g.name}, SUM({m.name}) AS s FROM src GROUP BY {g.name}",
                            {g.name: ["group"], m.name: ["measure"]}))
        elif kind == "filter":
            pool = by_type("DOUBLE", "INTEGER", "BIGINT")
            n = pool[int(rng.integers(0, len(pool)))]
            sel = [cols[int(i)].name for i in rng.choice(len(cols), size=int(rng.integers(1, 3)), replace=False)]
            uses = {s: ["select"] for s in sel}
            uses.setdefault(n.name, []).append("filter")
            jobs.append(Job(j, kind, f"CREATE TABLE {out} AS SELECT {', '.join(sel)} FROM src WHERE {n.name} > 100", uses))
        elif kind == "strfn":
            pool = by_type("VARCHAR")
            s = pool[int(rng.integers(0, len(pool)))]
            jobs.append(Job(j, kind, f"CREATE TABLE {out} AS SELECT UPPER({s.name}) AS u, LENGTH({s.name}) AS l FROM src",
                            {s.name: ["string_fn"]}))
        elif kind == "datefn":
            pool = by_type("DATE")
            d = pool[int(rng.integers(0, len(pool)))]
            jobs.append(Job(j, kind, f"CREATE TABLE {out} AS SELECT EXTRACT(year FROM {d.name}) AS y FROM src",
                            {d.name: ["date_fn"]}))
        elif kind == "join":
            pool = [c for c in cols if c.code]
            if not pool:
                continue
            k = pool[int(rng.integers(0, len(pool)))]
            jobs.append(Job(j, kind,
                            f"CREATE TABLE {out} AS SELECT s.{k.name} AS k, d.label FROM src s JOIN dim_{j} d ON s.{k.name} = d.k",
                            {k.name: ["join_key"]},
                            aux_ddl=[f"CREATE TABLE dim_{j} (k {k.dtype}, label VARCHAR)",
                                     f"INSERT INTO dim_{j} SELECT i, 'L' || i FROM range(0, 200) t(i)"]))
        elif kind == "load_notnull":
            pool = [c for c in cols if c.null_rate == 0.0]
            c = pool[int(rng.integers(0, len(pool)))]
            jobs.append(Job(j, kind, f"INSERT INTO tgt_{j} SELECT {c.name} FROM src", {c.name: ["notnull_target"]},
                            aux_ddl=[f"CREATE TABLE tgt_{j} ({c.name} {c.dtype} NOT NULL)"]))
        elif kind == "star_insert":
            if star_used:
                continue
            star_used = True
            jobs.append(Job(j, kind, f"INSERT INTO tgt_{j} SELECT * FROM src", {}, positional=True,
                            aux_ddl=[f"CREATE TABLE tgt_{j} ({_ddl_cols(cols)})"]))
        elif kind == "chain":
            parents = [x for x in jobs if x.kind == "proj"]
            if not parents:
                continue
            p = parents[int(rng.integers(0, len(parents)))]
            c1 = list(p.uses.keys())[0]
            jobs.append(Job(j, kind, f"CREATE TABLE {out} AS SELECT {c1}, COUNT(*) AS n FROM out_{p.jid} GROUP BY {c1}",
                            {}, depends_on=p.jid))
    return jobs


def make_pipeline(pid, rng, n_rows):
    for _ in range(100):
        cols = _make_columns(rng)
        jobs = _make_jobs(cols, rng)
        if len(jobs) >= 3:
            return Pipeline(pid, cols, jobs, _make_rows(cols, rng, n_rows))
    raise RuntimeError("could not generate a valid pipeline")


def candidate_changes(p):
    cands = []
    for c in p.columns:
        cands.append(dict(change_type="drop_column", col=c.name, old_type=c.dtype, new_type=None,
                          old_nullable=c.nullable, new_nullable=None, new_name=None))
        cands.append(dict(change_type="rename_column", col=c.name, old_type=c.dtype, new_type=None,
                          old_nullable=c.nullable, new_nullable=None, new_name=f"{c.name}_v2"))
        for t in TRANSITIONS[c.dtype]:
            cands.append(dict(change_type="type_change", col=c.name, old_type=c.dtype, new_type=t,
                              old_nullable=c.nullable, new_nullable=c.nullable, new_name=None))
        if c.name != "id":
            if not c.nullable:
                cands.append(dict(change_type="nullability_relax", col=c.name, old_type=c.dtype, new_type=None,
                                  old_nullable=False, new_nullable=True, new_name=None))
            elif c.null_rate == 0.0:
                cands.append(dict(change_type="nullability_tighten", col=c.name, old_type=c.dtype, new_type=None,
                                  old_nullable=True, new_nullable=False, new_name=None))
    for t in ["INTEGER", "VARCHAR", "DOUBLE"]:
        cands.append(dict(change_type="add_column", col=f"new_{t[:3].lower()}", old_type=None, new_type=t,
                          old_nullable=None, new_nullable=True, new_name=None))
    return cands


def sample_changes(p, rng, k):
    cands = candidate_changes(p)
    idx = rng.choice(len(cands), size=min(k, len(cands)), replace=False)
    return [Change(p.pid, cid, **cands[int(i)]) for cid, i in enumerate(sorted(idx))]


def generate(seed, n_pipelines, n_rows, k):
    rng = np.random.default_rng(seed)
    pipelines, changes = [], []
    for pid in range(n_pipelines):
        p = make_pipeline(pid, rng, n_rows)
        pipelines.append(p)
        changes.extend(sample_changes(p, rng, k))
    return pipelines, changes


def fingerprint(pipelines, changes) -> str:
    blob = json.dumps({"p": [asdict(p) for p in pipelines], "c": [asdict(c) for c in changes]},
                      sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()
