from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from .regimes import load_app_config

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS users(
  user_id TEXT PRIMARY KEY, full_name TEXT NOT NULL, role TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS studies(
  study_id TEXT PRIMARY KEY, product TEXT NOT NULL, strength TEXT NOT NULL, protocol TEXT NOT NULL,
  start_date TEXT NOT NULL, status TEXT NOT NULL, owner TEXT NOT NULL REFERENCES users(user_id));
CREATE TABLE IF NOT EXISTS batches(
  batch_id TEXT PRIMARY KEY, study_id TEXT NOT NULL REFERENCES studies(study_id),
  mfg_date TEXT NOT NULL, site TEXT NOT NULL, pack TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS storage_conditions(
  cond_id TEXT PRIMARY KEY, label TEXT NOT NULL, temp_c REAL NOT NULL, rh_pct REAL);
CREATE TABLE IF NOT EXISTS specifications(
  spec_id TEXT PRIMARY KEY, study_id TEXT NOT NULL REFERENCES studies(study_id),
  test_name TEXT NOT NULL, method TEXT NOT NULL, unit TEXT NOT NULL,
  lower_limit TEXT, upper_limit TEXT, limit_text TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS samples(
  sample_id TEXT PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batches(batch_id),
  cond_id TEXT NOT NULL REFERENCES storage_conditions(cond_id),
  timepoint_months INTEGER NOT NULL, pull_date TEXT NOT NULL, due_date TEXT NOT NULL,
  status TEXT NOT NULL, assigned_to TEXT REFERENCES users(user_id), location TEXT);
CREATE TABLE IF NOT EXISTS assay_results(
  result_id INTEGER PRIMARY KEY AUTOINCREMENT,
  sample_id TEXT NOT NULL REFERENCES samples(sample_id),
  spec_id TEXT NOT NULL REFERENCES specifications(spec_id),
  measured_value TEXT NOT NULL, reportable_value TEXT NOT NULL, oos INTEGER NOT NULL,
  analyst TEXT NOT NULL REFERENCES users(user_id), instrument TEXT, tested_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Entered', deleted INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS audit_trail(
  audit_id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, actor TEXT NOT NULL,
  entity TEXT NOT NULL, entity_id TEXT NOT NULL, action TEXT NOT NULL,
  field TEXT, old_value TEXT, new_value TEXT, reason TEXT);
CREATE INDEX IF NOT EXISTS ix_audit_entity ON audit_trail(entity, entity_id);
CREATE INDEX IF NOT EXISTS ix_results_sample ON assay_results(sample_id);
"""

SCHEMA_VERSION = 7


def db_path() -> Path:
    p = os.environ.get("SST_DATABASE") or load_app_config()["database"]
    return Path(p)


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(path) if path else db_path()
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    cur = conn.execute("SELECT MAX(version) FROM schema_version")
    if (cur.fetchone()[0] or 0) < SCHEMA_VERSION:
        conn.execute(
            "INSERT INTO schema_version(version, applied_at) VALUES (?, datetime('now'))",
            (SCHEMA_VERSION,),
        )
    conn.commit()
