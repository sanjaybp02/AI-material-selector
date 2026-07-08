import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def _normalize_column(series, invert=False):
    s_min, s_max = series.min(), series.max()
    if s_max == s_min:
        return pd.Series([0.5] * len(series), index=series.index)
    return (s_max - series) / (s_max - s_min) if invert else (series - s_min) / (s_max - s_min)


def radar_chart(df, selected_names, unit_system="Metric"):
    from modules.data_loader import get_yield_col, get_density_col, get_modulus_col, get_thermal_col, get_cost_col

    cols = {
        "Yield Strength": (get_yield_col(unit_system), False),
        "Density (lighter=better)": (get_density_col(unit_system), True),
        "Elastic Modulus": (get_modulus_col(unit_system), False),
        "Thermal Cond.": (get_thermal_col(unit_system), False),
        "Machinability": ("Machinability (1-10)", False),
        "Cost (cheaper=better)": (get_cost_col(unit_system), True),
    }

    subset = df[df["Material Name"].isin(selected_names)]
    if subset.empty:
        return go.Figure()

    categories = list(cols.keys())
    fills = ["rgba(99,110,250,0.45)", "rgba(239,85,59,0.45)", "rgba(0,204,150,0.45)", "rgba(171,99,250,0.45)"]
    lines = ["rgb(99,110,250)", "rgb(239,85,59)", "rgb(0,204,150)", "rgb(171,99,250)"]

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
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=categories + [categories[0]], fill="toself",
            fillcolor=fills[i % 4], line=dict(color=lines[i % 4], width=2), name=name))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1], showticklabels=False)),
        showlegend=True, title="Material Comparison — Radar Chart",
        height=480, margin=dict(t=60, b=40, l=60, r=60))
    return fig


def scatter_plot(df, x_col, y_col, highlight_names=None):
    plot_df = df.copy()
    plot_df["Highlight"] = plot_df["Material Name"].apply(
        lambda n: "⭐ Recommended" if highlight_names and n in highlight_names else "Other")

    fig = px.scatter(plot_df, x=x_col, y=y_col, color="Highlight", hover_name="Material Name",
                     hover_data={"Highlight": False},
                     color_discrete_map={"⭐ Recommended": "#FF6B35", "Other": "#636EFA"},
                     title=f"{y_col} vs {x_col}")
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color="white")))
    fig.update_layout(height=400, margin=dict(t=50, b=40, l=40, r=40))
    return fig


def property_heatmap(df, unit_system="Metric"):
    from modules.data_loader import get_yield_col, get_density_col, get_modulus_col, get_thermal_col, get_temp_col, get_cost_col

    numeric_cols = [get_yield_col(unit_system), get_density_col(unit_system), get_temp_col(unit_system),
                    get_modulus_col(unit_system), get_thermal_col(unit_system),
                    "Machinability (1-10)", get_cost_col(unit_system)]
    existing = [c for c in numeric_cols if c in df.columns]
    if not existing:
        return go.Figure()

    hm = df[["Material Name"] + existing].set_index("Material Name")
    norm = hm.apply(lambda col: _normalize_column(col))

    fig = px.imshow(norm.values, labels=dict(x="Property", y="Material", color="Normalised"),
                    x=[c.split("(")[0].strip() for c in existing], y=norm.index.tolist(),
                    color_continuous_scale="Viridis", aspect="auto", title="Material Property Heatmap (Normalised)")
    fig.update_layout(height=max(400, len(df) * 22), margin=dict(t=50, b=40, l=160, r=40))
    return fig
