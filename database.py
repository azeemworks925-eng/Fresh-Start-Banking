"""Reusable, read-only MySQL access for the whole app.

Every page calls `run_query(sql, params)`. Values from the user are ALWAYS passed in
`params` (never formatted into the SQL string), so the database driver escapes them
and SQL injection is not possible.
"""
from contextlib import contextmanager
from decimal import Decimal

import mysql.connector
import pandas as pd
import streamlit as st

from config import get_db_settings


@contextmanager
def get_connection():
    s = get_db_settings()
    conn = mysql.connector.connect(
        host=s.host,
        port=s.port,
        user=s.user,
        password=s.password,
        database=s.database,
        connection_timeout=8,
    )
    try:
        # Belt and braces: even if a write query slipped through, MySQL refuses it.
        cur = conn.cursor()
        cur.execute("SET SESSION TRANSACTION READ ONLY")
        cur.close()
        yield conn
    finally:
        conn.close()


def _is_read_only(sql: str) -> bool:
    head = sql.lstrip().split(None, 1)[0].lower() if sql.strip() else ""
    return head in {"select", "with", "show"}


@st.cache_data(ttl=30, show_spinner=False)
def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame. Results are cached for 30 seconds."""
    if not _is_read_only(sql):
        raise ValueError("This application is read-only: only SELECT queries are allowed.")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        columns = [c[0] for c in cur.description]
        rows = cur.fetchall()
        cur.close()
    df = pd.DataFrame(rows, columns=columns)
    # MySQL DECIMAL arrives as Python Decimal; convert so Pandas/Plotly can do maths.
    for col in df.columns:
        if len(df) and isinstance(df[col].iloc[0], Decimal):
            df[col] = df[col].astype(float)
    return df


def check_connection() -> tuple[bool, str]:
    """Used on start-up to show a friendly message instead of a stack trace."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()")
            n = cur.fetchone()[0]
            cur.close()
        return True, f"Connected ({n} tables)"
    except Exception as exc:  # noqa: BLE001 - we want to show any failure to the user
        return False, str(exc)
