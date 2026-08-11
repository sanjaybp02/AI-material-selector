"""AppTest target: renders render_status_banner() with a payload
shaped like what a prompt-injected AI response could echo back
(e.g. via app.py's "Error: {e}" exception-message path). The outer
test inspects the resulting markdown element's raw source directly to
confirm html.escape() actually ran."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from modules.ui import render_status_banner

PAYLOAD = "<img src=x onerror=alert(1)>"
render_status_banner(f"Error: {PAYLOAD}", kind="error")
