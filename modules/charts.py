import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Theme-aligned chart palette
CHART_COLORS = ["#00e5ff", "#ff6b35", "#3fb950", "#a371f7"]
CHART_FILLS = [
    "rgba(0, 229, 255, 0.22)",
    "rgba(255, 107, 53, 0.22)",
    "rgba(63, 185, 80, 0.22)",
    "rgba(163, 113, 247, 0.22)",
]
CHART_MUTED = "#484f58"
CHART_HIGHLIGHT = "#00e5ff"
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#c9d1d9", size=12),
    title_font=dict(size=15, color="#e6edf3"),
)


def _normalize_column(series, invert=False):
    s_min, s_max = series.min(), series.max()
    if s_max == s_min:
        return pd.Series([0.5] * len(series), index=series.index)
    return (s_max - series) / (s_max - s_min) if invert else (series - s_min) / (s_max - s_min)


def radar_chart(df, selected_names, unit_system="Metric"):
    from modules.data_loader import (
        get_yield_col, get_density_col, get_modulus_col,
        get_thermal_col, get_cost_col, get_fatigue_col, get_carbon_col
    )

    cols = {
        "Yield Strength": (get_yield_col(unit_system), False),
        "Density (lighter=better)": (get_density_col(unit_system), True),
        "Elastic Modulus": (get_modulus_col(unit_system), False),
        "Fatigue Strength": (get_fatigue_col(unit_system), False),
        "Machinability": ("Machinability (1-10)", False),
        "Cost (cheaper=better)": (get_cost_col(unit_system), True),
        "Carbon Footprint (lower=better)": (get_carbon_col(unit_system), True),
    }

    subset = df[df["Material Name"].isin(selected_names)]
    if subset.empty:
        return go.Figure()

    categories = list(cols.keys())
    fig = go.Figure()
    for i, name in enumerate(selected_names):
        row = subset[subset["Material Name"] == name]
        if row.empty:
            continue
        vals = []
        for _, (col, inv) in cols.items():
            if col in df.columns:
                norm = _normalize_column(df[col], invert=inv)
                vals.append(round(norm.loc[row.index[0]], 3) if row.index[0] in norm.index else 0)
            else:
                vals.append(0)
        vals.append(vals[0])
        color = CHART_COLORS[i % len(CHART_COLORS)]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=categories + [categories[0]], fill="toself",
            fillcolor=CHART_FILLS[i % len(CHART_FILLS)],
            line=dict(color=color, width=2),
            name=name,
        ))

    fig.update_layout(
        **CHART_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False, gridcolor="rgba(255,255,255,0.08)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        ),
        showlegend=True,
        title="Material comparison — normalized properties",
        height=480,
        margin=dict(t=60, b=40, l=60, r=60),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    return fig


def scatter_plot(df, x_col, y_col, highlight_names=None):
    plot_df = df.copy()
    plot_df["Group"] = plot_df["Material Name"].apply(
        lambda n: "Recommended" if highlight_names and n in highlight_names else "Other")

    fig = px.scatter(
        plot_df, x=x_col, y=y_col, color="Group", hover_name="Material Name",
        hover_data={"Group": False},
        color_discrete_map={"Recommended": CHART_HIGHLIGHT, "Other": CHART_MUTED},
        title=f"{y_col.split('(')[0].strip()} vs {x_col.split('(')[0].strip()}",
    )
    fig.update_traces(marker=dict(size=11, line=dict(width=1, color="rgba(255,255,255,0.3)")))
    fig.update_layout(**CHART_LAYOUT, height=400, margin=dict(t=50, b=40, l=40, r=40))
    return fig


def property_heatmap(df, unit_system="Metric"):
    from modules.data_loader import (
        get_yield_col, get_density_col, get_modulus_col,
        get_thermal_col, get_temp_col, get_cost_col, get_fatigue_col, get_carbon_col
    )

    numeric_cols = [
        get_yield_col(unit_system), get_density_col(unit_system), get_temp_col(unit_system),
        get_modulus_col(unit_system), get_fatigue_col(unit_system), get_thermal_col(unit_system),
        "Machinability (1-10)", get_cost_col(unit_system), get_carbon_col(unit_system),
    ]
    existing = [c for c in numeric_cols if c in df.columns]
    if not existing:
        return go.Figure()

    hm = df[["Material Name"] + existing].set_index("Material Name")
    norm = hm.apply(lambda col: _normalize_column(col))

    fig = px.imshow(
        norm.values,
        labels=dict(x="Property", y="Material", color="Score"),
        x=[c.split("(")[0].strip() for c in existing],
        y=norm.index.tolist(),
        color_continuous_scale=["#161b22", "#1a6b8a", "#00e5ff"],
        aspect="auto",
        title="Property heatmap (normalized 0–1)",
    )
    fig.update_layout(**CHART_LAYOUT, height=max(400, len(df) * 22), margin=dict(t=50, b=40, l=160, r=40))
    return fig
