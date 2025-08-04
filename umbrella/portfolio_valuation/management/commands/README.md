# Management Commands for Portfolio Valuation

This folder contains Django custom management commands to compute daily and batch portfolio valuations.

## Commands

```bash
python manage.py compute_valuation --date=YYYY-MM-DD
python manage.py compute_valuation_batch --start-date=YYYY-MM-DD --end-date=YYYY-MM-DD
```