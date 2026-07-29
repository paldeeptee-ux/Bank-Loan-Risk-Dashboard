import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Bank Loan Risk Dashboard",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Bank Loan Risk Analysis Dashboard")
st.markdown("---")

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("bank_loan_risk_dataset.csv")

    df["Disbursed Date"] = pd.to_datetime(
        df["Disbursed Date"],
        errors="coerce"
    )

    return df

df = load_data()

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Select Region",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

purpose = st.sidebar.multiselect(
    "Loan Purpose",
    options=df["Loan Purpose"].unique(),
    default=df["Loan Purpose"].unique()
)

status = st.sidebar.multiselect(
    "Loan Status",
    options=df["Loan Status"].unique(),
    default=df["Loan Status"].unique()
)

filtered = df[
    (df["Region"].isin(region)) &
    (df["Loan Purpose"].isin(purpose)) &
    (df["Loan Status"].isin(status))
]

# ---------------------------
# KPI Cards
# ---------------------------
total_loans = len(filtered)
loan_amount = filtered["Loan Amount (INR)"].sum()
avg_credit = filtered["Credit Score"].mean()
avg_income = filtered["Monthly Income (INR)"].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Loans", f"{total_loans:,}")
c2.metric("Loan Amount", f"₹{loan_amount:,.0f}")
c3.metric("Avg Credit Score", f"{avg_credit:.0f}")
c4.metric("Avg Monthly Income", f"₹{avg_income:,.0f}")

st.markdown("---")

# ---------------------------
# Charts Row 1
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    fig = px.pie(
        filtered,
        names="Loan Status",
        title="Loan Status Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        filtered.groupby("Loan Purpose")["Loan Amount (INR)"]
        .sum()
        .reset_index(),
        x="Loan Purpose",
        y="Loan Amount (INR)",
        title="Loan Amount by Purpose",
        color="Loan Amount (INR)"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Charts Row 2
# ---------------------------
col3, col4 = st.columns(2)

with col3:
    fig = px.histogram(
        filtered,
        x="Credit Score",
        nbins=30,
        title="Credit Score Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    fig = px.scatter(
        filtered,
        x="Monthly Income (INR)",
        y="Loan Amount (INR)",
        color="Loan Status",
        size="Credit Score",
        hover_data=["Employment Type"],
        title="Income vs Loan Amount"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Region Analysis
# ---------------------------
fig = px.bar(
    filtered.groupby("Region")["Loan Amount (INR)"]
    .sum()
    .reset_index(),
    x="Region",
    y="Loan Amount (INR)",
    color="Region",
    title="Loan Amount by Region"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Employment Analysis
# ---------------------------
fig = px.box(
    filtered,
    x="Employment Type",
    y="Loan Amount (INR)",
    color="Employment Type",
    title="Loan Amount by Employment Type"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Monthly Trend
# ---------------------------
if filtered["Disbursed Date"].notna().sum() > 0:

    trend = (
        filtered
        .groupby(filtered["Disbursed Date"].dt.to_period("M"))
        ["Loan Amount (INR)"]
        .sum()
        .reset_index()
    )

    trend["Disbursed Date"] = trend["Disbursed Date"].astype(str)

    fig = px.line(
        trend,
        x="Disbursed Date",
        y="Loan Amount (INR)",
        markers=True,
        title="Monthly Loan Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Data Table
# ---------------------------
st.subheader("Dataset")

st.dataframe(filtered, use_container_width=True)

# ---------------------------
# Download Button
# ---------------------------
csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Data",
    csv,
    file_name="filtered_bank_loan_data.csv",
    mime="text/csv"
)