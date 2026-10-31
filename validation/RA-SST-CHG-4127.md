# RA-SST-CHG-4127 — Risk Assessment
**System:** SST 3.4.1 → 3.5.0 · **Change:** CHG-4127 (issue #2, PR #6) · **Document revision:** 3.5 · **Status:** Draft (pending QA approval)
**Method:** SOP-CSV-010 §5 (GxP impact → High/Medium/Low) with FMEA-style severity/probability/detectability on functions, as in `RA-SST.md` · **Scope of full RA:** SOP-CSV-010 §6 (High)
**Author / Reviewed / Approved:** Drafted by Devin (drafting assistance under SOP-CSV-010 §4.7) / — / — (approval fields left blank; see §7)

Code reviewed: `d4a226e` (as submitted) and `805496c` (fix) on `feature/chg-4127-amend-results-r3`. Findings F1–F12 refer to the GxP findings review on PR #6. Scales are 1–5 (Det 5 = hardest to detect). Inherent ratings describe `d4a226e`; residual ratings describe `805496c` with the listed controls in place.

## 1. Functions affected
| Function | Change | Source |
|---|---|---|
| FS-009 (new) | `_amend` + `PATCH /api/results/{id}` (`measured_value`, `reason`) and `POST /results/{id}/amend` form | `sst/main.py`, `sst/templates/result.html` |
| FS-010 (new) | `_verify` + `POST /api/results/{id}/verify` (`reason`) and `POST /results/{id}/verify` form; status `Pending verification` → `Amended` | `sst/main.py`, `sst/templates/result.html` |
| FS-002, FS-003 | Audit row and reason for change on the new update paths | `sst/audit.py` (unchanged), called from `_amend`/`_verify` |
| FS-004 | Recomputation on amendment via `sst.rounding.evaluate` with regime `rounding` and `limit_inclusive` | `sst/rounding.py` (unchanged) |
| FS-006 | Result history shows amendment and verification rows | `sst/templates/result.html` |
| FS-007 | Attribution and role check (`AMEND_ROLES`, `VERIFY_ROLES`, `provisioned_user`) on the new paths | `sst/main.py` |
| FS-008 | API validation for the new `PATCH` and verify payloads | `sst/main.py` (`AmendIn`, `VerifyIn`) |

CR #2 lists only FS-005/006/008 (F10). This RA uses the corrected function list above; correcting the CR is for the Change Owner and QA.

## 2. Inherent risk (as submitted, `d4a226e`)
| ID | Function | Failure mode | Effect | Sev (1-5) | Prob (1-5) | Det (1-5) | Risk | Controls / required testing |
|---|---|---|---|---|---|---|---|---|
| R-01 (F1) | FS-002, FS-009 | Amendment updates `measured_value`, `reportable_value`, `oos`, `status` without an audit row | GxP record change not attributable or reconstructable; SOP-DI-004 §4.1, §4.5; URS-002 | 5 | 5 | 4 | **High** | One `audit.record()` row per changed field in the same transaction; TS-005, TS-006 |
| R-02 (F2) | FS-003, FS-009, FS-010 | Amendment accepted with no / short reason for change | Loss of "why"; SOP-DI-004 §4.2, §5.1; URS-003 | 4 | 5 | 3 | **High** | Mandatory `reason` on API and form, regime `reason_min_length`; negative tests TS-005 |
| R-03 (F3) | FS-002, FS-009 | Original measured/reportable/OOS values overwritten in place with no history | Original record lost; SOP-DI-004 §3 (Original), §5.2 | 5 | 5 | 4 | **High** | Old value written as `old_value` per field before update; TS-005, TS-006 |
| R-04 (F4) | FS-004, FS-009 | Reportable value computed with `round(float(...))` (binary float, banker's rounding), regime mode ignored | 0.155 → 0.15 against NMT 0.15: OOS reported as passing; SOP-QC-021 §4.2–§4.3 | 5 | 4 | 3 | **High** | Use `sst.rounding.evaluate` with regime `rounding`; boundary tests TS-005 |
| R-05 (F5) | FS-004, FS-009 | Spec comparison re-implemented: precision from `upper or lower`, `limit_inclusive` ignored | OOS result cleared to within specification; SOP-QC-021 §5.1–§5.2; URS-004 | 5 | 4 | 3 | **High** | Same as R-04 plus two-sided limit boundary tests TS-005 |
| R-06 (F6) | FS-007, FS-009 | Amendment not attributed; unprovisioned or unauthorised user can amend | Mis-attribution, unauthorised change; SOP-DI-004 §3 (Attributable), §5.1; URS-007 | 4 | 5 | 3 | **High** | `current_user` + `provisioned_user` + `AMEND_ROLES`; actor on audit rows; negative tests TS-005 |
| R-07 (F7) | FS-010 | Amendment that changes the OOS conclusion becomes reportable with no second-person verification | OOS conclusion changed by one person; product disposition on unverified data; SOP-DI-004 §5.3; SOP-QC-021 §6.2; `gmp.yaml` `second_person_verification_on_oos_change: true` | 5 | 5 | 3 | **High** | `Pending verification` status; verification by a different QC Supervisor with reason; TS-005 |
| R-08 (F9) | FS-008, FS-009 | Form route has no server-side value validation (`abc` → HTTP 500) | Failed or malformed update to a GxP record; SOP-QC-021 §6.1 | 3 | 4 | 2 | **High** | Server-side pattern check on both routes (422); negative tests TS-005 |
| R-09 (F11) | FS-010 | Verification is not an electronic signature although `gmp.yaml` lists `amendment_verification` under `e_signature.required_for` | Verification may not meet 21 CFR 11.50/11.200 as a signature | 4 | 5 | 1 | **High** | No SST capability; QA decision required (§4) |
| R-10 (F12) | FS-009 | No-op amendment (same value) sets status `Amended` | Misleading record status and audit history; SOP-DI-004 §4.1 | 2 | 3 | 2 | Medium | Reject identical value (422); TS-005 |
| R-11 | FS-009, FS-010 | Amend or verify applied to a soft-deleted result | Deleted record silently changed; SOP-DI-004 §4.3 | 4 | 2 | 2 | **High** | `_get_result` excludes `deleted=1` (404); scripted test required |

## 3. Controls implemented in `805496c` and residual risk
| ID | Control implemented (`805496c`) | Verifying test | Residual Sev / Prob / Det | Residual risk | Status |
|---|---|---|---|---|---|
| R-01 (F1) | `_amend` calls `audit.record()` (action `update`) for each changed field (`measured_value`, `reportable_value`, `oos`, `status`) with actor, UTC ms timestamp (`Z`), old/new value and reason; `_verify` writes a `status` row. Audit rows and the `UPDATE` are committed together; `ReasonRequired` rolls back. | TS-005: `test_amend_writes_audit_rows_with_old_and_new_values`, `test_oos_change_requires_supervisor_verification`; TS-006 (SOP-DI-004 §6 a–d, `tests/test_amend_audit.py`) | 5 / 1 / 2 | Low | Fixed |
| R-02 (F2) | `AmendIn.reason` and `VerifyIn.reason` mandatory; form `reason` field (required); `audit.record()` enforces regime `reason_min_length` (10 under GMP) → 422 and rollback, no partial change. | TS-005: `test_amend_rejected_without_adequate_reason` (`""`, `"   "`, `"too short"`), `test_amend_api_requires_reason_field`, `test_form_rejects_missing_reason`, `test_verify_requires_reason_and_pending_state` | 4 / 1 / 2 | Low | Fixed |
| R-03 (F3) | Prior values of every changed field are retained as `old_value` in the append-only `audit_trail` (no update/delete route, FS-006) and shown in the result history. The `assay_results` row holds the current value only. | TS-005: `test_amend_writes_audit_rows_with_old_and_new_values` (0.155 / 0.16 / OOS 1 retained as old values); TS-006 | 5 / 1 / 2 | Low | Fixed — QA to confirm that retention of the original value in the audit trail meets SOP-DI-004 §5.2 |
| R-04 (F4) | `_amend` uses `sst.rounding.evaluate(measured, lower, upper, regime.results.rounding, regime.results.limit_inclusive)`; exact `Decimal` half-up under GMP (SOP-QC-021 §4). | TS-005: `test_amend_nmt_within_spec` (0.145 → 0.15, 0.149/0.150/0.151/0.154 → 0.15), `test_amend_nmt_oos_retained` (0.1551/0.156 → 0.16) | 5 / 1 / 2 | Low (function stays High for testing rigour) | Fixed |
| R-05 (F5) | Same single implementation as FS-004: precision from the more precise limit, inclusive comparison from the regime (SOP-QC-021 §5). | TS-005: `test_amend_nmt_oos_retained`, `test_amend_two_sided_limits` (94.94/94.95/95.0/105.0/105.04/105.05/105.1 against 95.0–105.0) | 5 / 1 / 2 | Low (function stays High) | Fixed |
| R-06 (F6) | `current_user()` actor recorded on every audit row; `provisioned_user()` rejects unprovisioned users (403); `AMEND_ROLES` = QC Analyst, Senior QC Analyst, QC Supervisor (QA cannot amend). | TS-005: `test_amend_rejects_unprovisioned_user`, `test_amend_rejects_qa_role`; actor asserted in `test_amend_writes_audit_rows_with_old_and_new_values` | 4 / 2 / 3 | **High** — see G2 | Fixed for F6 as raised; G2 open |
| R-07 (F7) | If the OOS flag changes and `second_person_verification_on_oos_change` is true, status is `Pending verification`. `_verify` requires that status (409 otherwise), role QC Supervisor (`VERIFY_ROLES`), a verifier different from the last amender (`_last_amender`), and a reason; writes an audit row and sets `Amended`. Result page shows the verification form while pending. | TS-005: `test_oos_change_requires_supervisor_verification`, `test_verifier_must_differ_from_amender`, `test_verify_requires_reason_and_pending_state`, `test_amend_without_oos_change_needs_no_verification`, `test_form_amend_and_verify_flow` | 5 / 3 / 3 | **High** — see G1 | Partially fixed; G1 open |
| R-08 (F9) | `MEASURED_VALUE_PATTERN` checked server-side in `_amend` for both routes (422 before any write); Pydantic validation on `AmendIn`. | TS-005: `test_form_rejects_non_numeric_value`, `test_api_rejects_non_numeric_value` | 3 / 1 / 1 | Low | Fixed |
| R-09 (F11) | Verification recorded as an attributed, reason-bearing `audit_trail` entry by a different QC Supervisor. This is **not** an electronic signature. | TS-005 (verification entry); no test can close this risk in SST | 4 / 5 / 1 | **High** — QA decision | Open — QA decision (§4) |
| R-10 (F12) | `_amend` rejects a value numerically equal (`Decimal`) to the current measured value (422, no audit row, no status change). | TS-005: `test_amend_rejects_identical_value` | 2 / 1 / 1 | Low | Fixed |
| R-11 | `_get_result` returns 404 for `deleted=1` before any amend/verify logic. | No scripted case in TS-005 at `805496c` (checked ad hoc: amend after soft delete → 404). Flagged for addition to TS-005. | 4 / 1 / 2 | Low once scripted | Control present; test gap flagged |

Local pre-check (not CI evidence) at `805496c`: `tests/test_amend.py` 31 passed; full suite 70 passed. CI evidence for this change is recorded in `validation/executed_results/ER-CHG-4127.md`.

### Open gaps identified during this assessment (not closed by `805496c`)
| Gap | Description | Reproduction at `805496c` (seeded data, GMP) | Effect | Recommended action |
|---|---|---|---|---|
| **G1** (R-07, F7) | `oos_changed` compares the new OOS flag with the *current* row, not with the value last verified/released. A second amendment made while the result is `Pending verification` that leaves the flag unchanged sets status `Amended`, so the OOS-conclusion change is never verified. | R-000047 (0.155, OOS, NMT 0.15): analyst `mfarouk` amends to 0.154 → `Pending verification`, OOS 0; analyst `jokafor` amends to 0.150 → `Amended`, OOS 0. No QC Supervisor verification recorded. | OOS result cleared to within specification by analysts only; SOP-DI-004 §5.3, SOP-QC-021 §6.2 not met | Code fix before approval: keep `Pending verification` while pending (or compare with the OOS flag at the last `Amended`/created state) and add a TS-005 negative test for re-amendment while pending |
| **G2** (R-06, FS-007) | `current_user()` falls back to `os.environ.get("SST_USER", "mfarouk")`: with no `X-User` header and no `SST_USER`, the request is attributed to provisioned analyst `mfarouk`. Pre-existing at `main`; the `RA-SST` r3.4 FS-007 control states the fallback applies "only when `SST_USER` set". | `PATCH /api/results/{id}` with no `X-User` and `SST_USER` unset → 200, audit `actor` = `mfarouk`. | Amendment mis-attributed if the proxy header is missing; the F6 provisioning check does not detect it | Change Owner/QA to decide: remove the default (403 when no identity) under this change or a follow-up CR; until then the control relies on the SSO proxy (FS-007) |

## 4. F11 — electronic signature for amendment verification (QA decision)
`config/regimes/gmp.yaml` lists `amendment_verification` under `e_signature.required_for`. SST has no e-signature capability; `_verify` records an attributed audit entry with a reason (user ID, UTC timestamp, old/new status), which is not a signature under 21 CFR 11.50/11.200. Residual risk stays **High** until QA decides one of:
1. The e-signature for amendment verification is applied in the QMS against the SST audit entry (procedural control, to be written into the governing SOP/work instruction), or
2. A follow-up CR adds e-signature capability to SST, with `Pending verification` results treated as not reportable until then.

Decision, rationale and owner are recorded by QA in the CC record (`validation/change_control/CC-CHG-4127.md`). This RA does not make that decision.

## 5. Findings not rated as risk rows
- **F8** (missing evidence package) — process finding. Addressed by the package for this change: URS/FS delta (URS-010, URS-011; FS-009, FS-010), this RA and `RA-SST.md` r3.5, TS-005, TS-006, `ER-CHG-4127.md`, `RTM.md`, `CC-CHG-4127.md`.
- **F10** (CR function list) — see §1.

## 6. Classification, testing approach and periodic-review impact
Classification: **High** (SOP-CSV-010 §5). The change modifies GxP records, recomputes the reportable value and OOS status, and adds write paths subject to audit trail, reason for change, access control and e-signature requirements. FS-009 and FS-010 are new High functions; FS-002, FS-003, FS-004, FS-006, FS-007 and FS-008 remain at their `RA-SST` ratings.

Testing approach (SOP-CSV-010 §7): scripted automated tests executed in CI for all High rows — TS-005 (amendment, rounding/OOS boundaries at and either side of each limit, negative cases, second-person verification; `tests/test_amend.py`) and TS-006 (SOP-DI-004 §6 audit-trail verification; `tests/test_amend_audit.py`); full regression (TS-001–TS-004) on the same commit. Executed results with CI job, commit SHA and pass/fail in `ER-CHG-4127.md`. G1 and the R-11 test gap need TS-005 additions before the package is put forward for approval.

Periodic-review impact: the next SST periodic review should (a) include FS-009/FS-010 in scope and use `RA-SST.md` r3.5 once approved; (b) review `audit_trail` `update` entries on `assay_result` (`measured_value`, `oos`, `status`) for amendment frequency, reasons and verifier ≠ amender; (c) check for results left in `Pending verification`; (d) confirm the QA decision on F11 is implemented and effective; (e) confirm closure of G1 and G2. No periodic-review date is set by this document.

## 7. Approvals (humans only; e-signature in QMS)
| Role | Name | Decision | Date |
|---|---|---|---|
| Author (CSV) | | | |
| Reviewer (QC Supervisor) | | | |
| Approver (QA) | | | |
