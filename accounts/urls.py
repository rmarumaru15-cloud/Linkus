from django.urls import path
from .views import SignUpView, get_nonce, wallet_login

app_name = "accounts"

urlpatterns = [
    # Traditional auth
    path("signup/", SignUpView.as_view(), name="signup"),

    # API endpoints for wallet authentication
    path("api/get-nonce/", get_nonce, name="get_nonce"),
    path("api/wallet-login/", wallet_login, name="wallet_login"),
]
