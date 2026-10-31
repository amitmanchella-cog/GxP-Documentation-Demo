# FS-SST — Functional Specification, Stability Sample Tracker
**Revision:** 3.4 · **Status:** Approved · **Effective:** 2025-05-19
**Author:** P. Natarajan (Software Engineer) · **Reviewed:** K. Oyelaran (CSV Lead), 2025-05-13 · **Approved:** H. Lindqvist (QA Director), 2025-05-16

| ID | Function | Implements | Design |
|---|---|---|---|
| FS-001 | `sst.regimes.load_regime()` reads `config/app.yaml` → `active_regime` and `config/regimes/<code>.yaml` into an immutable `Regime` object; `Regime.requires_audit(action)` / `requires_reason(action)` are the only decision points for record controls. | URS-001 | `sst/regimes.py` |
| FS-002 | `sst.audit.record()` inserts one `audit_trail` row (ts, actor, entity, entity_id, action, field, old_value, new_value, reason) for each mutation; timestamps via `utcnow()` (UTC, ms, `Z`). All write paths in `sst/main.py` call it inside the same transaction. | URS-002, URS-009 | `sst/audit.py` |
| FS-003 | `record()` raises `ReasonRequired` when `requires_reason(action)` and `len(reason) < reason_min_length`; the API maps it to HTTP 422 and rolls back. `DELETE /api/results/{id}` sets `deleted=1, status='Deleted'`; deleted rows are excluded from views and return 404. | URS-003 | `sst/audit.py`, `sst/main.py::api_delete_result` |
| FS-004 | `sst.rounding.evaluate(measured, lower, upper, mode)` → `(reportable, oos)`. `decimal_places()` derives precision from the limit text; `reportable_value()` uses `Decimal(str(x)).quantize()` with `ROUND_HALF_UP` (or `ROUND_HALF_EVEN` for regimes that configure it); `is_oos()` compares inclusively. Stored columns: `measured_value`, `reportable_value`, `oos`. | URS-004 | `sst/rounding.py` |
| FS-005 | HTML views `/`, `/samples`, `/samples/{id}` (Jinja2 templates) with per-row OOS highlighting and result counts. | URS-005 | `sst/main.py`, `sst/templates/` |
| FS-006 | `/results/{id}` shows the result and its `audit_trail` rows; `/audit` lists the latest N entries; `/api/results/{id}/audit` returns them as JSON. No update or delete route exists for `audit_trail`. | URS-006 | `sst/main.py` |
| FS-007 | `current_user()` reads `X-User` set by the SSO proxy (fallback `SST_USER` for local dev); it is stored as `analyst` on results and `actor` on audit rows. | URS-007 | `sst/main.py` |
| FS-008 | `POST /api/results` (201) validates `measured_value` as a decimal string, computes FS-004, writes the result and the `create` audit row; `GET /api/results/{id}`; `DELETE /api/results/{id}` (FS-003). | URS-008 | `sst/main.py` |

Data model: `studies`, `batches`, `storage_conditions`, `specifications` (limits stored as text to preserve precision), `samples`, `assay_results`, `audit_trail`, `users` — see `sst/db.py` (schema version 7).
