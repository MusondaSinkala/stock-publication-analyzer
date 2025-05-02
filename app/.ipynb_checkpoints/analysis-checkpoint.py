import os

import numpy as np
import pandas as pd

import statsmodels.api as sm
import scipy.stats as stats

import matplotlib.pyplot as plt
import seaborn as sns

def calculate_metrics(df, industry):
    """
    Performs correlation and multiple linear regression analysis between 
    publication/citation activity (and their time-lagged versions) and ETF price data.

    Parameters:
        df (pd.DataFrame): DataFrame containing publication and citation counts (including lagged versions), 
                           ETF sector price data (e.g., 'close', 'pct_change_close', 'close_vol_3d'), 
                           and metadata including 'industry' and 'date'.
        industry (str): Name of the industry sector to filter the analysis on (e.g., 'Technology', 'Healthcare').

    Returns:
        results (pd.DataFrame): Summary table containing:
            - Pearson correlation coefficients between each predictor and:
                * ETF closing price
                * Daily percentage change in closing price
                * 3-day price volatility
            - Beta coefficients and p-values from a multiple linear regression model with 
              'pct_change_close' as the dependent variable.

        r_squared_mlr (float): R-squared value indicating the explanatory power of the regression model.
    """
    # Filter by industry and date
    df_filtered = df[(df['industry'] == industry) & (df['date'] >= '2025-04-01')].copy()
    df_filtered = df_filtered.fillna(0)  # Replace missing values with 0

    # Define predictor variables
    publication_variables = ['publications', 'publications_1', 'publications_3', 'publications_7', 'publications_14', 'publications_30']
    citation_variables    = ['citations', 'citations_1', 'citations_3', 'citations_7', 'citations_14', 'citations_30']
    predictors            = publication_variables + citation_variables

    # Initialize results DataFrame
    results = pd.DataFrame(index = ['beta', 'p_value', 'correlation_close', 
                                    'correlation_pct_change_close', 'correlation_volatility'
                                   ],
                           columns = predictors)

    # Loop through each predictor for correlation analysis
    for var in predictors:
        # Correlations
        results.at['correlation_close', var]            = stats.pearsonr(df_filtered[var], df_filtered['close'])[0]
        results.at['correlation_pct_change_close', var] = stats.pearsonr(df_filtered[var], df_filtered['pct_change_close'])[0]
        results.at['correlation_volatility', var]       = stats.pearsonr(df_filtered[var], df_filtered['close_vol_3d'])[0]

    # Fit Multiple Linear Regression model
    X_mlr     = sm.add_constant(df_filtered[predictors])
    y_mlr     = df_filtered['pct_change_close']
    mlr_model = sm.OLS(y_mlr, X_mlr).fit()

    # Extract full MLR beta coefficients and p-values
    mlr_summary = pd.DataFrame({'beta_mlr': mlr_model.params.drop('const'),
                                'p_value_mlr': mlr_model.pvalues.drop('const')
                              })

    # Populate beta and p_value rows in results table
    results.loc['beta', mlr_summary.index]    = mlr_summary['beta_mlr']
    results.loc['p_value', mlr_summary.index] = mlr_summary['p_value_mlr']

    # Extract adjust R² of the full model
    adjusted_r_squared_mlr = round(mlr_model.rsquared_adj * 100, 2)

    return results, adjusted_r_squared_mlr

def plot_close_vs_publications(df, industry):
    """
    Generates a dual-axis plot of ETF sector closing prices and publication volume over time for a given industry.

    Parameters:
        df (pd.DataFrame): DataFrame containing industry-specific ETF data, including 
                           'date', 'close' prices, and 'publications' counts.
        industry (str): The name of the industry sector to filter and visualize (e.g., 'Technology').

    Returns:
        matplotlib.figure.Figure: The matplotlib figure object containing the plot.
    """
    # Filter the dataset for the specific industry and date range
    df_filtered = df[(df['industry'] == industry) & (df['date'] >= '2025-03-01')].copy()
    
    # Ensure that the 'date' column is of datetime type
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])
    
    # Create a figure and axis
    fig, ax1 = plt.subplots(figsize = (12, 6))

    # Plot the 'close' price
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Close Price ($)', color = 'tab:blue')
    ax1.plot(df_filtered['date'], df_filtered['close'], color = 'tab:blue', label = 'Close Price', marker = 'o')
    ax1.tick_params(axis = 'y', labelcolor = 'tab:blue')
    
    # Create a second y-axis to plot publications
    ax2 = ax1.twinx()
    ax2.set_ylabel('Publications', color = 'tab:green')
    ax2.bar(df_filtered['date'], df_filtered['publications'], color = 'tab:green', alpha = 0.6, label = 'Publications')
    ax2.tick_params(axis = 'y', labelcolor = 'tab:green')
    
    # Add title and layout
    plt.title(f'Close Price and Publications for {industry} (From March 2025)', fontsize = 14)
    fig.tight_layout()
    
    return fig