import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """
    This class is used to get data from the Yahoo Finance API.
    It mimics the AlphaVantageClient interface for consistency.
    """
    def __init__(self):
        """
        Initialize the Yahoo Finance client.
        No API key is needed for Yahoo Finance.
        """
        pass

    def get_daily_time_series(self, ticker: str) -> dict:
        """
        Get the daily stock price series for a given ticker.
        Returns data in the same format as AlphaVantageClient.
        
        Args:
            ticker (str): The stock ticker symbol
            
        Returns:
            dict: A dictionary containing the daily time series data in AlphaVantage format
        """
        # Get data for the last 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)  # 5 years
        
        # Fetch data from Yahoo Finance
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)

        # Convert to AlphaVantage format
        time_series = {}
        for date, row in df.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            time_series[date_str] = {
                "1. open": str(row['Open']),
                "2. high": str(row['High']),
                "3. low": str(row['Low']),
                "4. close": str(row['Close']),
                "5. volume": str(int(row['Volume']))
            }
        
        return {
            "Time Series (Daily)": time_series
        } 
    
    def get_overview(self, ticker: str) -> dict:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        stock_info["Currency"] = stock_info["currency"]

        return stock.info
