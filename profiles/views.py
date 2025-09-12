from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, ListView
from django.forms import modelformset_factory
from django.db import transaction
from django.shortcuts import redirect

from accounts.models import User
from accounts.forms import CustomUserChangeForm
from .services import get_token_balances, get_nfts
from .models import SnsLink, Address
from .forms import SnsLinkForm, AddressForm


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
            context['token_balances'] = get_token_balances(profile_user.wallet_address)
            context['nfts'] = get_nfts(profile_user.wallet_address)

        # Fetch SNS links and addresses to display on the detail page
        context['sns_links'] = SnsLink.objects.filter(user=profile_user)
        context['addresses'] = Address.objects.filter(user=profile_user)

        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "profiles/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        SnsLinkFormSet = modelformset_factory(SnsLink, form=SnsLinkForm, extra=1, can_delete=True)
        AddressFormSet = modelformset_factory(Address, form=AddressForm, extra=1, can_delete=True)

        if self.request.POST:
            context['sns_formset'] = SnsLinkFormSet(self.request.POST, queryset=SnsLink.objects.filter(user=self.request.user), prefix='sns')
            context['address_formset'] = AddressFormSet(self.request.POST, queryset=Address.objects.filter(user=self.request.user), prefix='address')
        else:
            context['sns_formset'] = SnsLinkFormSet(queryset=SnsLink.objects.filter(user=self.request.user), prefix='sns')
            context['address_formset'] = AddressFormSet(queryset=Address.objects.filter(user=self.request.user), prefix='address')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        context = self.get_context_data()
        sns_formset = context['sns_formset']
        address_formset = context['address_formset']

        if form.is_valid() and sns_formset.is_valid() and address_formset.is_valid():
            return self.form_valid(form, sns_formset, address_formset)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, sns_formset, address_formset):
        with transaction.atomic():
            # Save the main user form
            self.object = form.save()

            # Save the SnsLink formset
            sns_instances = sns_formset.save(commit=False)
            for instance in sns_instances:
                instance.user = self.object
                instance.save()
            for obj in sns_formset.deleted_objects:
                obj.delete()

            # Save the Address formset
            address_instances = address_formset.save(commit=False)
            for instance in address_instances:
                instance.user = self.object
                instance.save()
            for obj in address_formset.deleted_objects:
                obj.delete()

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("profiles:detail", kwargs={"username": self.request.user.username})

class RankingView(ListView):
    model = User
    template_name = "profiles/ranking.html"
    context_object_name = "users"
    paginate_by = 50

    def get_queryset(self):
        return User.objects.filter(is_public=True).order_by('-portfolio_value')
