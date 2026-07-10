import streamlit as st
import pandas as pd
import sqlite3
import os
import io
from datetime import datetime

from modules.ui import render_empty_state

DB_FILE = "history.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_history():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                query TEXT,
                top_material TEXT,
                confidence TEXT,
                est_cost TEXT,
                volume REAL,
                units TEXT,
                num_results INTEGER
            )
        """)
        conn.commit()
    finally:
        conn.close()

def log_search(query, materials, costs, volume, unit_system, currency_symbol="₹"):
    init_history()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    short_query = query[:80] + ("..." if len(query) > 80 else "")
    top_mat = materials[0]["MaterialName"] if materials else "N/A"
    conf = f"{materials[0].get('Confidence', 'N/A')}%" if materials else "N/A"
    est_cost = f"{currency_symbol}{costs[0]:.2f}" if costs else "N/A"
    num_res = len(materials)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO search_history (timestamp, query, top_material, confidence, est_cost, volume, units, num_results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, short_query, top_mat, conf, est_cost, volume, unit_system, num_res))
        conn.commit()
    finally:
        conn.close()

def get_history_df():
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM search_history ORDER BY id DESC", conn)
    finally:
        conn.close()
    return df

def clear_history():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM search_history")
        conn.commit()
    finally:
        conn.close()

def save_history_changes(edited_df):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM search_history")
        for _, row in edited_df.iterrows():
            timestamp = str(row.get("Timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            query = str(row.get("Query") or "Manual Entry")
            top_mat = str(row.get("Top Material") or "N/A")
            conf = str(row.get("Confidence") or "N/A")
            est_cost = str(row.get("Est. Cost") or "N/A")
            volume = float(row.get("Volume") or 0.0)
            units = str(row.get("Units") or "Metric")
            num_res = int(row.get("# Results") or 0)
            
            cursor.execute("""
                INSERT INTO search_history (timestamp, query, top_material, confidence, est_cost, volume, units, num_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, query, top_mat, conf, est_cost, volume, units, num_res))
        conn.commit()
    finally:
        conn.close()

def import_history_csv(df, mode="append"):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if mode == "overwrite":
            cursor.execute("DELETE FROM search_history")
            
        for _, row in df.iterrows():
            timestamp = str(row.get("Timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            query = str(row.get("Query") or "Imported Entry")
            top_mat = str(row.get("Top Material") or "N/A")
            conf = str(row.get("Confidence") or "N/A")
            est_cost = str(row.get("Est. Cost") or "N/A")
            volume = float(row.get("Volume") or 0.0)
            units = str(row.get("Units") or "Metric")
            num_res = int(row.get("# Results") or 0)
            
            cursor.execute("""
                INSERT INTO search_history (timestamp, query, top_material, confidence, est_cost, volume, units, num_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, query, top_mat, conf, est_cost, volume, units, num_res))
        conn.commit()
    finally:
        conn.close()

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
            save_history_changes(edited_df)
            st.success("Database successfully updated!")
            st.rerun()

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
