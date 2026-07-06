"""
Shop Ownership System
Buy, operate, and upgrade your own shops
"""

import logging
import random
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ShopUpgrade:
    """Represents an upgrade for a player-owned shop"""
    
    UPGRADES = {
        'larger_inventory': {
            'name': 'Larger Inventory',
            'description': 'Increase stock capacity by 50%',
            'cost': 2000,
            'effect': {'inventory_mult': 1.5}
        },
        'better_location': {
            'name': 'Better Location',
            'description': 'Attract 30% more customers',
            'cost': 3000,
            'effect': {'customer_mult': 1.3}
        },
        'hire_salesperson': {
            'name': 'Hire Salesperson',
            'description': 'Shop operates when you\'re away',
            'cost': 1500,
            'effect': {'auto_sell': True}
        },
        'security_system': {
            'name': 'Security System',
            'description': 'Reduce theft by 80%',
            'cost': 2500,
            'effect': {'theft_reduction': 0.8}
        },
        'advertising': {
            'name': 'Advertising Campaign',
            'description': 'Double customer traffic for 7 days',
            'cost': 1000,
            'effect': {'customer_mult': 2.0, 'duration': 7}
        },
        'premium_display': {
            'name': 'Premium Display',
            'description': 'Increase prices by 10% without losing customers',
            'cost': 1800,
            'effect': {'price_mult': 1.1}
        },
        'warehouse': {
            'name': 'Warehouse Storage',
            'description': 'Store 100 extra items',
            'cost': 5000,
            'effect': {'storage': 100}
        },
        'apprentice': {
            'name': 'Hire Apprentice',
            'description': 'Reduces restock costs by 25%',
            'cost': 2000,
            'effect': {'restock_discount': 0.25}
        }
    }


class PlayerOwnedShop:
    """A shop owned and operated by the player"""
    
    def __init__(self, shop_id: str, shop_name: str, location: str, purchase_price: int):
        self.shop_id = shop_id
        self.shop_name = shop_name
        self.location = location  # Town name
        self.purchase_price = purchase_price
        self.purchase_day = 0
        
        # Inventory
        self.inventory = []
        self.max_inventory_size = 20
        self.storage = []  # Warehouse storage
        self.max_storage = 0
        
        # Financial
        self.daily_revenue = 0
        self.daily_expenses = 0
        self.total_profit = 0
        self.maintenance_cost = 50  # Daily maintenance
        
        # Staff
        self.has_salesperson = False
        self.has_apprentice = False
        self.staff_wages = 0
        
        # Upgrades
        self.upgrades: List[str] = []
        self.active_effects: Dict[str, any] = {}
        
        # Customer data
        self.customer_multiplier = 1.0
        self.price_multiplier = 1.0
        self.theft_reduction = 0.0
        
        # Statistics
        self.items_sold = 0
        self.customers_served = 0
        self.days_owned = 0
    
    def add_upgrade(self, upgrade_id: str):
        """Add an upgrade to the shop"""
        if upgrade_id not in ShopUpgrade.UPGRADES:
            return False
        
        if upgrade_id in self.upgrades:
            return False  # Already has upgrade
        
        self.upgrades.append(upgrade_id)
        upgrade = ShopUpgrade.UPGRADES[upgrade_id]
        
        # Apply effects
        effects = upgrade['effect']
        
        if 'inventory_mult' in effects:
            self.max_inventory_size = int(self.max_inventory_size * effects['inventory_mult'])
        
        if 'customer_mult' in effects:
            self.customer_multiplier *= effects['customer_mult']
        
        if 'auto_sell' in effects:
            self.has_salesperson = True
            self.staff_wages += 30  # Daily wage
        
        if 'theft_reduction' in effects:
            self.theft_reduction = effects['theft_reduction']
        
        if 'price_mult' in effects:
            self.price_multiplier *= effects['price_mult']
        
        if 'storage' in effects:
            self.max_storage += effects['storage']
        
        if 'restock_discount' in effects:
            self.has_apprentice = True
            self.staff_wages += 20
        
        logger.info(f"[SHOP OWNERSHIP] Added upgrade {upgrade_id} to {self.shop_name}")
        return True
    
    def stock_item(self, item, quantity: int, player):
        """Add items to shop inventory from player inventory"""
        if len(self.inventory) >= self.max_inventory_size:
            return False, "Inventory full! Upgrade or sell items first."
        
        # Check if player has items
        if item.item_id not in player.inventory or player.inventory[item.item_id] < quantity:
            return False, "You don't have enough items"
        
        # Transfer from player to shop
        player.inventory[item.item_id] -= quantity
        if player.inventory[item.item_id] <= 0:
            del player.inventory[item.item_id]
        
        # Add to shop
        # Find existing item or add new
        found = False
        for shop_item in self.inventory:
            if shop_item.item_id == item.item_id:
                shop_item.stock += quantity
                found = True
                break
        
        if not found:
            self.inventory.append(item)
        
        return True, f"Stocked {quantity}x {item.name}"
    
    def simulate_daily_sales(self, current_day: int) -> int:
        """Simulate a day of sales when player isn't managing shop"""
        if not self.has_salesperson:
            return 0  # No sales without staff
        
        revenue = 0
        base_customers = random.randint(5, 15)
        actual_customers = int(base_customers * self.customer_multiplier)
        
        for _ in range(actual_customers):
            if not self.inventory:
                break
            
            # Random customer buys random item
            item = random.choice(self.inventory)
            if item.stock > 0:
                price = int(item.buy_price * self.price_multiplier)
                revenue += price
                item.stock -= 1
                self.items_sold += 1
                self.customers_served += 1
        
        # Deduct expenses
        expenses = self.maintenance_cost + self.staff_wages
        
        # Random theft chance
        if random.random() > self.theft_reduction:
            theft_loss = random.randint(10, 100)
            expenses += theft_loss
        
        self.daily_revenue = revenue
        self.daily_expenses = expenses
        daily_profit = revenue - expenses
        self.total_profit += daily_profit
        self.days_owned += 1
        
        return daily_profit
    
    def get_value(self) -> int:
        """Calculate current shop value for resale"""
        base_value = self.purchase_price
        upgrade_value = sum(ShopUpgrade.UPGRADES[u]['cost'] for u in self.upgrades)
        profit_value = max(0, self.total_profit // 2)  # Half of profits add to value
        
        return base_value + upgrade_value + profit_value
    
    def get_status_report(self) -> str:
        """Get detailed shop status"""
        report = f"=== {self.shop_name} ({self.location}) ===\n\n"
        report += f"Days Owned: {self.days_owned}\n"
        report += f"Total Profit: {self.total_profit}g\n"
        report += f"Last Daily Revenue: {self.daily_revenue}g\n"
        report += f"Last Daily Expenses: {self.daily_expenses}g\n\n"
        report += f"Inventory: {len(self.inventory)}/{self.max_inventory_size}\n"
        report += f"Items Sold: {self.items_sold}\n"
        report += f"Customers Served: {self.customers_served}\n\n"
        
        if self.upgrades:
            report += "Upgrades:\n"
            for upgrade_id in self.upgrades:
                upgrade = ShopUpgrade.UPGRADES[upgrade_id]
                report += f"  - {upgrade['name']}\n"
        
        return report
    
    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'shop_id': self.shop_id,
            'shop_name': self.shop_name,
            'location': self.location,
            'purchase_price': self.purchase_price,
            'purchase_day': self.purchase_day,
            'upgrades': self.upgrades,
            'total_profit': self.total_profit,
            'days_owned': self.days_owned,
            'items_sold': self.items_sold,
            'customers_served': self.customers_served,
            'max_inventory_size': self.max_inventory_size,
            'max_storage': self.max_storage,
            'has_salesperson': self.has_salesperson,
            'has_apprentice': self.has_apprentice,
            'customer_multiplier': self.customer_multiplier,
            'price_multiplier': self.price_multiplier,
            'theft_reduction': self.theft_reduction
        }


class ShopOwnershipManager:
    """Manages player-owned shops"""
    
    def __init__(self):
        self.player_shops: Dict[str, PlayerOwnedShop] = {}
        self.available_for_sale: Dict[str, int] = {}  # shop_id -> price
        
    def list_shop_for_sale(self, shop_id: str, town: str, price: int):
        """Make a shop available for purchase"""
        self.available_for_sale[shop_id] = {
            'town': town,
            'price': price,
            'type': random.choice(['general', 'weaponsmith', 'armorer', 'alchemist'])
        }
    
    def purchase_shop(self, shop_id: str, player, current_day: int) -> Tuple[bool, str]:
        """Player purchases a shop"""
        if shop_id not in self.available_for_sale:
            return False, "Shop not available"
        
        shop_info = self.available_for_sale[shop_id]
        price = shop_info['price']
        
        if player.dubloons < price:
            return False, f"Not enough dubloons! Need {price}db, have {player.dubloons}db"
        
        # Purchase shop
        player.dubloons -= price
        
        shop_name = f"Player's {shop_info['type'].title()} Shop"
        owned_shop = PlayerOwnedShop(shop_id, shop_name, shop_info['town'], price)
        owned_shop.purchase_day = current_day
        
        self.player_shops[shop_id] = owned_shop
        del self.available_for_sale[shop_id]
        
        logger.info(f"[SHOP OWNERSHIP] Player purchased {shop_id} for {price}g")
        return True, f"Purchased {shop_name} in {shop_info['town']} for {price}g!"
    
    def sell_shop(self, shop_id: str, player) -> Tuple[bool, str, int]:
        """Player sells owned shop"""
        if shop_id not in self.player_shops:
            return False, "You don't own this shop", 0
        
        shop = self.player_shops[shop_id]
        sale_value = shop.get_value()
        
        # Return items in inventory to player
        for item in shop.inventory:
            if item.stock > 0:
                player.inventory[item.item_id] = player.inventory.get(item.item_id, 0) + item.stock
        
        # Give player gold
        player.dubloons += sale_value
        
        # Remove shop
        del self.player_shops[shop_id]
        
        logger.info(f"[SHOP OWNERSHIP] Player sold {shop_id} for {sale_value}g")
        return True, f"Sold {shop.shop_name} for {sale_value}g", sale_value
    
    def purchase_upgrade(self, shop_id: str, upgrade_id: str, player) -> Tuple[bool, str]:
        """Purchase an upgrade for a shop"""
        if shop_id not in self.player_shops:
            return False, "You don't own this shop"
        
        if upgrade_id not in ShopUpgrade.UPGRADES:
            return False, "Invalid upgrade"
        
        shop = self.player_shops[shop_id]
        upgrade = ShopUpgrade.UPGRADES[upgrade_id]
        cost = upgrade['cost']
        
        if upgrade_id in shop.upgrades:
            return False, "Already have this upgrade"
        
        if player.dubloons < cost:
            return False, f"Not enough dubloons! Need {cost}db"
        
        # Purchase upgrade
        player.dubloons -= cost
        shop.add_upgrade(upgrade_id)
        
        return True, f"Purchased {upgrade['name']} for {cost}g!"
    
    def daily_update(self, current_day: int):
        """Update all player shops daily"""
        for shop in self.player_shops.values():
            profit = shop.simulate_daily_sales(current_day)
            logger.info(f"[SHOP OWNERSHIP] {shop.shop_name} earned {profit}g profit today")
    
    def get_total_daily_income(self) -> int:
        """Get total income from all shops"""
        total = 0
        for shop in self.player_shops.values():
            total += (shop.daily_revenue - shop.daily_expenses)
        return total
    
    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'player_shops': {sid: shop.to_dict() for sid, shop in self.player_shops.items()},
            'available_for_sale': self.available_for_sale
        }
    
    def from_dict(self, data: dict):
        """Load from save data"""
        self.available_for_sale = data.get('available_for_sale', {})
        # Would need to reconstruct PlayerOwnedShop objects
