"""CHG-4127 regression tests for result amendment (TS-005; findings 1-7, 9, 12 on PR #6)."""

import pytest

ANALYST = {"X-User": "mfarouk"}
ANALYST2 = {"X-User": "jokafor"}
SUPERVISOR = {"X-User": "adiallo"}
REASON = "Transcription error corrected against instrument printout"


@pytest.fixture()
def nmt015(conn):
    """An OOS result against NMT 0.15 (seeded measured 0.155 -> reportable 0.16)."""
    row = conn.execute(
        "SELECT r.result_id FROM assay_results r JOIN specifications sp USING(spec_id)"
        " WHERE sp.upper_limit='0.15' AND r.measured_value='0.155' AND r.deleted=0"
    ).fetchone()
    return row["result_id"]


@pytest.fixture()
def range_result(conn):
    """An in-spec result against a two-sided limit with one decimal place."""
    row = conn.execute(
        "SELECT r.result_id FROM assay_results r JOIN specifications sp USING(spec_id)"
        " WHERE sp.lower_limit='95.0' AND sp.upper_limit='105.0' AND r.oos=0 AND r.deleted=0 LIMIT 1"
    ).fetchone()
    return row["result_id"]


def _audit(conn, rid):
    return conn.execute(
        "SELECT * FROM audit_trail WHERE entity='assay_result' AND entity_id=? AND action='update'"
        " ORDER BY audit_id",
        (str(rid),),
    ).fetchall()


def _amend(client, rid, value, reason=REASON, headers=ANALYST):
    return client.patch(
        f"/api/results/{rid}", json={"measured_value": value, "reason": reason}, headers=headers
    )


# Finding 1/3: every amended field is audited with user, old and new value, reason
def test_amend_writes_audit_rows_with_old_and_new_values(client, conn, nmt015):
    r = _amend(client, nmt015, "0.154")
    assert r.status_code == 200
    rows = {a["field"]: a for a in _audit(conn, nmt015)}
    assert rows["measured_value"]["old_value"] == "0.155"
    assert rows["measured_value"]["new_value"] == "0.154"
    assert rows["reportable_value"]["old_value"] == "0.16"
    assert rows["reportable_value"]["new_value"] == "0.15"
    assert rows["oos"]["old_value"] == "1" and rows["oos"]["new_value"] == "0"
    for a in rows.values():
        assert a["actor"] == "mfarouk"
        assert a["reason"] == REASON
        assert a["ts"].endswith("Z")


# Finding 2: reason is mandatory and min length is enforced; nothing is changed on refusal
@pytest.mark.parametrize("reason", ["", "   ", "too short"])
def test_amend_rejected_without_adequate_reason(client, conn, nmt015, reason):
    r = _amend(client, nmt015, "0.154", reason=reason)
    assert r.status_code == 422
    row = conn.execute(
        "SELECT measured_value, status FROM assay_results WHERE result_id=?", (nmt015,)
    ).fetchone()
    assert row["measured_value"] == "0.155"
    assert row["status"] != "Amended"
    assert _audit(conn, nmt015) == []


def test_amend_api_requires_reason_field(client, nmt015):
    r = client.patch(f"/api/results/{nmt015}", json={"measured_value": "0.154"}, headers=ANALYST)
    assert r.status_code == 422


# Finding 4/5: exact decimal half-up rounding and inclusive comparison at, below and above the limit
@pytest.mark.parametrize(
    "value,reportable,oos",
    [
        ("0.149", "0.15", 0),
        ("0.150", "0.15", 0),
        ("0.154", "0.15", 0),
        ("0.145", "0.15", 0),
        ("0.151", "0.15", 0),
    ],
)
def test_amend_nmt_within_spec(client, nmt015, value, reportable, oos):
    body = _amend(client, nmt015, value).json()
    assert (body["reportable_value"], body["oos"]) == (reportable, oos)


@pytest.mark.parametrize("value,reportable", [("0.156", "0.16"), ("0.1551", "0.16"), ("0.16", "0.16")])
def test_amend_nmt_oos_retained(client, nmt015, value, reportable):
    body = _amend(client, nmt015, value).json()
    assert (body["reportable_value"], body["oos"]) == (reportable, 1)
    assert body["status"] == "Amended"


@pytest.mark.parametrize(
    "value,reportable,oos",
    [
        ("94.95", "95.0", 0),
        ("94.94", "94.9", 1),
        ("95.0", "95.0", 0),
        ("105.0", "105.0", 0),
        ("105.04", "105.0", 0),
        ("105.05", "105.1", 1),
        ("105.1", "105.1", 1),
    ],
)
def test_amend_two_sided_limits(client, range_result, value, reportable, oos):
    body = _amend(client, range_result, value).json()
    assert (body["reportable_value"], body["oos"]) == (reportable, oos)


# Finding 6: attribution and authorisation
def test_amend_rejects_unprovisioned_user(client, conn, nmt015):
    assert _amend(client, nmt015, "0.154", headers={"X-User": "nobody"}).status_code == 403
    assert _audit(conn, nmt015) == []


def test_amend_rejects_qa_role(client, nmt015):
    assert _amend(client, nmt015, "0.154", headers={"X-User": "qa.review"}).status_code == 403


# Finding 7: OOS conclusion change needs second-person (supervisor) verification
def test_oos_change_requires_supervisor_verification(client, conn, nmt015):
    body = _amend(client, nmt015, "0.154").json()
    assert body["status"] == "Pending verification"
    assert (
        client.post(f"/api/results/{nmt015}/verify", json={"reason": REASON}, headers=ANALYST2).status_code
        == 403
    )
    r = client.post(
        f"/api/results/{nmt015}/verify", json={"reason": "Checked against raw data"}, headers=SUPERVISOR
    )
    assert r.status_code == 200
    assert r.json()["status"] == "Amended"
    last = _audit(conn, nmt015)[-1]
    assert (last["field"], last["old_value"], last["new_value"], last["actor"]) == (
        "status",
        "Pending verification",
        "Amended",
        "adiallo",
    )


def test_verifier_must_differ_from_amender(client, nmt015):
    _amend(client, nmt015, "0.154", headers=SUPERVISOR)
    r = client.post(f"/api/results/{nmt015}/verify", json={"reason": REASON}, headers=SUPERVISOR)
    assert r.status_code == 403


def test_verify_requires_reason_and_pending_state(client, nmt015):
    assert (
        client.post(f"/api/results/{nmt015}/verify", json={"reason": REASON}, headers=SUPERVISOR).status_code
        == 409
    )
    _amend(client, nmt015, "0.154")
    assert (
        client.post(f"/api/results/{nmt015}/verify", json={"reason": "short"}, headers=SUPERVISOR).status_code
        == 422
    )


def test_amend_without_oos_change_needs_no_verification(client, range_result):
    assert _amend(client, range_result, "100.23").json()["status"] == "Amended"


# Finding 9/12: input validation on both routes
def test_form_rejects_non_numeric_value(client, conn, nmt015):
    r = client.post(
        f"/results/{nmt015}/amend", data={"measured_value": "abc", "reason": REASON}, headers=ANALYST
    )
    assert r.status_code == 422
    assert _audit(conn, nmt015) == []


def test_api_rejects_non_numeric_value(client, nmt015):
    assert _amend(client, nmt015, "abc").status_code == 422


def test_amend_rejects_identical_value(client, nmt015):
    assert _amend(client, nmt015, "0.155").status_code == 422


def test_form_amend_and_verify_flow(client, conn, nmt015):
    r = client.post(
        f"/results/{nmt015}/amend",
        data={"measured_value": "0.154", "reason": REASON},
        headers=ANALYST,
        follow_redirects=False,
    )
    assert r.status_code == 303
    page = client.get(f"/results/{nmt015}")
    assert "supervisor verification required" in page.text
    assert "Reason for change" in page.text
    r = client.post(
        f"/results/{nmt015}/verify",
        data={"reason": "Checked against raw data"},
        headers=SUPERVISOR,
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert (
        conn.execute("SELECT status FROM assay_results WHERE result_id=?", (nmt015,)).fetchone()[0]
        == "Amended"
    )


def test_form_rejects_missing_reason(client, conn, nmt015):
    r = client.post(f"/results/{nmt015}/amend", data={"measured_value": "0.154"}, headers=ANALYST)
    assert r.status_code == 422
    assert _audit(conn, nmt015) == []
