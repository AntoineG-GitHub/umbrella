import datetime
from decimal import Decimal, ROUND_HALF_UP
import logging

from django.db import transaction as db_transaction
from transactions.models import Transaction
from portfolio_valuation.models import DailyPortfolioSnapshot, UserShareSnapshot

from pricing import get_fund_value
from nav import get_previous_units, get_previous_user_units, get_nav_per_unit
from metrics import compute_total_metrics

logger = logging.getLogger(__name__)

class ValuationService:
    def __init__(self, date: datetime.date):
        self.date = date

    @db_transaction.atomic
    def compute(self):
        logger.info(f"Starting valuation for {self.date}")
        fund_value = get_fund_value(self.date)
        logger.debug(f"Fund value: {fund_value}")

        nav = get_nav_per_unit(self.date)
        prev_units = get_previous_units(self.date)
        prev_user_units = get_previous_user_units(self.date)
        logger.debug(f"Previous NAV: {nav}, Total units: {prev_units}")

        new_user_units = {}
        total_units = prev_units

        # Handle deposits
        for tx in Transaction.objects.filter(date=self.date, type="deposit"):
            units = (tx.amount / nav).quantize(Decimal("0.00000001"))
            new_user_units[tx.user_id] = new_user_units.get(tx.user_id, prev_user_units.get(tx.user_id, Decimal("0"))) + units
            total_units += units

        # Handle withdrawals
        for tx in Transaction.objects.filter(date=self.date, type="withdrawal"):
            units = (tx.amount / nav).quantize(Decimal("0.00000001"))
            prev = new_user_units.get(tx.user_id, prev_user_units.get(tx.user_id, Decimal("0")))
            new_user_units[tx.user_id] = max(prev - units, Decimal("0"))
            total_units -= units

        # Carry forward others
        for uid, prev in prev_user_units.items():
            new_user_units.setdefault(uid, prev)

        gain_or_loss, cash, port_val, inflows, asset_val = compute_total_metrics(self.date, fund_value)

        DailyPortfolioSnapshot.objects.update_or_create(
            date=self.date,
            defaults={
                "total_value": fund_value,
                "total_units": total_units,
                "nav_per_unit": nav,
                "gain_or_loss": gain_or_loss,
                "cash": cash,
                "net_inflows": inflows,
                "portfolio_total_value": port_val,
            }
        )

        UserShareSnapshot.objects.filter(date=self.date).delete()
        UserShareSnapshot.objects.bulk_create([
            UserShareSnapshot(
                date=self.date,
                user_id=uid,
                units_held=units,
                value_held=(units * nav).quantize(Decimal("0.01"))
            ) for uid, units in new_user_units.items()
        ])

        logger.info("Valuation completed.")
