"""AppTest target: exercises save_custom_template() validation inside a
real Streamlit session_state, including the DuplicateWidgetID crash
that a duplicate template name used to be able to cause in
render_template_picker()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from modules.templates import TemplateValidationError, load_templates, save_custom_template

results = []


def try_save(name, description, prompt, label):
    try:
        save_custom_template(name, description, prompt)
        results.append(f"{label}: OK")
    except TemplateValidationError as e:
        results.append(f"{label}: REJECTED - {e}")


try_save("   ", "desc", "a real prompt", "whitespace_only_name")
try_save("Real Name", "desc", "   ", "whitespace_only_prompt")
try_save("x" * 100, "desc", "a real prompt", "too_long_name")
try_save("Good Template", "desc", "a real, valid prompt", "first_save")
try_save("Good Template", "other desc", "a different prompt", "duplicate_name")
try_save("good template", "other desc", "yet another prompt", "duplicate_name_case_insensitive")

custom = [t for t in load_templates() if t.get("is_custom")]
st.write(f"custom_count: {len(custom)}")
for r in results:
    st.write(r)

# Render one button per saved custom template using the same key
# pattern render_template_picker() uses in app.py. If a duplicate name
# had slipped past validation, THIS loop - not a separate assertion -
# is what would raise StreamlitDuplicateElementId, proving the fix
# works end to end rather than only at the validation-function level.
for t in custom:
    st.button("del-check", key=f"del_{t['name']}")
