# Hot-reload trigger: 2026-07-21
import os
import json
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import pandas as pd
from google import genai

from modules.data_loader import (
    load_data, convert_units, get_yield_col, get_density_col, get_cost_col,
    get_currency_symbol, get_volume_unit, get_carbon_col,
)
from modules.filters import render_filters
from modules.cost_engine import fetch_live_metal_price, calculate_part_cost
from modules.ai_engine import get_single_recommendation, get_top3_recommendations, chat_followup, explain_filter_failure
from modules.charts import radar_chart, scatter_plot, property_heatmap
from modules.pdf_report import create_pdf
from modules.history import init_history, log_search, render_history_table
from modules.templates import load_templates, save_custom_template, delete_custom_template
from modules.ui import (
    inject_theme, render_hero, section_header, render_status_banner,
    render_empty_state, render_confidence_bar, render_pros_cons,
    render_sidebar_status, render_footer, render_tour_banner,
    inject_clarity,
)

SETTINGS_FILE = "settings.json"
MODEL_OPTIONS = [
    "gemini-flash-latest", "gemini-pro-latest",
    "gemini-2.5-flash", "gemini-2.5-pro",
    "gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview",
]
COST_OPTIONS = ["Use CSV Database Pricing", "Use AI Market Estimation", "Use Live MetalPrice API"]


# ── Settings ────────────────────────────────────────────────────────
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f)


def match_material(df_raw, mat_name):
    """Match AI material name to database row (exact first, then fuzzy)."""
    if not mat_name:
        return None
    exact = df_raw[df_raw["Material Name"].str.lower() == mat_name.lower()]
    if not exact.empty:
        return exact.iloc[0]
    fuzzy = df_raw[df_raw["Material Name"].str.contains(mat_name, case=False, na=False)]
    if not fuzzy.empty:
        return fuzzy.iloc[0]
    return None


def compute_part_cost(row, part_volume, cost_source, ai_data=None):
    if cost_source == "Use AI Market Estimation" and ai_data:
        cpk = float(ai_data.get("EstimatedCostINR", 0))
        return calculate_part_cost(row, part_volume, cost_source, cpk)
    if cost_source == "Use Live MetalPrice API":
        live_price, err = fetch_live_metal_price(row["Material Name"])
        if live_price is not None:
            return calculate_part_cost(row, part_volume, cost_source, live_price)
        st.warning(f"Live price unavailable ({err}). Using database pricing.")
    return calculate_part_cost(row, part_volume, cost_source)


def format_mass(result, unit_system):
    mass_display = result.get("mass_display")
    if mass_display is None:
        mass_display = result["mass_kg"] if unit_system == "Metric" else result["mass_kg"] * 2.20462
    mass_unit = result.get("mass_unit", "kg" if unit_system == "Metric" else "lb")
    return mass_display, mass_unit


# ── Dialogs ─────────────────────────────────────────────────────────
@st.dialog("Save custom template")
def create_template_dialog():
    st.caption("Save a reusable prompt for common engineering scenarios.")
    t_name = st.text_input("Template name", placeholder="e.g. UAV wing spar")
    t_desc = st.text_input("Short description", placeholder="Shown on hover")
    t_prompt = st.text_area("Prompt text", placeholder="Describe material requirements...", height=120)
    if st.button("Save template", type="primary"):
        if t_name and t_prompt:
            save_custom_template(t_name, t_desc, t_prompt)
            st.rerun()
        else:
            st.error("Name and prompt are required.")


@st.dialog("Material Datasheet")
def render_datasheet(properties):
    st.markdown(f"### {properties.get('Material Name', 'Unknown Material')}")
    st.caption(f"Category: {properties.get('Category', 'N/A')}")
    
    df_props = pd.DataFrame([{"Property": k, "Value": v} for k, v in properties.items() if k not in ["Material Name", "Category"]])
    st.dataframe(df_props, hide_index=True, use_container_width=True)




def render_template_picker(templates):
    """Render searchable template quick-picks."""
    st.markdown("**Quick-start templates**")
    search = st.text_input(
        "Search templates",
        placeholder="Filter by name...",
        label_visibility="collapsed",
        key="template_search",
    )
    filtered = templates
    if search.strip():
        q = search.lower()
        filtered = [t for t in templates if q in t["name"].lower() or q in t.get("description", "").lower()]

    if not filtered:
        st.caption("No templates match your search.")
        return

    cols_per_row = 3
    for row_start in range(0, min(len(filtered), 12), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = row_start + j
            if idx >= len(filtered) or idx >= 12:
                break
            t = filtered[idx]
            with col:
                if st.button(t["name"], key=f"tpl_{idx}_{t['name']}", use_container_width=True, help=t.get("description", "")):
                    st.session_state["active_prompt"] = t["prompt"]
                    st.rerun()
                if t.get("is_custom"):
                    if st.button("Remove", key=f"del_{t['name']}", use_container_width=True):
                        delete_custom_template(t["name"])
                        st.rerun()

    if len(filtered) > 12:
        st.caption(f"Showing 12 of {len(filtered)} templates. Refine search to find more.")

    if st.button("+ Create custom template", use_container_width=True):
        create_template_dialog()


def render_lite_results(r, currency, unit_system):
    st.success("Analysis complete")
    mass_display, mass_unit = format_mass(r["result"], unit_system)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recommended material", r["exact_name"])
    c2.metric("Confidence", f"{r['confidence']}%")
    c3.metric(
        f"Est. part cost ({r['result']['source_label']})",
        f"{currency}{r['result']['total_cost']:.2f}",
        delta=f"{mass_display:.2f} {mass_unit}",
        delta_color="off",
    )
    
    # Calculate carbon metric
    carbon_val = r.get("total_carbon_kg", 0.0)
    carbon_unit = "kg CO2"
    if unit_system == "Imperial":
        carbon_val = carbon_val * 2.20462
        carbon_unit = "lb CO2"
    c4.metric("Est. Carbon Footprint", f"{carbon_val:.3f} {carbon_unit}")

    render_confidence_bar(r["confidence"])
    st.markdown("##### Engineering reasoning")
    st.info(r["reasoning"])

    pdf_bytes = create_pdf(
        r["exact_name"], r["confidence"], r["reasoning"],
        r["result"]["total_cost"], mass_display, r["part_volume"], currency,
        r.get("properties"), carbon_val, carbon_unit
    )

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        st.download_button(
            "Download PDF report", data=pdf_bytes,
            file_name="Material_Recommendation.pdf", mime="application/pdf",
            use_container_width=True,
        )
    with c_btn2:
        if st.button("View Datasheet", use_container_width=True):
            render_datasheet(r.get("properties", {}))


def render_advanced_results(processed, rec_names, df_display, unit_system, api_key, model_name):
    currency = get_currency_symbol(unit_system)
    tab_results, tab_charts, tab_compare, tab_history = st.tabs(
        ["Results", "Charts", "Compare", "History"]
    )

    with tab_results:
        st.caption(f"{len(processed)} candidate(s) ranked by suitability")
        summary_rows = []
        for rank, item in enumerate(processed, start=1):
            mass_display, mass_unit = format_mass(item["result"], unit_system)
            carbon_val = item.get("total_carbon_kg", 0.0)
            carbon_unit = "kg CO2"
            if unit_system == "Imperial":
                carbon_val = carbon_val * 2.20462
                carbon_unit = "lb CO2"
            summary_rows.append({
                "Rank": rank,
                "Material": item["exact_name"],
                "Confidence": f"{item['confidence']}%",
                "Cost": f"{currency}{item['result']['total_cost']:.2f}",
                "Mass": f"{mass_display:.2f} {mass_unit}",
                "Carbon": f"{carbon_val:.3f} {carbon_unit}",
            })
        if summary_rows:
            st.dataframe(
                pd.DataFrame(summary_rows),
                hide_index=True,
                use_container_width=True,
            )
            st.caption("Open a candidate below for engineering reasoning, exports, and datasheet details.")
        for rank, item in enumerate(processed):
            rank_label = f"Rank {rank + 1}"
            mass_display, mass_unit = format_mass(item["result"], unit_system)
            with st.expander(f"{rank_label}: {item['exact_name']} — {item['confidence']}% confidence", expanded=(rank == 0)):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Material", item["exact_name"])
                m2.metric("Confidence", f"{item['confidence']}%")
                m3.metric(
                    f"Cost ({item['result']['source_label']})",
                    f"{currency}{item['result']['total_cost']:.2f}",
                    delta=f"{mass_display:.2f} {mass_unit}",
                    delta_color="off",
                )
                carbon_val = item.get("total_carbon_kg", 0.0)
                carbon_unit = "kg CO2"
                if unit_system == "Imperial":
                    carbon_val = carbon_val * 2.20462
                    carbon_unit = "lb CO2"
                m4.metric("Carbon Footprint", f"{carbon_val:.3f} {carbon_unit}")

                render_confidence_bar(item["confidence"])
                st.markdown(f"**Reasoning:** {item['reasoning']}")
                render_pros_cons(item.get("pros", []), item.get("cons", []))
                
                pdf_bytes = create_pdf(
                    item["exact_name"], item["confidence"], item["reasoning"],
                    item["result"]["total_cost"], mass_display, item["part_volume"], currency,
                    item.get("properties"), carbon_val, carbon_unit
                )
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    st.download_button(
                        f"PDF — {item['exact_name']}", data=pdf_bytes,
                        file_name=f"Report_{item['exact_name'].replace(' ', '_')}.pdf",
                        mime="application/pdf", key=f"pdf_{rank}",
                        use_container_width=True,
                    )
                with c_btn2:
                    if st.button(f"Datasheet", key=f"ds_{rank}", use_container_width=True):
                        render_datasheet(item.get("properties", {}))

    with tab_charts:
        if rec_names:
            chart_df = st.session_state.get("last_edited_df", df_display)
            st.plotly_chart(
                radar_chart(chart_df, rec_names, unit_system),
                use_container_width=True,
                key="plotly_radar_chart"
            )
            
            st.markdown("##### Custom Scatter Telemetry")
            yield_c, density_c = get_yield_col(unit_system), get_density_col(unit_system)
            avail_cols = [c for c in chart_df.columns if c not in ["Material Name", "Category", "Bio-compatible", "Food Grade", "Standards"]]
            c_x, c_y = st.columns(2)
            with c_x:
                x_axis = st.selectbox(
                    "X-axis Property",
                    options=avail_cols,
                    index=avail_cols.index(density_c) if density_c in avail_cols else 0,
                    key="scatter_x_axis"
                )
            with c_y:
                y_axis = st.selectbox(
                    "Y-axis Property",
                    options=avail_cols,
                    index=avail_cols.index(yield_c) if yield_c in avail_cols else 0,
                    key="scatter_y_axis"
                )
            st.plotly_chart(
                scatter_plot(chart_df, x_axis, y_axis, rec_names),
                use_container_width=True,
                key="plotly_scatter_plot"
            )
            
            with st.expander("Property heatmap"):
                st.plotly_chart(
                    property_heatmap(chart_df, unit_system),
                    use_container_width=True,
                    key="plotly_heatmap"
                )
        else:
            render_empty_state("", "No chart data", "Run an analysis to generate visual comparisons.")

    with tab_compare:
        chart_df = st.session_state.get("last_edited_df", df_display)
        options = chart_df["Material Name"].tolist() if not chart_df.empty else []
        selected = st.multiselect(
            "Select materials to compare (up to 4)",
            options=options,
            default=rec_names[:2] if len(rec_names) >= 2 else rec_names,
            max_selections=4,
        )
        if len(selected) >= 2:
            st.plotly_chart(
                radar_chart(chart_df, selected, unit_system),
                use_container_width=True,
                key="plotly_radar_compare"
            )
        elif selected:
            st.info("Select at least two materials to compare.")
        else:
            render_empty_state("", "Pick materials", "Choose two or more from the list above.")

    with tab_history:
        render_history_table()

    return tab_results


# ── Main Setup ────────────────────────────────────────────────────────
# page config must be first
st.set_page_config(
    page_title="Material Selector",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()
inject_clarity()

# Load main application data
settings = load_settings()
df_raw = load_data()
init_history()

env_api_key = os.getenv("GEMINI_API_KEY", "")
api_key_saved = bool(settings.get("api_key", env_api_key))
app_mode = settings.get("mode", "Advanced")

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    if st.button(
        "Start Guided Tour",
        key="manual_tour_btn",
        help="Open the guided onboarding tour",
        use_container_width=True,
    ):
        st.session_state["tour_active"] = True
        st.session_state["tour_step"] = 1
        st.rerun()

    api_key = st.text_input(
        "Gemini API key",
        type="password",
        value=settings.get("api_key", env_api_key),
        help="Required for AI recommendations. Get one at Google AI Studio or set GEMINI_API_KEY in .env",
    )
    model_name = st.selectbox(
        "Model",
        MODEL_OPTIONS,
        index=MODEL_OPTIONS.index(settings.get("model_name", MODEL_OPTIONS[0]))
        if settings.get("model_name") in MODEL_OPTIONS else 0,
    )
    st.divider()
    mode = st.radio(
        "Mode",
        ["Lite", "Advanced"],
        index=0 if settings.get("mode", "Advanced") == "Lite" else 1,
        help="""**Lite Mode**
- **Instant Answers**: Get a single, direct material recommendation in seconds.
- **Zero Clutter**: Clean interface that skips complex filters.
- **Perfect for**: Quick feasibility checks and standard parts.

**Advanced Mode** (recommended)
- **Deep Dive Filters**: Fine-tune candidates using physical sliders and compliance settings.
- **Interactive Visuals**: Compare options with dynamic Radar, Heatmap, and Scatter plots.
- **AI Partner Chat**: Talk trade-offs and processing options in the centered chat.""",
    )
    is_advanced = mode == "Advanced"
    if is_advanced:
        st.divider()
        unit_system = st.radio(
            "Units",
            ["Metric", "Imperial"],
            horizontal=True,
            index=0 if settings.get("unit_system", "Metric") == "Metric" else 1,
        )
    else:
        unit_system = settings.get("unit_system", "Metric")

    render_sidebar_status(bool(api_key), len(df_raw))

df_display = convert_units(df_raw, unit_system)

# Tour state is user-controlled only so the interface does not block first-run screening.
if "tour_active" not in st.session_state:
    st.session_state["tour_active"] = False
    st.session_state["tour_step"] = 1

# Render spotlight backdrop if tour active
if st.session_state.get("tour_active"):
    st.markdown('<div class="tour-backdrop"></div>', unsafe_allow_html=True)

# Main layout
render_hero("Lite" if not is_advanced else "Advanced")

st.caption("ENGINEERING INTELLIGENCE DASHBOARD")

# Step 1 — Requirements
with st.container(border=True):
    st.markdown('<div id="tour-step-1-anchor"></div>', unsafe_allow_html=True)
    if st.session_state.get("tour_active") and st.session_state.get("tour_step") == 1:
        total = 3 if is_advanced else 2
        render_tour_banner(
            1, total, 
            "Define Requirements", 
            "Describe your application or select one of the Quick-start templates to prefill the query. Set your part volume and select a cost data source.",
            "tour_s1"
        )
    section_header(
        "1", "Define requirements",
        "Describe your application or pick a template, then set volume and pricing.",
    )
    req_left, req_right = st.columns([1.6, 1])

    with req_left:
        render_template_picker(load_templates())
        if is_advanced:
            alt_material = st.selectbox(
                "Replace existing material (optional)",
                options=["None"] + df_display["Material Name"].tolist(),
                help="Find a better alternative to a material you already use.",
            )
        else:
            alt_material = "None"

        user_query = st.text_area(
            "Project requirements",
            value=st.session_state.get("active_prompt", ""),
            placeholder="Example: Lightweight drone frame, high yield strength, good machinability, operating up to 80°C...",
            height=130,
            help="Be specific about load, environment, manufacturing process, and budget.",
        )

    with req_right:
        vol_unit = get_volume_unit(unit_system)
        part_volume = st.number_input(
            f"Part volume ({vol_unit})",
            min_value=1.0,
            value=float(settings.get("part_volume", 50.0)),
            step=10.0,
        )
        default_cost = settings.get("cost_source", COST_OPTIONS[0])
        cost_source = st.radio(
            "Cost data source",
            options=COST_OPTIONS,
            index=COST_OPTIONS.index(default_cost) if default_cost in COST_OPTIONS else 0,
        )
        st.caption("Volume × density × price per kg → estimated raw material cost.")

final_query = user_query
if alt_material != "None":
    final_query = f"I am currently using {alt_material}. Find a better alternative. Requirements: {user_query}"

# Step 2 — Constraints (Advanced only)
if is_advanced:
    with st.container(border=True):
        st.markdown('<div id="tour-step-2-anchor"></div>', unsafe_allow_html=True)
        if st.session_state.get("tour_active") and st.session_state.get("tour_step") == 2:
            render_tour_banner(
                2, 3, 
                "Physical Constraints", 
                "In Advanced mode, you can filter candidates using physical sliders (like Yield Strength, Fatigue Strength, and Embodied Carbon) and compliance checkmarks (like Bio-compatible or Food-grade).",
                "tour_s2"
            )
        section_header("2", "Physical constraints", "Narrow the database before AI ranking.")
        filtered_df, filter_vals = render_filters(df_display, mode, unit_system, settings)
        with st.expander("Candidate database", expanded=False):
            st.caption("Edit values for what-if scenarios — changes apply to this session only.")
            filtered_df = st.data_editor(filtered_df, hide_index=True, use_container_width=True)
else:
    filtered_df = df_display
    filter_vals = {}

save_settings({
    "api_key": api_key,
    "model_name": model_name,
    "mode": mode,
    "unit_system": unit_system,
    "part_volume": part_volume,
    "cost_source": cost_source,
    **filter_vals,
})

# Search readiness
can_search = True
if not api_key:
    render_status_banner("Add your Gemini API key in the sidebar to run analysis.", "warning")
    can_search = False
elif not user_query.strip():
    render_status_banner("Describe your project requirements to continue.", "info")
    can_search = False
elif filtered_df.empty:
    render_status_banner("No materials match your filters. Relax constraints in Step 2.", "error")
    if api_key and st.button("Why did my filters fail?"):
        with st.spinner("Analyzing constraints..."):
            try:
                client = genai.Client(api_key=api_key)
                explanation = explain_filter_failure(client, filter_vals, model_name)
                st.info(explanation)
            except Exception as e:
                st.error(f"Could not explain failure: {e}")
    can_search = False

if st.button("Find materials", type="primary", disabled=not can_search, use_container_width=True):
    st.session_state["last_edited_df"] = filtered_df
    cost_instruction = ""
    if cost_source == "Use AI Market Estimation":
        cost_instruction = "You MUST also estimate the current market price of this material per Kg in INR."

    with st.status("Analyzing materials...", expanded=True) as status:
        try:
            client = genai.Client(api_key=api_key)
            db_string = filtered_df.to_string(index=False)

            if not is_advanced:
                status.write("Querying AI for best match...")
                ai_data = get_single_recommendation(client, db_string, final_query, model_name, cost_instruction)
                row = match_material(df_display, ai_data.get("MaterialName"))
                if row is None:
                    st.error(f"AI suggested '{ai_data.get('MaterialName')}', which wasn't found in the database.")
                else:
                    exact_name = row["Material Name"]
                    result = compute_part_cost(row, part_volume, cost_source, ai_data)
                    carbon_per_kg = float(row.get("Embodied Carbon (kg CO2/kg)", 0.0))
                    total_carbon_kg = result["mass_kg"] * carbon_per_kg
                    st.session_state["lite_result"] = {
                        "exact_name": exact_name,
                        "confidence": ai_data.get("Confidence", 0),
                        "reasoning": ai_data.get("Reasoning", "No reasoning provided."),
                        "result": result,
                        "part_volume": part_volume,
                        "properties": row.to_dict(),
                        "total_carbon_kg": total_carbon_kg,
                        "carbon_per_kg": carbon_per_kg,
                    }
                    st.session_state["last_query"] = final_query
                    log_search(final_query, [ai_data], [result["total_cost"]], part_volume, unit_system, get_currency_symbol(unit_system))
                    status.update(label="Analysis complete", state="complete")
            else:
                status.write("Ranking top candidates...")
                results_list = get_top3_recommendations(client, db_string, final_query, model_name, cost_instruction)
                processed, rec_names, cost_values = [], [], []

                for ai_data in results_list:
                    row = match_material(df_display, ai_data.get("MaterialName"))
                    if row is None:
                        continue
                    exact_name = row["Material Name"]
                    result = compute_part_cost(row, part_volume, cost_source, ai_data)
                    carbon_per_kg = float(row.get("Embodied Carbon (kg CO2/kg)", 0.0))
                    total_carbon_kg = result["mass_kg"] * carbon_per_kg
                    rec_names.append(exact_name)
                    cost_values.append(result["total_cost"])
                    processed.append({
                        "exact_name": exact_name,
                        "confidence": ai_data.get("Confidence", 0),
                        "reasoning": ai_data.get("Reasoning", ""),
                        "pros": ai_data.get("Pros", []),
                        "cons": ai_data.get("Cons", []),
                        "result": result,
                        "part_volume": part_volume,
                        "properties": row.to_dict(),
                        "total_carbon_kg": total_carbon_kg,
                        "carbon_per_kg": carbon_per_kg,
                    })

                if not processed:
                    st.error("Could not match AI recommendations to the database. Try again or relax filters.")
                else:
                    st.session_state["advanced_results"] = processed
                    st.session_state["last_recommended"] = rec_names
                    st.session_state["last_query"] = final_query
                    summary = "; ".join(f"{r['exact_name']} ({r['confidence']}%)" for r in processed)
                    st.session_state["chat_history"] = [
                        {"role": "user", "text": final_query},
                        {"role": "model", "text": f"Top materials: {summary}. Ask follow-up questions about trade-offs, manufacturing, or alternatives."},
                    ]
                    st.session_state["chat_context"] = f"Current Material Database Context:\n{db_string}\nCost Source: {cost_source}\nCalculated Costs: {cost_values}"
                    log_search(final_query, results_list, cost_values, part_volume, unit_system, get_currency_symbol(unit_system))
                    status.update(label="Analysis complete", state="complete")

        except Exception as e:
            status.update(label="Analysis failed", state="error")
            err_str = str(e)
            if "503" in err_str or "UNAVAILABLE" in err_str:
                render_status_banner("AI service is busy (503). Wait a moment and retry.", "error")
            elif "404" in err_str or "NOT_FOUND" in err_str:
                render_status_banner(f"Model '{model_name}' is unavailable. Try another model in Settings.", "error")
            else:
                render_status_banner(f"Error: {e}", "error")

# Step 3 — Results
step_num = "2" if not is_advanced else "3"
has_lite = not is_advanced and "lite_result" in st.session_state
has_advanced = is_advanced and st.session_state.get("advanced_results")

with st.container(border=True):
    anchor_num = "3" if is_advanced else "2"
    st.markdown(f'<div id="tour-step-{anchor_num}-anchor"></div>', unsafe_allow_html=True)
    if st.session_state.get("tour_active") and st.session_state.get("tour_step") == (3 if is_advanced else 2):
        total = 3 if is_advanced else 2
        desc = "Review AI recommendations, download PDF reports, and export 3D CAD STEP files. You can also view interactive radar/scatter/heatmap visuals and ask follow-up questions in the chat panel below." if is_advanced else "Review the recommended material, download the engineering PDF report, and export the 3D CAD STEP model."
        render_tour_banner(
            total, total, 
            "Analysis & Exports", 
            desc,
            "tour_s3"
        )
    section_header(step_num, "Results", "Recommendations, exports, and comparisons.")

    if has_lite:
        render_lite_results(st.session_state["lite_result"], get_currency_symbol(unit_system), unit_system)
    elif has_advanced:
        render_advanced_results(
            st.session_state["advanced_results"],
            st.session_state.get("last_recommended", []),
            df_display, unit_system, api_key, model_name,
        )
        
        st.divider()
        c_left, c_mid, c_right = st.columns([1, 4, 1])
        with c_mid:
            st.markdown("##### Ask follow-ups")
            st.caption("Chat about trade-offs, processing, or alternatives.")
            if st.session_state.get("chat_history") and api_key:
                chat_box = st.container(height=450)
                with chat_box:
                    # Render chat history
                    for msg in st.session_state["chat_history"]:
                        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                            st.markdown(msg["text"])
                    
                    # Trigger assistant response if the last message is from the user
                    if st.session_state["chat_history"][-1]["role"] == "user":
                        with st.chat_message("assistant"):
                            with st.spinner("Thinking..."):
                                try:
                                    client = genai.Client(api_key=api_key)
                                    ctx = st.session_state.get("chat_context", "")
                                    # Send historical list and new question separately
                                    answer = chat_followup(
                                        client, 
                                        st.session_state["chat_history"][:-1], 
                                        st.session_state["chat_history"][-1]["text"], 
                                        model_name, 
                                        ctx
                                    )
                                    st.markdown(answer)
                                    st.session_state["chat_history"].append({"role": "model", "text": answer})
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                    
                    # Chat input box always below scrollable content inside container
                    followup = st.chat_input("Ask about materials...", key="chat_followup_input")
                    if followup:
                        st.session_state["chat_history"].append({"role": "user", "text": followup})
                        st.rerun()
            else:
                render_empty_state("", "Chat unavailable", "Run an analysis first to enable follow-up questions.")
    else:
        render_empty_state(
            "",
            "No results yet",
            "Complete Step 1, then click Find materials to get AI-powered recommendations.",
        )

render_footer()
