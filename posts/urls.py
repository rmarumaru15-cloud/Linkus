from django.urls import path
from .views import PostListView, like_post

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path("post/<int:post_id>/like/", like_post, name="like"),
]
