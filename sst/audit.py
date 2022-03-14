"""Audit trail writer (SOP-DI-004 s4). Every GxP record mutation goes through `record`."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from .regimes import Regime


class ReasonRequired(ValueError):
    pass


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def record(
    conn: sqlite3.Connection,
    regime: Regime,
    *,
    actor: str,
    entity: str,
    entity_id: str,
    action: str,
    field: str | None = None,
    old_value=None,
    new_value=None,
    reason: str | None = None,
    at: str | None = None,
) -> int:
    if not regime.requires_audit(action):
        return 0
    reason = (reason or "").strip()
    if regime.requires_reason(action) and len(reason) < regime.records.reason_min_length:
        raise ReasonRequired(
            f"reason for change is required for {action} (min {regime.records.reason_min_length} characters)"
        )
    cur = conn.execute(
        "INSERT INTO audit_trail(ts, actor, entity, entity_id, action, field, old_value, new_value, reason)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (
            at or utcnow(),
            actor,
            entity,
            str(entity_id),
            action,
            field,
            None if old_value is None else str(old_value),
            None if new_value is None else str(new_value),
            reason or None,
        ),
    )
    return int(cur.lastrowid)
