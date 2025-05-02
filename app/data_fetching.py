import os
import pandas as pd
import json
from dateutil.parser import parse
from datetime import datetime
import time

from tqdm import tqdm
import requests

import yfinance as yf

def fetch_sector_data(sector_etfs, period = "1y", interval = "1wk"):
    """
    Fetches time series data for a dictionary of sector ETFs and returns it in long format:
    Date, Industry, Open, High, Low, Close, Volume.

    Parameters:
        sector_etfs (dict): Dictionary mapping sector names to ETF tickers.
        period (str): Period of data to fetch (e.g., '1y', '6mo').
        interval (str): Data interval (e.g., '1wk', '1d').

    Returns:
        pd.DataFrame: Long-form DataFrame with columns: Date, Industry, Open, High, Low, Close, Volume.
    """
    
    tickers = list(sector_etfs.values())

    # Download historical price data
    df = yf.download(tickers, period = period, interval = interval, progress = False)

    # Convert from wide to long format
    df_long = df.stack(level = 1, future_stack = True).reset_index()

    # Rename the column holding tickers
    df_long = df_long.rename(columns = {'Ticker': 'Industry'})

    # Map tickers back to sector names
    inv_map             = {v: k for k, v in sector_etfs.items()}
    df_long['Industry'] = df_long['Industry'].map(inv_map)

    return df_long


def fetch_publication_data(concept_ids, from_date = "2025-01-01", to_date = "2025-12-31", max_per_sector = 50000, period = 'D'):
    """
    Fetches time series data for a dictionary of publications and returns it in long format:
    date, industry, publications, citations

    Parameters:
        concept_ids (dict): Dictionary mapping sector names to concept IDs.
        from_date (str): Start period of data retrieval.
        to_date (str): End period of data retrieval.
        max_per_sector (int): maximum number of publications to retrieve
        period: period of retrieval - 'D' (day), 'W' (week), 'M' (month)

    Returns:
        pd.DataFrame: Long-form DataFrame with columns: date, industry, publications, citations
    """
    
    base_url = "https://api.openalex.org/works"
    stats    = []

    for sector, concept_id in concept_ids.items():
        print(f"Fetching for {sector}")
        cursor = "*"
        total  = 0

        while True:
            filter_string = f"concepts.id:{concept_id},from_publication_date:{from_date},to_publication_date:{to_date}"
            params        = {"filter": filter_string,
                             "per-page": 200,
                             "cursor": cursor
                            }

            response = requests.get(base_url, params = params)
            data     = response.json()
            works    = data.get("results", [])
            cursor   = data.get("meta", {}).get("next_cursor")

            for work in works:
                stats.append({"sector": sector,
                              "date": work.get("publication_date"),
                              "citations": work.get("cited_by_count", 0)
                            })

            total += len(works)
            if not cursor or total >= max_per_sector:
                break

            time.sleep(1)

    df                 = pd.DataFrame(stats)
    df["date"]         = pd.to_datetime(df["date"])
    df["publications"] = 1
    if period == 'D':
        df             = df.groupby(["sector", "date"]).agg(publications = ("publications", "sum"),
                                                            citations = ("citations", "sum")).reset_index()
    elif period == 'W':
        df = df.groupby(["sector", df["date"].dt.to_period("M")]).agg(publications = ("publications", "sum"),
                                                                      citations = ("citations", "sum")
                                                                      ).reset_index()
    else:
        df = df.groupby(["sector", df["date"].dt.to_period("M")]).agg(publications = ("publications", "sum"),
                                                                      citations = ("citations", "sum")
                                                                      ).reset_index()
    df["date"]         = df["date"].astype(str)
    
    return df