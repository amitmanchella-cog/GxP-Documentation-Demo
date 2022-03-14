from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG_DIR = Path(os.environ.get("SST_CONFIG_DIR", Path(__file__).resolve().parent.parent / "config"))


@dataclass(frozen=True)
class RecordControls:
    audit_trail_on: tuple[str, ...]
    reason_required_on: tuple[str, ...]
    reason_min_length: int
    deletion: str
    second_person_verification_on_oos_change: bool


@dataclass(frozen=True)
class ResultRules:
    rounding: str
    compare_on: str
    limit_inclusive: bool


@dataclass(frozen=True)
class Regime:
    code: str
    label: str
    records: RecordControls
    results: ResultRules
    retention: dict = field(default_factory=dict)
    e_signature: dict = field(default_factory=dict)

    def requires_audit(self, action: str) -> bool:
        return action in self.records.audit_trail_on

    def requires_reason(self, action: str) -> bool:
        return action in self.records.reason_required_on


def load_app_config() -> dict:
    with open(CONFIG_DIR / "app.yaml") as fh:
        return yaml.safe_load(fh)


def load_regime(code: str | None = None) -> Regime:
    code = (code or os.environ.get("SST_REGIME") or load_app_config()["active_regime"]).lower()
    with open(CONFIG_DIR / "regimes" / f"{code}.yaml") as fh:
        raw = yaml.safe_load(fh)
    rc = raw["record_controls"]
    rr = raw["results"]
    return Regime(
        code=raw["regime"],
        label=raw["label"],
        records=RecordControls(
            audit_trail_on=tuple(rc["audit_trail_on"]),
            reason_required_on=tuple(rc["reason_required_on"]),
            reason_min_length=int(rc["reason_min_length"]),
            deletion=rc["deletion"],
            second_person_verification_on_oos_change=bool(rc["second_person_verification_on_oos_change"]),
        ),
        results=ResultRules(
            rounding=rr["rounding"],
            compare_on=rr["compare_on"],
            limit_inclusive=bool(rr["limit_inclusive"]),
        ),
        retention=raw.get("retention", {}),
        e_signature=raw.get("e_signature", {}),
    )


def available_regimes() -> list[str]:
    return sorted(p.stem for p in (CONFIG_DIR / "regimes").glob("*.yaml"))
