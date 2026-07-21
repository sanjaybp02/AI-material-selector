"""Shared UI theme, CSS, and reusable Streamlit presentation helpers."""

import streamlit as st

# ── Design tokens (SaaS theme) ─────────────────────────────────────────
ACCENT = "#58a6ff"  # Enterprise Blue
ACCENT_DIM = "rgba(56, 139, 253, 0.1)"
ACCENT_BORDER = "#30363d"
SURFACE = "#161b22"
SURFACE_LIGHT = "#f6f8fa"
TEXT_MUTED = "#8b949e"
SUCCESS = "#2ea44f"
WARNING = "#d29922"
DANGER = "#f85149"


def inject_theme():
    """Inject global CSS for the application."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {{
    --accent: {ACCENT};
    --accent-dim: {ACCENT_DIM};
    --accent-border: {ACCENT_BORDER};
    --surface: {SURFACE};
    --text-muted: {TEXT_MUTED};
    --success: {SUCCESS};
    --radius: 6px;
}}

.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1300px !important;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* ── Cards & containers ── */
div[data-testid="stExpander"],
div[data-testid="stMetric"],
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--accent-border) !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease !important;
}}

div[data-testid="stExpander"]:hover,
div[data-testid="stMetric"]:hover {{
    border-color: #8b949e !important;
}}

@media (prefers-color-scheme: light) {{
    div[data-testid="stExpander"],
    div[data-testid="stMetric"],
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {SURFACE_LIGHT} !important;
        border: 1px solid #e1e4e8 !important;
    }}
    div[data-testid="stExpander"]:hover,
    div[data-testid="stMetric"]:hover {{
        border-color: #959da5 !important;
    }}
}}

/* ── Buttons ── */
button[kind="primary"] {{
    background: #1f6feb !important;
    border: 1px solid #388bfd !important;
    border-radius: var(--radius) !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    transition: background 0.2s ease !important;
    box-shadow: none !important;
    text-transform: none !important;
    letter-spacing: normal !important;
}}
button[kind="primary"]:hover:not(:disabled) {{
    background: #388bfd !important;
    border-color: #58a6ff !important;
    box-shadow: none !important;
    transform: none !important;
}}
button[kind="primary"]:disabled {{
    opacity: 0.5 !important;
    background: #1f6feb !important;
}}

button[kind="secondary"] {{
    border-radius: var(--radius) !important;
    font-size: 0.875rem !important;
}}



/* ── Tabs ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 8px;
    border-bottom: 1px solid var(--accent-border);
    padding-bottom: 0;
}}
div[data-testid="stTabs"] button {{
    border-radius: var(--radius) var(--radius) 0 0 !important;
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    padding: 8px 16px !important;
}}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
    background: var(--accent-dim) !important;
    border-bottom: 2px solid var(--accent) !important;
    color: var(--accent) !important;
}}

/* ── Sidebar visually matched ── */
section[data-testid="stSidebar"] {{
    background: var(--surface) !important;
    border-right: 1px solid var(--accent-border) !important;
}}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {{
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: #f0f6fc;
}}
@media (prefers-color-scheme: light) {{
    section[data-testid="stSidebar"] {{
        background: {SURFACE_LIGHT} !important;
        border-right: 1px solid #e1e4e8 !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: #24292e;
    }}
}}

/* ── Inputs ── */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {{
    border-radius: var(--radius) !important;
    font-size: 0.9rem !important;
}}
div[data-testid="stRadio"] label {{
    font-size: 0.875rem !important;
}}

/* ── Chat ── */
div[data-testid="stChatMessage"] {{
    border-radius: var(--radius) !important;
    border: 1px solid #21262d !important;
}}

/* ── Custom components ── */
.hero-title {{
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.25;
    color: #f0f6fc;
}}
.hero-subtitle {{
    margin: 8px 0 0 0;
    font-size: 0.95rem;
    color: var(--text-muted);
    font-weight: 400;
    max-width: 700px;
}}
.section-label {{
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 2px;
}}
.section-title {{
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--accent-border);
    color: #f0f6fc;
}}
.template-pill {{
    display: inline-block;
    padding: 6px 12px;
    margin: 4px 6px 4px 0;
    border-radius: 12px;
    border: 1px solid var(--accent-border);
    background: var(--accent-dim);
    font-size: 0.8rem;
    font-weight: 500;
    cursor: default;
}}
.status-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}}
.status-dot.online {{ background: {SUCCESS}; }}
.status-dot.offline {{ background: {DANGER}; }}

.confidence-bar {{
    height: 5px;
    border-radius: 3px;
    background: #21262d;
    overflow: hidden;
    margin-top: 6px;
}}
.confidence-fill {{
    height: 100%;
    border-radius: 3px;
    background: var(--accent);
}}
.pro-tag {{
    display: inline-block;
    padding: 2px 8px;
    margin: 2px 4px 2px 0;
    border-radius: 3px;
    font-size: 0.75rem;
    background: rgba(56, 139, 253, 0.15);
    border: 1px solid rgba(56, 139, 253, 0.3);
    color: #58a6ff;
}}
.con-tag {{
    display: inline-block;
    padding: 2px 8px;
    margin: 2px 4px 2px 0;
    border-radius: 3px;
    font-size: 0.75rem;
    background: rgba(240, 139, 25, 0.1);
    border: 1px solid rgba(240, 139, 25, 0.25);
    color: #f08c1a;
}}
.empty-state {{
    text-align: center;
    padding: 32px 16px;
    color: var(--text-muted);
}}
.filter-chip {{
    display: inline-block;
    padding: 3px 8px;
    margin: 2px 4px 2px 0;
    border-radius: 4px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    background: #161b22;
    border: 1px solid var(--accent-border);
    color: #c9d1d9;
}}
.app-footer {{
    position: fixed !important;
    bottom: 3.2rem !important;
    right: 1.5rem !important;
    font-size: 0.75rem !important;
    color: {TEXT_MUTED} !important;
    background: transparent !important;
    z-index: 1000 !important;
    pointer-events: none !important;
    text-align: right !important;
}}

/* ── Tour highlights & spotlight ── */
.tour-backdrop {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.75) !important;
    z-index: 999998 !important;
    pointer-events: none;
    transition: opacity 0.3s ease;
}}

/* Raise active container and its layout ancestors above the backdrop */
div[data-testid="stVerticalBlock"]:has(.tour-banner-active),
div[class*="stColumn"]:has(.tour-banner-active) {{
    position: relative !important;
    z-index: 999999 !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.tour-banner-active) {{
    position: relative !important;
    z-index: 999999 !important;
    border: 2px solid #2ea44f !important;
    box-shadow: 0 0 35px rgba(46, 164, 79, 0.6) !important;
    background: #161b22 !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease, z-index 0.3s ease !important;
}}

@media (prefers-color-scheme: light) {{
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tour-banner-active) {{
        background: #ffffff !important;
        box-shadow: 0 0 35px rgba(46, 164, 79, 0.4) !important;
    }}
}}

/* ── Mechanical Loader Override (Rotating Gear) ── */
div[data-testid="stSpinner"] [role="progressbar"],
div[data-testid="stSpinner"] svg,
div[data-testid="stStatusWidget"] svg[class*="Spinner"],
div[data-testid="stStatusWidget"] div[class*="spinner"] {{
    display: none !important;
}}
div[data-testid="stSpinner"] > div,
div[data-testid="stStatusWidget"] > summary {{
    display: flex;
    align-items: center;
}}
div[data-testid="stSpinner"] > div::before,
div[data-testid="stStatusWidget"] > summary::before {{
    content: "⚙";
    font-size: 1.8rem;
    color: var(--accent);
    display: inline-block;
    animation: spin-gear 2s linear infinite;
    margin-right: 12px;
}}

/* ── Mechanical button loading overrides ── */
button:has(svg[class*="Spinner"])::before,
button:has(div[class*="spinner"])::before {{
    content: "⚙";
    font-size: 1rem;
    color: #ffffff;
    display: inline-block;
    animation: spin-gear 1.5s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
}}
button:has(svg[class*="Spinner"]) svg,
button:has(div[class*="spinner"]) div {{
    display: none !important;
}}

@keyframes spin-gear {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}
/* Keep header for sidebar toggle, but make background transparent and hide deploy/options menu */
[data-testid="stHeader"] {{
    background: transparent !important;
}}
[data-testid="stDecoration"] {{
    display: none !important;
}}
.stAppDeployButton, [data-testid="stAppDeployButton"], [data-testid="stHeaderActionElements"], #MainMenu {{
    display: none !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_hero(mode_label: str):
    st.markdown(
        f"""
<div style="margin-bottom: 24px;">
    <p class="section-label">Engineering Material Intelligence</p>
    <h1 class="hero-title">
        Material Selector
    </h1>
    <p class="hero-subtitle">
        Input requirements, configure constraints, and review ranked recommendations
        with cost estimation, carbon footprint metrics, and interactive telemetry.
        Active Mode: {mode_label}
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


def section_header(step: str, title: str, subtitle: str = ""):
    sub = f'<p style="margin: 2px 0 0 0; font-size: 0.8rem; color: {TEXT_MUTED};">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
<div style="margin-bottom: 16px;">
    <p class="section-label">Step {step}</p>
    <h3 class="section-title" style="margin-bottom: 0; padding-bottom: 6px;">{title}</h3>
    {sub}
</div>
""",
        unsafe_allow_html=True,
    )


def render_status_banner(message: str, kind: str = "info"):
    colors = {
        "info": ACCENT,
        "success": SUCCESS,
        "warning": WARNING,
        "error": DANGER,
    }
    color = colors.get(kind, ACCENT)
    st.markdown(
        f"""
<div style="
    padding: 10px 16px; margin-bottom: 16px;
    border-radius: var(--radius); border-left: 3px solid {color};
    background: #161b22;
    font-size: 0.875rem;
    color: #c9d1d9;
">
    <strong>{kind.upper()}:</strong> {message}
</div>
""",
        unsafe_allow_html=True,
    )


def render_empty_state(icon: str, title: str, body: str):
    """Render empty state card (ignoring icon parameter to avoid emojis)."""
    st.markdown(
        f"""
<div class="empty-state">
    <p style="font-size: 0.95rem; font-weight: 600; color: #c9d1d9; margin-bottom: 6px;">{title}</p>
    <p style="font-size: 0.85rem; margin: 0;">{body}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_confidence_bar(confidence: int):
    pct = max(0, min(100, int(confidence)))
    st.markdown(
        f"""
<div style="margin: 4px 0;">
    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: {TEXT_MUTED};">
        <span>Confidence</span><span style="color: var(--accent); font-weight: 600;">{pct}%</span>
    </div>
    <div class="confidence-bar"><div class="confidence-fill" style="width: {pct}%;"></div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_pros_cons(pros: list, cons: list):
    if pros:
        tags = "".join(f'<span class="pro-tag">{p}</span>' for p in pros)
        st.markdown(f"**Advantages**<br>{tags}", unsafe_allow_html=True)
    if cons:
        tags = "".join(f'<span class="con-tag">{c}</span>' for c in cons)
        st.markdown(f"<br>**Trade-offs**<br>{tags}", unsafe_allow_html=True)


def render_filter_summary(chips: list[str]):
    if not chips:
        return
    html = "".join(f'<span class="filter-chip">{c}</span>' for c in chips)
    st.markdown(
        f'<div style="margin: 8px 0 12px 0;"><span style="font-size:0.8rem;color:{TEXT_MUTED};margin-right:8px;">Active filters:</span>{html}</div>',
        unsafe_allow_html=True,
    )


def render_progress_tracker(steps: list[tuple[str, bool]]):
    """Render a vertical progress tracker without emojis or custom fonts."""
    lines = []
    for i, (label, done) in enumerate(steps):
        color = ACCENT if done else TEXT_MUTED
        icon = "Done" if done else "Pending"
        lines.append(
            f'<div style="font-size:0.8rem; color:{color}; padding: 2px 0;">'
            f'[{icon}] {label}</div>'
        )
    st.markdown("".join(lines), unsafe_allow_html=True)


def render_sidebar_status(api_connected: bool, material_count: int):
    dot_class = "online" if api_connected else "offline"
    status_text = "API Connected" if api_connected else "API Key Required"
    st.markdown(
        f"""
<div style="padding: 12px; border-radius: var(--radius); border: 1px solid var(--accent-border); margin-bottom: 16px; background: #161b22;">
    <span class="status-dot {dot_class}"></span>
    <span style="font-size: 0.85rem; font-weight: 600; color: #f0f6fc;">{status_text}</span>
    <p style="margin: 4px 0 0 0; font-size: 0.75rem; color: {TEXT_MUTED};">
        {material_count} materials in database
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        '<div class="app-footer">made with ❤️ by sanjay_bp</div>',
        unsafe_allow_html=True,
    )


def render_tour_banner(step_num: int, total_steps: int, title: str, text: str, key_prefix: str):
    """Render a premium green-bordered guided tour card with compact controls and auto-scroll."""
    # Render scroll trigger using the Streamlit HTML component to bypass Markdown security sanitization
    js_code = f"""
    <script>
        (function() {{
            var attempts = 0;
            var interval = setInterval(function() {{
                attempts++;
                var doc = document;
                try {{
                    if (window.parent && window.parent.document) doc = window.parent.document;
                }} catch(e) {{}}
                try {{
                    if (window.top && window.top.document) doc = window.top.document;
                }} catch(e) {{}}
                
                var el = doc.getElementById('tour-step-{step_num}-anchor');
                if (el) {{
                    console.log('Found tour anchor tour-step-{step_num}-anchor on attempt ' + attempts);
                    el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    clearInterval(interval);
                }} else if (attempts >= 30) {{
                    console.log('Failed to find tour anchor after 30 attempts');
                    clearInterval(interval);
                }}
            }}, 100);
        }})();
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)
    
    html_content = f"""
<div class="tour-banner-active" style="
    border: 2px solid #2ea44f; 
    background: rgba(46, 164, 79, 0.05); 
    padding: 16px; 
    border-radius: 6px; 
    margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(46, 164, 79, 0.15);
">
    <div style="font-size: 0.72rem; font-weight: 700; color: #2ea44f; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-family: 'Inter', sans-serif;">
        Guide Tour · Step {step_num} of {total_steps}
    </div>
    <h4 style="margin: 0 0 6px 0; color: #2ea44f; font-weight: 600; font-family: 'Inter', sans-serif;">{title}</h4>
    <p style="margin: 0; font-size: 0.875rem; color: var(--text-muted); line-height: 1.4; font-family: 'Inter', sans-serif;">{text}</p>
</div>"""
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Compact navigation controls
    btn_cols = st.columns([0.8, 0.8, 1, 4])
    with btn_cols[0]:
        if step_num > 1:
            if st.button("Back", key=f"{key_prefix}_back", use_container_width=True):
                st.session_state["tour_step"] -= 1
                st.rerun()
    with btn_cols[1]:
        label = "Finish" if step_num == total_steps else "Next"
        if st.button(label, key=f"{key_prefix}_next", type="primary", use_container_width=True):
            if step_num == total_steps:
                st.session_state["tour_active"] = False
                st.session_state["tour_step"] = 1
            else:
                st.session_state["tour_step"] += 1
            st.rerun()
    with btn_cols[2]:
        if st.button("Skip", key=f"{key_prefix}_skip", use_container_width=True):
            st.session_state["tour_active"] = False
            st.session_state["tour_step"] = 1
            st.rerun()


def inject_clarity():
    """Inject Microsoft Clarity tracking script with dual local and parent frame support."""
    js_code = """
    <script type="text/javascript">
        (function(c,l,a,r,i,t,y){
            c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
            
            try {
                if (window.parent && window.parent.document) {
                    var p_doc = window.parent.document;
                    if (!p_doc.getElementById('clarity-parent-script')) {
                        var p_t = p_doc.createElement(r);
                        p_t.id = 'clarity-parent-script';
                        p_t.async = 1;
                        p_t.src = "https://www.clarity.ms/tag/"+i;
                        var p_y = p_doc.getElementsByTagName(r)[0];
                        if (p_y) p_y.parentNode.insertBefore(p_t, p_y);
                        else p_doc.head.appendChild(p_t);
                    }
                }
            } catch(e) {
                console.log("Clarity parent context injection skipped:", e);
            }
        })(window, document, "clarity", "script", "xpyroe7f7m");
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

