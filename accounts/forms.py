from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

THEME_CHOICES = [
    ('default', 'Default'),
    ('crimson', 'Crimson'),
    ('ocean', 'Ocean'),
    ('forest', 'Forest'),
]

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "nickname")

class CustomUserChangeForm(UserChangeForm):
    # We add a separate field for theme choice, not bound to the model directly
    theme_choice = forms.ChoiceField(choices=THEME_CHOICES, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "nickname", "bio", "profile_image", "is_public")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial value for our custom theme field
        if self.instance and self.instance.theme and 'color' in self.instance.theme:
            self.fields['theme_choice'].initial = self.instance.theme['color']

    def save(self, commit=True):
        # First, save the user instance to get the object
        user = super().save(commit=False)

        # Now, update the JSONField `theme` with our choice
        selected_theme = self.cleaned_data.get('theme_choice', 'default')
        user.theme = {'color': selected_theme}

        if commit:
            user.save()
        return user
