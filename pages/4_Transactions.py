"""Transactions: searchable, filterable ledger."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import queries as q
from utils.helpers import (DIRECTION_COLORS, empty_state, metric_card, metric_row, page_header, pkr, section,
                           show_chart, style_fig)

page_header("Transactions", "Search the ledger by ID, type, account or date.")

all_types = q.transaction_types()
rng = q.transaction_date_range().iloc[0]
accounts = q.accounts()

c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
search = c1.text_input("Search", placeholder="ID, description or customer")
types = c2.multiselect("Type", all_types, placeholder="All types")
account_options = {"All accounts": None} | {f"{int(r.account_id)} - {r.holder}": int(r.account_id) for r in accounts.itertuples()}
account_label = c3.selectbox("Account", list(account_options))

start = end = None
if rng["first_day"] is not None:
    picked = c4.date_input("Date range", value=(rng["first_day"], rng["last_day"]),
                           min_value=rng["first_day"], max_value=rng["last_day"], format="DD/MM/YYYY")
    if isinstance(picked, tuple) and len(picked) == 2:
        start, end = picked

tx = q.transactions(search, tuple(types), account_options[account_label], start, end)
if tx.empty:
    empty_state("No transactions match these filters. Widen the date range or clear the search.")
    st.stop()

credits = tx.loc[tx["direction"] == "Credit", "amount"].sum()
debits = tx.loc[tx["direction"] == "Debit", "amount"].sum()
metric_row([
    metric_card("Transactions", str(len(tx))),
    metric_card("Credits in", pkr(credits), "deposits and profit payouts"),
    metric_card("Debits out", pkr(debits), "withdrawals and transfers"),
    metric_card("Net flow", pkr(credits - debits)),
])

st.write("")
view = tx.assign(
    atm=tx["atm_id"].map(lambda v: "-" if pd.isna(v) else str(int(v))),
    beneficiary_name=tx["beneficiary_name"].fillna("-"),
)
st.dataframe(
    view[["transaction_id", "date", "account_id", "customer", "transaction_type", "direction", "amount",
          "description", "atm", "beneficiary_name"]],
    hide_index=True, width="stretch",
    column_config={
        "transaction_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
        "date": st.column_config.DatetimeColumn("Date", format="DD MMM YYYY, HH:mm"),
        "account_id": st.column_config.NumberColumn("Account", format="%d", width="small"),
        "customer": "Customer", "transaction_type": "Type", "direction": "Direction",
        "amount": st.column_config.NumberColumn("Amount (Rs)", format="localized"),
        "description": "Description", "atm": st.column_config.TextColumn("ATM", width="small"),
        "beneficiary_name": "Beneficiary",
    },
)
st.markdown(
    '<div class="notice">The database stores no status for transactions, so none is shown. '
    "Direction is derived from the type: deposits and profit payouts are credits; "
    "withdrawals and transfers are debits.</div>",
    unsafe_allow_html=True,
)

section("Volume by type", "for the transactions listed above")
by_type = tx.groupby(["transaction_type", "direction"], as_index=False)["amount"].sum().sort_values("amount")
fig = px.bar(by_type, x="amount", y="transaction_type", color="direction", orientation="h",
             color_discrete_map=DIRECTION_COLORS)
fig.update_traces(marker_cornerradius=4, hovertemplate="%{y}: Rs %{x:,.0f}<extra></extra>")
fig.update_layout(bargap=0.5)
fig.update_xaxes(tickprefix="Rs ", tickformat="~s")
fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
show_chart(style_fig(fig, height=260))
