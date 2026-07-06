"""
Building Expansions System
Adds advanced trading features to existing buildings:
- Blacksmith: Equipment selling
- Tavern: Food trading
- Market: Player stalls
- Bank: Safety deposit boxes
"""

import pygame
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# BLACKSMITH EQUIPMENT SELLING
# =============================================================================

class EquipmentBuybackSystem:
    """Manages blacksmith equipment purchasing from players"""
    
    def __init__(self):
        # Base prices for different equipment types
        self.base_prices = {
            'weapon': 50,
            'armor': 40,
            'shield': 35,
            'helmet': 25,
            'boots': 20,
            'gloves': 20,
            'tool': 30,
        }
        
        # Rarity multipliers
        self.rarity_multipliers = {
            'common': 1.0,
            'uncommon': 2.0,
            'rare': 4.0,
            'epic': 8.0,
            'legendary': 16.0,
        }
        
        # Condition multipliers (based on durability)
        self.condition_tiers = [
            (0.0, 0.1, "Broken"),      # 0-10% = 10% value
            (0.1, 0.3, "Damaged"),     # 10-30% = 30% value
            (0.3, 0.6, "Worn"),        # 30-60% = 60% value
            (0.6, 0.85, "Good"),       # 60-85% = 85% value
            (0.85, 1.0, "Excellent"),  # 85-100% = 100% value
        ]
    
    def get_equipment_list(self, player) -> List[Tuple[str, any, bool, str]]:
        """Get all sellable equipment from player inventory and equipped items"""
        sellable = []
        
        # Check equipped items
        for slot_name in ['weapon', 'armor', 'helmet', 'boots', 'gloves', 'shield']:
            item = getattr(player, slot_name, None)
            if item and item is not None:
                item_type = self._get_item_type(slot_name)
                sellable.append((slot_name, item, True, item_type))
        
        # Check inventory for equipment
        for item_name, quantity in list(player.inventory.items()):
            # Check if it's equipment (has durability or is a tool)
            if self._is_sellable_equipment(item_name):
                item_type = self._get_item_type_from_name(item_name)
                sellable.append((item_name, {'name': item_name}, False, item_type))
        
        return sellable
    
    def _is_sellable_equipment(self, item_name: str) -> bool:
        """Check if an item is sellable equipment"""
        equipment_keywords = [
            'sword', 'axe', 'bow', 'staff', 'dagger', 'mace', 'spear',
            'armor', 'chainmail', 'plate', 'leather', 'robe',
            'helmet', 'helm', 'cap', 'hood',
            'boots', 'shoes', 'greaves',
            'gloves', 'gauntlets', 'bracers',
            'shield', 'buckler',
            'pickaxe', 'fishing_rod', 'fishing_pole', 'net'
        ]
        
        item_lower = item_name.lower()
        return any(keyword in item_lower for keyword in equipment_keywords)
    
    def _get_item_type(self, slot_name: str) -> str:
        """Get item type from slot name"""
        slot_map = {
            'weapon': 'weapon',
            'armor': 'armor',
            'helmet': 'helmet',
            'boots': 'boots',
            'gloves': 'gloves',
            'shield': 'shield',
        }
        return slot_map.get(slot_name, 'weapon')
    
    def _get_item_type_from_name(self, item_name: str) -> str:
        """Determine item type from name"""
        name_lower = item_name.lower()
        
        if any(w in name_lower for w in ['sword', 'axe', 'bow', 'staff', 'dagger', 'mace', 'spear']):
            return 'weapon'
        elif any(w in name_lower for w in ['armor', 'chainmail', 'plate', 'leather', 'robe']):
            return 'armor'
        elif any(w in name_lower for w in ['helmet', 'helm', 'cap', 'hood']):
            return 'helmet'
        elif any(w in name_lower for w in ['boots', 'shoes', 'greaves']):
            return 'boots'
        elif any(w in name_lower for w in ['gloves', 'gauntlets', 'bracers']):
            return 'gloves'
        elif any(w in name_lower for w in ['shield', 'buckler']):
            return 'shield'
        elif any(w in name_lower for w in ['pickaxe', 'fishing', 'net', 'rod', 'pole']):
            return 'tool'
        else:
            return 'weapon'
    
    def calculate_sell_price(self, item, item_type: str) -> int:
        """Calculate how much the blacksmith will pay for an item"""
        base = self.base_prices.get(item_type, 30)
        
        # Get rarity multiplier
        rarity = getattr(item, 'rarity', 'common').lower()
        rarity_mult = self.rarity_multipliers.get(rarity, 1.0)
        
        # Get condition multiplier (based on durability)
        condition_mult = 0.85  # Default for items without durability
        if hasattr(item, 'durability') and hasattr(item, 'max_durability'):
            if item.max_durability > 0:
                durability_pct = item.durability / item.max_durability
                for min_pct, max_pct, _ in self.condition_tiers:
                    if min_pct <= durability_pct <= max_pct:
                        condition_mult = max_pct
                        break
        
        # Calculate final price (blacksmith pays 40% of base value)
        final_price = int(base * rarity_mult * condition_mult * 0.4)
        
        return max(1, final_price)  # Minimum 1 dubloon
    
    def sell_equipment(self, player, slot_name: str, item, is_equipped: bool, price: int) -> Tuple[bool, str]:
        """Sell equipment to the blacksmith"""
        if is_equipped:
            # Unequip the item first
            if hasattr(player, slot_name):
                setattr(player, slot_name, None)
                player.dubloons += price
                logger.info(f"[BLACKSMITH SELL] Player sold equipped {item.name} for {price}g")
                return True, f"Sold {item.name} for {price}g!"
        else:
            # Remove from inventory
            item_name = item.get('name', slot_name) if isinstance(item, dict) else getattr(item, 'name', slot_name)
            if item_name in player.inventory:
                player.inventory[item_name] -= 1
                if player.inventory[item_name] <= 0:
                    del player.inventory[item_name]
                player.dubloons += price
                logger.info(f"[BLACKSMITH SELL] Player sold {item_name} for {price}g")
                return True, f"Sold {item_name} for {price}g!"
        
        return False, "Failed to sell item"


# =============================================================================
# TAVERN FOOD TRADING
# =============================================================================

class TavernFoodTrading:
    """Manages food and ingredient trading at taverns"""
    
    def __init__(self):
        # Food items that taverns buy
        self.food_items = {
            # Basic ingredients
            'wheat': 2,
            'flour': 3,
            'sugar': 4,
            'salt': 3,
            'milk': 5,
            'egg': 4,
            'butter': 6,
            'cheese': 8,
            
            # Meats
            'raw_meat': 10,
            'cooked_meat': 15,
            'raw_fish': 8,
            'cooked_fish': 12,
            'chicken': 12,
            'pork': 14,
            'beef': 16,
            
            # Produce
            'apple': 3,
            'carrot': 2,
            'potato': 2,
            'tomato': 3,
            'lettuce': 2,
            'onion': 2,
            'garlic': 3,
            'mushroom': 5,
            
            # Prepared foods
            'bread': 5,
            'pie': 12,
            'stew': 15,
            'soup': 10,
            'roast': 20,
            'cake': 18,
            
            # Beverages
            'ale': 4,
            'wine': 8,
            'mead': 10,
            'water': 1,
            'juice': 5,
        }
        
        # Tavern also sells some food at higher prices
        self.food_sell_prices = {
            'bread': 8,
            'cooked_meat': 20,
            'cooked_fish': 18,
            'stew': 25,
            'ale': 6,
            'wine': 12,
        }
    
    def get_sellable_food(self, player) -> List[Tuple[str, int, int]]:
        """Get all food items player can sell to tavern"""
        sellable = []
        
        for item_name, quantity in list(player.inventory.items()):
            if item_name.lower() in self.food_items:
                price = self.food_items[item_name.lower()]
                sellable.append((item_name, quantity, price))
        
        return sellable
    
    def get_buyable_food(self) -> List[Tuple[str, int]]:
        """Get food items player can buy from tavern"""
        buyable = []
        
        for item_name, price in self.food_sell_prices.items():
            buyable.append((item_name, price))
        
        return buyable
    
    def sell_food_to_tavern(self, player, item_name: str, quantity: int) -> Tuple[bool, str]:
        """Sell food to the tavern"""
        if item_name not in player.inventory:
            return False, "You don't have that item"
        
        available = player.inventory[item_name]
        if available < quantity:
            return False, f"You only have {available} {item_name}"
        
        price_per_item = self.food_items.get(item_name.lower(), 1)
        total_price = price_per_item * quantity
        
        # Remove items and add dubloons
        player.inventory[item_name] -= quantity
        if player.inventory[item_name] <= 0:
            del player.inventory[item_name]
        
        player.dubloons += total_price
        
        logger.info(f"[TAVERN TRADE] Player sold {quantity}x {item_name} for {total_price}g")
        return True, f"Sold {quantity}x {item_name} for {total_price}g!"
    
    def buy_food_from_tavern(self, player, item_name: str, quantity: int) -> Tuple[bool, str]:
        """Buy food from the tavern"""
        if item_name not in self.food_sell_prices:
            return False, "Tavern doesn't sell that item"
        
        price_per_item = self.food_sell_prices[item_name]
        total_cost = price_per_item * quantity
        
        if player.dubloons < total_cost:
            return False, f"Not enough dubloons! Need {total_cost}db"
        
        # Add items and subtract dubloons
        player.dubloons -= total_cost
        player.inventory[item_name] = player.inventory.get(item_name, 0) + quantity
        
        logger.info(f"[TAVERN TRADE] Player bought {quantity}x {item_name} for {total_cost}g")
        return True, f"Bought {quantity}x {item_name} for {total_cost}g!"


# =============================================================================
# MARKET PLAYER STALLS
# =============================================================================

class PlayerStall:
    """Represents a player-owned market stall"""
    
    def __init__(self, stall_id: int, location: str, rental_cost: int, size: str = "small"):
        self.stall_id = stall_id
        self.location = location  # Town name
        self.size = size  # "small", "medium", or "large"
        self.rental_cost = rental_cost  # Daily rental cost
        self.is_rented = False
        self.owner = None
        self.items_for_sale = {}  # {item_name: (quantity, price_per_unit)}
        self.days_remaining = 0
        self.total_sales = 0
        self.total_revenue = 0
    
    def rent(self, player_name: str, days: int) -> Tuple[bool, str]:
        """Rent the stall for a number of days"""
        if self.is_rented:
            return False, f"Stall already rented by {self.owner}"
        
        self.is_rented = True
        self.owner = player_name
        self.days_remaining = days
        logger.info(f"[MARKET STALL] {player_name} rented stall {self.stall_id} for {days} days")
        return True, f"Rented stall for {days} days!"
    
    def add_item(self, item_name: str, quantity: int, price_per_unit: int) -> Tuple[bool, str]:
        """Add an item to the stall for sale"""
        if not self.is_rented:
            return False, "Stall not rented"
        
        if item_name in self.items_for_sale:
            current_qty, current_price = self.items_for_sale[item_name]
            self.items_for_sale[item_name] = (current_qty + quantity, price_per_unit)
        else:
            self.items_for_sale[item_name] = (quantity, price_per_unit)
        
        logger.info(f"[MARKET STALL] Added {quantity}x {item_name} at {price_per_unit}g each")
        return True, f"Listed {quantity}x {item_name} for {price_per_unit}g each"
    
    def remove_item(self, item_name: str, quantity: int) -> Tuple[bool, str, int]:
        """Remove an item from the stall"""
        if item_name not in self.items_for_sale:
            return False, "Item not in stall", 0
        
        current_qty, price = self.items_for_sale[item_name]
        removed = min(quantity, current_qty)
        
        if removed >= current_qty:
            del self.items_for_sale[item_name]
        else:
            self.items_for_sale[item_name] = (current_qty - removed, price)
        
        return True, f"Removed {removed}x {item_name}", removed
    
    def simulate_sales(self) -> int:
        """Simulate NPC purchases (called daily)"""
        if not self.is_rented or not self.items_for_sale:
            return 0
        
        import random
        revenue = 0
        items_sold = []
        
        # Each item has a chance to sell based on price
        for item_name, (quantity, price) in list(self.items_for_sale.items()):
            # Lower prices = higher sell chance
            sell_chance = max(0.1, min(0.5, 1.0 / (price / 10 + 1)))
            
            if random.random() < sell_chance:
                sold = random.randint(1, max(1, quantity // 2))
                sold = min(sold, quantity)
                
                revenue += sold * price
                self.total_sales += sold
                items_sold.append((item_name, sold))
                
                remaining = quantity - sold
                if remaining <= 0:
                    del self.items_for_sale[item_name]
                else:
                    self.items_for_sale[item_name] = (remaining, price)
        
        self.total_revenue += revenue
        
        if items_sold:
            logger.info(f"[MARKET STALL] Daily sales: {items_sold}, Revenue: {revenue}g")
        
        return revenue
    
    def daily_update(self):
        """Update stall status (called daily)"""
        if self.is_rented:
            self.days_remaining -= 1
            if self.days_remaining <= 0:
                self.is_rented = False
                self.owner = None
                self.items_for_sale.clear()
                logger.info(f"[MARKET STALL] Stall {self.stall_id} rental expired")


class MarketStallSystem:
    """Manages all player stalls in markets"""
    
    def __init__(self):
        self.stalls = {}  # {town_name: [PlayerStall, ...]}
        self.rental_costs = {
            'small': 10,   # 10g per day
            'medium': 20,  # 20g per day
            'large': 35,   # 35g per day
        }
    
    def initialize_stalls(self, town_name: str, count: int = 5):
        """Create stalls for a town"""
        if town_name not in self.stalls:
            self.stalls[town_name] = []
            
            for i in range(count):
                stall_type = 'small' if i < 2 else 'medium' if i < 4 else 'large'
                rental_cost = self.rental_costs[stall_type]
                stall = PlayerStall(i, town_name, rental_cost, stall_type)
                self.stalls[town_name].append(stall)
            
            logger.info(f"[MARKET STALL] Initialized {count} stalls in {town_name}")
    
    def get_stalls(self, town_name: str) -> List[PlayerStall]:
        """Get all stalls in a town"""
        if town_name not in self.stalls:
            self.initialize_stalls(town_name)
        return self.stalls[town_name]
    
    def get_player_stall(self, town_name: str, player_name: str) -> Optional[PlayerStall]:
        """Get the stall owned by a player in a town"""
        stalls = self.get_stalls(town_name)
        for stall in stalls:
            if stall.is_rented and stall.owner == player_name:
                return stall
        return None
    
    def daily_update_all(self):
        """Update all stalls (called daily)"""
        for town_stalls in self.stalls.values():
            for stall in town_stalls:
                revenue = stall.simulate_sales()
                stall.daily_update()


# =============================================================================
# BANK SAFETY DEPOSIT BOXES
# =============================================================================

class SafetyDepositBox:
    """A safety deposit box for secure item storage"""
    
    def __init__(self, box_id: int, size: str, rental_cost: int, slots: int):
        self.box_id = box_id
        self.size = size  # 'small', 'medium', 'large'
        self.rental_cost = rental_cost  # Per rental period
        self.slots = slots
        self.is_rented = False
        self.owner = None
        self.items = {}  # {item_name: quantity}
        self.days_remaining = 0
    
    def rent(self, player_name: str, days: int) -> Tuple[bool, str]:
        """Rent the safety deposit box"""
        if self.is_rented:
            return False, f"Box already rented"
        
        self.is_rented = True
        self.owner = player_name
        self.days_remaining = days
        logger.info(f"[SAFETY DEPOSIT] {player_name} rented box {self.box_id} for {days} days")
        return True, f"Rented safety deposit box for {days} days!"
    
    def deposit_item(self, item_name: str, quantity: int) -> Tuple[bool, str]:
        """Deposit an item into the box"""
        if not self.is_rented:
            return False, "Box not rented"
        
        current_items = len(self.items)
        if current_items >= self.slots and item_name not in self.items:
            return False, f"Box full ({self.slots} slots)"
        
        self.items[item_name] = self.items.get(item_name, 0) + quantity
        logger.info(f"[SAFETY DEPOSIT] Deposited {quantity}x {item_name}")
        return True, f"Deposited {quantity}x {item_name}"
    
    def withdraw_item(self, item_name: str, quantity: int) -> Tuple[bool, str, int]:
        """Withdraw an item from the box"""
        if not self.is_rented:
            return False, "Box not rented", 0
        
        if item_name not in self.items:
            return False, "Item not in box", 0
        
        available = self.items[item_name]
        withdrawn = min(quantity, available)
        
        self.items[item_name] -= withdrawn
        if self.items[item_name] <= 0:
            del self.items[item_name]
        
        logger.info(f"[SAFETY DEPOSIT] Withdrew {withdrawn}x {item_name}")
        return True, f"Withdrew {withdrawn}x {item_name}", withdrawn
    
    def daily_update(self):
        """Update box status (called daily)"""
        if self.is_rented:
            self.days_remaining -= 1
            if self.days_remaining <= 0:
                # Box expires - items are held for 7 grace days
                logger.warning(f"[SAFETY DEPOSIT] Box {self.box_id} rental expired (grace period)")


class SafetyDepositSystem:
    """Manages all safety deposit boxes in banks"""
    
    def __init__(self):
        self.boxes = {}  # {bank_location: [SafetyDepositBox, ...]}
        self.box_sizes = {
            'small': {'slots': 5, 'cost': 50},
            'medium': {'slots': 15, 'cost': 150},
            'large': {'slots': 30, 'cost': 350},
        }
    
    def initialize_boxes(self, bank_location: str, count_per_size: int = 3):
        """Create safety deposit boxes for a bank"""
        if bank_location not in self.boxes:
            self.boxes[bank_location] = []
            
            box_id = 0
            for size, config in self.box_sizes.items():
                for _ in range(count_per_size):
                    box = SafetyDepositBox(
                        box_id,
                        size,
                        config['cost'],
                        config['slots']
                    )
                    self.boxes[bank_location].append(box)
                    box_id += 1
            
            logger.info(f"[SAFETY DEPOSIT] Initialized {len(self.boxes[bank_location])} boxes in {bank_location}")
    
    def get_boxes(self, bank_location: str) -> List[SafetyDepositBox]:
        """Get all boxes at a bank"""
        if bank_location not in self.boxes:
            self.initialize_boxes(bank_location)
        return self.boxes[bank_location]
    
    def get_player_box(self, bank_location: str, player_name: str) -> Optional[SafetyDepositBox]:
        """Get the box owned by a player at a bank"""
        boxes = self.get_boxes(bank_location)
        for box in boxes:
            if box.is_rented and box.owner == player_name:
                return box
        return None
    
    def get_available_boxes(self, bank_location: str) -> List[SafetyDepositBox]:
        """Get all available (unrented) boxes"""
        boxes = self.get_boxes(bank_location)
        return [box for box in boxes if not box.is_rented]
    
    def daily_update_all(self):
        """Update all boxes (called daily)"""
        for bank_boxes in self.boxes.values():
            for box in bank_boxes:
                box.daily_update()
