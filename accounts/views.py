import json
import uuid
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def get_nonce(request):
    """
    Generate a nonce for the user to sign, and store it in the session.
    """
    nonce = uuid.uuid4().hex
    request.session["login_nonce"] = nonce
    return JsonResponse({"nonce": nonce})


@csrf_exempt
@require_POST
def wallet_login(request):
    """
    Authenticate a user via their wallet signature.
    """
    try:
        data = json.loads(request.body)
        wallet_address = data.get("wallet_address")
        signature = data.get("signature")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")

    if not wallet_address or not signature:
        return HttpResponseBadRequest("Missing wallet_address or signature.")

    user = authenticate(request, wallet_address=wallet_address, signature=signature)

    if user:
        login(request, user)
        return JsonResponse({"success": True, "message": "Login successful."})
    else:
        return JsonResponse({"success": False, "message": "Authentication failed."}, status=401)
