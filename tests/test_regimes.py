"""TS-001 Regime configuration loading (URS-001, FS-001)."""

from sst.regimes import available_regimes, load_regime


def test_all_regimes_load():
    assert available_regimes() == ["gcp", "glp", "gmp", "sox"]
    for code in available_regimes():
        r = load_regime(code)
        assert r.requires_audit("create") and r.requires_audit("update") and r.requires_audit("delete")
        assert r.requires_reason("update") and r.requires_reason("delete")


def test_gmp_is_active_by_default(monkeypatch):
    monkeypatch.delenv("SST_REGIME", raising=False)
    r = load_regime()
    assert r.code == "GMP" and r.results.rounding == "half_up" and r.records.reason_min_length == 10
    assert r.records.second_person_verification_on_oos_change is True


def test_sox_uses_half_even():
    assert load_regime("sox").results.rounding == "half_even"
