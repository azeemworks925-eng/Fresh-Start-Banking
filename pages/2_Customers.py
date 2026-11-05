"""Customers: search, profile, and each customer's accounts, cards and loans (read-only)."""
from html import escape

import streamlit as st

from utils import queries as q
from utils.helpers import (account_details, empty_state, mask_card, mask_cnic, mask_email, mask_phone, metric_card,
                           metric_row, page_header, pkr, section)

page_header("Customers", "Find a customer and see everything they hold with the bank.")

search = st.text_input("Search by name or customer ID", placeholder="e.g. Ayesha or 3")
customers = q.customers(search)

if customers.empty:
    empty_state("No customers match that search. Try part of a name, or a customer ID.")
    st.stop()

table = customers.assign(
    cnic=customers["cnic"].map(mask_cnic),
    phone=customers["phone"].map(mask_phone),
    email=customers["email"].map(mask_email),
)
st.caption(f"{len(table)} customer{'s' if len(table) != 1 else ''} - select a row to see details")
event = st.dataframe(
    table.drop(columns=["address"]), hide_index=True, width="stretch",
    on_select="rerun", selection_mode="single-row", key="customer_table",
    column_config={
        "customer_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
        "name": "Name", "cnic": "CNIC (masked)", "phone": "Phone", "email": "Email",
        "accounts": st.column_config.NumberColumn("Accounts", format="%d", width="small"),
        "total_balance": st.column_config.NumberColumn("Combined balance (Rs)", format="localized"),
    },
)

selected_rows = event.selection.rows
row = customers.iloc[selected_rows[0]] if selected_rows else customers.iloc[0]
cid = int(row["customer_id"])

accounts = q.customer_accounts(cid)
loans = q.customer_loans(cid)
cards = q.customer_cards(cid)

section("Customer profile")
st.markdown(
    f"""<div class="profile"><h2>{escape(row['name'])}</h2>
    <div class="kv">
      <div><span>Customer ID</span><b>{cid}</b></div>
      <div><span>CNIC</span><b>{escape(mask_cnic(row['cnic']))}</b></div>
      <div><span>Phone</span><b>{escape(mask_phone(row['phone']))}</b></div>
      <div><span>Email</span><b>{escape(mask_email(row['email']))}</b></div>
      <div><span>Address</span><b>{escape(row['address'])}</b></div>
    </div></div>""",
    unsafe_allow_html=True,
)

st.write("")
outstanding = float(loans.loc[loans["status"] == "Approved", "balance"].sum()) if not loans.empty else 0.0
metric_row([
    metric_card("Combined balance", pkr(row["total_balance"]), f"{int(row['accounts'])} account(s)", primary=True),
    metric_card("Cards", str(len(cards))),
    metric_card("Loans", str(len(loans)), f"{pkr(outstanding)} outstanding" if len(loans) else ""),
])

section("Accounts")
if accounts.empty:
    empty_state("This customer has no accounts.")
else:
    view = accounts.assign(details=accounts.apply(account_details, axis=1))[
        ["account_id", "account_type", "balance", "open_date", "details"]]
    st.dataframe(view, hide_index=True, width="stretch", column_config={
        "account_id": st.column_config.NumberColumn("Account", format="%d", width="small"),
        "account_type": "Type",
        "balance": st.column_config.NumberColumn("Balance (Rs)", format="localized"),
        "open_date": st.column_config.DateColumn("Opened", format="DD MMM YYYY"),
        "details": "Terms",
    })

left, right = st.columns(2)
with left:
    section("Cards", "numbers are masked")
    if cards.empty:
        empty_state("No cards issued.")
    else:
        view = cards.assign(card_number=cards["card_number"].map(mask_card))[
            ["card_type", "card_number", "account_id", "expiry_date"]]
        st.dataframe(view, hide_index=True, width="stretch", column_config={
            "card_type": "Card", "card_number": "Number",
            "account_id": st.column_config.NumberColumn("Account", format="%d", width="small"),
            "expiry_date": st.column_config.DateColumn("Expires", format="MMM YYYY"),
        })
with right:
    section("Loans")
    if loans.empty:
        empty_state("No loans.")
    else:
        st.dataframe(loans[["loan_type", "amount", "balance", "end_date", "status"]], hide_index=True,
                     width="stretch", column_config={
            "loan_type": "Loan",
            "amount": st.column_config.NumberColumn("Amount (Rs)", format="localized"),
            "balance": st.column_config.NumberColumn("Balance (Rs)", format="localized"),
            "end_date": st.column_config.DateColumn("Ends", format="MMM YYYY"),
            "status": "Status",
        })
