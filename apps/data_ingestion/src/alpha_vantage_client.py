import requests
from data_ingestion.src.api_fetcher import APIFetcher
import logging

logger = logging.getLogger(__name__)

class AlphaVantageClient(APIFetcher):
    """
    This class is used to get data from the Alpha Vantage API.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://www.alphavantage.co/query"

            
    def get_daily_time_series(self, ticker: str) -> dict:
        """
        Get the daily stock price series for a given ticker.
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": self.api_key,
            "outputsize": "full"
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            logger.error(f"Request error occurred: {err}")

    def get_overview(self, ticker: str) -> dict:
        """
        Get the company overview for a given ticker.
        """
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": self.api_key
        }
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()
        if response.empty:
            logger.warning(f"No data found for ticker: {ticker}")
            raise ValueError(f"No data found for ticker: {ticker}")
        return response.json()

    def get_exchange_rates(self, from_symbol: str, to_symbol="EUR") -> dict:
        """
        Get the exchange rates for a given currency pair.
        """
        params = {
            "function": "FX_DAILY",
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "outputsize": "full",
            "apikey": self.api_key
        }
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()
        return response.json()
