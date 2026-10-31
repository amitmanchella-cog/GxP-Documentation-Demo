# RA-SST — Risk Assessment, Stability Sample Tracker
**Revision:** 3.4 · **Status:** Approved · **Effective:** 2025-05-19 · **Method:** SOP-CSV-010 §5 (GxP impact → High/Medium/Low) with FMEA-style severity/probability/detectability on functions.
**Author:** K. Oyelaran (CSV Lead) · **Reviewed:** A. Diallo (QC Supervisor), 2025-05-12 · **Approved:** H. Lindqvist (QA Director), 2025-05-16

| Function | Failure mode | Effect | Sev | Prob | Det | Risk | Controls / required testing |
|---|---|---|---|---|---|---|---|
| FS-004 rounding & OOS | Reportable value rounded incorrectly at the limit (e.g. binary float, wrong mode) | OOS result reported as passing; product disposition on wrong data | 5 | 2 | 2 | **High** | Exact decimal arithmetic; mode from regime; scripted boundary tests at and either side of each limit (TS-003); any change to this function is High under SOP-CSV-010 |
| FS-002 audit trail | Mutation path does not write audit row | Change to GxP record not attributable/reconstructable | 5 | 2 | 3 | **High** | Single writer `audit.record()`; every write path tested for an audit row (TS-002); code review checklist item |
| FS-003 reason for change | Modify/delete accepted without reason | Loss of "why"; SOP-DI-004 §4.2 breach | 4 | 2 | 2 | **High** | Regime-driven `ReasonRequired`; negative tests (TS-002) |
| FS-001 regime config | Wrong regime loaded or hard-coded behaviour | Controls not matching the governing regulation | 4 | 1 | 2 | **High** | Config page shows active regime; TS-001 loads all regimes |
| FS-007 attribution | Header missing → fallback user | Mis-attribution | 4 | 1 | 2 | **High** | Proxy enforces header in production; fallback only when `SST_USER` set; TS-002 asserts actor |
| FS-005 views | Wrong counts/filters | Review inefficiency; no record change | 2 | 2 | 1 | Medium | TS-004 render + content tests |
| FS-006 history view | Trail not shown | Review gap, data intact | 3 | 1 | 1 | Medium | TS-004 |
| FS-008 API | Invalid payload accepted | Bad record created | 3 | 2 | 2 | **High** | Pydantic validation; TS-002 |

Overall system classification: **GxP, High** (creates and modifies QC records used for disposition). Testing approach: scripted automated tests executed in CI for all High functions; results retained with the release.
