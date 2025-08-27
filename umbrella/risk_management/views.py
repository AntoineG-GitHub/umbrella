from django.shortcuts import render
from django.forms.models import model_to_dict
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from datetime import datetime
from risk_management.models import VARComputation


@require_GET
def get_historical_var(request):
    date_str = request.GET.get("date")
    if not date_str:
        return JsonResponse({"error": "Date parameter is required."}, status=400)
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
    
    query_set = VARComputation.objects.filter(date=date)
    
    var_data = [model_to_dict(var) for var in query_set]
    
    return JsonResponse({
        "status": "success",
        "data": var_data
    })