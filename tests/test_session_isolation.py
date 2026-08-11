"""Proves the core claim behind moving history.py and templates.py off
shared server files and onto st.session_state: two independent visitor
sessions never see each other's data. This is the same verification
method used to confirm the original data-leak fix - two genuinely
separate AppTest instances, not two calls in the same process.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_history_never_shared_between_sessions():
    session_a = AppTest.from_file(str(FIXTURES / "history_isolation_app.py"))
    session_b = AppTest.from_file(str(FIXTURES / "history_isolation_app.py"))

    session_a.run(timeout=30)
    session_b.run(timeout=30)

    text_a = "\n".join(m.value for m in session_a.markdown)
    text_b = "\n".join(m.value for m in session_b.markdown)

    # Each session logs one entry via the fixture; each must report
    # exactly its own single row, never zero, never two.
    assert "row_count: 1" in text_a
    assert "row_count: 1" in text_b


def test_custom_templates_never_shared_between_sessions():
    session_a = AppTest.from_file(str(FIXTURES / "templates_isolation_app.py"))
    session_b = AppTest.from_file(str(FIXTURES / "templates_isolation_app.py"))

    session_a.run(timeout=30)
    session_b.run(timeout=30)

    text_a = "\n".join(m.value for m in session_a.markdown)
    text_b = "\n".join(m.value for m in session_b.markdown)

    assert "custom_count: 1" in text_a
    assert "custom_count: 1" in text_b
