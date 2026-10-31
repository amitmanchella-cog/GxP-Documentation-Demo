"""CHG-4127 Part 11 / SOP-DI-004 s6 audit-trail verification for result amendment (TS-006).

Findings F1, F2, F3, F7 on PR #6. 21 CFR 11.10(e): audit trail captures who, when, old/new value and
reason, is computer-generated, cannot be altered, and does not obscure the original value.
"""

import pytest

from sst import audit

ANALYST = {"X-User": "mfarouk"}
SUPERVISOR = {"X-User": "adiallo"}
REASON = "Transcription error corrected against instrument printout"
VERIFY_REASON = "Checked amendment against raw chromatography data"
AMENDABLE_COLUMNS = ("measured_value", "reportable_value", "oos", "status")


@pytest.fixture()
def nmt015(conn):
    """Seeded OOS result against NMT 0.15 (measured 0.155 -> reportable 0.16, OOS)."""
    row = conn.execute(
        "SELECT r.result_id FROM assay_results r JOIN specifications sp ON sp.spec_id=r.spec_id"
        " WHERE sp.upper_limit='0.15' AND r.measured_value='0.155' AND r.deleted=0"
    ).fetchone()
    return row["result_id"]


@pytest.fixture()
def range_result(conn):
    """Seeded in-spec result against a two-sided 95.0-105.0 limit."""
    row = conn.execute(
        "SELECT r.result_id FROM assay_results r JOIN specifications sp ON sp.spec_id=r.spec_id"
        " WHERE sp.lower_limit='95.0' AND sp.upper_limit='105.0' AND r.oos=0 AND r.deleted=0 LIMIT 1"
    ).fetchone()
    return row["result_id"]


def _updates(conn, rid):
    return conn.execute(
        "SELECT * FROM audit_trail WHERE entity='assay_result' AND entity_id=? AND action='update'"
        " ORDER BY audit_id",
        (str(rid),),
    ).fetchall()


def _all_audit(conn):
    return [tuple(r) for r in conn.execute("SELECT * FROM audit_trail ORDER BY audit_id")]


def _result(conn, rid):
    row = conn.execute(
        "SELECT measured_value, reportable_value, oos, status FROM assay_results WHERE result_id=?", (rid,)
    ).fetchone()
    return {k: str(row[k]) for k in AMENDABLE_COLUMNS}


def _api_amend(client, rid, value, reason=REASON, headers=ANALYST):
    return client.patch(
        f"/api/results/{rid}", json={"measured_value": value, "reason": reason}, headers=headers
    )


# SOP-DI-004 s6(a) / F1: one audit row per field actually changed, no more, no less
@pytest.mark.parametrize(
    "fixture,value",
    [("nmt015", "0.154"), ("nmt015", "0.1551"), ("range_result", "100.23"), ("range_result", "94.94")],
)
def test_amend_writes_one_audit_row_per_changed_field(client, conn, request, fixture, value):
    rid = request.getfixturevalue(fixture)
    before = _result(conn, rid)
    assert _api_amend(client, rid, value).status_code == 200
    after = _result(conn, rid)
    changed = [c for c in AMENDABLE_COLUMNS if before[c] != after[c]]
    fields = [a["field"] for a in _updates(conn, rid)]
    assert "measured_value" in changed
    assert sorted(fields) == sorted(changed)
    assert len(fields) == len(set(fields))


# SOP-DI-004 s6(a) / F1, F3: who, when (UTC), record, field, old and new value, reason
def test_amend_audit_captures_old_and_new_values(client, conn, nmt015):
    before = _result(conn, nmt015)
    assert _api_amend(client, nmt015, "0.154").status_code == 200
    after = _result(conn, nmt015)
    rows = {a["field"]: a for a in _updates(conn, nmt015)}
    assert set(rows) == set(AMENDABLE_COLUMNS)
    for field, a in rows.items():
        assert a["old_value"] == before[field]
        assert a["new_value"] == after[field]
        assert a["actor"] == "mfarouk"
        assert a["entity"] == "assay_result" and a["entity_id"] == str(nmt015)
        assert a["reason"] == REASON
        assert a["ts"].endswith("Z") and "T" in a["ts"]
    assert (rows["measured_value"]["old_value"], rows["measured_value"]["new_value"]) == ("0.155", "0.154")
    assert rows["status"]["new_value"] == "Pending verification"


# SOP-DI-004 s6(b) / F2: reason for change mandatory on both the JSON API and the HTML form
def test_amend_rejected_without_reason_api_and_form(client, conn, nmt015):
    before = _result(conn, nmt015)
    attempts = [
        client.patch(f"/api/results/{nmt015}", json={"measured_value": "0.154"}, headers=ANALYST),
        _api_amend(client, nmt015, "0.154", reason=""),
        _api_amend(client, nmt015, "0.154", reason="          "),
        client.post(f"/results/{nmt015}/amend", data={"measured_value": "0.154"}, headers=ANALYST),
        client.post(
            f"/results/{nmt015}/amend", data={"measured_value": "0.154", "reason": "  "}, headers=ANALYST
        ),
    ]
    assert [r.status_code for r in attempts] == [422] * len(attempts)
    assert _result(conn, nmt015) == before
    assert _updates(conn, nmt015) == []


# SOP-DI-004 s6(a) / F7: second-person verification is itself audited
def test_verify_writes_status_audit_row(client, conn, nmt015):
    assert _api_amend(client, nmt015, "0.154").json()["status"] == "Pending verification"
    n_before = len(_updates(conn, nmt015))
    r = client.post(f"/api/results/{nmt015}/verify", json={"reason": VERIFY_REASON}, headers=SUPERVISOR)
    assert r.status_code == 200
    rows = _updates(conn, nmt015)
    assert len(rows) == n_before + 1
    last = rows[-1]
    assert (last["field"], last["old_value"], last["new_value"]) == (
        "status",
        "Pending verification",
        "Amended",
    )
    assert last["actor"] == "adiallo"
    assert last["reason"] == VERIFY_REASON
    assert last["ts"].endswith("Z")
    assert _result(conn, nmt015)["status"] == "Amended"


# SOP-DI-004 s6(c) / F3: no route can alter or remove audit entries
def test_audit_entries_cannot_be_modified_via_api(client, conn, nmt015):
    assert _api_amend(client, nmt015, "0.154").status_code == 200
    snapshot = _all_audit(conn)
    audit_id = _updates(conn, nmt015)[0]["audit_id"]
    paths = [
        "/api/audit",
        f"/api/audit/{audit_id}",
        f"/api/results/{nmt015}/audit",
        f"/api/results/{nmt015}/audit/{audit_id}",
        "/audit",
        f"/audit/{audit_id}",
    ]
    payload = {"old_value": "0.999", "new_value": "0.999", "reason": "Tampering attempt for test"}
    for path in paths:
        for method in ("PUT", "PATCH", "DELETE"):
            r = client.request(method, path, json=payload, headers=SUPERVISOR)
            assert r.status_code in (404, 405), (method, path, r.status_code)
    assert _all_audit(conn) == snapshot


# SOP-DI-004 s6(d) / F1, F2: a refused amendment leaves neither a changed result nor partial audit rows
def test_rejected_amend_leaves_no_partial_audit(client, conn, nmt015, monkeypatch):
    before = _result(conn, nmt015)
    snapshot = _all_audit(conn)

    r = _api_amend(client, nmt015, "0.154", reason="too short")
    assert r.status_code == 422
    assert _result(conn, nmt015) == before
    assert _all_audit(conn) == snapshot

    real_record = audit.record
    calls = {"n": 0}

    def fail_on_second_field(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 2:
            raise audit.ReasonRequired("simulated refusal after the first audit row was written")
        return real_record(*args, **kwargs)

    monkeypatch.setattr(audit, "record", fail_on_second_field)
    r = _api_amend(client, nmt015, "0.154")
    assert r.status_code == 422
    assert calls["n"] == 2
    monkeypatch.setattr(audit, "record", real_record)
    assert _result(conn, nmt015) == before
    assert _all_audit(conn) == snapshot

    # A later successful request must not commit anything left over from the refused one.
    assert client.get(f"/api/results/{nmt015}").status_code == 200
    conn.commit()
    assert _all_audit(conn) == snapshot


# SOP-DI-004 s6(a) / F3: original value is not obscured; history view shows old, new and reason
def test_original_value_visible_in_history_view(client, conn, nmt015):
    r = client.post(
        f"/results/{nmt015}/amend",
        data={"measured_value": "0.154", "reason": REASON},
        headers=ANALYST,
        follow_redirects=False,
    )
    assert r.status_code == 303
    page = client.get(f"/results/{nmt015}")
    assert page.status_code == 200
    history = page.text.split("Record history", 1)[1]
    row = next(
        line for line in history.split("<tr>") if "<td>update</td>" in line and ">measured_value<" in line
    )
    assert "<td>0.155</td>" in row
    assert "<td>0.154</td>" in row
    assert REASON in row
    assert "<td>mfarouk</td>" in row


# SOP-DI-004 s6(d): a storage failure after the audit rows are written must not leave orphan audit rows
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Defect: sst.main._amend only rolls back on audit.ReasonRequired. If the UPDATE of assay_results "
        "fails after the audit rows were inserted, the shared connection keeps the open transaction and "
        "the next request's commit persists audit rows for an amendment that never happened."
    ),
)
def test_amend_storage_failure_leaves_no_orphan_audit(conn, nmt015, range_result):
    from fastapi.testclient import TestClient

    from sst import main as app_module
    from sst.regimes import load_regime

    before = _result(conn, nmt015)
    conn.execute(
        "CREATE TRIGGER simulate_write_failure BEFORE UPDATE ON assay_results"
        f" WHEN OLD.result_id = {int(nmt015)} BEGIN SELECT RAISE(ABORT, 'simulated storage failure'); END"
    )
    conn.commit()
    app_module.reset_state(conn=conn, regime=load_regime("gmp"))
    try:
        with TestClient(app_module.app, raise_server_exceptions=False) as tc:
            assert _api_amend(tc, nmt015, "0.154").status_code == 500
            assert _api_amend(tc, range_result, "100.23").status_code == 200
    finally:
        app_module.reset_state()
    assert _result(conn, nmt015) == before
    assert _updates(conn, nmt015) == []
