from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from portfolio_valuation.src.valuation import ValuationService
import sys


class Command(BaseCommand):
    help = "Compute fund valuation for a specific date"

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, required=True, help='Valuation date in YYYY-MM-DD format')

    def handle(self, *args, **options):
        date_str = options['date']
        valuation_date = parse_date(date_str)

        if not valuation_date:
            self.stderr.write(self.style.ERROR("Invalid date format. Use YYYY-MM-DD."))
            sys.exit(1)

        if valuation_date.weekday() >= 5:
            self.stderr.write(self.style.WARNING("Market is closed on weekends. Skipping valuation."))
            return

        try:
            service = ValuationService(valuation_date)
            service.compute()
            self.stdout.write(self.style.SUCCESS(f"Valuation computed for {valuation_date}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during valuation: {str(e)}"))
