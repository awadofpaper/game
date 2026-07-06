"""
Shop System - Buy and Sell Items with Merchants
"""

import pygame
import random
from enum import Enum

class ShopCategory(Enum):
    WEAPONS = "Weapons"
    ARMOR = "Armor"
    CONSUMABLES = "Consumables"
    MATERIALS = "Materials"
    MISC = "Miscellaneous"

class ShopItem:
    """An item available for purchase in a shop"""
    
    def __init__(self, item_id, name, category, buy_price, sell_price=None, 
                 stock=-1, description="", stats=None):
        self.item_id = item_id
        self.name = name
        self.category = category
        self.buy_price = buy_price  # Price to buy from merchant
        self.sell_price = sell_price or (buy_price // 2)  # Price merchant pays you
        self.stock = stock  # -1 = infinite stock
        self.description = description
        self.stats = stats or {}  # Item stats (damage, defense, etc.)
    
    def can_afford(self, player_gold):
        return player_gold >= self.buy_price
    
    def has_stock(self):
        return self.stock == -1 or self.stock > 0
    
    def purchase(self):
        """Decrease stock when purchased"""
        if self.stock > 0:
            self.stock -= 1
    
    def restock(self, amount=1):
        """Increase stock"""
        if self.stock != -1:
            self.stock += amount

class MerchantShop:
    """A merchant's shop with inventory and pricing"""
    
    def __init__(self, merchant_name, merchant_type="general"):
        self.merchant_name = merchant_name
        self.merchant_type = merchant_type  # general, weaponsmith, armorer, alchemist
        self.inventory = []
        self.reputation_discount = 0.0  # Percentage discount based on reputation
        self.restock_timer = 0
        self.restock_interval = 1  # Days between restocks
        
        # System references (set by ShopManager)
        self.shop_id = None
        self.town_name = None  # Town location (for price events)
        self.reputation_manager = None
        self.dynamic_inventory_manager = None
        self.haggling_system = None
        self.bartering_system = None
        self.special_order_manager = None
        self.price_event_manager = None
        self.merchant_quest_manager = None
        
        # Financial tracking
        self.daily_revenue = 0  # Gold earned from sales today
        self.daily_expenses = 0  # Operating costs today
        self.daily_transactions = 0  # Number of transactions today
        self.total_inventory_value = 0  # Total value of current inventory
        
        # Initialize default inventory based on merchant type
        self._initialize_inventory()
        self._calculate_inventory_value()
    
    def _initialize_inventory(self):
        """Set up starting inventory based on merchant type"""
        
        if self.merchant_type == "general":
            # General merchant - variety of items
            self.inventory = [
                # Consumables
                ShopItem("health_potion", "Health Potion", ShopCategory.CONSUMABLES, 50, 25, 10,
                        "Restores 50 HP", {"healing": 50}),
                ShopItem("mana_potion", "Mana Potion", ShopCategory.CONSUMABLES, 40, 20, 10,
                        "Restores 30 Mana", {"mana_restore": 30}),
                ShopItem("bread", "Bread", ShopCategory.CONSUMABLES, 10, 5, 20,
                        "Restores 20 HP", {"healing": 20}),
                
                # Basic weapons
                ShopItem("iron_sword", "Iron Sword", ShopCategory.WEAPONS, 150, 75, 3,
                        "A sturdy iron blade", {"damage": 15}),
                ShopItem("wooden_bow", "Wooden Bow", ShopCategory.WEAPONS, 120, 60, 2,
                        "Simple hunting bow", {"damage": 12, "range": 200}),
                
                # Basic armor
                ShopItem("leather_armor", "Leather Armor", ShopCategory.ARMOR, 200, 100, 2,
                        "Light leather protection", {"defense": 8}),
                ShopItem("iron_helmet", "Iron Helmet", ShopCategory.ARMOR, 100, 50, 2,
                        "Protects your head", {"defense": 5}),
                
                # Materials
                ShopItem("rope", "Rope", ShopCategory.MATERIALS, 15, 7, 5,
                        "Useful rope"),
                ShopItem("torch", "Torch", ShopCategory.MATERIALS, 8, 4, 15,
                        "Provides light"),
            ]
        
        elif self.merchant_type == "weaponsmith":
            # Specialized weapons merchant
            self.inventory = [
                ShopItem("iron_sword", "Iron Sword", ShopCategory.WEAPONS, 150, 75, 5,
                        "A sturdy iron blade", {"damage": 15}),
                ShopItem("steel_sword", "Steel Sword", ShopCategory.WEAPONS, 300, 150, 2,
                        "High-quality steel blade", {"damage": 25}),
                ShopItem("battle_axe", "Battle Axe", ShopCategory.WEAPONS, 250, 125, 3,
                        "Heavy two-handed axe", {"damage": 30, "speed": -0.2}),
                ShopItem("wooden_bow", "Wooden Bow", ShopCategory.WEAPONS, 120, 60, 4,
                        "Simple hunting bow", {"damage": 12}),
                ShopItem("longbow", "Longbow", ShopCategory.WEAPONS, 280, 140, 2,
                        "Powerful longbow", {"damage": 22, "range": 300}),
                ShopItem("dagger", "Dagger", ShopCategory.WEAPONS, 80, 40, 5,
                        "Quick and light", {"damage": 10, "speed": 0.3}),
            ]
        
        elif self.merchant_type == "armorer":
            # Specialized armor merchant
            self.inventory = [
                ShopItem("leather_armor", "Leather Armor", ShopCategory.ARMOR, 200, 100, 3,
                        "Light leather protection", {"defense": 8}),
                ShopItem("chainmail", "Chainmail", ShopCategory.ARMOR, 400, 200, 2,
                        "Interlocking metal rings", {"defense": 15}),
                ShopItem("plate_armor", "Plate Armor", ShopCategory.ARMOR, 800, 400, 1,
                        "Heavy plate protection", {"defense": 30, "speed": -0.15}),
                ShopItem("iron_helmet", "Iron Helmet", ShopCategory.ARMOR, 100, 50, 3,
                        "Protects your head", {"defense": 5}),
                ShopItem("iron_boots", "Iron Boots", ShopCategory.ARMOR, 80, 40, 3,
                        "Sturdy footwear", {"defense": 4}),
                ShopItem("shield", "Shield", ShopCategory.ARMOR, 150, 75, 2,
                        "Wooden shield", {"defense": 10, "block_chance": 0.15}),
            ]
        
        elif self.merchant_type == "alchemist":
            # Specialized potions and consumables
            self.inventory = [
                ShopItem("health_potion", "Health Potion", ShopCategory.CONSUMABLES, 50, 25, 15,
                        "Restores 50 HP", {"healing": 50}),
                ShopItem("greater_health_potion", "Greater Health Potion", ShopCategory.CONSUMABLES, 150, 75, 5,
                        "Restores 150 HP", {"healing": 150}),
                ShopItem("mana_potion", "Mana Potion", ShopCategory.CONSUMABLES, 40, 20, 15,
                        "Restores 30 Mana", {"mana_restore": 30}),
                ShopItem("stamina_elixir", "Stamina Elixir", ShopCategory.CONSUMABLES, 75, 35, 8,
                        "Increases stamina regen", {"stamina_boost": 20, "duration": 60}),
                ShopItem("strength_potion", "Strength Potion", ShopCategory.CONSUMABLES, 100, 50, 5,
                        "Temporarily increases damage", {"damage_boost": 1.5, "duration": 45}),
                ShopItem("poison_antidote", "Antidote", ShopCategory.CONSUMABLES, 60, 30, 10,
                        "Cures poison", {"cure": "poison"}),
            ]
    
    def get_item_price(self, item, is_buying=True, reputation_level=0):
        """Calculate actual price with discounts"""
        base_price = item.buy_price if is_buying else item.sell_price
        
        if is_buying:
            # Apply reputation discount when buying
            discount = min(0.3, reputation_level * 0.05)  # Max 30% discount
            return int(base_price * (1.0 - discount))
        else:
            # Reputation increases sell prices slightly
            bonus = min(0.2, reputation_level * 0.03)  # Max 20% bonus
            return int(base_price * (1.0 + bonus))
    
    def _calculate_operating_costs(self):
        """Calculate daily operating costs based on shop type and inventory size"""
        # Base costs by shop type
        base_costs = {
            "general": 50,      # General stores have moderate overhead
            "weaponsmith": 80,  # Forges and equipment are expensive
            "armorer": 75,      # Metal working costs
            "alchemist": 60     # Ingredient preservation costs
        }
        
        base_cost = base_costs.get(self.merchant_type, 50)
        
        # Scale with inventory size (larger shops cost more to operate)
        inventory_size = len(self.inventory)
        size_multiplier = 1.0 + (inventory_size / 20.0)  # +5% per item
        
        # Add rent/maintenance based on inventory value
        value_maintenance = int(self.total_inventory_value * 0.01)  # 1% of inventory value
        
        total_cost = int(base_cost * size_multiplier) + value_maintenance
        return total_cost
    
    def _calculate_inventory_value(self):
        """Calculate total value of current inventory"""
        total = 0
        for item in self.inventory:
            if item.stock > 0:
                total += item.buy_price * item.stock
            elif item.stock == -1:
                # Infinite stock - estimate at 10 items
                total += item.buy_price * 10
        self.total_inventory_value = total
        return total
    
    def get_financial_data(self):
        """Get shop's financial performance data"""
        return {
            'revenue': self.daily_revenue,
            'expenses': self.daily_expenses,
            'profit': self.daily_revenue - self.daily_expenses,
            'transactions': self.daily_transactions,
            'inventory_value': self.total_inventory_value
        }
    
    def can_buy_item(self, item, player_gold):
        """Check if player can buy this item"""
        price = self.get_item_price(item, is_buying=True)
        return item.has_stock() and player_gold >= price
    
    def buy_item(self, item, player):
        """Player buys item from merchant"""
        # Get reputation discount multiplier
        discount_multiplier = 1.0
        if self.reputation_manager and self.shop_id:
            rep = self.reputation_manager.get_or_create_reputation(self.shop_id, self.merchant_name)
            
            # Check if merchant will trade
            if not rep.can_trade():
                return False, f"{rep.get_greeting()}"
            
            discount_multiplier = rep.get_discount_multiplier()
        
        # Get loyalty program discount
        loyalty_discount = 0.0
        if self.merchant_quest_manager and self.shop_id:
            loyalty_discount = self.merchant_quest_manager.get_loyalty_discount(self.shop_id)
        
        # Calculate price with reputation discount and loyalty
        base_price = item.buy_price
        
        # Apply price event modifiers
        event_modifier = 1.0
        if self.price_event_manager and self.town_name and hasattr(item, 'category'):
            event_modifier = self.price_event_manager.get_price_modifier(item.category, self.town_name)
        
        # Combine all modifiers (reputation reduces, events can increase or decrease, loyalty reduces)
        price = int(base_price * discount_multiplier * event_modifier * (1.0 - loyalty_discount))
        
        # Apply racial price modifiers (Human: -15% buying)
        if hasattr(player, 'trait_manager') and player.trait_manager:
            price = player.trait_manager.apply_shop_price_modifier(price, is_buying=True)
        
        if not item.has_stock():
            return False, "Out of stock!"
        
        if player.dubloons < price:
            return False, f"Not enough dubloons! Need {price}, have {player.dubloons}"
        
        # Deduct gold
        player.dubloons -= price
        
        # Decrease stock
        item.purchase()
        
        # Track revenue
        self.daily_revenue += price
        self.daily_transactions += 1
        
        # Add item to player inventory (dict-based system)
        if not hasattr(player, 'inventory'):
            player.inventory = {}
        
        player.inventory[item.item_id] = player.inventory.get(item.item_id, 0) + 1
        
        # Record purchase for reputation (after successful transaction)
        if self.reputation_manager and self.shop_id:
            self.reputation_manager.record_purchase(self.shop_id, self.merchant_name, price)
        
        # Record sale for demand tracking
        if self.dynamic_inventory_manager and self.shop_id:
            self.dynamic_inventory_manager.record_sale(self.shop_id, item.item_id, 1)
        
        # Record purchase for loyalty program
        if self.merchant_quest_manager and self.shop_id:
            self.merchant_quest_manager.record_purchase(self.shop_id, price)
        
        return True, f"Purchased {item.name} for {price} gold!"
    
    def sell_item_to_merchant(self, item_id, player, embargo_system=None, town_treasury_system=None, town_name=None):
        """Player sells item to merchant"""
        # Check if merchant will trade
        if self.reputation_manager and self.shop_id:
            rep = self.reputation_manager.get_or_create_reputation(self.shop_id, self.merchant_name)
            if not rep.can_trade():
                return False, f"{rep.get_greeting()}"
        
        # Find item in shop inventory to get sell price
        shop_item = None
        for item in self.inventory:
            if item.item_id == item_id:
                shop_item = item
                break
        
        if not shop_item:
            # If item not in shop, offer 50% of estimated value
            return False, "I don't buy that type of item."
        
        # Get reputation multiplier for better sell prices
        sell_multiplier = 1.0
        if self.reputation_manager and self.shop_id:
            rep = self.reputation_manager.get_or_create_reputation(self.shop_id, self.merchant_name)
            # Higher reputation gives better sell prices (inverse of buy discount)
            # At max discount (0.75 buy multiplier), get 1.25 sell multiplier
            buy_multiplier = rep.get_discount_multiplier()
            sell_multiplier = 2.0 - buy_multiplier  # If buy is 0.75, sell is 1.25
        
        sell_price = int(shop_item.sell_price * sell_multiplier)
        
        # Apply racial price modifiers (Human: +15% selling)
        if hasattr(player, 'trait_manager') and player.trait_manager:
            sell_price = player.trait_manager.apply_shop_price_modifier(sell_price, is_buying=False)
        
        # Check if player has the item (dict-based inventory)
        if not hasattr(player, 'inventory'):
            player.inventory = {}
        
        item_count = player.inventory.get(item_id, 0)
        if item_count <= 0:
            return False, "You don't have that item!"
        
        # Check for embargo fee (30% if active)
        embargo_fee = 0
        if embargo_system and embargo_system.embargo_active:
            embargo_fee = embargo_system.apply_embargo_fee(sell_price)
            sell_price -= embargo_fee
            
            # Deposit fee to town treasury
            if town_treasury_system and town_name:
                town_treasury_system.deposit(town_name, embargo_fee, 'embargo_fee')
        
        # Remove from player inventory
        player.inventory[item_id] = item_count - 1
        if player.inventory[item_id] <= 0:
            del player.inventory[item_id]
        
        # Give gold to player
        player.dubloons += sell_price
        
        # Track as expense (shop buying from player)
        self.daily_expenses += sell_price
        self.daily_transactions += 1
        
        # Restock the item
        shop_item.restock(1)
        
        # Record sale for reputation (after successful transaction)
        if self.reputation_manager and self.shop_id:
            self.reputation_manager.record_sale(self.shop_id, self.merchant_name, sell_price)
        
        if embargo_fee > 0:
            return True, f"Sold {shop_item.name} for {sell_price}g (Embargo fee: {embargo_fee}g)"
        else:
            return True, f"Sold {shop_item.name} for {sell_price} gold!"
    
    def restock(self):
        """Restock items (called daily) with dynamic inventory features"""
        # Reset daily financial tracking
        self.daily_revenue = 0
        self.daily_expenses = 0
        self.daily_transactions = 0
        
        for item in self.inventory:
            if item.stock > 0:
                # Base restock 1-3 items
                base_restock_qty = random.randint(1, 3)
                
                # Apply dynamic inventory multipliers if available
                if self.dynamic_inventory_manager and self.shop_id:
                    restock_qty = self.dynamic_inventory_manager.get_restock_quantity(
                        self.shop_id, item, base_restock_qty
                    )
                else:
                    restock_qty = base_restock_qty
                
                item.restock(restock_qty)
                # Track restocking costs as expenses
                self.daily_expenses += int(item.buy_price * 0.3 * restock_qty)  # 30% of buy price
                
            elif item.stock == 0:
                # Fully out of stock - restock to half capacity
                base_restock_qty = random.randint(1, 5)
                
                # Apply dynamic inventory multipliers
                if self.dynamic_inventory_manager and self.shop_id:
                    restock_qty = self.dynamic_inventory_manager.get_restock_quantity(
                        self.shop_id, item, base_restock_qty
                    )
                else:
                    restock_qty = base_restock_qty
                
                item.stock = restock_qty
                self.daily_expenses += int(item.buy_price * 0.3 * restock_qty)
        
        # Check for rare item appearance (5% chance or higher for specialized towns)
        if self.dynamic_inventory_manager and self.shop_id:
            rare_item = self.dynamic_inventory_manager.should_stock_rare_item(self.shop_id)
            if rare_item:
                # Add rare item to inventory (if not already present)
                if not any(item.item_id == rare_item.item_id for item in self.inventory):
                    self.inventory.append(rare_item)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"[SHOP] {self.merchant_name} now has rare item: {rare_item.name}!")
        
        # Add base operating costs
        self.daily_expenses += self._calculate_operating_costs()
        self._calculate_inventory_value()


class ShopManager:
    """Manages all shops in the game"""
    
    def __init__(self):
        self.shops = {}  # {shop_id: {'shop': MerchantShop, 'building': Building, 'position': (x, y)}}
        self.last_restock_day = 0
        
        # System references (set by main.py)
        self.embargo_system = None
        self.town_treasury_system = None
        self.reputation_manager = None  # MerchantReputationManager
        self.dynamic_inventory = None  # DynamicInventoryManager
        self.haggling_system = None  # HagglingSystem
        self.bartering_system = None  # BarteringSystem
        self.special_order_manager = None  # SpecialOrderManager
        self.price_event_manager = None  # PriceEventManager
        self.merchant_quest_manager = None  # MerchantQuestManager
    
    def register_shop(self, building, town_name):
        """Register a shop building"""
        shop_id = f"{town_name}_{building.name}"
        shop_name = building.name
        
        # Determine shop type based on town or random
        import random
        shop_types = ["general", "weaponsmith", "armorer", "alchemist"]
        weights = [50, 20, 20, 10]  # General shops are most common
        merchant_type = random.choices(shop_types, weights=weights)[0]
        
        shop = MerchantShop(shop_name, merchant_type)
        shop.shop_id = shop_id  # Set shop ID for reputation tracking
        shop.town_name = town_name  # Set town for price events
        
        # Connect all systems to the shop
        shop.reputation_manager = self.reputation_manager
        shop.dynamic_inventory_manager = self.dynamic_inventory
        shop.haggling_system = self.haggling_system
        shop.bartering_system = self.bartering_system
        shop.special_order_manager = self.special_order_manager
        shop.price_event_manager = self.price_event_manager
        shop.merchant_quest_manager = self.merchant_quest_manager
        
        self.shops[shop_id] = {
            'shop': shop,
            'building': building,
            'position': (building.door_x, building.door_y),
            'town_name': town_name
        }
        return shop
    
    def create_shop(self, npc_id, merchant_name, merchant_type="general"):
        """Create a new shop for an NPC (legacy support)"""
        shop = MerchantShop(merchant_name, merchant_type)
        self.shops[npc_id] = {
            'shop': shop,
            'building': None,
            'position': (0, 0),
            'town_name': 'Unknown'
        }
        return shop
    
    def get_shop(self, shop_id):
        """Get shop by ID"""
        shop_data = self.shops.get(shop_id)
        return shop_data['shop'] if shop_data else None
    
    def get_nearby_shop(self, x, y, max_distance=80):
        """Get shop near player position"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[SHOP DEBUG] get_nearby_shop called with player at ({x}, {y}), max_distance={max_distance}")
        logger.info(f"[SHOP DEBUG] Checking {len(self.shops)} registered shops")
        
        for shop_id, shop_data in self.shops.items():
            shop_x, shop_y = shop_data['position']
            distance = ((x - shop_x) ** 2 + (y - shop_y) ** 2) ** 0.5
            logger.info(f"[SHOP DEBUG] Shop '{shop_id}' at ({shop_x}, {shop_y}), distance={distance:.2f}")
            if distance <= max_distance:
                logger.info(f"[SHOP DEBUG] Found nearby shop: {shop_id}")
                return shop_data['shop'], shop_id
        logger.warning(f"[SHOP DEBUG] No shops found within {max_distance} pixels of ({x}, {y})")
        return None, None
    
    def daily_update(self, current_day):
        """Update shops daily (restocking, orders, etc.)"""
        if current_day > self.last_restock_day:
            self.last_restock_day = current_day
            for shop_data in self.shops.values():
                shop_data['shop'].restock()
            
            # Update special orders
            if self.special_order_manager:
                self.special_order_manager.update(current_day)
            
            # Weekly updates for dynamic inventory
            if self.dynamic_inventory:
                self.dynamic_inventory.weekly_update(current_day)
