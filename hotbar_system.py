"""
Hotbar System - Quick access slots for items, spells, and abilities

Provides 9 hotbar slots accessible via number keys 1-9 for quick access
during gameplay without opening menus.
"""

import time
from typing import Optional, Dict, Any, Tuple
from spells import SPELLS


class HotbarSlotType:
    """Types of items that can be placed in hotbar slots"""
    EMPTY = "empty"
    ITEM = "item"
    SPELL = "spell"
    ABILITY = "ability"
    EQUIPMENT = "equipment"


class HotbarSlot:
    """Represents a single hotbar slot"""
    
    def __init__(self, slot_id: int):
        self.slot_id = slot_id
        self.type = HotbarSlotType.EMPTY
        self.item_id = None  # Item/spell/ability identifier
        self.item_name = None
        self.icon = None  # For future icon support
        self.last_used = 0  # Timestamp of last use
        self.cooldown = 0  # Cooldown duration in seconds
        
    def set_item(self, item_id: str, item_name: str, slot_type: str = HotbarSlotType.ITEM):
        """Assign an item to this slot"""
        self.type = slot_type
        self.item_id = item_id
        self.item_name = item_name
        
    def clear(self):
        """Clear this slot"""
        self.type = HotbarSlotType.EMPTY
        self.item_id = None
        self.item_name = None
        self.icon = None
        
    def is_on_cooldown(self) -> bool:
        """Check if this slot is currently on cooldown"""
        if self.cooldown <= 0:
            return False
        return time.time() - self.last_used < self.cooldown
    
    def get_cooldown_remaining(self) -> float:
        """Get remaining cooldown time in seconds"""
        if self.cooldown <= 0:
            return 0
        remaining = self.cooldown - (time.time() - self.last_used)
        return max(0, remaining)
    
    def use(self, cooldown: float = 0):
        """Mark this slot as used and start cooldown"""
        self.last_used = time.time()
        self.cooldown = cooldown
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize slot to dictionary for saving"""
        return {
            'slot_id': self.slot_id,
            'type': self.type,
            'item_id': self.item_id,
            'item_name': self.item_name
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'HotbarSlot':
        """Deserialize slot from dictionary"""
        slot = HotbarSlot(data['slot_id'])
        slot.type = data.get('type', HotbarSlotType.EMPTY)
        slot.item_id = data.get('item_id')
        slot.item_name = data.get('item_name')
        return slot


class HotbarSystem:
    """Manages hotbar slots and quick access functionality"""
    
    def __init__(self, num_slots: int = 9):
        self.num_slots = num_slots
        self.slots = [HotbarSlot(i) for i in range(num_slots)]
        self.enabled = True
        self.locked = False  # Prevent accidental changes during combat
        
    def get_slot(self, slot_id: int) -> Optional[HotbarSlot]:
        """Get a specific slot by ID (0-8)"""
        if 0 <= slot_id < self.num_slots:
            return self.slots[slot_id]
        return None
    
    def set_slot_item(self, slot_id: int, item_id: str, item_name: str, 
                      slot_type: str = HotbarSlotType.ITEM) -> bool:
        """Assign an item to a specific slot"""
        slot = self.get_slot(slot_id)
        if slot and not self.locked:
            slot.set_item(item_id, item_name, slot_type)
            return True
        return False
    
    def clear_slot(self, slot_id: int) -> bool:
        """Clear a specific slot"""
        slot = self.get_slot(slot_id)
        if slot and not self.locked:
            slot.clear()
            return True
        return False
    
    def swap_slots(self, slot_id1: int, slot_id2: int) -> bool:
        """Swap contents of two slots"""
        if self.locked:
            return False
        
        slot1 = self.get_slot(slot_id1)
        slot2 = self.get_slot(slot_id2)
        
        if slot1 and slot2:
            # Swap all properties
            slot1.type, slot2.type = slot2.type, slot1.type
            slot1.item_id, slot2.item_id = slot2.item_id, slot1.item_id
            slot1.item_name, slot2.item_name = slot2.item_name, slot1.item_name
            slot1.icon, slot2.icon = slot2.icon, slot1.icon
            return True
        return False
    
    def use_slot(self, slot_id: int, player, game_state: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Use the item/spell in the specified slot
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        slot = self.get_slot(slot_id)
        
        if not slot or slot.type == HotbarSlotType.EMPTY:
            return False, "Empty slot"
        
        if slot.is_on_cooldown():
            remaining = slot.get_cooldown_remaining()
            return False, f"On cooldown: {remaining:.1f}s"
        
        # Handle different slot types
        success = False
        message = ""
        
        if slot.type == HotbarSlotType.ITEM:
            success, message = self._use_item(slot, player, game_state)
            
        elif slot.type == HotbarSlotType.SPELL:
            success, message = self._use_spell(slot, player, game_state)
            
        elif slot.type == HotbarSlotType.ABILITY:
            success, message = self._use_ability(slot, player, game_state)
            
        elif slot.type == HotbarSlotType.EQUIPMENT:
            success, message = self._quick_equip(slot, player)
        
        # If successful, start cooldown
        if success:
            # Default cooldowns by type
            cooldown = 1.0  # Default 1 second
            if slot.type == HotbarSlotType.SPELL:
                cooldown = 2.0
            elif slot.type == HotbarSlotType.ITEM:
                cooldown = 0.5
            slot.use(cooldown)
        
        return success, message
    
    def _use_item(self, slot: HotbarSlot, player, game_state: Dict[str, Any]) -> Tuple[bool, str]:
        """Use a consumable item from hotbar"""
        item_id = slot.item_id
        
        # Check if player has the item
        inventory = getattr(player, 'inventory', {})
        
        if item_id not in inventory or inventory[item_id] <= 0:
            # Item not in inventory, clear the slot
            slot.clear()
            return False, f"No {slot.item_name} in inventory"
        
        # Use the item based on its type
        if item_id in ['health_potion', 'small_health_potion', 'large_health_potion']:
            # Healing potions
            heal_amounts = {
                'small_health_potion': 20,
                'health_potion': 50,
                'large_health_potion': 100
            }
            heal = heal_amounts.get(item_id, 50)
            
            if player.health >= player.max_health:
                return False, "Already at full health"
            
            player.health = min(player.max_health, player.health + heal)
            inventory[item_id] -= 1
            return True, f"Restored {heal} HP"
        
        elif item_id in ['mana_potion', 'small_mana_potion', 'large_mana_potion']:
            # Mana potions
            mana_amounts = {
                'small_mana_potion': 20,
                'mana_potion': 50,
                'large_mana_potion': 100
            }
            restore = mana_amounts.get(item_id, 50)
            
            if not hasattr(player, 'mana') or player.mana >= player.max_mana:
                return False, "Already at full mana"
            
            player.mana = min(player.max_mana, player.mana + restore)
            inventory[item_id] -= 1
            return True, f"Restored {restore} mana"
        
        elif item_id in ['bread', 'cooked_meat', 'apple']:
            # Food items
            heal_amounts = {'bread': 10, 'cooked_meat': 25, 'apple': 5}
            heal = heal_amounts.get(item_id, 10)
            
            player.health = min(player.max_health, player.health + heal)
            inventory[item_id] -= 1
            return True, f"Ate {slot.item_name}, +{heal} HP"
        
        # Generic consumable
        if inventory[item_id] > 0:
            inventory[item_id] -= 1
            return True, f"Used {slot.item_name}"
        
        return False, "Cannot use this item"
    
    def _use_spell(self, slot: HotbarSlot, player, game_state: Dict[str, Any]) -> Tuple[bool, str]:
        """Cast a spell from hotbar"""
        spell_id = slot.item_id
        
        # Check if player knows the spell
        if not hasattr(player, 'known_spells') or spell_id not in player.known_spells:
            return False, "Spell not learned"
        
        # Check if spell exists in SPELLS dictionary
        if spell_id not in SPELLS:
            return False, "Unknown spell"
        
        spell = SPELLS[spell_id]
        
        # Check mana cost
        mana_cost = spell.get('mana_cost', 10)
        if hasattr(player, 'mana') and player.mana < mana_cost:
            return False, f"Not enough mana ({mana_cost} required)"
        
        # Spell casting handled by game's spell system in main.py
        # Return success and let main.py handle the actual casting with mouse position
        return True, f"Casting {slot.item_name}"
    
    def _use_ability(self, slot: HotbarSlot, player, game_state: Dict[str, Any]) -> Tuple[bool, str]:
        """Use a special ability from hotbar"""
        ability_id = slot.item_id
        
        # Check if player has the ability
        if not hasattr(player, 'abilities') or ability_id not in player.abilities:
            slot.clear()
            return False, "Ability not available"
        
        # Ability-specific logic would go here
        return True, f"Used {slot.item_name}"
    
    def _quick_equip(self, slot: HotbarSlot, player) -> Tuple[bool, str]:
        """Quickly equip an item from inventory"""
        item_id = slot.item_id
        
        # Check if player has the item
        inventory = getattr(player, 'inventory', {})
        if 'items' in inventory:
            # Find the item in items list
            for item in inventory['items']:
                if hasattr(item, 'id') and item.id == item_id:
                    # Equip the item
                    if hasattr(player, 'equipment'):
                        # Equipment system handles equipping
                        return True, f"Equipped {slot.item_name}"
        
        return False, "Item not found"
    
    def find_item_in_hotbar(self, item_id: str) -> Optional[int]:
        """Find which slot contains an item"""
        for slot in self.slots:
            if slot.item_id == item_id:
                return slot.slot_id
        return None
    
    def auto_assign_potion(self, item_id: str, item_name: str) -> bool:
        """Automatically assign a potion to the first empty slot"""
        for slot in self.slots:
            if slot.type == HotbarSlotType.EMPTY:
                slot.set_item(item_id, item_name, HotbarSlotType.ITEM)
                return True
        return False
    
    def toggle_lock(self):
        """Toggle hotbar lock to prevent accidental changes"""
        self.locked = not self.locked
        
    def clear_all(self):
        """Clear all hotbar slots"""
        if not self.locked:
            for slot in self.slots:
                slot.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize hotbar to dictionary for saving"""
        return {
            'num_slots': self.num_slots,
            'enabled': self.enabled,
            'locked': self.locked,
            'slots': [slot.to_dict() for slot in self.slots]
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'HotbarSystem':
        """Deserialize hotbar from dictionary"""
        num_slots = data.get('num_slots', 9)
        hotbar = HotbarSystem(num_slots)
        hotbar.enabled = data.get('enabled', True)
        hotbar.locked = data.get('locked', False)
        
        slots_data = data.get('slots', [])
        for i, slot_data in enumerate(slots_data):
            if i < num_slots:
                hotbar.slots[i] = HotbarSlot.from_dict(slot_data)
        
        return hotbar
