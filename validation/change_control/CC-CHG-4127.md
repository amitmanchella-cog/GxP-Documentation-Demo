# CC-CHG-4127 — Amendment of assay results with audit trail and second-person verification
**System:** SST 3.4.1 → target 3.5.0 · **Status:** Draft · **Raised:** 2026-10-31 by T. Brennan (Stability Coordinator, requester per [CHG-4127 / issue #2](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/issues/2)) · **Change Owner:** P. Natarajan (per issue #2) · **QA:** 
**Author:** Devin (drafted for CHG-4127, session https://devin-gtm.devinenterprise.com/sessions/f7412005b33a44b7a8716574a4959ee2) · **Reviewed:**  · **Approved:** 

## 1. Description and reason
Change request [CHG-4127 (issue #2)](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/issues/2) asks for an amendment function so that a transcription error in a result's measured value can be corrected in place on the existing result, instead of soft-deleting it and re-entering it under a new ID (which splits the record and makes trend reports harder to read). Requested scope: an **Amend** action on `/results/{id}`, `PATCH /api/results/{id}` for the CDS interface, recalculation of the reportable value and OOS flag from the corrected value, and status `Amended`.

Implementation is in [PR #5](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/5) (`feature/chg-4127-amend-results-r2`). As drafted for this record, the change:
- routes both amendment paths (`PATCH /api/results/{id}`, `POST /results/{id}/amend`) through one `_amend()` that requires a provisioned user in an amend role (QC Analyst, Senior QC Analyst, QC Supervisor), validates the decimal server-side, recomputes reportable value and OOS with `sst.rounding.evaluate()` using the regime's rounding and limit settings, and writes one `update` audit row per changed field with a mandatory reason in the same transaction (SOP-DI-004 §4.1, §4.2, §5.1–§5.2; SOP-QC-021 §4–§5);
- sets status `Amended - pending verification` when an amendment changes the OOS conclusion, and adds `_verify()` (`POST /api/results/{id}/verify`, `POST /results/{id}/verify`) so a QC Supervisor other than the amending analyst can verify it, with reason and audit row (SOP-DI-004 §5.3; `gmp.yaml` `second_person_verification_on_oos_change: true`).

**History (finding 11):** this is the same change as [PR #3](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/3) (`ef700f6`, merged as `a03a9c6`), which was merged to main and then reverted in [PR #4](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/4) (`1a85efa`) because its change-control package was not complete (SOP-CSV-010 §4.5, §8). PR #5 re-raises the change; it must not be merged until the evidence package in §3 is complete and the approvals in §5 are recorded.

## 2. GxP impact assessment
Summarised from the GxP impact & risk assessment comment on [PR #5](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/5) (assessed under SOP-CSV-010 §4.2–§4.4, §5, §6, §7; active regime `config/regimes/gmp.yaml`).

| Area | Effect of the change | GxP record / control |
|---|---|---|
| `assay_results` row | Amendment overwrites `measured_value`, `reportable_value`, `oos`, `status` | **Modifies GxP records** (QC stability results used for batch disposition) |
| Reportable value / OOS | Recomputed on amendment | **Changes a calculation, rounding and specification comparison that determines OOS** (SOP-QC-021 §4–§5) |
| Audit trail | New mutation path and new verification path | **Audit trail** (SOP-DI-004 §4) |
| Access control / attribution | New write endpoints | **Access control** (SOP-DI-004 §3, §5.1) |
| Second-person verification | Amendment can change the OOS conclusion | SOP-DI-004 §5.3; `gmp.yaml` |
| Validated functions affected | FS-002, FS-003, FS-004, FS-005, FS-006, FS-007, FS-008; new FS-009, FS-010 (the CR lists FS-005/006/008 only) | URS-002, -003, -004, -006, -007, -008; new URS-010, URS-011 |

GxP impact **Yes**: product quality and data integrity are affected, because an amendment can change a reportable result and its OOS conclusion.

Risk level per SOP-CSV-010 §5: **High**. Each of the following §5 High criteria applies on its own:
- it modifies GxP records (result amendment);
- it changes the rounding and specification comparison that determine a reportable result and OOS status;
- it changes audit-trail and access-control behaviour (new mutation and verification paths).

The diff size (+33 lines in the original commit) does not lower the classification, and "UI + API only" is not an exemption (SOP-CSV-010 §4.2). Testing approach: scripted automated tests executed in CI (SOP-CSV-010 §7); every new or changed URS/FS traced in the RTM (§8).

**Periodic review impact:** the next SST periodic review must include URS-010/URS-011, FS-009/FS-010, TS-005/TS-006 and a review of `Amended` and `Amended - pending verification` results and their audit-trail entries (SOP-DI-004 §6). Finding 9 (e-signature on amendment verification) remains open and should be tracked in the periodic review until its separate CR is decided.

## 3. Evidence package (SOP-CSV-010 §6, High)
| Deliverable | Reference |
|---|---|
| GxP impact assessment | §2 of this record; PR #5 impact assessment comment |
| URS delta | `validation/deltas/URS-FS-delta-CHG-4127.md` — new URS-010, URS-011; changed URS-002, URS-003, URS-008 |
| FS delta | `validation/deltas/URS-FS-delta-CHG-4127.md` — new FS-009, FS-010; changed FS-002, FS-003, FS-006, FS-008 |
| Risk assessment | `validation/RA-SST-CHG-4127.md` + new rows in `validation/RA-SST.md` |
| Test scripts | `validation/test_scripts/TS-005.md` (amendment, rounding at and either side of each limit, negative cases) automated in `tests/test_amend.py`; `validation/test_scripts/TS-006.md` automated in `tests/test_amend_audit.py` |
| Executed results (CI job, commit SHA, pass/fail) | `validation/executed_results/ER-CHG-4127.md` — [run 41238179614 / job 124646264910](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41238179614/job/124646264910) on `43da149` (last code/test commit): success, 62 passed, coverage 93.57% |
| RTM | `validation/RTM.md` — rows for URS-010, URS-011; updated rows for URS-002, URS-003, URS-004, URS-006, URS-007, URS-008 |
| Audit-trail verification (SOP-DI-004 §6) | TS-006 (§6 a–d), automated in `tests/test_amend_audit.py`, executed in CI |
| Change-control record | this document |
| Periodic review impact note | §2 of this record |

## 3a. Findings on the original change (`a90e609`) and disposition
Findings from the PR #5 review "CHG-4127 GxP findings for a90e609"; numbering is fixed.

| # | Class | Finding | SOP clause | Disposition |
|---|---|---|---|---|
| 1 | Blocking | No audit-trail row on amendment; original value lost | SOP-DI-004 §4.1, §4.4, §5.2 | Fixed in `08b7269` (one `update` audit row per changed field, same transaction); regression tests `test_amend_writes_audit_row_per_changed_field`, `test_original_value_preserved_in_history_view` (TS-006) |
| 2 | Blocking | No reason for change on API or form | SOP-DI-004 §4.2, §5.1 | Fixed in `08b7269` (mandatory reason, GMP min 10 chars, rollback on `ReasonRequired`); regression tests `test_amend_requires_reason`, `test_amend_form_has_reason_and_is_hidden_on_deleted` (TS-005), `test_amend_and_verify_rejected_without_reason_leave_record_unchanged` (TS-006) |
| 3 | Blocking | Float `round()` instead of `evaluate()`: 0.155 vs NMT 0.15 → 0.15 pass (SOP 0.16, OOS); 105.05 vs 95.0–105.0 → 105.0 pass (SOP 105.1, OOS) | SOP-QC-021 §4–§5 | Fixed in `08b7269` (`sst.rounding.evaluate()` with regime rounding/limit settings); regression test `test_amend_uses_sop_half_up_rounding_at_limit` (TS-005) |
| 4 | Blocking | No provisioning or role check; actor not attributed | SOP-DI-004 §5.1, §3 | Fixed in `08b7269` (provisioned user and amend role required, 403 otherwise; actor recorded in audit row); regression test `test_amend_rejects_unprovisioned_and_unauthorised_roles` (TS-005) |
| 5 | Blocking | OOS-changing amendment without second-person verification | SOP-DI-004 §5.3 | Fixed in `08b7269` (status `Amended - pending verification`; `_verify()` by a different QC Supervisor); regression tests `test_oos_change_requires_second_person_verification`, `test_verifier_must_differ_and_be_supervisor` (TS-005), `test_verify_writes_audit_row` (TS-006) |
| 6 | Blocking | No server-side validation on form (`1e3` stored, `abc` → 500) | FS-008 | Fixed in `08b7269` (decimal pattern enforced server-side, 422); regression test `test_amend_form_validates_decimal_server_side` (TS-005) |
| 7 | Blocking | No evidence package | SOP-CSV-010 §6, §7, §8 | Evidence package drafted (§3); ER-CHG-4127 records CI job 124646264910 on `43da149`. Closure requires the §5 human approvals |
| 8 | Advisory | Amend form shown on deleted results; no-op amendments accepted | SOP-DI-004 §4.3, §3 | Fixed in `08b7269` (no form on deleted results; 404 on deleted, 422 on unchanged value); regression tests `test_amend_rejects_deleted_and_unchanged`, `test_amend_form_has_reason_and_is_hidden_on_deleted` (TS-005) |
| 9 | Advisory | `gmp.yaml` `e_signature.required_for: [amendment_verification]` but SST has no e-signature; verification is attributable (SSO user + audit row) but not e-signed | SOP-CSV-010 §5; 21 CFR 11.50/11.70 (referenced) | **Open — human decision.** Out of scope for CHG-4127; separate CR for QA decision |
| 10 | Advisory | Version still 3.4.1 vs target 3.5.0 | SOP-CSV-010 §4.8 | **Open — human decision.** Version bump, VSR update and release note belong to the release CC |
| 11 | Advisory | Same change as PR #3, merged then reverted in PR #4 for incomplete CC package | SOP-CSV-010 §4.5, §8 | Addressed in §1 of this record (history stated) |

## 4. Implementation
- PR: [#5](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/5) `feature/chg-4127-amend-results-r2` → `main`.
- Original commit: `a90e6092fe39b222b2f463271a7ac7e0045b4cf1` — CHG-4127: allow analysts to amend assay results (findings 1–8 raised against it).
- Fix commit: `08b7269e58e7ccd3432fdf91c4e0082676eddada` — audited, reasoned, role-checked amendment with SOP rounding and second-person verification.
- Evidence commits: `78d3aab` (URS/FS delta), `4985ffe` (RA), `e799753` (TS-005 + tests), `b1787e4` (RTM), `39297bc` (TS-006 + tests), `43da149` (this record), then the ER-CHG-4127/traceability commit (documents only). CI runs for every commit are on PR #5.
- Second review: Devin Review on PR #5.
- Technical review, system owner and QA review: see §5 (humans only).

## 4a. Traceability chain
CHG-4127 ([issue #2](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/issues/2))
→ [PR #5](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/5)
→ `a90e609` (original) → `08b7269` (fix) → evidence commits `78d3aab` (URS/FS), `4985ffe` (RA), `e799753` (TS-005), `b1787e4` (RTM), `39297bc` (TS-006), `43da149` (CC), followed by the ER/traceability commit
→ TS-005 (`tests/test_amend.py`): `test_amend_requires_reason`, `test_amend_uses_sop_half_up_rounding_at_limit`, `test_amend_rejects_unprovisioned_and_unauthorised_roles`, `test_oos_change_requires_second_person_verification`, `test_verifier_must_differ_and_be_supervisor`, `test_amend_form_validates_decimal_server_side`, `test_amend_rejects_deleted_and_unchanged`, `test_amend_form_has_reason_and_is_hidden_on_deleted`
→ TS-006 (`tests/test_amend_audit.py`): `test_amend_writes_audit_row_per_changed_field`, `test_verify_writes_audit_row`, `test_amend_and_verify_rejected_without_reason_leave_record_unchanged`, `test_audit_entries_not_modifiable_via_api_after_amend`, `test_original_value_preserved_in_history_view`
→ ER-CHG-4127 CI run ([run 41238179614 / job 124646264910](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41238179614/job/124646264910) on `43da149` (last code/test commit): success, 62 passed, coverage 93.57%)
→ coordinating Devin session https://devin-gtm.devinenterprise.com/sessions/668c5454cc7b490a94054cdc68dfe220

## 5. Approvals (humans only; e-signature in QMS)
| Role | Name | Decision | Date |
|---|---|---|---|
| Technical reviewer | | | |
| System owner | | | |
| QA | | | |

Drafted by Devin; approval and merge are reserved for the named human approvers per SOP-CSV-010 §4.7.
