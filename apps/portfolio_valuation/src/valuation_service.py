import datetime
from decimal import Decimal, ROUND_HALF_UP

from transactions.models import Transaction
from data_ingestion.models import HistoricalPrice
from portfolio_valuation.models import DailyPortfolioSnapshot, UserShareSnapshot

from django.db import transaction as db_transaction
from django.db.models import Sum, Case, When, F, DecimalField
from django.db.models.functions import Abs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValuationService:
    def __init__(self, valuation_date: datetime.date):
        self.date = valuation_date

    def get_fund_value(self) -> Decimal:
        """
        Calculate the total value of a portfolio as of a specific date.
        This method aggregates buy and sell transactions to determine the net quantity
        of each asset (ticker) in the portfolio. It then retrieves the historical close
        price in EUR for each asset on the specified date and calculates the total value
        of the portfolio.
        Returns:
            Decimal: The total value of the portfolio, rounded to two decimal places.
        Notes:
            - Transactions with a net quantity of zero are ignored.
            - If the historical price for a ticker on the specified date is missing,
              that ticker is skipped in the calculation.
            - This computes the portoflio value with a load of the whole history of transactions. 
        """
        
        asset_values = {}
        total_value = Decimal("0.0")

        def get_sum(type_):
            return Transaction.objects.filter(type=type_, date__lte=self.date).annotate(abs_amount=Abs("amount")).aggregate(total=Sum("abs_amount"))["total"] or Decimal("0")

        deposits = get_sum("deposit")
        withdrawals = get_sum("withdrawal")
        dividends = get_sum("dividend")
        fees = get_sum("fee")
        buy = get_sum("buy")
        sell = get_sum("sell")

        cash = deposits + dividends + sell - (abs(withdrawals) + abs(fees) + abs(buy))

        total_value += cash

        # Aggregate buy/sell transactions to find net quantity per ticker
        asset_tx = (
            Transaction.objects
            .filter(date__lte=self.date, type__in=["buy", "sell"])
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
        )  # TODO: Fix this issue 
        logger.debug("Assets in portfolio")
        for item in asset_tx:
            ticker = item["ticker"]
            net_qty = Decimal(item["total_qty"])

            if net_qty == 0:
                continue

            # Get close price in EUR for this date
            try:
                price = HistoricalPrice.objects.get(ticker=ticker, date=self.date)
                close_eur = price.close_euro
                logger.debug(f"Ticker: {ticker}, Net Quantity: {net_qty}, Close Price: {close_eur}, Value: {net_qty * close_eur}")
                value = (net_qty * close_eur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                asset_values[ticker] = value
                total_value += value
            except HistoricalPrice.DoesNotExist:
                continue  # Skip missing prices

        return total_value

    def get_nav_per_unit(self) -> Decimal:
        """
        Returns the NAV (Net Asset Value) per unit for the current date.
        If no units exist, defaults to 1.0 (initial day of the portfolio).
        """
        # Get the last snapshot before current date
        last_date = self.get_last_available_snapshot_date(self.date)

        if last_date:
            try:
                previous_snapshot = DailyPortfolioSnapshot.objects.get(date=last_date)
                previous_units = previous_snapshot.total_units
                previous_value = previous_snapshot.total_value

                if previous_units > 0:
                    logger.debug( "Previous NAV calculation: Value = %s, Units = %s", previous_value, previous_units)
                    previous_nav = (previous_value / previous_units).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
                    return previous_nav
            except DailyPortfolioSnapshot.DoesNotExist:
                pass

        # Fallback: first day or no previous data
        return Decimal("1.0")

    def get_last_available_snapshot_date(self, current_date: datetime.date) -> datetime.date | None:
        """
        Return the most recent date before `current_date` for which a snapshot exists.
        """
        try:
            last_snapshot = DailyPortfolioSnapshot.objects.filter(date__lt=current_date).order_by("-date").first()
            return last_snapshot.date if last_snapshot else None
        except DailyPortfolioSnapshot.DoesNotExist:
            return None

    def get_previous_units(self) -> Decimal:
        """
        Total portfolio units (shares) in circulation from the previous day.
        """
        last_date = self.get_last_available_snapshot_date(self.date)
        if last_date:
            snapshot = DailyPortfolioSnapshot.objects.get(date=last_date)
            return snapshot.total_units
        return Decimal("0.0")

    def get_previous_user_units(self) -> dict:
        """
        Return a dict of {user_id: units_held} from the previous day.
        """
        last_date = self.get_last_available_snapshot_date(self.date)
        if not last_date:
            return {}
        snapshots = UserShareSnapshot.objects.filter(date=last_date)
        return {snap.user_id: snap.units_held for snap in snapshots}

    def compute_total_gain_or_loss(self, fund_value: Decimal):

        def get_sum(type_):
            return Transaction.objects.filter(type=type_, date__lte=self.date).annotate(abs_amount=Abs("amount")).aggregate(total=Sum("abs_amount"))["total"] or Decimal("0")

        deposits = get_sum("deposit")
        withdrawals = get_sum("withdrawal")
        dividends = get_sum("dividend")
        fees = get_sum("fee")
        buy = get_sum("buy")
        sell = get_sum("sell")

        cash = deposits + dividends + sell - (abs(withdrawals) + abs(fees) + abs(buy))
        asset_value = fund_value - cash
        net_inflows = deposits - abs(withdrawals)
        gain_or_loss = fund_value - net_inflows
        portfolio_value = fund_value - cash
        return gain_or_loss, cash, portfolio_value, net_inflows, asset_value

    @db_transaction.atomic
    def compute(self):
        """
        Computes and stores the daily portfolio valuation and user share snapshots.

        This is a core function that:
        1. Calculates the total portfolio value based on asset prices for the given date
        2. Processes any deposits/withdrawals that occurred on this date
        3. Updates unit allocations and NAV (Net Asset Value) per unit
        4. Tracks gains/losses and other portfolio metrics
        5. Stores snapshots of portfolio and user positions

        The function follows unit-based accounting principles:
        - Initial NAV per unit is set to 1.0
        - New deposits buy units at the current NAV price
        - Withdrawals redeem units at the current NAV price
        - NAV fluctuates based on portfolio performance

        Key metrics computed and stored:
        - total_value: Market value of all portfolio assets
        - total_units: Total fund units in circulation
        - nav_per_unit: Price per unit (total_value / total_units)
        - gain_or_loss: Total P&L considering deposits/withdrawals
        - cash: Available cash after all transactions
        - net_inflows: Net of all deposits minus withdrawals
        - portfolio_total_value: Assets + cash positions

        The function uses an atomic transaction to ensure data consistency
        when updating both portfolio and user-level snapshots.

        Returns:
            None. Results are stored in DailyPortfolioSnapshot and 
            UserShareSnapshot models.
        """
        logger.debug("###############")
        logger.info(f"Starting valuation computation for date {self.date}")

        # Step 1: Get portfolio value
        portfolio_value = self.get_fund_value()
        logger.debug(f"Total Fund value: {portfolio_value}")

        # Step 2: Get previous units
        previous_units = self.get_previous_units()
        user_units = self.get_previous_user_units()
        logger.debug(f"Previous total units: {previous_units}")
        logger.debug(f"Previous user units: {user_units}")

        # Step 3: Get deposits/withdrawals and adjust user units
        new_user_units = {}
        total_units = previous_units
        deposits = Transaction.objects.filter(date=self.date, type="deposit")
        withdrawals = Transaction.objects.filter(date=self.date, type="withdrawal")
        nav_per_unit = self.get_nav_per_unit()
        logger.info(f"Current NAV per unit: {nav_per_unit}")

        # Issue new units for deposits
        for tx in deposits:
            issued_units = (tx.amount / nav_per_unit).quantize(Decimal("0.00000001"))
            new_user_units[tx.user_id] = new_user_units.get(tx.user_id, user_units.get(tx.user_id, Decimal("0.0"))) + issued_units
            total_units += issued_units

        # Redeem units for withdrawals
        for tx in withdrawals:
            redeemed_units = (tx.amount / nav_per_unit).quantize(Decimal("0.00000001"))
            original_units = new_user_units.get(tx.user_id, user_units.get(tx.user_id, Decimal("0.0")))
            new_user_units[tx.user_id] = max(original_units - redeemed_units, Decimal("0.0"))
            total_units -= redeemed_units

        # Carry forward units for users with no activity
        for user_id, prev_units in user_units.items():
            if user_id not in new_user_units:
                new_user_units[user_id] = prev_units
               
        gain_or_loss, cash, portfolio_total, net_inflows, asset_value = self.compute_total_gain_or_loss(portfolio_value)
        logger.info(f"Portfolio metrics - Gain/Loss: {gain_or_loss}, Cash: {cash}, Fund value: {portfolio_value}, Portfolio value: {portfolio_total}, Net Inflows: {net_inflows}")

        # Step 4: Save Daily Snapshot
        logger.info("Saving daily portfolio snapshot")
        DailyPortfolioSnapshot.objects.update_or_create(
            date=self.date,
            defaults={
                "total_value": portfolio_value,
                "total_units": total_units,
                "nav_per_unit": nav_per_unit,
                "gain_or_loss": gain_or_loss,
                "cash": cash,  
                "net_inflows": net_inflows,
                "portfolio_total_value": portfolio_total,
            }
        )

        # Step 5: Save user share snapshots
        logger.info("Saving user share snapshots")
        UserShareSnapshot.objects.filter(date=self.date).delete()

        # Calculate each user's share of the cash position
        user_share_snapshots = []
        for user_id, units in new_user_units.items():
            # Calculate user's share of assets based on units
            asset_value = (units * nav_per_unit).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
            # Calculate user's share of cash (proportional to their units)
            cash_share = (units / total_units * cash).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_units > 0 else Decimal("0.0")
            
            # Total value is asset value plus cash share
            total_value = asset_value + cash_share
            
            user_share_snapshots.append(
                UserShareSnapshot(
                    date=self.date,
                    user_id=user_id,
                    units_held=units,
                    value_held=total_value
                )
            )
            logger.debug(f"User {user_id} snapshot - Units: {units}, Asset Value: {asset_value}, Cash Share: {cash_share}, Total: {total_value}")

        UserShareSnapshot.objects.bulk_create(user_share_snapshots)
        logger.info("Valuation computation completed successfully")
