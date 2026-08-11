import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.cost_engine import calculate_part_cost


def test_metric_cost_from_database_source():
    row = pd.Series({"Density (g/cm³)": 7.87, "Cost per Kg (INR)": 60.0})
    result = calculate_part_cost(row, part_volume=10.0, cost_source="Database (CSV)")
    # mass = 10 cm3 * 7.87 g/cm3 = 78.7 g = 0.0787 kg
    assert result["mass_kg"] == pytest.approx(0.0787, abs=1e-4)
    assert result["source_label"] == "Database"
    assert result["cost_unit"] == "INR/kg"
    # total = 0.0787 kg * 60 INR/kg
    assert result["total_cost"] == pytest.approx(4.722, abs=0.01)


def test_metric_cost_with_live_api_override_labels_source_correctly():
    row = pd.Series({"Density (g/cm³)": 7.87, "Cost per Kg (INR)": 60.0})
    result = calculate_part_cost(row, part_volume=10.0, cost_source="Live Market (API)", cost_per_kg_override=75.0)
    assert result["source_label"] == "Live API"
    assert result["cost_per_kg"] == 75.0


def test_metric_cost_with_ai_estimate_labels_source_correctly():
    row = pd.Series({"Density (g/cm³)": 7.87, "Cost per Kg (INR)": 60.0})
    result = calculate_part_cost(row, part_volume=10.0, cost_source="AI Estimated", cost_per_kg_override=80.0)
    assert result["source_label"] == "AI Estimated"


def test_imperial_cost_uses_lb_density_and_usd_columns():
    row = pd.Series({"Density (lb/in³)": 0.284, "Cost per lb (USD)": 0.75})
    result = calculate_part_cost(row, part_volume=2.0, cost_source="Database (CSV)")
    assert result["mass_unit"] == "lb"
    assert result["cost_unit"] == "USD/lb"
    # mass = 2 in3 * 0.284 lb/in3 = 0.568 lb
    assert result["mass_display"] == pytest.approx(0.568, abs=1e-3)


def test_imperial_override_converts_inr_to_usd_per_lb():
    row = pd.Series({"Density (lb/in³)": 0.284, "Cost per lb (USD)": 0.75})
    result = calculate_part_cost(
        row, part_volume=2.0, cost_source="Live Market (API)",
        cost_per_kg_override=6000.0, inr_to_usd_rate=85.0,
    )
    # 6000 INR/kg -> USD/kg = 6000/85 -> USD/lb = /2.20462
    expected_usd_per_lb = (6000.0 / 85.0) / 2.20462
    assert result["cost_per_unit"] == pytest.approx(expected_usd_per_lb, rel=1e-3)


def test_zero_volume_yields_zero_cost():
    row = pd.Series({"Density (g/cm³)": 7.87, "Cost per Kg (INR)": 60.0})
    result = calculate_part_cost(row, part_volume=0.0, cost_source="Database (CSV)")
    assert result["total_cost"] == 0.0
