import streamlit as st
import pandas as pd

from modules.data_loader import (
    get_yield_col, get_temp_col, get_modulus_col,
    get_thermal_col, get_density_col
)


def render_filters(df, mode, unit_system, settings):
    """
    Render filter widgets in the main page area (2-column grid)
    and return the filtered DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The (possibly unit-converted) materials DataFrame.
    mode : str
        "⚡ Lite" or "🔬 Normal".
    unit_system : str
        "Metric" or "Imperial".
    settings : dict
        Persisted settings dict for default values.

    Returns
    -------
    (pd.DataFrame, dict)
        Filtered subset of df, and filter values to persist.
    """
    yield_col = get_yield_col(unit_system)
    temp_col = get_temp_col(unit_system)
    modulus_col = get_modulus_col(unit_system)
    thermal_col = get_thermal_col(unit_system)
    density_col = get_density_col(unit_system)

    filtered = df.copy()

    # --- Category filter (Normal only, full-width at top) ---
    if mode == "🔬 Normal" and "Category" in df.columns:
        all_categories = sorted(df["Category"].unique().tolist())
        selected_categories = st.multiselect(
            "Material Category",
            options=all_categories,
            default=all_categories,
            help="Select one or more material categories"
        )
        filtered = filtered[filtered["Category"].isin(selected_categories)]

    # --- Basic filters in 2 columns ---
    fc1, fc2 = st.columns(2)

    with fc1:
        if temp_col in df.columns and not df[temp_col].empty:
            temp_min_val = int(df[temp_col].min())
            temp_max_val = int(df[temp_col].max())
            unit_label = "°F" if unit_system == "Imperial" else "°C"
            min_temp = st.slider(
                f"Min Operating Temp ({unit_label})",
                min_value=temp_min_val,
                max_value=temp_max_val,
                value=max(settings.get("min_temp", temp_min_val), temp_min_val),
                step=10
            )
        else:
            min_temp = 0

    with fc2:
        if yield_col in df.columns and not df[yield_col].empty:
            yield_min_val = int(df[yield_col].min())
            yield_max_val = int(df[yield_col].max())
            unit_label = "psi" if unit_system == "Imperial" else "MPa"
            min_yield = st.slider(
                f"Min Yield Strength ({unit_label})",
                min_value=yield_min_val,
                max_value=yield_max_val,
                value=max(settings.get("min_yield", yield_min_val), yield_min_val),
                step=10 if unit_system == "Metric" else 1000
            )
        else:
            min_yield = 0

    # Apply basic filters
    if temp_col in filtered.columns:
        filtered = filtered[filtered[temp_col] >= min_temp]
    if yield_col in filtered.columns:
        filtered = filtered[filtered[yield_col] >= min_yield]

    # --- Advanced filters (Normal only, 2-column grid) ---
    if mode == "🔬 Normal":
        ac1, ac2 = st.columns(2)

        with ac1:
            # Max Density
            if density_col in df.columns and not df[density_col].empty:
                d_unit = "lb/in³" if unit_system == "Imperial" else "g/cm³"
                d_max = float(df[density_col].max())
                d_min = float(df[density_col].min())
                max_density = st.slider(
                    f"Max Density ({d_unit})",
                    min_value=d_min,
                    max_value=d_max,
                    value=d_max,
                    step=0.01 if unit_system == "Imperial" else 0.5,
                    help="Lower density = lighter material"
                )
                filtered = filtered[filtered[density_col] <= max_density]

            # Min Elastic Modulus
            if modulus_col in df.columns and not df[modulus_col].empty:
                mod_unit = "Mpsi" if unit_system == "Imperial" else "GPa"
                mod_min = float(df[modulus_col].min())
                mod_max = float(df[modulus_col].max())
                min_modulus = st.slider(
                    f"Min Elastic Modulus ({mod_unit})",
                    min_value=mod_min,
                    max_value=mod_max,
                    value=mod_min,
                    step=1.0 if unit_system == "Metric" else 0.5,
                    help="Higher = stiffer material"
                )
                filtered = filtered[filtered[modulus_col] >= min_modulus]

        with ac2:
            # Min Machinability
            if "Machinability (1-10)" in df.columns:
                min_mach = st.slider(
                    "Min Machinability (1–10)",
                    min_value=1,
                    max_value=10,
                    value=1,
                    step=1,
                    help="10 = easiest to machine"
                )
                filtered = filtered[filtered["Machinability (1-10)"] >= min_mach]

            # Min Thermal Conductivity
            if thermal_col in df.columns and not df[thermal_col].empty:
                tc_unit = "BTU/hr·ft·°F" if unit_system == "Imperial" else "W/m·K"
                tc_min = float(df[thermal_col].min())
                tc_max = float(df[thermal_col].max())
                min_tc = st.slider(
                    f"Min Thermal Conductivity ({tc_unit})",
                    min_value=tc_min,
                    max_value=tc_max,
                    value=tc_min,
                    step=1.0,
                    help="Higher = better heat conduction"
                )
                filtered = filtered[filtered[thermal_col] >= min_tc]

    return filtered, {"min_temp": min_temp, "min_yield": min_yield}
