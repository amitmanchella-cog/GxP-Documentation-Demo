# URS-SST — User Requirements Specification, Stability Sample Tracker
**Revision:** 3.4 · **Status:** Approved · **Effective:** 2025-05-19
**Author:** T. Brennan (Stability Coordinator) · **Reviewed:** A. Diallo (QC Supervisor), 2025-05-12 · **Approved:** H. Lindqvist (QA Director), 2025-05-16

| ID | Requirement | GxP impact | Source |
|---|---|---|---|
| URS-001 | The system shall apply record controls (audit-trail events, reason-for-change rule, deletion mode, rounding mode, retention) from the active regime configuration file; regime behaviour shall not be hard-coded. | High | SOP-CSV-010 §5; shared platform decision CC-2025-009 |
| URS-002 | Every create, modify or delete of an assay result shall write an audit-trail entry with user ID, UTC timestamp, record ID, field, old value, new value and reason. | High | SOP-DI-004 §4.1; 21 CFR 11.10(e) |
| URS-003 | Modification or deletion of an assay result shall be rejected unless a reason for change of at least the configured minimum length is supplied; deletion shall be a soft delete that preserves the record. | High | SOP-DI-004 §4.2–4.3 |
| URS-004 | The system shall compute the reportable value by rounding the measured value once, to the precision of the specification limit, with exact decimal arithmetic and the regime's rounding mode (half-up for GMP), and shall set the OOS flag by comparing the reportable value with the limit. Users shall not be able to set or clear the OOS flag. | High | SOP-QC-021 §4–5 |
| URS-005 | Users shall be able to list studies, list and filter samples by study and status, and view a sample with its results, specification, OOS status, analyst, instrument and test time. | Medium | QC stability workflow |
| URS-006 | The result page shall show the full record history (audit trail) for that result; a system-wide audit-trail view shall be available. | High | SOP-DI-004 §4.6 |
| URS-007 | Every action shall be attributed to the authenticated user supplied by the site SSO proxy. | High | SOP-DI-004 §3 (Attributable) |
| URS-008 | A JSON API shall allow result creation, retrieval, soft deletion and audit retrieval for integration with the chromatography data system. | High | Interface spec IF-CDS-02 |
| URS-009 | Timestamps shall be system-generated in UTC and not user-editable. | High | SOP-DI-004 §3 (Contemporaneous) |

Change history: r3.0 (2022-03) initial re-platform; r3.3 (2024-06) URS-004 rewritten for exact decimal rounding; r3.4 (2025-05) URS-001 added for regime configuration.
