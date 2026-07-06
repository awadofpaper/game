"""
Inventory System Module

Handles all inventory-related functionality including item management, equipment,
crafting, and item interactions. Extracted from the main monolithic file.
"""

import pygame
import random
import json
import time
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum


class ItemType(Enum):
    """Types of items in the game."""
    CONSUMABLE = "consumable"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    TOOL = "tool"
    QUEST = "quest"
    KEY = "key"


class EquipmentSlot(Enum):
    """Equipment slot types."""
    WEAPON = "weapon"
    SHIELD = "shield"
    HELMET = "helmet"
    CHEST = "chest"
    LEGS = "legs"
    BOOTS = "boots"
    RING = "ring"
    NECKLACE = "necklace"


class ItemRarity(Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Item:
    """Base item class."""
    
    def __init__(self, item_id: str, name: str, item_type: ItemType, 
                 description: str = "", rarity: ItemRarity = ItemRarity.COMMON,
                 value: int = 1, stackable: bool = True, max_stack: int = 99):
        self.item_id = item_id
        self.name = name
        self.type = item_type
        self.description = description
        self.rarity = rarity
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack
        
        # Visual properties
        self.color = self._get_rarity_color()
        self.icon = None  # Could be a pygame surface or character
    
    def _get_rarity_color(self) -> Tuple[int, int, int]:
        """Get color based on rarity."""
        rarity_colors = {
            ItemRarity.COMMON: (200, 200, 200),
            ItemRarity.UNCOMMON: (50, 200, 50),
            ItemRarity.RARE: (50, 50, 255),
            ItemRarity.EPIC: (200, 50, 200),
            ItemRarity.LEGENDARY: (255, 165, 0)
        }
        return rarity_colors.get(self.rarity, (200, 200, 200))
    
    def can_use(self, player) -> bool:
        """Check if player can use this item."""
        return self.type == ItemType.CONSUMABLE
    
    def use(self, player) -> bool:
        """Use the item. Returns True if item was consumed."""
        if not self.can_use(player):
            return False
        
        # Override in subclasses
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for saving."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "rarity": self.rarity.value,
            "value": self.value,
            "stackable": self.stackable,
            "max_stack": self.max_stack
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create item from dictionary."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            item_type=ItemType(data["type"]),
            description=data.get("description", ""),
            rarity=ItemRarity(data.get("rarity", "common")),
            value=data.get("value", 1),
            stackable=data.get("stackable", True),
            max_stack=data.get("max_stack", 99)
        )


class Equipment(Item):
    """Equipment item that can be equipped."""
    
    def __init__(self, item_id: str, name: str, equipment_slot: EquipmentSlot,
                 description: str = "", rarity: ItemRarity = ItemRarity.COMMON,
                 value: int = 10, stat_bonuses: Dict[str, int] = None):
        super().__init__(item_id, name, ItemType.EQUIPMENT, description, rarity, value, False, 1)
        self.equipment_slot = equipment_slot
        self.stat_bonuses = stat_bonuses or {}
    
    def can_use(self, player) -> bool:
        """Equipment can be equipped."""
        return True
    
    def use(self, player) -> bool:
        """Equip the item."""
        if hasattr(player, 'equipment'):
            return player.equipment.equip_item(self)
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment to dictionary."""
        data = super().to_dict()
        data.update({
            "equipment_slot": self.equipment_slot.value,
            "stat_bonuses": self.stat_bonuses
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Equipment':
        """Create equipment from dictionary."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            equipment_slot=EquipmentSlot(data["equipment_slot"]),
            description=data.get("description", ""),
            rarity=ItemRarity(data.get("rarity", "common")),
            value=data.get("value", 10),
            stat_bonuses=data.get("stat_bonuses", {})
        )


class ConsumableItem(Item):
    """Consumable item with effects."""
    
    def __init__(self, item_id: str, name: str, description: str = "",
                 rarity: ItemRarity = ItemRarity.COMMON, value: int = 5,
                 effects: Dict[str, Any] = None, stackable: bool = True, max_stack: int = 99):
        super().__init__(item_id, name, ItemType.CONSUMABLE, description, rarity, value, stackable, max_stack)
        self.effects = effects or {}
    
    def use(self, player) -> bool:
        """Apply consumable effects to player."""
        if not self.can_use(player):
            return False
        
        # Apply effects
        for effect, value in self.effects.items():
            if effect == "heal":
                if hasattr(player, 'heal'):
                    player.heal(value)
                elif hasattr(player, 'health'):
                    player.health = min(player.max_health, player.health + value)
            
            elif effect == "mana":
                if hasattr(player, 'mana'):
                    player.mana = min(player.max_mana, player.mana + value)
            
            elif effect == "stamina":
                if hasattr(player, 'stamina'):
                    player.stamina = min(player.max_stamina, player.stamina + value)
            
            elif effect == "buff":
                # Apply temporary buff
                if hasattr(player, 'apply_buff'):
                    player.apply_buff(value["type"], value["amount"], value.get("duration", 60))
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert consumable to dictionary."""
        data = super().to_dict()
        data["effects"] = self.effects
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsumableItem':
        """Create consumable from dictionary."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data.get("description", ""),
            rarity=ItemRarity(data.get("rarity", "common")),
            value=data.get("value", 5),
            effects=data.get("effects", {}),
            stackable=data.get("stackable", True),
            max_stack=data.get("max_stack", 99)
        )


class ItemStack:
    """Represents a stack of items in inventory."""
    
    def __init__(self, item: Item, quantity: int = 1):
        self.item = item
        self.quantity = min(quantity, item.max_stack if item.stackable else 1)
    
    def can_add(self, amount: int) -> int:
        """Check how many items can be added to this stack."""
        if not self.item.stackable:
            return 0
        
        return min(amount, self.item.max_stack - self.quantity)
    
    def add(self, amount: int) -> int:
        """Add items to stack. Returns amount actually added."""
        can_add = self.can_add(amount)
        self.quantity += can_add
        return can_add
    
    def remove(self, amount: int) -> int:
        """Remove items from stack. Returns amount actually removed."""
        removed = min(amount, self.quantity)
        self.quantity -= removed
        return removed
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return self.quantity <= 0
    
    def is_full(self) -> bool:
        """Check if stack is full."""
        return self.quantity >= (self.item.max_stack if self.item.stackable else 1)
    
    def split(self, amount: int) -> Optional['ItemStack']:
        """Split stack into two. Returns new stack or None."""
        if amount >= self.quantity or amount <= 0:
            return None
        
        self.quantity -= amount
        return ItemStack(self.item, amount)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stack to dictionary."""
        return {
            "item": self.item.to_dict(),
            "quantity": self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemStack':
        """Create stack from dictionary."""
        item_data = data["item"]
        
        # Create appropriate item type
        if item_data["type"] == "equipment":
            item = Equipment.from_dict(item_data)
        elif item_data["type"] == "consumable":
            item = ConsumableItem.from_dict(item_data)
        else:
            item = Item.from_dict(item_data)
        
        return cls(item, data["quantity"])


class Inventory:
    """Player inventory management."""
    
    def __init__(self, capacity: int = 30):
        self.capacity = capacity
        self.slots: List[Optional[ItemStack]] = [None] * capacity
        self.gold = 0
    
    def add_item(self, item: Item, quantity: int = 1) -> int:
        """Add items to inventory. Returns quantity actually added."""
        remaining = quantity
        
        # First, try to add to existing stacks
        if item.stackable:
            for slot in self.slots:
                if slot and slot.item.item_id == item.item_id and not slot.is_full():
                    added = slot.add(remaining)
                    remaining -= added
                    if remaining <= 0:
                        break
        
        # Then, add to empty slots
        if remaining > 0:
            for i, slot in enumerate(self.slots):
                if slot is None:
                    stack_size = min(remaining, item.max_stack if item.stackable else 1)
                    self.slots[i] = ItemStack(item, stack_size)
                    remaining -= stack_size
                    if remaining <= 0:
                        break
        
        return quantity - remaining
    
    def remove_item(self, item_id: str, quantity: int = 1) -> int:
        """Remove items from inventory. Returns quantity actually removed."""
        removed = 0
        
        for i, slot in enumerate(self.slots):
            if slot and slot.item.item_id == item_id:
                stack_removed = slot.remove(min(quantity - removed, slot.quantity))
                removed += stack_removed
                
                if slot.is_empty():
                    self.slots[i] = None
                
                if removed >= quantity:
                    break
        
        return removed
    
    def get_item_count(self, item_id: str) -> int:
        """Get total quantity of item in inventory."""
        total = 0
        for slot in self.slots:
            if slot and slot.item.item_id == item_id:
                total += slot.quantity
        return total
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has enough of an item."""
        return self.get_item_count(item_id) >= quantity
    
    def get_empty_slots(self) -> int:
        """Get number of empty inventory slots."""
        return sum(1 for slot in self.slots if slot is None)
    
    def is_full(self) -> bool:
        """Check if inventory is completely full."""
        return self.get_empty_slots() == 0
    
    def use_item(self, slot_index: int, player) -> bool:
        """Use item from specific slot."""
        if 0 <= slot_index < len(self.slots) and self.slots[slot_index]:
            stack = self.slots[slot_index]
            
            if stack.item.use(player):
                # Item was consumed
                stack.remove(1)
                if stack.is_empty():
                    self.slots[slot_index] = None
                return True
        
        return False
    
    def move_item(self, from_slot: int, to_slot: int) -> bool:
        """Move item from one slot to another."""
        if (0 <= from_slot < len(self.slots) and 0 <= to_slot < len(self.slots) and
            from_slot != to_slot):
            
            from_stack = self.slots[from_slot]
            to_stack = self.slots[to_slot]
            
            if from_stack is None:
                return False
            
            if to_stack is None:
                # Simple move
                self.slots[to_slot] = from_stack
                self.slots[from_slot] = None
                return True
            
            elif (to_stack.item.item_id == from_stack.item.item_id and 
                  to_stack.item.stackable and not to_stack.is_full()):
                # Stack merge
                can_add = to_stack.can_add(from_stack.quantity)
                to_stack.add(can_add)
                from_stack.remove(can_add)
                
                if from_stack.is_empty():
                    self.slots[from_slot] = None
                
                return True
            
            else:
                # Swap items
                self.slots[from_slot] = to_stack
                self.slots[to_slot] = from_stack
                return True
        
        return False
    
    def sort_inventory(self) -> None:
        """Sort inventory by item type and name."""
        # Collect all non-empty stacks
        stacks = [stack for stack in self.slots if stack is not None]
        
        # Sort by item type, then by name
        stacks.sort(key=lambda s: (s.item.type.value, s.item.name))
        
        # Clear slots and re-add sorted items
        self.slots = [None] * self.capacity
        for i, stack in enumerate(stacks):
            if i < self.capacity:
                self.slots[i] = stack
    
    def get_items_by_type(self, item_type: ItemType) -> List[Tuple[int, ItemStack]]:
        """Get all items of a specific type with their slot indices."""
        items = []
        for i, slot in enumerate(self.slots):
            if slot and slot.item.type == item_type:
                items.append((i, slot))
        return items
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary for saving."""
        return {
            "capacity": self.capacity,
            "gold": self.gold,
            "slots": [slot.to_dict() if slot else None for slot in self.slots]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Inventory':
        """Create inventory from dictionary."""
        inventory = cls(data.get("capacity", 30))
        inventory.gold = data.get("gold", 0)
        
        slot_data = data.get("slots", [])
        for i, slot_info in enumerate(slot_data):
            if i < inventory.capacity and slot_info:
                inventory.slots[i] = ItemStack.from_dict(slot_info)
        
        return inventory


class PlayerEquipment:
    """Player equipment management."""
    
    def __init__(self):
        self.slots: Dict[EquipmentSlot, Optional[Equipment]] = {
            slot: None for slot in EquipmentSlot
        }
    
    def equip_item(self, equipment: Equipment) -> bool:
        """Equip an equipment item."""
        slot = equipment.equipment_slot
        
        # Store old equipment
        old_equipment = self.slots[slot]
        
        # Equip new item
        self.slots[slot] = equipment
        
        # If there was old equipment, it would need to go back to inventory
        # This would be handled by the calling code
        
        return True
    
    def unequip_item(self, slot: EquipmentSlot) -> Optional[Equipment]:
        """Unequip item from slot."""
        equipment = self.slots[slot]
        self.slots[slot] = None
        return equipment
    
    def get_stat_bonuses(self) -> Dict[str, int]:
        """Get total stat bonuses from all equipped items."""
        total_bonuses = {}
        
        for equipment in self.slots.values():
            if equipment:
                for stat, bonus in equipment.stat_bonuses.items():
                    total_bonuses[stat] = total_bonuses.get(stat, 0) + bonus
        
        return total_bonuses
    
    def get_equipped_item(self, slot: EquipmentSlot) -> Optional[Equipment]:
        """Get item equipped in specific slot."""
        return self.slots[slot]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment to dictionary."""
        return {
            slot.value: equipment.to_dict() if equipment else None
            for slot, equipment in self.slots.items()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerEquipment':
        """Create equipment from dictionary."""
        equipment = cls()
        
        for slot_name, equipment_data in data.items():
            try:
                slot = EquipmentSlot(slot_name)
                if equipment_data:
                    equipment.slots[slot] = Equipment.from_dict(equipment_data)
            except ValueError:
                continue  # Skip invalid slot names
        
        return equipment


class ItemDatabase:
    """Database of all available items."""
    
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self._initialize_default_items()
    
    def _initialize_default_items(self) -> None:
        """Initialize default game items."""
        # Consumables
        self.register_item(ConsumableItem(
            "health_potion", "Health Potion", "Restores 50 health points",
            ItemRarity.COMMON, 25, {"heal": 50}
        ))
        
        self.register_item(ConsumableItem(
            "mana_potion", "Mana Potion", "Restores 30 mana points",
            ItemRarity.COMMON, 20, {"mana": 30}
        ))
        
        self.register_item(ConsumableItem(
            "stamina_potion", "Stamina Potion", "Restores 40 stamina points",
            ItemRarity.COMMON, 15, {"stamina": 40}
        ))
        
        # Equipment
        self.register_item(Equipment(
            "iron_sword", "Iron Sword", EquipmentSlot.WEAPON,
            "A sturdy iron sword", ItemRarity.COMMON, 50,
            {"attack": 10, "strength": 2}
        ))
        
        self.register_item(Equipment(
            "wooden_shield", "Wooden Shield", EquipmentSlot.SHIELD,
            "A basic wooden shield", ItemRarity.COMMON, 30,
            {"defense": 5, "constitution": 1}
        ))
        
        self.register_item(Equipment(
            "leather_helmet", "Leather Helmet", EquipmentSlot.HELMET,
            "Basic leather protection", ItemRarity.COMMON, 20,
            {"defense": 2}
        ))
        
        # Materials
        self.register_item(Item(
            "wood", "Wood", ItemType.MATERIAL,
            "Basic crafting material", ItemRarity.COMMON, 1
        ))
        
        self.register_item(Item(
            "stone", "Stone", ItemType.MATERIAL,
            "Hard crafting material", ItemRarity.COMMON, 2
        ))
        
        self.register_item(Item(
            "iron_ore", "Iron Ore", ItemType.MATERIAL,
            "Metal crafting material", ItemRarity.UNCOMMON, 5
        ))
        
        # Tools
        self.register_item(Item(
            "pickaxe", "Pickaxe", ItemType.TOOL,
            "For mining stone and ore", ItemRarity.COMMON, 40, False, 1
        ))
        
        self.register_item(Item(
            "axe", "Axe", ItemType.TOOL,
            "For chopping wood", ItemRarity.COMMON, 35, False, 1
        ))
    
    def register_item(self, item: Item) -> None:
        """Register an item in the database."""
        self.items[item.item_id] = item
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get item by ID."""
        return self.items.get(item_id)
    
    def create_item(self, item_id: str) -> Optional[Item]:
        """Create a new instance of an item."""
        template = self.get_item(item_id)
        if template:
            # Create new instance from template
            if isinstance(template, Equipment):
                return Equipment(
                    template.item_id, template.name, template.equipment_slot,
                    template.description, template.rarity, template.value,
                    template.stat_bonuses.copy()
                )
            elif isinstance(template, ConsumableItem):
                return ConsumableItem(
                    template.item_id, template.name, template.description,
                    template.rarity, template.value, template.effects.copy(),
                    template.stackable, template.max_stack
                )
            else:
                return Item(
                    template.item_id, template.name, template.type,
                    template.description, template.rarity, template.value,
                    template.stackable, template.max_stack
                )
        return None
    
    def get_items_by_type(self, item_type: ItemType) -> List[Item]:
        """Get all items of a specific type."""
        return [item for item in self.items.values() if item.type == item_type]
    
    def get_random_item(self, item_type: Optional[ItemType] = None, 
                       rarity: Optional[ItemRarity] = None) -> Optional[Item]:
        """Get a random item, optionally filtered by type and rarity."""
        candidates = list(self.items.values())
        
        if item_type:
            candidates = [item for item in candidates if item.type == item_type]
        
        if rarity:
            candidates = [item for item in candidates if item.rarity == rarity]
        
        if candidates:
            template = random.choice(candidates)
            return self.create_item(template.item_id)
        
        return None


# Global item database instance
item_database = ItemDatabase()


# Utility functions for backwards compatibility
def create_item(item_type: str, **kwargs) -> Optional[Item]:
    """Create an item - backwards compatibility function."""
    return item_database.create_item(item_type)


def add_item_to_inventory(inventory: Inventory, item_id: str, quantity: int = 1) -> int:
    """Add item to inventory by ID."""
    item = item_database.create_item(item_id)
    if item:
        return inventory.add_item(item, quantity)
    return 0


def get_item_info(item_id: str) -> Optional[Dict[str, Any]]:
    """Get item information by ID."""
    item = item_database.get_item(item_id)
    if item:
        return item.to_dict()
    return None