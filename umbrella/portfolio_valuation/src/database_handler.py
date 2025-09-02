
from decimal import Decimal, ROUND_HALF_UP
from data_ingestion.models import HistoricalPrice
from portfolio_valuation.models import DailyPortfolioSnapshot
from portfolio_valuation.models import UserShareSnapshot
from portfolio_valuation.models import PortfolioCompositionSnapshot
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, date):
        self.date = date

    def save_to_PortfolioCompositionSnapshot(self, portfolio_composition):

        for item in portfolio_composition:
            ticker = item["ticker"]
            net_qty = Decimal(item["total_qty"])
            if net_qty == 0:
                continue

            try:
                price = HistoricalPrice.objects.get(ticker=ticker, date=self.date)
                close_eur = price.close_euro
                value = (net_qty * close_eur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except HistoricalPrice.DoesNotExist:
                logger.warning(f"Missing historical price for {ticker} on {self.date}")
        

            PortfolioCompositionSnapshot.objects.create(
                ticker=ticker,
                date=self.date,
                quantity=net_qty,
                value_eur=value
            )

    def save_to_DailyPortfolioSnapshot(self, fund_value, total_units, nav, nav_returns, gain_or_loss, cash, port_val, inflows):

        DailyPortfolioSnapshot.objects.update_or_create(
            date=self.date,
            defaults={
                "total_value": fund_value,
                "total_units": total_units,
                "nav_per_unit": nav,
                "nav_returns": nav_returns,
                "gain_or_loss": gain_or_loss,
                "cash": cash,
                "net_inflows": inflows,
                "portfolio_total_value": port_val
            }
        )

    def save_to_UserShareSnapshot(self, new_user_units):
        for user_id, units in new_user_units.items():
            UserShareSnapshot.objects.update_or_create(
                date=self.date,
                user_id=user_id,
                defaults={"units_held": units}
            )