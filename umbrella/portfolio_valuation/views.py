from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from portfolio_valuation.models import DailyPortfolioSnapshot
from django.forms.models import model_to_dict
from datetime import timedelta
from django.views import View
from portfolio_valuation.models import UserShareSnapshot
from django.core.exceptions import ValidationError

from portfolio_valuation.src.valuation import ValuationService


class ComputeValuationView(APIView):
    """
    Endpoint: /portfolio_valuation/compute/?date=YYYY-MM-DD
    Triggers the valuation logic for the specified date.
    """

    def is_market_open(self, date):
        # Check if the date is a business day (Monday to Friday)
        return date.weekday() < 5

    def get(self, request, *args, **kwargs):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "Missing date parameter."}, status=status.HTTP_400_BAD_REQUEST)

        valuation_date = parse_date(date_str)

        if not valuation_date:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = ValuationService(valuation_date)
            if self.is_market_open(valuation_date):
                service.compute()
            else:
                return Response({"error": "Market is closed."},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred during valuation computation: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"Valuation computed for {valuation_date}."}, status=status.HTTP_200_OK)


class BatchValuationView(APIView):
    """
    Endpoint: /api/valuation/batch
    POST body: {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD"
    }
    Triggers valuations for each date in the range [start_date, end_date].
    """

    def is_market_open(self, date):
        # Check if the date is a business day (Monday to Friday)
        return date.weekday() < 5

    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        if not start_date_str or not end_date_str:
            return Response({"error": "Both start_date and end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        if not start_date or not end_date or end_date < start_date:
            return Response({"error": "Invalid date range."}, status=status.HTTP_400_BAD_REQUEST)

        current_date = start_date
        while current_date <= end_date:
            service = ValuationService(current_date)
            if self.is_market_open(current_date):
                service.compute()
            else:
                pass

            current_date += timedelta(days=1)

        return Response({
            "message": f"Valuations computed from {start_date} to {end_date}."
        }, status=status.HTTP_200_OK)

@require_GET
def get_portfolio_valuations(request):
    """
    Get daily portfolio valuations over a specified time period.
    Query parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    """
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date or not end_date:
        return JsonResponse({
            "status": "error",
            "message": "start_date and end_date query parameters are required."
        }, status=400)

    valuations = DailyPortfolioSnapshot.objects.filter(date__range=[start_date, end_date]).order_by("date")

    data = [model_to_dict(v) for v in valuations]

    return JsonResponse({
        "status": "success",
        "data": data
    })

class UserShareSnapshotView(View):
    def get(self, request, user_id):
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        try:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                raise ValidationError("Invalid date format.")
        except Exception:
            return JsonResponse({"error": "Invalid or missing date format (YYYY-MM-DD expected)."}, status=400)

        snapshots = UserShareSnapshot.objects.filter(
            user_id=user_id, date__range=[start_date, end_date]
        ).order_by("date")

        data = [
            {
                "date": snapshot.date.strftime("%Y-%m-%d"),
                "units_held": float(snapshot.units_held),
                "value_held": float(snapshot.value_held)
            }
            for snapshot in snapshots
        ]

        return JsonResponse({"user_id": user_id, "snapshots": data})
