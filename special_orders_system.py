"""
Special Orders and Commissions System
Allows players to request custom items with deposits and wait times
"""

import logging
import random
from typing import Dict, List, Optional, Tuple
from shop_system import ShopItem, ShopCategory

logger = logging.getLogger(__name__)


class SpecialOrder:
    """Represents a special order request"""
    
    def __init__(self, order_id: str, merchant_id: str, merchant_name: str, 
                 item_id: str, item_name: str, quantity: int, total_price: int,
                 deposit: int, delivery_day: int):
        self.order_id = order_id
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name
        self.item_id = item_id
        self.item_name = item_name
        self.quantity = quantity
        self.total_price = total_price
        self.deposit = deposit
        self.remaining_payment = total_price - deposit
        self.delivery_day = delivery_day
        self.is_ready = False
        self.is_collected = False
        self.order_date = 0  # Set when order is placed
    
    def check_ready(self, current_day: int):
        """Check if order is ready for pickup"""
        if not self.is_ready and current_day >= self.delivery_day:
            self.is_ready = True
            logger.info(f"[SPECIAL ORDER] Order {self.order_id} is now ready!")
    
    def days_until_ready(self, current_day: int) -> int:
        """Get days remaining until ready"""
        return max(0, self.delivery_day - current_day)
    
    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'order_id': self.order_id,
            'merchant_id': self.merchant_id,
            'merchant_name': self.merchant_name,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'deposit': self.deposit,
            'remaining_payment': self.remaining_payment,
            'delivery_day': self.delivery_day,
            'is_ready': self.is_ready,
            'is_collected': self.is_collected,
            'order_date': self.order_date
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'SpecialOrder':
        """Load from dictionary"""
        order = SpecialOrder(
            data['order_id'],
            data['merchant_id'],
            data['merchant_name'],
            data['item_id'],
            data['item_name'],
            data['quantity'],
            data['total_price'],
            data['deposit'],
            data['delivery_day']
        )
        order.remaining_payment = data['remaining_payment']
        order.is_ready = data['is_ready']
        order.is_collected = data['is_collected']
        order.order_date = data['order_date']
        return order


class CustomCraftingRequest:
    """Represents a custom equipment crafting request"""
    
    def __init__(self, request_id: str, blacksmith_id: str, blacksmith_name: str,
                 item_type: str, custom_name: str, base_stats: dict, 
                 enhancement_level: int, total_price: int, deposit: int, delivery_day: int):
        self.request_id = request_id
        self.blacksmith_id = blacksmith_id
        self.blacksmith_name = blacksmith_name
        self.item_type = item_type  # "weapon", "armor", etc.
        self.custom_name = custom_name
        self.base_stats = base_stats
        self.enhancement_level = enhancement_level
        self.total_price = total_price
        self.deposit = deposit
        self.remaining_payment = total_price - deposit
        self.delivery_day = delivery_day
        self.is_ready = False
        self.is_collected = False
    
    def check_ready(self, current_day: int):
        """Check if crafting is complete"""
        if not self.is_ready and current_day >= self.delivery_day:
            self.is_ready = True
            logger.info(f"[CUSTOM CRAFT] {self.custom_name} is ready!")
    
    def days_until_ready(self, current_day: int) -> int:
        """Days until completion"""
        return max(0, self.delivery_day - current_day)
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'request_id': self.request_id,
            'blacksmith_id': self.blacksmith_id,
            'blacksmith_name': self.blacksmith_name,
            'item_type': self.item_type,
            'custom_name': self.custom_name,
            'base_stats': self.base_stats,
            'enhancement_level': self.enhancement_level,
            'total_price': self.total_price,
            'deposit': self.deposit,
            'remaining_payment': self.remaining_payment,
            'delivery_day': self.delivery_day,
            'is_ready': self.is_ready,
            'is_collected': self.is_collected
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'CustomCraftingRequest':
        """Load from dictionary"""
        request = CustomCraftingRequest(
            data['request_id'],
            data['blacksmith_id'],
            data['blacksmith_name'],
            data['item_type'],
            data['custom_name'],
            data['base_stats'],
            data['enhancement_level'],
            data['total_price'],
            data['deposit'],
            data['delivery_day']
        )
        request.remaining_payment = data['remaining_payment']
        request.is_ready = data['is_ready']
        request.is_collected = data['is_collected']
        return request


class SpecialOrderManager:
    """Manages all special orders and commissions"""
    
    def __init__(self):
        self.active_orders: Dict[str, SpecialOrder] = {}  # order_id -> SpecialOrder
        self.active_crafting: Dict[str, CustomCraftingRequest] = {}  # request_id -> CustomCraftingRequest
        self.next_order_id = 1
        self.next_request_id = 1
        
        # Configuration
        self.min_deposit_percentage = 0.25  # 25% minimum deposit
        self.bulk_discount_threshold = 10  # Bulk order at 10+ items
        self.bulk_discount_rate = 0.15  # 15% discount for bulk
    
    def create_special_order(self, merchant_id: str, merchant_name: str, item: ShopItem,
                            quantity: int, current_day: int, player) -> Tuple[bool, str, Optional[SpecialOrder]]:
        """
        Create a special order for an item not in stock
        Returns: (success, message, order)
        """
        # Calculate pricing
        base_price_per_item = item.buy_price
        total_base_price = base_price_per_item * quantity
        
        # Apply bulk discount if applicable
        if quantity >= self.bulk_discount_threshold:
            discount = total_base_price * self.bulk_discount_rate
            total_price = int(total_base_price - discount)
            discount_msg = f" ({int(self.bulk_discount_rate * 100)}% bulk discount applied!)"
        else:
            total_price = total_base_price
            discount_msg = ""
        
        # Calculate deposit (25-50% based on order size)
        deposit_percentage = min(0.5, self.min_deposit_percentage + (quantity * 0.01))
        deposit = int(total_price * deposit_percentage)
        
        # Check if player can afford deposit
        if player.dubloons < deposit:
            return False, f"Cannot afford deposit of {deposit}g (have {player.dubloons}g)", None
        
        # Calculate delivery time (3-7 days, more for larger orders)
        base_days = 3
        extra_days = min(4, quantity // 5)  # +1 day per 5 items, max +4 days
        delivery_days = base_days + extra_days
        delivery_day = current_day + delivery_days
        
        # Create order
        order_id = f"ORDER_{self.next_order_id}"
        self.next_order_id += 1
        
        order = SpecialOrder(
            order_id, merchant_id, merchant_name,
            item.item_id, item.name, quantity,
            total_price, deposit, delivery_day
        )
        order.order_date = current_day
        
        # Deduct deposit
        player.dubloons -= deposit
        
        # Store order
        self.active_orders[order_id] = order
        
        success_msg = (f"Special order placed for {quantity}x {item.name}!{discount_msg}\n"
                      f"Total Price: {total_price}g | Deposit Paid: {deposit}g\n"
                      f"Remaining: {order.remaining_payment}g | Ready in {delivery_days} days")
        
        logger.info(f"[SPECIAL ORDER] Created {order_id} for {quantity}x {item.name}")
        return True, success_msg, order
    
    def create_custom_crafting(self, blacksmith_id: str, blacksmith_name: str,
                              item_type: str, custom_name: str, base_stats: dict,
                              enhancement_level: int, current_day: int, player) -> Tuple[bool, str, Optional[CustomCraftingRequest]]:
        """
        Create a custom crafting request
        Returns: (success, message, request)
        """
        # Calculate price based on item type and enhancement
        base_prices = {
            'weapon': 500,
            'armor': 600,
            'accessory': 400
        }
        
        base_price = base_prices.get(item_type, 500)
        
        # Enhancement multiplier (each level adds 50%)
        enhancement_multiplier = 1.0 + (enhancement_level * 0.5)
        total_price = int(base_price * enhancement_multiplier)
        
        # Deposit (50% for custom work)
        deposit = int(total_price * 0.5)
        
        # Check affordability
        if player.dubloons < deposit:
            return False, f"Cannot afford deposit of {deposit}g", None
        
        # Delivery time (5-10 days based on enhancement level)
        delivery_days = 5 + enhancement_level
        delivery_day = current_day + delivery_days
        
        # Create request
        request_id = f"CRAFT_{self.next_request_id}"
        self.next_request_id += 1
        
        request = CustomCraftingRequest(
            request_id, blacksmith_id, blacksmith_name,
            item_type, custom_name, base_stats,
            enhancement_level, total_price, deposit, delivery_day
        )
        
        # Deduct deposit
        player.dubloons -= deposit
        
        # Store request
        self.active_crafting[request_id] = request
        
        success_msg = (f"Custom {item_type} '{custom_name}' commissioned!\n"
                      f"Enhancement Level: +{enhancement_level}\n"
                      f"Total Price: {total_price}g | Deposit Paid: {deposit}g\n"
                      f"Ready in {delivery_days} days")
        
        logger.info(f"[CUSTOM CRAFT] Created {request_id} for {custom_name}")
        return True, success_msg, request
    
    def collect_order(self, order_id: str, player) -> Tuple[bool, str]:
        """
        Collect a completed special order
        Returns: (success, message)
        """
        if order_id not in self.active_orders:
            return False, "Order not found"
        
        order = self.active_orders[order_id]
        
        if not order.is_ready:
            days_left = order.days_until_ready(0)  # Will be negative if calculating manually
            return False, f"Order not ready yet ({abs(days_left)} days remaining)"
        
        if order.is_collected:
            return False, "Order already collected"
        
        # Check payment
        if player.dubloons < order.remaining_payment:
            return False, f"Need {order.remaining_payment}g to collect (have {player.dubloons}g)"
        
        # Complete transaction
        player.dubloons -= order.remaining_payment
        
        # Add items to inventory
        player.inventory[order.item_id] = player.inventory.get(order.item_id, 0) + order.quantity
        
        # Mark as collected
        order.is_collected = True
        
        success_msg = f"Collected {order.quantity}x {order.item_name} for {order.remaining_payment}g!"
        logger.info(f"[SPECIAL ORDER] Collected {order_id}")
        
        return True, success_msg
    
    def collect_custom_item(self, request_id: str, player) -> Tuple[bool, str]:
        """
        Collect custom crafted item
        Returns: (success, message)
        """
        if request_id not in self.active_crafting:
            return False, "Crafting request not found"
        
        request = self.active_crafting[request_id]
        
        if not request.is_ready:
            return False, f"Not ready yet ({request.days_until_ready(0)} days remaining)"
        
        if request.is_collected:
            return False, "Already collected"
        
        # Check payment
        if player.dubloons < request.remaining_payment:
            return False, f"Need {request.remaining_payment}g to collect"
        
        # Complete transaction
        player.dubloons -= request.remaining_payment
        
        # Create custom item (simplified - would need proper item creation)
        custom_item_id = f"custom_{request.item_type}_{request.request_id}"
        player.inventory[custom_item_id] = player.inventory.get(custom_item_id, 0) + 1
        
        # Mark collected
        request.is_collected = True
        
        success_msg = f"Collected custom {request.item_type} '{request.custom_name}'!"
        logger.info(f"[CUSTOM CRAFT] Collected {request_id}")
        
        return True, success_msg
    
    def update(self, current_day: int):
        """Update all orders and check for completion"""
        for order in self.active_orders.values():
            if not order.is_collected:
                order.check_ready(current_day)
        
        for request in self.active_crafting.values():
            if not request.is_collected:
                request.check_ready(current_day)
    
    def get_player_orders(self) -> List[SpecialOrder]:
        """Get all active orders for player"""
        return [order for order in self.active_orders.values() if not order.is_collected]
    
    def get_player_crafting(self) -> List[CustomCraftingRequest]:
        """Get all active crafting requests"""
        return [req for req in self.active_crafting.values() if not req.is_collected]
    
    def get_ready_orders(self) -> List[SpecialOrder]:
        """Get orders that are ready for pickup"""
        return [order for order in self.active_orders.values() 
                if order.is_ready and not order.is_collected]
    
    def get_ready_crafting(self) -> List[CustomCraftingRequest]:
        """Get crafting requests ready for pickup"""
        return [req for req in self.active_crafting.values() 
                if req.is_ready and not req.is_collected]
    
    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'active_orders': {oid: order.to_dict() for oid, order in self.active_orders.items()},
            'active_crafting': {rid: req.to_dict() for rid, req in self.active_crafting.items()},
            'next_order_id': self.next_order_id,
            'next_request_id': self.next_request_id
        }
    
    def from_dict(self, data: dict):
        """Load from save data"""
        self.active_orders = {
            oid: SpecialOrder.from_dict(order_data) 
            for oid, order_data in data.get('active_orders', {}).items()
        }
        self.active_crafting = {
            rid: CustomCraftingRequest.from_dict(req_data)
            for rid, req_data in data.get('active_crafting', {}).items()
        }
        self.next_order_id = data.get('next_order_id', 1)
        self.next_request_id = data.get('next_request_id', 1)
