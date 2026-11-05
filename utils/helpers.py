"""Formatting, masking, chart styling and small UI building blocks."""
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from config import MASK_PII

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# Fixed colour per account type (validated: colour-blind safe, 3:1 contrast on the page).
TYPE_COLORS = {"Savings": "#2457A6", "Current": "#0F9D8A", "Islamic PLS": "#A87510"}
NAVY = "#0B2545"
TEAL = "#0F9D8A"
INK_MUTED = "#5B6B82"
GRID = "#E4E9F0"
DIRECTION_COLORS = {"Credit": "#0F9D8A", "Debit": "#2457A6"}


# --------------------------------------------------------------- formatting
def pkr(value) -> str:
    return f"Rs {float(value):,.0f}"


def pkr_compact(value) -> str:
    v = float(value)
    for limit, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(v) >= limit:
            return f"Rs {v / limit:,.2f}{suffix}"
    return f"Rs {v:,.0f}"


def mask_cnic(cnic: str) -> str:
    """35202-1982731-1 -> 35202-*******-1"""
    parts = str(cnic).split("-")
    if len(parts) == 3:
        return f"{parts[0]}-{'*' * len(parts[1])}-{parts[2]}"
    return "*" * len(str(cnic))


def mask_email(email: str) -> str:
    """kamran.bhatti@gmail.com -> k***@gmail.com (only when MASK_PII=true)."""
    if not MASK_PII or "@" not in str(email):
        return str(email)
    local, domain = str(email).split("@", 1)
    return f"{local[:1]}***@{domain}"


def mask_phone(phone: str) -> str:
    """03001234567 -> 0300****567 (only when MASK_PII=true)."""
    p = str(phone)
    if not MASK_PII or len(p) < 8:
        return p
    return f"{p[:4]}{'*' * (len(p) - 7)}{p[-3:]}"


def mask_card(number: str) -> str:
    """Only the last four digits are ever shown."""
    return f"**** **** **** {str(number)[-4:]}"


# --------------------------------------------------------------- UI pieces
def load_css() -> None:
    css = (ASSETS / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-head"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = "", primary: bool = False) -> str:
    note_html = f'<div class="m-note">{escape(note)}</div>' if note else ""
    css = "metric primary" if primary else "metric"
    return (
        f'<div class="{css}"><div class="m-label">{escape(label)}</div>'
        f'<div class="m-value">{escape(value)}</div>{note_html}</div>'
    )


def metric_row(cards: list[str]) -> None:
    primary = any('class="metric primary"' in c for c in cards)
    extra = f" with-primary rest-{len(cards) - 1}" if primary else ""
    st.markdown(f'<div class="metric-row{extra}">{"".join(cards)}</div>', unsafe_allow_html=True)


def section(title: str, caption: str = "") -> None:
    cap = f'<span>{escape(caption)}</span>' if caption else ""
    st.markdown(f'<div class="section-title"><h3>{escape(title)}</h3>{cap}</div>', unsafe_allow_html=True)


def empty_state(message: str) -> None:
    st.markdown(f'<div class="empty">{escape(message)}</div>', unsafe_allow_html=True)


def account_details(row: pd.Series) -> str:
    """One readable line built from whichever subtype table the account belongs to."""
    if pd.notna(row.get("interest_rate")):
        return f"Interest {row['interest_rate']:.2f}% - minimum balance {pkr(row['minimum_balance'])}"
    if pd.notna(row.get("overdraft_limit")):
        return f"Overdraft limit {pkr(row['overdraft_limit'])} at {row['overdraft_rate']:.2f}%"
    if pd.notna(row.get("mudarabah_rate")):
        return f"Mudarabah rate {row['mudarabah_rate']:.2f}% - {row['investment_allocation']}"
    return ""


# --------------------------------------------------------------- charts
def style_fig(fig, height: int = 320, legend: bool = True):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=12, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", size=13, color=NAVY),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text="", font=dict(size=12, color=INK_MUTED)),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family="IBM Plex Sans", size=13, color=NAVY)),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=INK_MUTED), title_text=None, automargin=True)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=INK_MUTED), title_text=None, automargin=True)
    return fig


def show_chart(fig) -> None:
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
