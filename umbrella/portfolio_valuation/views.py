from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from portfolio_valuation.models import DailyPortfolioSnapshot
from django.forms.models import model_to_dict
from django.views import View
from portfolio_valuation.models import UserShareSnapshot
from django.db.models import Sum, Case, When, F, DecimalField
from transactions.models import Transaction
from decimal import Decimal

@require_GET
def get_portfolio_valuations(request):
    """
    Get daily portfolio valuations over a specified time period.
    Query parameters:
        - start_date (YYYY-MM-DD, optional)
        - end_date (YYYY-MM-DD, optional)
    """
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    valuations_query = DailyPortfolioSnapshot.objects.all()

    if start_date and end_date:
        valuations_query = valuations_query.filter(date__range=[start_date, end_date])
    elif start_date:
        valuations_query = valuations_query.filter(date__gte=start_date)
    elif end_date:
        valuations_query = valuations_query.filter(date__lte=end_date)

    valuations = valuations_query.order_by("date")
    data = [model_to_dict(v) for v in valuations]

    return JsonResponse({
        "status": "success",
        "data": data
    })

@require_GET
def get_portfolio_stock(request):
    """
    Get current stock holdings based on buy/sell transactions.
    """

    # Aggregate buy/sell transactions to find net quantity per ticker
    asset_tx = (
        Transaction.objects
        .filter(type__in=["buy", "sell"])
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

    stocks = {}

    for item in asset_tx:
        if item["total_qty"] > 0:
            stocks[item["ticker"]] = Decimal(item["total_qty"])

    return JsonResponse({
        "status": "success",
        "data": stocks
    })

class UserShareSnapshotView(View):
    def get(self, request, user_id):
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        snapshots_query = UserShareSnapshot.objects.filter(user_id=user_id)
        if start_date and end_date:
            snapshots_query = snapshots_query.filter(date__range=[start_date, end_date])
        elif start_date:
            snapshots_query = snapshots_query.filter(date__gte=start_date)
        elif end_date:
            snapshots_query = snapshots_query.filter(date__lte=end_date)

        snapshots = snapshots_query.order_by("date")

        data = [
            {
                "date": snapshot.date.strftime("%Y-%m-%d"),
                "units_held": float(snapshot.units_held),
                "value_held": float(snapshot.value_held)
            }
            for snapshot in snapshots
        ]

        return JsonResponse({"user_id": user_id, "snapshots": data})
