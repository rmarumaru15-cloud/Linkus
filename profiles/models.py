from django.conf import settings
from django.db import models

class SnsLink(models.Model):
    """
    Stores social media links for a user.
    """
    PLATFORM_CHOICES = [
        ("twitter", "Twitter"),
        ("github", "GitHub"),
        ("website", "Website"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sns_links"
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        help_text="The social media platform."
    )
    url = models.URLField(
        max_length=200,
        help_text="The URL of the user's profile on the platform."
    )

    class Meta:
        unique_together = ("user", "platform")

    def __str__(self):
        return f"{self.user.username}'s {self.get_platform_display()} Link"


class Address(models.Model):
    """
    Stores additional crypto addresses for a user.
    """
    CURRENCY_CHOICES = [
        ("eth", "Ethereum"),
        ("btc", "Bitcoin"),
        ("sol", "Solana"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    address = models.CharField(
        max_length=255,
        help_text="The crypto wallet address."
    )
    currency_type = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        help_text="The type of cryptocurrency."
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Is this address visible on the public profile?"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Has ownership of this address been verified?"
    )

    class Meta:
        verbose_name_plural = "Addresses"
        unique_together = ("user", "address")

    def __str__(self):
        return f"{self.user.username}'s {self.get_currency_type_display()} Address: {self.address}"
