import datetime
from decimal import Decimal
import logging

from django.db import transaction as db_transaction
from transactions.models import Transaction
from portfolio_valuation.src.database_handler import DatabaseHandler
from .pricing import get_investment_value
from .nav import get_previous_units, get_previous_user_units, get_nav_per_unit, get_daily_returns
from .metrics import compute_total_metrics

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValuationService:
    def __init__(self, date: datetime.date):
        self.date = date
        self.database_handler = DatabaseHandler(self.date)

    @db_transaction.atomic
    def compute(self):
        logger.info(f"Starting valuation for {self.date}")
        fund_value, portfolio_composition = get_investment_value(self.date)
        logger.debug(f"Portfolio value: {fund_value}")

        nav = get_nav_per_unit(self.date)
        nav_returns = get_daily_returns(self.date, nav)
        prev_units = get_previous_units(self.date)
        prev_user_units = get_previous_user_units(self.date)
        logger.debug(f"NAV: {nav}, Total units: {prev_units}, Returns: {nav_returns}")

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


        self.database_handler.save_to_PortfolioCompositionSnapshot(portfolio_composition)
        self.database_handler.save_to_DailyPortfolioSnapshot(
            fund_value, total_units, nav, nav_returns, gain_or_loss, cash, port_val, inflows
        )
        self.database_handler.save_to_UserShareSnapshot(new_user_units)

        logger.info("Valuation completed.")
