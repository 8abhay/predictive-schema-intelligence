import schema_generator as G
import execute as X


def test_generation_is_deterministic():
    a = G.generate(7, 5, 40, 6)
    b = G.generate(7, 5, 40, 6)
    assert G.fingerprint(*a) == G.fingerprint(*b)
    c = G.generate(8, 5, 40, 6)
    assert G.fingerprint(*a) != G.fingerprint(*c)


def test_every_pipeline_runs_cleanly_without_a_schema_change():
    """Validity check: documented job rules must hold on the UNCHANGED schema."""
    pipelines, _ = G.generate(11, 15, 60, 3)
    for p in pipelines:
        con = X.open_pipeline(p)
        assert X.baseline_ok(con, p)
        con.close()


def test_changes_are_unique_within_pipeline():
    _, changes = G.generate(3, 5, 30, 15)
    seen = set()
    for c in changes:
        key = (c.pid, c.change_type, c.col, c.new_type)
        assert key not in seen
        seen.add(key)


def test_known_engine_behaviour_drop_referenced_column_fails():
    pipelines, changes = G.generate(5, 10, 60, 25)
    hits = 0
    for p in pipelines:
        con = X.open_pipeline(p)
        for ch in [c for c in changes if c.pid == p.pid and c.change_type == "drop_column"]:
            referenced = any(ch.col in j.uses for j in p.jobs)
            rec = X.run_change(con, p, ch)
            if referenced:
                assert rec["status"] == "executed" and rec["failed"] == 1
                hits += 1
        con.close()
    assert hits > 0
