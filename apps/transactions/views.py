from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.utils.dateparse import parse_date
from django.db.models import Q
from rest_framework import status
from .models import Transaction
import json
from django.contrib.auth import get_user_model

@csrf_exempt
@require_http_methods(["POST"])
def create_transaction(request):
    """
    Create a new transaction.
    Expects a JSON body with:
    - type: deposit, withdrawal, buy, sell, dividend, fee
    - amount: float
    - date: YYYY-MM-DD
    - user_id: optional
    - ticker: optional
    - shares: optional
    - metadata: optional (dict)
    """
    try:
        data = json.loads(request.body)
        transaction = Transaction.objects.create(
            type=data["type"],
            amount=data["amount"],
            date=parse_date(data["date"]),
            user_id=data.get("user_id"),
            ticker=data.get("ticker"),
            shares=data.get("shares"),
            metadata=data.get("metadata", {})
        )
        return JsonResponse({"status": "success", "transaction": model_to_dict(transaction)}, status=201)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@require_http_methods(["GET"])
def list_transactions(request):
    """
    List transactions with optional filters:
    - type
    - start_date
    - end_date
    - user_id
    - ticker
    """
    try:
        filters = Q()
        if type_ := request.GET.get("type"):
            filters &= Q(type=type_)
        if start_date := request.GET.get("start_date"):
            filters &= Q(date__gte=parse_date(start_date))
        if end_date := request.GET.get("end_date"):
            filters &= Q(date__lte=parse_date(end_date))
        if user_id := request.GET.get("user_id"):
            filters &= Q(user_id=user_id)
        if ticker := request.GET.get("ticker"):
            filters &= Q(ticker=ticker)

        transactions = Transaction.objects.filter(filters)
        data = [model_to_dict(txn) for txn in transactions]
        return JsonResponse({"status": "success", "data": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@require_http_methods(["GET"])
def get_transaction(request, transaction_id):
    """
    Get a single transaction by its ID.
    """
    try:
        txn = Transaction.objects.get(id=transaction_id)
        return JsonResponse({"status": "success", "data": model_to_dict(txn)})
    except Transaction.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Transaction not found."}, status=404)


@require_http_methods(["POST"])
def delete_transaction(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        transaction.delete()
        return JsonResponse({"message": f"Transaction {id} deleted successfully."}, status=status.HTTP_200_OK)
    except Transaction.DoesNotExist:
        return JsonResponse({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

User = get_user_model()

@csrf_exempt
def create_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            email = data.get("email", "")

            if not username or not password:
                return JsonResponse({"error": "Username and password are required."}, status=400)

            user = User.objects.create_user(username=username, password=password, email=email)
            return JsonResponse({"status": "success", "user_id": user.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST allowed."}, status=405)

def list_users(request):
    users = User.objects.all().values("id", "username", "email", "date_joined")
    return JsonResponse(list(users), safe=False)
