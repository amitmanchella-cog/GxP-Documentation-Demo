"""TS-003 Reportable value rounding and specification comparison (URS-004, FS-004)."""

from decimal import Decimal

import pytest

from sst.rounding import decimal_places, evaluate, reportable_value


@pytest.mark.parametrize(
    "measured,places,expected",
    [
        ("0.154", 2, "0.15"),
        ("0.155", 2, "0.16"),  # digit 5 rounds up (SOP-QC-021 s4.2)
        ("0.125", 2, "0.13"),
        ("89.95", 1, "90.0"),
        ("89.94", 1, "89.9"),
        ("110.05", 1, "110.1"),
        ("2.675", 2, "2.68"),  # binary float would give 2.67
        ("1.45", 1, "1.5"),
        (0.155, 2, "0.16"),  # float input is taken as entered, not as its binary expansion
    ],
)
def test_half_up_rounding(measured, places, expected):
    assert reportable_value(measured, places, "half_up") == Decimal(expected)


def test_half_even_mode_for_financial_regimes():
    assert reportable_value("2.5", 0, "half_even") == Decimal("2")
    assert reportable_value("3.5", 0, "half_even") == Decimal("4")


def test_unknown_mode_rejected():
    with pytest.raises(ValueError):
        reportable_value("1.0", 1, "truncate")


def test_decimal_places_from_limit():
    assert decimal_places("0.15") == 2
    assert decimal_places("90.0") == 1
    assert decimal_places("80") == 0


@pytest.mark.parametrize(
    "measured,lo,hi,rv,oos",
    [
        ("0.154", None, "0.15", "0.15", False),
        ("0.155", None, "0.15", "0.16", True),
        ("0.150", None, "0.15", "0.15", False),
        ("94.95", "95.0", "105.0", "95.0", False),
        ("94.94", "95.0", "105.0", "94.9", True),
        ("105.05", "95.0", "105.0", "105.1", True),
        ("79.5", "80", None, "80", False),
        ("79.4", "80", None, "79", True),
    ],
)
def test_evaluate_against_specification(measured, lo, hi, rv, oos):
    got_rv, got_oos = evaluate(measured, lo, hi, "half_up")
    assert (str(got_rv), got_oos) == (rv, oos)
