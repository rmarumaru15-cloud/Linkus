import logging
from decimal import Decimal
from celery import shared_task
from accounts.models import User
from .services import get_token_balances, get_token_prices

logger = logging.getLogger(__name__)

@shared_task
def update_all_user_portfolios():
    """
    A periodic task that updates the portfolio value for all active users
    with a registered wallet address.
    """
    logger.info("Starting periodic task: update_all_user_portfolios")

    users = User.objects.filter(is_active=True, wallet_address__isnull=False).only("id", "wallet_address")
    if not users:
        logger.info("No users with wallet addresses to update.")
        return "No users to update."

    all_balances = {}
    all_token_addresses = set()

    # Step 1: Get all balances for all users
    for user in users:
        balances = get_token_balances(user.wallet_address)
        if balances:
            all_balances[user.id] = balances
            for balance in balances:
                all_token_addresses.add(balance["contractAddress"])

    # Step 2: Get all prices for all unique tokens
    if not all_token_addresses:
        logger.info("No tokens found for any user.")
        return "No tokens to price."

    token_prices = get_token_prices(list(all_token_addresses))

    # Step 3: Calculate portfolio value for each user and prepare for bulk update
    users_to_update = []
    for user in users:
        if user.id not in all_balances:
            continue

        total_value = Decimal("0.0")
        for balance in all_balances[user.id]:
            contract_address = balance["contractAddress"]
            price = token_prices.get(contract_address.lower())

            if price:
                # Alchemy returns balance in hex, needs conversion.
                # Assuming tokens have 18 decimal places for simplicity.
                # A more robust solution would fetch token metadata for decimals.
                token_balance_wei = int(balance["tokenBalance"], 16)
                token_balance_ether = Decimal(token_balance_wei) / Decimal(10**18)
                total_value += token_balance_ether * price

        user.portfolio_value = total_value
        users_to_update.append(user)

    # Step 4: Bulk update all users
    if users_to_update:
        User.objects.bulk_update(users_to_update, ["portfolio_value"])
        logger.info(f"Successfully updated portfolio value for {len(users_to_update)} users.")
    else:
        logger.info("No user portfolios were updated.")

    logger.info("Finished periodic task: update_all_user_portfolios")
    return f"Updated portfolio value for {len(users_to_update)} users."
