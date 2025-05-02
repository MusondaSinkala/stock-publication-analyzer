import os
import pandas as pd

import streamlit as st

from analysis import calculate_metrics, plot_close_vs_publications
from feature_engineering import merge_data

# Load data
data_dir          = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
market_daily      = pd.read_parquet(os.path.join(data_dir, "daily_stocks.parquet"))
publication_daily = pd.read_parquet(os.path.join(data_dir, "daily_publications.parquet"))
df_daily          = merge_data(market_daily, publication_daily, period = "D")

# Streamlit App
def main():
    sectors = ["Energy", "Materials", "Industrials", "Healthcare",
               "Financials", "Technology", "Telecommunication Services",
               "Utilities", "Real Estate", "Clean Energy", "Semiconductors",
               "Renewables", "Cloud Computing", "Genomics"]\

    st.title("Stock Publication and Trend Analysis")

    # Sidebar for user input
    st.sidebar.header("Select an Industry from the drop-down list below")
    industries = sectors #df_daily['industry'].unique()
    industry   = st.sidebar.selectbox("Select Industry", industries)

    # Plot close price vs publications
    st.subheader(f"ETF Closing Price vs Publications for {industry}")
    fig = plot_close_vs_publications(df_daily, industry)
    st.pyplot(fig)

    # Display Industry Metrics
    def highlight_pval_row(row):
        if row.name == 'P-Values':
            return ['background-color: green' if val < 0.05 else '' for val in row]
        else:
            return ['' for _ in row]

    def highlight_correlation_rows(row):
        target_rows = [
            "(Correlations) Closing Price",
            "(Correlations) day-to-day Δ Closing Price",
            "(Correlations) 3-day Volatility"
        ]

        if row.name not in target_rows:
            return ['' for _ in row]

        # Apply color based on value: green (positive), red (negative), no color near 0
        styled_row = []
        for val in row:
            if abs(val) < 0.05:
                styled_row.append('')
            elif val > 0:
                styled_row.append('background-color: green')
            else:
                styled_row.append('background-color: red')
        return styled_row

    st.subheader(f"Metrics for {industry}")
    metrics, r_squared = calculate_metrics(df_daily, industry)
    metrics_styled = (metrics.style
                      .apply(highlight_pval_row, axis=1)
                      .apply(highlight_correlation_rows, axis=1))

    st.write("Correlation Results:")
    st.dataframe(metrics_styled, use_container_width = True)

    st.write(f"Adjusted R-squared: {r_squared:.2f}%")

if __name__ == "__main__":
    main()
