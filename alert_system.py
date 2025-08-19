import asyncio
import json
import aiofiles
import os
from typing import Dict, List, Any, Set
from datetime import datetime
import logging
from data_fetcher import DataFetcher

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self, storage_file: str = "alerts.json"):
        self.storage_file = storage_file
        self.alerts = {}
        self.next_id = 1
        self.load_alerts()
    
    def load_alerts(self):
        """Load alerts from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.alerts = data.get('alerts', {})
                    self.next_id = data.get('next_id', 1)
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
            self.alerts = {}
            self.next_id = 1
    
    async def save_alerts(self):
        """Save alerts to storage file"""
        try:
            data = {
                'alerts': self.alerts,
                'next_id': self.next_id
            }
            async with aiofiles.open(self.storage_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
    
    def add_alert(self, user_id: int, coin: str, condition: str, price: float) -> int:
        """Add a new alert"""
        alert_id = self.next_id
        self.next_id += 1
        
        alert = {
            'id': alert_id,
            'user_id': user_id,
            'coin': coin,
            'condition': condition,
            'price': price,
            'created_at': datetime.now().isoformat(),
            'triggered': False
        }
        
        if str(user_id) not in self.alerts:
            self.alerts[str(user_id)] = []
        
        self.alerts[str(user_id)].append(alert)
        
        # Save asynchronously
        asyncio.create_task(self.save_alerts())
        
        return alert_id
    
    def get_user_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all alerts for a user"""
        return self.alerts.get(str(user_id), [])
    
    def remove_alert(self, user_id: int, alert_id: int) -> bool:
        """Remove an alert"""
        user_alerts = self.alerts.get(str(user_id), [])
        
        for i, alert in enumerate(user_alerts):
            if alert['id'] == alert_id:
                user_alerts.pop(i)
                
                # Save asynchronously
                asyncio.create_task(self.save_alerts())
                return True
                
        return False
    
    async def check_alerts(self, data_fetcher: DataFetcher) -> List[tuple]:
        """Check all alerts and return those that are triggered"""
        triggered = []
        coins_to_check = set()
        
        # Collect all coins we need to check
        for user_id, user_alerts in self.alerts.items():
            for alert in user_alerts:
                if not alert['triggered']:
                    coins_to_check.add(alert['coin'])
        
        # Get current prices for all needed coins
        if coins_to_check:
            current_prices = await data_fetcher.get_multiple_prices(list(coins_to_check))
            
            # Check each alert
            for user_id, user_alerts in self.alerts.items():
                for alert in user_alerts:
                    if alert['triggered']:
                        continue
                    
                    coin = alert['coin']
                    current_price = current_prices.get(coin, 0)
                    
                    if current_price > 0:  # Only check if we have a valid price
                        condition_met = False
                        
                        if alert['condition'] == 'above' and current_price >= alert['price']:
                            condition_met = True
                        elif alert['condition'] == 'below' and current_price <= alert['price']:
                            condition_met = True
                        
                        if condition_met:
                            alert['triggered'] = True
                            triggered.append((alert, current_price))
            
            # Remove triggered alerts and save
            if triggered:
                self._cleanup_triggered_alerts()
                asyncio.create_task(self.save_alerts())
        
        return triggered
    
    def _cleanup_triggered_alerts(self):
        """Remove triggered alerts that are older than 24 hours"""
        current_time = datetime.now()
        
        for user_id, user_alerts in self.alerts.items():
            # Keep only non-triggered alerts or recently triggered ones (<24h)
            self.alerts[user_id] = [
                alert for alert in user_alerts 
                if not alert['triggered'] or 
                (datetime.fromisoformat(alert['created_at']) - current_time).total_seconds() < 86400
            ]
