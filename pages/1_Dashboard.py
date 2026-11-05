"""Dashboard: headline numbers, charts and recent activity, all calculated by MySQL."""
import plotly.express as px
import streamlit as st

from utils import queries as q
from utils.helpers import (DIRECTION_COLORS, TYPE_COLORS, metric_card, metric_row, page_header, pkr, pkr_compact,
                           section, show_chart, style_fig)

page_header("Dashboard", "A live overview of the bank, read straight from the database.")

m = q.overview_metrics().iloc[0]
metric_row([
    metric_card("Total balances", pkr(m["total_balance"]), f"across {int(m['accounts'])} accounts", primary=True),
    metric_card("Customers", f"{int(m['customers']):,}"),
    metric_card("Accounts", f"{int(m['accounts']):,}"),
    metric_card("Transactions", f"{int(m['transactions']):,}"),
    metric_card("Branches", f"{int(m['branches']):,}"),
    metric_card("Employees", f"{int(m['employees']):,}"),
])

# ---- accounts by type ------------------------------------------------------
by_type = q.accounts_by_type()
by_type["label"] = by_type["total_balance"].map(pkr_compact)

left, right = st.columns(2)
with left:
    section("Accounts by type", "number of accounts")
    fig = px.bar(by_type, x="account_type", y="accounts", color="account_type", color_discrete_map=TYPE_COLORS,
                 text="accounts")
    fig.update_traces(marker_cornerradius=4, textposition="outside", hovertemplate="%{x}: %{y} accounts<extra></extra>")
    fig.update_layout(bargap=0.55)
    fig.update_yaxes(dtick=1, rangemode="tozero")
    show_chart(style_fig(fig, legend=False))
with right:
    section("Balance by type", "total held")
    fig = px.bar(by_type, x="account_type", y="total_balance", color="account_type", color_discrete_map=TYPE_COLORS,
                 text="label")
    fig.update_traces(marker_cornerradius=4, textposition="outside",
                      hovertemplate="%{x}: Rs %{y:,.0f}<extra></extra>")
    fig.update_layout(bargap=0.55)
    fig.update_yaxes(tickprefix="Rs ", tickformat="~s", rangemode="tozero")
    show_chart(style_fig(fig, legend=False))

# ---- transaction activity --------------------------------------------------
monthly = q.monthly_activity()
mix = q.transaction_summary()

left, right = st.columns([3, 2])
with left:
    section("Transaction activity", "volume per month; only months with activity are shown")
    if monthly.empty:
        st.info("No transactions recorded yet.")
    else:
        fig = px.bar(monthly, x="month", y="volume", custom_data=["transactions"])
        fig.update_traces(marker_color="#13315C", marker_cornerradius=4,
                          hovertemplate="%{x}<br>Rs %{y:,.0f} in %{customdata[0]} transactions<extra></extra>")
        fig.update_layout(bargap=0.6)
        fig.update_xaxes(type="category")
        fig.update_yaxes(tickprefix="Rs ", tickformat="~s", rangemode="tozero")
        show_chart(style_fig(fig, legend=False))
with right:
    section("Transactions by type", "credits and debits")
    fig = px.bar(mix.sort_values("volume"), x="volume", y="transaction_type", color="direction", orientation="h",
                 color_discrete_map=DIRECTION_COLORS, custom_data=["transactions"])
    fig.update_traces(marker_cornerradius=4,
                      hovertemplate="%{y}<br>Rs %{x:,.0f} in %{customdata[0]} transactions<extra></extra>")
    fig.update_layout(bargap=0.5)
    fig.update_xaxes(tickprefix="Rs ", tickformat="~s")
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    show_chart(style_fig(fig))

# ---- customers and recent transactions -------------------------------------
left, right = st.columns([2, 3])
with left:
    section("Customers by number of accounts")
    dist = q.customers_by_account_count()
    dist["n_accounts"] = dist["n_accounts"].astype(str) + dist["n_accounts"].map(lambda n: " account" if n == 1 else " accounts")
    fig = px.bar(dist, x="n_accounts", y="customers", text="customers")
    fig.update_traces(marker_color="#0F9D8A", marker_cornerradius=4, textposition="outside",
                      hovertemplate="%{x}: %{y} customers<extra></extra>")
    fig.update_layout(bargap=0.6)
    fig.update_yaxes(dtick=1, rangemode="tozero")
    show_chart(style_fig(fig, legend=False))
with right:
    section("Recent transactions", "latest 8")
    recent = q.recent_transactions(8).drop(columns=["account_id", "direction"])
    st.dataframe(
        recent, hide_index=True, width="stretch",
        column_config={
            "transaction_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "date": st.column_config.DatetimeColumn("Date", format="DD MMM YYYY, HH:mm"),
            "customer": "Customer",
            "account_id": st.column_config.NumberColumn("Account", format="%d", width="small"),
            "transaction_type": "Type",
            "direction": "Direction",
            "amount": st.column_config.NumberColumn("Amount (Rs)", format="localized"),
        },
    )
