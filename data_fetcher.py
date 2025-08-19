import aiohttp
import asyncio
import json
from typing import Dict, Any, List
import logging
from config import COINGECKO_API_KEY, BINANCE_API_KEY, SUPPORTED_CRYPTOS

logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        self.session = None
        self.cache = {}
        
    async def init_session(self):
        """Initialize aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_crypto_data(self, coin: str) -> Dict[str, Any]:
        """Get cryptocurrency data from APIs"""
        await self.init_session()
        
        try:
            # Try CoinGecko first
            data = await self._fetch_from_coingecko(coin)
            if data:
                return data
                
            # Fallback to Binance
            data = await self._fetch_from_binance(coin)
            if data:
                return data
                
            raise Exception(f"Could not fetch data for {coin}")
            
        except Exception as e:
            logger.error(f"Error fetching data for {coin}: {e}")
            # Return mock data for demonstration
            return self._get_mock_data(coin)
    
    async def _fetch_from_coingecko(self, coin: str) -> Dict[str, Any]:
        """Fetch data from CoinGecko API"""
        if not COINGECKO_API_KEY:
            return None
            
        try:
            coin_id = self._get_coingecko_id(coin)
            if not coin_id:
                return None
                
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_coingecko_data(data)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching from CoinGecko: {e}")
            return None
    
    async def _fetch_from_binance(self, coin: str) -> Dict[str, Any]:
        """Fetch data from Binance API"""
        try:
            symbol = f"{coin}USDT"
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_binance_data(data, coin)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching from Binance: {e}")
            return None
    
    def _parse_coingecko_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse CoinGecko API response"""
        market_data = data.get('market_data', {})
        return {
            'price': market_data.get('current_price', {}).get('usd', 0),
            'change_24h': market_data.get('price_change_percentage_24h', 0),
            'high_24h': market_data.get('high_24h', {}).get('usd', 0),
            'low_24h': market_data.get('low_24h', {}).get('usd', 0),
            'volume': market_data.get('total_volume', {}).get('usd', 0),
            'market_cap': market_data.get('market_cap', {}).get('usd', 0)
        }
    
    def _parse_binance_data(self, data: Dict[str, Any], coin: str) -> Dict[str, Any]:
        """Parse Binance API response"""
        return {
            'price': float(data.get('lastPrice', 0)),
            'change_24h': float(data.get('priceChangePercent', 0)),
            'high_24h': float(data.get('highPrice', 0)),
            'low_24h': float(data.get('lowPrice', 0)),
            'volume': float(data.get('volume', 0)),
            'market_cap': 0  # Binance doesn't provide market cap
        }
    
    def _get_coingecko_id(self, coin: str) -> str:
        """Map symbol to CoinGecko ID"""
        coin_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'SOL': 'solana',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network'
        }
        return coin_map.get(coin, '')
    
    def _get_mock_data(self, coin: str) -> Dict[str, Any]:
        """Generate mock data for demonstration"""
        import random
        
        base_prices = {
            'BTC': 50000 + random.randint(-2000, 2000),
            'ETH': 3000 + random.randint(-200, 200),
            'BNB': 400 + random.randint(-20, 20),
            'ADA': 1.2 + random.uniform(-0.1, 0.1),
            'XRP': 0.8 + random.uniform(-0.05, 0.05),
            'SOL': 100 + random.randint(-5, 5),
            'DOT': 20 + random.uniform(-1, 1),
            'DOGE': 0.2 + random.uniform(-0.01, 0.01),
            'AVAX': 60 + random.randint(-3, 3),
            'MATIC': 1.5 + random.uniform(-0.1, 0.1)
        }
        
        base_price = base_prices.get(coin, 100)
        change = random.uniform(-5, 5)
        
        return {
            'price': base_price,
            'change_24h': change,
            'high_24h': base_price * (1 + abs(change/100) + random.uniform(0, 2)),
            'low_24h': base_price * (1 - abs(change/100) - random.uniform(0, 2)),
            'volume': random.randint(100000000, 5000000000),
            'market_cap': random.randint(1000000000, 1000000000000)
        }
    
    async def get_multiple_prices(self, coins: List[str]) -> Dict[str, float]:
        """Get current prices for multiple cryptocurrencies"""
        prices = {}
        for coin in coins:
            try:
                data = await self.get_crypto_data(coin)
                prices[coin] = data['price']
            except Exception as e:
                logger.error(f"Error getting price for {coin}: {e}")
                prices[coin] = 0
                
        return prices
