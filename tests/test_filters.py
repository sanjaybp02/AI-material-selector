import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.filters import _build_filter_chips, _clamp


def test_clamp_keeps_in_range_value_unchanged():
    assert _clamp(20.0, 0.0, 45.0) == 20.0


def test_clamp_pulls_down_an_out_of_range_high_default():
    # Confirmed-live bug this guards against: a stale persisted value
    # of 99.0 against a dataset whose real max is 45.0 used to expand
    # the slider itself to 0-99 instead of clamping.
    assert _clamp(99.0, 0.0, 45.0) == 45.0


def test_clamp_pulls_up_an_out_of_range_low_default():
    assert _clamp(-10.0, 0.0, 45.0) == 0.0


def test_filter_chips_include_active_temp_and_yield_constraints():
    chips = _build_filter_chips({"min_temp": 100, "min_yield": 200}, "Metric")
    assert any("Temp" in c for c in chips)
    assert any("Yield" in c for c in chips)


def test_filter_chips_respect_unit_system_labels():
    metric_chips = _build_filter_chips({"min_yield": 200}, "Metric")
    imperial_chips = _build_filter_chips({"min_yield": 200}, "Imperial")
    assert any("MPa" in c for c in metric_chips)
    assert any("psi" in c for c in imperial_chips)


def test_filter_chips_empty_when_no_constraints_active():
    assert _build_filter_chips({}, "Metric") == []


def test_filter_chips_include_boolean_compliance_flags():
    chips = _build_filter_chips({"req_bio": True, "req_food": True}, "Metric")
    assert "Bio-compatible" in chips
    assert "Food Grade" in chips
