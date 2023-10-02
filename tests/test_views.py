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
