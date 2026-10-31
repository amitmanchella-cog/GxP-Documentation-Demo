"""TS-004 Views, record history and seeded dataset (URS-005/006/007, FS-005/006/007)."""


def test_seed_shape(conn):
    n_s = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
    n_r = conn.execute("SELECT COUNT(*) FROM assay_results").fetchone()[0]
    assert 40 <= n_s <= 80 and 120 <= n_r <= 260
    assert conn.execute("SELECT COUNT(*) FROM audit_trail").fetchone()[0] == n_r
    oos = {r[0] for r in conn.execute("SELECT sample_id FROM assay_results WHERE oos=1")}
    assert "VC21118A-ACC-06M" in oos


def test_pages_render(client):
    for path in [
        "/",
        "/samples",
        "/samples?study=STB-2021-004&status=Reported",
        "/audit",
        "/config",
        "/samples/VC21118A-ACC-06M",
        "/results/1",
        "/api/health",
    ]:
        r = client.get(path)
        assert r.status_code == 200, path


def test_oos_visible_on_sample_page(client):
    html = client.get("/samples/VC21118A-ACC-06M").text
    assert "0.155" in html and "0.16" in html and ">OOS<" in html


def test_404s(client):
    assert client.get("/samples/NOPE").status_code == 404
    assert client.get("/results/999999").status_code == 404


def test_audit_limit_is_clamped(client):
    assert client.get("/audit?limit=-1").status_code == 200
    assert client.get("/audit?limit=-1").text.count("<tr>") <= 2


def test_schema_migration_adds_missing_columns():
    import sqlite3

    from sst.db import SCHEMA, init_schema

    c = sqlite3.connect(":memory:")
    c.executescript(
        SCHEMA.replace(
            ",\n  status TEXT NOT NULL DEFAULT 'Entered', deleted INTEGER NOT NULL DEFAULT 0",
            ",\n  status TEXT NOT NULL DEFAULT 'Entered'",
        )
    )
    c.execute("INSERT INTO schema_version(version, applied_at) VALUES (6, 'x')")
    assert "deleted" not in {r[1] for r in c.execute("PRAGMA table_info(assay_results)")}
    init_schema(c)
    assert "deleted" in {r[1] for r in c.execute("PRAGMA table_info(assay_results)")}
    assert c.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 7


def test_concurrent_requests_do_not_deadlock(client):
    from concurrent.futures import ThreadPoolExecutor

    paths = ["/samples", "/audit", "/", "/results/1", "/config"] * 6
    with ThreadPoolExecutor(max_workers=8) as ex:
        codes = list(ex.map(lambda p: client.get(p).status_code, paths))
    assert codes == [200] * len(paths)
    # a failing request must release the lock for the next one
    assert client.get("/results/999999").status_code == 404
    assert client.get("/samples").status_code == 200
