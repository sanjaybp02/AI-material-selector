"""AppTest target: logs one history entry unique to this simulated
visitor. Booted twice (as two independent AppTest instances) by
test_session_isolation.py, standing in for two different browser
sessions hitting the same shared server process."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from modules.history import get_history_df, init_history, log_search

init_history()
if "seeded" not in st.session_state:
    log_search("this visitor's own private query", [{"MaterialName": "Ti-6Al-4V", "Confidence": 90}], [500.0], 10.0, "Metric")
    st.session_state["seeded"] = True

df = get_history_df()
st.write(f"row_count: {len(df)}")
if not df.empty:
    st.write(f"query: {df.iloc[0]['query']}")
