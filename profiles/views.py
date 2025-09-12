from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, ListView
from accounts.models import User
from accounts.forms import CustomUserChangeForm
from .services import get_token_balances, get_nfts

class ProfileDetailView(DetailView):
    model = User
    template_name = "profiles/profile_detail.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()

        if profile_user.wallet_address:
            # Fetch token balances and NFTs from external APIs
            # These service functions have built-in caching
            context['token_balances'] = get_token_balances(profile_user.wallet_address)
            context['nfts'] = get_nfts(profile_user.wallet_address)

        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "profiles/profile_edit.html"

    def get_object(self, queryset=None):
        """Only allow users to edit their own profile."""
        return self.request.user

    def get_success_url(self):
        """Redirect to the user's profile page after a successful edit."""
        return reverse_lazy("profiles:detail", kwargs={"username": self.request.user.username})

class RankingView(ListView):
    model = User
    template_name = "profiles/ranking.html"
    context_object_name = "users"
    paginate_by = 50

    def get_queryset(self):
        """
        Return public users, ordered by their portfolio value in descending order.
        """
        return User.objects.filter(is_public=True).order_by('-portfolio_value')
