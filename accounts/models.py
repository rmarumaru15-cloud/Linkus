from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model that extends the default Django user.
    Includes fields for web3 wallet, profile customization, and portfolio value.
    """
    # Profile information
    nickname = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="The user's display name."
    )
    bio = models.TextField(
        blank=True,
        help_text="A short biography of the user."
    )
    profile_image = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True,
        help_text="The user's profile picture."
    )

    # Web3 related fields
    wallet_address = models.CharField(
        max_length=42,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="The user's primary wallet address (e.g., 0x...)."
    )
    portfolio_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="The calculated total value of the user's crypto portfolio in USD."
    )

    # Customization and settings
    is_public = models.BooleanField(
        default=True,
        help_text="Designates whether the user's profile is visible to others."
    )
    theme = models.JSONField(
        default=dict,
        blank=True,
        help_text="UI theme customization settings for the user's profile page."
    )

    def save(self, *args, **kwargs):
        """
        If nickname is not provided, set it to the username.
        """
        if not self.nickname:
            self.nickname = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
