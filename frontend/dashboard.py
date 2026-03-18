import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Business Analytics SaaS",
    layout="wide"
)

st.title("📊 Business Analytics SaaS Dashboard")

st.sidebar.header("Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload Inventory CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Upload a CSV file to begin analysis.")
    st.stop()

# Call backend API
with st.spinner("Running analytics..."):

    response = requests.post(
        "http://127.0.0.1:5000/upload",
        files={"file": uploaded_file}
    )

if response.status_code != 200:
    st.error(f"Backend error: {response.text}")
    st.stop()

data = response.json()

# Convert JSON to DataFrames
demand = pd.DataFrame(data["Demand Forecast"]).T
inventory = pd.DataFrame(data["Inventory Analysis"]).T
revenue = pd.DataFrame(data["Revenue Forecast"]).T
expiry = pd.DataFrame(data["Expiry Risk"]).T

# ---------------- KPI SECTION ---------------- #

st.header("📈 Business KPIs")

total_revenue = revenue["Predicted Revenue"].sum()
expiry_units = expiry["Potential Expiry Units"].sum()
reorder_products = inventory[inventory["Status"] == "Reorder Needed"].shape[0]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Predicted Monthly Revenue",
    f"${total_revenue:,}"
)

col2.metric(
    "Products Needing Reorder",
    reorder_products
)

col3.metric(
    "Units at Expiry Risk",
    expiry_units
)

st.divider()

# ---------------- TABS ---------------- #

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Sales Forecast",
    "📦 Inventory",
    "💰 Revenue",
    "⚠ Expiry Risk"
])

# ---------------- SALES FORECAST TAB ---------------- #

with tab1:

    st.subheader("Predicted Daily Demand")

    fig = px.bar(
        demand,
        y="Predicted Daily Demand",
        title="Demand Forecast per Product"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(demand)

# ---------------- INVENTORY TAB ---------------- #

with tab2:

    st.subheader("Inventory Analysis")

    reorder = inventory[inventory["Status"] == "Reorder Needed"]

    if not reorder.empty:
        st.warning("⚠ Some products require restocking")

    st.dataframe(inventory)

# ---------------- REVENUE TAB ---------------- #

with tab3:

    st.subheader("Revenue Forecast")

    fig = px.bar(
        revenue,
        y="Predicted Revenue",
        title="Revenue Forecast per Product"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(revenue)

# ---------------- EXPIRY TAB ---------------- #

with tab4:

    st.subheader("Expiry Risk Detection")

    risk = expiry[expiry["Status"] == "Expiry Risk"]

    if not risk.empty:
        st.error("⚠ Products at risk of expiry")

    st.dataframe(expiry)

# ---------------- AI BUSINESS ASSISTANT ---------------- #

st.divider()

st.header("🤖 AI Business Assistant")

provider = st.selectbox(
    "Select AI Provider",
    ["openai", "groq"]
)

question = st.text_input(
    "Ask a question about your business data"
)

api_key = st.text_input(
    "Enter API Key",
    type="password"
)

if provider == "openai":

    base_url = st.text_input(
        "Base URL",
        value="https://api.openai.com/v1"
    )

    model_name = st.text_input(
        "Model Name",
        value="gpt-4o-mini"
    )

else:

    base_url = st.text_input(
        "Base URL",
        value="https://api.groq.com/openai/v1"
    )

    model_name = st.text_input(
        "Model Name",
        value="llama-3.3-70b-versatile"
    )

if st.button("Generate AI Insights"):

    if not question:
        st.warning("Please enter a question.")
        st.stop()

    if not api_key:
        st.warning("Please enter API key.")
        st.stop()

    with st.spinner("Generating AI insights..."):

        response = requests.post(
            "http://127.0.0.1:5000/ai-insights",
            json={
                "question": question,
                "api_key": api_key,
                "base_url": base_url,
                "model_name": model_name,
                "provider": provider
            }
        )

        if response.status_code != 200:
            st.error("AI service error")
        else:
            answer = response.json()["answer"]
            st.success("AI Insight")
            st.write(answer)