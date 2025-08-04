from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Abs
from transactions.models import Transaction

def compute_total_metrics(date, fund_value: Decimal):
    def sum_tx(tx_type):
        return Transaction.objects.filter(type=tx_type, date__lte=date).annotate(abs_amount=Abs("amount")).aggregate(total=Sum("abs_amount"))["total"] or Decimal("0")

    deposits = sum_tx("deposit")
    withdrawals = sum_tx("withdrawal")
    dividends = sum_tx("dividend")
    fees = sum_tx("fee")
    buy = sum_tx("buy")
    sell = sum_tx("sell")

    cash = deposits + dividends + sell - (abs(withdrawals) + abs(fees) + abs(buy))
    asset_value = fund_value - cash
    net_inflows = deposits - abs(withdrawals)
    gain_or_loss = fund_value - net_inflows
    portfolio_value = fund_value - cash

    return gain_or_loss, cash, portfolio_value, net_inflows, asset_value
