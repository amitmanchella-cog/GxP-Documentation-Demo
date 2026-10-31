# Changelog

## 3.4.1 — 2025-09-02 (CC-2025-018)
- Audit-trail view: default page size 200, link entity IDs to records.
- Dependency refresh (FastAPI 0.115 line); no functional change. Regression run attached to CC-2025-018.

## 3.4.0 — 2025-05-19 (CC-2025-009)
- Regime configuration externalised to `config/regimes/*.yaml`; GLP, GCP and SOX profiles added for the shared platform.
- Config page shows the active regime and its record controls.

## 3.3.2 — 2024-11-27 (CC-2024-031)
- Result deletion changed to soft delete with mandatory reason (SOP-DI-004 r4.2 alignment).
- Added `TS-002` negative test: delete without reason is rejected.

## 3.3.0 — 2024-06-10 (CC-2024-014)
- Reportable value rounding moved to `sst/rounding.py` using exact decimal arithmetic (SOP-QC-021 r7.1).
- Added boundary tests at and either side of each limit type.

## 3.2.0 — 2023-10-02 (CC-2023-022)
- Sample list filters (study, status); sample detail page with result history.

## 3.0.0 — 2022-03-14 (CC-2022-005)
- Re-platform from the Access front end to FastAPI + SQLite. Data migrated under MP-SST-001.

## 2.x — 2019–2021
- Legacy releases; records retained in the QMS.
