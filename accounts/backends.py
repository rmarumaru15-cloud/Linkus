from django.contrib.auth.backends import ModelBackend
from .models import User
from web3.auto import w3
from eth_account.messages import defunct_hash_message

class WalletBackend(ModelBackend):
    """
    Custom authentication backend to authenticate users via wallet signature.
    """
    def authenticate(self, request, wallet_address=None, signature=None):
        """
        Authenticates a user by verifying a signed message (nonce).
        """
        # The nonce should be generated and stored in the session in a separate view.
        nonce = request.session.get("login_nonce")
        if not nonce or not wallet_address or not signature:
            return None

        try:
            # The message that was signed on the frontend
            message_hash = defunct_hash_message(text=nonce)

            # Recover the address from the signature
            signer_address = w3.eth.account.recoverHash(message_hash, signature=signature)

            # Check if the recovered address matches the provided address
            if signer_address.lower() == wallet_address.lower():
                # Get or create the user with this wallet address
                user, created = User.objects.get_or_create(
                    wallet_address=wallet_address.lower(),
                    defaults={'username': wallet_address.lower()} # Use wallet address as username if new
                )

                # Clear the nonce from the session after successful login
                request.session["login_nonce"] = None
                return user
        except Exception as e:
            # Handle exceptions (e.g., invalid signature)
            print(f"Authentication error: {e}") # For debugging
            return None

        return None

    def get_user(self, user_id):
        """
        Standard method to retrieve a user instance.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
