from data_ingestion.src.database_handler import DatabaseHandler
from data_ingestion.src.api_fetcher import APIFetcher
from data_ingestion.models import BaseHistoricalExchangeRate
import logging
from datetime import datetime, timedelta
import pandas as pd
from transactions.models import Transaction

logger = logging.getLogger(__name__)

class StockPriceService:
    """
    This class is responsible for fetching stock prices and exchange rates from the Alpha Vantage API,
    enriching the data with additional information, and saving it to the database using the DatabaseHandler.
    """
    def __init__(self, client: APIFetcher, repository: DatabaseHandler):
        self.client = client
        self.repo = repository
    
    def _get_currency(self, ticker: str) -> str:
        """
        Fetches the currency of the stock ticker from the API.
        """

        try:
            overview = self.client.get_overview(ticker)
            currency = overview.get("Currency")
            logging.info(f"Currency for {ticker} is {currency}")
        except Exception as e:
            logger.error(f"Error fetching the currency for {ticker}: {e}")
            raise e

        exchange_rates = {}
        if (currency != "EUR"):
            exchange_rates = BaseHistoricalExchangeRate.objects.filter(from_currency=currency).values('date', 'close')
            if not exchange_rates:
                raise ValueError(f"No exchange rates found for {currency} in the database or API response.")
            else:
                # Convert database results to expected format
                exchange_rates = {
                    rate['date'].strftime("%Y-%m-%d"): {"4. close": str(rate['close'])} 
                    for rate in exchange_rates
                }

        return currency, exchange_rates

    def save_daily_prices(self, ticker: str):
        """
        Fetches and saves daily stock prices for the given ticker.
        This method retrieves daily stock prices, enriches them with exchange rates if necessary,
        and saves the data to the database.
        """
        logger.info(f"Fetching daily prices for {ticker}")
        raw_prices = self.client.get_daily_time_series(ticker)
        prices = raw_prices["Time Series (Daily)"]

        prices_df = pd.DataFrame.from_dict(prices, orient='index')
        prices_df.index = pd.to_datetime(prices_df.index).normalize()
        
        # Get data for the last 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)  # 5 years

        # Create a DataFrame with all weekdays in the date range, with timezone-aware datetime
        all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B').normalize()
        df = prices_df.reindex(all_weekdays)

        # Forward fill to replace empty values with previous day's data
        df = df.ffill()

        # --------------------------
        # Compute NAV field
        # --------------------------
        # Get the date of the first transaction from the Transaction table
        first_transaction = Transaction.objects.order_by('date').first()
        if first_transaction:
            base_date = first_transaction.date
            # Ensure base_date is normalized to match df.index
            base_date = pd.to_datetime(base_date).normalize()
        else:
            logger.warning("No transactions found in the Transaction table, NAV will be None")
            base_date = None

        if base_date in df.index:
            base_price = float(df.loc[base_date]["4. close"])
            df["nav"] = df["4. close"].astype(float) / base_price
        else:
            logger.warning(f"Base date {base_date.date()} not in data for {ticker}, NAV will be None")
            df["nav"] = None

        # --------------------------
        # Merge with exchange rates
        # --------------------------
        currency, exchange_rates = self._get_currency(ticker)

        merged = {}
        for date, row in df.iterrows():
            date_str = date.strftime("%Y-%m-%d")
            price_data = row.to_dict()
            exchange_rate = exchange_rates.get(date_str, {}).get("4. close", 1)

            merged[date_str] = {
                **price_data,
                "exchange_rate": exchange_rate,
                "nav": float(row["nav"]),
            }

        self.repo.ensure_table_exists()
        logger.info(f"Saving daily prices for {ticker} in {currency}")
        self.repo.save_prices(ticker, currency, merged)

    def save_daily_exchange_rates(self, from_symbol: str, to_symbol="EUR"):
        """
        Fetches and saves daily exchange rates from the Alpha Vantage API.
        This method retrieves daily exchange rates for the specified `from_symbol` and `to_symbol`
        """
        logger.info(f"Fetching daily exchange rates from {from_symbol} to {to_symbol}")
        raw_fx = self.client.get_exchange_rates(from_symbol, to_symbol)
        exchange_rates = raw_fx["Time Series FX (Daily)"]
        self.repo.ensure_table_exists()
        self.repo.save_daily_exchange_rates(from_symbol, to_symbol, exchange_rates)