import streamlit as st
import pandas as pd

from modules.data_loader import (
    get_yield_col, get_temp_col, get_modulus_col,
    get_thermal_col, get_density_col, get_fatigue_col, get_carbon_col,
)
from modules.ui import render_filter_summary


def _build_filter_chips(filter_meta, unit_system):
    """Build human-readable filter summary chips."""
    chips = []
    if filter_meta.get("categories") and filter_meta.get("all_categories"):
        sel = filter_meta["categories"]
        all_c = filter_meta["all_categories"]
        if len(sel) < len(all_c):
            chips.append(f"Category: {', '.join(sel[:3])}{'…' if len(sel) > 3 else ''}")

    temp_col = get_temp_col(unit_system)
    yield_col = get_yield_col(unit_system)
    density_col = get_density_col(unit_system)
    fatigue_col = get_fatigue_col(unit_system)
    carbon_col = get_carbon_col(unit_system)

    if filter_meta.get("min_temp") is not None:
        u = "°F" if unit_system == "Imperial" else "°C"
        chips.append(f"Temp ≥ {filter_meta['min_temp']}{u}")
    if filter_meta.get("min_yield") is not None:
        u = "psi" if unit_system == "Imperial" else "MPa"
        chips.append(f"Yield ≥ {filter_meta['min_yield']} {u}")
    if filter_meta.get("max_density") is not None:
        u = "lb/in³" if unit_system == "Imperial" else "g/cm³"
        chips.append(f"Density ≤ {filter_meta['max_density']} {u}")
    if filter_meta.get("min_mach") and filter_meta["min_mach"] > 1:
        chips.append(f"Machinability ≥ {filter_meta['min_mach']}/10")
    if filter_meta.get("min_modulus") is not None:
        mod_unit = "Mpsi" if unit_system == "Imperial" else "GPa"
        chips.append(f"Modulus ≥ {filter_meta['min_modulus']} {mod_unit}")
    if filter_meta.get("min_tc") is not None:
        tc_unit = "BTU/hr·ft·°F" if unit_system == "Imperial" else "W/m·K"
        chips.append(f"Thermal cond. ≥ {filter_meta['min_tc']} {tc_unit}")
    
    # New filter chips
    if filter_meta.get("min_fatigue") is not None:
        u = "psi" if unit_system == "Imperial" else "MPa"
        chips.append(f"Fatigue ≥ {filter_meta['min_fatigue']} {u}")
    if filter_meta.get("min_hardness") is not None:
        chips.append(f"Hardness ≥ {filter_meta['min_hardness']} HB")
    if filter_meta.get("min_corrosion") and filter_meta["min_corrosion"] > 1:
        chips.append(f"Corrosion ≥ {filter_meta['min_corrosion']}/10")
    if filter_meta.get("min_weld") and filter_meta["min_weld"] > 1:
        chips.append(f"Weldability ≥ {filter_meta['min_weld']}/10")
    if filter_meta.get("min_uv") and filter_meta["min_uv"] > 1:
        chips.append(f"UV ≥ {filter_meta['min_uv']}/10")
    if filter_meta.get("max_carbon") is not None:
        u = "lb CO2/lb" if unit_system == "Imperial" else "kg CO2/kg"
        chips.append(f"Carbon ≤ {filter_meta['max_carbon']} {u}")
    if filter_meta.get("req_bio"):
        chips.append("Bio-compatible")
    if filter_meta.get("req_food"):
        chips.append("Food Grade")

    return chips


def render_filters(df, mode, unit_system, settings):
    """
    Render filter widgets and return the filtered DataFrame.

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
    fatigue_col = get_fatigue_col(unit_system)
    carbon_col = get_carbon_col(unit_system)

    filtered = df.copy()
    filter_meta = {}
    summary_meta = {}

    st.markdown("Use sliders to narrow the candidate pool before AI analysis.")

    # Category filter
    if "Category" in df.columns:
        all_categories = sorted(df["Category"].unique().tolist())
        selected_categories = st.multiselect(
            "Material categories",
            options=all_categories,
            default=all_categories,
            help="Limit search to specific material types (Metal, Polymer, etc.)",
        )
        filter_meta["categories"] = selected_categories
        filter_meta["all_categories"] = all_categories
        if len(selected_categories) < len(all_categories):
            summary_meta["categories"] = selected_categories
            summary_meta["all_categories"] = all_categories
        filtered = filtered[filtered["Category"].isin(selected_categories)]

    st.markdown("##### Industry Constraint Packs")
    pack_c1, pack_c2, pack_c3, pack_c4 = st.columns(4)
    with pack_c1:
        if st.button("Aerospace", use_container_width=True, help="High temp, high strength, low density"):
            st.session_state["pack_min_temp"] = 150 if unit_system == "Metric" else 300
            st.session_state["pack_min_yield"] = 300 if unit_system == "Metric" else 43500
            st.session_state["pack_max_density"] = 3.0 if unit_system == "Metric" else 0.11
            st.rerun()
    with pack_c2:
        if st.button("Medical", use_container_width=True, help="Moderate temp & strength, bio-compatible"):
            st.session_state["pack_min_temp"] = 130 if unit_system == "Metric" else 265
            st.session_state["pack_min_yield"] = 200 if unit_system == "Metric" else 29000
            st.session_state["pack_bio_compatible"] = "Yes"
            st.rerun()
    with pack_c3:
        if st.button("Heavy Machinery", use_container_width=True, help="High strength, temp, less density concern"):
            st.session_state["pack_min_temp"] = 200 if unit_system == "Metric" else 390
            st.session_state["pack_min_yield"] = 400 if unit_system == "Metric" else 58000
            st.rerun()
    with pack_c4:
        if st.button("Sustainable", use_container_width=True, help="Low carbon footprint, bio-compatible or food-grade"):
            st.session_state["pack_max_carbon"] = 3.5
            st.session_state["pack_bio_compatible"] = "Yes"
            st.rerun()

    if st.button("Reset Packs", type="tertiary"):
        for k in ["pack_min_temp", "pack_min_yield", "pack_max_density", "pack_max_carbon", "pack_bio_compatible"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.markdown("##### Essential constraints")
    fc1, fc2 = st.columns(2)

    with fc1:
        if temp_col in df.columns and not df[temp_col].empty:
            temp_min_val = int(df[temp_col].min())
            temp_max_val = int(df[temp_col].max())
            unit_label = "°F" if unit_system == "Imperial" else "°C"
            min_temp = st.slider(
                f"Minimum operating temperature ({unit_label})",
                min_value=temp_min_val,
                max_value=temp_max_val,
                value=max(st.session_state.get("pack_min_temp", settings.get("min_temp", temp_min_val)), temp_min_val),
                step=10,
                help="Materials must survive at or above this temperature.",
            )
            filter_meta["min_temp"] = min_temp
            if min_temp > temp_min_val:
                summary_meta["min_temp"] = min_temp
        else:
            min_temp = 0

    with fc2:
        if yield_col in df.columns and not df[yield_col].empty:
            yield_min_val = int(df[yield_col].min())
            yield_max_val = int(df[yield_col].max())
            unit_label = "psi" if unit_system == "Imperial" else "MPa"
            min_yield = st.slider(
                f"Minimum yield strength ({unit_label})",
                min_value=yield_min_val,
                max_value=yield_max_val,
                value=max(st.session_state.get("pack_min_yield", settings.get("min_yield", yield_min_val)), yield_min_val),
                step=10 if unit_system == "Metric" else 1000,
                help="Minimum structural strength required.",
            )
            filter_meta["min_yield"] = min_yield
            if min_yield > yield_min_val:
                summary_meta["min_yield"] = min_yield
        else:
            min_yield = 0

    if temp_col in filtered.columns:
        filtered = filtered[filtered[temp_col] >= min_temp]
    if yield_col in filtered.columns:
        filtered = filtered[filtered[yield_col] >= min_yield]

    # Advanced filters in expander
    with st.expander("Advanced constraints", expanded=False):
        ac1, ac2 = st.columns(2)

        with ac1:
            if density_col in df.columns and not df[density_col].empty:
                d_unit = "lb/in³" if unit_system == "Imperial" else "g/cm³"
                d_max = float(df[density_col].max())
                d_min = float(df[density_col].min())
                max_density = st.slider(
                    f"Maximum density ({d_unit})",
                    min_value=d_min,
                    max_value=d_max,
                    value=min(st.session_state.get("pack_max_density", d_max), d_max),
                    step=0.01 if unit_system == "Imperial" else 0.5,
                    help="Lower density means lighter parts.",
                )
                filter_meta["max_density"] = max_density
                if max_density < d_max:
                    summary_meta["max_density"] = max_density
                filtered = filtered[filtered[density_col] <= max_density]

            if modulus_col in df.columns and not df[modulus_col].empty:
                mod_unit = "Mpsi" if unit_system == "Imperial" else "GPa"
                mod_min = float(df[modulus_col].min())
                mod_max = float(df[modulus_col].max())
                min_modulus = st.slider(
                    f"Minimum elastic modulus ({mod_unit})",
                    min_value=mod_min,
                    max_value=mod_max,
                    value=max(settings.get("min_modulus", mod_min), mod_min),
                    step=1.0 if unit_system == "Metric" else 0.5,
                    help="Higher modulus = stiffer material.",
                )
                filter_meta["min_modulus"] = min_modulus
                if min_modulus > mod_min:
                    summary_meta["min_modulus"] = min_modulus
                filtered = filtered[filtered[modulus_col] >= min_modulus]

            if fatigue_col in df.columns and not df[fatigue_col].empty:
                fat_min_val = int(df[fatigue_col].min())
                fat_max_val = int(df[fatigue_col].max())
                f_unit = "psi" if unit_system == "Imperial" else "MPa"
                min_fatigue = st.slider(
                    f"Minimum fatigue strength ({f_unit})",
                    min_value=fat_min_val,
                    max_value=fat_max_val,
                    value=max(settings.get("min_fatigue", fat_min_val), fat_min_val),
                    step=10 if unit_system == "Metric" else 1000,
                    help="Materials must resist cyclic loading above this strength.",
                )
                filter_meta["min_fatigue"] = min_fatigue
                if min_fatigue > fat_min_val:
                    summary_meta["min_fatigue"] = min_fatigue
                filtered = filtered[filtered[fatigue_col] >= min_fatigue]

            if "Hardness (Brinell)" in df.columns and not df["Hardness (Brinell)"].empty:
                h_min = int(df["Hardness (Brinell)"].min())
                h_max = int(df["Hardness (Brinell)"].max())
                min_hardness = st.slider(
                    "Minimum hardness (Brinell)",
                    min_value=h_min,
                    max_value=h_max,
                    value=max(settings.get("min_hardness", h_min), h_min),
                    step=10,
                    help="Resistance to localized plastic deformation.",
                )
                filter_meta["min_hardness"] = min_hardness
                if min_hardness > h_min:
                    summary_meta["min_hardness"] = min_hardness
                filtered = filtered[filtered["Hardness (Brinell)"] >= min_hardness]

        with ac2:
            if "Machinability (1-10)" in df.columns:
                min_mach = st.slider(
                    "Minimum machinability (1–10)",
                    min_value=1,
                    max_value=10,
                    value=max(settings.get("min_mach", 1), 1),
                    step=1,
                    help="10 = easiest to machine.",
                )
                filter_meta["min_mach"] = min_mach
                if min_mach > 1:
                    summary_meta["min_mach"] = min_mach
                filtered = filtered[filtered["Machinability (1-10)"] >= min_mach]

            if thermal_col in df.columns and not df[thermal_col].empty:
                tc_unit = "BTU/hr·ft·°F" if unit_system == "Imperial" else "W/m·K"
                tc_min = float(df[thermal_col].min())
                tc_max = float(df[thermal_col].max())
                min_tc = st.slider(
                    f"Minimum thermal conductivity ({tc_unit})",
                    min_value=tc_min,
                    max_value=tc_max,
                    value=max(settings.get("min_tc", tc_min), tc_min),
                    step=1.0,
                    help="Important for heat sinks and exchangers.",
                )
                filter_meta["min_tc"] = min_tc
                if min_tc > tc_min:
                    summary_meta["min_tc"] = min_tc
                filtered = filtered[filtered[thermal_col] >= min_tc]

            if "Corrosion Resistance (1-10)" in df.columns:
                min_corrosion = st.slider(
                    "Minimum corrosion resistance (1–10)",
                    min_value=1,
                    max_value=10,
                    value=max(settings.get("min_corrosion", 1), 1),
                    step=1,
                    help="10 = extremely corrosion resistant.",
                )
                filter_meta["min_corrosion"] = min_corrosion
                if min_corrosion > 1:
                    summary_meta["min_corrosion"] = min_corrosion
                filtered = filtered[filtered["Corrosion Resistance (1-10)"] >= min_corrosion]

            if "Weldability (1-10)" in df.columns:
                min_weld = st.slider(
                    "Minimum weldability (1–10)",
                    min_value=1,
                    max_value=10,
                    value=max(settings.get("min_weld", 1), 1),
                    step=1,
                    help="10 = excellent weldability.",
                )
                filter_meta["min_weld"] = min_weld
                if min_weld > 1:
                    summary_meta["min_weld"] = min_weld
                filtered = filtered[filtered["Weldability (1-10)"] >= min_weld]

            if "UV Resistance (1-10)" in df.columns:
                min_uv = st.slider(
                    "Minimum UV resistance (1–10)",
                    min_value=1,
                    max_value=10,
                    value=max(settings.get("min_uv", 1), 1),
                    step=1,
                    help="10 = excellent resistance to UV degradation.",
                )
                filter_meta["min_uv"] = min_uv
                if min_uv > 1:
                    summary_meta["min_uv"] = min_uv
                filtered = filtered[filtered["UV Resistance (1-10)"] >= min_uv]

            if carbon_col in df.columns and not df[carbon_col].empty:
                c_unit = "lb CO2/lb" if unit_system == "Imperial" else "kg CO2/kg"
                c_min = float(df[carbon_col].min())
                c_max = float(df[carbon_col].max())
                max_carbon = st.slider(
                    f"Maximum embodied carbon ({c_unit})",
                    min_value=c_min,
                    max_value=c_max,
                    value=float(st.session_state.get("pack_max_carbon", settings.get("max_carbon", c_max))),
                    step=0.1,
                    help="Lower embodied carbon is more sustainable.",
                )
                filter_meta["max_carbon"] = max_carbon
                if max_carbon < c_max:
                    summary_meta["max_carbon"] = max_carbon
                filtered = filtered[filtered[carbon_col] <= max_carbon]

        st.markdown("##### Compliance & Certification")
        ch_c1, ch_c2 = st.columns(2)
        with ch_c1:
            preset_bio = st.session_state.get("pack_bio_compatible", "No") == "Yes"
            req_bio = st.checkbox(
                "Require bio-compatible materials",
                value=preset_bio or settings.get("req_bio", False),
                help="Only show materials certified bio-compatible.",
            )
            filter_meta["req_bio"] = req_bio
            if req_bio:
                summary_meta["req_bio"] = True
                filtered = filtered[filtered["Bio-compatible"] == "Yes"]
        with ch_c2:
            req_food = st.checkbox(
                "Require food-grade materials",
                value=settings.get("req_food", False),
                help="Only show food-safe materials.",
            )
            filter_meta["req_food"] = req_food
            if req_food:
                summary_meta["req_food"] = True
                filtered = filtered[filtered["Food Grade"] == "Yes"]

    chips = _build_filter_chips(summary_meta, unit_system)
    render_filter_summary(chips)

    count = len(filtered)
    if count == 0:
        st.error("No materials match your constraints. Try relaxing one or more filters.")
    elif count <= 5:
        st.warning(f"Only {count} material(s) match — consider relaxing filters for more options.")
    else:
        st.success(f"{count} materials available for AI analysis.")

    return filtered, {
        "min_temp": min_temp,
        "min_yield": min_yield,
        "max_density": filter_meta.get("max_density", 0.0),
        "min_modulus": filter_meta.get("min_modulus", 0.0),
        "min_mach": filter_meta.get("min_mach", 1),
        "min_tc": filter_meta.get("min_tc", 0.0),
        "min_fatigue": filter_meta.get("min_fatigue", 0),
        "min_hardness": filter_meta.get("min_hardness", 0),
        "min_corrosion": filter_meta.get("min_corrosion", 1),
        "min_weld": filter_meta.get("min_weld", 1),
        "min_uv": filter_meta.get("min_uv", 1),
        "max_carbon": filter_meta.get("max_carbon", 99.0),
        "req_bio": req_bio,
        "req_food": req_food,
    }
