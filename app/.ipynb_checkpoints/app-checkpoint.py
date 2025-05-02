import os
import pandas as pd

import matplotlib.pyplot as plt

import streamlit as st

from analysis import calculate_metrics, plot_close_vs_publications
from data_fetching import merge_data

# Load data
data_dir          = os.path.join("..", "data")
market_daily      = pd.read_parquet(os.path.join(data_dir, "daily_stocks.parquet"))
publication_daily = pd.read_parquet(os.path.join(data_dir, "daily_publications.parquet"))
df_daily          = merge_data(market_daily, publication_daily, period="D")

# Streamlit App
def main():
    st.title("Stock Publication and Trend Analysis")

    # Sidebar for user input
    st.sidebar.header("User Input")
    industries = df_daily['industry'].unique()
    industry   = st.sidebar.selectbox("Select Industry", industries)

    # Plot close price vs publications
    st.subheader(f"Close Price vs Publications for {industry}")
    fig = plot_close_vs_publications(df_daily, industry)
    st.pyplot(fig)

    # Display Industry Metrics
    st.subheader(f"Metrics for {industry}")
    metrics, r_squared = calculate_metrics(df_daily, industry)
    st.write("Correlation Results:")
    st.dataframe(metrics)

    st.write(f"Adjusted R-squared: {r_squared:.4f}%")

if __name__ == "__main__":
    main()
