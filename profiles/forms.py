from django import forms
from .models import SnsLink, Address

class SnsLinkForm(forms.ModelForm):
    class Meta:
        model = SnsLink
        fields = ['platform', 'url']
        widgets = {
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/your_handle'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['currency_type', 'address', 'is_public']
        widgets = {
            'currency_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your wallet address'}),
        }
