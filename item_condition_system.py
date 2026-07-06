"""
Item Quality/Condition System
Items have condition states that affect price and durability
"""

import random
from typing import Dict, Tuple
from logger_config import logger


class ItemCondition:
    """Represents the condition/quality of an item"""
    
    # Condition states with value multipliers and durability multipliers
    CONDITIONS = {
        'Perfect': {'value_mult': 1.3, 'durability_mult': 1.2, 'description': 'Brand new, flawless'},
        'Excellent': {'value_mult': 1.15, 'durability_mult': 1.1, 'description': 'Like new'},
        'Good': {'value_mult': 1.0, 'durability_mult': 1.0, 'description': 'Well maintained'},
        'Worn': {'value_mult': 0.75, 'durability_mult': 0.85, 'description': 'Shows wear'},
        'Damaged': {'value_mult': 0.5, 'durability_mult': 0.6, 'description': 'Needs repair'},
        'Poor': {'value_mult': 0.3, 'durability_mult': 0.4, 'description': 'Barely functional'},
    }
    
    CONDITION_ORDER = ['Perfect', 'Excellent', 'Good', 'Worn', 'Damaged', 'Poor']
    
    def __init__(self, condition: str = 'Good'):
        """Initialize with a condition state"""
        if condition not in self.CONDITIONS:
            condition = 'Good'
        self.condition = condition
        self.wear_points = 0  # Accumulates as item is used
        
    def get_value_multiplier(self) -> float:
        """Get price multiplier based on condition"""
        return self.CONDITIONS[self.condition]['value_mult']
    
    def get_durability_multiplier(self) -> float:
        """Get durability multiplier"""
        return self.CONDITIONS[self.condition]['durability_mult']
    
    def get_description(self) -> str:
        """Get condition description"""
        return self.CONDITIONS[self.condition]['description']
    
    def degrade(self, amount: int = 1):
        """Degrade the item condition"""
        self.wear_points += amount
        
        # Check if condition should drop
        current_index = self.CONDITION_ORDER.index(self.condition)
        
        # Each condition level requires more wear to degrade
        threshold = (current_index + 1) * 20
        
        if self.wear_points >= threshold and current_index < len(self.CONDITION_ORDER) - 1:
            old_condition = self.condition
            self.condition = self.CONDITION_ORDER[current_index + 1]
            self.wear_points = 0  # Reset wear points
            logger.info(f"[CONDITION] Item degraded: {old_condition} → {self.condition}")
            return True
        
        return False
    
    def repair(self, quality: str = 'Good'):
        """Repair item to specified quality"""
        if quality in self.CONDITIONS:
            self.condition = quality
            self.wear_points = 0
            logger.info(f"[CONDITION] Item repaired to {quality}")
            return True
        return False
    
    def can_repair_to(self, target_condition: str) -> bool:
        """Check if can repair to target condition"""
        current_index = self.CONDITION_ORDER.index(self.condition)
        target_index = self.CONDITION_ORDER.index(target_condition)
        # Can't repair beyond original condition without special skills
        return target_index <= current_index
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'condition': self.condition,
            'wear_points': self.wear_points
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize"""
        instance = cls(data.get('condition', 'Good'))
        instance.wear_points = data.get('wear_points', 0)
        return instance


class ConditionManager:
    """Manages item conditions across the game"""
    
    def __init__(self):
        self.item_conditions: Dict[str, ItemCondition] = {}  # item_id → ItemCondition
        
    def register_item(self, item_id: str, initial_condition: str = 'Good'):
        """Register an item with a condition"""
        if item_id not in self.item_conditions:
            self.item_conditions[item_id] = ItemCondition(initial_condition)
            
    def get_condition(self, item_id: str) -> ItemCondition:
        """Get condition for an item"""
        if item_id not in self.item_conditions:
            self.register_item(item_id)
        return self.item_conditions[item_id]
    
    def degrade_item(self, item_id: str, amount: int = 1) -> bool:
        """Degrade an item's condition"""
        condition = self.get_condition(item_id)
        return condition.degrade(amount)
    
    def repair_item(self, item_id: str, target_quality: str = 'Good') -> bool:
        """Repair an item"""
        condition = self.get_condition(item_id)
        return condition.repair(target_quality)
    
    def get_adjusted_price(self, item_id: str, base_price: int) -> int:
        """Get price adjusted for condition"""
        condition = self.get_condition(item_id)
        multiplier = condition.get_value_multiplier()
        return int(base_price * multiplier)
    
    def generate_clearance_bin_items(self, shop_items: list) -> list:
        """Generate clearance bin items (damaged goods at discount)"""
        clearance = []
        
        for item in shop_items:
            # 20% chance each item has damaged variant
            if random.random() < 0.2:
                damaged_item = {
                    'item_id': item.item_id,
                    'name': item.name,
                    'condition': random.choice(['Worn', 'Damaged', 'Poor']),
                    'base_price': item.buy_price,
                    'category': item.category
                }
                clearance.append(damaged_item)
                
        return clearance
    
    def get_repair_cost(self, item_id: str, target_condition: str, base_value: int) -> int:
        """Calculate repair cost"""
        current_condition = self.get_condition(item_id)
        current_index = ItemCondition.CONDITION_ORDER.index(current_condition.condition)
        target_index = ItemCondition.CONDITION_ORDER.index(target_condition)
        
        # Cost = difference in condition levels * 20% of base value
        levels_to_repair = current_index - target_index
        if levels_to_repair <= 0:
            return 0
            
        return int(base_value * 0.2 * levels_to_repair)
    
    def on_item_used(self, item_id: str, use_type: str = 'normal'):
        """Called when item is used (combat, gathering, etc)"""
        degradation_rates = {
            'normal': 1,
            'combat': 2,
            'heavy_combat': 3,
            'gathering': 1,
            'crafting': 1
        }
        
        amount = degradation_rates.get(use_type, 1)
        degraded = self.degrade_item(item_id, amount)
        
        if degraded:
            return f"Your {item_id} is showing wear and tear!"
        return None
    
    def to_dict(self) -> dict:
        """Serialize all conditions"""
        return {
            item_id: condition.to_dict() 
            for item_id, condition in self.item_conditions.items()
        }
    
    def from_dict(self, data: dict):
        """Deserialize all conditions"""
        self.item_conditions = {
            item_id: ItemCondition.from_dict(cond_data)
            for item_id, cond_data in data.items()
        }
