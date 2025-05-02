import os

import pandas as pd

def merge_data(market_df, publication_df, period = "D"):
    """
    Merges market and publication dataframes and returns a dataset with lagged publication and citation data.

    Parameters:  
        market_df (pd.DataFrame): Market data (must include 'Date' and 'Industry').
        publication_df (pd.DataFrame): Publication data (must include 'date' and 'sector').
        period (str): One of 'daily', 'weekly', 'monthly'. Controls the aggregation period.

    Returns:
        pd.DataFrame: Merged dataframe with lagged features.
    """

    # Determine string conversion based on period
    if period == "D":
        market_df["Date_str"]      = market_df["Date"].dt.strftime("%Y-%m-%d")
        publication_df["date_str"] = pd.to_datetime(publication_df["date"]).dt.strftime("%Y-%m-%d")
    elif period == "W":
        market_df["Date_str"]      = market_df["Date"].dt.to_period("W").astype(str)
        publication_df["date_str"] = pd.to_datetime(publication_df["date"]).dt.to_period("W").astype(str)
    elif period == "M":
        market_df["Date_str"]      = market_df["Date"].dt.to_period("M").astype(str)
        publication_df["date_str"] = pd.to_datetime(publication_df["date"]).dt.to_period("M").astype(str)
    else:
        raise ValueError("Invalid period. Must be 'D', 'W', or 'M'.")

    # Aggregate publication data
    pub_agg = publication_df.groupby(["date_str", "sector"])[["publications", "citations"]].sum().reset_index()

    # Merge market and publication data
    merged_df = pd.merge(
        market_df,
        pub_agg,
        left_on  = ["Date_str", "Industry"],
        right_on = ["date_str", "sector"],
        how      = "left"
    )

    # Sort for lag generation
    merged_df.sort_values(by = ["Industry", "Date"], inplace = True)

    # Create backward-looking lags
    lags = [1, 3, 7, 14, 30]
    for lag in lags:
        merged_df[f"publications_{lag}"] = merged_df.groupby("Industry")["publications"].shift(lag)
        merged_df[f"citations_{lag}"]    = merged_df.groupby("Industry")["citations"].shift(lag)

    # Create closing etf percent change column
    merged_df["pct_change_close"] = (merged_df.sort_values(["Industry", "date_str"])
                                              .groupby("Industry")["Close"]
                                              .pct_change() * 100
                                     )

    # Create closing etf 3-day volatility column
    merged_df['close_vol_3d'] = merged_df['Close'].rolling(window = 3).std()

    # Replace NaN values with 0s in specific columns
    nan_columns = ["pct_change_close", "close_vol_3d", "publications", "citations"] + \
                  [f"publications_{lag}" for lag in lags] + \
                  [f"citations_{lag}" for lag in lags]
    
    merged_df[nan_columns] = merged_df[nan_columns].fillna(0)

    # Final columns to keep
    keep_cols = ["Date_str", "Industry", "Close", "pct_change_close", "close_vol_3d", "High", "Low", "Open", "Volume",
                 "publications", "citations"] + \
                [f"publications_{lag}" for lag in lags] + \
                [f"citations_{lag}" for lag in lags]

    merged_df = merged_df[keep_cols].reset_index(drop = True)

    merged_df.rename(columns = {"Date_str": "date", "Industry": "industry", "Close": "close", "High": "high",
                                "Low": "low", "Open": "open", "Volume": "volume"
                               }, inplace = True)
    
    return merged_df