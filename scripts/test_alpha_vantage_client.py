import sys
import os
import django

# Add the root of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django
django.setup()

from data_ingestion.src.alpha_vantage_client import AlphaVantageClient
import os


if __name__ == "__main__":
    # Initialize the AlphaVantageClient with your API key
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    client = AlphaVantageClient(api_key)
    client.save_daily_prices("NVDA")