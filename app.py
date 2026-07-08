import streamlit as st
import pandas as pd
import os
import json

from google import genai

from modules.data_loader import (
    load_data, convert_units, get_yield_col, get_temp_col, get_cost_col,
    get_density_col, get_currency_symbol, get_volume_unit, get_mass_unit,
)
from modules.filters import render_filters
from modules.cost_engine import fetch_live_metal_price, calculate_part_cost
from modules.ai_engine import get_single_recommendation, get_top3_recommendations, chat_followup
from modules.charts import radar_chart, scatter_plot, property_heatmap
from modules.pdf_report import create_pdf
from modules.history import init_history, log_search, render_history_table
from modules.templates import load_templates, save_custom_template, delete_custom_template

# ──────────────────────────── Settings I/O ───────────────────────────
SETTINGS_FILE = "settings.json"

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

settings = load_settings()

# ──────────────────────────── Page Config ────────────────────────────
api_key_saved = bool(settings.get("api_key", ""))
app_mode = settings.get("mode", "⚡ Lite")
initial_sidebar = "collapsed" if (app_mode == "⚡ Lite" and api_key_saved) else "expanded"

st.set_page_config(page_title="AI Material Selector", page_icon="⚙️", layout="wide", initial_sidebar_state=initial_sidebar)

# Industrial / Tactical CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* Push content up to utilize top space */
.block-container {
    padding-top: 2rem !important;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hardened Containers */
div[data-testid="stExpander"], div[data-testid="stMetric"], div.template-card, div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(30, 35, 40, 0.5) !important;
    backdrop-filter: blur(8px) !important;
    border-radius: 4px !important;
    border: 1px solid rgba(0, 255, 255, 0.15) !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
}

/* Hover Transitions for Internal UI */
div[data-testid="stExpander"]:hover, div[data-testid="stMetric"]:hover {
    border-color: #00ffff !important;
    box-shadow: 0 6px 15px rgba(0, 255, 255, 0.15) !important;
    transform: translateY(-2px);
}

/* Dark mode adaptability fallback for light mode */
@media (prefers-color-scheme: light) {
    div[data-testid="stExpander"], div[data-testid="stMetric"], div.template-card, div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(240, 245, 250, 0.8) !important;
        border: 1px solid rgba(0, 150, 255, 0.2) !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stExpander"]:hover, div[data-testid="stMetric"]:hover {
        border-color: #0096ff !important;
        box-shadow: 0 6px 15px rgba(0, 150, 255, 0.2) !important;
    }
}

/* Tactical Primary Button */
button[kind="primary"] {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%) !important;
    border: 1px solid rgba(0, 255, 255, 0.3) !important;
    border-radius: 2px !important;
    color: #00ffff !important;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700 !important;
    letter-spacing: 1px;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%) !important;
    border-color: #00ffff !important;
    box-shadow: 0 0 10px rgba(0, 255, 255, 0.4) !important;
}

/* Tactical Tabs */
div[data-testid="stTabs"] button {
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    font-size: 0.85rem;
    padding: 10px 15px;
    margin-right: 5px;
    transition: background 0.3s ease !important;
}
div[data-testid="stTabs"] button:hover {
    background: rgba(0, 255, 255, 0.05) !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: rgba(0, 255, 255, 0.1) !important;
    border-bottom: 2px solid #00ffff !important;
    color: #00ffff !important;
}

/* Make Progress Tracker Static (Sticky) */
div[data-testid="column"]:has(#sticky-tracker-anchor) {
    position: -webkit-sticky !important;
    position: sticky !important;
    top: 3rem !important;
    z-index: 10;
    align-self: flex-start;
}

.custom-footer {
    position: fixed;
    bottom: 10px;
    right: 20px;
    color: #888;
    font-size: 14px;
    font-family: 'JetBrains Mono', monospace;
    z-index: 100;
}
</style>
<div class="custom-footer">SYSTEM ONLINE // sanjay bp</div>
""", unsafe_allow_html=True)

def section_header(num, title):
    st.markdown(f"""
    <div style='border-bottom: 1px solid rgba(0, 255, 255, 0.2); padding-bottom: 8px; margin-bottom: 20px;'>
        <h4 style='margin: 0; font-family: "JetBrains Mono", monospace; text-transform: uppercase; letter-spacing: 1.5px; color: #00ffff;'>
            <span style='opacity: 0.5;'>[ {num} ]</span> {title}
        </h4>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────── Dialogs ──────────────────────────────
@st.dialog("➕ CREATE CUSTOM TEMPLATE")
def create_template_dialog():
    st.write("Register a new engineering prompt vector.")
    t_name = st.text_input("Designation", placeholder="e.g. MK-IV Chassis")
    t_desc = st.text_input("Parameters (Hover Hint)", placeholder="e.g. High tensile, low thermal expansion.")
    t_prompt = st.text_area("Directive Prompt", placeholder="I require a material that...")
    if st.button("EXECUTE SAVE", type="primary"):
        if t_name and t_prompt:
            save_custom_template(t_name, t_desc, t_prompt)
            st.rerun()
        else:
            st.error("Designation and Directive are mandatory.")

# ──────────────────────────── Minimal Sidebar ────────────────────────
with st.sidebar:
    st.header("⚙️ SYSTEM SETTINGS")

    api_key = st.text_input("🔑 Gemini API Key", type="password",
                            value=settings.get("api_key", ""),
                            help="Provide valid authentication token")

    model_name = st.selectbox(
        "🤖 Inference Engine",
        [
            "gemini-flash-latest", "gemini-pro-latest",
            "gemini-2.5-flash", "gemini-2.5-pro",
            "gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview"
        ],
        index=0 if settings.get("model_name", "gemini-flash-latest") == "gemini-flash-latest" else
              (["gemini-flash-latest", "gemini-pro-latest", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview"].index(settings.get("model_name", "gemini-flash-latest"))
               if settings.get("model_name", "gemini-flash-latest") in ["gemini-flash-latest", "gemini-pro-latest", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview"] else 0),
        help="Select logic processing unit."
    )

    st.divider()

    mode = st.radio(
        "Operational Mode",
        ["⚡ Lite", "🔬 Normal"],
        index=0 if settings.get("mode", "⚡ Lite") == "⚡ Lite" else 1,
        help="Lite: Fast single output.\nNormal: Multi-vector analysis."
    )

    if mode == "🔬 Normal":
        st.divider()
        unit_system = st.radio("📐 Metrics", ["Metric", "Imperial"], horizontal=True,
                               index=0 if settings.get("unit_system", "Metric") == "Metric" else 1)
    else:
        unit_system = "Metric"

is_normal = mode == "🔬 Normal"

# ──────────────────────────── Title ──────────────────────────────────
st.markdown("""
<div style="padding: 0 0 20px 0; margin-bottom: 30px;">
    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;">
        <span style="color: #00ffff;">//</span> MATERIAL <span style="font-weight: 300;">SELECTOR</span>
    </h1>
    <p style="margin: 5px 0 0 0; font-size: 0.95rem; color: #888; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 2px;">
        Tactical Engineering Analysis & Constraints Engine
    </p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────── Load Data ──────────────────────────────
df_raw = load_data()
df_display = convert_units(df_raw, unit_system)
init_history()

app_col, tracker_col = st.columns([4, 1], gap="large")

with app_col:
    # ═══════════════════════════════════════════════════════════════════════
    #  STEP ① — Define Your Requirements
    # ═══════════════════════════════════════════════════════════════════════
    with st.container(border=True):
        section_header("01", "REQUIREMENTS DEFINITION")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("##### 🎯 Quick Vectors")
            templates = load_templates()
            
            t_cols = st.columns(3)
            for i, t in enumerate(templates):
                with t_cols[i % 3]:
                    if st.button(t["name"], help=t.get("description", ""), use_container_width=True):
                        st.session_state["active_prompt"] = t["prompt"]
                    
                    if t.get("is_custom"):
                        if st.button("🗑️ DELETE", key=f"del_{t['name']}", help="Purge Custom Template"):
                            delete_custom_template(t["name"])
                            st.rerun()
                            
            if st.button("➕ NEW VECTOR", use_container_width=True):
                create_template_dialog()
                
            if is_normal:
                st.markdown("<br>", unsafe_allow_html=True)
                alt_material = st.selectbox("🔄 Target Replacement (Optional)", options=["None"] + df_display["Material Name"].tolist())
            else:
                alt_material = "None"
        
            user_query = st.text_area(
                "Mission / Project Directives:",
                value=st.session_state.get("active_prompt", ""),
                placeholder="e.g. Drone frame requiring high yield strength and minimal density...",
                height=120,
            )
        
        with col2:
            vol_unit = get_volume_unit(unit_system)
            part_volume = st.number_input(f"📐 Target Volume ({vol_unit})",
                                          min_value=1.0,
                                          value=float(settings.get("part_volume", 50.0)),
                                          step=10.0)
        
            cost_options = ["Use CSV Database Pricing", "Use AI Market Estimation", "Use Live MetalPrice API"]
            default_idx = cost_options.index(settings.get("cost_source", cost_options[0])) if settings.get("cost_source", cost_options[0]) in cost_options else 0
            cost_source = st.radio("💰 Pricing Model", options=cost_options, index=default_idx)

    # Establish final query early for tracker logic
    final_query = user_query
    if alt_material != "None":
        final_query = f"I am currently using {alt_material}. Please find a better alternative. Requirements: {user_query}"
    
    # ═══════════════════════════════════════════════════════════════════════
    #  STEP ② — Set Constraints (Normal Mode Only)
    # ═══════════════════════════════════════════════════════════════════════
    if is_normal:
        with st.container(border=True):
            section_header("02", "PHYSICAL CONSTRAINTS")
            filtered_df, filter_vals = render_filters(df_display, mode, unit_system, settings)
        
            st.markdown("#### 📝 Database Matrix")
            st.caption("Temporary override permitted for what-if scenarios.")
            filtered_df = st.data_editor(filtered_df, hide_index=True, use_container_width=True)
        
            if not filtered_df.empty:
                st.success(f"SYSTEM: {len(filtered_df)} viable materials identified.")
            else:
                st.error("SYSTEM: 0 materials viable. Relax constraints.")
    else:
        # For Lite mode, pass-through the unfiltered/raw data to avoid missing variable
        filtered_df = df_display
        filter_vals = {}
    
    # ═══════════════════════════════════════════════════════════════════════
    #  Persist Settings
    # ═══════════════════════════════════════════════════════════════════════
    save_settings({
        "api_key": api_key,
        "model_name": model_name,
        "mode": mode,
        "unit_system": unit_system,
        "part_volume": part_volume,
        "cost_source": cost_source,
        **filter_vals,
    })
    
    # ═══════════════════════════════════════════════════════════════════════
    #  FIND MATERIAL BUTTON
    # ═══════════════════════════════════════════════════════════════════════
    can_search = True
    help_msg = ""
    if not api_key:
        can_search = False
        help_msg = "AWAITING API AUTHENTICATION IN SIDEBAR."
    elif not user_query.strip():
        can_search = False
        help_msg = "AWAITING MISSION DIRECTIVE."
    elif filtered_df.empty:
        can_search = False
        help_msg = "CONSTRAINTS TOO STRICT. NO VIABLE ASSETS."
    
    if help_msg:
        st.info(help_msg)
    
    if st.button("INITIATE ANALYSIS", type="primary", disabled=not can_search):
        st.session_state["last_edited_df"] = filtered_df
    
        with st.status("PROCESSING DIRECTIVES...", expanded=True):
            try:
                client = genai.Client(api_key=api_key)
                db_string = filtered_df.to_string(index=False)
    
                cost_instruction = ""
                if cost_source == "Use AI Market Estimation":
                    cost_instruction = "You MUST also estimate the current market price of this material per Kg in INR."
    
                # ────── Lite: single recommendation ──────
                if not is_normal:
                    ai_data = get_single_recommendation(client, db_string, final_query, model_name, cost_instruction)
                    mat_name = ai_data.get("MaterialName")
                    confidence = ai_data.get("Confidence", 0)
                    reasoning = ai_data.get("Reasoning", "No reasoning provided.")
    
                    matched_row = df_raw[df_raw['Material Name'].str.contains(mat_name, case=False, na=False)]
                    if not matched_row.empty:
                        row = matched_row.iloc[0]
                        exact_name = row['Material Name']
    
                        if cost_source == "Use AI Market Estimation":
                            cpk = float(ai_data.get("EstimatedCostINR", 0))
                            result = calculate_part_cost(row, part_volume, cost_source, cpk)
                        elif cost_source == "Use Live MetalPrice API":
                            live_price, err = fetch_live_metal_price(exact_name)
                            if live_price is not None:
                                result = calculate_part_cost(row, part_volume, cost_source, live_price)
                            else:
                                st.warning(f"Live price unavailable: {err}. Falling back to CSV.")
                                result = calculate_part_cost(row, part_volume, cost_source)
                        else:
                            result = calculate_part_cost(row, part_volume, cost_source)
    
                        st.session_state["lite_result"] = {
                            "exact_name": exact_name,
                            "confidence": confidence,
                            "reasoning": reasoning,
                            "result": result,
                            "part_volume": part_volume,
                        }
                        st.session_state["last_query"] = final_query
                        log_search(final_query, [ai_data], [result['total_cost']], part_volume, unit_system)
                    else:
                        st.error(f"AI recommended '{mat_name}', but it wasn't found in the database!")
    
                # ────── Normal: top 3 ──────
                else:
                    results_list = get_top3_recommendations(client, db_string, final_query, model_name, cost_instruction)
    
                    recommended_names = []
                    cost_values = []
                    processed_results = []
    
                    for rank, ai_data in enumerate(results_list):
                        mat_name = ai_data.get("MaterialName", "Unknown")
                        matched_row = df_raw[df_raw['Material Name'].str.contains(mat_name, case=False, na=False)]
                        if matched_row.empty:
                            continue
    
                        row = matched_row.iloc[0]
                        exact_name = row['Material Name']
                        recommended_names.append(exact_name)
    
                        if cost_source == "Use AI Market Estimation":
                            cpk = float(ai_data.get("EstimatedCostINR", 0))
                            result = calculate_part_cost(row, part_volume, cost_source, cpk)
                        elif cost_source == "Use Live MetalPrice API":
                            live_price, err = fetch_live_metal_price(exact_name)
                            if live_price is not None:
                                result = calculate_part_cost(row, part_volume, cost_source, live_price)
                            else:
                                result = calculate_part_cost(row, part_volume, cost_source)
                        else:
                            result = calculate_part_cost(row, part_volume, cost_source)
    
                        cost_values.append(result['total_cost'])
                        processed_results.append({
                            "exact_name": exact_name,
                            "confidence": ai_data.get("Confidence", 0),
                            "reasoning": ai_data.get("Reasoning", ""),
                            "pros": ai_data.get("Pros", []),
                            "cons": ai_data.get("Cons", []),
                            "result": result,
                            "part_volume": part_volume,
                        })
    
                    st.session_state["normal_results"] = processed_results
                    st.session_state["last_recommended"] = recommended_names
                    st.session_state["last_query"] = final_query
    
                    summary = "; ".join([f"{r['exact_name']} ({r['confidence']}%)" for r in processed_results])
                    st.session_state["chat_history"] = [
                        {"role": "user", "text": final_query},
                        {"role": "model", "text": f"Based on my analysis, the top materials are: {summary}. Feel free to ask follow-up questions."}
                    ]
    
                    if recommended_names:
                        log_search(final_query, results_list, cost_values, part_volume, unit_system)
    
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    st.error("🚨 SYSTEM BUSY (503): High traffic load on AI inference engine.")
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    st.error(f"🚨 UNAVAILABLE (404): The model '{model_name}' is restricted.")
                else:
                    st.error(f"CRITICAL ERROR: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    #  STEP ③ — Explore Results
    # ═══════════════════════════════════════════════════════════════════════
    if not is_normal and "lite_result" in st.session_state:
        with st.container(border=True):
            section_header( "02" if not is_normal else "03", "ANALYSIS RESULTS")
            r = st.session_state["lite_result"]
        
            st.success("ANALYSIS COMPLETE.")
        
            cA, cB, cC = st.columns(3)
            cA.metric("🏆 Target Material", r["exact_name"])
            cB.metric("🧠 Confidence", f"{r['confidence']}%")
            cC.metric(f"💰 Est. Part Cost ({r['result']['source_label']})",
                      f"₹{r['result']['total_cost']:.2f}",
                      delta=f"{r['result']['mass_kg']:.2f} kg", delta_color="off")
        
            st.markdown("**📝 Technical Reasoning**")
            st.info(r["reasoning"])
        
            pdf_bytes = create_pdf(r["exact_name"], r["confidence"], r["reasoning"],
                                   r["result"]["total_cost"], r["result"]["mass_kg"], r["part_volume"])
            st.download_button("📄 EXPORT DOSSIER (PDF)", data=pdf_bytes,
                               file_name="Material_Recommendation.pdf", mime="application/pdf")
    
    elif is_normal and "normal_results" in st.session_state and st.session_state["normal_results"]:
        with st.container(border=True):
            section_header("03", "ANALYSIS RESULTS")
        
            res_main_col, res_chat_col = st.columns([2, 1], gap="large")
            
            with res_main_col:
                tab_results, tab_charts, tab_compare, tab_history = st.tabs(
                    ["🏆 MATRIX", "📊 CHARTS", "🔀 COMPARE", "📜 LOGS"]
                )
        
            processed = st.session_state["normal_results"]
            rec_names = st.session_state.get("last_recommended", [])
        
            with tab_results:
                st.success(f"TOP {len(processed)} CANDIDATES IDENTIFIED")
                for rank, item in enumerate(processed):
                    medal = ["🥇", "🥈", "🥉"][rank] if rank < 3 else "▪️"
                    with st.expander(f"{medal} Rank {rank+1} — {item['exact_name']} ({item['confidence']}%)", expanded=(rank == 0)):
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Material", item["exact_name"])
                        m2.metric("Confidence", f"{item['confidence']}%")
                        m3.metric(f"Cost ({item['result']['source_label']})",
                                  f"₹{item['result']['total_cost']:.2f}",
                                  delta=f"{item['result']['mass_kg']:.2f} kg", delta_color="off")
        
                        st.markdown(f"**Reasoning:** {item['reasoning']}")
                        if item["pros"]:
                            st.markdown("**✅ Advantages:** " + " • ".join(item["pros"]))
                        if item["cons"]:
                            st.markdown("**⚠️ Drawbacks:** " + " • ".join(item["cons"]))
        
                        pdf_bytes = create_pdf(item["exact_name"], item["confidence"], item["reasoning"],
                                               item["result"]["total_cost"], item["result"]["mass_kg"], item["part_volume"])
                        st.download_button(f"📄 EXPORT DOSSIER — {item['exact_name']}", data=pdf_bytes,
                                           file_name=f"Report_{item['exact_name'].replace(' ', '_')}.pdf",
                                           mime="application/pdf", key=f"pdf_{rank}")
        
            with tab_charts:
                if rec_names:
                    chart_df = st.session_state.get("last_edited_df", df_display)
                    st.plotly_chart(radar_chart(chart_df, rec_names, unit_system))
        
                    sc1, sc2 = st.columns(2)
                    yield_c = get_yield_col(unit_system)
                    density_c = get_density_col(unit_system)
                    cost_c = get_cost_col(unit_system)
        
                    with sc1:
                        if yield_c in chart_df.columns and density_c in chart_df.columns:
                            st.plotly_chart(scatter_plot(chart_df, density_c, yield_c, rec_names))
                    with sc2:
                        if cost_c in chart_df.columns and "Machinability (1-10)" in chart_df.columns:
                            st.plotly_chart(scatter_plot(chart_df, cost_c, "Machinability (1-10)", rec_names))
        
                    with st.expander("🗺️ Property Heatmap"):
                        st.plotly_chart(property_heatmap(chart_df, unit_system))
                else:
                    st.info("Execute search to generate telemetry.")
        
            with tab_compare:
                chart_df = st.session_state.get("last_edited_df", df_display)
                compare_options = chart_df["Material Name"].tolist() if not chart_df.empty else []
                compare_selected = st.multiselect(
                    "Select assets for cross-examination:",
                    options=compare_options,
                    default=rec_names[:2] if len(rec_names) >= 2 else rec_names,
                    max_selections=4
                )
                if len(compare_selected) >= 2:
                    st.plotly_chart(radar_chart(chart_df, compare_selected, unit_system))
                elif compare_selected:
                    st.info("Select minimum 2 assets.")
                else:
                    st.info("Select assets from the registry.")
        
            with res_chat_col:
                st.markdown("#### 💬 ADVISORY LINK")
                if "chat_history" in st.session_state and api_key:
                    for msg in st.session_state["chat_history"]:
                        role = "user" if msg["role"] == "user" else "assistant"
                        with st.chat_message(role):
                            st.markdown(msg["text"])
        
                    followup = st.chat_input("Input query...")
                    if followup:
                        st.session_state["chat_history"].append({"role": "user", "text": followup})
                        with st.chat_message("user"):
                            st.markdown(followup)
        
                        with st.chat_message("assistant"):
                            with st.spinner("Processing..."):
                                try:
                                    client = genai.Client(api_key=api_key)
                                    answer = chat_followup(client, st.session_state["chat_history"], followup, model_name)
                                    st.markdown(answer)
                                    st.session_state["chat_history"].append({"role": "model", "text": answer})
                                except Exception as e:
                                    st.error(f"LINK FAILED: {e}")
                else:
                    st.info("Run search to establish link.")
        
            with tab_history:
                render_history_table()
    
    elif is_normal and ("normal_results" not in st.session_state or not st.session_state.get("normal_results")):
        with st.container(border=True):
            section_header("03", "ANALYSIS RESULTS")
            st.info("AWAITING INITIATION.")

# ──────────────────────────── Progress Tracker ───────────────────────
with tracker_col:
    st.markdown("<div id='sticky-tracker-anchor'></div>", unsafe_allow_html=True)
    section_header("TRK", "PROGRESS")
    
    # Calculate step status
    step1_done = bool(user_query.strip())
    step2_done = step1_done 
    
    # Check if the current query in the UI matches what the AI last analyzed
    current_search_active = False
    if "last_query" in st.session_state:
        if st.session_state["last_query"] == final_query:
            current_search_active = True
            
    step3_done = ("normal_results" in st.session_state or "lite_result" in st.session_state) and current_search_active
    
    def render_step(num, title, is_done):
        color = "#00ffff" if is_done else "#555"
        icon = "■" if is_done else "□"
        st.markdown(f"**<span style='color:{color}; font-family: \"JetBrains Mono\", monospace; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;'>{icon} STEP {num}: {title}</span>**", unsafe_allow_html=True)
        
    if is_normal:
        render_step(1, "REQUIREMENTS", step1_done)
        render_step(2, "CONSTRAINTS", step2_done)
        render_step(3, "ANALYSIS", step3_done)
        render_step(4, "RESULTS", step3_done)
    else:
        # Lite Mode Fix
        render_step(1, "REQUIREMENTS", step1_done)
        render_step(2, "ANALYSIS", step3_done)
        render_step(3, "RESULTS", step3_done)
