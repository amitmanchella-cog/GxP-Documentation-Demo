# PRE-FIX-CHG-4127-TS-006 — Local pre-fix / post-fix run of TS-006 (informative)
**Status:** Draft · **Author:** Devin (drafted for CHG-4127, session https://devin-gtm.devinenterprise.com/sessions/8654e49b929746838ac08dee9be01191) · **Reviewed:** · **Approved:** · **Executed by:** Devin session VM (local workstation run) · **Python:** 3.10.12

> This is a **local informative run**, not the CI evidence. It shows that `tests/test_amend_audit.py` (TS-006) detects the audit-trail defects of the original CHG-4127 change (findings 1, 2, 5) and passes on the fix. The executed results of record for CHG-4127 are produced by CI and recorded in `validation/executed_results/ER-CHG-4127.md`.

| Item | Value |
|---|---|
| Test file | `tests/test_amend_audit.py`, sha256 `93fbbb89e66aabb2f45b0cc51f0b53eb73fbfdd93522ef58511087b6dfe7079b` (identical to the file committed on branch `devin/chg-4127-ws-e`) |
| Pre-fix code (`sst/`) | `a90e6092fe39b222b2f463271a7ac7e0045b4cf1` — original PR #5 head |
| Post-fix code (`sst/`) | `08b7269e58e7ccd3432fdf91c4e0082676eddada` — fix on `feature/chg-4127-amend-results-r2` |
| Fail run started (UTC) | 2026-10-31T20:15:39Z |
| Pass run started (UTC) | 2026-10-31T20:15:41Z |

## Summary
- Pre-fix (`a90e609`): 8 of 8 TS-006 test cases fail (pytest exit=1). Failures: no audit rows written on amendment (finding 1); amendment with blank/short reason accepted with 200 (finding 2); no verification route (finding 5).
- Post-fix (`08b7269`): 8 of 8 pass (pytest exit=0).

## Fail run — commands
```
git checkout a90e609 -- sst/ && pytest tests/test_amend_audit.py -p no:cacheprovider --no-cov -q; git checkout 08b7269 -- sst/
```

## Fail run — console output (verbatim, unedited)
```
FFFFFFFF                                                                 [100%]
=================================== FAILURES ===================================
________________ test_amend_writes_audit_row_per_changed_field _________________

client = <starlette.testclient.TestClient object at 0x7aeaa2dc2ef0>
conn = <sqlite3.Connection object at 0x7aeaa2f21c40>

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
>       assert got == [
            ("update", "measured_value", "0.048", "0.155"),
            ("update", "reportable_value", "0.05", "0.16"),
            ("update", "oos", "0", "1"),
            ("update", "status", "Reviewed", "Amended - pending verification"),
        ]
E       AssertionError: assert [] == [('update', '...erification')]
E         
E         Right contains 4 more items, first extra item: ('update', 'measured_value', '0.048', '0.155')
E         Use -v to get more diff

tests/test_amend_audit.py:66: AssertionError
_________________________ test_verify_writes_audit_row _________________________

client = <starlette.testclient.TestClient object at 0x7aeaa2fcbd90>
conn = <sqlite3.Connection object at 0x7aeaa2f21f40>

    def test_verify_writes_audit_row(client, conn):
        """SOP-DI-004 s5.3, s6(a)/(b); 21 CFR 11.10(e); finding 5."""
        assert _amend(client).status_code == 200
        before = _trail(conn)
        t0 = audit.utcnow()
        r = _verify(client)
        t1 = audit.utcnow()
>       assert r.status_code == 200, r.text
E       AssertionError: {"detail":"Not Found"}
E       assert 404 == 200
E        +  where 404 = <Response [404 Not Found]>.status_code

tests/test_amend_audit.py:117: AssertionError
____ test_amend_and_verify_rejected_without_reason_leave_record_unchanged[] ____

client = <starlette.testclient.TestClient object at 0x7aeaa2fca1d0>
conn = <sqlite3.Connection object at 0x7aeaa2f22040>, reason = ''

    @pytest.mark.parametrize("reason", ["", "   ", "typo", "123456789"])
    def test_amend_and_verify_rejected_without_reason_leave_record_unchanged(client, conn, reason):
        """SOP-DI-004 s4.2, s6(c); GMP reason_min_length 10; finding 2."""
        rec0, trail0 = _result(conn), _all_audit_rows(conn)
    
        r = _amend(client, reason=reason)
>       assert r.status_code == 422, r.text
E       AssertionError: {"result_id":2,"sample_id":"VC21118A-LT-00M","spec_id":"STB-2021-004-S02","measured_value":"0.155","reportable_value":"0.15","oos":0,"analyst":"jokafor","instrument":"HPLC-09","tested_at":"2021-06-26T17:59:00Z","status":"Amended","deleted":0,"test_name":"Any unspecified degradant","method":"HPLC-UV AM-114","unit":"%","limit_text":"NMT 0.15 %","lower_limit":null,"upper_limit":"0.15","analyst_name":"Jide Okafor"}
E       assert 200 == 422
E        +  where 200 = <Response [200 OK]>.status_code

tests/test_amend_audit.py:146: AssertionError
__ test_amend_and_verify_rejected_without_reason_leave_record_unchanged[   ] ___

client = <starlette.testclient.TestClient object at 0x7aeaa2d9ceb0>
conn = <sqlite3.Connection object at 0x7aeaa2f22340>, reason = '   '

    @pytest.mark.parametrize("reason", ["", "   ", "typo", "123456789"])
    def test_amend_and_verify_rejected_without_reason_leave_record_unchanged(client, conn, reason):
        """SOP-DI-004 s4.2, s6(c); GMP reason_min_length 10; finding 2."""
        rec0, trail0 = _result(conn), _all_audit_rows(conn)
    
        r = _amend(client, reason=reason)
>       assert r.status_code == 422, r.text
E       AssertionError: {"result_id":2,"sample_id":"VC21118A-LT-00M","spec_id":"STB-2021-004-S02","measured_value":"0.155","reportable_value":"0.15","oos":0,"analyst":"jokafor","instrument":"HPLC-09","tested_at":"2021-06-26T17:59:00Z","status":"Amended","deleted":0,"test_name":"Any unspecified degradant","method":"HPLC-UV AM-114","unit":"%","limit_text":"NMT 0.15 %","lower_limit":null,"upper_limit":"0.15","analyst_name":"Jide Okafor"}
E       assert 200 == 422
E        +  where 200 = <Response [200 OK]>.status_code

tests/test_amend_audit.py:146: AssertionError
__ test_amend_and_verify_rejected_without_reason_leave_record_unchanged[typo] __

client = <starlette.testclient.TestClient object at 0x7aeaa2d9cf40>
conn = <sqlite3.Connection object at 0x7aeaa2f22040>, reason = 'typo'

    @pytest.mark.parametrize("reason", ["", "   ", "typo", "123456789"])
    def test_amend_and_verify_rejected_without_reason_leave_record_unchanged(client, conn, reason):
        """SOP-DI-004 s4.2, s6(c); GMP reason_min_length 10; finding 2."""
        rec0, trail0 = _result(conn), _all_audit_rows(conn)
    
        r = _amend(client, reason=reason)
>       assert r.status_code == 422, r.text
E       AssertionError: {"result_id":2,"sample_id":"VC21118A-LT-00M","spec_id":"STB-2021-004-S02","measured_value":"0.155","reportable_value":"0.15","oos":0,"analyst":"jokafor","instrument":"HPLC-09","tested_at":"2021-06-26T17:59:00Z","status":"Amended","deleted":0,"test_name":"Any unspecified degradant","method":"HPLC-UV AM-114","unit":"%","limit_text":"NMT 0.15 %","lower_limit":null,"upper_limit":"0.15","analyst_name":"Jide Okafor"}
E       assert 200 == 422
E        +  where 200 = <Response [200 OK]>.status_code

tests/test_amend_audit.py:146: AssertionError
_ test_amend_and_verify_rejected_without_reason_leave_record_unchanged[123456789] _

client = <starlette.testclient.TestClient object at 0x7aeaa2fcb8b0>
conn = <sqlite3.Connection object at 0x7aeaa2f22140>, reason = '123456789'

    @pytest.mark.parametrize("reason", ["", "   ", "typo", "123456789"])
    def test_amend_and_verify_rejected_without_reason_leave_record_unchanged(client, conn, reason):
        """SOP-DI-004 s4.2, s6(c); GMP reason_min_length 10; finding 2."""
        rec0, trail0 = _result(conn), _all_audit_rows(conn)
    
        r = _amend(client, reason=reason)
>       assert r.status_code == 422, r.text
E       AssertionError: {"result_id":2,"sample_id":"VC21118A-LT-00M","spec_id":"STB-2021-004-S02","measured_value":"0.155","reportable_value":"0.15","oos":0,"analyst":"jokafor","instrument":"HPLC-09","tested_at":"2021-06-26T17:59:00Z","status":"Amended","deleted":0,"test_name":"Any unspecified degradant","method":"HPLC-UV AM-114","unit":"%","limit_text":"NMT 0.15 %","lower_limit":null,"upper_limit":"0.15","analyst_name":"Jide Okafor"}
E       assert 200 == 422
E        +  where 200 = <Response [200 OK]>.status_code

tests/test_amend_audit.py:146: AssertionError
____________ test_audit_entries_not_modifiable_via_api_after_amend _____________

client = <starlette.testclient.TestClient object at 0x7aeaa2db4790>
conn = <sqlite3.Connection object at 0x7aeaa2f22240>

    def test_audit_entries_not_modifiable_via_api_after_amend(client, conn):
        """SOP-DI-004 s4.4, s6(d); 21 CFR 11.10(e); FS-006."""
        assert _amend(client).status_code == 200
        amend_rows = [a for a in _trail(conn) if a["action"] == "update"]
>       assert len(amend_rows) == 4
E       assert 0 == 4
E        +  where 0 = len([])

tests/test_amend_audit.py:181: AssertionError
________________ test_original_value_preserved_in_history_view _________________

client = <starlette.testclient.TestClient object at 0x7aeaa2fcbf70>
conn = <sqlite3.Connection object at 0x7aeaa2f22140>

    def test_original_value_preserved_in_history_view(client, conn):
        """SOP-DI-004 s5.2, s4.6; URS-006, URS-010; finding 1."""
        assert _amend(client).status_code == 200
        assert client.get(f"/api/results/{RID}").json()["measured_value"] == "0.155"
    
        api = client.get(f"/api/results/{RID}/audit")
        assert api.status_code == 200
        rows = api.json()
        assert rows[0]["action"] == "create" and rows[0]["new_value"] == "0.048"
        upd = [a for a in rows if a["action"] == "update" and a["field"] == "measured_value"]
>       assert len(upd) == 1
E       assert 0 == 1
E        +  where 0 = len([])

tests/test_amend_audit.py:218: AssertionError
=============================== warnings summary ===============================
../../.local/lib/python3.10/site-packages/anyio/pytest_plugin.py:14
  /home/ubuntu/.local/lib/python3.10/site-packages/anyio/pytest_plugin.py:14: PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.
  The CallSpec2 alias will be removed in pytest 10.
  Update imports to use CallSpec instead.
  See https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed
    from _pytest.python import CallSpec2

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_amend_audit.py::test_amend_writes_audit_row_per_changed_field
FAILED tests/test_amend_audit.py::test_verify_writes_audit_row - AssertionErr...
FAILED tests/test_amend_audit.py::test_amend_and_verify_rejected_without_reason_leave_record_unchanged[]
FAILED tests/test_amend_audit.py::test_amend_and_verify_rejected_without_reason_leave_record_unchanged[   ]
FAILED tests/test_amend_audit.py::test_amend_and_verify_rejected_without_reason_leave_record_unchanged[typo]
FAILED tests/test_amend_audit.py::test_amend_and_verify_rejected_without_reason_leave_record_unchanged[123456789]
FAILED tests/test_amend_audit.py::test_audit_entries_not_modifiable_via_api_after_amend
FAILED tests/test_amend_audit.py::test_original_value_preserved_in_history_view
```

## Pass run — command
```
pytest tests/test_amend_audit.py --no-cov -q
```

## Pass run — console output (verbatim, unedited)
```
........                                                                 [100%]
=============================== warnings summary ===============================
../../.local/lib/python3.10/site-packages/anyio/pytest_plugin.py:14
  /home/ubuntu/.local/lib/python3.10/site-packages/anyio/pytest_plugin.py:14: PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.
  The CallSpec2 alias will be removed in pytest 10.
  Update imports to use CallSpec instead.
  See https://docs.pytest.org/en/stable/deprecations.html#callspec2-renamed
    from _pytest.python import CallSpec2

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```
