# RTM — Requirements Traceability Matrix, Stability Sample Tracker
**Revision:** 3.5 · **Status:** Draft · **Effective:** · **Approved:**

Supersedes r3.4 (Approved, effective 2025-05-19, H. Lindqvist (QA Director), 2025-05-16) on approval. r3.5 is raised under change control CHG-4127 (see `validation/change_control/CC-CHG-4127.md`) and addresses PR #6 review finding F8 (RTM not updated). Prepared per SOP-CSV-010 §8.

TS-005 = `tests/test_amend.py` (+ `tests/test_amend_boundaries.py`, if present). TS-006 = `tests/test_amend_audit.py`. In the test-case column, `::name` refers to the file named most recently before it.

| URS | FS | Risk | Test script | Test cases (automated) | Code | Last executed |
|---|---|---|---|---|---|---|
| URS-001 | FS-001 | High | TS-001 | `tests/test_regimes.py::test_all_regimes_load`, `::test_gmp_is_active_by_default`, `::test_sox_uses_half_even` | `sst/regimes.py` | ER-2025-018 |
| URS-002 | FS-002 | High | TS-002, TS-005, TS-006 | `tests/test_audit.py::test_create_result_writes_audit_entry`, `::test_delete_is_soft_and_audited`; `tests/test_amend.py::test_amend_writes_audit_rows_with_old_and_new_values`, `::test_oos_change_requires_supervisor_verification`; `tests/test_amend_audit.py::test_amend_writes_one_audit_row_per_changed_field`, `::test_amend_audit_captures_old_and_new_values`, `::test_verify_writes_status_audit_row` | `sst/audit.py`, `sst/main.py`, `sst/main.py::_amend`, `sst/main.py::_verify` | ER-CHG-4127 |
| URS-003 | FS-003 | High | TS-002, TS-005, TS-006 | `tests/test_audit.py::test_delete_requires_reason`, `::test_delete_is_soft_and_audited`, `::test_reason_rule_is_regime_driven`; `tests/test_amend.py::test_amend_rejected_without_adequate_reason`, `::test_amend_api_requires_reason_field`, `::test_form_rejects_missing_reason`, `::test_verify_requires_reason_and_pending_state`; `tests/test_amend_audit.py::test_amend_rejected_without_reason_api_and_form`, `::test_rejected_amend_leaves_no_partial_audit` | `sst/audit.py`, `sst/main.py::api_delete_result`, `sst/main.py::_amend`, `sst/main.py::_verify` | ER-CHG-4127 |
| URS-004 | FS-004 | High | TS-003 | `tests/test_rounding.py::test_half_up_rounding`, `::test_half_even_mode_for_financial_regimes`, `::test_unknown_mode_rejected`, `::test_decimal_places_from_limit`, `::test_evaluate_against_specification` | `sst/rounding.py` | ER-2025-018 |
| URS-005 | FS-005 | Medium | TS-004 | `tests/test_views.py::test_pages_render`, `::test_oos_visible_on_sample_page`, `::test_404s`, `::test_seed_shape` | `sst/main.py`, `sst/templates/` | ER-2025-018 |
| URS-006 | FS-006 | High | TS-004, TS-002, TS-005, TS-006 | `tests/test_views.py::test_pages_render` (`/results/1`, `/audit`), `tests/test_audit.py::test_audit_entries_are_append_only_at_api_level`; `tests/test_amend.py::test_form_amend_and_verify_flow` (result page shows reason for change); `tests/test_amend_audit.py::test_original_value_visible_in_history_view`, `::test_audit_entries_cannot_be_modified_via_api` | `sst/main.py`, `sst/templates/result.html` | ER-CHG-4127 |
| URS-007 | FS-007 | High | TS-002, TS-005 | `tests/test_audit.py::test_create_result_writes_audit_entry` (actor = `X-User`); `tests/test_amend.py::test_amend_writes_audit_rows_with_old_and_new_values` (amender = `X-User`), `::test_oos_change_requires_supervisor_verification` (verifier = `X-User`), `::test_amend_rejects_unprovisioned_user` | `sst/main.py::current_user` | ER-CHG-4127 |
| URS-008 | FS-008 | High | TS-002, TS-005 | `tests/test_audit.py::test_create_result_writes_audit_entry`, `::test_delete_is_soft_and_audited`; `tests/test_amend.py::test_amend_api_requires_reason_field`, `::test_api_rejects_non_numeric_value`, `::test_oos_change_requires_supervisor_verification` (`PATCH /api/results/{id}`, `POST /api/results/{id}/verify`) | `sst/main.py`, `sst/main.py::api_amend_result`, `sst/main.py::api_verify_result` | ER-CHG-4127 |
| URS-009 | FS-002 | High | TS-002 | `tests/test_audit.py::test_create_result_writes_audit_entry` (ts generated server-side) | `sst/audit.py::utcnow` | ER-2025-018 |
| URS-010 | FS-009 | High | TS-005, TS-006 | `tests/test_amend.py::test_amend_writes_audit_rows_with_old_and_new_values`, `::test_amend_rejected_without_adequate_reason`, `::test_amend_api_requires_reason_field`, `::test_amend_nmt_within_spec`, `::test_amend_nmt_oos_retained`, `::test_amend_two_sided_limits`, `::test_amend_rejects_unprovisioned_user`, `::test_amend_rejects_qa_role`, `::test_form_rejects_non_numeric_value`, `::test_api_rejects_non_numeric_value`, `::test_amend_rejects_identical_value`, `::test_form_rejects_missing_reason`; `tests/test_amend_boundaries.py` (if present); `tests/test_amend_audit.py::test_amend_writes_one_audit_row_per_changed_field`, `::test_amend_audit_captures_old_and_new_values`, `::test_amend_rejected_without_reason_api_and_form`, `::test_rejected_amend_leaves_no_partial_audit`, `::test_original_value_visible_in_history_view` | `sst/main.py::_amend`, `sst/main.py::api_amend_result`, `sst/main.py::amend_result_form`, `sst/rounding.py` | ER-CHG-4127 |
| URS-011 | FS-010 | High | TS-005, TS-006 | `tests/test_amend.py::test_oos_change_requires_supervisor_verification`, `::test_verifier_must_differ_from_amender`, `::test_verify_requires_reason_and_pending_state`, `::test_amend_without_oos_change_needs_no_verification`, `::test_form_amend_and_verify_flow`; `tests/test_amend_audit.py::test_verify_writes_status_audit_row` | `sst/main.py::_verify`, `sst/main.py::api_verify_result`, `sst/main.py::verify_result_form`, `sst/templates/result.html` | ER-CHG-4127 |

Coverage: 11/11 URS traced to FS, test and code. Rows with "Last executed" = ER-CHG-4127 are traced to `validation/executed_results/ER-CHG-4127.md`; that record is completed from the CI run listed below.

## Change traceability — CHG-4127

| Link | Reference |
|---|---|
| Change request | CHG-4127 — GitHub issue [#2](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/issues/2) (allow analysts to amend assay results) |
| Change control record | `validation/change_control/CC-CHG-4127.md` |
| Pull request | [#6](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/6) |
| Code commit | `805496c` (branch `feature/chg-4127-amend-results-r3`) — `sst/main.py` (`_amend`, `_verify`, `api_amend_result`, `api_verify_result`, `amend_result_form`, `verify_result_form`), `sst/templates/result.html`, `tests/test_amend.py` |
| Evidence commits | see CC-CHG-4127: `<evidence SHAs — parent fills>` |
| Requirements | URS-010 → FS-009 (new); URS-011 → FS-010 (new); URS-002, URS-003, URS-006, URS-007, URS-008 (changed: amendment tests added) |
| Test scripts | TS-005 (`tests/test_amend.py`; `tests/test_amend_boundaries.py` if present); TS-006 (`tests/test_amend_audit.py`) |
| CI run | `<CI run URL — parent fills>` |
| Executed results | ER-CHG-4127 (`validation/executed_results/ER-CHG-4127.md`) |
| Devin session | https://devin-gtm.devinenterprise.com/sessions/968d18d35b254ea79fd50bf0becb2488 |

## Open items at r3.5 (Draft)

- F11: decision for QA on whether amendment and OOS verification require an electronic signature (21 CFR 11.50/11.200) rather than an SSO-attributed audit entry. Not implemented in `805496c`; QA decision to be recorded in CC-CHG-4127.
- Evidence placeholders above (evidence commit SHAs, CI run URL) and ER-CHG-4127 execution results to be completed from CI before review.
- TS-006 (`tests/test_amend_audit.py`) and `tests/test_amend_boundaries.py` are being written in parallel; test node IDs above must be checked against the committed files and the executed CI run before approval.
- URS-SST, FS-SST and RA-SST revisions for URS-010/URS-011, FS-009/FS-010 and their risk ratings are tracked under CC-CHG-4127; the "High" risk shown for URS-010/URS-011 is subject to the RA-SST update.
- Review and approval of r3.5: approver and dates intentionally left blank.
