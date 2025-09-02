import pandas as pd
from portfolio_valuation.models import DailyPortfolioSnapshot
from data_ingestion.models import HistoricalPrice
from transactions.models import Transaction
from django.db.models import Sum, Case, When, F, DecimalField
from decimal import Decimal
from datetime import timedelta

def get_last_snapshot_date(date):
    """
    Get the most recent date for which a DailyPortfolioSnapshot exists before the given date.
    Note that there is no data for weekends days.
    """
    snapshot = DailyPortfolioSnapshot.objects.filter(date__lt=date).order_by("-date").first()
    return snapshot.date if snapshot else None

def get_portfolio_composition(date):
    """
    Get the portfolio composition (ticker and quantity) as of the given date.
    This is done by aggregating all buy/sell transactions up to that date.
    """

    # Aggregate buy/sell transactions to find net quantity per ticker
    asset_tx = (
        Transaction.objects
        .filter(type__in=["buy", "sell"])
        .values("ticker")
        .annotate(
            total_qty=Sum(
                Case(
                    When(type="buy", then=F("shares")),
                    When(type="sell", then=-F("shares")),
                    default=Decimal("0"),
                    output_field=DecimalField(),
                )
            )
        )
    )

    portfolio_composition = {}
    for item in asset_tx:
        if item["total_qty"] > 0:
            portfolio_composition[item["ticker"]] = Decimal(item["total_qty"])
    
    return portfolio_composition

def compute_historical_var(date):
    """
    Compute historical Value at Risk (VaR) for the portfolio on the given date
    for a 95% and 99% confidence level at 1-day, 5-day, and 10-day horizons.
    This is done through reconstructing the theoretical portfolio values over the past year given the current portfolio composition.
    """
    from risk_management.models import VARComputation

    last_date = get_last_snapshot_date(date)

    portfolio_composition = get_portfolio_composition(last_date)

    # Build a DataFrame of daily portfolio value over the past year
    portfolio_values = {}
    for stock, qty in portfolio_composition.items():
        prices = HistoricalPrice.objects.filter(
            ticker=stock,
            date__lt=last_date,
            date__gte=last_date - timedelta(days=365)
        ).values("date", "close_euro")
        for p in prices:
            d = p["date"]
            v = p["close_euro"] or Decimal("0")
            portfolio_values.setdefault(d, Decimal("0"))
            portfolio_values[d] += qty * v # Sum value of each stock * quantity

    # Convert to DataFrame and sort by date
    df = pd.DataFrame(list(portfolio_values.items()), columns=["date", "value"])
    df = df.sort_values("date").set_index("date")

    # Compute daily returns
    df["returns"] = df["value"].pct_change().dropna()

    # Compute VaR for 1, 5, and 10-day horizons
    var_results = {}
    for horizon in [1, 5, 10]:
        # Rolling sum of returns for multi-day horizon
        rolling_returns = df["returns"].rolling(window=horizon).sum().dropna()
        var_95 = -rolling_returns.quantile(0.05)
        var_99 = -rolling_returns.quantile(0.01)
        es_95 = -rolling_returns[rolling_returns <= rolling_returns.quantile(0.05)].mean()
        es_99 = -rolling_returns[rolling_returns <= rolling_returns.quantile(0.01)].mean()
        var_results[horizon] = {
            "var_95": var_95,
            "var_99": var_99,
            "es_95": es_95,
            "es_99": es_99,
        }

    # Save the 1-day VaR and ES to the database
    VARComputation.objects.update_or_create(
        date=last_date,
        defaults={
            "var_95_1day": var_results[1]["var_95"],
            "var_95_1day_amount": var_results[1]["var_95"] * float(df["value"].iloc[-1]),
            "var_99_1day": var_results[1]["var_99"],
            "var_99_1day_amount": var_results[1]["var_99"] * float(df["value"].iloc[-1]),
            "expected_shortfall_95_1day": var_results[1]["es_95"],
            "expected_shortfall_95_1day_amount": var_results[1]["es_95"] * float(df["value"].iloc[-1]),
            "expected_shortfall_99_1day": var_results[1]["es_99"],
            "expected_shortfall_99_1day_amount": var_results[1]["es_99"] * float(df["value"].iloc[-1]),
            "var_95_5day": var_results[5]["var_95"],
            "var_95_5day_amount": var_results[5]["var_95"] * float(df["value"].iloc[-1]),
            "var_99_5day": var_results[5]["var_99"],
            "var_99_5day_amount": var_results[5]["var_99"] * float(df["value"].iloc[-1]),
            "expected_shortfall_95_5day": var_results[5]["es_95"],
            "expected_shortfall_95_5day_amount": var_results[5]["es_95"] * float(df["value"].iloc[-1]),
            "expected_shortfall_99_5day": var_results[5]["es_99"],
            "expected_shortfall_99_5day_amount": var_results[5]["es_99"] * float(df["value"].iloc[-1]),
            "var_95_10day": var_results[10]["var_95"],
            "var_95_10day_amount": var_results[10]["var_95"] * float(df["value"].iloc[-1]),
            "var_99_10day": var_results[10]["var_99"], 
            "var_99_10day_amount": var_results[10]["var_99"] * float(df["value"].iloc[-1]),
            "expected_shortfall_95_10day": var_results[10]["es_95"],
            "expected_shortfall_95_10day_amount": var_results[10]["es_95"] * float(df["value"].iloc[-1]),
            "expected_shortfall_99_10day": var_results[10]["es_99"],
            "expected_shortfall_99_10day_amount": var_results[10]["es_99"] * float(df["value"].iloc[-1]),
        }
    )

    return var_results





