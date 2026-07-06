from utils import ITEM_WEIGHTS, item_weight, inventory_weight


# Inventory component for the player
class Inventory:
    def __init__(self):
        # Will hold inventory items
        self.items = {}
        # Maximum weight the player can carry
        self.max_weight = 100
        # Current weight being carried
        self.current_weight = 0
        
    def inter_items(self):
        return self.items.items()
        
    def get(self, item, default=0):
        """Allow dict-like access to inventory items."""
        return self.items.get(item, default)
        
    def add_item(self, item_id, quantity=1):
        """
        Add an item to the inventory
        
        Args:
            item_id (str): ID of the item to add
            quantity (int): Amount to add (default 1)
        
        Returns:
            bool: True if item was added successfully
        """
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
            
        # Update weight
        item_weight = ITEM_WEIGHTS.get(item_id, 2) * quantity
        self.current_weight += item_weight
        
        return True
    
    def remove_item(self, item_id, quantity=1):
        """
        Remove an item from the inventory
        
        Args:
            item_id (str): ID of the item to remove
            quantity (int): Amount to remove (default 1)
        
        Returns:
            bool: True if item was removed successfully
        """
        if item_id not in self.items:
            return False
            
        if self.items[item_id] < quantity:
            return False
            
        self.items[item_id] -= quantity
        if self.items[item_id] <= 0:
            del self.items[item_id]
        
        # Update weight
        item_weight = ITEM_WEIGHTS.get(item_id, 2) * quantity
        self.current_weight -= item_weight
        
        return True
    
    def has_item(self, item_id, quantity=1):
        """
        Check if the inventory has a specific item
        
        Args:
            item_id (str): ID of the item to check
            quantity (int): Minimum quantity required
        
        Returns:
            bool: True if inventory has the required quantity
        """
        return item_id in self.items and self.items[item_id] >= quantity
        
    def get_item_count(self, item_id):
        """
        Get the quantity of a specific item
        
        Args:
            item_id (str): ID of the item to check
            
        Returns:
            int: Quantity of the item (0 if not present)
        """
        return self.items.get(item_id, 0)
    
    