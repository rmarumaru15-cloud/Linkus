from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        """Test creating a new user."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpassword123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        # Test that nickname is set from username on save
        self.assertEqual(user.nickname, "testuser")

    def test_create_superuser(self):
        """Test creating a new superuser."""
        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123"
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_with_wallet(self):
        """Test creating a user with a wallet address."""
        wallet_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
        user = User.objects.create_user(
            username="vitalik",
            wallet_address=wallet_address.lower()
        )
        self.assertEqual(user.wallet_address, wallet_address.lower())
