# RTM — Requirements Traceability Matrix, Stability Sample Tracker
**Revision:** 3.4 · **Status:** Approved · **Effective:** 2025-05-19 · **Approved:** H. Lindqvist (QA Director), 2025-05-16

| URS | FS | Risk | Test script | Test cases (automated) | Code | Last executed |
|---|---|---|---|---|---|---|
| URS-001 | FS-001 | High | TS-001 | `tests/test_regimes.py::test_all_regimes_load`, `::test_gmp_is_active_by_default`, `::test_sox_uses_half_even` | `sst/regimes.py` | ER-2025-018 |
| URS-002 | FS-002 | High | TS-002 | `tests/test_audit.py::test_create_result_writes_audit_entry`, `::test_delete_is_soft_and_audited` | `sst/audit.py`, `sst/main.py` | ER-2025-018 |
| URS-003 | FS-003 | High | TS-002 | `tests/test_audit.py::test_delete_requires_reason`, `::test_delete_is_soft_and_audited`, `::test_reason_rule_is_regime_driven` | `sst/audit.py`, `sst/main.py::api_delete_result` | ER-2025-018 |
| URS-004 | FS-004 | High | TS-003 | `tests/test_rounding.py::test_half_up_rounding`, `::test_half_even_mode_for_financial_regimes`, `::test_unknown_mode_rejected`, `::test_decimal_places_from_limit`, `::test_evaluate_against_specification` | `sst/rounding.py` | ER-2025-018 |
| URS-005 | FS-005 | Medium | TS-004 | `tests/test_views.py::test_pages_render`, `::test_oos_visible_on_sample_page`, `::test_404s`, `::test_seed_shape` | `sst/main.py`, `sst/templates/` | ER-2025-018 |
| URS-006 | FS-006 | High | TS-004, TS-002 | `tests/test_views.py::test_pages_render` (`/results/1`, `/audit`), `tests/test_audit.py::test_audit_entries_are_append_only_at_api_level` | `sst/main.py` | ER-2025-018 |
| URS-007 | FS-007 | High | TS-002 | `tests/test_audit.py::test_create_result_writes_audit_entry` (actor = `X-User`) | `sst/main.py::current_user` | ER-2025-018 |
| URS-008 | FS-008 | High | TS-002 | `tests/test_audit.py::test_create_result_writes_audit_entry`, `::test_delete_is_soft_and_audited` | `sst/main.py` | ER-2025-018 |
| URS-009 | FS-002 | High | TS-002 | `tests/test_audit.py::test_create_result_writes_audit_entry` (ts generated server-side) | `sst/audit.py::utcnow` | ER-2025-018 |

Coverage: 9/9 URS traced to FS, test and code. Open gaps: none at r3.4.
