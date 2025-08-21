import os
import logging
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from data_ingestion.src.alpha_vantage_client import AlphaVantageClient
from data_ingestion.src.yahoo_finance_client import YahooFinanceClient
from data_ingestion.src.database_handler import DatabaseHandler
from data_ingestion.src.stock_price_service import StockPriceService
from data_ingestion.models import HistoricalPrice

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Command(BaseCommand):
    help = "Fetch and save stock price data for a given ticker"

    def add_arguments(self, parser):
        parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol (e.g., AAPL)")

    def handle(self, *args, **options):
        ticker = options["ticker"]

        try:
            client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY"))
            repository = DatabaseHandler(model=HistoricalPrice)
            service = StockPriceService(client=client, repository=repository)
            service.save_daily_prices(ticker)
        except Exception as e:
            logger.warning(f"AlphaVantage failed: {e}, falling back to YahooFinance.")
            client = YahooFinanceClient()
            repository = DatabaseHandler(model=HistoricalPrice)
            service = StockPriceService(client=client, repository=repository)
            service.save_daily_prices(ticker)

        self.stdout.write(self.style.SUCCESS(f"Successfully fetched and saved data for {ticker}"))
