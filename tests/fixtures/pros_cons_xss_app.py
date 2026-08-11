"""AppTest target: renders render_pros_cons() with a malicious pro/con
string, standing in for AI-generated text an indirect prompt injection
could produce. The outer test inspects the resulting markdown
element's raw source directly to confirm html.escape() actually ran."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from modules.ui import render_pros_cons

PAYLOAD = "<img src=x onerror=alert(1)>"
render_pros_cons(pros=[PAYLOAD], cons=["Higher cost"])
