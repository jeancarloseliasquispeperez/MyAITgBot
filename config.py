import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# API Keys (you'll need to get these from respective services)
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')

# Analysis Settings
UPDATE_INTERVAL = 300  # 5 minutes in seconds
ALERT_CHECK_INTERVAL = 60  # 1 minute in seconds

# Supported cryptocurrencies
SUPPORTED_CRYPTOS = ['BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOT', 'DOGE', 'AVAX', 'MATIC']
