from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from portfolio_valuation.src.valuation import ValuationService
from datetime import timedelta
import sys


class Command(BaseCommand):
    help = "Compute fund valuation between two dates (inclusive)"

    def add_arguments(self, parser):
        parser.add_argument('--start-date', type=str, required=True, help='Start date in YYYY-MM-DD format')
        parser.add_argument('--end-date', type=str, required=True, help='End date in YYYY-MM-DD format')

    def handle(self, *args, **options):
        start_date = parse_date(options['start_date'])
        end_date = parse_date(options['end_date'])

        if not start_date or not end_date or end_date < start_date:
            self.stderr.write(self.style.ERROR("Invalid date range."))
            sys.exit(1)

        current = start_date
        successes = []
        failures = []

        while current <= end_date:
            if current.weekday() < 5:
                try:
                    ValuationService(current).compute()
                    successes.append(str(current))
                except Exception as e:
                    failures.append((str(current), str(e)))
            current += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f"Completed valuations for: {successes}"))
        if failures:
            self.stderr.write(self.style.WARNING("Failures:"))
            for date, err in failures:
                self.stderr.write(f"  {date}: {err}")
