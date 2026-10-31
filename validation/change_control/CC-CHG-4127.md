# CC-CHG-4127 — Result amendment with reason, audit trail and OOS second-person verification
**System:** SST 3.4.1 → 3.5.0 (GMP regime, `config/regimes/gmp.yaml`) · **Status:** Draft · **Raised:** <date — Change Owner fills> · **Requested by:** T. Brennan (per CR #2) · **Change Owner:** P. Natarajan (per CR #2) · **QA:** <to be assigned>

> Draft prepared with Devin drafting assistance (SOP-CSV-010 §4.7). QA assigns the CC number in the QMS. Approvals, signatures and dates are entered by the named humans only; none have been entered here. Final CI run URL and SHA are recorded in section 5 and ER-CHG-4127.

## 1. Description and reason
**Change request:** CHG-4127 ([issue #2](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/issues/2)) · **PR:** [#6](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/6) `feature/chg-4127-amend-results-r3` → `main` · **Target release:** 3.5.0

**Business reason (from CR):** When a transcription error is found after a result has been entered, analysts currently have to soft-delete the result and enter a new one. This splits the record across two IDs and makes trend reports harder to read. QC asks for an amendment function so the measured value can be corrected in place on the existing result.

**What changes (as implemented at `805496c`):**
- New **Amend** action on `/results/{id}` (`POST /results/{id}/amend`) and `PATCH /api/results/{id}` for the CDS interface.
- Mandatory reason for change, at least `reason_min_length` (10 under GMP), on both the API and the form.
- Reportable value and OOS flag recomputed through `sst.rounding.evaluate` with the regime's `rounding` (`half_up`) and `limit_inclusive` settings.
- One audit-trail row per changed field (user, UTC timestamp, old/new value, reason), written in the same transaction as the result update.
- Only provisioned users with role QC Analyst, Senior QC Analyst or QC Supervisor may amend (`AMEND_ROLES`).
- If an amendment changes the OOS conclusion, the result goes to status `Pending verification`. A QC Supervisor who is not the amending user must verify it (`POST /results/{id}/verify`, `POST /api/results/{id}/verify`) before it becomes `Amended`. This follows `second_person_verification_on_oos_change: true`.
- Server-side validation of `measured_value` (HTTP 422 on non-decimal input). Amendments that do not change the value are rejected.
- Schema unchanged (v7). No data migration.

## 2. GxP impact assessment
Reproduced from the PR #6 comment "GxP impact & risk assessment — CHG-4127", which assessed original head `d4a226e`. QA must confirm this conclusion.

### 2.1 What the change touches (SOP-CSV-010 §4.2)
| Area | Touched? | Basis |
|---|---|---|
| Creates / modifies / deletes GxP records | **Yes (modifies)** | Updates `measured_value`, `reportable_value`, `oos`, `status` on `assay_results` |
| Calculation, rounding or specification comparison that sets a reportable result / OOS status | **Yes** | Recomputes the reportable value and OOS flag. At `d4a226e` this used a separate float implementation; at `805496c` it uses `sst.rounding.evaluate` |
| Audit trail / e-signature / access control | **Yes** | New mutation path. Audit rows, role checks and second-person verification were added at `805496c`. The regime lists `amendment_verification` as an e-signature point (see F11) |
| Data migration | No | Schema unchanged (v7) |
| Display of GxP data | Yes | `result.html` amend/verify forms. Statuses `Amended` and `Pending verification` shown |

**Affected functions:** The CR names only FS-005/006/008. The change also affects **FS-002** (audit trail), **FS-003** (reason for change), **FS-004** (rounding & OOS) and **FS-007** (attribution), and adds FS-009 (amend) and FS-010 (verify). See F10.

### 2.2 Classification (SOP-CSV-010 §5)
**GxP impact: Yes** (product quality through OOS disposition, and data integrity). **Risk level: High.**

Justification: the change meets three High criteria, and any one is enough:
1. It modifies GxP records (assay results).
2. It recomputes the reportable value and OOS status. An amendment that recomputes OOS status is High however small the diff is.
3. It adds a write path that touches the audit trail and access control.

`RA-SST` r3.4 already rates FS-002, FS-003 and FS-004 High, so any change to those functions is High. The High evidence package in SOP-CSV-010 §6/§7 is required (section 4).

## 3. Review findings and disposition
Source: PR #6 review "GxP findings — CHG-4127 (PR #6 @ `d4a226e`)": 9 blocking, 3 advisory. Each finding was reproduced against `d4a226e`. Code fixes are in commit `805496c`, with regression tests in `tests/test_amend.py` (TS-005) and `tests/test_amend_audit.py` (TS-006). Closure of each finding depends on QA review of the executed results in ER-CHG-4127.

| # | Class | SOP / requirement | Finding (at `d4a226e`) | Disposition | Verification |
|---|---|---|---|---|---|
| F1 | Blocking | SOP-DI-004 §4.1, §4.5; URS-002; 21 CFR 11.10(e) | `_amend` wrote no `audit.record()` row | **Fixed in `805496c`**: one audit row per changed field, same transaction | TS-005, TS-006 |
| F2 | Blocking | SOP-DI-004 §4.2, §5.1; URS-003 | No reason for change captured | **Fixed in `805496c`**: mandatory `reason`, regime minimum length enforced on API (422) and form | TS-005, TS-006 |
| F3 | Blocking | SOP-DI-004 §3 (Original), §5.2 | Original values overwritten and not kept | **Fixed in `805496c`**: old/new values for each field kept in the audit trail | TS-006 |
| F4 | Blocking | SOP-QC-021 §4.2–§4.3; URS-004; FS-004 | Binary-float banker's rounding (0.155 → 0.15, 0.145 → 0.14). Regime mode ignored | **Fixed in `805496c`**: uses `sst.rounding.evaluate` with regime `rounding` | TS-005 boundary cases |
| F5 | Blocking | SOP-QC-021 §5.1–§5.2; URS-004 | Float spec comparison, wrong precision source, `limit_inclusive` ignored. An OOS result was cleared | **Fixed in `805496c`**: uses `sst.rounding.evaluate` with regime `limit_inclusive` | TS-005 boundary cases |
| F6 | Blocking | SOP-DI-004 §3 (Attributable), §5.1; URS-007 | Amendment not attributed. Unprovisioned user could amend | **Fixed in `805496c`**: `current_user()` attribution, provisioning check, `AMEND_ROLES` (403 otherwise) | TS-005, TS-006 |
| F7 | Blocking | SOP-DI-004 §5.3; SOP-QC-021 §6.2; `gmp.yaml` | No second-person verification when the OOS conclusion changes | **Fixed in `805496c`**: `Pending verification` status. A different QC Supervisor must verify, and the verification is audited with a reason | TS-005, TS-006 |
| F8 | Blocking | SOP-CSV-010 §4.6, §6–§8; SOP-DI-004 §6 | No validation deliverables and no automated tests for the new routes | **Being addressed by the evidence package** (section 4). Regression tests were added in `805496c` (`tests/test_amend.py`). The rest of the package is being produced in parallel. Remains open until every row in section 4 is present and reviewed | Section 4 checklist |
| F9 | Blocking | SOP-QC-021 §6.1; FS-008 | Form route returned HTTP 500 on non-decimal `measured_value` | **Fixed in `805496c`**: server-side decimal validation (422) | TS-005 negative cases |
| F10 | Advisory | SOP-CSV-010 §4.2 | CR #2 "Affected functions" lists only FS-005/006/008 | **For QA decision**: Change Owner and QA to correct the CR impact section to add FS-002/003/004/007 (and new FS-009/010). Not a code change | — |
| F11 | Advisory | `gmp.yaml` `e_signature.required_for: [amendment_verification]`; 21 CFR 11.50/11.200 | SST has no e-signature capability. Verification is an attributed, reason-bearing audit entry, which is **not** an e-signature | **For QA decision**: either the e-signature for amendment verification is applied in the QMS, or a follow-up CR adds e-signature to SST. Record the decision here before approval | — |
| F12 | Advisory | SOP-DI-004 §4.1 | Amendments that do not change the value would set a misleading `Amended` status | **Fixed in `805496c`**: rejected with 422 | TS-005 |
| F13 | Blocking (found by the evidence workstream) | SOP-DI-004 §4.1, §6 | A storage failure after the audit insert left orphan audit rows that the next request committed | **Fixed in `7e96a8b`**: `get_conn()` rolls back on any exception | TS-006 |
| F14 | Blocking (found by the evidence workstream, G1) | SOP-DI-004 §5.3 | A second amendment made while the result was pending verification cleared the verification requirement | **Fixed in `f75d60c`** | TS-005 |
| F15 | Advisory (found by the evidence workstream, G2) | SOP-DI-004 §3 Attributable | With no identity, requests were attributed by default to `mfarouk` | **Partly fixed in `f75d60c`**: amend/verify return 401. The fallback for create/delete is unchanged; QA/Change Owner to decide on a follow-up CR | TS-005 |

## 4. Evidence package (SOP-CSV-010 §6, High)
Status column: "Assembled" means the artefact is on the PR branch in Draft. Human review and approval are still required.

| Deliverable | Reference | Status |
|---|---|---|
| GxP impact assessment | Section 2 of this record; PR #6 comment "GxP impact & risk assessment — CHG-4127" | Drafted |
| URS delta | `validation/deltas/URS-FS-delta-CHG-4127.md`. New URS-010 (result amendment), URS-011 (second-person verification of an OOS-conclusion change). Changed URS-002, URS-003, URS-006, URS-007, URS-008 | Assembled on PR #6 (Draft; awaiting human review) |
| FS delta | `validation/deltas/URS-FS-delta-CHG-4127.md`. New FS-009 (amend), FS-010 (verify). Changed FS-002, FS-003, FS-004, FS-006, FS-007, FS-008 | Assembled on PR #6 (Draft; awaiting human review) |
| Risk assessment | `validation/RA-SST-CHG-4127.md` (change RA); `validation/RA-SST.md` (updated function rows) | Assembled on PR #6 (Draft; awaiting human review) |
| Test scripts | `validation/test_scripts/TS-005.md` (amendment, rounding/OOS boundaries, negative cases, second-person verification; automated in `tests/test_amend.py`); `validation/test_scripts/TS-006.md` (audit-trail verification; automated in `tests/test_amend_audit.py`) | Assembled on PR #6 (Draft; awaiting human review) |
| Executed results (CI job, commit SHA, pass/fail) | `validation/executed_results/ER-CHG-4127.md`. CI run: https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41239870984 (job 124651363065, SHA `600fd97`) · SHA: `600fd97` · Result: from CI `test-evidence` artefact (`reports/`) | Assembled on PR #6 (Draft; awaiting human review) |
| RTM | `validation/RTM.md` rev 3.5: rows for URS-010/011 added, changed rows updated, coverage line | Assembled on PR #6 (Draft; awaiting human review) |
| Audit-trail verification (SOP-DI-004 §6) | `validation/test_scripts/TS-006.md` / `tests/test_amend_audit.py` | Assembled on PR #6 (Draft; awaiting human review) |
| Change-control record | `validation/change_control/CC-CHG-4127.md` (this document) | Draft |
| Periodic review impact note | Section 6 of this record | Drafted |

## 5. Implementation and traceability
**PR:** [#6](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/6) · **Branch:** `feature/chg-4127-amend-results-r3`

| Commit | Description |
|---|---|
| `d4a226e` | CHG-4127: allow analysts to amend assay results (original head; findings F1–F12 raised against this) |
| `805496c` | CHG-4127: audited, reasoned, exact-decimal result amendment with OOS second-person verification (fixes F1–F7, F9, F12; adds `tests/test_amend.py`) |
| `9e61826`, `aea14e1`, `8ed8b86`, `0812fe3`, `f666648`, `3508826` | Evidence workstreams (TS-006 + tests, URS/FS deltas, CC draft, RTM, RA, TS-005 + boundary tests), merged on the PR branch |
| `7e96a8b` | Rolls back the request transaction on any failure (fixes F13, which was found by the TS-006 audit-trail verification) |
| `f75d60c` | Keeps a re-amended result in pending verification (F14, found by RA/TS-005 as G1); requires an explicit identity to amend or verify (F15, G2) |
| `600fd97` | Final head, executed in CI (see ER-CHG-4127) |

**Traceability chain:**
CHG-4127 ([issue #2](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/issues/2)) → PR [#6](https://github.com/amitmanchella-cog/GxP-Documentation-Demo/pull/6) → commits `d4a226e`, `805496c`, `600fd97` → TS-005 (`tests/test_amend.py`) / TS-006 (`tests/test_amend_audit.py`) → CI run https://github.com/amitmanchella-cog/GxP-Documentation-Demo/actions/runs/41239870984 (job 124651363065, SHA `600fd97`) → `validation/executed_results/ER-CHG-4127.md` → URS-010/011, FS-009/010 and changed URS/FS rows (`validation/deltas/URS-FS-delta-CHG-4127.md`, `validation/RTM.md` rev 3.5) → Devin sessions: [evidence workstream](https://devin-gtm.devinenterprise.com/sessions/968d18d35b254ea79fd50bf0becb2488), [author's originating session](https://devin-gtm.devinenterprise.com/sessions/1e103ae6045b46c8bc2aadaf3ea21c53)

**Reviewers:** AI-assisted review (Devin) recorded on PR #6. Independent human technical review is pending (section 8).

## 6. Periodic review impact
**Impact: Yes.** The change adds GxP-relevant functions (result amendment, second-person verification of OOS-conclusion changes) and two new result statuses (`Amended`, `Pending verification`). The next SST periodic review should:
- include amended results and their audit-trail entries in its audit-trail review sample (SOP-DI-004);
- check that no result stays in `Pending verification` for longer than expected, and that verifiers were always different from amenders;
- confirm the F11 e-signature decision has been carried out (QMS procedure or follow-up CR);
- refer to the VSR for 3.5.0 in place of `VSR-SST-3.4.md` as the current validation baseline once it is issued.

## 7. Residual risks and open items
| # | Item | Owner | Status |
|---|---|---|---|
| O1 | F11: no e-signature in SST for `amendment_verification`. QA to decide between a QMS e-signature and a follow-up CR | QA | Open |
| O2 | F10: CR #2 affected-functions section to be corrected | Change Owner / QA | Open |
| O3 | F8: evidence package rows in section 4 assembled on PR #6; human review of the package | Change Owner | Open (assembled; awaiting review) |
| O4 | Executed results: CI run 41239870984 and SHA `600fd97` recorded in ER-CHG-4127 and this record | Parent session | Closed (recorded) |
| O5 | Independent human technical review of `805496c` and the evidence package (findings were raised and fixes drafted with AI assistance) | Independent technical reviewer | Open |
| O6 | Residual risk: amendment relies on SSO proxy `X-User` attribution (FS-007). Unchanged control, same as the existing create/delete paths | — | Accepted per RA-SST r3.4 (to be reconfirmed in RA-SST-CHG-4127) |
| O7 | VSR for release 3.5.0 to be raised | Change Owner / CSV | Open |

## 8. Independent second review
| Item | Entry |
|---|---|
| Reviewer (independent of author and fixer) | |
| Scope reviewed (commits, evidence documents) | |
| Findings / comments | |
| Outcome | |
| Date | |

## 9. Approvals (humans only; e-signature in QMS)
| Role | Name | Decision | Date |
|---|---|---|---|
| Change Owner | | | |
| Independent technical reviewer | | | |
| QA | | | |

Release and closure: not released. Not approved.
