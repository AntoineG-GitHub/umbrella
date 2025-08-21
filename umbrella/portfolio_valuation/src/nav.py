from decimal import Decimal, ROUND_HALF_UP
from portfolio_valuation.models import DailyPortfolioSnapshot, UserShareSnapshot

def get_last_snapshot_date(date):
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
    last_date = get_last_snapshot_date(date)
    if last_date:
        snapshot = DailyPortfolioSnapshot.objects.get(date=last_date)
        if snapshot.total_units > 0:
            return (snapshot.total_value / snapshot.total_units).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
    return Decimal("1.0")
