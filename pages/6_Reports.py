"""Reports: SQL-driven analysis with charts and tables."""
import plotly.express as px
import streamlit as st

from utils import queries as q
from utils.helpers import (DIRECTION_COLORS, TYPE_COLORS, empty_state, page_header, section, show_chart, style_fig)

page_header("Reports", "Distribution, ranking and comparison reports built with SQL aggregates.")

MONEY = st.column_config.NumberColumn(format="localized")
tab_acc, tab_bal, tab_cust, tab_tx, tab_loans = st.tabs(
    ["Account types", "Balances", "Customers", "Transactions", "Loans and bills"])

# ---------------------------------------------------------------- account types
with tab_acc:
    cmp_ = q.type_comparison()
    section("Account type comparison", "GROUP BY account type")
    st.dataframe(cmp_, hide_index=True, width="stretch", column_config={
        "account_type": "Type", "accounts": st.column_config.NumberColumn("Accounts", format="%d"),
        "total_balance": st.column_config.NumberColumn("Total (Rs)", format="localized"),
        "avg_balance": st.column_config.NumberColumn("Average (Rs)", format="localized"),
        "min_balance": st.column_config.NumberColumn("Lowest (Rs)", format="localized"),
        "max_balance": st.column_config.NumberColumn("Highest (Rs)", format="localized"),
        "customers": st.column_config.NumberColumn("Customers", format="%d"),
    })
    section("Average balance per account")
    fig = px.bar(cmp_, x="account_type", y="avg_balance", color="account_type", color_discrete_map=TYPE_COLORS)
    fig.update_traces(marker_cornerradius=4, hovertemplate="%{x}: Rs %{y:,.0f} on average<extra></extra>")
    fig.update_layout(bargap=0.6)
    fig.update_yaxes(tickprefix="Rs ", tickformat="~s", rangemode="tozero")
    show_chart(style_fig(fig, legend=False))

# ---------------------------------------------------------------- balances
with tab_bal:
    left, right = st.columns(2)
    with left:
        section("Balance distribution", "accounts per balance band")
        bands = q.balance_bands()
        bands["band"] = bands["band"].str.replace(r"^\d\. ", "", regex=True)
        fig = px.bar(bands, x="band", y="accounts", text="accounts")
        fig.update_traces(marker_color="#13315C", marker_cornerradius=4, textposition="outside",
                          hovertemplate="%{x}: %{y} accounts<extra></extra>")
        fig.update_layout(bargap=0.5)
        fig.update_yaxes(dtick=1, rangemode="tozero")
        show_chart(style_fig(fig, legend=False))
    with right:
        section("Highest-balance accounts", "top 5")
        top = q.top_accounts(5).sort_values("balance")
        top["label"] = top["account_id"].astype(str) + " - " + top["holder"]
        fig = px.bar(top, x="balance", y="label", color="account_type", orientation="h",
                     color_discrete_map=TYPE_COLORS)
        fig.update_traces(marker_cornerradius=4, hovertemplate="%{y}: Rs %{x:,.0f}<extra></extra>")
        fig.update_layout(bargap=0.4)
        fig.update_xaxes(tickprefix="Rs ", tickformat="~s")
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        show_chart(style_fig(fig))

# ---------------------------------------------------------------- customers
with tab_cust:
    section("Customers with more than one account", "GROUP BY ... HAVING COUNT(*) > 1")
    multi = q.multi_account_customers()
    if multi.empty:
        empty_state("Every customer has exactly one account.")
    else:
        st.dataframe(multi, hide_index=True, width="stretch", column_config={
            "customer_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "name": "Customer", "accounts": st.column_config.NumberColumn("Accounts", format="%d"),
            "total_balance": st.column_config.NumberColumn("Combined balance (Rs)", format="localized"),
            "account_types": "Account types",
        })

# ---------------------------------------------------------------- transactions
with tab_tx:
    summary = q.transaction_summary()
    section("Transaction summary by type")
    st.dataframe(summary, hide_index=True, width="stretch", column_config={
        "transaction_type": "Type", "direction": "Direction",
        "transactions": st.column_config.NumberColumn("Count", format="%d"),
        "volume": st.column_config.NumberColumn("Volume (Rs)", format="localized"),
        "avg_amount": st.column_config.NumberColumn("Average (Rs)", format="localized"),
    })
    section("Credits versus debits")
    flow = summary.groupby("direction", as_index=False)["volume"].sum()
    fig = px.bar(flow, x="direction", y="volume", color="direction", color_discrete_map=DIRECTION_COLORS)
    fig.update_traces(marker_cornerradius=4, hovertemplate="%{x}: Rs %{y:,.0f}<extra></extra>")
    fig.update_layout(bargap=0.7)
    fig.update_yaxes(tickprefix="Rs ", tickformat="~s", rangemode="tozero")
    show_chart(style_fig(fig, legend=False, height=260))

# ---------------------------------------------------------------- loans & payments
with tab_loans:
    section("Loans", "how much of each loan has been repaid")
    loans = q.loan_overview()
    st.dataframe(loans, hide_index=True, width="stretch", column_config={
        "loan_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
        "customer": "Customer", "loan_type": "Loan",
        "amount": st.column_config.NumberColumn("Amount (Rs)", format="localized"),
        "balance": st.column_config.NumberColumn("Balance (Rs)", format="localized"),
        "repaid_pct": st.column_config.ProgressColumn("Repaid", format="%.1f%%", min_value=0, max_value=100),
        "end_date": st.column_config.DateColumn("Ends", format="MMM YYYY"), "status": "Status",
    })
    section("Bill payments by status")
    pay = q.payment_status()
    st.dataframe(pay, hide_index=True, width="stretch", column_config={
        "status": "Status", "payments": st.column_config.NumberColumn("Payments", format="%d"),
        "total": st.column_config.NumberColumn("Total (Rs)", format="localized"),
    })
