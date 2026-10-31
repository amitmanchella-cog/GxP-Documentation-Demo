"""TS-006 Audit-trail verification for result amendment and verification (SOP-DI-004 s6; URS-002, URS-003, URS-006, URS-010, URS-011; FS-002, FS-003, FS-009, FS-010)."""  # noqa: E501

import re

import pytest

from sst import audit
from sst import main as app_module

RID = 2  # seeded: NMT 0.15 % degradant, measured 0.048, reportable 0.05, oos 0, status Reviewed
ANALYST = "mfarouk"  # QC Analyst
SUPERVISOR = "adiallo"  # QC Supervisor
AMEND_REASON = "Transcription error, see notebook LN-2291 p.14"
VERIFY_REASON = "Checked against raw data LN-2291 p.14 and CDS sequence"
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
AUDIT_COLS = ("ts", "actor", "entity", "entity_id", "action", "field", "old_value", "new_value", "reason")


def _result(conn, rid=RID):
    row = conn.execute(
        "SELECT measured_value, reportable_value, oos, status, deleted FROM assay_results WHERE result_id=?",
        (rid,),
    ).fetchone()
    return tuple(row)


def _trail(conn, rid=RID):
    return [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM audit_trail WHERE entity='assay_result' AND entity_id=? ORDER BY audit_id",
            (str(rid),),
        )
    ]


def _all_audit_rows(conn):
    return [tuple(r) for r in conn.execute("SELECT * FROM audit_trail ORDER BY audit_id")]


def _amend(client, value="0.155", reason=AMEND_REASON, user=ANALYST, rid=RID, **extra):
    return client.patch(
        f"/api/results/{rid}",
        json={"measured_value": value, "reason": reason, **extra},
        headers={"x-user": user},
    )


def _verify(client, reason=VERIFY_REASON, user=SUPERVISOR, rid=RID):
    return client.post(f"/api/results/{rid}/verify", json={"reason": reason}, headers={"x-user": user})


def test_amend_writes_audit_row_per_changed_field(client, conn):
    """SOP-DI-004 s4.1, s6(a)/(b); 21 CFR 11.10(e); finding 1."""
    before = _trail(conn)
    t0 = audit.utcnow()
    # Client-supplied actor/ts must be ignored: attribution comes from X-User, time from the server.
    r = _amend(client, actor="someone.else", ts="2000-01-01T00:00:00.000Z")
    t1 = audit.utcnow()
    assert r.status_code == 200, r.text

    after = _trail(conn)
    assert after[: len(before)] == before
    new = after[len(before) :]
    got = [(a["action"], a["field"], a["old_value"], a["new_value"]) for a in new]
    assert got == [
        ("update", "measured_value", "0.048", "0.155"),
        ("update", "reportable_value", "0.05", "0.16"),
        ("update", "oos", "0", "1"),
        ("update", "status", "Reviewed", "Amended - pending verification"),
    ]
    for a in new:
        assert a["actor"] == ANALYST
        assert (a["entity"], a["entity_id"]) == ("assay_result", str(RID))
        assert a["reason"] == AMEND_REASON
        assert TS_RE.match(a["ts"]) and t0 <= a["ts"] <= t1
    assert r.json()["status"] == "Amended - pending verification"

    # Only fields that actually change are audited (100.04 keeps reportable 100.0 and the OOS conclusion).
    n = len(_trail(conn, 4))
    r = client.patch(
        "/api/results/1",
        json={"measured_value": "100.04", "reason": AMEND_REASON},
        headers={"x-user": "lhansen"},
    )
    assert r.status_code == 200, r.text
    new = _trail(conn, 1)[-2:]
    assert [(a["field"], a["old_value"], a["new_value"], a["actor"]) for a in new] == [
        ("measured_value", "100.03", "100.04", "lhansen"),
        ("status", "Reviewed", "Amended", "lhansen"),
    ]
    assert len(_trail(conn, 4)) == n

    # The HTML form path writes the same attributable rows.
    r = client.post(
        "/results/4/amend",
        data={"measured_value": "99.61", "reason": AMEND_REASON},
        headers={"x-user": "rsato"},
        follow_redirects=False,
    )
    assert r.status_code == 303, r.text
    new = _trail(conn, 4)[n:]
    assert [(a["field"], a["old_value"], a["new_value"]) for a in new] == [
        ("measured_value", "99.58", "99.61"),
        ("status", "Reviewed", "Amended"),
    ]
    assert all(a["actor"] == "rsato" and a["reason"] == AMEND_REASON for a in new)


def test_verify_writes_audit_row(client, conn):
    """SOP-DI-004 s5.3, s6(a)/(b); 21 CFR 11.10(e); finding 5."""
    assert _amend(client).status_code == 200
    before = _trail(conn)
    t0 = audit.utcnow()
    r = _verify(client)
    t1 = audit.utcnow()
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "Amended"

    after = _trail(conn)
    assert after[: len(before)] == before
    assert len(after) == len(before) + 1
    v = after[-1]
    assert {k: v[k] for k in AUDIT_COLS if k != "ts"} == {
        "actor": SUPERVISOR,
        "entity": "assay_result",
        "entity_id": str(RID),
        "action": "update",
        "field": "status",
        "old_value": "Amended - pending verification",
        "new_value": "Amended",
        "reason": VERIFY_REASON,
    }
    assert TS_RE.match(v["ts"]) and t0 <= v["ts"] <= t1
    # The verifier is distinct from the actor who set the pending status.
    assert before[-1]["actor"] == ANALYST != v["actor"]
    assert _result(conn) == ("0.155", "0.16", 1, "Amended", 0)


@pytest.mark.parametrize("reason", ["", "   ", "typo", "123456789"])
def test_amend_and_verify_rejected_without_reason_leave_record_unchanged(client, conn, reason):
    """SOP-DI-004 s4.2, s6(c); GMP reason_min_length 10; finding 2."""
    rec0, trail0 = _result(conn), _all_audit_rows(conn)

    r = _amend(client, reason=reason)
    assert r.status_code == 422, r.text
    assert _result(conn) == rec0 and _all_audit_rows(conn) == trail0

    r = client.post(
        f"/results/{RID}/amend",
        data={"measured_value": "0.155", "reason": reason},
        headers={"x-user": ANALYST},
        follow_redirects=False,
    )
    assert r.status_code == 422, r.text
    assert _result(conn) == rec0 and _all_audit_rows(conn) == trail0

    # Put the result into pending verification with a valid reason, then attempt verification without one.
    assert _amend(client).status_code == 200
    rec1, trail1 = _result(conn), _all_audit_rows(conn)
    assert rec1[3] == "Amended - pending verification"

    r = _verify(client, reason=reason)
    assert r.status_code == 422, r.text
    assert _result(conn) == rec1 and _all_audit_rows(conn) == trail1

    r = client.post(
        f"/results/{RID}/verify",
        data={"reason": reason},
        headers={"x-user": SUPERVISOR},
        follow_redirects=False,
    )
    assert r.status_code == 422, r.text
    assert _result(conn) == rec1 and _all_audit_rows(conn) == trail1


def test_audit_entries_not_modifiable_via_api_after_amend(client, conn):
    """SOP-DI-004 s4.4, s6(d); 21 CFR 11.10(e); FS-006."""
    assert _amend(client).status_code == 200
    amend_rows = [a for a in _trail(conn) if a["action"] == "update"]
    assert len(amend_rows) == 4
    snapshot = _all_audit_rows(conn)

    # No route other than GET/HEAD is exposed for audit-trail resources.
    for route in app_module.app.routes:
        path = getattr(route, "path", "")
        if "audit" in path:
            assert set(getattr(route, "methods", set())) <= {"GET", "HEAD"}, (path, route.methods)

    targets = ["/api/audit", "/audit", f"/api/results/{RID}/audit"]
    for a in amend_rows:
        targets += [f"/api/audit/{a['audit_id']}", f"/api/results/{RID}/audit/{a['audit_id']}"]
    tamper = {"old_value": "0.155", "new_value": "0.048", "reason": "Tamper attempt for TS-006", "ts": "x"}
    for user in (ANALYST, SUPERVISOR, "qa.review"):
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            for path in targets:
                r = client.request(method, path, json=tamper, headers={"x-user": user})
                assert r.status_code in (404, 405), (method, path, r.status_code)

    assert _all_audit_rows(conn) == snapshot

    # Later lawful writes (verification) append only; earlier rows remain byte-identical.
    assert _verify(client).status_code == 200
    later = _all_audit_rows(conn)
    assert later[: len(snapshot)] == snapshot and len(later) == len(snapshot) + 1


def test_original_value_preserved_in_history_view(client, conn):
    """SOP-DI-004 s5.2, s4.6; URS-006, URS-010; finding 1."""
    assert _amend(client).status_code == 200
    assert client.get(f"/api/results/{RID}").json()["measured_value"] == "0.155"

    api = client.get(f"/api/results/{RID}/audit")
    assert api.status_code == 200
    rows = api.json()
    assert rows[0]["action"] == "create" and rows[0]["new_value"] == "0.048"
    upd = [a for a in rows if a["action"] == "update" and a["field"] == "measured_value"]
    assert len(upd) == 1
    assert (upd[0]["old_value"], upd[0]["new_value"], upd[0]["actor"], upd[0]["reason"]) == (
        "0.048",
        "0.155",
        ANALYST,
        AMEND_REASON,
    )

    page = client.get(f"/results/{RID}")
    assert page.status_code == 200
    history = page.text.split("Record history", 1)[1]
    row_html = (
        f"<td>{upd[0]['audit_id']}</td><td>{upd[0]['ts']}</td><td>{ANALYST}</td><td>update</td>"
        f"<td>measured_value</td><td>0.048</td><td>0.155</td><td>{AMEND_REASON}</td>"
    )
    assert row_html in history

    # Still visible after verification.
    assert _verify(client).status_code == 200
    assert row_html in client.get(f"/results/{RID}").text.split("Record history", 1)[1]
    assert any(
        a["field"] == "measured_value" and a["old_value"] == "0.048"
        for a in client.get(f"/api/results/{RID}/audit").json()
    )
