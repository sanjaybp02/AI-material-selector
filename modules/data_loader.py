import os
import pandas as pd


def load_data(csv_path="materials.csv"):
    """Load the materials CSV and return a DataFrame."""
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


# Every downstream module (filters.py, charts.py, cost_engine.py,
# cad_export.py) assumes these columns exist and reads them directly by
# name — none of them validate first. Without a check here, a missing or
# renamed column in materials.csv doesn't fail where the real problem is;
# it fails minutes later as a cryptic KeyError deep inside a filter
# slider or a chart, far from the actual cause.
REQUIRED_MATERIAL_COLUMNS = [
    "Material Name", "Category", "Yield Strength (MPa)", "Density (g/cm³)",
    "Max Temp (°C)", "Elastic Modulus (GPa)", "Thermal Conductivity (W/m·K)",
    "Machinability (1-10)", "Cost per Kg (INR)", "Fatigue Strength (MPa)",
    "Embodied Carbon (kg CO2/kg)",
]

# Columns every cost/filter/chart calculation treats as real numbers.
# pandas silently reads a mixed-type CSV column as dtype=object rather
# than raising, so a single stray non-numeric cell (a typo, a unit
# suffix accidentally left in) would otherwise reach float()/arithmetic
# deep in another module before ever surfacing as an error.
_NUMERIC_MATERIAL_COLUMNS = [
    "Yield Strength (MPa)", "Density (g/cm³)", "Max Temp (°C)",
    "Elastic Modulus (GPa)", "Thermal Conductivity (W/m·K)",
    "Machinability (1-10)", "Cost per Kg (INR)", "Fatigue Strength (MPa)",
    "Embodied Carbon (kg CO2/kg)",
]


def validate_materials_df(df):
    """Validate the loaded materials DataFrame before the rest of the app
    ever touches it. Returns (is_valid, errors) rather than raising, so
    the caller can decide how to present the problem (this app shows all
    of them at once and stops, instead of the user fixing one typo per
    reload).
    """
    errors = []
    if df is None or df.empty:
        errors.append("materials.csv is missing, empty, or failed to load.")
        return False, errors

    missing = [c for c in REQUIRED_MATERIAL_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing required column(s): {', '.join(missing)}")
        return False, errors  # can't safely check row-level content without the columns

    name_col = df["Material Name"]
    if name_col.isna().any() or (name_col.astype(str).str.strip() == "").any():
        errors.append("One or more rows have a blank 'Material Name'.")

    normalized_names = name_col.astype(str).str.strip().str.lower()
    dupes = sorted(normalized_names[normalized_names.duplicated()].unique())
    if dupes:
        errors.append(f"Duplicate 'Material Name' value(s): {', '.join(dupes)}")

    for col in _NUMERIC_MATERIAL_COLUMNS:
        coerced = pd.to_numeric(df[col], errors="coerce")
        bad_mask = coerced.isna() & df[col].notna()
        if bad_mask.any():
            bad_names = df.loc[bad_mask, "Material Name"].astype(str).tolist()
            shown = ", ".join(bad_names[:5])
            more = f" (+{len(bad_names) - 5} more)" if len(bad_names) > 5 else ""
            errors.append(f"Non-numeric value(s) in '{col}' for: {shown}{more}")

    return (len(errors) == 0), errors


# ----- Unit Conversion System -----

# Column name mappings: Metric -> Imperial
METRIC_TO_IMPERIAL_COLUMNS = {
    "Yield Strength (MPa)": "Yield Strength (psi)",
    "Max Temp (°C)": "Max Temp (°F)",
    "Elastic Modulus (GPa)": "Elastic Modulus (Mpsi)",
    "Density (g/cm³)": "Density (lb/in³)",
    "Thermal Conductivity (W/m·K)": "Thermal Conductivity (BTU/hr·ft·°F)",
    "Cost per Kg (INR)": "Cost per lb (USD)",
    "Fatigue Strength (MPa)": "Fatigue Strength (psi)",
    "Embodied Carbon (kg CO2/kg)": "Embodied Carbon (lb CO2/lb)",
}

# Default exchange rate — can be overridden by user
DEFAULT_INR_TO_USD = 85.0


def convert_units(df, system="Metric", inr_to_usd_rate=DEFAULT_INR_TO_USD):
    """
    Convert a DataFrame between Metric and Imperial unit systems.

    Parameters
    ----------
    df : pd.DataFrame
        The materials dataframe in its original Metric units.
    system : str
        "Metric" or "Imperial".
    inr_to_usd_rate : float
        INR per 1 USD.

    Returns
    -------
    pd.DataFrame
        Converted DataFrame (copy, original is not mutated).
    """
    if system == "Metric" or df.empty:
        return df.copy()

    converted = df.copy()

    # Yield Strength: MPa -> psi  (× 145.038)
    if "Yield Strength (MPa)" in converted.columns:
        converted["Yield Strength (MPa)"] = (converted["Yield Strength (MPa)"] * 145.038).round(0)
        converted.rename(columns={"Yield Strength (MPa)": "Yield Strength (psi)"}, inplace=True)

    # Elastic Modulus: GPa -> Mpsi  (× 0.145038)
    if "Elastic Modulus (GPa)" in converted.columns:
        converted["Elastic Modulus (GPa)"] = (converted["Elastic Modulus (GPa)"] * 0.145038).round(2)
        converted.rename(columns={"Elastic Modulus (GPa)": "Elastic Modulus (Mpsi)"}, inplace=True)

    # Max Temp: °C -> °F  (× 1.8 + 32)
    if "Max Temp (°C)" in converted.columns:
        converted["Max Temp (°C)"] = (converted["Max Temp (°C)"] * 1.8 + 32).round(0)
        converted.rename(columns={"Max Temp (°C)": "Max Temp (°F)"}, inplace=True)

    # Density: g/cm³ -> lb/in³  (× 0.03613)
    if "Density (g/cm³)" in converted.columns:
        converted["Density (g/cm³)"] = (converted["Density (g/cm³)"] * 0.03613).round(4)
        converted.rename(columns={"Density (g/cm³)": "Density (lb/in³)"}, inplace=True)

    # Thermal Conductivity: W/m·K -> BTU/(hr·ft·°F)  (× 0.5779)
    if "Thermal Conductivity (W/m·K)" in converted.columns:
        converted["Thermal Conductivity (W/m·K)"] = (converted["Thermal Conductivity (W/m·K)"] * 0.5779).round(2)
        converted.rename(columns={"Thermal Conductivity (W/m·K)": "Thermal Conductivity (BTU/hr·ft·°F)"}, inplace=True)

    # Cost: INR/Kg -> USD/lb  ( ÷ rate ÷ 2.20462 )
    if "Cost per Kg (INR)" in converted.columns:
        converted["Cost per Kg (INR)"] = (converted["Cost per Kg (INR)"] / inr_to_usd_rate / 2.20462).round(2)
        converted.rename(columns={"Cost per Kg (INR)": "Cost per lb (USD)"}, inplace=True)

    # Fatigue Strength: MPa -> psi  (× 145.038)
    if "Fatigue Strength (MPa)" in converted.columns:
        converted["Fatigue Strength (MPa)"] = (converted["Fatigue Strength (MPa)"] * 145.038).round(0)
        converted.rename(columns={"Fatigue Strength (MPa)": "Fatigue Strength (psi)"}, inplace=True)

    # Embodied Carbon: kg CO2/kg -> lb CO2/lb (remains numerically identical, rename column)
    if "Embodied Carbon (kg CO2/kg)" in converted.columns:
        converted.rename(columns={"Embodied Carbon (kg CO2/kg)": "Embodied Carbon (lb CO2/lb)"}, inplace=True)

    return converted


def get_density_col(system="Metric"):
    return "Density (lb/in³)" if system == "Imperial" else "Density (g/cm³)"


def get_yield_col(system="Metric"):
    return "Yield Strength (psi)" if system == "Imperial" else "Yield Strength (MPa)"


def get_temp_col(system="Metric"):
    return "Max Temp (°F)" if system == "Imperial" else "Max Temp (°C)"


def get_modulus_col(system="Metric"):
    return "Elastic Modulus (Mpsi)" if system == "Imperial" else "Elastic Modulus (GPa)"


def get_thermal_col(system="Metric"):
    return "Thermal Conductivity (BTU/hr·ft·°F)" if system == "Imperial" else "Thermal Conductivity (W/m·K)"


def get_cost_col(system="Metric"):
    return "Cost per lb (USD)" if system == "Imperial" else "Cost per Kg (INR)"


def get_currency_symbol(system="Metric"):
    return "$" if system == "Imperial" else "₹"


def get_volume_unit(system="Metric"):
    return "in³" if system == "Imperial" else "cm³"


def get_mass_unit(system="Metric"):
    return "lb" if system == "Imperial" else "kg"


def get_fatigue_col(system="Metric"):
    return "Fatigue Strength (psi)" if system == "Imperial" else "Fatigue Strength (MPa)"


def get_carbon_col(system="Metric"):
    return "Embodied Carbon (lb CO2/lb)" if system == "Imperial" else "Embodied Carbon (kg CO2/kg)"
