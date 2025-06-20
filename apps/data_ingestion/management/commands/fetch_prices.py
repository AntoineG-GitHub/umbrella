from django.core.management.base import BaseCommand
from src.core.alpha_vantage_client import AlphaVantageClient
import os

class Command(BaseCommand):
    help = "Fetch data from API and save to database"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Fetching historical prices..."))
        client = AlphaVantageClient(os.getenv("ALPHA_VANTAGE_API_KEY"))
        client.save_daily_prices("AAPL")
