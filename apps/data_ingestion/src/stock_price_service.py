from data_ingestion.src.alpha_vantage_client import AlphaVantageClient
from data_ingestion.src.database_handler import DatabaseHandler
from data_ingestion.src.api_fetcher import APIFetcher
from data_ingestion.models import BaseHistoricalExchangeRate
import logging
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

class StockPriceService:
    """
    This class is responsible for fetching stock prices and exchange rates from the Alpha Vantage API,
    enriching the data with additional information, and saving it to the database using the DatabaseHandler.
    """
    def __init__(self, client: APIFetcher, repository: DatabaseHandler):
        self.client = client
        self.repo = repository

    def save_daily_prices(self, ticker: str):
        logger.info(f"Fetching daily prices for {ticker}")
        raw_prices = self.client.get_daily_time_series(ticker)
        prices = raw_prices["Time Series (Daily)"]
        try: 
            prices_df = pd.DataFrame.from_dict(prices, orient='index')
            logger.info(f"Raw prices for {ticker}: {prices_df.head()}")
            prices_df.index = pd.to_datetime(prices_df.index).normalize()
            
            # logger.info(f"Raw prices for {prices_df.index}")

            # Get data for the last 5 years
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1825)  # 5 years

            # Create a DataFrame with all weekdays in the date range, with timezone-aware datetime
            all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B').normalize()
            df = prices_df.reindex(all_weekdays)

            # Forward fill to replace empty values with previous day's data
            df = df.ffill()
            print(f"Processed prices for {df.head()}")
        except Exception as e:
            logger.error(f"Error processing prices for {ticker}: {e}")
            raise e
        # Convert to AlphaVantage format
        time_series = {}
        for date, row in df.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            time_series[date_str] = {
                "1. open": str(row['1. open']),
                "2. high": str(row['2. high']),
                "3. low": str(row['3. low']),
                "4. close": str(row['4. close']),
                "5. volume": str(int(row['5. volume']))
            }
        
        prices  = time_series

        # First check if we have ticker info in the database
        ticker_info = self.repo.model.objects.filter(ticker=ticker).first()
        if ticker_info:
            currency = ticker_info.currency
        else:
            # If no data found, fetch from API
            try:
                overview = self.client.get_overview(ticker)
            except Exception as e:
                logger.error(f"Error fetching the currency for {ticker} with AlphaVantage: {e}")
                raise e
            else:
                currency = overview.get("Currency")
            

        currency = "EUR"
        logger.info(f"Saving daily prices for {ticker} in {currency}")
        exchange_rates = {}
        if (currency != "EUR"):
            # First check if we have exchange rates in the database
            exchange_rates = BaseHistoricalExchangeRate.objects.filter(from_currency=currency).values('date', 'close')
            if not exchange_rates:
                # If no data found, fetch from API
                raw_fx = self.client.get_exchange_rates(currency)
                exchange_rates = raw_fx["Time Series FX (Daily)"]
            else:
                # Convert database results to expected format
                exchange_rates = {
                    rate['date'].strftime("%Y-%m-%d"): {"4. close": str(rate['close'])} 
                    for rate in exchange_rates
                }

        merged = {}
        for date, price_data in prices.items():
            exchange_rate = exchange_rates.get(date, {}).get("4. close", 1)
            merged[date] = {**price_data, "exchange_rate": exchange_rate}

        self.repo.ensure_table_exists()
        self.repo.save_prices(ticker, currency, merged)

    def save_daily_exchange_rates(self, from_symbol: str, to_symbol="EUR"):
        raw_fx = self.client.get_exchange_rates(from_symbol, to_symbol)
        exchange_rates = raw_fx["Time Series FX (Daily)"]
        self.repo.ensure_table_exists()
        self.repo.save_daily_exchange_rates(from_symbol, to_symbol, exchange_rates)