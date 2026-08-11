"""Tests for modules/templates.py's save_custom_template() validation.
Uses AppTest since templates live in real st.session_state - not a
plain function-call test - and specifically proves the DuplicateWidgetID
crash risk from a duplicate template name is actually closed end to
end (via a real widget render in the fixture), not just rejected at
the validation-function boundary.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_template_validation_end_to_end():
    at = AppTest.from_file(str(FIXTURES / "template_validation_app.py"))
    at.run(timeout=30)

    assert not at.exception, f"App raised (likely a DuplicateWidgetID regression): {at.exception}"

    outputs = "\n".join(m.value for m in at.markdown)
    assert "whitespace_only_name: REJECTED" in outputs
    assert "whitespace_only_prompt: REJECTED" in outputs
    assert "too_long_name: REJECTED" in outputs
    assert "first_save: OK" in outputs
    assert "duplicate_name: REJECTED" in outputs
    assert "duplicate_name_case_insensitive: REJECTED" in outputs
    # Only the one legitimate save should have gone through.
    assert "custom_count: 1" in outputs
