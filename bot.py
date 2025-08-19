import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from analysis_engine import AnalysisEngine
from data_fetcher import DataFetcher
from alert_system import AlertSystem
from config import TELEGRAM_BOT_TOKEN

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CryptoAIBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.data_fetcher = DataFetcher()
        self.analysis_engine = AnalysisEngine()
        self.alert_system = AlertSystem()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("analyze", self.analyze))
        self.application.add_handler(CommandHandler("trends", self.trends))
        self.application.add_handler(CommandHandler("setalert", self.set_alert))
        self.application.add_handler(CommandHandler("myalerts", self.my_alerts))
        self.application.add_handler(CommandHandler("removealert", self.remove_alert))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message and show main menu"""
        welcome_text = (
            "🤖 Welcome to Crypto AI Analyst Bot!\n\n"
            "I use artificial intelligence to analyze cryptocurrency trends "
            "and provide actionable insights in real-time.\n\n"
            "Available commands:\n"
            "/analyze - Analyze a specific cryptocurrency\n"
            "/trends - Show current market trends\n"
            "/setalert - Set a price alert\n"
            "/myalerts - View your active alerts\n"
            "/removealert - Remove an alert\n"
            "/help - Show help information"
        )
        
        keyboard = [['/analyze', '/trends'], ['/setalert', '/myalerts']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        help_text = (
            "📖 <b>How to use Crypto AI Analyst Bot</b>\n\n"
            "<b>Commands:</b>\n"
            "/analyze [coin] - Analyze a specific cryptocurrency (e.g., /analyze BTC)\n"
            "/trends - Get current market trends and insights\n"
            "/setalert [coin] [condition] [price] - Set a price alert\n"
            "   Example: /setalert BTC above 50000\n"
            "/myalerts - View your active alerts\n"
            "/removealert [id] - Remove an alert by ID\n\n"
            "<b>Features:</b>\n"
            "• Real-time cryptocurrency analysis\n"
            "• AI-powered trend predictions\n"
            "• Personalized price alerts\n"
            "• Market sentiment analysis\n"
            "• Technical indicator monitoring"
        )
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze a specific cryptocurrency"""
        if not context.args:
            await update.message.reply_text("Please specify a cryptocurrency. Example: /analyze BTC")
            return
        
        coin = context.args[0].upper()
        await update.message.reply_text(f"🔍 Analyzing {coin}, please wait...")
        
        try:
            # Fetch data
            data = await self.data_fetcher.get_crypto_data(coin)
            
            # Perform analysis
            analysis = await self.analysis_engine.analyze(data, coin)
            
            # Send results
            response = (
                f"📊 <b>{coin} Analysis Report</b>\n\n"
                f"{analysis['summary']}\n\n"
                f"<b>Current Price:</b> ${data['price']:,.2f}\n"
                f"<b>24h Change:</b> {data['change_24h']:.2f}%\n"
                f"<b>Market Sentiment:</b> {analysis['sentiment']}\n\n"
                f"<b>Key Indicators:</b>\n"
                f"• RSI: {analysis['indicators']['rsi']:.2f} "
                f"({'Overbought' if analysis['indicators']['rsi'] > 70 else 'Oversold' if analysis['indicators']['rsi'] < 30 else 'Neutral'})\n"
                f"• Trend: {analysis['trend']}\n\n"
                f"<b>AI Prediction:</b>\n"
                f"{analysis['prediction']}\n\n"
                f"<b>Confidence Level:</b> {analysis['confidence']}%"
            )
            
            await update.message.reply_text(response, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error analyzing {coin}: {e}")
            await update.message.reply_text(f"Sorry, I couldn't analyze {coin}. Please try again later.")
    
    async def trends(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current market trends"""
        await update.message.reply_text("📈 Gathering market trends, please wait...")
        
        try:
            trends = await self.analysis_engine.get_market_trends()
            
            response = (
                f"🌐 <b>Current Market Trends</b>\n\n"
                f"<b>Overall Sentiment:</b> {trends['market_sentiment']}\n"
                f"<b>Top Gainers (24h):</b>\n"
            )
            
            for i, gainer in enumerate(trends['top_gainers'][:5], 1):
                response += f"{i}. {gainer['symbol']}: +{gainer['change']:.2f}%\n"
                
            response += f"\n<b>Top Losers (24h):</b>\n"
            
            for i, loser in enumerate(trends['top_losers'][:5], 1):
                response += f"{i}. {loser['symbol']}: {loser['change']:.2f}%\n"
                
            response += f"\n<b>AI Insights:</b>\n{trends['insights']}"
            
            await update.message.reply_text(response, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            await update.message.reply_text("Sorry, I couldn't fetch market trends. Please try again later.")
    
    async def set_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set a price alert"""
        if len(context.args) < 3:
            await update.message.reply_text(
                "Please specify alert parameters. Example: /setalert BTC above 50000\n"
                "Format: /setalert [coin] [above/below] [price]"
            )
            return
        
        try:
            coin = context.args[0].upper()
            condition = context.args[1].lower()
            price = float(context.args[2])
            
            if condition not in ['above', 'below']:
                await update.message.reply_text("Condition must be 'above' or 'below'")
                return
            
            user_id = update.effective_user.id
            alert_id = self.alert_system.add_alert(user_id, coin, condition, price)
            
            await update.message.reply_text(
                f"✅ Alert set successfully!\n"
                f"<b>ID:</b> {alert_id}\n"
                f"<b>Coin:</b> {coin}\n"
                f"<b>Condition:</b> Price {condition} ${price:,.2f}",
                parse_mode='HTML'
            )
            
        except ValueError:
            await update.message.reply_text("Please enter a valid price number")
        except Exception as e:
            logger.error(f"Error setting alert: {e}")
            await update.message.reply_text("Sorry, I couldn't set the alert. Please try again.")
    
    async def my_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's active alerts"""
        user_id = update.effective_user.id
        alerts = self.alert_system.get_user_alerts(user_id)
        
        if not alerts:
            await update.message.reply_text("You don't have any active alerts.")
            return
        
        response = "🔔 <b>Your Active Alerts</b>\n\n"
        for alert in alerts:
            response += (
                f"<b>ID:</b> {alert['id']}\n"
                f"<b>Coin:</b> {alert['coin']}\n"
                f"<b>Condition:</b> Price {alert['condition']} ${alert['price']:,.2f}\n"
                f"<b>Created:</b> {alert['created_at']}\n\n"
            )
        
        await update.message.reply_text(response, parse_mode='HTML')
    
    async def remove_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove an alert"""
        if not context.args:
            await update.message.reply_text("Please specify an alert ID. Example: /removealert 123")
            return
        
        try:
            alert_id = int(context.args[0])
            user_id = update.effective_user.id
            
            if self.alert_system.remove_alert(user_id, alert_id):
                await update.message.reply_text(f"✅ Alert {alert_id} removed successfully!")
            else:
                await update.message.reply_text("Alert not found or you don't have permission to remove it.")
                
        except ValueError:
            await update.message.reply_text("Please enter a valid alert ID (number)")
        except Exception as e:
            logger.error(f"Error removing alert: {e}")
            await update.message.reply_text("Sorry, I couldn't remove the alert. Please try again.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any other text messages"""
        text = update.message.text.lower()
        
        if any(greeting in text for greeting in ['hello', 'hi', 'hey', 'greetings']):
            await update.message.reply_text("Hello! I'm Crypto AI Analyst Bot. Use /help to see what I can do!")
        elif 'thank' in text:
            await update.message.reply_text("You're welcome! 😊")
        else:
            await update.message.reply_text(
                "I'm not sure how to respond to that. Use /help to see available commands."
            )
    
    async def monitor_alerts(self):
        """Background task to monitor alerts and notify users"""
        while True:
            try:
                triggered_alerts = await self.alert_system.check_alerts(self.data_fetcher)
                
                for alert, current_price in triggered_alerts:
                    message = (
                        f"🚨 <b>Price Alert Triggered!</b>\n\n"
                        f"<b>Coin:</b> {alert['coin']}\n"
                        f"<b>Condition:</b> Price {alert['condition']} ${alert['price']:,.2f}\n"
                        f"<b>Current Price:</b> ${current_price:,.2f}\n\n"
                        f"<i>This alert will now be removed.</i>"
                    )
                    
                    try:
                        await self.application.bot.send_message(
                            chat_id=alert['user_id'],
                            text=message,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Error sending alert notification: {e}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                await asyncio.sleep(60)
    
    def run(self):
        """Start the bot"""
        # Start alert monitoring in the background
        loop = asyncio.get_event_loop()
        loop.create_task(self.monitor_alerts())
        
        # Start the bot
        self.application.run_polling()

if __name__ == '__main__':
    bot = CryptoAIBot()
    bot.run()
