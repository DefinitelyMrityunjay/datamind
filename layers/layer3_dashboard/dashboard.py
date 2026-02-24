import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append("../../")
sys.path.append("../../layers/layer1_ingestion")
sys.path.append("../../layers/layer2_sql")

from ingestion import ingest_file
from sql_engine import push_to_postgres, run_query, get_table_schema
from insights import generate_insights

# -----------------------------------------------
# PAGE CONFIG
# -----------------------------------------------

st.set_page_config(
    page_title="AnalyzeIQ",
    page_icon="🧠",
    layout="wide"
)

# -----------------------------------------------
# HEADER
# -----------------------------------------------

st.title("🧠 AnalyzeIQ")
st.markdown("*Upload any data file and get instant AI-powered insights*")
st.divider()

# -----------------------------------------------
# SIDEBAR — File Upload
# -----------------------------------------------

with st.sidebar:
    st.header("📂 Upload Your Data")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls", "pdf", "png", "jpg", "jpeg"],
        help="Supports CSV, Excel, PDF, and Images"
    )

    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} uploaded")

    st.divider()
    st.markdown("**Supported formats:**")
    st.markdown("- CSV files")
    st.markdown("- Excel (.xlsx, .xls)")
    st.markdown("- PDF with tables")
    st.markdown("- Images (PNG, JPG)")

# -----------------------------------------------
# MAIN — Process and Display
# -----------------------------------------------

if uploaded_file is not None:

    # Save uploaded file temporarily
    temp_path = f"../../uploads/{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # ---- LAYER 1: Ingest ----
    with st.spinner("📥 Reading your file..."):
        try:
            df = ingest_file(temp_path)
            st.success(f"✅ File loaded — {df.shape[0]} rows × {df.shape[1]} columns")
        except Exception as e:
            st.error(f"❌ Could not read file: {e}")
            st.stop()

    # ---- LAYER 2: Push to PostgreSQL ----
    with st.spinner("🗄️ Pushing to database..."):
        try:
            metadata = push_to_postgres(df, file_name=uploaded_file.name)
            table_name = metadata["table_name"]
            st.success(f"✅ Stored as table: `{table_name}`")
        except Exception as e:
            st.error(f"❌ Database error: {e}")
            st.stop()

    st.divider()

    # ---- LAYER 3: Dashboard ----
    st.header("📊 Your Data")

    # Raw data preview
    with st.expander("🔍 Preview Raw Data", expanded=False):
        st.dataframe(df, use_container_width=True)

    # Schema info
    with st.expander("🗂️ Table Schema", expanded=False):
        schema = get_table_schema(table_name)
        schema_df = pd.DataFrame(schema["columns"])
        st.dataframe(schema_df, use_container_width=True)

    st.divider()

    # ---- AUTO CHARTS ----
    st.header("📈 Auto-Generated Charts")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    # Chart 1 — Bar chart (categorical vs numeric)
    if categorical_cols and numeric_cols:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Bar Chart")
            cat = categorical_cols[0]
            num = numeric_cols[0]
            bar_data = df.groupby(cat)[num].sum().reset_index()
            fig = px.bar(
                bar_data, x=cat, y=num,
                color=cat,
                title=f"{num} by {cat}",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Pie Chart")
            fig2 = px.pie(
                bar_data, names=cat, values=num,
                title=f"{num} Distribution by {cat}",
                template="plotly_dark"
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Chart 2 — Line chart (date vs numeric)
    if date_cols and numeric_cols:
        st.subheader("Trend Over Time")
        date_col = date_cols[0]
        num_col = numeric_cols[0]
        line_data = df.groupby(date_col)[num_col].sum().reset_index()
        fig3 = px.line(
            line_data, x=date_col, y=num_col,
            title=f"{num_col} over time",
            template="plotly_dark",
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Chart 3 — Correlation heatmap
    if len(numeric_cols) >= 2:
        st.subheader("Correlation Heatmap")
        corr = df[numeric_cols].corr()
        fig4 = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu",
            title="Correlation between numeric columns",
            template="plotly_dark"
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Chart 4 — Scatter plot
    if len(numeric_cols) >= 2:
        st.subheader("Scatter Plot")
        col3, col4 = st.columns(2)
        with col3:
            x_axis = st.selectbox("X axis", numeric_cols, index=0)
        with col4:
            y_axis = st.selectbox("Y axis", numeric_cols, index=1)

        color_col = categorical_cols[0] if categorical_cols else None
        fig5 = px.scatter(
            df, x=x_axis, y=y_axis,
            color=color_col,
            title=f"{x_axis} vs {y_axis}",
            template="plotly_dark",
            size_max=15
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.divider()

    # ---- AI INSIGHTS ----
    st.header("🤖 AI Insights")

    with st.spinner("Analyzing your data with AI..."):
        insights = generate_insights(df, table_name)

    st.markdown(insights)

    st.divider()

    # ---- KEY METRICS ----
    st.header("📌 Key Metrics")

    cols = st.columns(len(numeric_cols[:4]))
    for i, col_name in enumerate(numeric_cols[:4]):
        with cols[i]:
            st.metric(
                label=col_name.replace("_", " ").title(),
                value=f"{df[col_name].sum():,.2f}",
                delta=f"avg: {df[col_name].mean():,.2f}"
            )

else:
    # ---- LANDING STATE ----
    st.info("👈 Upload a file from the sidebar to get started")

    st.markdown("""
    ### What AnalyzeIQ does:
    - 📥 **Ingests** any file — CSV, Excel, PDF, or Image
    - 🗄️ **Stores** your data in a live PostgreSQL database
    - 📊 **Generates** automatic charts and visualizations
    - 🤖 **Analyzes** your data with AI to surface key insights
    - 💬 **Answers** your questions in plain English *(coming in Layer 4)*
    """)


## Add your OpenAI key to `.env`
