"""Shared UI theme, CSS, and reusable Streamlit presentation helpers.

Design system: single dark theme (see .streamlit/config.toml for the
matching native-widget palette). Every color used anywhere in this module
traces back to the token set below — no scattered magic hex values — so the
app reads as one deliberately designed surface rather than a patchwork.
Light-mode media queries were removed on purpose: the app was dark-first
from the start (charts, cards, sidebar all assumed a dark background), so a
partial light variant only produced a broken hybrid for light-OS visitors.
Committing to one polished theme beats half-supporting two.
"""

import base64

import streamlit as st

# ── Design tokens ───────────────────────────────────────────────────────
ACCENT = "#58a6ff"
ACCENT_STRONG = "#1f6feb"          # solid button fill
ACCENT_STRONG_HOVER = "#388bfd"
ACCENT_DIM = "rgba(56, 139, 253, 0.1)"
BORDER = "#30363d"                 # card/panel outline
BORDER_HOVER = "#484f58"
SURFACE = "#161b22"                # card / sidebar background
SURFACE_INSET = "#0d1117"          # recessed elements: page bg, chips, track fills
TEXT_HEADING = "#f0f6fc"
TEXT_BODY = "#c9d1d9"
TEXT_MUTED = "#8b949e"
SUCCESS = "#2ea44f"
WARNING = "#d29922"
DANGER = "#f85149"
RADIUS = "6px"
RADIUS_LG = "10px"

# Back-compat alias — SURFACE_LIGHT is no longer used (dark-only theme) but
# kept as a no-op alias in case another module still imports it.
SURFACE_LIGHT = SURFACE


def inject_theme():
    """Inject global CSS for the application."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {{
    --accent: {ACCENT};
    --accent-strong: {ACCENT_STRONG};
    --accent-strong-hover: {ACCENT_STRONG_HOVER};
    --accent-dim: {ACCENT_DIM};
    --border: {BORDER};
    --border-hover: {BORDER_HOVER};
    --surface: {SURFACE};
    --surface-inset: {SURFACE_INSET};
    --text-heading: {TEXT_HEADING};
    --text-body: {TEXT_BODY};
    --text-muted: {TEXT_MUTED};
    --success: {SUCCESS};
    --warning: {WARNING};
    --danger: {DANGER};
    --radius: {RADIUS};
    --radius-lg: {RADIUS_LG};
}}

.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1300px !important;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}
/* Streamlit injects its own per-component rules like
   ".st-emotion-cache-XXXX h1, h2, h3, ..." that target heading/text
   tags *directly* — confirmed by walking document.styleSheets and
   finding exactly this selector setting font-family to "Source Sans"
   (traced in-browser, not guessed). Those rules have no !important, but
   they still won over the block above because that block only sets
   font-family on elements whose *own* class contains "css" (the
   wrapper divs) — h1/p/span never match it directly, so they only
   inherited Inter from their parent, and a direct (even unimportant,
   even lower-specificity) rule on the element itself always beats an
   inherited value. Result: headings/captions/labels silently fell back
   to Source Sans while only directly-styled elements kept Inter — a
   visibly inconsistent mix of two fonts on the same page. Fixed by
   directly targeting every text-bearing tag with !important instead of
   relying on inheritance. */
[data-testid="stApp"] :is(h1, h2, h3, h4, h5, h6, p, span, div, label, li, a, td, th, button, textarea, input) {{
    font-family: 'Inter', sans-serif !important;
}}
code, pre, kbd, samp,
div[data-testid="stCodeBlock"] *,
[data-testid="stApp"] code, [data-testid="stApp"] pre {{
    font-family: 'JetBrains Mono', monospace !important;
}}

/* ── Cards & containers ── */
div[data-testid="stExpander"],
div[data-testid="stMetric"],
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: var(--border-hover) !important;
}}
/* Lift is scoped to the smaller card-like elements (metrics, expanders) —
   not the large Step 1/2/3 containers, where a hover-shift would feel
   twitchy since the mouse sits over them constantly while typing. */
div[data-testid="stExpander"]:hover,
div[data-testid="stMetric"]:hover {{
    border-color: var(--border-hover) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
    transform: translateY(-2px) !important;
}}

/* stMetric value: monospace for an instrument-panel feel on numeric readouts */
div[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace !important;
}}
div[data-testid="stMetric"] {{
    border-top: 2px solid var(--accent) !important;
}}

/* ── Custom scrollbar ── */
::-webkit-scrollbar {{
    width: 10px;
    height: 10px;
}}
::-webkit-scrollbar-track {{
    background: var(--surface-inset);
}}
::-webkit-scrollbar-thumb {{
    background: var(--border-hover);
    border-radius: 5px;
    border: 2px solid var(--surface-inset);
}}
::-webkit-scrollbar-thumb:hover {{
    background: var(--accent);
}}

/* ── Text selection ── */
::selection {{
    background: var(--accent-dim);
    color: var(--text-heading);
}}

/* ── Buttons ── */
button[kind="primary"] {{
    background: var(--accent-strong) !important;
    border: 1px solid var(--accent-strong-hover) !important;
    border-radius: var(--radius) !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease !important;
    box-shadow: none !important;
    text-transform: none !important;
    letter-spacing: normal !important;
}}
button[kind="primary"]:hover:not(:disabled) {{
    background: var(--accent-strong-hover) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 4px 12px rgba(56, 139, 253, 0.35) !important;
    transform: translateY(-1px) !important;
}}
button[kind="primary"]:active:not(:disabled) {{
    transform: translateY(0) !important;
    box-shadow: 0 1px 4px rgba(56, 139, 253, 0.3) !important;
}}
button[kind="primary"]:disabled {{
    opacity: 0.5 !important;
    background: var(--accent-strong) !important;
}}

button[kind="secondary"] {{
    border-radius: var(--radius) !important;
    font-size: 0.875rem !important;
}}

/* ── Tabs ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 8px;
    border-bottom: 1px solid var(--border);
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

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {{
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: var(--text-heading) !important;
}}

/* ── Inputs ── */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {{
    border-radius: var(--radius) !important;
    font-size: 0.9rem !important;
    transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
}}
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
}}
div[data-testid="stRadio"] label {{
    font-size: 0.875rem !important;
}}

/* Numeric readouts (slider value labels, number inputs) get the mono
   font for an instrument-panel feel consistent with stMetric values. */
div[data-testid="stSlider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-testid="stTickBarMax"],
div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"],
div[data-testid="stNumberInput"] input {{
    font-family: 'JetBrains Mono', monospace !important;
}}

/* ── Chat ── */
div[data-testid="stChatMessage"] {{
    border-radius: var(--radius) !important;
    border: 1px solid var(--surface-inset) !important;
}}

/* ── Dividers: a soft accent-tinted fade instead of a flat grey rule ── */
div[data-testid="stMarkdownContainer"] hr,
hr {{
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border-hover) 50%, transparent) !important;
    margin: 1.5rem 0 !important;
}}

/* ── Custom components ── */
.hero-wrap {{
    position: relative;
    margin-bottom: 24px;
    padding: 4px 0;
}}
.hero-wrap::before {{
    content: "";
    position: absolute;
    top: -40px;
    left: -60px;
    width: 340px;
    height: 220px;
    background: radial-gradient(circle, rgba(88, 166, 255, 0.14) 0%, rgba(88, 166, 255, 0) 70%);
    pointer-events: none;
    z-index: -1;
}}
.hero-title {{
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.25;
    color: var(--text-heading) !important;
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
    border-bottom: 1px solid var(--border);
    color: var(--text-heading) !important;
}}
.template-pill {{
    display: inline-block;
    padding: 6px 12px;
    margin: 4px 6px 4px 0;
    border-radius: 12px;
    border: 1px solid var(--border);
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
.status-dot.online {{ background: var(--success); }}
.status-dot.offline {{ background: var(--danger); }}

.confidence-bar {{
    height: 5px;
    border-radius: 3px;
    background: var(--surface-inset);
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
    color: var(--accent);
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
    background: var(--surface-inset);
    border: 1px solid var(--border);
    color: var(--text-body);
}}
.app-footer {{
    position: fixed !important;
    bottom: 3.2rem !important;
    right: 1.5rem !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    background: rgba(22, 27, 34, 0.85) !important;
    opacity: 1 !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    border: 1px solid rgba(48, 54, 61, 0.7) !important;
    backdrop-filter: blur(8px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    z-index: 999999 !important;
    pointer-events: none !important;
    text-align: center !important;
    display: inline-block !important;
    line-height: 1.2 !important;
    overflow: hidden !important;
}}
.app-footer span {{
    position: static !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 0 !important;
    margin: 0 !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    text-shadow: none !important;
}}

/* ── Step tracker ── */
.stepper {{
    display: flex;
    align-items: flex-start;
    margin: 4px 0 28px 0;
}}
.stepper-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 0 0 auto;
}}
.stepper-connector {{
    flex: 1 1 auto;
    height: 2px;
    background: var(--border);
    margin: 15px 8px 0 8px;
    border-radius: 1px;
    transition: background 0.3s ease;
}}
.stepper-connector.done {{ background: var(--success); }}
.stepper-circle {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    border: 2px solid var(--border);
    color: var(--text-muted);
    background: var(--surface);
    transition: all 0.25s ease;
}}
.stepper-circle.active {{
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-dim);
    animation: stepper-pulse 2.4s ease-in-out infinite;
}}
@keyframes stepper-pulse {{
    0%, 100% {{ box-shadow: 0 0 0 4px var(--accent-dim); }}
    50% {{ box-shadow: 0 0 0 7px rgba(56, 139, 253, 0.18); }}
}}
.stepper-circle.done {{
    border-color: var(--success);
    color: #ffffff;
    background: var(--success);
}}
.stepper-label {{
    margin-top: 8px;
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-muted);
    text-align: center;
    max-width: 110px;
}}
.stepper-item.is-active .stepper-label {{ color: var(--text-heading); }}
.stepper-item.is-done .stepper-label {{ color: var(--text-body); }}

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

div[data-testid="stVerticalBlock"]:has(.tour-banner-active),
div[class*="stColumn"]:has(.tour-banner-active) {{
    position: relative !important;
    z-index: 999999 !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.tour-banner-active) {{
    position: relative !important;
    z-index: 999999 !important;
    border: 2px solid var(--success) !important;
    box-shadow: 0 0 35px rgba(46, 164, 79, 0.6) !important;
    background: var(--surface) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease, z-index 0.3s ease !important;
}}

/* ── Mechanical loader override (rotating gear) ── */
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
<div class="hero-wrap">
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


def render_stepper(labels: list[str], current: int, done: set[int]):
    """Premium horizontal step tracker. `labels` are the step names in
    order, `current` is the 0-based index in focus, `done` is the set of
    0-based indices already completed. Pure presentation — callers derive
    state from whatever signals they already have (no new session state
    required)."""
    items = []
    for i, label in enumerate(labels):
        is_done = i in done
        is_active = i == current and not is_done
        circle_class = "done" if is_done else ("active" if is_active else "")
        item_class = "is-done" if is_done else ("is-active" if is_active else "")
        content = "✓" if is_done else str(i + 1)
        items.append(
            f'<div class="stepper-item {item_class}">'
            f'<div class="stepper-circle {circle_class}">{content}</div>'
            f'<div class="stepper-label">{label}</div>'
            f'</div>'
        )
        if i < len(labels) - 1:
            connector_class = "done" if i in done else ""
            items.append(f'<div class="stepper-connector {connector_class}"></div>')
    st.markdown(f'<div class="stepper">{"".join(items)}</div>', unsafe_allow_html=True)


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
    background: {SURFACE};
    font-size: 0.875rem;
    color: {TEXT_BODY};
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
    <p style="font-size: 0.95rem; font-weight: 600; color: {TEXT_BODY}; margin-bottom: 6px;">{title}</p>
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


def render_sidebar_status(api_connected: bool, material_count: int):
    dot_class = "online" if api_connected else "offline"
    status_text = "API Connected" if api_connected else "API Key Required"
    st.markdown(
        f"""
<div style="padding: 12px; border-radius: var(--radius); border: 1px solid var(--border); margin-bottom: 16px; background: {SURFACE};">
    <span class="status-dot {dot_class}"></span>
    <span style="font-size: 0.85rem; font-weight: 600; color: {TEXT_HEADING};">{status_text}</span>
    <p style="margin: 4px 0 0 0; font-size: 0.75rem; color: {TEXT_MUTED};">
        {material_count} materials in database
    </p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        '<div class="app-footer"><span>made with ❤️ by sanjay_bp</span></div>',
        unsafe_allow_html=True,
    )


def scroll_to_anchor(anchor_id: str, attempts: int = 30, delay_ms: int = 100):
    """Smooth-scroll the page (searching parent/top window contexts, since
    Streamlit components render inside an iframe) to an element with the
    given id, retrying briefly in case it hasn't painted yet. Shared by the
    guided tour and the post-analysis auto-scroll-to-results."""
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

                var el = doc.getElementById('{anchor_id}');
                if (el) {{
                    el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    clearInterval(interval);
                }} else if (attempts >= {attempts}) {{
                    clearInterval(interval);
                }}
            }}, {delay_ms});
        }})();
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)


def render_tour_banner(step_num: int, total_steps: int, title: str, text: str, key_prefix: str):
    """Render a premium green-bordered guided tour card with compact controls and auto-scroll."""
    scroll_to_anchor(f"tour-step-{step_num}-anchor")

    html_content = f"""
<div class="tour-banner-active" style="
    border: 2px solid {SUCCESS};
    background: rgba(46, 164, 79, 0.05);
    padding: 16px;
    border-radius: 6px;
    margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(46, 164, 79, 0.15);
">
    <div style="font-size: 0.72rem; font-weight: 700; color: {SUCCESS}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-family: 'Inter', sans-serif;">
        Guide Tour · Step {step_num} of {total_steps}
    </div>
    <h4 style="margin: 0 0 6px 0; color: {SUCCESS}; font-weight: 600; font-family: 'Inter', sans-serif;">{title}</h4>
    <p style="margin: 0; font-size: 0.875rem; color: {TEXT_MUTED}; line-height: 1.4; font-family: 'Inter', sans-serif;">{text}</p>
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
    """Inject Microsoft Clarity tracking script directly into the parent window context."""
    js_code = """
    <script type="text/javascript">
        try {
            (function(c,l,a,r,i,t,y){
                c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
                t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
                y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
            })(window.parent, window.parent.document, "clarity", "script", "xpyroe7f7m");
        } catch(e) {
            console.log("Parent context blocked. Falling back to local iframe context.");
            (function(c,l,a,r,i,t,y){
                c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
                t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
                y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
            })(window, document, "clarity", "script", "xpyroe7f7m");
        }
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)


def render_stl_viewer(stl_bytes: bytes, height: int = 420):
    """Embed a lightweight three.js viewer (rotate/zoom via mouse) for a CAD
    Studio preview mesh, so users can inspect a specimen before downloading
    it rather than trusting a blind export. Self-contained per render call —
    three.js is loaded from CDN, standard for a server-rendered Streamlit
    component (unlike a published Artifact, this iframe has normal network
    access)."""
    b64 = base64.b64encode(stl_bytes).decode("ascii")
    html = f"""
    <div id="stl-viewer-root" style="width:100%;height:{height}px;border-radius:12px;
        overflow:hidden;background:{SURFACE};border:1px solid {BORDER};"></div>
    <div id="stl-viewer-hint" style="color:{TEXT_MUTED};font-size:12px;margin-top:6px;
        font-family:Inter,sans-serif;">Drag to rotate · scroll to zoom</div>
    <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
    <script src="https://unpkg.com/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
    <script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
    (function() {{
        var root = document.getElementById('stl-viewer-root');
        var height = {height};
        var width = root.clientWidth || 600;

        var scene = new THREE.Scene();
        scene.background = new THREE.Color('{SURFACE}');

        var camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100000);
        var renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(width, height);
        root.appendChild(renderer.domElement);

        scene.add(new THREE.AmbientLight(0xffffff, 0.65));
        var dl1 = new THREE.DirectionalLight(0xffffff, 0.75);
        dl1.position.set(1, 1, 1);
        scene.add(dl1);
        var dl2 = new THREE.DirectionalLight(0xffffff, 0.35);
        dl2.position.set(-1, -1, -0.5);
        scene.add(dl2);

        var raw = atob("{b64}");
        var buf = new Uint8Array(raw.length);
        for (var i = 0; i < raw.length; i++) buf[i] = raw.charCodeAt(i);

        var geometry = new THREE.STLLoader().parse(buf.buffer);
        geometry.center();
        geometry.computeBoundingSphere();

        var material = new THREE.MeshStandardMaterial({{
            color: 0x4fd1c5, metalness: 0.2, roughness: 0.6, side: THREE.DoubleSide,
        }});
        var mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        var radius = (geometry.boundingSphere && geometry.boundingSphere.radius) || 20;
        camera.position.set(radius * 2.2, radius * 1.6, radius * 2.2);
        camera.lookAt(0, 0, 0);

        var controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(0, 0, 0);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.update();

        (function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }})();

        window.addEventListener('resize', function() {{
            var w = root.clientWidth || width;
            camera.aspect = w / height;
            camera.updateProjectionMatrix();
            renderer.setSize(w, height);
        }});
    }})();
    </script>
    """
    st.components.v1.html(html, height=height + 30, scrolling=False)
