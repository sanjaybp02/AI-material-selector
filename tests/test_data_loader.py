import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.data_loader import convert_units, get_cost_col, get_density_col, get_yield_col, validate_materials_df


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


# ---------------------------------------------------------------------
# validate_materials_df — fail-fast schema/content validation for the
# CSV every downstream module (filters, charts, cost_engine, cad_export)
# assumes is already correct.
# ---------------------------------------------------------------------

def _valid_row(**overrides):
    row = {
        "Material Name": "Aluminum 6061",
        "Category": "Metal",
        "Yield Strength (MPa)": 276,
        "Density (g/cm³)": 2.70,
        "Max Temp (°C)": 150,
        "Elastic Modulus (GPa)": 68.9,
        "Thermal Conductivity (W/m·K)": 167.0,
        "Machinability (1-10)": 9,
        "Cost per Kg (INR)": 290.5,
        "Fatigue Strength (MPa)": 96.0,
        "Embodied Carbon (kg CO2/kg)": 8.5,
    }
    row.update(overrides)
    return row


def test_valid_dataframe_passes():
    df = pd.DataFrame([_valid_row(), _valid_row(**{"Material Name": "Steel 1018"})])
    is_valid, errors = validate_materials_df(df)
    assert is_valid is True
    assert errors == []


def test_empty_dataframe_fails_with_clear_message():
    is_valid, errors = validate_materials_df(pd.DataFrame())
    assert is_valid is False
    assert any("missing, empty" in e for e in errors)


def test_none_input_fails_without_crashing():
    is_valid, errors = validate_materials_df(None)
    assert is_valid is False


def test_missing_required_column_is_reported_by_name():
    df = pd.DataFrame([_valid_row()]).drop(columns=["Density (g/cm³)"])
    is_valid, errors = validate_materials_df(df)
    assert is_valid is False
    assert any("Density (g/cm³)" in e for e in errors)


def test_blank_material_name_is_rejected():
    df = pd.DataFrame([_valid_row(**{"Material Name": "   "})])
    is_valid, errors = validate_materials_df(df)
    assert is_valid is False
    assert any("blank" in e.lower() for e in errors)


def test_duplicate_material_names_are_rejected():
    df = pd.DataFrame([_valid_row(), _valid_row()])  # same name twice
    is_valid, errors = validate_materials_df(df)
    assert is_valid is False
    assert any("Duplicate" in e for e in errors)


def test_duplicate_check_is_case_and_whitespace_insensitive():
    df = pd.DataFrame([_valid_row(), _valid_row(**{"Material Name": "  aluminum 6061  "})])
    is_valid, errors = validate_materials_df(df)
    assert is_valid is False
    assert any("Duplicate" in e for e in errors)


def test_non_numeric_value_in_numeric_column_is_rejected():
    df = pd.DataFrame([_valid_row(**{"Yield Strength (MPa)": "very strong"})])
    is_valid, errors = validate_materials_df(df)
    assert is_valid is False
    assert any("Yield Strength (MPa)" in e for e in errors)


def test_real_materials_csv_passes_validation():
    """The actual shipped dataset must always pass its own validator."""
    from modules.data_loader import load_data

    df = load_data(str(Path(__file__).resolve().parent.parent / "materials.csv"))
    is_valid, errors = validate_materials_df(df)
    assert is_valid is True, f"materials.csv failed its own validation: {errors}"
