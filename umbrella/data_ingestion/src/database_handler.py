from django.utils import timezone
from django.db import connection
from datetime import datetime

class DatabaseHandler:
    def __init__(self, model, table_name="daily_stock_prices"):
        self.model = model
        self.table_name = table_name

    def ensure_table_exists(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s;", [self.table_name])
            if not cursor.fetchone():
                with connection.schema_editor() as schema_editor:
                    self.model._meta.db_table = self.table_name
                    schema_editor.create_model(self.model)

    def save_prices(self, ticker, currency, merged_data):
        """
        Save the daily stock prices for a given ticker and currency.
        """
        self.model.objects.filter(ticker=ticker).delete()
        for date, value in merged_data.items():
            naive_date = datetime.strptime(date, "%Y-%m-%d")
            aware_date = timezone.make_aware(naive_date).date()
            rate = value.get("exchange_rate")
            self.model.objects.update_or_create(
                ticker=ticker,
                currency=currency,
                date=aware_date,
                open=value.get("1. open"),
                high=value.get("2. high"),
                low=value.get("3. low"),
                close=value.get("4. close"),
                volume=value.get("5. volume"),
                open_euro=float(value.get("1. open")) * float(rate) if rate else None,
                high_euro=float(value.get("2. high")) * float(rate) if rate else None,
                low_euro=float(value.get("3. low")) * float(rate) if rate else None,
                close_euro=float(value.get("4. close")) * float(rate) if rate else None,
                nav=value.get("nav")
            )

    def save_company_information(self, ticker, data: dict):
        # Overwrite data by deleting all existing rows
        self.model.objects.filter(ticker=ticker).delete()
        self.model.objects.create(
            ticker=ticker,
            name=data.get("Name"),
            description=data.get("Description"),
            sector=data.get("Sector"),
            industry=data.get("Industry"),
            currency=data.get("Currency"),
            market_cap=data.get("MarketCapitalization"),
            ebitda=data.get("EBITDA"),
            eps=data.get("EPS"),
            pe_ratio=data.get("PERatio"),
            dividend_yield=data.get("DividendYield"),
            dividend_per_share=data.get("DividendPerShare"),
            analyst_rating_buy=data.get("AnalystRatingBuy"),
            analyst_rating_strong_buy=data.get("AnalystRatingStrongBuy"),
            analyst_rating_hold=data.get("AnalystRatingHold"),
            analyst_rating_sell=data.get("AnalystRatingSell"),
            analyst_rating_strong_sell=data.get("AnalystRatingStrongSell"),
            trailing_pe=data.get("TrailingPE"),
            forward_pe=data.get("ForwardPE"),
            price_to_sales_ratio_ttm=data.get("PriceToSalesRatioTTM"),
            price_to_book_ratio=data.get("PriceToBookRatio"),
            ev_to_revenue=data.get("EVToRevenue"),
            ev_to_ebitda=data.get("EVToEBITDA"),
            beta=data.get("Beta"),
            week_52_high=data.get("52WeekHigh"),
            week_52_low=data.get("52WeekLow"),
            day_50_moving_average=data.get("50DayMovingAverage"),
            day_200_moving_average=data.get("200DayMovingAverage"),
            shares_outstanding=data.get("SharesOutstanding"),
            dividend_date=data.get("DividendDate"),
            ex_dividend_date=data.get("ExDividendDate")
        )
    
    def save_daily_exchange_rates(self, from_currency, to_currency, data):
        print(f"Saving exchange rates from {from_currency} to {to_currency}")
        self.model.objects.filter(from_currency=from_currency).delete()
        for date, value in data.items():
            naive_datetime = datetime.strptime(date, "%Y-%m-%d")
            aware_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
            self.model.objects.update_or_create(
                from_currency=from_currency,
                to_currency=to_currency,
                open=value.get("1. open"),
                high=value.get("2. high"),
                low=value.get("3. low"),
                close=value.get("4. close"),
                date=aware_datetime
            ) 