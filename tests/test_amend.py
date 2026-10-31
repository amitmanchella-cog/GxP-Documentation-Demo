"""TS-005 Result amendment, rounding and second-person verification (URS-010, URS-011, URS-004, FS-009, FS-010, FS-004)."""  # noqa: E501

import pytest

PENDING = "Amended - pending verification"
REASON = "Transcription error, see logbook LB-117 p.42"
NMT_015 = (None, "0.15")
ASSAY = ("95.0", "105.0")


def _result_id(conn, limits, oos=0):
    lower, upper = limits
    row = conn.execute(
        """SELECT r.result_id FROM assay_results r JOIN specifications sp ON sp.spec_id=r.spec_id
           WHERE sp.lower_limit IS ? AND sp.upper_limit=? AND r.oos=? AND r.deleted=0
           ORDER BY r.result_id LIMIT 1""",
        (lower, upper, oos),
    ).fetchone()
    assert row is not None, f"seed has no result against {limits} with oos={oos}"
    return row[0]


def _row(conn, rid):
    return conn.execute("SELECT * FROM assay_results WHERE result_id=?", (rid,)).fetchone()


def _patch(client, rid, value, reason=REASON, user="jokafor"):
    body = {"measured_value": value}
    if reason is not None:
        body["reason"] = reason
    return client.patch(f"/api/results/{rid}", json=body, headers={"x-user": user})


def _verify(client, rid, user="adiallo", reason="Raw data and calculation checked against LB-117"):
    return client.post(f"/api/results/{rid}/verify", json={"reason": reason}, headers={"x-user": user})


def test_amend_requires_reason(client, conn):
    rid = _result_id(conn, NMT_015)
    before = dict(_row(conn, rid))
    for reason in (None, "", "typo"):
        r = _patch(client, rid, "0.049", reason=reason)
        assert r.status_code == 422, (reason, r.text)
        assert dict(_row(conn, rid)) == before
    r = client.post(
        f"/results/{rid}/amend",
        data={"measured_value": "0.049", "reason": "typo"},
        headers={"x-user": "jokafor"},
    )
    assert r.status_code == 422 and "reason for change is required" in r.text
    assert dict(_row(conn, rid)) == before


@pytest.mark.parametrize(
    "limits, measured, reportable, oos",
    [
        (NMT_015, "0.150", "0.15", 0),
        (NMT_015, "0.154", "0.15", 0),
        (NMT_015, "0.155", "0.16", 1),
        (NMT_015, "0.156", "0.16", 1),
        (ASSAY, "94.94", "94.9", 1),
        (ASSAY, "94.95", "95.0", 0),
        (ASSAY, "105.04", "105.0", 0),
        (ASSAY, "105.05", "105.1", 1),
    ],
)
def test_amend_uses_sop_half_up_rounding_at_limit(client, conn, limits, measured, reportable, oos):
    rid = _result_id(conn, limits)
    r = _patch(client, rid, measured)
    assert r.status_code == 200, r.text
    body = r.json()
    assert (body["measured_value"], body["reportable_value"], body["oos"]) == (measured, reportable, oos)
    row = _row(conn, rid)
    assert (row["reportable_value"], row["oos"]) == (reportable, oos)


def test_amend_rejects_unprovisioned_and_unauthorised_roles(client, conn):
    rid = _result_id(conn, NMT_015)
    before = dict(_row(conn, rid))
    for user in ("new.analyst", "tbrennan", "qa.review"):
        r = _patch(client, rid, "0.049", user=user)
        assert r.status_code == 403, (user, r.text)
        assert dict(_row(conn, rid)) == before
    conn.execute("UPDATE users SET active=0 WHERE user_id='rsato'")
    assert _patch(client, rid, "0.049", user="rsato").status_code == 403
    assert dict(_row(conn, rid)) == before
    for user, value in (("mfarouk", "0.049"), ("lhansen", "0.047"), ("adiallo", "0.046")):
        r = _patch(client, rid, value, user=user)
        assert r.status_code == 200, (user, r.text)
        actor = conn.execute(
            "SELECT actor FROM audit_trail WHERE entity='assay_result' AND entity_id=? AND action='update'"
            " ORDER BY audit_id DESC LIMIT 1",
            (str(rid),),
        ).fetchone()[0]
        assert actor == user


def test_oos_change_requires_second_person_verification(client, conn):
    rid = _result_id(conn, NMT_015)
    r = _patch(client, rid, "0.049")
    assert r.status_code == 200 and r.json()["status"] == "Amended" and r.json()["oos"] == 0

    r = _patch(client, rid, "0.155")
    assert r.status_code == 200, r.text
    assert (r.json()["oos"], r.json()["status"]) == (1, PENDING)
    assert _patch(client, rid, "0.160").status_code == 409
    assert _row(conn, rid)["measured_value"] == "0.155"
    page = client.get(f"/results/{rid}")
    assert "Pending verification" in page.text and f"/results/{rid}/verify" in page.text

    r = _verify(client, rid)
    assert r.status_code == 200, r.text
    assert (r.json()["status"], r.json()["oos"], r.json()["reportable_value"]) == ("Amended", 1, "0.16")

    oos_rid = _result_id(conn, NMT_015, oos=1)
    r = _patch(client, oos_rid, "0.10")
    assert (r.json()["oos"], r.json()["status"]) == (0, PENDING)


def test_verifier_must_differ_and_be_supervisor(client, conn):
    rid = _result_id(conn, ASSAY)
    assert _verify(client, rid).status_code == 409
    r = _patch(client, rid, "105.05", user="adiallo")
    assert r.status_code == 200 and r.json()["status"] == PENDING
    assert _verify(client, rid, user="adiallo").status_code == 403
    for user in ("lhansen", "jokafor", "qa.review", "new.analyst"):
        assert _verify(client, rid, user=user).status_code == 403, user
    assert _row(conn, rid)["status"] == PENDING
    r = client.post(
        f"/results/{rid}/verify",
        data={"reason": "Self-verification attempt"},
        headers={"x-user": "adiallo"},
    )
    assert r.status_code == 403 and "must not be the analyst" in r.text
    conn.execute("INSERT INTO users VALUES ('pnovak', 'Petra Novak', 'QC Supervisor', 1)")
    r = client.post(
        f"/results/{rid}/verify",
        data={"reason": "Raw data and calculation checked"},
        headers={"x-user": "pnovak"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _row(conn, rid)["status"] == "Amended"
    assert _verify(client, rid, user="pnovak").status_code == 409


def test_amend_form_validates_decimal_server_side(client, conn):
    rid = _result_id(conn, NMT_015)
    before = dict(_row(conn, rid))
    for value in ("1e3", "abc", "", "0.05%", "1,5"):
        r = client.post(
            f"/results/{rid}/amend",
            data={"measured_value": value, "reason": REASON},
            headers={"x-user": "jokafor"},
        )
        assert r.status_code == 422, (value, r.status_code)
        assert "decimal number" in r.text
        assert dict(_row(conn, rid)) == before
    assert _patch(client, rid, "1e3").status_code == 422
    r = client.post(
        f"/results/{rid}/amend",
        data={"measured_value": " 0.049 ", "reason": REASON},
        headers={"x-user": "jokafor"},
        follow_redirects=False,
    )
    assert r.status_code == 303 and r.headers["location"] == f"/results/{rid}"
    assert (_row(conn, rid)["measured_value"], _row(conn, rid)["reportable_value"]) == ("0.049", "0.05")


def test_amend_rejects_deleted_and_unchanged(client, conn):
    rid = _result_id(conn, NMT_015)
    current = _row(conn, rid)["measured_value"]
    r = _patch(client, rid, current)
    assert r.status_code == 422 and "unchanged" in r.text
    assert _row(conn, rid)["status"] != "Amended"

    r = client.request(
        "DELETE",
        f"/api/results/{rid}",
        json={"reason": "Duplicate entry of R-000001"},
        headers={"x-user": "adiallo"},
    )
    assert r.status_code == 200
    assert _patch(client, rid, "0.049").status_code == 404
    r = client.post(
        f"/results/{rid}/amend",
        data={"measured_value": "0.049", "reason": REASON},
        headers={"x-user": "jokafor"},
    )
    assert r.status_code == 404
    row = _row(conn, rid)
    assert (row["measured_value"], row["status"], row["deleted"]) == (current, "Deleted", 1)


def test_amend_form_has_reason_and_is_hidden_on_deleted(client, conn):
    rid = _result_id(conn, NMT_015)
    page = client.get(f"/results/{rid}").text
    assert f'action="/results/{rid}/amend"' in page
    assert 'name="reason"' in page and "Reason for change" in page

    client.request(
        "DELETE",
        f"/api/results/{rid}",
        json={"reason": "Duplicate entry of R-000001"},
        headers={"x-user": "adiallo"},
    )
    page = client.get(f"/results/{rid}")
    assert page.status_code == 200 and "Deleted" in page.text
    assert f"/results/{rid}/amend" not in page.text and f"/results/{rid}/verify" not in page.text

    other = _result_id(conn, NMT_015)
    assert _patch(client, other, "0.155").json()["status"] == PENDING
    page = client.get(f"/results/{other}").text
    assert f"/results/{other}/amend" not in page and f'action="/results/{other}/verify"' in page
