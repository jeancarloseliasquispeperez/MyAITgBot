# AI-Powered Cryptocurrency Trend Analysis Telegram Bot

This Telegram bot uses artificial intelligence to analyze cryptocurrency trends in real-time and provides users with actionable insights and alerts.

The bot will:
- Monitor real-time cryptocurrency data from multiple exchanges
- Use AI/ML techniques to identify trends and patterns
- Send personalized alerts to users based on their preferences
- Provide actionable insights through natural language explanations

## Features

- Real-time cryptocurrency price monitoring
- AI-powered trend analysis and predictions
- Technical indicator calculations (RSI, MACD, Moving Averages, etc.)
- Personalized price alerts
- Market sentiment analysis
- Support for multiple cryptocurrencies

## Project Structure
- bot.py                 # Main bot application
- config.py              # Configuration settings
- requirements.txt       # Python dependencies
- analysis_engine.py     # AI analysis components
- data_fetcher.py        # Crypto data collection
- alert_system.py        # User alert management
- README.md              # Setup instructions


## Setup Instructions

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from [BotFather](https://t.me/BotFather))
- API keys for cryptocurrency data (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jeancarloseliasquispeperez/MyAITgBot
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and bot token
```

4. Run the bot:
```bash
python bot.py
```

### Configuration

Edit the `.env` file with your credentials:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
COINGECKO_API_KEY=your_coingecko_api_key_optional
BINANCE_API_KEY=your_binance_api_key_optional
```

### Usage

1. Start a chat with your bot on Telegram
2. Use the following commands:
   - `/start` - Welcome message and main menu
   - `/help` - Show help information
   - `/analyze [coin]` - Analyze a specific cryptocurrency
   - `/trends` - Show current market trends
   - `/setalert [coin] [above/below] [price]` - Set a price alert
   - `/myalerts` - View your active alerts
   - `/removealert [id]` - Remove an alert

## Supported Cryptocurrencies

BTC, ETH, BNB, ADA, XRP, SOL, DOT, DOGE, AVAX, MATIC

## AI Features

The bot uses machine learning algorithms to:
- Predict short-term price movements
- Identify trend patterns
- Calculate technical indicators
- Generate market sentiment analysis

## License

MIT License - see LICENSE file for details
```

## How to Set Up and Run the Bot

1. **Create a Telegram Bot**:
   - Message @BotFather on Telegram
   - Use the `/newbot` command to create a new bot
   - Copy the API token provided

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Create a `.env` file with your Telegram bot token
   - Optionally add API keys for enhanced data sources

4. **Run the Bot**:
   ```bash
   python bot.py
   ```

5. **Interact with Your Bot**:
   - Find your bot on Telegram
   - Send the `/start` command to begin

## Enhancements for Production Use

For a production environment, consider adding:

1. **Database Integration**: Replace the JSON storage with a proper database
2. **More Data Sources**: Add additional cryptocurrency APIs for redundancy
3. **Advanced ML Models**: Implement more sophisticated prediction algorithms
4. **Rate Limiting**: Add protection against API abuse
5. **Error Handling**: Improve error handling and logging
6. **Backtesting**: Add functionality to test strategies historically
7. **Portfolio Tracking**: Allow users to track their cryptocurrency portfolios

This bot provides a solid foundation for a cryptocurrency analysis tool that can be extended with more advanced features as needed.
