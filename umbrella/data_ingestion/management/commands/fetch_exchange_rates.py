import os
import logging
from dotenv import load_dotenv
from django.core.management.base import BaseCommand, CommandError
from data_ingestion.src.alpha_vantage_client import AlphaVantageClient
from data_ingestion.src.database_handler import DatabaseHandler
from data_ingestion.src.stock_price_service import StockPriceService
from data_ingestion.models import BaseHistoricalExchangeRate

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Command(BaseCommand):
    help = "Fetch and save exchange rates for a given currency"

    def add_arguments(self, parser):
        parser.add_argument("--from_currency", type=str, required=True, help="Base currency (e.g., USD)")

    def handle(self, *args, **options):
        from_currency = options["from_currency"]

        client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY"))
        repository = DatabaseHandler(model=BaseHistoricalExchangeRate)
        service = StockPriceService(client=client, repository=repository)

        try:
            service.save_daily_exchange_rates(from_currency)
            self.stdout.write(self.style.SUCCESS(f"Successfully fetched exchange rates for {from_currency}"))
        except Exception as e:
            raise CommandError(f"Failed to fetch exchange rates: {e}")
