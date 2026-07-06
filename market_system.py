"""
Market Economy System - Core Data Structures
Handles commodity trading, price tracking, and market data management
"""

import time
import json
from typing import Dict, List, Tuple, Optional
from enum import Enum
from collections import deque


class CommodityCategory(Enum):
    """Categories for tradeable items"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    RESOURCE = "resource"
    CRAFTING_MATERIAL = "crafting_material"
    TOOL = "tool"
    FOOD = "food"
    POTION = "potion"
    MISC = "misc"


class CommodityRarity(Enum):
    """Rarity levels - only Common/Uncommon are tradeable"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"  # NOT tradeable
    EPIC = "epic"  # NOT tradeable
    LEGENDARY = "legendary"  # NOT tradeable


class Commodity:
    """Represents a tradeable item in the market"""
    
    def __init__(self, item_id: str, name: str, category: CommodityCategory, 
                 base_price: float, rarity: CommodityRarity = CommodityRarity.COMMON,
                 weather_sensitive: bool = False, seasonal_item: bool = False,
                 volatility: float = 0.2):
        self.item_id = item_id
        self.name = name
        self.category = category
        self.base_price = base_price
        self.rarity = rarity
        self.weather_sensitive = weather_sensitive
        self.seasonal_item = seasonal_item
        self.volatility = volatility  # 0.0 = stable, 1.0 = extreme volatility
        
        # Market constraints
        self.min_price = base_price * 0.1  # Can drop to 10% of base
        self.max_price = base_price * 100  # Can spike to 100x base (absurdity allowed!)
        
        # Trading rules
        self.tradeable = rarity in [CommodityRarity.COMMON, CommodityRarity.UNCOMMON]
        
    def is_tradeable(self) -> bool:
        """Check if this commodity can be traded"""
        return self.tradeable
    
    def get_price_range(self) -> Tuple[float, float]:
        """Get the allowed price range for this commodity"""
        return (self.min_price, self.max_price)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'category': self.category.value,
            'base_price': self.base_price,
            'rarity': self.rarity.value,
            'weather_sensitive': self.weather_sensitive,
            'seasonal_item': self.seasonal_item,
            'volatility': self.volatility,
            'tradeable': self.tradeable
        }


class PriceHistory:
    """Tracks historical prices for a commodity"""
    
    def __init__(self, max_days: int = 30):
        self.max_days = max_days
        self.prices = deque(maxlen=max_days)  # (day, price) tuples
        self.volumes = deque(maxlen=max_days)  # (day, volume) tuples
        
    def add_price(self, day: int, price: float, volume: int = 0):
        """Record a price for a given day"""
        self.prices.append((day, price))
        self.volumes.append((day, volume))
    
    def get_latest_price(self) -> Optional[float]:
        """Get the most recent price"""
        if self.prices:
            return self.prices[-1][1]
        return None
    
    def get_price_trend(self, days: int = 7) -> str:
        """Determine price trend (up, down, stable)"""
        if len(self.prices) < 2:
            return "stable"
        
        recent = list(self.prices)[-days:]
        if len(recent) < 2:
            return "stable"
        
        start_price = recent[0][1]
        end_price = recent[-1][1]
        change_percent = ((end_price - start_price) / start_price) * 100
        
        if change_percent > 10:
            return "rising"
        elif change_percent < -10:
            return "falling"
        else:
            return "stable"
    
    def get_price_change_percent(self, days: int = 1) -> float:
        """Get percentage change over specified days"""
        if len(self.prices) < days + 1:
            return 0.0
        
        old_price = list(self.prices)[-(days + 1)][1]
        new_price = list(self.prices)[-1][1]
        
        return ((new_price - old_price) / old_price) * 100
    
    def get_average_price(self, days: int = 7) -> float:
        """Get average price over specified days"""
        if not self.prices:
            return 0.0
        
        recent = list(self.prices)[-days:]
        return sum(p[1] for p in recent) / len(recent)
    
    def get_volatility(self, days: int = 7) -> float:
        """Calculate price volatility (standard deviation)"""
        if len(self.prices) < 2:
            return 0.0
        
        recent = list(self.prices)[-days:]
        prices = [p[1] for p in recent]
        
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5
        
        return std_dev / mean if mean > 0 else 0.0


class MarketData:
    """Market data for a specific commodity in a specific town"""
    
    def __init__(self, commodity: Commodity, town_name: str):
        self.commodity = commodity
        self.town_name = town_name
        
        # Current market state
        self.current_price = commodity.base_price
        self.supply = 100  # Current supply level (0-1000+)
        self.demand = 100  # Current demand level (0-1000+)
        self.last_update_day = 0
        
        # Trading volume
        self.daily_volume = 0  # Units traded today
        self.total_volume = 0  # All-time volume
        
        # Price tracking
        self.history = PriceHistory(max_days=30)
        self.history.add_price(0, self.current_price, 0)
        
        # Market state
        self.market_sentiment = 0.0  # -1.0 (bearish) to +1.0 (bullish)
        self.last_trade_time = 0
        self.trade_cooldown_seconds = 5  # 5 seconds between large trades
        
    def update_supply(self, amount: int):
        """Update supply (positive = increase, negative = decrease)"""
        self.supply = max(0, self.supply + amount)
    
    def update_demand(self, amount: int):
        """Update demand (positive = increase, negative = decrease)"""
        self.demand = max(0, self.demand + amount)
    
    def record_trade(self, quantity: int, is_buy: bool):
        """Record a trade transaction"""
        self.daily_volume += quantity
        self.total_volume += quantity
        self.last_trade_time = time.time()
        
        # Update supply/demand based on trade
        if is_buy:
            self.update_supply(-quantity)
            self.update_demand(quantity)
        else:
            self.update_supply(quantity)
            self.update_demand(-quantity)
    
    def can_trade_now(self) -> bool:
        """Check if cooldown has expired"""
        return time.time() - self.last_trade_time >= self.trade_cooldown_seconds
    
    def get_cooldown_remaining(self) -> float:
        """Get remaining cooldown time in seconds"""
        elapsed = time.time() - self.last_trade_time
        remaining = self.trade_cooldown_seconds - elapsed
        return max(0, remaining)
    
    def calculate_supply_demand_ratio(self) -> float:
        """Calculate supply to demand ratio"""
        if self.demand == 0:
            return 10.0  # High ratio = oversupply
        return self.supply / self.demand
    
    def get_scarcity_multiplier(self) -> float:
        """Get price multiplier based on scarcity"""
        if self.supply <= 0:
            return 10.0  # Last item = extreme premium
        elif self.supply <= 5:
            return 3.0  # Very scarce
        elif self.supply <= 20:
            return 1.5  # Scarce
        elif self.supply <= 50:
            return 1.0  # Normal
        elif self.supply <= 200:
            return 0.8  # Abundant
        else:
            return 0.5  # Oversupply
    
    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'commodity_id': self.commodity.item_id,
            'town_name': self.town_name,
            'current_price': self.current_price,
            'supply': self.supply,
            'demand': self.demand,
            'daily_volume': self.daily_volume,
            'total_volume': self.total_volume,
            'market_sentiment': self.market_sentiment,
            'price_trend': self.history.get_price_trend(),
            'price_change_7d': self.history.get_price_change_percent(7)
        }


class TransactionLimit:
    """Manages transaction limits per player"""
    
    def __init__(self):
        self.max_single_transaction = 1000  # Max quantity per trade
        self.daily_transaction_limit = 10000  # Max total quantity per day
        self.daily_volume = {}  # {player_id: {day: volume}}
        
    def can_trade(self, player_id: str, quantity: int, current_day: int) -> Tuple[bool, str]:
        """Check if a trade is allowed"""
        # Check single transaction limit
        if quantity > self.max_single_transaction:
            return False, f"Maximum {self.max_single_transaction} units per transaction"
        
        # Check daily limit
        if player_id not in self.daily_volume:
            self.daily_volume[player_id] = {}
        
        if current_day not in self.daily_volume[player_id]:
            self.daily_volume[player_id][current_day] = 0
        
        current_volume = self.daily_volume[player_id][current_day]
        if current_volume + quantity > self.daily_transaction_limit:
            remaining = self.daily_transaction_limit - current_volume
            return False, f"Daily limit reached. Remaining: {remaining} units"
        
        return True, "OK"
    
    def record_trade(self, player_id: str, quantity: int, current_day: int):
        """Record a trade for limit tracking"""
        if player_id not in self.daily_volume:
            self.daily_volume[player_id] = {}
        
        if current_day not in self.daily_volume[player_id]:
            self.daily_volume[player_id][current_day] = 0
        
        self.daily_volume[player_id][current_day] += quantity
    
    def cleanup_old_days(self, current_day: int, keep_days: int = 7):
        """Remove old day data to prevent memory bloat"""
        cutoff_day = current_day - keep_days
        
        for player_id in list(self.daily_volume.keys()):
            days_to_remove = [day for day in self.daily_volume[player_id] if day < cutoff_day]
            for day in days_to_remove:
                del self.daily_volume[player_id][day]
            
            # Remove player if no data
            if not self.daily_volume[player_id]:
                del self.daily_volume[player_id]


# Global commodity database - will be populated from existing game items
TRADEABLE_COMMODITIES = {}


def initialize_commodities():
    """Initialize the commodity database from game items"""
    from equipment import EQUIPMENT_DATA
    
    global TRADEABLE_COMMODITIES
    
    commodities = {}
    
    # ===== EQUIPMENT ITEMS (Common & Uncommon only) =====
    for item_id, item_data in EQUIPMENT_DATA.items():
        rarity = item_data.get("rarity", "common")
        if rarity not in ["common", "uncommon"]:
            continue
            
        slot = item_data.get("slot", "")
        item_type = item_data.get("type", "")
        base_value = item_data.get("value", 10)
        
        # Determine category
        if item_type == "weapon":
            category = CommodityCategory.WEAPON
        elif item_type in ["armor", "shield"]:
            category = CommodityCategory.ARMOR
        elif item_type == "accessory":
            category = CommodityCategory.MISC
        else:
            category = CommodityCategory.TOOL
        
        # Set rarity
        commodity_rarity = CommodityRarity.UNCOMMON if rarity == "uncommon" else CommodityRarity.COMMON
        
        # Determine volatility (weapons/armor more volatile than accessories)
        if item_type == "weapon":
            volatility = 0.7  # High volatility - combat drives demand
        elif item_type in ["armor", "shield"]:
            volatility = 0.6  # Medium-high volatility
        else:
            volatility = 0.4  # Lower volatility for accessories
        
        # Base price = value * 10 (market markup)
        base_price = base_value * 10
        
        commodities[item_id] = Commodity(
            item_id,
            item_data.get("name", item_id.replace("_", " ").title()),
            category,
            base_price,
            commodity_rarity,
            volatility=volatility
        )
    
    # ===== CRAFTING MATERIALS & RESOURCES =====
    crafting_materials = {
        # Basic resources (wood, fiber, rubble are worthless - not tradeable)
        "stone": Commodity("stone", "Stone", CommodityCategory.RESOURCE, 3, CommodityRarity.COMMON, volatility=0.5),
        "stick": Commodity("stick", "Stick", CommodityCategory.RESOURCE, 1, CommodityRarity.COMMON, volatility=0.4),
        "rope": Commodity("rope", "Rope", CommodityCategory.CRAFTING_MATERIAL, 8, CommodityRarity.COMMON, volatility=0.5),
        "cloth": Commodity("cloth", "Cloth", CommodityCategory.CRAFTING_MATERIAL, 12, CommodityRarity.COMMON, volatility=0.6),
        
        # Minerals & ores
        "ore": Commodity("ore", "Iron Ore", CommodityCategory.RESOURCE, 15, CommodityRarity.COMMON, volatility=0.7),
        "iron_ore": Commodity("iron_ore", "Iron Ore", CommodityCategory.RESOURCE, 15, CommodityRarity.COMMON, volatility=0.7),
        "ash": Commodity("ash", "Ash", CommodityCategory.RESOURCE, 2, CommodityRarity.COMMON, volatility=0.4),
        
        # Botanical
        "herbs": Commodity("herbs", "Herbs", CommodityCategory.CRAFTING_MATERIAL, 10, CommodityRarity.COMMON, seasonal_item=True, volatility=0.8),
        "berries": Commodity("berries", "Berries", CommodityCategory.FOOD, 5, CommodityRarity.COMMON, weather_sensitive=True, seasonal_item=True, volatility=0.9),
        "mushroom": Commodity("mushroom", "Mushroom", CommodityCategory.FOOD, 7, CommodityRarity.COMMON, weather_sensitive=True, volatility=0.7),
        "apple": Commodity("apple", "Apple", CommodityCategory.FOOD, 4, CommodityRarity.COMMON, seasonal_item=True, volatility=0.8),
    }
    
    # ===== CONSUMABLES =====
    consumables = {
        # Food
        "bread": Commodity("bread", "Bread", CommodityCategory.FOOD, 10, CommodityRarity.COMMON, weather_sensitive=True, seasonal_item=True, volatility=0.8),
        "fish": Commodity("fish", "Fish", CommodityCategory.FOOD, 8, CommodityRarity.COMMON, weather_sensitive=True, seasonal_item=True, volatility=0.9),
        "food": Commodity("food", "Food", CommodityCategory.FOOD, 6, CommodityRarity.COMMON, weather_sensitive=True, volatility=0.8),
        
        # Potions
        "health_potion": Commodity("health_potion", "Health Potion", CommodityCategory.POTION, 50, CommodityRarity.COMMON, volatility=0.6),
        "mana_potion": Commodity("mana_potion", "Mana Potion", CommodityCategory.POTION, 45, CommodityRarity.COMMON, volatility=0.6),
        "potion": Commodity("potion", "Potion", CommodityCategory.POTION, 40, CommodityRarity.COMMON, volatility=0.5),
        "antidote": Commodity("antidote", "Antidote", CommodityCategory.POTION, 35, CommodityRarity.COMMON, volatility=0.7),
        "strength_potion": Commodity("strength_potion", "Strength Potion", CommodityCategory.POTION, 60, CommodityRarity.UNCOMMON, volatility=0.5),
        "defense_potion": Commodity("defense_potion", "Defense Potion", CommodityCategory.POTION, 55, CommodityRarity.UNCOMMON, volatility=0.5),
        "stamina_potion": Commodity("stamina_potion", "Stamina Potion", CommodityCategory.POTION, 50, CommodityRarity.UNCOMMON, volatility=0.5),
        
        # Medical supplies
        "bandage": Commodity("bandage", "Bandage", CommodityCategory.CONSUMABLE, 15, CommodityRarity.COMMON, volatility=0.6),
        
        # Scrolls & other
        "scroll": Commodity("scroll", "Scroll", CommodityCategory.MISC, 25, CommodityRarity.COMMON, volatility=0.4),
    }
    
    # ===== TOOLS =====
    tools = {
        "torch": Commodity("torch", "Torch", CommodityCategory.TOOL, 5, CommodityRarity.COMMON, volatility=0.3),
        "lockpick": Commodity("lockpick", "Lockpick", CommodityCategory.TOOL, 20, CommodityRarity.COMMON, volatility=0.6),
        "campfire": Commodity("campfire", "Campfire", CommodityCategory.TOOL, 25, CommodityRarity.COMMON, volatility=0.4),
        "backpack": Commodity("backpack", "Backpack", CommodityCategory.TOOL, 100, CommodityRarity.UNCOMMON, volatility=0.3),
    }
    
    # Merge all categories
    commodities.update(crafting_materials)
    commodities.update(consumables)
    commodities.update(tools)
    
    TRADEABLE_COMMODITIES = commodities


def get_commodity(item_id: str) -> Optional[Commodity]:
    """Get a commodity by ID"""
    return TRADEABLE_COMMODITIES.get(item_id)


def is_tradeable(item_id: str) -> bool:
    """Check if an item is tradeable in the market"""
    commodity = get_commodity(item_id)
    return commodity is not None and commodity.is_tradeable()


# Initialize on module load
initialize_commodities()
