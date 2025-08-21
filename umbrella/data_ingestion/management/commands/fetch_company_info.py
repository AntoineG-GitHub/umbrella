import os
import logging
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from data_ingestion.src.alpha_vantage_client import AlphaVantageClient
from data_ingestion.src.yahoo_finance_client import YahooFinanceClient
from data_ingestion.src.database_handler import DatabaseHandler
from data_ingestion.models import TickerInfo

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Command(BaseCommand):
    help = "Fetch and save company info for a given ticker"

    def add_arguments(self, parser):
        parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol (e.g., AAPL)")

    def handle(self, *args, **options):
        ticker = options["ticker"]
        try:
            client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY"))
            repository = DatabaseHandler(model=TickerInfo)
            stock_info = client.get_overview(ticker)
            repository.save_company_information(ticker, stock_info)
        except Exception as e:
            logger.warning(f"AlphaVantage failed: {e}, falling back to YahooFinance.")
            client = YahooFinanceClient()
            repository = DatabaseHandler(model=TickerInfo)
            stock_info = client.get_overview(ticker)
            repository.save_company_information(ticker, stock_info)

        self.stdout.write(self.style.SUCCESS(f"Successfully fetched company info for {ticker}"))
