"""Accounts: search, filter by type, and inspect one account in detail."""
from html import escape

import streamlit as st

from utils import queries as q
from utils.helpers import (account_details, empty_state, metric_card, metric_row, page_header, pkr, section)

page_header("Accounts", "Every account with its type, holder, balance and terms.")

types = q.account_types()
c1, c2 = st.columns([2, 3])
search = c1.text_input("Search by account ID, customer ID or holder name", placeholder="e.g. 503 or Hina")
chosen = c2.multiselect("Account type", types["type_name"].tolist(), placeholder="All types")

accounts = q.accounts(search, tuple(chosen))
if accounts.empty:
    empty_state("No accounts match these filters. Clear the search or choose different types.")
    st.stop()

metric_row([
    metric_card("Accounts shown", str(len(accounts))),
    metric_card("Total balance", pkr(accounts["balance"].sum())),
    metric_card("Average balance", pkr(accounts["balance"].mean())),
    metric_card("Largest balance", pkr(accounts["balance"].max())),
])

st.write("")
table = accounts.assign(details=accounts.apply(account_details, axis=1))
st.caption("Select a row to see the account in detail")
event = st.dataframe(
    table[["account_id", "holder", "account_type", "balance", "open_date", "details"]],
    hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", key="account_table",
    column_config={
        "account_id": st.column_config.NumberColumn("Account", format="%d", width="small"),
        "holder": "Holder", "account_type": "Type",
        "balance": st.column_config.NumberColumn("Balance (Rs)", format="localized"),
        "open_date": st.column_config.DateColumn("Opened", format="DD MMM YYYY"),
        "details": "Terms",
    },
)

picked = event.selection.rows
acc = table.iloc[picked[0]] if picked else table.iloc[0]
section(f"Account {int(acc['account_id'])}", f"{acc['account_type']} - {acc['holder']}")
st.markdown(
    f"""<div class="profile"><div class="kv">
      <div><span>Holder</span><b>{escape(acc['holder'])} (customer {int(acc['customer_id'])})</b></div>
      <div><span>Balance</span><b>{pkr(acc['balance'])}</b></div>
      <div><span>Opened</span><b>{acc['open_date']:%d %b %Y}</b></div>
      <div><span>Terms</span><b>{escape(acc['details'])}</b></div>
    </div></div>""",
    unsafe_allow_html=True,
)

section("Latest transactions on this account")
tx = q.transactions(account_id=int(acc["account_id"])).head(5)
if tx.empty:
    empty_state("No transactions recorded for this account.")
else:
    st.dataframe(tx[["transaction_id", "date", "transaction_type", "direction", "amount", "description"]],
                 hide_index=True, width="stretch", column_config={
        "transaction_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
        "date": st.column_config.DatetimeColumn("Date", format="DD MMM YYYY, HH:mm"),
        "transaction_type": "Type", "direction": "Direction",
        "amount": st.column_config.NumberColumn("Amount (Rs)", format="localized"),
        "description": "Description",
    })
