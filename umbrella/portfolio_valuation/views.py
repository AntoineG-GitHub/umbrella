from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from portfolio_valuation.models import DailyPortfolioSnapshot
from django.forms.models import model_to_dict
from django.views import View
from portfolio_valuation.models import UserShareSnapshot
from django.core.exceptions import ValidationError

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
