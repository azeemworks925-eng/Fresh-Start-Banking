"""Branches: contact details, staff and ATM statistics per branch."""
from html import escape

import streamlit as st

from utils import queries as q
from utils.helpers import page_header, pkr_compact, section

page_header("Branches", "Where the bank operates and who works there.")

branches = q.branch_summary()
cols = st.columns(max(len(branches), 1))
for col, b in zip(cols, branches.itertuples()):
    with col:
        st.markdown(
            f"""<div class="card"><h4>{escape(b.branch_name)}</h4>
            <div class="loc">{escape(b.city)}</div>
            <div class="addr">{escape(b.address)}<br>{escape(b.phone)}</div>
            <div class="stats">
              <div><b>{b.employees}</b><span>Staff</span></div>
              <div><b>{b.atms}</b><span>ATMs</span></div>
              <div><b>{pkr_compact(b.atm_volume)}</b><span>ATM volume</span></div>
            </div></div>""",
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="notice">Customers and accounts are not linked to a branch in this database, '
    "so branch statistics use staff, ATMs and ATM transactions only.</div>",
    unsafe_allow_html=True,
)

section("Staff")
st.dataframe(q.employees(), hide_index=True, width="stretch", column_config={
    "employee_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
    "name": "Name", "designation": "Designation", "branch_name": "Branch",
    "role_type": "Role", "role_detail": "Department / register / specialization",
})

section("ATMs")
st.dataframe(q.atms(), hide_index=True, width="stretch", column_config={
    "atm_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
    "location": "Location", "branch_name": "Branch", "status": "Status",
    "transactions": st.column_config.NumberColumn("Transactions", format="%d"),
})
