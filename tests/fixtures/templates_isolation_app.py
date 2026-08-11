"""AppTest target: saves one custom template unique to this simulated
visitor. Booted twice by test_session_isolation.py, standing in for
two different browser sessions hitting the same shared server
process."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from modules.templates import load_templates, save_custom_template

if "seeded" not in st.session_state:
    save_custom_template("My Private Template", "desc", "this visitor's own proprietary prompt text")
    st.session_state["seeded"] = True

custom = [t for t in load_templates() if t.get("is_custom")]
st.write(f"custom_count: {len(custom)}")
if custom:
    st.write(f"name: {custom[0]['name']}")
