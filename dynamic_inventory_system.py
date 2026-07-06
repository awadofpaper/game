"""
Dynamic Shop Inventory System
Manages limited stock, rare items, town specializations, and demand-based restocking
"""

import logging
import random
from typing import Dict, List, Optional
from shop_system import ShopItem, ShopCategory

logger = logging.getLogger(__name__)


class TownSpecialization:
    """Defines what types of items a town specializes in"""
    
    COASTAL = {
        'name': 'Coastal',
        'bonus_categories': [ShopCategory.CONSUMABLES],
        'special_items': ['fish', 'net', 'boat_supplies', 'pearl', 'seaweed', 'salt'],
        'stock_multiplier': 1.5,
        'price_modifier': 0.8  # 20% cheaper for specialized items
    }
    
    MINING = {
        'name': 'Mining',
        'bonus_categories': [ShopCategory.MATERIALS, ShopCategory.WEAPONS],
        'special_items': ['iron_ore', 'copper_ore', 'coal', 'pickaxe', 'mining_helmet', 'dynamite'],
        'stock_multiplier': 2.0,
        'price_modifier': 0.7  # 30% cheaper for specialized items
    }
    
    FARMING = {
        'name': 'Farming',
        'bonus_categories': [ShopCategory.CONSUMABLES],
        'special_items': ['wheat', 'corn', 'carrot', 'potato', 'milk', 'cheese', 'scythe', 'hoe'],
        'stock_multiplier': 2.0,
        'price_modifier': 0.75
    }
    
    FOREST = {
        'name': 'Forest',
        'bonus_categories': [ShopCategory.WEAPONS, ShopCategory.MATERIALS],
        'special_items': ['wood', 'lumber', 'bow', 'arrow', 'rope', 'herbs', 'mushroom'],
        'stock_multiplier': 1.8,
        'price_modifier': 0.8
    }
    
    TRADE_HUB = {
        'name': 'Trade Hub',
        'bonus_categories': [ShopCategory.CONSUMABLES, ShopCategory.MATERIALS],
        'special_items': ['exotic_spice', 'silk', 'perfume', 'rare_gem'],
        'stock_multiplier': 1.2,
        'price_modifier': 1.1  # 10% more expensive (middleman markup)
    }
    
    MILITARY = {
        'name': 'Military',
        'bonus_categories': [ShopCategory.WEAPONS, ShopCategory.ARMOR],
        'special_items': ['military_sword', 'chainmail', 'shield', 'helmet', 'war_horse'],
        'stock_multiplier': 1.5,
        'price_modifier': 0.85
    }
    
    @staticmethod
    def get_specialization(town_name: str) -> dict:
        """Get specialization based on town name/type"""
        town_lower = town_name.lower()
        
        if 'harbor' in town_lower or 'port' in town_lower or 'coast' in town_lower or 'wave' in town_lower:
            return TownSpecialization.COASTAL
        elif 'stone' in town_lower or 'mine' in town_lower or 'forge' in town_lower:
            return TownSpecialization.MINING
        elif 'meadow' in town_lower or 'farm' in town_lower or 'field' in town_lower:
            return TownSpecialization.FARMING
        elif 'wood' in town_lower or 'forest' in town_lower or 'pine' in town_lower or 'heart' in town_lower:
            return TownSpecialization.FOREST
        elif 'capital' in town_lower or 'city' in town_lower or 'crossing' in town_lower:
            return TownSpecialization.TRADE_HUB
        elif 'fort' in town_lower or 'guard' in town_lower or 'watch' in town_lower:
            return TownSpecialization.MILITARY
        else:
            return TownSpecialization.TRADE_HUB  # Default


class RareItemPool:
    """Pool of rare items that can randomly appear in shops"""
    
    RARE_ITEMS = [
        # Legendary Weapons
        ShopItem("excalibur_replica", "Excalibur Replica", ShopCategory.WEAPONS, 5000, 2500, 1,
                "A masterwork replica of the legendary sword", {"damage": 50, "rarity": "legendary"}),
        ShopItem("dragonbone_bow", "Dragonbone Bow", ShopCategory.WEAPONS, 3500, 1750, 1,
                "Carved from ancient dragon remains", {"damage": 40, "range": 300, "rarity": "legendary"}),
        ShopItem("shadowstrike_dagger", "Shadowstrike Dagger", ShopCategory.WEAPONS, 2800, 1400, 1,
                "Grants bonus stealth damage", {"damage": 25, "stealth_bonus": 50, "rarity": "rare"}),
        
        # Legendary Armor
        ShopItem("dragonscale_armor", "Dragonscale Armor", ShopCategory.ARMOR, 4500, 2250, 1,
                "Impervious dragon scales", {"defense": 50, "fire_resist": 80, "rarity": "legendary"}),
        ShopItem("assassin_cloak", "Assassin's Cloak", ShopCategory.ARMOR, 3000, 1500, 1,
                "Enhances stealth capabilities", {"defense": 20, "stealth": 100, "rarity": "rare"}),
        ShopItem("plate_of_the_ancients", "Plate of the Ancients", ShopCategory.ARMOR, 5500, 2750, 1,
                "Legendary full plate armor", {"defense": 60, "rarity": "legendary"}),
        
        # Rare Consumables
        ShopItem("elixir_of_life", "Elixir of Life", ShopCategory.CONSUMABLES, 1000, 500, 1,
                "Fully restores HP and cures all ailments", {"healing": 9999, "rarity": "rare"}),
        ShopItem("phoenix_down", "Phoenix Down", ShopCategory.CONSUMABLES, 800, 400, 2,
                "Revives from death", {"revive": True, "rarity": "rare"}),
        ShopItem("dragons_breath_potion", "Dragon's Breath Potion", ShopCategory.CONSUMABLES, 600, 300, 3,
                "Grants fire breath for 60 seconds", {"fire_damage": 100, "duration": 60, "rarity": "rare"}),
        
        # Rare Materials
        ShopItem("mythril_ingot", "Mythril Ingot", ShopCategory.MATERIALS, 2500, 1250, 2,
                "Legendary crafting material", {"rarity": "legendary"}),
        ShopItem("star_metal", "Star Metal", ShopCategory.MATERIALS, 3000, 1500, 1,
                "Metal from a fallen star", {"rarity": "legendary"}),
        ShopItem("philosophers_stone", "Philosopher's Stone", ShopCategory.MATERIALS, 10000, 5000, 1,
                "Transmutes base metals to gold", {"rarity": "legendary"}),
    ]
    
    @staticmethod
    def get_random_rare_item() -> Optional[ShopItem]:
        """Get a random rare item with low probability"""
        if random.random() < 0.3:  # 30% chance of rare item appearing
            return random.choice(RareItemPool.RARE_ITEMS)
        return None


class DemandTracker:
    """Tracks what items sell well to influence restocking"""
    
    def __init__(self):
        self.sales_history: Dict[str, int] = {}  # item_id -> units sold
        self.demand_score: Dict[str, float] = {}  # item_id -> demand score (0-100)
        
    def record_sale(self, item_id: str, quantity: int = 1):
        """Record a sale to track demand"""
        self.sales_history[item_id] = self.sales_history.get(item_id, 0) + quantity
        self._update_demand_score(item_id)
    
    def _update_demand_score(self, item_id: str):
        """Calculate demand score based on sales history"""
        sales = self.sales_history.get(item_id, 0)
        # Demand score: 0-100, higher = stock more
        self.demand_score[item_id] = min(100, sales * 10)  # 10 points per sale, max 100
    
    def get_demand_multiplier(self, item_id: str) -> float:
        """Get stock multiplier based on demand (1.0 to 3.0)"""
        demand = self.demand_score.get(item_id, 50)  # Default 50 (neutral)
        return 1.0 + (demand / 50.0)  # 1.0 at 0 demand, 3.0 at 100 demand
    
    def get_hot_items(self, top_n: int = 5) -> List[str]:
        """Get list of high-demand items"""
        sorted_items = sorted(self.demand_score.items(), key=lambda x: x[1], reverse=True)
        return [item_id for item_id, _ in sorted_items[:top_n]]
    
    def decay_demand(self, decay_rate: float = 0.9):
        """Gradually reduce demand over time (called weekly)"""
        for item_id in self.demand_score:
            self.demand_score[item_id] *= decay_rate


class DynamicInventoryManager:
    """Manages dynamic inventory for all shops"""
    
    def __init__(self):
        self.demand_trackers: Dict[str, DemandTracker] = {}  # shop_id -> DemandTracker
        self.specializations: Dict[str, dict] = {}  # shop_id -> specialization
        self.last_weekly_update = 0
        
    def register_shop(self, shop_id: str, town_name: str):
        """Register a shop with town specialization"""
        self.demand_trackers[shop_id] = DemandTracker()
        self.specializations[shop_id] = TownSpecialization.get_specialization(town_name)
        logger.info(f"[DYNAMIC INVENTORY] {shop_id} specialized in {self.specializations[shop_id]['name']}")
    
    def record_sale(self, shop_id: str, item_id: str, quantity: int = 1):
        """Record sale for demand tracking"""
        if shop_id in self.demand_trackers:
            self.demand_trackers[shop_id].record_sale(item_id, quantity)
    
    def get_restock_quantity(self, shop_id: str, item: ShopItem, base_quantity: int) -> int:
        """Calculate restock quantity based on demand and specialization"""
        quantity = base_quantity
        
        # Apply demand multiplier
        if shop_id in self.demand_trackers:
            demand_mult = self.demand_trackers[shop_id].get_demand_multiplier(item.item_id)
            quantity = int(quantity * demand_mult)
        
        # Apply specialization multiplier
        if shop_id in self.specializations:
            spec = self.specializations[shop_id]
            if item.category in spec['bonus_categories'] or item.item_id in spec['special_items']:
                quantity = int(quantity * spec['stock_multiplier'])
        
        return max(1, quantity)
    
    def get_specialized_price(self, shop_id: str, item: ShopItem, base_price: int) -> int:
        """Get price modified by town specialization"""
        if shop_id in self.specializations:
            spec = self.specializations[shop_id]
            if item.category in spec['bonus_categories'] or item.item_id in spec['special_items']:
                return int(base_price * spec['price_modifier'])
        return base_price
    
    def should_stock_rare_item(self, shop_id: str) -> Optional[ShopItem]:
        """Determine if shop should stock a rare item today"""
        # Higher chance for trade hubs and high-reputation shops
        base_chance = 0.05  # 5% base chance
        
        if shop_id in self.specializations:
            spec = self.specializations[shop_id]
            if spec['name'] == 'Trade Hub':
                base_chance = 0.15  # 15% for trade hubs
        
        if random.random() < base_chance:
            return RareItemPool.get_random_rare_item()
        return None
    
    def weekly_update(self, current_day: int):
        """Perform weekly maintenance (decay demand)"""
        if current_day // 7 > self.last_weekly_update:
            self.last_weekly_update = current_day // 7
            for tracker in self.demand_trackers.values():
                tracker.decay_demand(0.85)  # 15% decay per week
            logger.info("[DYNAMIC INVENTORY] Weekly demand decay applied")
    
    def get_shop_summary(self, shop_id: str) -> str:
        """Get summary of shop's dynamic state"""
        if shop_id not in self.demand_trackers:
            return "No data available"
        
        tracker = self.demand_trackers[shop_id]
        spec = self.specializations.get(shop_id, {})
        
        hot_items = tracker.get_hot_items(3)
        spec_name = spec.get('name', 'None')
        
        summary = f"Specialization: {spec_name}\n"
        if hot_items:
            summary += f"High Demand: {', '.join(hot_items[:3])}\n"
        else:
            summary += "High Demand: None yet\n"
        
        return summary
    
    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'demand_trackers': {
                shop_id: {
                    'sales_history': tracker.sales_history,
                    'demand_score': tracker.demand_score
                }
                for shop_id, tracker in self.demand_trackers.items()
            },
            'last_weekly_update': self.last_weekly_update
        }
    
    def from_dict(self, data: dict):
        """Load from save data"""
        if 'demand_trackers' in data:
            for shop_id, tracker_data in data['demand_trackers'].items():
                if shop_id in self.demand_trackers:
                    self.demand_trackers[shop_id].sales_history = tracker_data.get('sales_history', {})
                    self.demand_trackers[shop_id].demand_score = tracker_data.get('demand_score', {})
        
        self.last_weekly_update = data.get('last_weekly_update', 0)
