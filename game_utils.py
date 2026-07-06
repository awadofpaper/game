"""
Game utility functions module.
Contains helper functions for UI, menus, character creation, and item management.
"""
import pygame
import sys
import random
import logging
from resource_cache import get_cached_surface, get_cached_font

logger = logging.getLogger(__name__)

# Menu options
MENU_OPTIONS = ["New Game", "Load Game", "Help", "Delete Save", "Exit"]

# Item Icons - Comprehensive emoji mapping for visual representation
ITEM_ICONS = {
    # Weapons
    'sword': '⚔️', 'iron_sword': '⚔️', 'steel_sword': '⚔️', 'bronze_sword': '⚔️',
    'bow': '🏹', 'crossbow': '🏹',
    'staff': '🪄', 'wand': '🪄', 'magic_staff': '🪄',
    'axe': '🪓', 'battle_axe': '🪓',
    'dagger': '🗡️', 'knife': '🗡️',
    'spear': '🔱',
    'hammer': '🔨',
    'stick': '🦯',
    
    # Armor - Helmets
    'helm': '⛑️', 'helmet': '⛑️', 'iron_helm': '⛑️', 'steel_helm': '⛑️', 'bronze_helm': '⛑️',
    'stone_helm': '⛑️', 'leather_helm': '🎓',
    
    # Armor - Chest
    'chestplate': '🛡️', 'armor': '🛡️', 'iron_chestplate': '🛡️', 'steel_chestplate': '🛡️',
    'bronze_chestplate': '🛡️', 'leather_armor': '🦺',
    
    # Armor - Legs
    'leggings': '👖', 'pants': '👖', 'iron_leggings': '👖', 'steel_leggings': '👖',
    
    # Armor - Boots
    'boots': '🥾', 'iron_boots': '🥾', 'steel_boots': '🥾', 'leather_boots': '👢',
    
    # Tools
    'pickaxe': '⛏️', 'iron_pickaxe': '⛏️', 'bronze_pickaxe': '⛏️', 'stone_pickaxe': '⛏️',
    'bronze_axe': '🪓', 'iron_axe': '🪓',
    'shovel': '🪣',
    'fishing_rod': '🎣', 'fishing_net': '🕸️',
    
    # Food
    'apple': '🍎', 'bread': '🍞', 'meat': '🍖', 'cooked_meat': '🍗',
    'fish': '🐟', 'cooked_fish': '🍣',
    'berries': '🫐', 'mushroom': '🍄',
    'cheese': '🧀', 'egg': '🥚',
    
    # Potions
    'health_potion': '❤️', 'mana_potion': '💙', 'stamina_potion': '💚',
    'strength_potion': '💪', 'defense_potion': '🛡️',
    'invisibility_potion': '👻', 'fire_resist_potion': '🔥',
    'elixir': '🧪', 'antidote': '💊', 'energy_drink': '⚡',
    'potion': '🧃',
    
    # Resources
    'wood': '🪵', 'log': '🪵', 'plank': '🪵',
    'stone': '🪨', 'rock': '🪨', 'rubble': '🪨',
    'ore': '⛰️', 'iron_ore': '⛰️', 'copper_ore': '🟫', 'tin_ore': '⚪',
    'iron': '⚙️', 'copper': '🟠', 'tin': '⚪',
    'coal': '⚫', 'diamond': '💎', 'emerald': '💚', 'ruby': '❤️',
    'fiber': '🧵', 'thread': '🧵', 'cloth': '🧶',
    'leather': '🟤',
    'herbs': '🌿', 'plant': '🌱',
    'bones': '🦴', 'skull': '💀',
    'feather': '🪶',
    'ash': '🌫️', 'sand': '⏳',
    
    # Currency
    'dubloon': '🪙', 'coin': '🪙', 'gold': '💰',
    
    # Quest Items
    'ancient_relic': '🏺', 'magic_key': '🗝️', 'lost_letter': '📜',
    'sacred_stone': '🔮', 'map_fragment': '🗺️',
    'scroll': '📜', 'book': '📖',
    
    # Utility Items
    'torch': '🔦', 'lantern': '🏮',
    'rope': '🪢',
    'lockpick': '🔓',
    'bomb': '💣', 'dynamite': '🧨',
    'compass': '🧭',
    'bag': '🎒', 'backpack': '🎒',
    
    # Special Items
    'crystal': '💎',
    'gem': '💎',
    'amulet': '📿',
    'ring': '💍',
    'crown': '👑',
    'trophy': '🏆',
    
    # Default fallback
    'default': '📦'
}


def get_item_icon(item_name):
    """Get the emoji icon for an item. Returns default if not found."""
    if not item_name:
        return ITEM_ICONS['default']
    # Normalize item name to lowercase
    item_key = str(item_name).lower().strip()
    return ITEM_ICONS.get(item_key, ITEM_ICONS['default'])


def get_equipment_slot(item):
    """Determine which equipment slot an item should go in based on its name/type."""
    if not hasattr(item, 'name') and not hasattr(item, 'type'):
        return None
    
    item_name = getattr(item, 'name', '').lower() if hasattr(item, 'name') else ''
    item_type = getattr(item, 'type', '').lower() if hasattr(item, 'type') else ''
    
    # Check for weapons
    if item_type == 'weapon' or any(word in item_name for word in ['sword', 'axe', 'bow', 'staff', 'dagger', 'spear', 'mace', 'wand']):
        return 'weapon'
    
    # Check for head gear
    if 'helm' in item_name or 'helmet' in item_name or 'hat' in item_name or 'crown' in item_name or 'hood' in item_name:
        return 'head'
    
    # Check for body armor
    if 'chest' in item_name or 'plate' in item_name or 'robe' in item_name or 'tunic' in item_name or 'shirt' in item_name or 'armor' in item_name:
        return 'body'
    
    # Check for arm/shoulder gear
    if 'shoulder' in item_name or 'pauldron' in item_name or 'arm' in item_name:
        return 'arms'
    
    # Check for hand gear
    if 'glove' in item_name or 'gauntlet' in item_name or 'hand' in item_name:
        return 'hands'
    
    # Check for leg gear
    if 'leg' in item_name or 'pant' in item_name or 'greave' in item_name or 'trouser' in item_name:
        return 'legs'
    
    # Check for foot gear
    if 'boot' in item_name or 'shoe' in item_name or 'sandal' in item_name or 'feet' in item_name:
        return 'feet'
    
    # Check for necklace
    if 'necklace' in item_name or 'amulet' in item_name or 'pendant' in item_name:
        return 'necklace'
    
    # Check for rings
    if 'ring' in item_name or item_type == 'ring':
        return 'ring'  # The equip method will handle ring1/ring2 selection
    
    # Check for shields
    if 'shield' in item_name or item_type == 'shield':
        return 'off_hand'
    
    # Default to body for generic armor type
    if item_type == 'armor':
        return 'body'
    
    # Default to accessory as body slot
    if item_type == 'accessory':
        return 'necklace'
    
    return None


def get_equipment_comparison(item, player):
    """
    Generate detailed equipment comparison information.
    Returns a dict with item stats and comparison to currently equipped item.
    """
    # Validate item object
    if not item:
        return None
    
    if not hasattr(item, 'stats'):
        return None
    
    # Validate stats is a dictionary
    item_stats = getattr(item, 'stats', None)
    if not isinstance(item_stats, dict):
        return None
    
    slot = get_equipment_slot(item)
    if not slot:
        return None
    
    comparison = {
        'item': item,
        'slot': slot,
        'slot_display': slot.replace('_', ' ').title() if slot not in ['ring1', 'ring2'] else 'Ring',
        'stats': {},
        'currently_equipped': None,
        'stat_changes': {},
        'net_effect': 'neutral'  # 'positive', 'negative', or 'neutral'
    }
    
    # Get item stats with validation
    for stat_name, stat_value in item_stats.items():
        # Skip internal attributes and validate stat values
        if stat_name not in ['stack_count', 'durability', 'max_durability']:
            # Ensure stat value is numeric
            if isinstance(stat_value, (int, float)):
                comparison['stats'][stat_name] = stat_value
    
    # Get currently equipped item in this slot
    current_item = None
    if slot == 'ring':
        # Check both ring slots
        ring1 = player.equipment.get('ring1')
        ring2 = player.equipment.get('ring2')
        if ring1:
            current_item = ring1
        elif ring2:
            current_item = ring2
    else:
        current_item = player.equipment.get(slot)
    
    if current_item and hasattr(current_item, 'stats'):
        comparison['currently_equipped'] = current_item
        current_stats = getattr(current_item, 'stats', {})
        
        # Validate current_stats is a dictionary
        if not isinstance(current_stats, dict):
            current_stats = {}
        
        # Calculate stat changes
        all_stat_names = set(item_stats.keys()) | set(current_stats.keys())
        positive_changes = 0
        negative_changes = 0
        
        for stat_name in all_stat_names:
            if stat_name in ['stack_count', 'durability', 'max_durability']:
                continue
            
            new_value = item_stats.get(stat_name, 0)
            old_value = current_stats.get(stat_name, 0)
            
            # Validate values are numeric before comparison
            if not isinstance(new_value, (int, float)):
                new_value = 0
            if not isinstance(old_value, (int, float)):
                old_value = 0
            
            change = new_value - old_value
            
            if change != 0:
                comparison['stat_changes'][stat_name] = {
                    'old': old_value,
                    'new': new_value,
                    'change': change
                }
                
                # Determine if this is positive or negative
                # Most stats are positive when increased, except weight
                if stat_name.lower() in ['weight', 'curse']:
                    if change < 0:
                        positive_changes += abs(change)
                    else:
                        negative_changes += abs(change)
                else:
                    if change > 0:
                        positive_changes += abs(change)
                    else:
                        negative_changes += abs(change)
        
        # Determine net effect
        if positive_changes > negative_changes:
            comparison['net_effect'] = 'positive'
        elif negative_changes > positive_changes:
            comparison['net_effect'] = 'negative'
        else:
            comparison['net_effect'] = 'neutral'
    else:
        # No item equipped, so equipping is always positive
        comparison['net_effect'] = 'positive'
    
    return comparison


def format_equipment_tooltip(comparison, font_size=16):
    """
    Format equipment comparison data into readable text lines.
    Returns a list of (text, color) tuples.
    """
    if not comparison:
        return []
    
    lines = []
    item = comparison['item']
    
    # Item name and rarity
    rarity_colors = {
        'common': (200, 200, 200),
        'uncommon': (100, 255, 100),
        'rare': (100, 100, 255),
        'epic': (200, 100, 255),
        'legendary': (255, 200, 50),
        'artifact': (255, 128, 0),
        'set': (255, 215, 0)
    }
    item_rarity = getattr(item, 'rarity', 'common')
    item_name = getattr(item, 'name', 'Unknown')
    
    # Add equipped indicator
    is_equipped = False
    if comparison['currently_equipped'] == item:
        is_equipped = True
        lines.append((f"✓ {item_name} [EQUIPPED]", rarity_colors.get(item_rarity, (255, 255, 255))))
    else:
        lines.append((f"{item_name}", rarity_colors.get(item_rarity, (255, 255, 255))))
    
    # Show rarity
    rarity_display = item_rarity.capitalize()
    lines.append((f"Rarity: {rarity_display}", rarity_colors.get(item_rarity, (180, 180, 180))))
    
    lines.append((f"Slot: {comparison['slot_display']}", (180, 180, 180)))
    
    # Show level requirement if available
    if hasattr(item, 'level_requirement'):
        level_req = item.level_requirement
        lines.append((f"Level Required: {level_req}", (255, 200, 100)))
    elif hasattr(item, 'stats') and 'level_requirement' in item.stats:
        level_req = item.stats['level_requirement']
        lines.append((f"Level Required: {level_req}", (255, 200, 100)))
    
    # Show value/price
    if hasattr(item, 'value'):
        value = item.value
        lines.append((f"Value: {value} 🪙", (255, 215, 0)))
    elif hasattr(item, 'stats') and 'value' in item.stats:
        value = item.stats['value']
        lines.append((f"Value: {value} 🪙", (255, 215, 0)))
    
    # Show weight
    if hasattr(item, 'weight'):
        weight = item.weight
        lines.append((f"Weight: {weight}", (180, 180, 180)))
    elif hasattr(item, 'stats') and 'weight' in item.stats:
        weight = item.stats['weight']
        lines.append((f"Weight: {weight}", (180, 180, 180)))
    
    # Show durability if available
    if hasattr(item, 'durability') and hasattr(item, 'max_durability'):
        durability = item.durability
        max_durability = item.max_durability
        durability_percent = (durability / max_durability * 100) if max_durability > 0 else 0
        
        # Color based on durability
        if durability_percent > 70:
            dur_color = (100, 255, 100)
        elif durability_percent > 30:
            dur_color = (255, 255, 100)
        else:
            dur_color = (255, 100, 100)
        
        lines.append((f"Durability: {durability}/{max_durability} ({durability_percent:.0f}%)", dur_color))
    
    lines.append(("", (255, 255, 255)))  # Blank line
    
    # Current stats
    if comparison['stats']:
        lines.append(("Stats:", (255, 255, 100)))
        for stat_name, value in comparison['stats'].items():
            if stat_name not in ['level_requirement', 'value', 'weight', 'durability', 'max_durability']:
                stat_display = stat_name.replace('_', ' ').title()
                lines.append((f"  {stat_display}: {value}", (220, 220, 220)))
        lines.append(("", (255, 255, 255)))  # Blank line
    
    # Show set bonus information
    if hasattr(item, 'set_name'):
        set_name = item.set_name
        lines.append((f"Set: {set_name}", (255, 215, 0)))
        if hasattr(item, 'set_bonus'):
            lines.append(("Set Bonus:", (200, 200, 100)))
            set_bonus = item.set_bonus
            if isinstance(set_bonus, dict):
                for bonus_stat, bonus_value in set_bonus.items():
                    lines.append((f"  (2) {bonus_stat}: +{bonus_value}", (150, 255, 150)))
            else:
                lines.append((f"  {set_bonus}", (150, 255, 150)))
        lines.append(("", (255, 255, 255)))  # Blank line
    
    # Show flavor text/description
    if hasattr(item, 'description'):
        description = item.description
        # Word wrap description at ~40 characters
        words = description.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 40:
                current_line += word + " "
            else:
                if current_line:
                    lines.append((current_line.strip(), (160, 160, 180)))
                current_line = word + " "
        if current_line:
            lines.append((current_line.strip(), (160, 160, 180)))
        lines.append(("", (255, 255, 255)))  # Blank line
    
    # Comparison with equipped item
    if comparison['currently_equipped'] and comparison['currently_equipped'] != item:
        current_name = getattr(comparison['currently_equipped'], 'name', 'Unknown')
        lines.append((f"Currently Equipped: {current_name}", (200, 200, 100)))
        
        if comparison['stat_changes']:
            lines.append(("Changes:", (255, 255, 100)))
            for stat_name, change_data in comparison['stat_changes'].items():
                stat_display = stat_name.replace('_', ' ').title()
                change = change_data['change']
                
                # Determine color based on whether change is good or bad
                is_negative_stat = stat_name.lower() in ['weight', 'curse']
                if (change > 0 and not is_negative_stat) or (change < 0 and is_negative_stat):
                    color = (100, 255, 100)  # Green for good
                    symbol = "▲"
                elif (change < 0 and not is_negative_stat) or (change > 0 and is_negative_stat):
                    color = (255, 100, 100)  # Red for bad
                    symbol = "▼"
                else:
                    color = (200, 200, 200)
                    symbol = "="
                
                lines.append((f"  {symbol} {stat_display}: {change_data['old']} -> {change_data['new']} ({change:+})", color))
        else:
            lines.append(("No stat changes", (180, 180, 180)))
    elif is_equipped:
        lines.append(("This item is currently equipped", (100, 255, 100)))
    else:
        lines.append(("No item equipped in this slot", (180, 180, 180)))
        lines.append(("Equipping will add these stats!", (100, 255, 100)))
    
    return lines


def get_item_rarity_color(item):
    """Get the color for an item based on its rarity."""
    rarity_colors = {
        'common': (200, 200, 200),
        'uncommon': (100, 255, 100),
        'rare': (100, 100, 255),
        'epic': (200, 100, 255),
        'legendary': (255, 200, 50),
        'artifact': (255, 128, 0),
        'set': (255, 215, 0)
    }
    item_rarity = getattr(item, 'rarity', 'common')
    return rarity_colors.get(item_rarity, (200, 200, 200))


def is_item_equipped(item, player):
    """Check if an item is currently equipped."""
    if not hasattr(item, 'type'):
        return False
    
    # Check all equipment slots
    for slot_name, equipped_item in player.equipment.items():
        if equipped_item == item:
            return True
    return False


def get_font(name, size):
    """Get a pygame font with the specified name and size."""
    return get_cached_font(name, size)


def get_active_set_bonuses(player):
    """Detect and return active set bonuses from equipped items."""
    set_counts = {}
    set_items = {}
    
    # Count items per set
    for slot_name, item in player.equipment.items():
        if item and hasattr(item, 'set_name') and item.set_name:
            set_name = item.set_name
            if set_name not in set_counts:
                set_counts[set_name] = 0
                set_items[set_name] = []
            set_counts[set_name] += 1
            set_items[set_name].append(item)
    
    # Determine active bonuses (2-piece minimum)
    active_bonuses = {}
    for set_name, count in set_counts.items():
        if count >= 2:
            # Get set bonus from any item in the set
            item = set_items[set_name][0]
            if hasattr(item, 'set_bonus'):
                active_bonuses[set_name] = {
                    'count': count,
                    'bonus': item.set_bonus,
                    'items': set_items[set_name]
                }
    
    return active_bonuses


def should_auto_loot(item_rarity, min_rarity):
    """Check if an item should be auto-looted based on rarity filter."""
    rarity_values = {
        'common': 1,
        'uncommon': 2,
        'rare': 3,
        'epic': 4,
        'legendary': 5,
        'artifact': 6,
        'set': 6
    }
    
    item_value = rarity_values.get(item_rarity, 1)
    min_value = rarity_values.get(min_rarity, 1)
    
    return item_value >= min_value


def salvage_equipment(item, player):
    """Salvage equipment into crafting materials."""
    if not hasattr(item, 'rarity'):
        return False, "Cannot salvage this item"
    
    rarity = item.rarity
    item_name = getattr(item, 'name', 'Unknown')
    
    # Salvage rewards based on rarity
    salvage_table = {
        'common': {'fiber': 1, 'gold': 1},
        'uncommon': {'fiber': 2, 'gold': 3},
        'rare': {'fiber': 5, 'gold': 8},
        'epic': {'fiber': 10, 'gold': 20},
        'legendary': {'fiber': 20, 'gold': 50},
        'artifact': {'fiber': 30, 'gold': 100},
        'set': {'fiber': 15, 'gold': 40}
    }
    
    rewards = salvage_table.get(rarity, {'fiber': 1, 'gold': 1})
    
    # Give rewards
    for material, amount in rewards.items():
        if material == 'gold':
            player.dubloons += amount
        elif material in player.inventory:
            player.inventory[material] += amount
        else:
            player.inventory[material] = amount
    
    # Remove item from inventory
    player.remove_item(item)
    
    reward_text = ", ".join([f"{amt} {mat}" for mat, amt in rewards.items()])
    return True, f"Salvaged {item_name} -> {reward_text}"


def sort_inventory_items(items, sort_mode):
    """Sort inventory items based on the selected sort mode."""
    if not items or len(items) == 0:
        return items
    
    # Don't sort tuple items (old inventory format)
    if any(isinstance(item, tuple) for item in items):
        return items
    
    if sort_mode == 'rarity':
        # Sort by rarity (legendary > epic > rare > uncommon > common)
        rarity_order = {
            'artifact': 7,
            'set': 7,
            'legendary': 6,
            'epic': 5,
            'rare': 4,
            'uncommon': 3,
            'common': 2,
            'junk': 1
        }
        return sorted(items, key=lambda x: rarity_order.get(getattr(x, 'rarity', 'common'), 0), reverse=True)
    
    elif sort_mode == 'level':
        # Sort by level requirement (high to low)
        return sorted(items, key=lambda x: getattr(x, 'level_req', 0), reverse=True)
    
    elif sort_mode == 'value':
        # Sort by value (high to low)
        return sorted(items, key=lambda x: getattr(x, 'value', 0), reverse=True)
    
    elif sort_mode == 'type':
        # Sort by equipment type
        type_order = {
            'weapon': 1,
            'armor': 2,
            'accessory': 3,
            'consumable': 4,
            'material': 5,
            'quest': 6,
            'other': 7
        }
        return sorted(items, key=lambda x: type_order.get(getattr(x, 'type', 'other'), 99))
    
    else:  # 'default'
        return items


def random_color():
    """Generate a random RGB color tuple."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def random_name():
    """Generate a random character name from syllables."""
    syllables = ["ar", "en", "li", "ra", "do", "mi", "ka", "ze", "lo", "va", "si", "to", "na", "el", "ur"]
    return random.choice(syllables).capitalize() + random.choice(syllables) + random.choice(syllables)
