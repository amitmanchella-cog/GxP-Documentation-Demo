"""CHG-4127 TS-005 gap tests: cases not covered by tests/test_amend.py (findings 2, 4-7, 9 on PR #6)."""

import dataclasses

import pytest

from sst import main as app_module
from sst.regimes import load_regime

ANALYST = {"X-User": "mfarouk"}
ANALYST2 = {"X-User": "jokafor"}
SUPERVISOR = {"X-User": "adiallo"}
REASON = "Transcription error corrected against instrument printout"


@pytest.fixture()
def nmt015(conn):
    """OOS result against NMT 0.15 (seeded measured 0.155 -> reportable 0.16)."""
    row = conn.execute(
        "SELECT r.result_id FROM assay_results r JOIN specifications sp USING(spec_id)"
        " WHERE sp.upper_limit='0.15' AND r.measured_value='0.155' AND r.deleted=0"
    ).fetchone()
    return row["result_id"]


@pytest.fixture()
def q80(conn):
    """In-spec result against the lower-only integer limit Q = 80 % (dissolution)."""
    row = conn.execute(
        "SELECT r.result_id FROM assay_results r JOIN specifications sp USING(spec_id)"
        " WHERE sp.lower_limit='80' AND sp.upper_limit IS NULL AND r.oos=0 AND r.deleted=0"
        " AND r.measured_value NOT IN ('80', '79.5', '79.49', '80.5', '79') LIMIT 1"
    ).fetchone()
    return row["result_id"]


@pytest.fixture()
def range_result(conn):
    row = conn.execute(
        "SELECT r.result_id, r.spec_id FROM assay_results r JOIN specifications sp USING(spec_id)"
        " WHERE sp.lower_limit='95.0' AND sp.upper_limit='105.0' AND r.oos=0 AND r.deleted=0 LIMIT 1"
    ).fetchone()
    return row["result_id"], row["spec_id"]


def _use_regime(conn, regime):
    app_module.reset_state(conn=conn, regime=regime)


def _amend(client, rid, value, reason=REASON, headers=ANALYST):
    return client.patch(
        f"/api/results/{rid}", json={"measured_value": value, "reason": reason}, headers=headers
    )


def _verify(client, rid, headers=SUPERVISOR, reason="Checked against raw data"):
    return client.post(f"/api/results/{rid}/verify", json={"reason": reason}, headers=headers)


def _update_rows(conn, rid):
    return conn.execute(
        "SELECT COUNT(*) FROM audit_trail WHERE entity='assay_result' AND entity_id=? AND action='update'",
        (str(rid),),
    ).fetchone()[0]


# Finding 4/5, SOP-QC-021 s4.4: lower-only integer limit, at and either side of Q = 80
@pytest.mark.parametrize(
    "value,reportable,oos",
    [
        ("80", "80", 0),
        ("79.5", "80", 0),
        ("79.49", "79", 1),
        ("79", "79", 1),
        ("80.5", "81", 0),
    ],
)
def test_amend_lower_only_integer_limit(client, q80, value, reportable, oos):
    body = _amend(client, q80, value).json()
    assert (body["reportable_value"], body["oos"]) == (reportable, oos)


# Finding 5, SOP-QC-021 s4.2: precision comes from the more precise of the two limits
@pytest.mark.parametrize("value,reportable,oos", [("0.495", "0.50", 0), ("0.494", "0.49", 1)])
def test_amend_precision_from_more_precise_limit(client, conn, range_result, value, reportable, oos):
    rid, spec_id = range_result
    conn.execute("UPDATE specifications SET lower_limit='0.50', upper_limit='2' WHERE spec_id=?", (spec_id,))
    body = _amend(client, rid, value).json()
    assert (body["reportable_value"], body["oos"]) == (reportable, oos)


# Finding 5, URS-001: the regime's limit_inclusive setting is honoured
def test_amend_honours_regime_limit_inclusive(client, conn, nmt015):
    gmp = load_regime("gmp")
    _use_regime(
        conn, dataclasses.replace(gmp, results=dataclasses.replace(gmp.results, limit_inclusive=False))
    )
    body = _amend(client, nmt015, "0.150").json()
    assert (body["reportable_value"], body["oos"]) == ("0.15", 1)


# Finding 4, URS-001: the regime's rounding mode is used (SOX = half_even)
@pytest.mark.parametrize(
    "value,reportable,oos", [("0.165", "0.16", 1), ("0.145", "0.14", 0), ("0.135", "0.14", 0)]
)
def test_amend_uses_regime_rounding_mode_half_even(client, conn, nmt015, value, reportable, oos):
    _use_regime(conn, load_regime("sox"))
    body = _amend(client, nmt015, value).json()
    assert (body["reportable_value"], body["oos"]) == (reportable, oos)


# Finding 7, URS-001: second-person verification on OOS change is regime-driven
@pytest.mark.parametrize(
    "regime,status",
    [
        ("gmp", "Pending verification"),
        ("glp", "Pending verification"),
        ("gcp", "Amended"),
        ("sox", "Amended"),
    ],
)
def test_oos_change_verification_is_regime_driven(client, conn, nmt015, regime, status):
    _use_regime(conn, load_regime(regime))
    body = _amend(client, nmt015, "0.154").json()
    assert (body["oos"], body["status"]) == (0, status)


# Finding 2, SOP-DI-004 s4.2: reason length boundary at GMP reason_min_length (10), whitespace trimmed
@pytest.mark.parametrize(
    "reason,code",
    [("123456789", 422), ("  123456789  ", 422), ("1234567890", 200), ("12345678901", 200)],
)
def test_amend_reason_min_length_boundary(client, conn, nmt015, reason, code):
    assert _amend(client, nmt015, "0.156", reason=reason).status_code == code
    assert (_update_rows(conn, nmt015) > 0) is (code == 200)


# FS-003: a soft-deleted result cannot be amended or verified on either route
def test_deleted_result_cannot_be_amended_or_verified(client, conn, nmt015):
    r = client.request(
        "DELETE", f"/api/results/{nmt015}", json={"reason": "Wrong sample injected"}, headers=SUPERVISOR
    )
    assert r.status_code == 200
    assert _amend(client, nmt015, "0.154").status_code == 404
    form = client.post(
        f"/results/{nmt015}/amend", data={"measured_value": "0.154", "reason": REASON}, headers=ANALYST
    )
    assert form.status_code == 404
    assert _verify(client, nmt015).status_code == 404
    assert _update_rows(conn, nmt015) == 0


# Finding 7: a verified result can be re-amended; a new OOS change needs a new verification
def test_verified_result_can_be_re_amended(client, nmt015):
    assert _amend(client, nmt015, "0.154").json()["status"] == "Pending verification"
    assert _verify(client, nmt015).json()["status"] == "Amended"
    body = _amend(client, nmt015, "0.156", headers=ANALYST2).json()
    assert (body["reportable_value"], body["oos"], body["status"]) == ("0.16", 1, "Pending verification")
    assert _verify(client, nmt015).json()["status"] == "Amended"


# Finding 7: the verifier check applies to the latest amendment, not the first
def test_supervisor_cannot_verify_own_re_amendment(client, nmt015):
    _amend(client, nmt015, "0.154")
    _verify(client, nmt015)
    assert _amend(client, nmt015, "0.156", headers=SUPERVISOR).json()["status"] == "Pending verification"
    assert _verify(client, nmt015).status_code == 403


# Finding 7 gap G1 (open against 805496c): a further amendment while pending clears the verification
def test_amendment_while_pending_keeps_verification_requirement(client, nmt015):
    assert _amend(client, nmt015, "0.154").json()["status"] == "Pending verification"
    assert _amend(client, nmt015, "0.150", headers=ANALYST2).json()["status"] == "Pending verification"


# Finding 9, FS-008: only plain decimal strings are accepted (API)
@pytest.mark.parametrize("value", ["NaN", "inf", "1e-1", "+0.14", ".14", "0.14 ", "0,14", ""])
def test_api_rejects_non_plain_decimal(client, conn, nmt015, value):
    assert _amend(client, nmt015, value).status_code == 422
    assert _update_rows(conn, nmt015) == 0


# Finding 9, FS-008: server-side validation on the form route
@pytest.mark.parametrize("value", ["NaN", "inf", "1e-1", "0,14"])
def test_form_rejects_non_plain_decimal(client, conn, nmt015, value):
    r = client.post(
        f"/results/{nmt015}/amend", data={"measured_value": value, "reason": REASON}, headers=ANALYST
    )
    assert r.status_code == 422
    assert _update_rows(conn, nmt015) == 0


# Finding 6: attribution and role checks on the form route
@pytest.mark.parametrize("user", ["nobody", "qa.review", "tbrennan"])
def test_form_rejects_unprovisioned_or_unauthorised_user(client, conn, nmt015, user):
    r = client.post(
        f"/results/{nmt015}/amend",
        data={"measured_value": "0.154", "reason": REASON},
        headers={"X-User": user},
        follow_redirects=False,
    )
    assert r.status_code == 403
    assert _update_rows(conn, nmt015) == 0


# Finding 6: every role in AMEND_ROLES may amend, and the actor is recorded
@pytest.mark.parametrize("user", ["mfarouk", "lhansen", "adiallo"])
def test_amend_allowed_for_each_amend_role(client, conn, nmt015, user):
    assert _amend(client, nmt015, "0.156", headers={"X-User": user}).status_code == 200
    actors = conn.execute(
        "SELECT DISTINCT actor FROM audit_trail"
        " WHERE entity='assay_result' AND entity_id=? AND action='update'",
        (str(nmt015),),
    ).fetchall()
    assert [a[0] for a in actors] == [user]
