# Stability Sample Tracker (SST)

QC stability sample and assay-result tracking for Veltrix Pharmaceuticals, Site 02. System ID `SST`, GxP (GMP) regime.

**Validation status:** see `validation/VSR-SST-3.4.md`. Changes follow SOP-CSV-010; records follow SOP-DI-004; result reporting follows SOP-QC-021.

## Run

```bash
pip install -e ".[dev]"
python -m sst.seed            # one-off: populates data/sst.sqlite3 with the site dataset
uvicorn sst.main:app --port 8000
```

Open http://localhost:8000. Identity comes from the SSO reverse proxy (`X-User` header); set `SST_USER` for local use.

## Configuration

`config/app.yaml` selects the active regime (`gmp`). Regime rules live in `config/regimes/*.yaml` (audit trail, reason-for-change, rounding mode, retention, e-signature points). Code must read these; do not hard-code regime behaviour.

## Test

```bash
ruff check . && ruff format --check . && pytest
```

CI runs the same on every PR and publishes `reports/` (junit, coverage, console log) as the executed-test evidence referenced from `validation/`.

## Layout

| Path | Purpose |
|---|---|
| `sst/` | application (FastAPI + SQLite) |
| `sst/rounding.py` | reportable value rounding and specification comparison |
| `sst/audit.py` | audit-trail writer used by every record mutation |
| `config/` | runtime and regime configuration |
| `validation/` | URS, FS, risk assessment, test scripts, executed results, RTM, change control |
| `tests/` | automated test scripts (`TS-nnn`) |
