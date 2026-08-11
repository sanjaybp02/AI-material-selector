import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.data_loader import convert_units, get_cost_col, get_density_col, get_yield_col


@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {
            "MaterialName": "Steel 1018",
            "Yield Strength (MPa)": 370.0,
            "Density (g/cm³)": 7.87,
            "Max Temp (°C)": 400.0,
            "Elastic Modulus (GPa)": 205.0,
            "Thermal Conductivity (W/m·K)": 51.9,
            "Cost per Kg (INR)": 60.0,
            "Fatigue Strength (MPa)": 170.0,
            "Embodied Carbon (kg CO2/kg)": 1.9,
        }
    ])


def test_metric_passthrough_returns_unmodified_copy(sample_df):
    result = convert_units(sample_df, system="Metric")
    assert result.equals(sample_df)
    assert result is not sample_df  # must be a copy, not the same object


def test_imperial_conversion_renames_and_converts_columns(sample_df):
    result = convert_units(sample_df, system="Imperial")
    assert "Yield Strength (psi)" in result.columns
    assert "Yield Strength (MPa)" not in result.columns
    # 370 MPa * 145.038 ~= 53664 psi
    assert result.iloc[0]["Yield Strength (psi)"] == pytest.approx(53664, abs=1)


def test_imperial_density_conversion_is_correct(sample_df):
    result = convert_units(sample_df, system="Imperial")
    # 7.87 g/cm3 * 0.03613 ~= 0.2844 lb/in3
    assert result.iloc[0]["Density (lb/in³)"] == pytest.approx(0.2844, abs=0.001)


def test_imperial_temp_conversion_is_correct(sample_df):
    result = convert_units(sample_df, system="Imperial")
    # 400 C -> F = 400*1.8+32 = 752
    assert result.iloc[0]["Max Temp (°F)"] == pytest.approx(752, abs=1)


def test_original_dataframe_never_mutated(sample_df):
    original_cols = list(sample_df.columns)
    convert_units(sample_df, system="Imperial")
    assert list(sample_df.columns) == original_cols  # untouched


def test_empty_dataframe_does_not_crash():
    result = convert_units(pd.DataFrame(), system="Imperial")
    assert result.empty


def test_column_helpers_respect_unit_system():
    assert get_density_col("Metric") == "Density (g/cm³)"
    assert get_density_col("Imperial") == "Density (lb/in³)"
    assert get_yield_col("Imperial") == "Yield Strength (psi)"
    assert get_cost_col("Metric") == "Cost per Kg (INR)"
