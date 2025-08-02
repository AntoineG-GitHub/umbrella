from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login
import json

User = get_user_model()

@csrf_exempt
@require_POST
def add_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("email")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Email and password are required."}, status=400)

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return JsonResponse({"status": "success", "user_id": user.id})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_GET
def get_user(request):
    """
    Get users, optionally filtered by:
    - id: integer
    - username: string

    Example usage:
    /api/users?id=3
    /api/users?username=johndoe
    """
    user_id = request.GET.get("id")
    first_name = request.GET.get("first_name")

    filters = {}
    if user_id:
        filters["id"] = user_id
    if first_name:
        filters["first_name"] = first_name

    users = User.objects.filter(**filters).values("id", "first_name", "last_name", "username", "password")

    return JsonResponse(list(users), safe=False)

@csrf_exempt
@require_POST
def login_user(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"status": "success", "message": "Logged in successfully."})
        else:
            return JsonResponse({"status": "error", "message": "Invalid credentials."}, status=401)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
