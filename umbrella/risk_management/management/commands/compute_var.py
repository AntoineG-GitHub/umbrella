from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from risk_management.src.var_computation import compute_historical_var
import sys

class Command(BaseCommand):
    help = "Compute Value at Risk (VaR) for the portfolio on a specific date"

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, required=True, help='Computation date in YYYY-MM-DD format')
    
    def handle(self, *args, **options):
        date_str = options['date']
        computation_date = parse_date(date_str)

        if not computation_date:
            self.stderr.write(self.style.ERROR("Invalid date format. Use YYYY-MM-DD."))
            sys.exit(1)

        if computation_date.weekday() >= 5:
            self.stderr.write(self.style.WARNING("Market is closed on weekends. Skipping VAR computation."))
            return

        try:
            compute_historical_var(computation_date)

            self.stdout.write(self.style.SUCCESS(f"VAR computed for {computation_date}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during VAR computation: {str(e)}"))