from django.db import models

class HistoricalPrice(models.Model):
    """
    Model for storing historical price data for financial instruments.
    Tracks daily OHLCV data in original currency and EUR equivalent.
    """
    ticker = models.CharField(max_length=10)
    currency = models.CharField(max_length=10, null=True)
    open = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    close = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    volume = models.BigIntegerField(null=True)
    open_euro = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    high_euro = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    low_euro = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    close_euro = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    date = models.DateField()

class BaseHistoricalExchangeRate(models.Model):
    """
    Model for storing historical exchange rate data between two currencies.
    Tracks daily exchange rate data for a specific currency pair.
    """
    from_currency = models.CharField(max_length=3)
    to_currency = models.CharField(max_length=3)
    open = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    close = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    date = models.DateField()

class TickerInfo(models.Model):
    """
    Model for storing additional information about a financial instrument.
    Tracks details such as name, description, sector, industry, market cap, etc.
    """
    ticker = models.CharField(max_length=10)
    name = models.TextField(null=True)
    description = models.TextField(null=True)
    sector = models.TextField(null=True)
    industry = models.TextField(null=True)
    market_cap = models.BigIntegerField(null=True)
    exchange = models.CharField(max_length=10, null=True)
    currency = models.CharField(max_length=10, null=True)
    country = models.CharField(max_length=50, null=True)
    address = models.TextField(null=True)
    official_site = models.URLField(null=True)
    fiscal_year_end = models.CharField(max_length=20, null=True)
    latest_quarter = models.DateField(null=True)
    ebitda = models.BigIntegerField(null=True)
    pe_ratio = models.FloatField(null=True)
    peg_ratio = models.FloatField(null=True)
    book_value = models.FloatField(null=True)
    dividend_per_share = models.FloatField(null=True)
    dividend_yield = models.FloatField(null=True)
    eps = models.FloatField(null=True)
    revenue_per_share_ttm = models.FloatField(null=True)
    profit_margin = models.FloatField(null=True)
    operating_margin_ttm = models.FloatField(null=True)
    return_on_assets_ttm = models.FloatField(null=True)
    return_on_equity_ttm = models.FloatField(null=True)
    revenue_ttm = models.BigIntegerField(null=True)
    gross_profit_ttm = models.BigIntegerField(null=True)
    diluted_eps_ttm = models.FloatField(null=True)
    quarterly_earnings_growth_yoy = models.FloatField(null=True)
    quarterly_revenue_growth_yoy = models.FloatField(null=True)
    analyst_target_price = models.FloatField(null=True)
    analyst_rating_strong_buy = models.IntegerField(null=True)
    analyst_rating_buy = models.IntegerField(null=True)
    analyst_rating_hold = models.IntegerField(null=True)
    analyst_rating_sell = models.IntegerField(null=True)
    analyst_rating_strong_sell = models.IntegerField(null=True)
    trailing_pe = models.FloatField(null=True)
    forward_pe = models.FloatField(null=True)
    price_to_sales_ratio_ttm = models.FloatField(null=True)
    price_to_book_ratio = models.FloatField(null=True)
    ev_to_revenue = models.FloatField(null=True)
    ev_to_ebitda = models.FloatField(null=True)
    beta = models.FloatField(null=True)
    week_52_high = models.FloatField(null=True)
    week_52_low = models.FloatField(null=True)
    day_50_moving_average = models.FloatField(null=True)
    day_200_moving_average = models.FloatField(null=True)
    shares_outstanding = models.BigIntegerField(null=True)
    dividend_date = models.DateField(null=True)
    ex_dividend_date = models.DateField(null=True)
