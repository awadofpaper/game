"""
Enhanced Item System Integration
Fixes crafting, consumables, and adds missing functionality
"""

import random
import time

def fix_consumable_items_integration():
    """Add missing crafted consumables to the main consumable system"""
    
    # This would be added to the consumable_items dictionary in thebestyet.py
    additional_consumables = {
        # Crafted elixirs (more powerful than basic potions)
        "health_elixir": {
            "heal": 75, 
            "message": "Used Health Elixir (+75 HP) - Enhanced healing!", 
            "craft_bonus": True
        },
        "mana_elixir": {
            "mana": 50, 
            "message": "Used Mana Elixir (+50 MP) - Enhanced restoration!", 
            "craft_bonus": True
        },
        "potion_of_swiftness": {
            "speed_boost": {"duration": 300, "multiplier": 1.5}, 
            "message": "Used Potion of Swiftness (+50% speed for 5 minutes)", 
            "craft_bonus": True
        },
        
        # Generic loot potions (weaker than crafted ones)
        "generic_potion": {
            "heal": 30, 
            "message": "Used Mysterious Potion (+30 HP)"
        },
        
        # Food items expansion
        "cheese": {
            "heal": 25, 
            "stamina": 10, 
            "message": "Ate Cheese (+25 HP, +10 Stamina)"
        },
        "meat": {
            "heal": 40, 
            "stamina": 15, 
            "message": "Ate Cooked Meat (+40 HP, +15 Stamina)"
        },
        "stew": {
            "heal": 60, 
            "stamina": 25, 
            "warmth": 5, 
            "message": "Ate Hearty Stew (+60 HP, +25 Stamina, Warmth)"
        },
        
        # Scroll items (single-use spells)
        "scroll_fireball": {
            "spell_cast": {"type": "fireball", "damage": 35}, 
            "message": "Cast Fireball from Scroll"
        },
        "scroll_healing": {
            "heal": 50, 
            "mana": 20, 
            "message": "Used Healing Scroll (+50 HP, +20 MP)"
        },
        "scroll_teleport": {
            "teleport": {"range": 5}, 
            "message": "Used Teleport Scroll"
        }
    }
    
    return additional_consumables

def create_enchantment_system():
    """Wood-based enchantment system for gear"""
    
    WOOD_ENCHANTMENTS = {
        "reinforcement": {
            "name": "Wooden Reinforcement",
            "ingredients": {"wood": 3, "fiber": 1},
            "effects": {"durability": 25, "defense": 2},
            "description": "Reinforces armor with wooden plates",
            "applicable_to": ["armor", "shield", "helmet"]
        },
        "grip_wrap": {
            "name": "Wooden Grip Wrap", 
            "ingredients": {"wood": 2, "ash": 1},
            "effects": {"accuracy": 5, "damage": 1},
            "description": "Wooden grip improves weapon handling",
            "applicable_to": ["weapon"]
        },
        "wooden_spikes": {
            "name": "Wooden Spikes",
            "ingredients": {"wood": 4, "stick": 2},
            "effects": {"thorns_damage": 3, "intimidation": 10},
            "description": "Wooden spikes deal damage to attackers",
            "applicable_to": ["armor", "shield"]
        }
    }
    
    return WOOD_ENCHANTMENTS

def create_basic_armor_recipes():
    """Fiber/wood/ash/stone/rubble armor crafting recipes"""
    
    ARMOR_RECIPES = {
        # Fiber armor (light, basic protection)
        "fiber_vest": {
            "ingredients": {"fiber": 8, "stick": 2},
            "unlock_level": 1,
            "type": "equipment",
            "equipment_data": {
                "name": "Fiber Vest",
                "type": "armor",
                "slot": "chest",
                "base_defense": 3,
                "stat_bonuses": {"Agility": 1},
                "rarity": "common",
                "weight": 2,
                "value": 8,
                "description": "Woven plant fibers provide basic protection"
            }
        },
        
        "fiber_boots": {
            "ingredients": {"fiber": 4, "ash": 1},
            "unlock_level": 1,
            "type": "equipment",
            "equipment_data": {
                "name": "Fiber Boots",
                "type": "armor", 
                "slot": "boots",
                "base_defense": 1,
                "stat_bonuses": {"Agility": 2},
                "rarity": "common",
                "weight": 1,
                "value": 5,
                "description": "Light woven boots for quiet movement"
            }
        },
        
        # Wood armor (medium protection)
        "wooden_breastplate": {
            "ingredients": {"wood": 6, "fiber": 3, "ash": 1},
            "unlock_level": 2,
            "type": "equipment",
            "equipment_data": {
                "name": "Wooden Breastplate",
                "type": "armor",
                "slot": "chest", 
                "base_defense": 8,
                "stat_bonuses": {"Defense": 2},
                "rarity": "common",
                "weight": 5,
                "value": 15,
                "description": "Carved wooden plates bound with fiber"
            }
        },
        
        # Stone armor (heavy protection)
        "stone_helm": {
            "ingredients": {"stone": 4, "fiber": 2, "ash": 1},
            "unlock_level": 3,
            "type": "equipment",
            "equipment_data": {
                "name": "Stone Helmet",
                "type": "armor",
                "slot": "helmet",
                "base_defense": 6,
                "stat_bonuses": {"Defense": 3, "Agility": -1},
                "rarity": "uncommon",
                "weight": 4,
                "value": 20,
                "description": "Heavy stone helm with fiber padding"
            }
        },
        
        "stone_gauntlets": {
            "ingredients": {"stone": 3, "rubble": 2, "fiber": 1},
            "unlock_level": 3,
            "type": "equipment",
            "equipment_data": {
                "name": "Stone Gauntlets",
                "type": "armor",
                "slot": "gloves",
                "base_defense": 4,
                "stat_bonuses": {"Strength": 2, "Agility": -1},
                "rarity": "uncommon", 
                "weight": 3,
                "value": 18,
                "description": "Stone-reinforced gloves for protection"
            }
        },
        
        # Rubble armor (makeshift but functional)
        "rubble_padding": {
            "ingredients": {"rubble": 6, "fiber": 4},
            "unlock_level": 1,
            "type": "equipment",
            "equipment_data": {
                "name": "Rubble Padding",
                "type": "armor",
                "slot": "chest",
                "base_defense": 5,
                "stat_bonuses": {"Defense": 1},
                "rarity": "common",
                "weight": 6,
                "value": 8,
                "description": "Makeshift armor from bound rubble pieces"
            }
        }
    }
    
    return ARMOR_RECIPES

def create_enhanced_crafting_integration():
    """Fix crafting system to actually create and use items properly"""
    
    def craft_item_properly(recipe_name, recipe_data, player, message_console):
        """Properly handle crafting with resource consumption and item creation"""
        
        # Check if player has all ingredients
        ingredients = recipe_data["ingredients"]
        for ingredient, amount in ingredients.items():
            if player.inventory.get(ingredient, 0) < amount:
                if message_console:
                    message_console.add_message(f"Need {amount} {ingredient} to craft {recipe_name}", color=(255, 100, 100))
                return False
        
        # Consume ingredients
        for ingredient, amount in ingredients.items():
            player.inventory.remove_item(ingredient, amount)
        
        # Create the item based on type
        if recipe_data.get("type") == "equipment":
            # Equipment crafting
            equipment_data = recipe_data.get("equipment_data", {})
            
            # Add to player's inventory as equipment
            if hasattr(player, 'inventory') and hasattr(player.inventory, 'items'):
                if recipe_name in player.inventory.items:
                    player.inventory.items[recipe_name] += 1
                else:
                    player.inventory.items[recipe_name] = 1
            
            if message_console:
                message_console.add_message(f"Crafted {equipment_data.get('name', recipe_name)}!", color=(100, 255, 100))
            
        else:
            # Consumable crafting
            if hasattr(player, 'inventory'):
                player.inventory.add_item(recipe_name, 1)
            
            if message_console:
                message_console.add_message(f"Crafted {recipe_name}!", color=(100, 255, 100))
        
        return True
    
    return craft_item_properly

def create_loot_table_fixes():
    """Fix generic loot drops to resolve to actual items"""
    
    LOOT_RESOLUTION = {
        "potion": ["generic_potion", "health_potion", "mana_potion"],
        "scroll": ["scroll_fireball", "scroll_healing", "scroll_teleport"], 
        "food": ["bread", "apple", "cheese", "meat"]
    }
    
    def resolve_generic_loot(generic_item):
        """Convert generic loot to specific items"""
        if generic_item in LOOT_RESOLUTION:
            return random.choice(LOOT_RESOLUTION[generic_item])
        return generic_item
    
    return resolve_generic_loot

def create_utility_mechanics():
    """Add actual utility mechanics for rope and other utility items"""
    
    UTILITY_MECHANICS = {
        "rope": {
            "climbing": True,
            "bridge_support": True, 
            "tying_enemies": True,
            "description": "Can be used for climbing, supporting bridges, or restraining"
        },
        "torch": {
            "light_radius": 3,
            "fire_damage": 2,
            "description": "Provides light and can ignite flammable materials"
        },
        "pickaxe": {
            "mining_bonus": 2,
            "stone_breaking": True,
            "description": "Improved resource gathering from stone and ore"
        }
    }
    
    def use_utility_item(item_id, player, target_pos=None, message_console=None):
        """Handle utility item usage"""
        if item_id not in UTILITY_MECHANICS:
            return False
        
        utility = UTILITY_MECHANICS[item_id]
        
        if item_id == "rope":
            # Example: Use rope for climbing (could extend to actual climbing mechanics)
            if not hasattr(player, 'climbing_gear'):
                player.climbing_gear = {}
            player.climbing_gear[item_id] = True
            
            if message_console:
                message_console.add_message("Rope equipped - you can now climb difficult terrain", color=(100, 255, 100))
            return True
        
        elif item_id == "torch":
            # Add light source
            if not hasattr(player, 'light_sources'):
                player.light_sources = {}
            player.light_sources[item_id] = utility["light_radius"]
            
            if message_console:
                message_console.add_message("Torch lit - provides light in dark areas", color=(255, 200, 100))
            return True
        
        return False
    
    return use_utility_item

# Integration recommendations
INTEGRATION_RECOMMENDATIONS = {
    "bridge_building": {
        "description": "Add bridge building mode with B key",
        "implementation": "Hold B + left click to place bridge material at cursor",
        "controls": "B + Wood/Fiber/Stone number key to select material"
    },
    
    "enchantment_workshop": {
        "description": "Add enchantment station to crafting menu", 
        "implementation": "New crafting tab for enchantments using wood + other materials",
        "integration": "Enchant existing equipped items to add bonuses"
    },
    
    "improved_crafting": {
        "description": "Fix crafting to actually consume resources and create items",
        "implementation": "Replace current crafting logic with proper resource checking",
        "validation": "Ensure crafted items appear in inventory and work when used"
    },
    
    "loot_system_fix": {
        "description": "Fix generic loot drops to resolve to real items",
        "implementation": "Add resolution system for 'potion', 'scroll', 'food' drops",
        "expansion": "Add more specific food and scroll types"
    }
}