"""
Equipment Manager - Handles all equipment operations
Standardizes equipment system across the game
"""
import logging

logger = logging.getLogger(__name__)


class EquipmentManager:
    """Manages player equipment operations"""
    
    def __init__(self, player):
        self.player = player
        
        # Standard equipment slots
        self.slots = {
            'head': {'name': 'Head', 'types': ['helmet', 'hat', 'hood', 'head']},
            'neck': {'name': 'Neck', 'types': ['necklace', 'amulet', 'neck']},
            'chest': {'name': 'Chest', 'types': ['chestplate', 'armor', 'robe', 'chest', 'body']},
            'main_hand': {'name': 'Main Hand', 'types': ['weapon', 'sword', 'axe', 'staff', 'wand', 'dagger', 'spear', 'stick']},
            'off_hand': {'name': 'Off Hand', 'types': ['shield', 'weapon', 'sword', 'dagger', 'off_hand']},
            'hands': {'name': 'Hands', 'types': ['gloves', 'gauntlets', 'hands']},
            'legs': {'name': 'Legs', 'types': ['leggings', 'pants', 'legs']},
            'feet': {'name': 'Feet', 'types': ['boots', 'shoes', 'feet']},
            'ring1': {'name': 'Ring 1', 'types': ['ring', 'ring1', 'accessory']},
            'ring2': {'name': 'Ring 2', 'types': ['ring', 'ring2', 'accessory']},
        }
        
    def can_equip_to_slot(self, item, slot):
        """Check if an item can be equipped to a specific slot"""
        if slot not in self.slots:
            return False, f"Invalid slot: {slot}"
        
        # Get item type
        item_type = self.get_item_type(item)
        if not item_type:
            return False, "Item has no type"
        
        # Check if item type matches slot
        valid_types = self.slots[slot]['types']
        if item_type.lower() not in valid_types:
            return False, f"Cannot equip {item_type} to {self.slots[slot]['name']}"
        
        # Check level requirements if they exist
        if hasattr(item, 'level_requirement'):
            if self.player.level < item.level_requirement:
                return False, f"Requires level {item.level_requirement}"
        
        return True, "OK"
    
    def get_item_type(self, item):
        """Get the type of an item"""
        if hasattr(item, 'type'):
            return item.type
        elif hasattr(item, 'equipment_type'):
            return item.equipment_type
        elif hasattr(item, 'slot'):
            return item.slot
        return None
    
    def get_best_slot_for_item(self, item):
        """Determine the best slot for an item"""
        item_type = self.get_item_type(item)
        if not item_type:
            return None
        
        item_type_lower = item_type.lower()
        
        # Check each slot to find the best match
        for slot, slot_info in self.slots.items():
            if item_type_lower in slot_info['types']:
                # For rings, use first empty ring slot
                if slot in ['ring1', 'ring2']:
                    if self.player.equipment.get('ring1') is None:
                        return 'ring1'
                    elif self.player.equipment.get('ring2') is None:
                        return 'ring2'
                    else:
                        return 'ring1'  # Replace first ring
                return slot
        
        # Fallback: legacy slot mapping
        if 'weapon' in item_type_lower or 'sword' in item_type_lower or 'stick' in item_type_lower:
            return 'main_hand'
        elif 'armor' in item_type_lower or 'chest' in item_type_lower:
            return 'chest'
        elif 'ring' in item_type_lower or 'accessory' in item_type_lower:
            return 'ring1'
        
        return None
    
    def equip_item(self, item, slot=None):
        """
        Equip an item to a slot
        
        Args:
            item: Item object to equip
            slot: Specific slot (optional, auto-determined if None)
            
        Returns:
            tuple: (success: bool, message: str, unequipped_item)
        """
        # Determine slot if not specified
        if slot is None:
            slot = self.get_best_slot_for_item(item)
            if slot is None:
                return False, "Cannot determine equipment slot for this item", None
        
        # Validate slot
        can_equip, reason = self.can_equip_to_slot(item, slot)
        if not can_equip:
            return False, reason, None
        
        # Get currently equipped item
        current_item = self.player.equipment.get(slot)
        
        # Equip new item
        self.player.equipment[slot] = item
        
        # Remove from inventory
        if item in self.player.inventory.get('items', []):
            self.player.inventory['items'].remove(item)
        
        # Update player stats
        self._update_player_stats()
        
        logger.info(f"[EQUIP] Equipped {self.get_item_name(item)} to {slot}")
        
        return True, f"Equipped {self.get_item_name(item)} to {self.slots[slot]['name']}", current_item
    
    def unequip_item(self, slot):
        """
        Unequip an item from a slot
        
        Args:
            slot: Slot to unequip from
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if slot not in self.player.equipment:
            return False, f"Invalid slot: {slot}"
        
        item = self.player.equipment.get(slot)
        if item is None:
            return False, f"No item equipped in {self.slots.get(slot, {}).get('name', slot)}"
        
        # Remove from slot
        self.player.equipment[slot] = None
        
        # Add back to inventory
        self.player.inventory['items'].append(item)
        
        # Update player stats
        self._update_player_stats()
        
        logger.info(f"[UNEQUIP] Unequipped {self.get_item_name(item)} from {slot}")
        
        return True, f"Unequipped {self.get_item_name(item)}"
    
    def swap_equipment(self, from_slot, to_slot):
        """Swap equipment between two slots"""
        if from_slot not in self.player.equipment or to_slot not in self.player.equipment:
            return False, "Invalid slots"
        
        item1 = self.player.equipment[from_slot]
        item2 = self.player.equipment[to_slot]
        
        self.player.equipment[from_slot] = item2
        self.player.equipment[to_slot] = item1
        
        self._update_player_stats()
        
        return True, "Equipment swapped"
    
    def get_item_name(self, item):
        """Get the display name of an item"""
        if item is None:
            return "Empty"
        if hasattr(item, 'name'):
            return item.name
        return str(item)
    
    def get_item_stats(self, item):
        """Get all stats from an item"""
        if item is None:
            return {}
        
        stats = {}
        if hasattr(item, 'stats') and isinstance(item.stats, dict):
            stats.update(item.stats)
        
        # Check for individual stat attributes
        for attr in ['damage', 'defense', 'attack', 'health', 'mana', 'stamina']:
            if hasattr(item, attr):
                value = getattr(item, attr)
                if value and value != 0:
                    stats[attr] = value
        
        return stats
    
    def compare_items(self, item1, item2):
        """
        Compare two items and return stat differences
        
        Returns:
            dict: {stat_name: (item1_value, item2_value, difference)}
        """
        stats1 = self.get_item_stats(item1)
        stats2 = self.get_item_stats(item2)
        
        comparison = {}
        
        # Get all unique stat names
        all_stats = set(list(stats1.keys()) + list(stats2.keys()))
        
        for stat in all_stats:
            val1 = stats1.get(stat, 0)
            val2 = stats2.get(stat, 0)
            diff = val2 - val1
            comparison[stat] = (val1, val2, diff)
        
        return comparison
    
    def get_total_stats(self):
        """Calculate total stats from all equipped items"""
        total_stats = {}
        
        for slot, item in self.player.equipment.items():
            if item is not None:
                item_stats = self.get_item_stats(item)
                for stat, value in item_stats.items():
                    total_stats[stat] = total_stats.get(stat, 0) + value
        
        return total_stats
    
    def _update_player_stats(self):
        """Update player stats based on equipped items"""
        # This will be called after equip/unequip
        # The actual stat application should be handled by the player class
        # or we can implement it here if needed
        pass
    
    def get_equipped_items_list(self):
        """Get a list of all equipped items with their slots"""
        equipped = []
        for slot, item in self.player.equipment.items():
            if item is not None:
                equipped.append({
                    'slot': slot,
                    'slot_name': self.slots.get(slot, {}).get('name', slot.title()),
                    'item': item,
                    'name': self.get_item_name(item)
                })
        return equipped
    
    def get_equippable_items(self):
        """Get all items from inventory that can be equipped"""
        equippable = []
        
        for item in self.player.inventory.get('items', []):
            slot = self.get_best_slot_for_item(item)
            if slot is not None:
                equippable.append({
                    'item': item,
                    'name': self.get_item_name(item),
                    'slot': slot,
                    'slot_name': self.slots.get(slot, {}).get('name', slot.title())
                })
        
        return equippable
