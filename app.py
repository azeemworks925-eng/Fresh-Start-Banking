"""Entry point: page config, shared styling, sidebar and navigation.

Run with:  streamlit run app.py
"""
import streamlit as st

from config import APP_TITLE
from database import check_connection
from utils.helpers import load_css

st.set_page_config(page_title=APP_TITLE, page_icon="🏦", layout="wide")
load_css()

pages = [
    st.Page("pages/1_Dashboard.py", title="Dashboard", icon=":material/space_dashboard:", default=True),
    st.Page("pages/2_Customers.py", title="Customers", icon=":material/groups:"),
    st.Page("pages/3_Accounts.py", title="Accounts", icon=":material/account_balance_wallet:"),
    st.Page("pages/4_Transactions.py", title="Transactions", icon=":material/receipt_long:"),
    st.Page("pages/5_Branches.py", title="Branches", icon=":material/apartment:"),
    st.Page("pages/6_Reports.py", title="Reports", icon=":material/monitoring:"),
]
nav = st.navigation(pages)

st.logo("assets/logo.svg", size="large")

ok, message = check_connection()
if not ok:
    st.error("Cannot connect to the database.")
    st.markdown(
        "Check these in your `.env` file, then refresh the page:\n"
        "- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` are correct\n"
        "- `DB_NAME` is `DB_Final_Group_Project_Working`\n"
        "- The MySQL server is running"
    )
    st.code(message)
    st.stop()

with st.sidebar:
    pass

nav.run()
