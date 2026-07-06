import json
import os
import random
from equipment import EQUIPMENT_DATA
from logger_config import get_logger

logger = get_logger(__name__)

def get_specific_equipment_id(generic_type):
    """Return a random specific equipment ID for a generic type (e.g., 'helmet')."""
    # Map generic loot types to actual equipment slots
    type_to_slot_mapping = {
        'sword': 'main_hand',
        'axe': 'main_hand',
        'bow': 'main_hand',
        'staff': 'main_hand',
        'helmet': 'head',
        'armor': 'chest',
        'boots': 'feet',
        'shield': 'off_hand',
        'gloves': 'hands',
        'ring': 'ring',
        'necklace': 'neck',
        'weapon': 'main_hand'
    }
    
    # Convert generic type to slot, or use as-is if already a slot name
    slot = type_to_slot_mapping.get(generic_type, generic_type)
    
    # Find all equipment matching this slot
    matches = [eid for eid, data in EQUIPMENT_DATA.items() if data.get("slot") == slot]
    
    # Also check for alternative slot names
    if not matches and slot == 'ring':
        matches = [eid for eid, data in EQUIPMENT_DATA.items() if data.get("slot") == 'finger']
    if not matches and slot == 'neck':
        matches = [eid for eid, data in EQUIPMENT_DATA.items() if data.get("slot") == 'necklace']
    if not matches and slot == 'feet':
        matches = [eid for eid, data in EQUIPMENT_DATA.items() if data.get("slot") == 'boots']
    if not matches and slot == 'head':
        matches = [eid for eid, data in EQUIPMENT_DATA.items() if data.get("slot") == 'helmet']
    if not matches and slot == 'hands':
        matches = [eid for eid, data in EQUIPMENT_DATA.items() if data.get("slot") == 'gloves']
    
    if matches:
        return random.choice(matches)
    
    logger.warning(f"No specific equipment found for type '{generic_type}' (mapped to slot '{slot}')")
    return None

# filepath: c:\Users\alexa\Myproject(3)\loot.py
LOOT_TABLE_PATH = os.path.join(os.path.dirname(__file__), "loot_tables.json")
with open(LOOT_TABLE_PATH, "r") as f:
    LOOT_TABLE = json.load(f)
    
def get_random_filler():
    return random.choice(LOOT_TABLE["filler_items"])

def get_random_consumable():
    return random.choice(LOOT_TABLE["consumables"])

def get_random_equipment_type():
    return random.choice(LOOT_TABLE["equipment_types"])

def get_random_equipment_rarity():
    return random.choice(LOOT_TABLE["equipment_rarities"])

def get_random_dubloon_amount(enemy_type):
    return random.choice(LOOT_TABLE["dubloon_amounts"].get(enemy_type, []))

def get_random_recipe_scroll():
    """Return a random recipe scroll from the loot table."""
    return random.choice(LOOT_TABLE["recipe_scrolls"])

def weighted_choice(choices):
    """
    choices: list of (item, weight) tuples
    Returns a randomly selected item based on weights.
    """
    total = sum(weight for item, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices:
        if upto + weight >= r:
            return item
        upto += weight
    return choices[-1][0]  # fallback

def get_regular_enemy_loot():
    # Always drop equipment, dubloons, and a filler item
    loot = []

    equipment_type = get_random_equipment_type()
    specific_equipment_id = get_specific_equipment_id(equipment_type)
    if specific_equipment_id:
        # Regular enemies use the rarity redistribution system in handle_enemy_drops
        equipment = {
            "type": specific_equipment_id,
            "rarity": "common"  # Base rarity, will be redistributed by handle_enemy_drops
        }
        loot.append(equipment)
    else:
        logger.warning(f"No specific equipment found for type '{equipment_type}'")

    # Dubloons (always 1-4)
    dubloon_amount = get_random_dubloon_amount("regular_enemy")
    loot.append({
        "type": "dubloon",
        "amount": dubloon_amount
    })

    # Filler item (random)
    filler = get_random_filler()
    # Recipe scroll (5% chance)
    if random.random() < LOOT_TABLE["regular_enemy"]["recipe_scroll"]:
        recipe_scroll = get_random_recipe_scroll()
        loot.append({
            "type": recipe_scroll
        })

    loot.append({
        "type": filler
    })

    return loot
    
def get_boss_loot():
    loot = []

    if random.random() < LOOT_TABLE["boss"]["regular_equipment"]:
        equipment_type = get_random_equipment_type()
        specific_equipment_id = get_specific_equipment_id(equipment_type)
        if specific_equipment_id:
            loot.append({
                "type": specific_equipment_id,
                "rarity": "rare"  # Boss regular equipment starts at rare
            })
        else:
            logger.warning(f"No specific equipment found for type '{equipment_type}'")

    # Consumable (30% chance)
    if random.random() < LOOT_TABLE["boss"]["consumable"]:
        loot.append({
            "type": get_random_consumable()
        })

    # Dubloons (always 50)
    loot.append({
        "type": "dubloon",
        "amount": LOOT_TABLE["dubloon_amounts"]["boss"][0]
    })

    # Recipe scroll (25% chance)
    if random.random() < LOOT_TABLE["boss"]["recipe_scroll"]:
        recipe_scroll = get_random_recipe_scroll()
        loot.append({
            "type": recipe_scroll
        })

    rare_roll = random.random()
    if rare_roll < LOOT_TABLE["boss"]["legendary_equipment"]:
        equipment_type = get_random_equipment_type()
        specific_equipment_id = get_specific_equipment_id(equipment_type)
        if specific_equipment_id:
            loot.append({
                "type": specific_equipment_id,
                "rarity": "legendary"
            })
        else:
            logger.warning(f"No specific equipment found for type '{equipment_type}'")
    elif rare_roll < LOOT_TABLE["boss"]["epic_equipment"] + LOOT_TABLE["boss"]["legendary_equipment"]:
        equipment_type = get_random_equipment_type()
        specific_equipment_id = get_specific_equipment_id(equipment_type)
        if specific_equipment_id:
            loot.append({
                "type": specific_equipment_id,
                "rarity": "epic"
            })
        else:
            logger.warning(f"No specific equipment found for type '{equipment_type}'")
    elif rare_roll < (LOOT_TABLE["boss"]["rare_equipment"] +
                    LOOT_TABLE["boss"]["epic_equipment"] +
                    LOOT_TABLE["boss"]["legendary_equipment"]):
        equipment_type = get_random_equipment_type()
        specific_equipment_id = get_specific_equipment_id(equipment_type)
        if specific_equipment_id:
            loot.append({
                "type": specific_equipment_id,
                "rarity": "rare"
            })
        else:
            logger.warning(f"No specific equipment found for type '{equipment_type}'")

    return loot

# Central list of all possible dungeon loot types
DUNGEON_LOOT_TYPES = (
    LOOT_TABLE["filler_items"] +
    LOOT_TABLE["consumables"] +
    LOOT_TABLE["recipe_scrolls"] +
    list(EQUIPMENT_DATA.keys()) +  # <-- Use actual equipment IDs
    ["dubloon"]
)