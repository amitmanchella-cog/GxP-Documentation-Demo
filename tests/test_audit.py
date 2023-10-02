"""TS-002 Audit trail and result API on create/delete (URS-002, URS-003, URS-008, FS-002, FS-003, FS-008)."""

import pytest

from sst import audit
from sst.regimes import load_regime


def test_create_result_writes_audit_entry(client, conn):
    before = conn.execute("SELECT COUNT(*) FROM audit_trail").fetchone()[0]
    r = client.post(
        "/api/results",
        json={
            "sample_id": "VC21118A-LT-00M",
            "spec_id": "STB-2021-004-S01",
            "measured_value": "99.87",
            "instrument": "HPLC-07",
            "tested_at": "2025-01-10T09:12:00Z",
        },
        headers={"x-user": "jokafor"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["reportable_value"] == "99.9" and body["oos"] == 0 and body["analyst"] == "jokafor"
    trail = client.get(f"/api/results/{body['result_id']}/audit").json()
    assert len(trail) == 1
    assert (
        trail[0]["action"] == "create" and trail[0]["new_value"] == "99.87" and trail[0]["actor"] == "jokafor"
    )
    assert conn.execute("SELECT COUNT(*) FROM audit_trail").fetchone()[0] == before + 1


def test_delete_requires_reason(client, conn):
    rid = conn.execute("SELECT result_id FROM assay_results LIMIT 1").fetchone()[0]
    r = client.request("DELETE", f"/api/results/{rid}", json={"reason": "typo"})
    assert r.status_code == 422
    assert conn.execute("SELECT deleted FROM assay_results WHERE result_id=?", (rid,)).fetchone()[0] == 0


def test_delete_is_soft_and_audited(client, conn):
    rid = conn.execute("SELECT result_id FROM assay_results LIMIT 1").fetchone()[0]
    r = client.request(
        "DELETE",
        f"/api/results/{rid}",
        json={"reason": "Duplicate entry of R-000001"},
        headers={"x-user": "adiallo"},
    )
    assert r.status_code == 200
    row = conn.execute("SELECT deleted, status FROM assay_results WHERE result_id=?", (rid,)).fetchone()
    assert (row["deleted"], row["status"]) == (1, "Deleted")
    last = conn.execute("SELECT * FROM audit_trail ORDER BY audit_id DESC LIMIT 1").fetchone()
    assert (last["action"], last["actor"], last["old_value"], last["new_value"]) == (
        "delete",
        "adiallo",
        "Reviewed",
        "Deleted",
    )
    assert last["reason"] == "Duplicate entry of R-000001"
    assert client.get(f"/api/results/{rid}").status_code == 404


def test_audit_entries_are_append_only_at_api_level(client):
    assert client.request("DELETE", "/api/audit/1").status_code in (404, 405)
    assert client.request("PATCH", "/api/audit/1", json={}).status_code in (404, 405)


def test_reason_rule_is_regime_driven(conn):
    gmp = load_regime("gmp")
    with pytest.raises(audit.ReasonRequired):
        audit.record(conn, gmp, actor="x", entity="assay_result", entity_id="1", action="update", reason="")
    sox = load_regime("sox")
    assert (
        audit.record(
            conn,
            sox,
            actor="x",
            entity="assay_result",
            entity_id="1",
            action="update",
            reason="JE-44 fix",
        )
        > 0
    )
