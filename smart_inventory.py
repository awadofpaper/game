"""
Smart Inventory Management System
Advanced inventory features including auto-sorting, stack merging, favorites, and intelligent organization
"""

import time
import json
from collections import defaultdict

class SmartInventoryManager:
    def __init__(self, player_inventory, player=None):
        self.inventory = player_inventory
        self.player = player  # Store player reference for selling junk, etc.
        self.auto_sort_enabled = True
        self.auto_stack_enabled = True
        self.favorites = set()  # Item IDs marked as favorites
        self.sort_mode = "type"  # "type", "rarity", "value", "name", "recent"
        self.last_sort_time = 0
        self.sort_cooldown = 1.0  # Prevent too frequent sorting
        
        # Category priorities for sorting
        self.category_priority = {
            "weapon": 1,
            "armor": 2, 
            "helmet": 2,
            "chestplate": 2,
            "leggings": 2,
            "boots": 2,
            "gloves": 2,
            "consumable": 3,
            "health_potion": 3,
            "mana_potion": 3,
            "material": 4,
            "gem": 5,
            "key": 6,
            "scroll": 7,
            "food": 8,
            "misc": 9
        }
        
        # Rarity values for sorting
        self.rarity_values = {
            "common": 1,
            "uncommon": 2,
            "rare": 3,
            "epic": 4,
            "legendary": 5,
            "set": 6,
            "artifact": 7
        }
        
        # Track recent additions for "recent" sort mode
        self.recent_items = []
        self.max_recent_items = 20
        
        # Junk item patterns (for quick sell)
        self.junk_patterns = [
            "broken_",
            "rusty_",
            "damaged_",
            "worn_",
            "cracked_"
        ]
        
    def add_item_smart(self, item_id, quantity=1, item_data=None):
        """Smart item addition with automatic stacking and sorting"""
        # Try to stack first if auto-stacking is enabled
        if self.auto_stack_enabled:
            stacked = self.try_stack_item(item_id, quantity, item_data)
            if stacked:
                self.update_recent_items(item_id)
                if self.auto_sort_enabled:
                    self.smart_sort()
                return True
        
        # Add normally if stacking fails or is disabled
        result = self.inventory.add_item(item_id, quantity, item_data)
        if result:
            self.update_recent_items(item_id)
            if self.auto_sort_enabled:
                self.smart_sort()
        return result
    
    def try_stack_item(self, item_id, quantity, item_data=None):
        """Attempt to stack item with existing items"""
        if item_id in self.inventory.items:
            current_quantity = self.inventory.items[item_id].get("quantity", 1)
            max_stack = self.get_max_stack_size(item_id)
            
            if current_quantity < max_stack:
                new_quantity = min(current_quantity + quantity, max_stack)
                added_quantity = new_quantity - current_quantity
                
                self.inventory.items[item_id]["quantity"] = new_quantity
                remaining = quantity - added_quantity
                
                if remaining > 0:
                    # Create new stack for remaining items
                    return self.inventory.add_item(f"{item_id}_stack", remaining, item_data)
                return True
        return False
    
    def get_max_stack_size(self, item_id):
        """Get maximum stack size for an item"""
        # Equipment typically doesn't stack
        if any(eq_type in item_id.lower() for eq_type in ["sword", "armor", "helmet", "boots", "gloves", "ring", "amulet"]):
            return 1
        
        # Consumables and materials can stack
        if any(cons_type in item_id.lower() for cons_type in ["potion", "scroll", "food", "material", "ore", "gem"]):
            return 99
        
        # Default stack size
        return 10
    
    def smart_sort(self, force=False):
        """Intelligent inventory sorting"""
        current_time = time.time()
        if not force and (current_time - self.last_sort_time) < self.sort_cooldown:
            return
        
        if not self.auto_sort_enabled and not force:
            return
            
        self.last_sort_time = current_time
        
        # Get all items
        items_list = list(self.inventory.items.items())
        
        # Separate favorites from regular items
        favorites_items = [(k, v) for k, v in items_list if k in self.favorites]
        regular_items = [(k, v) for k, v in items_list if k not in self.favorites]
        
        # Sort each group
        favorites_sorted = self.sort_items_by_mode(favorites_items)
        regular_sorted = self.sort_items_by_mode(regular_items)
        
        # Rebuild inventory with favorites first
        new_items = {}
        for item_id, item_data in favorites_sorted + regular_sorted:
            new_items[item_id] = item_data
            
        self.inventory.items = new_items
    
    def sort_items_by_mode(self, items_list):
        """Sort items based on current sort mode"""
        if self.sort_mode == "type":
            return sorted(items_list, key=lambda x: (
                self.category_priority.get(self.get_item_category(x[0]), 999),
                x[0]
            ))
        elif self.sort_mode == "rarity":
            return sorted(items_list, key=lambda x: (
                -self.rarity_values.get(self.get_item_rarity(x[1]), 0),
                self.category_priority.get(self.get_item_category(x[0]), 999)
            ))
        elif self.sort_mode == "value":
            return sorted(items_list, key=lambda x: (
                -self.get_item_value(x[1]),
                x[0]
            ))
        elif self.sort_mode == "name":
            return sorted(items_list, key=lambda x: x[0].lower())
        elif self.sort_mode == "recent":
            def recent_priority(item):
                try:
                    return self.recent_items.index(item[0])
                except ValueError:
                    return 999
            return sorted(items_list, key=recent_priority)
        else:
            return items_list
    
    def get_item_category(self, item_id):
        """Determine item category from ID"""
        item_lower = item_id.lower()
        
        if any(weapon in item_lower for weapon in ["sword", "axe", "staff", "wand", "bow", "dagger", "spear"]):
            return "weapon"
        elif "helmet" in item_lower:
            return "helmet"
        elif "chestplate" in item_lower or "armor" in item_lower:
            return "chestplate"
        elif "leggings" in item_lower:
            return "leggings"
        elif "boots" in item_lower:
            return "boots"
        elif "gloves" in item_lower:
            return "gloves"
        elif "potion" in item_lower:
            if "health" in item_lower:
                return "health_potion"
            elif "mana" in item_lower:
                return "mana_potion"
            return "consumable"
        elif any(mat in item_lower for mat in ["ore", "ingot", "leather", "wood", "fiber"]):
            return "material"
        elif "gem" in item_lower or any(gem in item_lower for gem in ["ruby", "emerald", "diamond", "sapphire"]):
            return "gem"
        elif "key" in item_lower:
            return "key"
        elif "scroll" in item_lower:
            return "scroll"
        elif any(food in item_lower for food in ["bread", "apple", "cheese", "meat"]):
            return "food"
        else:
            return "misc"
    
    def get_item_rarity(self, item_data):
        """Get item rarity from data"""
        if isinstance(item_data, dict):
            return item_data.get("rarity", "common")
        return "common"
    
    def get_item_value(self, item_data):
        """Get item value for sorting"""
        if isinstance(item_data, dict):
            return item_data.get("value", 0)
        return 0
    
    def update_recent_items(self, item_id):
        """Update recently added items list"""
        if item_id in self.recent_items:
            self.recent_items.remove(item_id)
        self.recent_items.insert(0, item_id)
        
        # Trim list if too long
        if len(self.recent_items) > self.max_recent_items:
            self.recent_items = self.recent_items[:self.max_recent_items]
    
    def toggle_favorite(self, item_id):
        """Toggle favorite status of an item"""
        if item_id in self.favorites:
            self.favorites.remove(item_id)
            return False
        else:
            self.favorites.add(item_id)
            return True
    
    def consolidate_stacks(self):
        """Merge partial stacks of the same item"""
        stack_groups = defaultdict(list)
        
        # Group items by base ID (removing _stack suffixes)
        for item_id, item_data in self.inventory.items.items():
            base_id = item_id.replace("_stack", "").replace("_stack2", "").replace("_stack3", "")
            if self.get_max_stack_size(base_id) > 1:
                stack_groups[base_id].append((item_id, item_data))
        
        consolidated_count = 0
        
        # Consolidate each group
        for base_id, items in stack_groups.items():
            if len(items) <= 1:
                continue
                
            total_quantity = sum(item[1].get("quantity", 1) for item in items)
            max_stack = self.get_max_stack_size(base_id)
            
            # Remove old entries
            for item_id, _ in items:
                del self.inventory.items[item_id]
            
            # Create consolidated stacks
            remaining = total_quantity
            stack_num = 0
            
            while remaining > 0:
                stack_size = min(remaining, max_stack)
                stack_id = base_id if stack_num == 0 else f"{base_id}_stack{stack_num}"
                
                # Use first item's data as template
                item_data = items[0][1].copy()
                item_data["quantity"] = stack_size
                
                self.inventory.items[stack_id] = item_data
                remaining -= stack_size
                stack_num += 1
                consolidated_count += 1
        
        return consolidated_count
    
    def identify_junk_items(self):
        """Identify items that are likely junk"""
        junk_items = []
        
        for item_id, item_data in self.inventory.items.items():
            # Skip favorites
            if item_id in self.favorites:
                continue
                
            # Check junk patterns
            if any(pattern in item_id.lower() for pattern in self.junk_patterns):
                junk_items.append(item_id)
                continue
                
            # Check low rarity + low value
            rarity = self.get_item_rarity(item_data)
            value = self.get_item_value(item_data)
            
            if rarity == "common" and value < 5:
                junk_items.append(item_id)
        
        return junk_items
    
    def quick_sell_junk(self, player=None):
        """Sell all identified junk items"""
        # Use stored player reference if not provided
        if player is None:
            player = self.player
        
        if player is None:
            return 0, 0  # Can't sell without player reference
        
        junk_items = self.identify_junk_items()
        total_value = 0
        
        for item_id in junk_items:
            item_data = self.inventory.items[item_id]
            quantity = item_data.get("quantity", 1)
            value = self.get_item_value(item_data)
            
            total_value += value * quantity
            del self.inventory.items[item_id]
        
        # Add money to player
        player.dubloons = getattr(player, 'dubloons', 0) + total_value
        
        return len(junk_items), total_value
    
    def get_inventory_stats(self):
        """Get inventory statistics"""
        stats = {
            "total_items": len(self.inventory.items),
            "favorites": len(self.favorites),
            "unique_types": len(set(self.get_item_category(item_id) for item_id in self.inventory.items.keys())),
            "total_value": sum(self.get_item_value(data) * data.get("quantity", 1) for data in self.inventory.items.values()),
            "junk_items": len(self.identify_junk_items())
        }
        
        # Count by rarity
        rarity_counts = defaultdict(int)
        for item_data in self.inventory.items.values():
            rarity = self.get_item_rarity(item_data)
            rarity_counts[rarity] += 1
        stats["by_rarity"] = dict(rarity_counts)
        
        return stats
    
    def search_items(self, query):
        """Search inventory for items matching query"""
        query = query.lower()
        matches = []
        
        for item_id, item_data in self.inventory.items.items():
            # Search in item name
            if query in item_id.lower():
                matches.append(item_id)
                continue
                
            # Search in item category
            if query in self.get_item_category(item_id):
                matches.append(item_id)
                continue
                
            # Search in rarity
            if query in self.get_item_rarity(item_data):
                matches.append(item_id)
                continue
        
        return matches
    
    def create_item_groups(self):
        """Create logical groups of items for display"""
        groups = defaultdict(list)
        
        for item_id, item_data in self.inventory.items.items():
            category = self.get_item_category(item_id)
            groups[category].append((item_id, item_data))
        
        # Sort items within each group
        for category in groups:
            groups[category] = self.sort_items_by_mode(groups[category])
        
        return dict(groups)
    
    def save_settings(self):
        """Save smart inventory settings"""
        return {
            "auto_sort_enabled": self.auto_sort_enabled,
            "auto_stack_enabled": self.auto_stack_enabled,
            "favorites": list(self.favorites),
            "sort_mode": self.sort_mode,
            "recent_items": self.recent_items.copy()
        }
    
    def load_settings(self, settings):
        """Load smart inventory settings"""
        self.auto_sort_enabled = settings.get("auto_sort_enabled", True)
        self.auto_stack_enabled = settings.get("auto_stack_enabled", True)
        self.favorites = set(settings.get("favorites", []))
        self.sort_mode = settings.get("sort_mode", "type")
        self.recent_items = settings.get("recent_items", [])

class SmartInventoryActions:
    """Helper class for inventory batch actions"""
    
    @staticmethod
    def repair_all_items(player, inventory_manager):
        """Repair all damaged items if player has sufficient resources"""
        repaired_count = 0
        repair_cost = 0
        
        for item_id, item_data in inventory_manager.inventory.items.items():
            if isinstance(item_data, dict) and "durability" in item_data:
                max_durability = item_data.get("max_durability", 100)
                current_durability = item_data["durability"]
                
                if current_durability < max_durability:
                    # Calculate repair cost (1 dubloon per 10 durability points)
                    cost = (max_durability - current_durability) // 10 + 1
                    repair_cost += cost
                    repaired_count += 1
        
        # Check if player can afford repairs
        if repair_cost <= getattr(player, 'dubloons', 0):
            player.dubloons -= repair_cost
            
            # Actually repair the items
            for item_id, item_data in inventory_manager.inventory.items.items():
                if isinstance(item_data, dict) and "durability" in item_data:
                    item_data["durability"] = item_data.get("max_durability", 100)
            
            return repaired_count, repair_cost
        
        return 0, 0
    
    @staticmethod
    def mass_craft_items(player, inventory_manager, recipe_id, quantity=1):
        """Attempt to craft multiple items if materials are available"""
        # This would integrate with a crafting system
        # Placeholder for now
        return False, "Crafting system not implemented"
    
    @staticmethod
    def organize_by_sets(inventory_manager):
        """Organize equipment by set pieces"""
        set_groups = defaultdict(list)
        
        for item_id, item_data in inventory_manager.inventory.items.items():
            if isinstance(item_data, dict) and "set_id" in item_data:
                set_id = item_data["set_id"]
                set_groups[set_id].append((item_id, item_data))
        
        return dict(set_groups)