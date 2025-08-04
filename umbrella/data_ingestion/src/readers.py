from data_ingestion.models import TickerInfo
from data_ingestion.models import HistoricalPrice, BaseHistoricalExchangeRate
from django.utils.dateparse import parse_date
from django.utils.timezone import now

class CompanyInfoReader:
    def get_info(self, ticker: str):
        return TickerInfo.objects.filter(ticker=ticker).first()

class PriceReader:
    def get_prices(self, ticker: str, start_date=None, end_date=None):
        queryset = HistoricalPrice.objects.filter(ticker=ticker)

        if start_date:
            queryset = queryset.filter(date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date__lte=parse_date(end_date))
        else:
            queryset = queryset.filter(date__lte=now())

        return queryset.order_by('date')

class ExchangeRateReader:
    def get_exchange_rates(self, from_currency: str, to_currency='EUR', start_date=None, end_date=None):
        queryset = BaseHistoricalExchangeRate.objects.filter(from_currency=from_currency, to_currency=to_currency)  

        if start_date:
            queryset = queryset.filter(date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date__lte=parse_date(end_date))
        else:
            queryset = queryset.filter(date__lte=now())

        return queryset.order_by('date')
