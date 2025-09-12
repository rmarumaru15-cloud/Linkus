import logging
import requests
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

ALCHEMY_URL = f"https://eth-mainnet.g.alchemy.com/v2/{settings.ALCHEMY_API_KEY}"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


def get_token_balances(wallet_address: str) -> list:
    """
    Fetches ERC20 token balances for a given wallet address using Alchemy API.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet_address, "erc20"]
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(ALCHEMY_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            logger.error(f"Alchemy API error for {wallet_address}: {data['error']}")
            return []

        balances = data.get("result", {}).get("tokenBalances", [])
        # Filter out tokens with a zero balance
        return [b for b in balances if int(b.get("tokenBalance", 0), 16) > 0]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Alchemy API for {wallet_address}: {e}")
        return []


def get_token_prices(token_addresses: list[str]) -> dict:
    """
    Fetches the USD price for a list of token contract addresses using CoinGecko API.
    Results are cached for 10 minutes to reduce API calls.
    """
    if not token_addresses:
        return {}

    # Check cache first for prices we already have
    cache_keys = {addr: f"price_{addr}" for addr in token_addresses}
    cached_prices = cache.get_many(list(cache_keys.values()))

    # Map cache keys back to addresses
    prices = {addr: cached_prices[key] for addr, key in cache_keys.items() if key in cached_prices}

    # Find which addresses were not in the cache
    missing_addresses = [addr for addr in token_addresses if addr not in prices]

    if missing_addresses:
        logger.info(f"Fetching prices for {len(missing_addresses)} tokens from CoinGecko.")

        url = f"{COINGECKO_API_URL}/simple/token_price/ethereum"
        params = {
            "contract_addresses": ",".join(missing_addresses),
            "vs_currencies": "usd",
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            new_prices_data = response.json()

            new_prices = {}
            prices_to_cache = {}
            for addr, data in new_prices_data.items():
                if "usd" in data:
                    price = Decimal(str(data["usd"]))
                    new_prices[addr.lower()] = price
                    # Prepare data for cache.set_many
                    prices_to_cache[cache_keys[addr.lower()]] = price

            if prices_to_cache:
                cache.set_many(prices_to_cache, timeout=60 * 10) # Cache for 10 minutes

            prices.update(new_prices)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling CoinGecko API: {e}")

    return prices


def get_nfts(wallet_address: str) -> list:
    """
    Fetches NFTs for a given wallet address using Alchemy API.
    Results are cached for 10 minutes.
    """
    cache_key = f"nfts_{wallet_address}"
    cached_nfts = cache.get(cache_key)
    if cached_nfts is not None:
        return cached_nfts

    url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{settings.ALCHEMY_API_KEY}/getNFTs"
    params = {"owner": wallet_address}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        owned_nfts = data.get("ownedNfts", [])

        # Cache the result
        cache.set(cache_key, owned_nfts, timeout=60 * 10) # Cache for 10 minutes

        return owned_nfts
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Alchemy NFT API for {wallet_address}: {e}")
        return []
