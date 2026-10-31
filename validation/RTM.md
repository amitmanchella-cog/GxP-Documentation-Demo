# RTM — Requirements Traceability Matrix, Stability Sample Tracker
**Revision:** 3.5-draft (CHG-4127) · **Status:** Draft · **Effective:** · **Author:** Devin (drafted for CHG-4127, session https://devin-gtm.devinenterprise.com/sessions/f1caf5c6314642fda372bc09736e61a0) · **Reviewed:** · **Approved:**

Supersedes on approval: r3.4 (Approved, effective 2025-05-19). Drafted for CHG-4127 (GitHub issue #2, PR #5) to address finding 7 (RTM part; SOP-CSV-010 §8). Rows URS-002, URS-003, URS-004, URS-006, URS-007, URS-008 updated and rows URS-010, URS-011 added; URS-001, URS-005, URS-009 unchanged from r3.4.

| URS | FS | Risk | Test script | Test cases (automated) | Code | Last executed |
|---|---|---|---|---|---|---|
| URS-001 | FS-001 | High | TS-001 | `tests/test_regimes.py::test_all_regimes_load`, `::test_gmp_is_active_by_default`, `::test_sox_uses_half_even` | `sst/regimes.py` | ER-2025-018 |
| URS-002 | FS-002, FS-009, FS-010 | High | TS-002, TS-006 | `tests/test_audit.py::test_create_result_writes_audit_entry`, `::test_delete_is_soft_and_audited`, `tests/test_amend_audit.py::test_amend_writes_audit_row_per_changed_field`, `::test_verify_writes_audit_row` | `sst/audit.py`, `sst/main.py`, `sst/main.py::_audit_updates`, `::_amend`, `::_verify` | ER-CHG-4127 (final CI run — completed by parent) |
| URS-003 | FS-003, FS-009, FS-010 | High | TS-002, TS-005, TS-006 | `tests/test_audit.py::test_delete_requires_reason`, `::test_delete_is_soft_and_audited`, `::test_reason_rule_is_regime_driven`, `tests/test_amend.py::test_amend_requires_reason`, `::test_amend_form_has_reason_and_is_hidden_on_deleted`, `tests/test_amend_audit.py::test_amend_and_verify_rejected_without_reason_leave_record_unchanged` | `sst/audit.py`, `sst/main.py::api_delete_result`, `::_amend`, `::_verify`, `sst/templates/result.html` | ER-CHG-4127 (final CI run — completed by parent) |
| URS-004 | FS-004, FS-009 | High | TS-003, TS-005 | `tests/test_rounding.py::test_half_up_rounding`, `::test_half_even_mode_for_financial_regimes`, `::test_unknown_mode_rejected`, `::test_decimal_places_from_limit`, `::test_evaluate_against_specification`, `tests/test_amend.py::test_amend_uses_sop_half_up_rounding_at_limit` (amend path reuses `evaluate()`) | `sst/rounding.py`, `sst/main.py::_amend` (calls `sst.rounding.evaluate`) | ER-CHG-4127 (final CI run — completed by parent) |
| URS-005 | FS-005 | Medium | TS-004 | `tests/test_views.py::test_pages_render`, `::test_oos_visible_on_sample_page`, `::test_404s`, `::test_seed_shape` | `sst/main.py`, `sst/templates/` | ER-2025-018 |
| URS-006 | FS-006 | High | TS-004, TS-002, TS-006 | `tests/test_views.py::test_pages_render` (`/results/1`, `/audit`), `tests/test_audit.py::test_audit_entries_are_append_only_at_api_level`, `tests/test_amend_audit.py::test_original_value_preserved_in_history_view`, `::test_audit_entries_not_modifiable_via_api_after_amend` | `sst/main.py`, `sst/main.py::_result_page`, `sst/templates/result.html` | ER-CHG-4127 (final CI run — completed by parent) |
| URS-007 | FS-007, FS-009, FS-010 | High | TS-002, TS-005, TS-006 | `tests/test_audit.py::test_create_result_writes_audit_entry` (actor = `X-User`), `tests/test_amend.py::test_amend_rejects_unprovisioned_and_unauthorised_roles`, `::test_verifier_must_differ_and_be_supervisor`, `tests/test_amend_audit.py::test_amend_writes_audit_row_per_changed_field` (actor = `X-User`), `::test_verify_writes_audit_row` (actor = verifier) | `sst/main.py::current_user`, `::provisioned_user`, `::_amend`, `::_verify` | ER-CHG-4127 (final CI run — completed by parent) |
| URS-008 | FS-008, FS-009, FS-010 | High | TS-002, TS-005, TS-006 | `tests/test_audit.py::test_create_result_writes_audit_entry`, `::test_delete_is_soft_and_audited`, `tests/test_amend.py::test_amend_form_validates_decimal_server_side`, `::test_oos_change_requires_second_person_verification`, `tests/test_amend_audit.py::test_amend_writes_audit_row_per_changed_field` (`PATCH /api/results/{id}`), `::test_verify_writes_audit_row` (`POST /api/results/{id}/verify`) | `sst/main.py`, `sst/main.py::api_amend_result`, `::api_verify_amendment` | ER-CHG-4127 (final CI run — completed by parent) |
| URS-009 | FS-002 | High | TS-002 | `tests/test_audit.py::test_create_result_writes_audit_entry` (ts generated server-side) | `sst/audit.py::utcnow` | ER-2025-018 |
| URS-010 | FS-009 | High | TS-005, TS-006 | `tests/test_amend.py::test_amend_requires_reason`, `::test_amend_uses_sop_half_up_rounding_at_limit`, `::test_amend_rejects_unprovisioned_and_unauthorised_roles`, `::test_amend_form_validates_decimal_server_side`, `::test_amend_rejects_deleted_and_unchanged`, `::test_amend_form_has_reason_and_is_hidden_on_deleted`, `tests/test_amend_audit.py::test_amend_writes_audit_row_per_changed_field`, `::test_amend_and_verify_rejected_without_reason_leave_record_unchanged`, `::test_audit_entries_not_modifiable_via_api_after_amend`, `::test_original_value_preserved_in_history_view` | `sst/main.py::_amend`, `::api_amend_result`, `::amend_result_form`, `sst/templates/result.html` | ER-CHG-4127 (final CI run — completed by parent) |
| URS-011 | FS-010 | High | TS-005, TS-006 | `tests/test_amend.py::test_oos_change_requires_second_person_verification`, `::test_verifier_must_differ_and_be_supervisor`, `tests/test_amend_audit.py::test_verify_writes_audit_row`, `::test_amend_and_verify_rejected_without_reason_leave_record_unchanged` | `sst/main.py::_verify`, `::api_verify_amendment`, `::verify_amendment_form` | ER-CHG-4127 (final CI run — completed by parent) |

Coverage: 11/11 URS traced to FS, test and code (draft r3.5, CHG-4127). Open gaps: none in scope; findings 9 and 10 open for QA decision.

## Finding → RTM row cross-reference (CHG-4127)

| Finding | SOP clause | RTM rows |
|---|---|---|
| 1 No audit row on amendment | SOP-DI-004 §4.1, §4.4, §5.2 | URS-002, URS-006, URS-010 |
| 2 No reason for change | SOP-DI-004 §4.2, §5.1 | URS-003, URS-010, URS-011 |
| 3 Float `round()` instead of `evaluate()` | SOP-QC-021 §4–§5 | URS-004, URS-010 |
| 4 No provisioning / role check / attribution | SOP-DI-004 §3, §5.1 | URS-007, URS-010 |
| 5 OOS-changing amendment without second-person verification | SOP-DI-004 §5.3 | URS-011 |
| 6 No server-side validation on form | FS-008 | URS-008, URS-010 |
| 7 No evidence package (RTM part) | SOP-CSV-010 §6–§8 | this document |
| 8 Form on deleted results; no-op amendments accepted | — (advisory) | URS-010 |
| 9 E-signature for amendment verification not implemented | gmp.yaml `e_signature.required_for` | not traced — out of scope, separate CR for QA decision |
| 10 Version 3.4.1 vs target 3.5.0 | — (advisory) | not traced — release CC |
| 11 Same change as PR #3 (merged, reverted in PR #4) | SOP-CSV-010 | traceability chain below |

## Traceability chain (CHG-4127)

CHG-4127 (GitHub issue #2) → PR #5 (https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/5) → commits `a90e609` (original), `08b7269` (fix), evidence commits (to be listed by parent) → TS-005 (`tests/test_amend.py`) / TS-006 (`tests/test_amend_audit.py`) → ER-CHG-4127 → Devin session https://devin-gtm.devinenterprise.com/sessions/668c5454cc7b490a94054cdc68dfe220 (coordinating) / https://devin-gtm.devinenterprise.com/sessions/f1caf5c6314642fda372bc09736e61a0 (RTM draft).

Change history: r3.4 (2025-05) approved baseline, 9/9 URS; r3.5-draft (CHG-4127) adds URS-010/URS-011 and amendment/verification traces — pending review and approval.
