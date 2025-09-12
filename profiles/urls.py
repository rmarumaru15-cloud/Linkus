from django.urls import path
from .views import ProfileDetailView, ProfileEditView, RankingView

app_name = "profiles"

urlpatterns = [
    path("ranking/", RankingView.as_view(), name="ranking"),
    path("edit/", ProfileEditView.as_view(), name="edit"),
    path("<str:username>/", ProfileDetailView.as_view(), name="detail"),
]
