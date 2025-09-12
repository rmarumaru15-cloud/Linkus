from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.test import TestCase, override_settings
from django.core.cache import cache
from .services import get_token_balances, get_token_prices, get_nfts

# A sample successful response from Alchemy's getTokenBalances
MOCK_ALCHEMY_BALANCES_SUCCESS = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "address": "0x...",
        "tokenBalances": [
            {"contractAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "tokenBalance": "0xDE0B6B3A7640000"}, # 1 Ether
            {"contractAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7", "tokenBalance": "0x0"},
        ]
    }
}

# A sample successful response from CoinGecko's token_price
MOCK_COINGECKO_PRICES_SUCCESS = {
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {"usd": 1.0},
    "0xanotheraddress": {"usd": 123.45}
}

# A sample successful response from Alchemy's getNFTs
MOCK_ALCHEMY_NFTS_SUCCESS = {
    "ownedNfts": [
        {"title": "Test NFT 1", "contract": {"address": "0xnft1"}},
        {"title": "Test NFT 2", "contract": {"address": "0xnft2"}},
    ]
}

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class ServicesTest(TestCase):

    def setUp(self):
        cache.clear()

    @patch('profiles.services.requests.post')
    def test_get_token_balances_success(self, mock_post):
        """Test successful fetching of token balances."""
        # Configure the mock to return a success response
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ALCHEMY_BALANCES_SUCCESS
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        balances = get_token_balances("0x123")

        # We expect the zero balance token to be filtered out
        self.assertEqual(len(balances), 1)
        self.assertEqual(balances[0]['contractAddress'], '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48')
        mock_post.assert_called_once()

    @patch('profiles.services.requests.get')
    def test_get_token_prices_caching(self, mock_get):
        """Test that token price results are cached."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_COINGECKO_PRICES_SUCCESS
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # First call - should hit the API
        requested_addresses = ["0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "0xanotheraddress"]
        prices = get_token_prices(requested_addresses)
        self.assertEqual(prices["0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"], Decimal("1.0"))
        self.assertEqual(prices["0xanotheraddress"], Decimal("123.45"))
        mock_get.assert_called_once() # API was called

        # Second call - should use the cache
        prices_cached = get_token_prices(requested_addresses)
        self.assertEqual(prices_cached["0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"], Decimal("1.0"))
        mock_get.assert_called_once() # API was NOT called again

    @patch('profiles.services.requests.get')
    def test_get_nfts_success(self, mock_get):
        """Test successful fetching of NFTs."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_ALCHEMY_NFTS_SUCCESS
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        nfts = get_nfts("0x123")
        self.assertEqual(len(nfts), 2)
        self.assertEqual(nfts[0]['title'], 'Test NFT 1')
        mock_get.assert_called_once()
