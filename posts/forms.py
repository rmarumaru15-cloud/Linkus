from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "What's on your mind?",
                    "class": "form-control",
                }
            ),
        }
        labels = {
            "content": "", # Hide the label
        }
