from decimal import Decimal, ROUND_HALF_UP
from portfolio_valuation.models import DailyPortfolioSnapshot, UserShareSnapshot
from datetime import timedelta

def get_last_snapshot_date(date):
    """
    Get the most recent date for which a DailyPortfolioSnapshot exists before the given date.
    Note that there is no data for weekends days.
    """
    snapshot = DailyPortfolioSnapshot.objects.filter(date__lt=date).order_by("-date").first()
    return snapshot.date if snapshot else None

def get_previous_units(date):
    last_date = get_last_snapshot_date(date)
    if not last_date:
        return Decimal("0.0")
    return DailyPortfolioSnapshot.objects.get(date=last_date).total_units

def get_previous_user_units(date):
    last_date = get_last_snapshot_date(date)
    if not last_date:
        return {}
    return {
        snap.user_id: snap.units_held
        for snap in UserShareSnapshot.objects.filter(date=last_date)
    }

def get_nav_per_unit(date):
    """
    Calculate the Net Asset Value (NAV) per unit for a given date.
    If no previous snapshot exists, return 1.0 as the default NAV.

    Note that the NAV calculated at time T is computed on total_value from T-1.
    This is needed because transactions at time T (deposits and widthdrawals) are executed at the NAV of T-1.
    """
    last_date = get_last_snapshot_date(date)
    if last_date:
        snapshot = DailyPortfolioSnapshot.objects.get(date=last_date)
        if snapshot.total_units > 0:
            return (snapshot.total_value / snapshot.total_units).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
    return Decimal("1.0")


def get_daily_returns(date, current_nav):
    last_date = get_last_snapshot_date(date)
    if not last_date:
        return Decimal("0.0")
    previous_nav = DailyPortfolioSnapshot.objects.get(date=last_date).nav_per_unit
    if previous_nav == 0:
        return Decimal("0.0")
    return ((current_nav - previous_nav) / previous_nav).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
