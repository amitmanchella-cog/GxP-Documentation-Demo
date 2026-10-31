# RA-SST-CHG-4127 — Risk Assessment, CHG-4127 result amendment with second-person verification
**System:** Stability Sample Tracker 3.4.1 (release target 3.5.0, see open item F10) · **Change:** CHG-4127 ([issue #2](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/issues/2)), [PR #5](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/5) `feature/chg-4127-amend-results-r2` · **Regime:** GMP (`config/regimes/gmp.yaml`)
**Revision:** 3.5-draft (CHG-4127) · **Status:** Draft · **Method:** SOP-CSV-010 §5 (GxP impact → High/Medium/Low) with FMEA-style severity/probability/detectability on functions, as in `RA-SST.md`
**Author:** Devin (drafted for CHG-4127, session https://devin-gtm.devinenterprise.com/sessions/a0b666f3a4b84c259b6f21ef9a20abeb) · **Reviewed:** · **Approved:**

Assessed code: pre-fix PR head `a90e6092fe39b222b2f463271a7ac7e0045b4cf1` (findings 1–11, PR #5 review "CHG-4127 GxP findings for a90e609") and fixed head `08b7269e58e7ccd3432fdf91c4e0082676eddada`. Finding numbers (F1–F11) are those of that review. This record is the full risk assessment required for a High change by SOP-CSV-010 §6 and addresses the risk-assessment part of F7.

## 1. Change description
CHG-4127 adds amendment of an assay result's measured value (FS-009: `_amend()`, `PATCH /api/results/{id}`, `POST /results/{id}/amend`) and, after the fix, second-person verification of amendments that change the OOS conclusion (FS-010: `_verify()`, `POST /api/results/{id}/verify`, `POST /results/{id}/verify`). The amendment recomputes the reportable value and OOS flag through FS-004 and writes FS-002 audit rows. The result page (FS-006) gains the amend form, the verify form and a pending-verification banner. New requirements: URS-010 (amendment), URS-011 (second-person verification); changed: URS-002, URS-003, URS-008; changed functions: FS-002, FS-003, FS-006, FS-008.

Files changed against `main` at `08b7269`: `sst/main.py`, `sst/templates/result.html`, `CHANGELOG.md`. No change to `sst/db.py` (schema version 7), `sst/rounding.py`, `sst/audit.py` or `config/`.

## 2. GxP impact and risk classification (SOP-CSV-010 §4.2, §5)
**GxP impact: Yes.** The change modifies assay results used for stability reporting and batch disposition, and an amendment can change a reportable value and its OOS conclusion (product quality and data integrity).

| SOP-CSV-010 §5 High criterion | Applies | Justification |
|---|---|---|
| Creates, modifies or deletes GxP records | **Yes** | `_amend()` updates `measured_value`, `reportable_value`, `oos` and `status` of `assay_results`; `_verify()` updates `status`. |
| Changes a calculation, rounding or specification comparison that determines a reportable result or OOS status | **Yes** | The amendment path recomputes the reportable value and OOS flag. On `a90e609` it used its own float `round()` and comparison (F3); on `08b7269` it calls `sst.rounding.evaluate()` (FS-004) with the regime's `rounding` and `limit_inclusive`. Either way a new caller determines OOS status. |
| Changes audit trail, e-signature or access control | **Yes** | New mutation paths write `update` audit rows (FS-002/003); new role checks `AMEND_ROLES` / `VERIFY_ROLES` and the verifier ≠ amender rule (access control). E-signature is not changed; `gmp.yaml` `e_signature.required_for: [amendment_verification]` is open item F9. |
| Changes data migration | No | No schema or data change; existing rows are not touched. |

Any one criterion is sufficient (SOP-CSV-010 §5); three apply. **Classification: High.** The Medium criteria (display/filter/export only, no stored-value change) and Low criteria (no GxP impact) do not fit because stored GxP values change. The small diff size and the "UI + API only" description in the CR do not lower the classification (SOP-CSV-010 §4.2).

## 3. Scoring scales
| Score | Severity (Sev) | Probability (Prob) | Detectability (Det) |
|---|---|---|---|
| 1 | No GxP effect | Remote: prevented by a hard control verified by an automated test | Failure is certain to be detected (automated test in CI, or the system refuses the action) |
| 2 | Review inefficiency, record intact | Unlikely | Likely detected in routine use or review |
| 3 | Record or review gap, recoverable | Occasional | May be detected at audit-trail review |
| 4 | Loss of attribution or reason; SOP-DI-004 breach | Likely | Unlikely to be detected |
| 5 | Wrong reportable result / OOS conclusion, or original value lost; product disposition on wrong data | Every execution of the path | Not detectable (no test; silent) |

Risk class, following the ratings in `RA-SST.md` r3.4: **High** where Sev ≥ 4, or Sev = 3 and Sev×Prob×Det (RPN) ≥ 12; **Medium** where Sev is 2–3 otherwise; **Low** where Sev = 1. The rule is derived from the r3.4 ratings (r3.4 does not state it) and is for reviewer confirmation. Because classes are severity-driven, a High function stays High after controls; the reduction shows in Prob, Det and RPN, and High functions keep scripted CI testing (SOP-CSV-010 §7).

## 4. Pre-fix risk on `a90e609`
| ID | Function | Failure mode | Effect | Sev | Prob | Det | Risk | Finding / evidence (PR #5 review, verbatim reproduction on `a90e609`) |
|---|---|---|---|---|---|---|---|---|
| R-01 | FS-009 amendment | Amendment overwrites the result without an audit row | Original value lost; change not attributable or reconstructable (SOP-DI-004 §3 Original, §4.1, §4.4, §5.2) | 5 | 5 | 5 | **High** (RPN 125) | F1: `audit rows 1 -> 1` |
| R-02 | FS-009 amendment | Amendment accepted without reason for change | Loss of "why"; SOP-DI-004 §4.2, §5.1, SOP-QC-021 §6.2 breach | 4 | 5 | 5 | **High** (RPN 100) | F2: `PATCH 0.155 (no reason) -> HTTP 200` |
| R-03 | FS-009 amendment (reuse of FS-004) | Reportable value rounded with binary-float `round()` (ties-to-even), precision from `upper or lower`, regime mode and `limit_inclusive` ignored | OOS result reported as passing; product disposition on wrong data (SOP-QC-021 §4.1–§4.4, §5.1) | 5 | 3 | 5 | **High** (RPN 75) | F3: NMT 0.15: 0.155 → 0.15 pass (SOP 0.16, OOS); 95.0–105.0: 105.05 → 105.0 pass (SOP 105.1, OOS); 0.125 → 0.12 (SOP 0.13) |
| R-04 | FS-009 amendment | Unprovisioned user or non-analyst role amends; actor not recorded | Unauthorised change to GxP record; mis-attribution (SOP-DI-004 §5.1, §3 Attributable) | 5 | 4 | 5 | **High** (RPN 100) | F4: `unprovisioned X-User PATCH -> HTTP 200`; `Stability Coordinator (non-analyst) PATCH -> HTTP 200` |
| R-05 | FS-009 amendment (form) | No server-side validation of `measured_value` on the form path | Non-decimal value stored, or HTTP 500 (SOP-DI-004 §3 Accurate; FS-008) | 3 | 3 | 3 | **High** (RPN 27) | F6: `form measured_value='1e3' -> HTTP 303; stored measured_value='1e3'`; `'abc' -> HTTP 500` |
| R-06 | FS-009 amendment | No-op amendment accepted; amend of a pending or deleted record not guarded | Result marked `Amended` with no change (SOP-DI-004 §3 Consistent) | 2 | 3 | 2 | Medium (RPN 12) | F8: `no-op amendment to same value -> HTTP 200 status=Amended` |
| R-07 | FS-010 verification | OOS-changing amendment becomes reportable without second-person verification | Changed OOS conclusion reported without supervisor check (SOP-DI-004 §5.3; SOP-QC-021 §6.2; `gmp.yaml` `second_person_verification_on_oos_change: true`) | 5 | 4 | 5 | **High** (RPN 100) | F5: `OOS conclusion change 0 -> 1 status='Amended' (no verification step)` |
| R-08 | FS-010 verification | Amending analyst verifies own amendment (self-verification) | Second-person control defeated (SOP-DI-004 §5.3) | 5 | — | — | **High** | Not applicable on `a90e609`: no verification function existed (F5) |
| R-09 | FS-010 verification | Verification without reason or without audit row | Verification not attributable or reconstructable (SOP-DI-004 §4.1, §4.2) | 4 | — | — | **High** | Not applicable on `a90e609` (F5) |
| R-10 | FS-004 rounding & OOS (reuse) | Creation and amendment paths compute different reportable values for the same input; a later change to `evaluate()` affects a caller that is not tested | Same as R-03 | 5 | 3 | 5 | **High** (RPN 75) | F3 (amendment path bypassed FS-004) |
| R-11 | FS-006 result page / history | Amend form on deleted results; no reason field; no pending indication; original value not in history | Review gap; user misled about record state (SOP-DI-004 §4.3, §5.2) | 3 | 4 | 2 | **High** (RPN 24) | F8: `amend form rendered on soft-deleted result: True`; F2 (no reason input); F1 (no history row) |
| R-12 | FS-002 / FS-006 audit trail | Audit entries for the new path modifiable via the API | Audit trail can be obscured (SOP-DI-004 §4.3, §6d) | 5 | 1 | 3 | **High** (RPN 15) | Existing control unchanged (no update/delete route for `audit_trail`); no amendment rows existed to protect (F1) |
| R-13 | Evidence | No URS/FS/RA/TS/RTM/CC/ER for the change; no tests for the new code | Green CI says nothing about the change (SOP-CSV-010 §6, §7, §8) | 4 | 5 | 4 | **High** (RPN 80) | F7 |

## 5. Controls and residual risk on `08b7269`
| ID | Function | Failure mode | Effect | Sev | Prob | Det | Risk | Controls / required testing |
|---|---|---|---|---|---|---|---|---|
| R-01 | FS-009 amendment | Amendment without audit row | Original lost; not reconstructable | 5 | 1 | 1 | **High** (RPN 5) | `_audit_updates()` writes one `update` row per changed field (`measured_value`, `reportable_value`, `oos`, `status`) with actor, old/new value and reason through the single writer `audit.record()` (FS-002), in the same transaction as the `UPDATE`. Original value kept as `old_value` and shown on the history view (SOP-DI-004 §5.2). **TS-006:** `test_amend_writes_audit_row_per_changed_field` (§6a/b), `test_original_value_preserved_in_history_view`. |
| R-02 | FS-009 amendment | Amendment without reason | Loss of "why" | 4 | 1 | 1 | **High** (RPN 4) | `AmendIn.reason` required; form has a required reason field (`minlength` from regime); `audit.record()` raises `ReasonRequired` below `reason_min_length` (GMP 10) → HTTP 422 and rollback, record unchanged (FS-003). **TS-005:** `test_amend_requires_reason`, `test_amend_form_has_reason_and_is_hidden_on_deleted`. **TS-006:** `test_amend_and_verify_rejected_without_reason_leave_record_unchanged` (§6c). |
| R-03 | FS-009 amendment (reuse of FS-004) | Wrong rounding / comparison at the limit | OOS reported as pass | 5 | 1 | 1 | **High** (RPN 5) | `_amend()` calls `sst.rounding.evaluate(measured, lower, upper, regime.results.rounding, regime.results.limit_inclusive)`; precision from both limits; exact decimal, half-up for GMP (SOP-QC-021 §4.1–§4.3, §5.1). **TS-005:** `test_amend_uses_sop_half_up_rounding_at_limit`, parametrized at and either side of NMT 0.15 (0.150, 0.154, 0.155, 0.156) and 95.0–105.0 (94.94, 94.95, 105.04, 105.05) (SOP-CSV-010 §7 boundary cases). Regression: TS-003. |
| R-04 | FS-009 amendment | Unauthorised amendment / mis-attribution | Unauthorised change; mis-attribution | 5 | 1 | 1 | **High** (RPN 5) | Actor from `current_user()` (`X-User`, FS-007); `provisioned_user()` → 403 if not an active SST user; role must be in `AMEND_ROLES` {QC Analyst, Senior QC Analyst, QC Supervisor} → else 403; actor stored on every audit row (SOP-DI-004 §5.1, §3). Relies on the SSO proxy enforcing `X-User` in production (existing FS-007 control). **TS-005:** `test_amend_rejects_unprovisioned_and_unauthorised_roles`. **TS-006:** `test_amend_writes_audit_row_per_changed_field` (actor). |
| R-05 | FS-009 amendment | Invalid measured value accepted | Bad value stored / HTTP 500 | 3 | 1 | 1 | Medium (RPN 3) | `DECIMAL_RE` `^-?\d+(\.\d+)?$` checked in `_amend()` for both paths (plus Pydantic pattern on the API) → 422; the form re-renders the result page with the message and the HTTP error status. **TS-005:** `test_amend_form_validates_decimal_server_side`. |
| R-06 | FS-009 amendment | No-op, pending or deleted amendment | Misleading `Amended` status | 2 | 1 | 1 | Medium (RPN 2) | Identical value → 422; deleted → 404; status `Amended - pending verification` → 409. **TS-005:** `test_amend_rejects_deleted_and_unchanged`. |
| R-07 | FS-010 verification | Verification bypass | Changed OOS conclusion reported unverified | 5 | 2 | 2 | **High** (RPN 20) | When the OOS conclusion changes and `second_person_verification_on_oos_change` is true, status is `Amended - pending verification`; further amendment is refused (409) while pending; `_verify()` is the only path to `Amended`; verify on a non-pending result → 409; pending banner on the result page (SOP-DI-004 §5.3). **TS-005:** `test_oos_change_requires_second_person_verification`. Prob/Det kept at 2: the new reportable value and OOS flag are already stored while pending, so sample/study views (FS-005) and API consumers must honour `status` (open item O-1). |
| R-08 | FS-010 verification | Self-verification | Second-person control defeated | 5 | 1 | 1 | **High** (RPN 5) | Role must be in `VERIFY_ROLES` {QC Supervisor} → else 403; `_amended_by()` finds the actor who set the pending status and refuses the same actor (403), so a QC Supervisor cannot verify an amendment they made. Depends on unique user IDs (SOP-DI-004 §3, no shared accounts). **TS-005:** `test_verifier_must_differ_and_be_supervisor`. |
| R-09 | FS-010 verification | Verification without reason / audit row | Not attributable or reconstructable | 4 | 1 | 1 | **High** (RPN 4) | `_verify()` writes an audit row field `status`, pending → `Amended`, with actor and mandatory reason; `ReasonRequired` → 422 and rollback. **TS-006:** `test_verify_writes_audit_row` (§6a/b), `test_amend_and_verify_rejected_without_reason_leave_record_unchanged` (§6c). |
| R-10 | FS-004 rounding & OOS (reuse) | Divergence between creation and amendment paths; later change to `evaluate()` | Same as R-03 | 5 | 1 | 1 | **High** (RPN 5) | Both paths call the same `evaluate()`; `sst/rounding.py` unchanged by CHG-4127. Any future change to FS-004 stays High (RA-SST) and must re-run TS-003 and TS-005. **TS-003** (regression) and **TS-005** `test_amend_uses_sop_half_up_rounding_at_limit`. |
| R-11 | FS-006 result page / history | Wrong form state; history missing original | Review gap; user misled | 3 | 1 | 1 | Medium (RPN 3) | No amend form on deleted results; verify form replaces amend form while pending; reason field on both forms; history table lists every amendment and verification row. **TS-005:** `test_amend_form_has_reason_and_is_hidden_on_deleted`. **TS-006:** `test_original_value_preserved_in_history_view`. Regression: TS-004. |
| R-12 | FS-002 / FS-006 audit trail | Audit entries modifiable via API | Audit trail obscured | 5 | 1 | 1 | **High** (RPN 5) | No update/delete route for `audit_trail` (FS-006). **TS-006:** `test_audit_entries_not_modifiable_via_api_after_amend` (§6d). Regression: TS-002 `test_audit_entries_are_append_only_at_api_level`. |
| R-13 | Evidence | Incomplete evidence package | Change not demonstrably controlled | 4 | 2 | 2 | **High** (RPN 16) | This RA plus the parallel CHG-4127 deliverables: `deltas/URS-FS-delta-CHG-4127.md`, `test_scripts/TS-005.md`, `TS-006.md`, `RTM.md`, `change_control/CC-CHG-4127.md`, `executed_results/ER-CHG-4127.md` (verbatim CI output for the final SHA). Prob/Det stay at 2 until those are drafted, executed in CI and approved by named humans (SOP-CSV-010 §4.7). |

### Finding coverage
| Finding | Class | RA rows | Status in this draft |
|---|---|---|---|
| F1 no audit row | Blocking | R-01, R-11, R-12 | Fixed in `08b7269`; traced to TS-006 |
| F2 no reason | Blocking | R-02, R-09, R-11 | Fixed; traced to TS-005, TS-006 |
| F3 float rounding | Blocking | R-03, R-10 | Fixed; traced to TS-005, TS-003 |
| F4 no authorisation / attribution | Blocking | R-04 | Fixed; traced to TS-005, TS-006 |
| F5 no second-person verification | Blocking | R-07, R-08, R-09 | Fixed; traced to TS-005, TS-006; open item O-1 |
| F6 no server-side validation | Blocking | R-05 | Fixed; traced to TS-005 |
| F7 no evidence package | Blocking | R-13 | RA part drafted here; other deliverables in parallel |
| F8 form on deleted / no-op accepted | Advisory | R-06, R-11 | Fixed; traced to TS-005 |
| F9 e-signature for verification | Advisory | — | Open, out of scope (§7) |
| F10 version 3.4.1 vs 3.5.0 | Advisory | — | Open, release CC (§7) |
| F11 history of PR #3 / #4 | Advisory | — | Open, to be stated in CC (§7) |

## 6. Testing approach (SOP-CSV-010 §7, §8; SOP-DI-004 §6)
High risk: scripted tests with pre-defined steps and expected results, automated and executed in the CI pipeline, each traced in the RTM to URS-010/011 and FS-009/010 (and the changed URS-002/003/008, FS-002/003/006/008).
- **TS-005** (`validation/test_scripts/TS-005.md`, automated in `tests/test_amend.py`): amendment and verification behaviour, including boundary values at and either side of each limit (R-03, R-10) and negative cases (R-02, R-04 to R-08).
- **TS-006** (`validation/test_scripts/TS-006.md`, automated in `tests/test_amend_audit.py`): audit-trail verification for the amendment and verification paths.
- **Regression:** TS-001 to TS-004 on the same SHA.
- **Executed results:** `validation/executed_results/ER-CHG-4127.md`, CI job ID, commit SHA and pass/fail, output pasted verbatim (SOP-CSV-010 §4.6, §7).

| SOP-DI-004 §6 | Test |
|---|---|
| (a) audit entry for each create/modify/delete path touched | `test_amend_writes_audit_row_per_changed_field`, `test_verify_writes_audit_row` |
| (b) old and new values captured | same two tests; `test_original_value_preserved_in_history_view` (§5.2) |
| (c) change rejected without a reason | `test_amend_and_verify_rejected_without_reason_leave_record_unchanged`, `test_amend_requires_reason` |
| (d) audit entries cannot be modified via the API | `test_audit_entries_not_modifiable_via_api_after_amend` |

## 7. Open items
| ID | Item | Owner / route |
|---|---|---|
| F9 | `gmp.yaml` lists `amendment_verification` under `e_signature.required_for`, but SST has no e-signature function. After the fix, verification is attributable (SSO user, QC Supervisor role, verifier ≠ amender, audit row with reason) but is **not** an electronic signature (21 CFR 11.50/11.70, referenced). Adding e-signature would itself be a High change (SOP-CSV-010 §5) and needs a **separate CR**. QA to decide whether CHG-4127 may be released without it, or whether that CR is a prerequisite. The residual risk of R-07/R-08 is scored without e-signature. | QA decision; separate CR |
| F10 | `pyproject.toml` version is still 3.4.1; CR #2 targets 3.5.0. The version bump, VSR update (superseding VSR-SST-3.4) and release note belong to the **release CC** (SOP-CSV-010 §4.8). | Release CC |
| F11 | The same change was merged as PR #3 (`a03a9c6`) and reverted in PR #4 (`1a85efa`) because its change-control package was incomplete. `CC-CHG-4127.md` must record this history (SOP-CSV-010 §4.5, §8). No residual risk from the revert itself: `main` does not contain the amendment code. | CC-CHG-4127 |
| O-1 | Observation, not a numbered finding: while a result is `Amended - pending verification`, its new reportable value and OOS flag are already stored. The result page shows a banner. The sample page shows the status text and the study/sample OOS counts include the new flag. `GET /api/results/{id}` returns the status, and consumers (IF-CDS-02) must treat pending results as not reportable. To be confirmed by QC/QA as adequate for SOP-DI-004 §5.3 "before the result is reportable", or raised as a follow-up. | QC Supervisor / QA review of this RA |
| O-2 | Acceptance of the residual risk in §5 and confirmation of the scoring rule in §3. | Reviewer and QA (SOP-CSV-010 §4.7) |

## 8. Periodic review impact note (SOP-CSV-010 §6)
CHG-4127 adds a new way to modify GxP results and a second-person control, so it affects the scope of the next SST periodic review:
- RA-SST r3.5 (with the FS-009/FS-010 rows) supersedes r3.4 on approval. The periodic review should confirm that R-01 to R-12 and their controls still hold.
- Audit-trail review (SOP-DI-004 §4.6) now covers result amendments and verifications. QC supervisors review them at batch disposition; QA's quarterly sample should include `update` rows on `assay_result` and their reasons.
- The periodic review should check for results left in `Amended - pending verification` and confirm that no verification was performed by the amending user.
- The status of F9 (e-signature CR) and O-1 should be recorded at the next review.
- No change to the review frequency is proposed; that decision rests with the system owner and QA.

## 9. Approvals (humans only; e-signature in QMS)
| Role | Name | Decision | Date |
|---|---|---|---|
| Technical reviewer | | | |
| System owner | | | |
| QA | | | |
