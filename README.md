# Scientific Literature & Sector Stock Trend Analysis

This project explores the relationship between trends in scientific publication activity and short-term stock market performance in related sectors.

## Problem Statement

Scientific research often precedes innovation, which in turn impacts market dynamics. This project investigates whether patterns in scientific publication activity (e.g., number of papers, keyword frequency) can help predict near-term price movements in related market sectors.

We aim to answer:
- Can increased research activity in a field (e.g., biotech, energy) signal upcoming movements in stock prices of the corresponding sector?
- Are these signals merely correlated, or is there evidence of predictive relationships?

---

## Data Sources

- **Scientific Literature**: [Open Alex]([https://api.semanticscholar.org/](https://openalex.org/))  
  - Paper metadata including titles, abstracts, and publication dates.
- **Stock Market Sector Data**: [Yahoo Finance via `yfinance`](https://pypi.org/project/yfinance/)  
  - Sector ETFs like:
    - XLV → Healthcare
    - XLE → Energy
    - XLK → Technology

---

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/MusondaSinkala/stock-publication-analyzer.git
```

### 2. Build & Run the Docker Container

docker build -t literature-trends-app .<br>
docker run -p 8501:8501 literature-trends-app

Then open your browser to http://localhost:8501

### (Alternative) Run Locally without Docker

pip install -r requirements.txt<br>
cd app<br>
streamlit run app/app.py

---

## Features

- Trend comparison between weekly paper counts and sector ETF performance
- Correlation analysis (Pearson)
- Regression modelling
- Streamlit web UI (accessible at https://publicationstocktracker.streamlit.app/)

## Limitations

- OpenAlex rate limits and data granularity slow down analysis.
- Research activity may correlate with ETF movements but not cause them. Other features may be needed to determine causes of stock price movements.

## Folder Structure
```
literature-stock-trends/
├── app/
│   ├── app.py                  # Streamlit web app
│   ├── data_fetching.py        # Data ingestion scripts
│   ├── feature_engineering.py  # Periodic count aggregation
│   ├── analysis.py             # Correlation computation
│   └── utils.py                # Helper functions
├── data/                       # Local storage for testing
├── notebooks/                  # For EDA
├── Dockerfile
├── requirements.txt
└── README.md
```

## Author
Musonda Sinkala<br>
mks9887@nyu.edu
