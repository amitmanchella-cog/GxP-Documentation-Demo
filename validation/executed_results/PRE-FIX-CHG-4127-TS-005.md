# PRE-FIX-CHG-4127-TS-005 — Local regression run of TS-005 on original (a90e609) vs fixed (08b7269) code
**Status:** Draft · **Author:** Devin (drafted for CHG-4127, session https://devin-gtm.devinenterprise.com/sessions/a874cf9342e94daebc309078264d64c4) · **Reviewed:** · **Approved:**

**This is a local, informative run on a Devin development VM. It is not the CI evidence and not executed results for release**; the executed results for CHG-4127 are recorded by the parent in `validation/executed_results/ER-CHG-4127.md` from CI (`reports/`).

Purpose: show that the TS-005 regression tests in `tests/test_amend.py` detect findings 2, 3, 4, 5, 6 and 8 of the PR #5 review "CHG-4127 GxP findings for a90e609" — they fail against the `sst/` code of the original PR head and pass against the fix.

| Field | Value |
|---|---|
| Python | 3.10.12 (pytest 9.2.0, fastapi 0.115.14) |
| Checkout (HEAD) | `08b7269e58e7ccd3432fdf91c4e0082676eddada` (`feature/chg-4127-amend-results-r2` fix) on branch `devin/chg-4127-ws-c` |
| Original code under test (run 1) | `sst/` from `a90e6092fe39b222b2f463271a7ac7e0045b4cf1` |
| Fixed code under test (run 2) | `sst/` from `08b7269e58e7ccd3432fdf91c4e0082676eddada` |
| Test file | `tests/test_amend.py`, sha256 `a68d43c6dde80672e3f51bafcf0b4d4a60ffab7f9d50ff0519c2afe5669fb4f0` (uncommitted at run time; content identical to the committed file) |
| Run 1 started (UTC) | 2026-10-31T20:15:58Z |
| Run 2 started (UTC) | 2026-10-31T20:16:00Z |

Note: `pyproject.toml` already adds `-q`, so the extra `-q` gives `-qq`, which prints no totals line. Run 1 short test summary lists 9 FAILED of 15 collected (6 passed: the six boundary values where float `round()` happens to give the SOP result); run 2 shows 15 dots and exit code 0.

## Run 1 — original code (expected: FAIL)
Commands:
```
git checkout a90e609 -- sst/ && pytest tests/test_amend.py -p no:cacheprovider --no-cov -q; git checkout 08b7269 -- sst/
```
`git diff --stat 08b7269 -- sst/` while the original code was checked out (verbatim):
```
 sst/main.py               | 184 ++++++----------------------------------------
 sst/templates/result.html |  10 ---
 2 files changed, 21 insertions(+), 173 deletions(-)
```
Console output (verbatim, unedited):
```
F..F....FFFFFFF                                                          [100%]
=================================== FAILURES ===================================
__________________________ test_amend_requires_reason __________________________

client = <starlette.testclient.TestClient object at 0x72809d739780>
conn = <sqlite3.Connection object at 0x72809d835b40>

    def test_amend_requires_reason(client, conn):
        rid = _result_id(conn, NMT_015)
        before = dict(_row(conn, rid))
        for reason in (None, "", "typo"):
            r = _patch(client, rid, "0.049", reason=reason)
>           assert r.status_code == 422, (reason, r.text)
E           AssertionError: (None, '{"result_id":2,"sample_id":"VC21118A-LT-00M","spec_id":"STB-2021-004-S02","measured_value":"0.049","reportable...UV AM-114","unit":"%","limit_text":"NMT 0.15 %","lower_limit":null,"upper_limit":"0.15","analyst_name":"Jide Okafor"}')
E           assert 200 == 422
E            +  where 200 = <Response [200 OK]>.status_code

tests/test_amend.py:43: AssertionError
_____ test_amend_uses_sop_half_up_rounding_at_limit[limits2-0.155-0.16-1] ______

client = <starlette.testclient.TestClient object at 0x72809d7e25c0>
conn = <sqlite3.Connection object at 0x72809d836040>, limits = (None, '0.15')
measured = '0.155', reportable = '0.16', oos = 1

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
>       assert (body["measured_value"], body["reportable_value"], body["oos"]) == (measured, reportable, oos)
E       AssertionError: assert ('0.155', '0.15', 0) == ('0.155', '0.16', 1)
E         
E         At index 1 diff: '0.15' != '0.16'
E         Use -v to get more diff

tests/test_amend.py:72: AssertionError
____ test_amend_uses_sop_half_up_rounding_at_limit[limits7-105.05-105.1-1] _____

client = <starlette.testclient.TestClient object at 0x72809d73b6a0>
conn = <sqlite3.Connection object at 0x72809d835f40>, limits = ('95.0', '105.0')
measured = '105.05', reportable = '105.1', oos = 1

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
>       assert (body["measured_value"], body["reportable_value"], body["oos"]) == (measured, reportable, oos)
E       AssertionError: assert ('105.05', '105.0', 0) == ('105.05', '105.1', 1)
E         
E         At index 1 diff: '105.0' != '105.1'
E         Use -v to get more diff

tests/test_amend.py:72: AssertionError
___________ test_amend_rejects_unprovisioned_and_unauthorised_roles ____________

client = <starlette.testclient.TestClient object at 0x72809d7e3910>
conn = <sqlite3.Connection object at 0x72809d836540>

    def test_amend_rejects_unprovisioned_and_unauthorised_roles(client, conn):
        rid = _result_id(conn, NMT_015)
        before = dict(_row(conn, rid))
        for user in ("new.analyst", "tbrennan", "qa.review"):
            r = _patch(client, rid, "0.049", user=user)
>           assert r.status_code == 403, (user, r.text)
E           AssertionError: ('new.analyst', '{"result_id":2,"sample_id":"VC21118A-LT-00M","spec_id":"STB-2021-004-S02","measured_value":"0.049","r...UV AM-114","unit":"%","limit_text":"NMT 0.15 %","lower_limit":null,"upper_limit":"0.15","analyst_name":"Jide Okafor"}')
E           assert 200 == 403
E            +  where 200 = <Response [200 OK]>.status_code

tests/test_amend.py:82: AssertionError
_____________ test_oos_change_requires_second_person_verification ______________

client = <starlette.testclient.TestClient object at 0x72809d7e1ab0>
conn = <sqlite3.Connection object at 0x72809d836440>

    def test_oos_change_requires_second_person_verification(client, conn):
        rid = _result_id(conn, NMT_015)
        r = _patch(client, rid, "0.049")
        assert r.status_code == 200 and r.json()["status"] == "Amended" and r.json()["oos"] == 0
    
        r = _patch(client, rid, "0.155")
        assert r.status_code == 200, r.text
>       assert (r.json()["oos"], r.json()["status"]) == (1, PENDING)
E       AssertionError: assert (0, 'Amended') == (1, 'Amended ...verification')
E         
E         At index 0 diff: 0 != 1
E         Use -v to get more diff

tests/test_amend.py:105: AssertionError
_________________ test_verifier_must_differ_and_be_supervisor __________________

client = <starlette.testclient.TestClient object at 0x72809d73a170>
conn = <sqlite3.Connection object at 0x72809d836640>

    def test_verifier_must_differ_and_be_supervisor(client, conn):
        rid = _result_id(conn, ASSAY)
>       assert _verify(client, rid).status_code == 409
E       assert 404 == 409
E        +  where 404 = <Response [404 Not Found]>.status_code
E        +    where <Response [404 Not Found]> = _verify(<starlette.testclient.TestClient object at 0x72809d73a170>, 1)

tests/test_amend.py:122: AssertionError
________________ test_amend_form_validates_decimal_server_side _________________

client = <starlette.testclient.TestClient object at 0x72809d739ff0>
conn = <sqlite3.Connection object at 0x72809d836440>

    def test_amend_form_validates_decimal_server_side(client, conn):
        rid = _result_id(conn, NMT_015)
        before = dict(_row(conn, rid))
        for value in ("1e3", "abc", "", "0.05%", "1,5"):
            r = client.post(
                f"/results/{rid}/amend",
                data={"measured_value": value, "reason": REASON},
                headers={"x-user": "jokafor"},
            )
>           assert r.status_code == 422, (value, r.status_code)
E           AssertionError: ('1e3', 200)
E           assert 200 == 422
E            +  where 200 = <Response [200 OK]>.status_code

tests/test_amend.py:156: AssertionError
___________________ test_amend_rejects_deleted_and_unchanged ___________________

client = <starlette.testclient.TestClient object at 0x72809c616590>
conn = <sqlite3.Connection object at 0x72809d836840>

    def test_amend_rejects_deleted_and_unchanged(client, conn):
        rid = _result_id(conn, NMT_015)
        current = _row(conn, rid)["measured_value"]
        r = _patch(client, rid, current)
>       assert r.status_code == 422 and "unchanged" in r.text
E       assert (200 == 422)
E        +  where 200 = <Response [200 OK]>.status_code

tests/test_amend.py:174: AssertionError
_____________ test_amend_form_has_reason_and_is_hidden_on_deleted ______________

client = <starlette.testclient.TestClient object at 0x72809d739540>
conn = <sqlite3.Connection object at 0x72809d836440>

    def test_amend_form_has_reason_and_is_hidden_on_deleted(client, conn):
        rid = _result_id(conn, NMT_015)
        page = client.get(f"/results/{rid}").text
        assert f'action="/results/{rid}/amend"' in page
>       assert 'name="reason"' in page and "Reason for change" in page
E       assert ('name="reason"' in '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><title>R-000002 · SST</title>\n<link rel="stylesheet" hr...ty Sample Tracker · SST · regime GMP (EU/US GMP (21 CFR 210/211, EudraLex Vol 4)) · times UTC</footer>\n</body></html>')

tests/test_amend.py:199: AssertionError
=============================== warnings summary ===============================
../../.local/lib/python3.10/site-packages/anyio/pytest_plugin.py:14
  /home/ubuntu/.local/lib/python3.10/site-packages/anyio/pytest_plugin.py:14: PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.
  The CallSpec2 alias will be removed in pytest 10.
  Update imports to use CallSpec instead.
  See https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed
    from _pytest.python import CallSpec2

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_amend.py::test_amend_requires_reason - AssertionError: (Non...
FAILED tests/test_amend.py::test_amend_uses_sop_half_up_rounding_at_limit[limits2-0.155-0.16-1]
FAILED tests/test_amend.py::test_amend_uses_sop_half_up_rounding_at_limit[limits7-105.05-105.1-1]
FAILED tests/test_amend.py::test_amend_rejects_unprovisioned_and_unauthorised_roles
FAILED tests/test_amend.py::test_oos_change_requires_second_person_verification
FAILED tests/test_amend.py::test_verifier_must_differ_and_be_supervisor - ass...
FAILED tests/test_amend.py::test_amend_form_validates_decimal_server_side - A...
FAILED tests/test_amend.py::test_amend_rejects_deleted_and_unchanged - assert...
FAILED tests/test_amend.py::test_amend_form_has_reason_and_is_hidden_on_deleted
```
exit code: 1

## Run 2 — fixed code (expected: PASS)
Command:
```
pytest tests/test_amend.py --no-cov -q
```
Console output (verbatim, unedited):
```
...............                                                          [100%]
=============================== warnings summary ===============================
../../.local/lib/python3.10/site-packages/anyio/pytest_plugin.py:14
  /home/ubuntu/.local/lib/python3.10/site-packages/anyio/pytest_plugin.py:14: PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.
  The CallSpec2 alias will be removed in pytest 10.
  Update imports to use CallSpec instead.
  See https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed
    from _pytest.python import CallSpec2

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```
exit code: 0

## Finding coverage (run 1 failures)
| Finding | Failing test(s) on a90e609 |
|---|---|
| 2 No reason for change | `test_amend_requires_reason`, `test_amend_form_has_reason_and_is_hidden_on_deleted` |
| 3 Float `round()` instead of `evaluate()` | `test_amend_uses_sop_half_up_rounding_at_limit[limits2-0.155-0.16-1]`, `[limits7-105.05-105.1-1]` |
| 4 No provisioning / role check / attribution | `test_amend_rejects_unprovisioned_and_unauthorised_roles` |
| 5 No second-person verification on OOS change | `test_oos_change_requires_second_person_verification`, `test_verifier_must_differ_and_be_supervisor` |
| 6 No server-side validation on form | `test_amend_form_validates_decimal_server_side` |
| 8 Form on deleted results; no-op amendments accepted | `test_amend_rejects_deleted_and_unchanged`, `test_amend_form_has_reason_and_is_hidden_on_deleted` |
