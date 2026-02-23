import streamlit as st
import yfinance as yf
import pandas as pd


@st.cache_data
def get_stock_data(tickers, start_date, end_date):
    """
    Fetches historical stock data for the given tickers.

    Args:
        tickers (list): List of ticker symbols.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: DataFrame of adjusted closing prices. Columns are Tickers.
    """
    if not tickers:
        return pd.DataFrame()

    try:
        # Download data
        # auto_adjust=True returns 'Close' which is adjusted for splits/dividends
        # threads=True is default but good to be explicit
        data = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False,
            threads=True,
        )

        if data.empty:
            return pd.DataFrame()

        # Handle different return structures from yfinance

        # 1. If we have a MultiIndex columns (e.g. ('Close', 'AAPL'), ('Close', 'MSFT'))
        if isinstance(data.columns, pd.MultiIndex):
            # Check if 'Close' is one of the levels
            if "Close" in data.columns.levels[0]:
                return data["Close"]
            # Fallback for some versions where level might be different
            elif "Adj Close" in data.columns.levels[0]:
                return data["Adj Close"]

        # 2. If it's a single level DataFrame (happens if only 1 ticker is valid or requested)
        else:
            # If the column name is 'Close', we need to know which ticker it belongs to
            if "Close" in data.columns:
                # If we requested multiple, but got single level 'Close', likely only 1 was valid
                # We can't easily know which one if yfinance doesn't tell us,
                # but usually yfinance returns the ticker name as column if standard download is used without group_by.
                # BUT with auto_adjust=True and 1 ticker, it returns 'Close'.
                if len(tickers) == 1:
                    return data.rename(columns={"Close": tickers[0]})

            # If the columns ARE the tickers (e.g. data['AAPL']), just return
            if all(t in data.columns for t in tickers):
                return data[tickers]

            # If we have a mix, just return what we have
            return data

        # Default fallback
        return data

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
