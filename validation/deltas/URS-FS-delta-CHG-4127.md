# URS / FS delta for CHG-4127 — Result amendment with second-person verification
**System:** Stability Sample Tracker 3.4.1 → target 3.5.0 · **Change request:** CHG-4127 ([issue #2](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/issues/2)) · **PR:** [#5](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/5) `feature/chg-4127-amend-results-r2` · **Code basis:** `08b7269` (`sst/main.py`, `sst/templates/result.html`) · **Regime:** GMP (`config/regimes/gmp.yaml`)
**Status:** Draft · **Author:** Devin (drafted for CHG-4127, session https://devin-gtm.devinenterprise.com/sessions/bfd89d4bc3484a2daf6bf5582de12fcc) · **Reviewed:** · **Approved:**
**Risk:** High (SOP-CSV-010 §5: modifies GxP records; changes the rounding/specification comparison that determines OOS; audit trail and access control) — see `RA-SST-CHG-4127.md`.

Purpose: URS/FS part of the SOP-CSV-010 §6 evidence package for a High-risk change (finding 7). Every statement below was derived from the code at `08b7269`; the full revised text is in `URS-SST.md` and `FS-SST.md` r3.5-draft.

## URS delta
| ID | New / Changed | Text | GxP impact | Source |
|---|---|---|---|---|
| URS-010 | New | Provisioned users with an authorised analyst or supervisor role (QC Analyst, Senior QC Analyst, QC Supervisor) shall be able to amend the measured value of a non-deleted assay result through the application only (result page or API), with a mandatory reason for change. The measured value shall be validated as a decimal number; an unchanged value shall be rejected. The original value shall be preserved in the audit trail and shown in the record history. The reportable value and OOS flag shall be recomputed per URS-004 and the result status set to `Amended`. | High | SOP-DI-004 §5.1–5.2; SOP-QC-021 §6.2; CHG-4127. Traces findings 1, 2, 3, 4, 6, 8 |
| URS-011 | New | An amendment that changes the OOS conclusion shall not be reportable until it is verified by a QC Supervisor other than the amending analyst; until then the result shall carry status `Amended - pending verification` and no further amendment shall be accepted. Verification shall be attributable, audited and require a reason for change. | High | SOP-DI-004 §5.3; `gmp.yaml` `second_person_verification_on_oos_change: true`; CHG-4127. Traces finding 5 |
| URS-002 | Changed | Adds: the audit-trail requirement explicitly covers amendment of the measured value (URS-010) and verification of an amendment (URS-011); entries are written in the same transaction as the change, and a modification that changes several fields records each changed field. | High | SOP-DI-004 §4.1, §4.4; 21 CFR 11.10(e). Traces finding 1 |
| URS-003 | Changed | Adds: the reason-for-change rule explicitly covers amendment and amendment verification; a request without a sufficient reason is rejected and leaves the record unchanged. | High | SOP-DI-004 §4.2, §5.1. Traces finding 2 |
| URS-008 | Changed | Adds: the JSON API allows amendment of the measured value (URS-010) and verification of a pending amendment (URS-011). | High | Interface spec IF-CDS-02; CHG-4127 |

## FS delta
| ID | New / Changed | Text | GxP impact | Source |
|---|---|---|---|---|
| FS-009 | New | `_amend()` via `PATCH /api/results/{id}` (body `{measured_value, reason}`) and form `POST /results/{id}/amend` (fields `measured_value`, `reason`); actor = `current_user()`. Checks in order: provisioned active user (`provisioned_user()`, 403); role in `AMEND_ROLES` {QC Analyst, Senior QC Analyst, QC Supervisor} (403); trimmed value matches `^-?\d+(\.\d+)?$` (422); result exists and is not deleted (404); status `Amended - pending verification` (409); identical `measured_value` text (422). Recomputes with `evaluate(measured, lower_limit, upper_limit, regime.results.rounding, regime.results.limit_inclusive)`. OOS changed and `second_person_verification_on_oos_change` → status `Amended - pending verification`, else `Amended`. One `audit.record(action="update")` row per changed field (`measured_value`, `reportable_value`, `oos`, `status`) with old/new value and reason, then `UPDATE`, then commit in one transaction; `ReasonRequired` → 422 + rollback. Form: 303 redirect on success; 403/409/422 re-render the result page with the message and that status. | High | URS-010, URS-011, URS-002, URS-003, URS-004, URS-007; `sst/main.py::_amend`, `::api_amend_result`, `::amend_result_form`. Traces findings 1, 2, 3, 4, 5, 6, 8 |
| FS-010 | New | `_verify()` via `POST /api/results/{id}/verify` (body `{reason}`) and form `POST /results/{id}/verify` (field `reason`); actor = `current_user()`. Provisioned (403); role in `VERIFY_ROLES` {QC Supervisor} (403); not deleted (404); status must be `Amended - pending verification` (409); actor must differ from the actor of the latest audit row that set that status (`_amended_by()`, 403). Writes one `update` audit row, field `status`, pending → `Amended`, with reason; sets `status='Amended'`; commit; `ReasonRequired` → 422 + rollback. No electronic signature (see finding 9). | High | URS-011, URS-002, URS-003, URS-007; `sst/main.py::_verify`, `::_amended_by`, `::api_verify_amendment`, `::verify_amendment_form`. Traces findings 4, 5 |
| FS-002 | Changed | Adds amendment (FS-009) and verification (FS-010) to the write paths that call `audit.record()` in the same transaction, via `_audit_updates()`; amendment writes one `update` row per changed field. | High | URS-002, URS-009, URS-010, URS-011; `sst/main.py::_audit_updates`. Traces finding 1 |
| FS-003 | Changed | `ReasonRequired` → 422 + rollback now also on `_amend()` and `_verify()` (API and form); reason length is measured after trimming (`reason.strip()`), GMP minimum 10 for `update`/`delete`; amend/verify on a deleted result → 404; deleted results are excluded from lists and the JSON API (the result page still shows them, FS-006). | High | URS-003; `sst/audit.py::record`, `sst/main.py`. Traces findings 2, 8 |
| FS-006 | Changed | Result page (`result.html`, also for soft-deleted results): amend form with measured value and reason-for-change fields, only when not deleted and not pending; when status is `Amended - pending verification`, a "Pending verification" banner citing SOP-DI-004 §5.3 and a verify form (reason) replace the amend form; amend/verify errors shown as an alert. Record history shows the original value of an amended field as `old_value`. | High | URS-006, URS-010, URS-011; `sst/main.py::_result_page`, `sst/templates/result.html`. Traces findings 1, 2, 5, 8 |
| FS-008 | Changed | Adds `PATCH /api/results/{id}` (FS-009; `AmendIn` pattern `^-?\d+(\.\d+)?$`, 422 otherwise) and `POST /api/results/{id}/verify` (FS-010); the amend form path validates `measured_value` server-side with the same pattern (`DECIMAL_RE`), so `1e3` and `abc` are rejected with 422. | High | URS-008, URS-010, URS-011; `sst/main.py`. Traces finding 6 |

## Impacted but unchanged
| ID | Why unchanged |
|---|---|
| URS-004 / FS-004 | Rounding and OOS rules are unchanged; FS-009 now calls the same `sst.rounding.evaluate()` with the regime's `rounding` and `limit_inclusive` instead of the float `round()` at `a90e609` (finding 3). Boundary testing for the amendment path is in TS-005 `test_amend_uses_sop_half_up_rounding_at_limit`. |
| URS-006 | Record history and audit view already required; FS-006 extended. No `audit_trail` update/delete route added. |
| URS-007 / FS-007 | `current_user()` unchanged; FS-009/FS-010 use it for attribution (finding 4). |
| URS-001 / FS-001 | Amendment reads `reason_min_length`, `second_person_verification_on_oos_change`, `rounding` and `limit_inclusive` from the regime; nothing hard-coded per regime. |
| Data model | Schema version 7 unchanged; `assay_results.status` gains values `Amended` and `Amended - pending verification`. |

## Findings trace (PR #5 review "CHG-4127 GxP findings for a90e609")
| # | Finding | Addressed by (requirement / function) | Verified by |
|---|---|---|---|
| 1 | No audit row on amendment (SOP-DI-004 §4.1/§4.4/§5.2) | URS-002, URS-010 / FS-002, FS-009, FS-006 | TS-006 `test_amend_writes_audit_row_per_changed_field`, `test_original_value_preserved_in_history_view` |
| 2 | No reason for change (SOP-DI-004 §4.2/§5.1) | URS-003, URS-010 / FS-003, FS-009, FS-006 | TS-005 `test_amend_requires_reason`, `test_amend_form_has_reason_and_is_hidden_on_deleted`; TS-006 `test_amend_and_verify_rejected_without_reason_leave_record_unchanged` |
| 3 | Float `round()` instead of `evaluate()` (SOP-QC-021 §4–§5) | URS-004, URS-010 / FS-004, FS-009 | TS-005 `test_amend_uses_sop_half_up_rounding_at_limit` |
| 4 | No provisioning/role check/attribution (SOP-DI-004 §5.1, §3) | URS-007, URS-010 / FS-007, FS-009, FS-010 | TS-005 `test_amend_rejects_unprovisioned_and_unauthorised_roles` |
| 5 | No second-person verification on OOS change (SOP-DI-004 §5.3) | URS-011 / FS-009, FS-010, FS-006 | TS-005 `test_oos_change_requires_second_person_verification`, `test_verifier_must_differ_and_be_supervisor`; TS-006 `test_verify_writes_audit_row` |
| 6 | No server-side validation on form (FS-008) | URS-010 / FS-008, FS-009 | TS-005 `test_amend_form_validates_decimal_server_side` |
| 7 | No evidence package (SOP-CSV-010 §6/§7/§8) | This delta, URS-SST/FS-SST r3.5-draft (URS/FS part); RA, TS-005/006, RTM, ER and CC by the other CHG-4127 deliverables | — |
| 8 | Form on deleted results; no-op amendments accepted (advisory) | URS-010 / FS-003, FS-006, FS-009 | TS-005 `test_amend_rejects_deleted_and_unchanged`, `test_amend_form_has_reason_and_is_hidden_on_deleted` |

## Out of scope of this delta (flagged)
- Finding 9: `gmp.yaml` `e_signature.required_for` lists `amendment_verification`, but SST has no electronic signature. No URS/FS for e-signature is drafted here; FS-010 records the gap. Separate CR for QA decision.
- Finding 10: `sst.__version__` is still `3.4.1`; target 3.5.0 is for the release CC.
- Finding 11: same change as PR #3 (merged, then reverted in PR #4 for an incomplete CC package); this delta is part of the package for the re-submission.
