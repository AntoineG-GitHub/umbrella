from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run all daily data fetching tasks"

    def handle(self, *args, **options):
        success, failed = [], []

        # 1. Fetch exchange rates first
        self.stdout.write("Fetching exchange rates (USD)...")
        try:
            call_command("fetch_exchange_rates", "--from_currency=USD")
            self.stdout.write(self.style.SUCCESS("Successfully fetched exchange rates"))
            success.append("exchange_rates")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch exchange rates: {e}"))
            failed.append("exchange_rates")

        # 2. Fetch stock data for all tickers
        tickers = ["AMD", "CRM", "NVDA", "MSFT", "PHYS", "RITM", "SGLD.MI", "SPYD.DE", "SXLP.MI", "WIX", "SPY"]

        for ticker in tickers:
            self.stdout.write(f"Fetching data for {ticker}...")
            try:
                call_command("fetch_company_info", f"--ticker={ticker}")
                self.stdout.write(self.style.SUCCESS(f"Successfully fetched company info for {ticker}"))
                success.append(ticker)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to fetch company info for {ticker}: {e}"))
                failed.append(ticker)
            try:
                call_command("fetch_stock_data", f"--ticker={ticker}")
                self.stdout.write(self.style.SUCCESS(f"Successfully fetched data for {ticker}"))
                success.append(ticker)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to fetch data for {ticker}: {e}"))
                failed.append(ticker)

        # Summary
        self.stdout.write("\n✅ Success: " + ", ".join(success) if success else "✅ None succeeded")
        self.stdout.write("❌ Failed: " + ", ".join(failed) if failed else "❌ None failed")
