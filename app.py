import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Nassau Candy Optimization",
    page_icon="🍬",
    layout="wide"
)

st.title("🍬 Nassau Candy Optimization")
st.write(
    "Explore product performance, order trends, "
    "and shipping lead times."
)

# Find the CSV file in the project folder
csv_files = list(Path(".").glob("*.csv"))

if not csv_files:
    st.error(
        "No CSV dataset found. Upload your dataset "
        "to the project folder and GitHub repository."
    )
    st.stop()

# Load the first CSV file
df = pd.read_csv(csv_files[0])
df.columns = df.columns.str.strip()

st.success(f"Dataset loaded: {csv_files[0].name}")

# Identify useful columns without assuming every column exists
columns = {col.lower(): col for col in df.columns}

order_col = next(
    (columns[c] for c in ["order id", "order_id"] if c in columns),
    None
)
product_col = next(
    (col for col in df.columns if "product" in col.lower()
     and "name" in col.lower()),
    None
)
order_date_col = next(
    (columns[c] for c in ["order date", "order_date"] if c in columns),
    None
)
ship_date_col = next(
    (columns[c] for c in ["ship date", "ship_date"] if c in columns),
    None
)

# Calculate shipping lead time when dates are available
if order_date_col and ship_date_col:
    df[order_date_col] = pd.to_datetime(
        df[order_date_col], errors="coerce"
    )
    df[ship_date_col] = pd.to_datetime(
        df[ship_date_col], errors="coerce"
    )

    df["Lead Time (Days)"] = (
        df[ship_date_col] - df[order_date_col]
    ).dt.days

    # Exclude invalid or negative lead times
    df.loc[df["Lead Time (Days)"] < 0, "Lead Time (Days)"] = pd.NA

# Summary metrics
col1, col2, col3 = st.columns(3)

col1.metric("Total Records", f"{len(df):,}")

if order_col:
    col2.metric("Unique Orders", f"{df[order_col].nunique():,}")
else:
    col2.metric("Columns", len(df.columns))

if "Lead Time (Days)" in df.columns:
    avg_lead = df["Lead Time (Days)"].mean()
    col3.metric(
        "Average Lead Time",
        f"{avg_lead:.1f} days" if pd.notna(avg_lead) else "N/A"
    )
else:
    col3.metric("Products", df[product_col].nunique() if product_col else "N/A")

# Dataset preview
st.subheader("📋 Dataset Preview")
st.dataframe(df.head(100), use_container_width=True)

# Product analysis
if product_col:
    st.subheader("📦 Product Analysis")

    if "Lead Time (Days)" in df.columns:
        product_analysis = (
            df.dropna(subset=["Lead Time (Days)"])
            .groupby(product_col)
            .agg(
                Average_Lead_Time=("Lead Time (Days)", "mean"),
                Records=(product_col, "size")
            )
            .sort_values("Average_Lead_Time", ascending=False)
        )

        st.write("Products with the highest average shipping lead time")
        st.dataframe(product_analysis.head(10), use_container_width=True)

        if not product_analysis.empty:
            chart_data = product_analysis.head(10).sort_values(
                "Average_Lead_Time"
            )
            st.bar_chart(chart_data["Average_Lead_Time"])

    else:
        st.info("Shipping analysis requires Order Date and Ship Date columns.")

# Dataset column information
with st.expander("View dataset columns"):
    st.write(df.columns.tolist())

st.caption("Nassau Candy Optimization | Python, Pandas and Streamlit")