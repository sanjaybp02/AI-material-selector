import streamlit as st
import pandas as pd
from datetime import datetime


def init_history():
    """Initialize search history in session state if not present."""
    if "search_history" not in st.session_state:
        st.session_state["search_history"] = []


def log_search(query, materials, costs, volume, unit_system):
    """
    Append a search record to session history.

    Parameters
    ----------
    query : str
        The user's requirement text.
    materials : list[dict]
        List of recommended material dicts, each with keys:
        MaterialName, Confidence, Reasoning (and optionally Pros, Cons).
    costs : list[float]
        Corresponding estimated part costs.
    volume : float
        Part volume used for the calculation.
    unit_system : str
        "Metric" or "Imperial".
    """
    init_history()
    record = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Query": query[:80] + ("..." if len(query) > 80 else ""),
        "Top Material": materials[0]["MaterialName"] if materials else "N/A",
        "Confidence": f"{materials[0].get('Confidence', 'N/A')}%" if materials else "N/A",
        "Est. Cost": f"₹{costs[0]:.2f}" if costs else "N/A",
        "Volume": volume,
        "Units": unit_system,
        "# Results": len(materials),
    }
    st.session_state["search_history"].append(record)


def render_history_table():
    """Display the search history as a styled dataframe."""
    init_history()
    history = st.session_state["search_history"]

    if not history:
        st.info("No searches yet in this session. Run a query to see history here.")
        return

    hist_df = pd.DataFrame(history)
    # Show newest first
    hist_df = hist_df.iloc[::-1].reset_index(drop=True)
    hist_df.index = hist_df.index + 1
    hist_df.index.name = "#"
    st.dataframe(hist_df, width='stretch')
