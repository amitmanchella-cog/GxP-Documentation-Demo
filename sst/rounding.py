"""Reportable-value rounding and specification comparison (SOP-QC-021 s4-s5)."""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

_MODES = {"half_up": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN}


def decimal_places(limit_text: str) -> int:
    """Number of decimal places in a limit such as '0.15' or '90.0'."""
    s = limit_text.strip()
    return len(s.split(".")[1]) if "." in s else 0


def reportable_value(measured: float | str | Decimal, places: int, mode: str = "half_up") -> Decimal:
    """Round a measured value once, at the precision of the limit, using exact decimal arithmetic.

    The measured value is converted through ``str`` so that 0.155 is treated as the analyst
    entered it, not as its binary float expansion.
    """
    if mode not in _MODES:
        raise ValueError(f"unsupported rounding mode {mode!r}")
    q = Decimal(1).scaleb(-places)
    return Decimal(str(measured)).quantize(q, rounding=_MODES[mode])


def is_oos(reportable: Decimal, lower: str | None, upper: str | None, inclusive: bool = True) -> bool:
    lo = Decimal(lower) if lower not in (None, "") else None
    hi = Decimal(upper) if upper not in (None, "") else None
    if lo is not None and (reportable < lo if inclusive else reportable <= lo):
        return True
    if hi is not None and (reportable > hi if inclusive else reportable >= hi):
        return True
    return False


def evaluate(measured, lower: str | None, upper: str | None, mode: str = "half_up", inclusive: bool = True):
    """Return (reportable_value, oos_flag) for a measured value against a specification."""
    places = max(decimal_places(lower or "0"), decimal_places(upper or "0"))
    rv = reportable_value(measured, places, mode)
    return rv, is_oos(rv, lower, upper, inclusive)
