from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, Case, When, F, DecimalField
from django.db.models.functions import Abs

from transactions.models import Transaction
from data_ingestion.models import HistoricalPrice
import logging

logger = logging.getLogger(__name__)

def get_investment_value(date) -> Decimal:
    asset_values = {}
    total_value = Decimal("0.0")

    def sum_tx(tx_type):
        return Transaction.objects.filter(type=tx_type, date__lte=date).annotate(abs_amount=Abs("amount")).aggregate(total=Sum("abs_amount"))["total"] or Decimal("0")

    cash = sum_tx("deposit") + sum_tx("dividend") + sum_tx("sell") \
         - (abs(sum_tx("withdrawal")) + abs(sum_tx("fee")) + abs(sum_tx("buy")))

    total_value += cash

    asset_tx = (
        Transaction.objects
        .filter(date__lte=date, type__in=["buy", "sell"])
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

    for item in asset_tx:
        ticker = item["ticker"]
        net_qty = Decimal(item["total_qty"])
        if net_qty == 0:
            continue

        try:
            price = HistoricalPrice.objects.get(ticker=ticker, date=date)
            close_eur = price.close_euro
            value = (net_qty * close_eur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            asset_values[ticker] = (value, net_qty)
            total_value += value
        except HistoricalPrice.DoesNotExist:
            logger.warning(f"Missing historical price for {ticker} on {date}")
    
    logger.info(f"Assets in the portfolio: {asset_values}")

    return total_value, asset_tx
