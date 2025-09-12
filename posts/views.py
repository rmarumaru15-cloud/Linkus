from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from .models import Post, PostLike
from .forms import PostForm

class PostListView(FormMixin, ListView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_list.html"
    context_object_name = "post_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'likes':
            return queryset.order_by('-likes_count', '-created_at')
        return queryset.order_by('-created_at') # Default sort

    def get_success_url(self):
        return reverse_lazy("posts:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["sort_by"] = self.request.GET.get('sort', 'newest')

        if self.request.user.is_authenticated:
            liked_post_ids = PostLike.objects.filter(
                user=self.request.user,
                post__in=context['post_list']
            ).values_list('post_id', flat=True)
            context['liked_post_ids'] = set(liked_post_ids)
        else:
            context['liked_post_ids'] = set()

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Set the author to the current user before saving
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    with transaction.atomic():
        like, created = PostLike.objects.get_or_create(user=request.user, post=post)

        if created:
            # If the like was just created (user is liking the post)
            Post.objects.filter(id=post_id).update(likes_count=F('likes_count') + 1)
            liked = True
        else:
            # If the like already existed (user is unliking the post)
            like.delete()
            Post.objects.filter(id=post_id).update(likes_count=F('likes_count') - 1)
            liked = False

    # Refresh the post from the database to get the updated likes_count.
    # Note: In a very high-concurrency scenario, the returned likes_count might
    # not be the absolute latest value, but the atomic update guarantees the
    # database value is correct.
    post.refresh_from_db()

    return JsonResponse({
        "success": True,
        "likes_count": post.likes_count,
        "liked": liked,
    })
