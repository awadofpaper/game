"""
Market Manager - Central hub for all market operations
Manages multiple town markets, processes transactions, updates prices
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from market_system import (
    MarketData, Commodity, TransactionLimit, 
    get_commodity, is_tradeable, TRADEABLE_COMMODITIES
)
from price_engine import PriceCalculator, MarketSentimentCalculator

logger = logging.getLogger(__name__)


class TownMarket:
    """Represents a market in a specific town"""
    
    def __init__(self, town_name: str):
        self.town_name = town_name
        self.market_data = {}  # {commodity_id: MarketData}
        self.active = True
        self.transaction_fees = 0.02  # 2% base fee
        
        # Merchant gold reserves (prevents infinite gold exploit)
        self.gold_reserve = 10000.0  # Starting gold
        self.max_gold_reserve = 25000.0  # Maximum gold merchant can hold
        self.daily_gold_regen = 500.0  # Gold regenerated per day
        
        # Market-specific modifiers
        self.local_events = []
        self.prosperity = 1.0  # Economic health multiplier
        
        # Initialize market data for all commodities
        self._initialize_market_data()
    
    def _initialize_market_data(self):
        """Create MarketData for each tradeable commodity"""
        # Only initialize if commodities are loaded
        if TRADEABLE_COMMODITIES:
            for commodity_id, commodity in TRADEABLE_COMMODITIES.items():
                if commodity.is_tradeable():
                    self.market_data[commodity_id] = MarketData(commodity, self.town_name)
    
    def get_or_create_market_data(self, commodity_id: str) -> Optional[MarketData]:
        """Get or create market data for a specific commodity"""
        if commodity_id not in self.market_data:
            commodity = TRADEABLE_COMMODITIES.get(commodity_id)
            if commodity and commodity.is_tradeable():
                self.market_data[commodity_id] = MarketData(commodity, self.town_name)
        return self.market_data.get(commodity_id)
    
    def get_market_data(self, commodity_id: str) -> Optional[MarketData]:
        """Get market data for a specific commodity"""
        return self.market_data.get(commodity_id)
    
    def add_local_event(self, event: str):
        """Add a local event that affects this market"""
        if event not in self.local_events:
            self.local_events.append(event)
            logger.info(f"Market event in {self.town_name}: {event}")
    
    def remove_local_event(self, event: str):
        """Remove a local event"""
        if event in self.local_events:
            self.local_events.remove(event)
    
    def get_all_prices(self) -> Dict[str, float]:
        """Get current prices for all commodities"""
        return {
            commodity_id: market_data.current_price
            for commodity_id, market_data in self.market_data.items()
        }
    
    def update_prosperity(self, change: float):
        """Update town prosperity (affects all prices)"""
        self.prosperity = max(0.5, min(2.0, self.prosperity + change))
    
    def regenerate_gold(self, amount: float = None):
        """Regenerate merchant's gold reserves (called daily)"""
        regen_amount = amount if amount is not None else self.daily_gold_regen
        self.gold_reserve = min(self.max_gold_reserve, self.gold_reserve + regen_amount)
        logger.info(f"{self.town_name} market: +{regen_amount:.0f} gold, reserve now {self.gold_reserve:.0f}")


class MarketManager:
    """Central manager for the entire market economy system"""
    
    # Level required to unlock market features
    MARKET_UNLOCK_LEVEL = 15
    
    def __init__(self, game_time=None, weather_system=None):
        self.game_time = game_time
        self.weather_system = weather_system
        
        # Town markets
        self.town_markets = {}  # {town_name: TownMarket}
        
        # Global state
        self.price_calculator = PriceCalculator()
        self.sentiment_calculator = MarketSentimentCalculator()
        self.transaction_limits = TransactionLimit()
        
        # Global events (affect all markets)
        self.global_events = []
        
        # Update tracking
        self.last_update_day = 0
        self.last_morning_update = False
        self.last_evening_update = False
        
        # Statistics
        self.total_transactions = 0
        self.total_volume = 0
        
        logger.info("MarketManager initialized")
    
    def register_town_market(self, town_name: str) -> TownMarket:
        """Register a new town market"""
        if town_name not in self.town_markets:
            market = TownMarket(town_name)
            self.town_markets[town_name] = market
            logger.info(f"Registered market for town: {town_name}")
            return market
        return self.town_markets[town_name]
    
    def initialize_starter_supplies(self):
        """Initialize each market with starter supply levels"""
        from market_system import TRADEABLE_COMMODITIES
        
        for town_name, market in self.town_markets.items():
            for commodity_id, commodity in TRADEABLE_COMMODITIES.items():
                # Set initial supply based on commodity type and rarity
                base_supply = 50  # Base supply amount
                
                # Common items have more supply
                if commodity.rarity.value == "common":
                    supply = base_supply * 2
                else:  # uncommon
                    supply = base_supply
                
                # Resources and consumables have higher supply
                if commodity.category.value in ["resource", "food", "consumable"]:
                    supply = int(supply * 1.5)
                
                # Weapons and armor have lower supply
                elif commodity.category.value in ["weapon", "armor"]:
                    supply = int(supply * 0.6)
                
                # Initialize market data for this commodity
                market_data = market.get_or_create_market_data(commodity_id)
                market_data.supply = supply
                market_data.demand = supply // 2  # Initial demand is half of supply
                
                # Calculate initial price
                from price_engine import PriceCalculator
                calculator = PriceCalculator()
                market_data.current_price = calculator.calculate_price(
                    market_data, {}
                )
                
        logger.info("Initialized starter supplies for all markets")
    
    def is_market_unlocked(self, player_level: int) -> bool:
        """Check if player has unlocked market features"""
        return player_level >= self.MARKET_UNLOCK_LEVEL
    
    def get_unlock_requirements(self, player_level: int) -> str:
        """Get text describing unlock requirements"""
        if self.is_market_unlocked(player_level):
            return "Market unlocked!"
        else:
            levels_needed = self.MARKET_UNLOCK_LEVEL - player_level
            return f"Market unlocks at level {self.MARKET_UNLOCK_LEVEL} (need {levels_needed} more levels)"
    
    def update_daily_prices(self, current_day: int, time_period: str):
        """
        Update all market prices (called twice daily - morning and evening)
        
        Args:
            current_day: Current game day
            time_period: 'morning' or 'evening'
        """
        # Check if we've already updated for this period
        if current_day == self.last_update_day:
            if time_period == 'morning' and self.last_morning_update:
                return
            if time_period == 'evening' and self.last_evening_update:
                return
        
        if current_day != self.last_update_day:
            self.last_update_day = current_day
            self.last_morning_update = False
            self.last_evening_update = False
        
        # Regenerate merchant gold reserves (once per day, morning only)
        if time_period == 'morning':
            for town_market in self.town_markets.values():
                town_market.regenerate_gold()
        
        logger.info(f"Updating market prices for day {current_day} ({time_period})")
        
        # Get current conditions
        modifiers = self._get_current_modifiers()
        
        # Update sentiment
        all_market_data = []
        for town_market in self.town_markets.values():
            all_market_data.extend(town_market.market_data.values())
        
        self.sentiment_calculator.update_sentiment(
            all_market_data, 
            self.total_volume,
            self.global_events
        )
        modifiers['global_sentiment'] = self.sentiment_calculator.get_sentiment()
        
        # Update prices for each town market
        for town_name, town_market in self.town_markets.items():
            # Add local events to modifiers
            local_modifiers = modifiers.copy()
            local_modifiers['events'] = modifiers.get('events', []) + town_market.local_events
            
            # Update each commodity
            for commodity_id, market_data in town_market.market_data.items():
                # Calculate new price
                new_price = self.price_calculator.calculate_price(market_data, local_modifiers)
                
                # Apply town prosperity
                new_price *= town_market.prosperity
                
                # Update market data
                market_data.current_price = new_price
                market_data.history.add_price(current_day, new_price, market_data.daily_volume)
                market_data.last_update_day = current_day
                
                # Reset daily volume
                market_data.daily_volume = 0
        
        # Mark this period as updated
        if time_period == 'morning':
            self.last_morning_update = True
        else:
            self.last_evening_update = True
        
        # Cleanup old transaction limit data
        self.transaction_limits.cleanup_old_days(current_day)
    
    def _get_current_modifiers(self) -> Dict:
        """Get current market modifiers from game systems"""
        modifiers = {}
        
        # Weather
        if self.weather_system and hasattr(self.weather_system, 'current_weather'):
            modifiers['weather'] = self.weather_system.current_weather
        
        # Season
        if self.game_time and hasattr(self.game_time, 'get_current_season'):
            modifiers['season'] = self.game_time.get_current_season()
        elif self.game_time and hasattr(self.game_time, 'seasons'):
            # Calculate season from month
            month = getattr(self.game_time, 'month_count', 1)
            season_index = (month - 1) // 3
            modifiers['season'] = self.game_time.seasons[season_index]
        
        # Global events
        modifiers['events'] = self.global_events.copy()
        
        return modifiers
    
    def buy_commodity(self, player, town_name: str, commodity_id: str, quantity: int) -> Tuple[bool, str, float]:
        """
        Process a buy transaction
        
        Returns:
            (success: bool, message: str, total_cost: float)
        """
        # Check market unlocked
        if not self.is_market_unlocked(player.level):
            return False, self.get_unlock_requirements(player.level), 0.0
        
        # Validate commodity
        commodity = get_commodity(commodity_id)
        if not commodity or not commodity.is_tradeable():
            return False, f"{commodity_id} is not tradeable", 0.0
        
        # Validate town market
        if town_name not in self.town_markets:
            return False, f"No market in {town_name}", 0.0
        
        town_market = self.town_markets[town_name]
        market_data = town_market.get_market_data(commodity_id)
        
        if not market_data:
            return False, f"{commodity.name} not available in this market", 0.0
        
        # Check cooldown
        if not market_data.can_trade_now():
            remaining = market_data.get_cooldown_remaining()
            return False, f"Trade cooldown: {remaining:.1f}s remaining", 0.0
        
        # Check transaction limits
        current_day = self.game_time.day_count if self.game_time else 0
        player_id = str(id(player))  # Use object id as player identifier
        
        can_trade, limit_msg = self.transaction_limits.can_trade(player_id, quantity, current_day)
        if not can_trade:
            return False, limit_msg, 0.0
        
        # Check supply
        if market_data.supply < quantity:
            return False, f"Insufficient supply (available: {market_data.supply})", 0.0
        
        # Calculate costs
        unit_price = market_data.current_price
        subtotal = unit_price * quantity
        
        # Transaction fee (reduced by merchant skill)
        merchant_skill = getattr(player, 'merchant_skill_level', 0) if hasattr(player, 'merchant_skill_level') else 0
        fee_percent = max(0.001, town_market.transaction_fees * (1 - merchant_skill / 200))  # Max 50% reduction
        fee = subtotal * fee_percent
        
        total_cost = subtotal + fee
        
        # Check player funds
        player_gold = player.dubloons if hasattr(player, 'dubloons') else 0
        if player_gold < total_cost:
            return False, f"Insufficient funds (need: {total_cost:.2f}, have: {player_gold:.2f})", total_cost
        
        # Execute transaction
        player.dubloons -= total_cost
        town_market.gold_reserve += total_cost  # Merchant gains gold from sale (capped at max)
        town_market.gold_reserve = min(town_market.gold_reserve, town_market.max_gold_reserve)
        
        # Add to player inventory
        if hasattr(player, 'inventory'):
            if isinstance(player.inventory, dict):
                # Simple dict-based inventory
                player.inventory[commodity_id] = player.inventory.get(commodity_id, 0) + quantity
            elif hasattr(player.inventory, 'add_item'):
                # Inventory object with add_item method
                for _ in range(quantity):
                    player.inventory.add_item(commodity_id)
        else:
            logger.warning(f"Player has no inventory system to add {commodity_id}")
        
        # Update market data
        market_data.record_trade(quantity, is_buy=True)
        self.transaction_limits.record_trade(player_id, quantity, current_day)
        
        # Update stats
        self.total_transactions += 1
        self.total_volume += quantity
        
        # Award merchant XP
        if hasattr(player, 'gain_merchant_xp'):
            xp_gain = int(total_cost / 10)  # 1 XP per 10 gold spent
            player.gain_merchant_xp(xp_gain)
        
        logger.info(f"BUY: {player_id} bought {quantity}x {commodity.name} for {total_cost:.2f} in {town_name}")
        
        return True, f"Purchased {quantity}x {commodity.name} for {total_cost:.2f} dubloons", total_cost
    
    def sell_commodity(self, player, town_name: str, commodity_id: str, quantity: int) -> Tuple[bool, str, float]:
        """
        Process a sell transaction
        
        Returns:
            (success: bool, message: str, total_revenue: float)
        """
        # Check market unlocked
        if not self.is_market_unlocked(player.level):
            return False, self.get_unlock_requirements(player.level), 0.0
        
        # Validate commodity
        commodity = get_commodity(commodity_id)
        if not commodity or not commodity.is_tradeable():
            return False, f"{commodity_id} is not tradeable", 0.0
        
        # Validate town market
        if town_name not in self.town_markets:
            return False, f"No market in {town_name}", 0.0
        
        town_market = self.town_markets[town_name]
        market_data = town_market.get_market_data(commodity_id)
        
        if not market_data:
            return False, f"{commodity.name} not available in this market", 0.0
        
        # Check cooldown
        if not market_data.can_trade_now():
            remaining = market_data.get_cooldown_remaining()
            return False, f"Trade cooldown: {remaining:.1f}s remaining", 0.0
        
        # Check transaction limits
        current_day = self.game_time.day_count if self.game_time else 0
        player_id = str(id(player))
        
        can_trade, limit_msg = self.transaction_limits.can_trade(player_id, quantity, current_day)
        if not can_trade:
            return False, limit_msg, 0.0
        
        # Check player inventory
        player_has_items = False
        if hasattr(player, 'inventory'):
            if isinstance(player.inventory, dict):
                player_has_items = player.inventory.get(commodity_id, 0) >= quantity
            elif hasattr(player.inventory, 'count_item'):
                player_has_items = player.inventory.count_item(commodity_id) >= quantity
            elif hasattr(player.inventory, 'has_item'):
                # Check if player has enough items
                count = 0
                for item in player.inventory.get('items', []):
                    if hasattr(item, 'id') and item.id == commodity_id:
                        count += 1
                    elif isinstance(item, str) and item == commodity_id:
                        count += 1
                player_has_items = count >= quantity
        
        if not player_has_items:
            return False, f"You don't have {quantity}x {commodity.name} to sell", 0.0
        
        # Calculate revenue
        unit_price = market_data.current_price
        subtotal = unit_price * quantity
        
        # Transaction fee
        merchant_skill = getattr(player, 'merchant_skill_level', 0) if hasattr(player, 'merchant_skill_level') else 0
        fee_percent = max(0.001, town_market.transaction_fees * (1 - merchant_skill / 200))
        fee = subtotal * fee_percent
        
        total_revenue = subtotal - fee
        
        # Check if merchant has enough gold
        if town_market.gold_reserve < total_revenue:
            return False, f"Merchant only has {town_market.gold_reserve:.0f} gold (need {total_revenue:.0f})", 0.0
        
        # Execute transaction
        player.dubloons += total_revenue
        town_market.gold_reserve -= total_revenue  # Deduct from merchant's reserves
        
        # Remove from player inventory
        if isinstance(player.inventory, dict):
            player.inventory[commodity_id] = player.inventory.get(commodity_id, 0) - quantity
            if player.inventory[commodity_id] <= 0:
                del player.inventory[commodity_id]
        elif hasattr(player.inventory, 'remove_item'):
            for _ in range(quantity):
                player.inventory.remove_item(commodity_id)
        
        # Update market data
        market_data.record_trade(quantity, is_buy=False)
        self.transaction_limits.record_trade(player_id, quantity, current_day)
        
        # Update stats
        self.total_transactions += 1
        self.total_volume += quantity
        
        # Award merchant XP
        if hasattr(player, 'gain_merchant_xp'):
            xp_gain = int(total_revenue / 10)
            player.gain_merchant_xp(xp_gain)
        
        logger.info(f"SELL: {player_id} sold {quantity}x {commodity.name} for {total_revenue:.2f} in {town_name}")
        
        return True, f"Sold {quantity}x {commodity.name} for {total_revenue:.2f} gold", total_revenue
    
    def get_price(self, town_name: str, commodity_id: str) -> Optional[float]:
        """Get current price for a commodity in a town"""
        if town_name in self.town_markets:
            market_data = self.town_markets[town_name].get_market_data(commodity_id)
            if market_data:
                return market_data.current_price
        return None
    
    def get_all_town_prices(self, commodity_id: str) -> Dict[str, float]:
        """Get prices for a commodity across all towns"""
        prices = {}
        for town_name, town_market in self.town_markets.items():
            market_data = town_market.get_market_data(commodity_id)
            if market_data:
                prices[town_name] = market_data.current_price
        return prices
    
    def find_arbitrage_opportunities(self, commodity_id: str) -> Optional[Dict]:
        """Find best arbitrage opportunity for a commodity"""
        town_prices = self.get_all_town_prices(commodity_id)
        return self.price_calculator.calculate_arbitrage_opportunity(town_prices)
    
    def add_global_event(self, event: str):
        """Add a global event affecting all markets"""
        if event not in self.global_events:
            self.global_events.append(event)
            logger.info(f"Global market event: {event}")
    
    def remove_global_event(self, event: str):
        """Remove a global event"""
        if event in self.global_events:
            self.global_events.remove(event)
    
    def get_market_summary(self, town_name: str = None) -> Dict:
        """Get summary of market state"""
        summary = {
            'sentiment': self.sentiment_calculator.get_sentiment_description(),
            'sentiment_value': self.sentiment_calculator.get_sentiment(),
            'total_transactions': self.total_transactions,
            'total_volume': self.total_volume,
            'global_events': self.global_events.copy(),
        }
        
        if town_name and town_name in self.town_markets:
            town_market = self.town_markets[town_name]
            summary['town_events'] = town_market.local_events.copy()
            summary['prosperity'] = town_market.prosperity
            summary['active'] = town_market.active
        
        return summary
    
    def save_state(self) -> dict:
        """Save market state for persistence"""
        state = {
            'last_update_day': self.last_update_day,
            'global_events': self.global_events,
            'total_transactions': self.total_transactions,
            'total_volume': self.total_volume,
            'sentiment': self.sentiment_calculator.get_sentiment(),
            'town_markets': {}
        }
        
        for town_name, town_market in self.town_markets.items():
            state['town_markets'][town_name] = {
                'prosperity': town_market.prosperity,
                'local_events': town_market.local_events,
                'market_data': {
                    commodity_id: md.to_dict()
                    for commodity_id, md in town_market.market_data.items()
                }
            }
        
        return state
    
    def load_state(self, state: dict):
        """Load market state from save"""
        self.last_update_day = state.get('last_update_day', 0)
        self.global_events = state.get('global_events', [])
        self.total_transactions = state.get('total_transactions', 0)
        self.total_volume = state.get('total_volume', 0)
        self.sentiment_calculator.sentiment = state.get('sentiment', 0.0)
        
        # Note: Full market data restoration would require more complex deserialization
        # For now, we'll reinitialize markets and just restore key values
        logger.info("Market state loaded")
