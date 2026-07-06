"""
Crafting system for the RPG game.
Defines recipes and handles crafting logic with recipe discovery system.
"""

import pygame
from logger_config import get_logger

logger = get_logger(__name__)

class CraftingRecipe:
    """Represents a single crafting recipe"""
    def __init__(self, name, ingredients, result, result_count=1, category="General", recipe_id=None, auto_discover=False):
        self.name = name  # Display name of the recipe
        self.ingredients = ingredients  # Dict of {item_name: count}
        self.result = result  # Item name to create
        self.result_count = result_count  # How many items to create
        self.category = category  # Recipe category for organization
        self.recipe_id = recipe_id or result  # Unique identifier for this recipe
        self.auto_discover = auto_discover  # If True, recipe is available from the start
        
    def can_craft(self, player_inventory, player=None):
        """Check if player has all required ingredients"""
        for item, count in self.ingredients.items():
            if player_inventory.get(item, 0) < count:
                return False
        return True
    
    def craft(self, player_inventory, player=None):
        """Consume ingredients and add result to inventory"""
        if not self.can_craft(player_inventory, player):
            return False
        
        # Consume ingredients
        for item, count in self.ingredients.items():
            player_inventory[item] -= count
        
        # Add result
        player_inventory[self.result] = player_inventory.get(self.result, 0) + self.result_count
        return True


# Define all crafting recipes
CRAFTING_RECIPES = [
    # Tools & Weapons
    CraftingRecipe(
        name="Wooden Sword",
        ingredients={"wood": 2},
        result="wooden_sword",
        category="Weapons",
        recipe_id="wooden_sword",
        auto_discover=True  # Basic starter recipe
    ),
    CraftingRecipe(
        name="Wooden Shield",
        ingredients={"wood": 4, "fiber": 2},
        result="wooden_shield",
        category="Equipment",
        recipe_id="wooden_shield"
    ),
    CraftingRecipe(
        name="Wooden Bow",
        ingredients={"wood": 3, "fiber": 5},
        result="wooden_bow",
        category="Weapons",
        recipe_id="wooden_bow"
    ),
    
    # Basic Items
    CraftingRecipe(
        name="Rope",
        ingredients={"fiber": 5},
        result="rope",
        result_count=1,
        category="Materials",
        recipe_id="rope",
        auto_discover=True  # Basic starter recipe
    ),
    CraftingRecipe(
        name="Bandage",
        ingredients={"fiber": 3},
        result="bandage",
        result_count=2,
        category="Consumables",
        recipe_id="bandage",
        auto_discover=True  # Basic starter recipe
    ),
    CraftingRecipe(
        name="Torch",
        ingredients={"wood": 1, "fiber": 2},
        result="torch",
        result_count=3,
        category="Tools",
        recipe_id="torch",
        auto_discover=True  # Basic starter recipe
    ),
    CraftingRecipe(
        name="Campfire",
        ingredients={"wood": 5, "fiber": 3},
        result="campfire",
        category="Tools",
        recipe_id="campfire"
    ),
    
    # Utility
    CraftingRecipe(
        name="Backpack",
        ingredients={"fiber": 10, "rope": 2},
        result="backpack",
        category="Equipment",
        recipe_id="backpack"
    ),
    
    # Crafting Materials - Potions (using herbs)
    CraftingRecipe(
        name="Antidote",
        ingredients={"herbs": 2, "apple": 1},
        result="antidote",
        result_count=1,
        category="Consumables",
        recipe_id="antidote"
    ),
    CraftingRecipe(
        name="Strength Potion",
        ingredients={"herbs": 3, "berries": 2},
        result="strength_potion",
        result_count=1,
        category="Consumables",
        recipe_id="strength_potion"
    ),
    CraftingRecipe(
        name="Defense Potion",
        ingredients={"herbs": 3, "mushroom": 1},
        result="defense_potion",
        result_count=1,
        category="Consumables",
        recipe_id="defense_potion"
    ),
    CraftingRecipe(
        name="Stamina Potion",
        ingredients={"herbs": 2, "berries": 1},
        result="stamina_potion",
        result_count=1,
        category="Consumables",
        recipe_id="stamina_potion"
    ),
    
    # Ore-based crafting
    CraftingRecipe(
        name="Iron Sword",
        ingredients={"ore": 3, "wood": 1},
        result="iron_sword",
        category="Weapons",
        recipe_id="iron_sword"
    ),
    CraftingRecipe(
        name="Iron Armor",
        ingredients={"ore": 5, "cloth": 2},
        result="iron_armor",
        category="Equipment",
        recipe_id="iron_armor"
    ),
    CraftingRecipe(
        name="Lockpick",
        ingredients={"ore": 1, "wood": 1},
        result="lockpick",
        result_count=3,
        category="Tools",
        recipe_id="lockpick"
    ),
    
    # Cloth-based crafting
    CraftingRecipe(
        name="Cloth Armor",
        ingredients={"cloth": 4, "fiber": 3},
        result="cloth_armor",
        category="Equipment",
        recipe_id="cloth_armor"
    ),
    CraftingRecipe(
        name="Bandana",
        ingredients={"cloth": 2},
        result="bandana",
        category="Equipment",
        recipe_id="bandana"
    ),
    CraftingRecipe(
        name="Bag",
        ingredients={"cloth": 3, "rope": 1},
        result="bag",
        category="Equipment",
        recipe_id="bag"
    ),
    
    # Bones-based crafting
    CraftingRecipe(
        name="Bone Dagger",
        ingredients={"bones": 2, "fiber": 1},
        result="bone_dagger",
        category="Weapons",
        recipe_id="bone_dagger"
    ),
    CraftingRecipe(
        name="Bone Armor",
        ingredients={"bones": 4, "cloth": 1},
        result="bone_armor",
        category="Equipment",
        recipe_id="bone_armor"
    ),
    CraftingRecipe(
        name="Bone Charm",
        ingredients={"bones": 3, "fiber": 2},
        result="bone_charm",
        category="Accessories",
        recipe_id="bone_charm"
    ),
    
    # Advanced combinations
    CraftingRecipe(
        name="Bomb",
        ingredients={"ore": 2, "herbs": 1, "fiber": 1},
        result="bomb",
        result_count=2,
        category="Tools",
        recipe_id="bomb"
    ),
    
    # ==================== STICK-BASED CRAFTING ====================
    # Weapons - Basic Tier
    CraftingRecipe(
        name="Wooden Spear",
        ingredients={"stick": 3, "fiber": 1},
        result="wooden_spear",
        category="Weapons",
        recipe_id="wooden_spear",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Wooden Club",
        ingredients={"stick": 4, "fiber": 2},
        result="wooden_club",
        category="Weapons",
        recipe_id="wooden_club",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Training Sword",
        ingredients={"stick": 2, "wood": 1, "fiber": 1},
        result="training_sword",
        category="Weapons",
        recipe_id="training_sword",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Sling",
        ingredients={"stick": 2, "fiber": 3},
        result="sling",
        category="Weapons",
        recipe_id="sling"
    ),
    
    # Weapons - Upgraded Tier
    CraftingRecipe(
        name="Quarterstaff",
        ingredients={"stick": 5, "ore": 1},
        result="quarterstaff",
        category="Weapons",
        recipe_id="quarterstaff"
    ),
    CraftingRecipe(
        name="Wooden Mace",
        ingredients={"stick": 3, "bones": 2, "fiber": 1},
        result="wooden_mace",
        category="Weapons",
        recipe_id="wooden_mace"
    ),
    CraftingRecipe(
        name="Javelin",
        ingredients={"stick": 2, "ore": 1},
        result="javelin",
        result_count=3,
        category="Weapons",
        recipe_id="javelin"
    ),
    CraftingRecipe(
        name="Reinforced Spear",
        ingredients={"stick": 4, "ore": 2, "fiber": 1},
        result="reinforced_spear",
        category="Weapons",
        recipe_id="reinforced_spear"
    ),
    
    # Armor - Basic Set
    CraftingRecipe(
        name="Wooden Pauldrons",
        ingredients={"stick": 3, "fiber": 2},
        result="wooden_pauldrons",
        category="Armor",
        recipe_id="wooden_pauldrons"
    ),
    CraftingRecipe(
        name="Wooden Bracers",
        ingredients={"stick": 2, "fiber": 1},
        result="wooden_bracers",
        category="Armor",
        recipe_id="wooden_bracers"
    ),
    CraftingRecipe(
        name="Wooden Mask",
        ingredients={"stick": 3, "cloth": 1},
        result="wooden_mask",
        category="Armor",
        recipe_id="wooden_mask"
    ),
    CraftingRecipe(
        name="Wooden Chest Guard",
        ingredients={"stick": 5, "fiber": 3},
        result="wooden_chest_guard",
        category="Armor",
        recipe_id="wooden_chest_guard"
    ),
    
    # Armor - Enhanced
    CraftingRecipe(
        name="Bone-Studded Wooden Armor",
        ingredients={"stick": 4, "bones": 3, "fiber": 2},
        result="bone_studded_wooden_armor",
        category="Armor",
        recipe_id="bone_studded_wooden_armor"
    ),
    CraftingRecipe(
        name="Forest Ranger Armor",
        ingredients={"stick": 6, "cloth": 3, "fiber": 2},
        result="forest_ranger_armor",
        category="Armor",
        recipe_id="forest_ranger_armor"
    ),
    
    # Accessories - Necklaces/Amulets
    CraftingRecipe(
        name="Wooden Charm Necklace",
        ingredients={"stick": 2, "fiber": 3},
        result="wooden_charm_necklace",
        category="Accessories",
        recipe_id="wooden_charm_necklace"
    ),
    CraftingRecipe(
        name="Branch Amulet",
        ingredients={"stick": 3, "herbs": 2},
        result="branch_amulet",
        category="Accessories",
        recipe_id="branch_amulet"
    ),
    CraftingRecipe(
        name="Bone & Wood Talisman",
        ingredients={"stick": 2, "bones": 3, "fiber": 1},
        result="bone_wood_talisman",
        category="Accessories",
        recipe_id="bone_wood_talisman"
    ),
    CraftingRecipe(
        name="Forest Blessing Pendant",
        ingredients={"stick": 4, "herbs": 2, "rope": 1},
        result="forest_blessing_pendant",
        category="Accessories",
        recipe_id="forest_blessing_pendant"
    ),
    
    # Accessories - Rings
    CraftingRecipe(
        name="Carved Wood Ring",
        ingredients={"stick": 1, "fiber": 2},
        result="carved_wood_ring",
        category="Accessories",
        recipe_id="carved_wood_ring"
    ),
    CraftingRecipe(
        name="Fiber-Wrapped Ring",
        ingredients={"stick": 1, "fiber": 3},
        result="fiber_wrapped_ring",
        category="Accessories",
        recipe_id="fiber_wrapped_ring"
    ),
    CraftingRecipe(
        name="Nature's Band",
        ingredients={"stick": 2, "herbs": 1},
        result="natures_band",
        category="Accessories",
        recipe_id="natures_band"
    ),
    
    # Enchantments & Magic Items
    CraftingRecipe(
        name="Wooden Wand",
        ingredients={"stick": 3, "herbs": 1, "fiber": 1},
        result="wooden_wand",
        category="Magic Items",
        recipe_id="wooden_wand"
    ),
    CraftingRecipe(
        name="Apprentice Staff",
        ingredients={"stick": 5, "herbs": 2, "cloth": 1},
        result="apprentice_staff",
        category="Magic Items",
        recipe_id="apprentice_staff"
    ),
    CraftingRecipe(
        name="Wooden Totem",
        ingredients={"stick": 4, "bones": 3, "fiber": 2},
        result="wooden_totem",
        category="Magic Items",
        recipe_id="wooden_totem"
    ),
    CraftingRecipe(
        name="Rune-Carved Stick",
        ingredients={"stick": 2, "ore": 1, "herbs": 1},
        result="rune_carved_stick",
        category="Magic Items",
        recipe_id="rune_carved_stick"
    ),
    CraftingRecipe(
        name="Nature Spirit Charm",
        ingredients={"stick": 3, "herbs": 3, "bones": 1},
        result="nature_spirit_charm",
        category="Magic Items",
        recipe_id="nature_spirit_charm"
    ),
    CraftingRecipe(
        name="Druid's Focus",
        ingredients={"stick": 4, "herbs": 2, "cloth": 2},
        result="druids_focus",
        category="Magic Items",
        recipe_id="druids_focus"
    ),
    
    # Utility & Tools
    CraftingRecipe(
        name="Reinforced Torch",
        ingredients={"stick": 2, "fiber": 1, "ore": 1},
        result="reinforced_torch",
        result_count=5,
        category="Tools",
        recipe_id="reinforced_torch"
    ),
    CraftingRecipe(
        name="Fishing Rod",
        ingredients={"stick": 3, "fiber": 5},
        result="fishing_rod",
        category="Tools",
        recipe_id="fishing_rod"
    ),
    CraftingRecipe(
        name="Bear Trap",
        ingredients={"stick": 4, "ore": 2, "rope": 1},
        result="bear_trap",
        category="Tools",
        recipe_id="bear_trap"
    ),
    CraftingRecipe(
        name="Wooden Ladder",
        ingredients={"stick": 6, "fiber": 2},
        result="wooden_ladder",
        result_count=3,
        category="Tools",
        recipe_id="wooden_ladder"
    ),
    CraftingRecipe(
        name="Sign Post",
        ingredients={"stick": 2, "wood": 1},
        result="sign_post",
        category="Tools",
        recipe_id="sign_post"
    ),
    CraftingRecipe(
        name="Walking Stick",
        ingredients={"stick": 2, "fiber": 1},
        result="walking_stick",
        category="Tools",
        recipe_id="walking_stick"
    ),
    CraftingRecipe(
        name="Wooden Barricade",
        ingredients={"stick": 8, "fiber": 4},
        result="wooden_barricade",
        category="Tools",
        recipe_id="wooden_barricade"
    ),
    
    # Crafting Stations & Furniture
    CraftingRecipe(
        name="Basic Workbench",
        ingredients={"stick": 10, "wood": 5, "fiber": 2},
        result="basic_workbench",
        category="Furniture",
        recipe_id="basic_workbench"
    ),
    CraftingRecipe(
        name="Drying Rack",
        ingredients={"stick": 6, "fiber": 4},
        result="drying_rack",
        category="Furniture",
        recipe_id="drying_rack"
    ),
    CraftingRecipe(
        name="Weapon Rack",
        ingredients={"stick": 4, "wood": 2},
        result="weapon_rack",
        category="Furniture",
        recipe_id="weapon_rack"
    ),
    CraftingRecipe(
        name="Wooden Chair",
        ingredients={"stick": 5, "wood": 3},
        result="wooden_chair",
        category="Furniture",
        recipe_id="wooden_chair"
    ),
    
    # ==================== POTIONS & ELIXIRS ====================
    # Health/Mana Potions
    CraftingRecipe(
        name="Minor Health Potion",
        ingredients={"herbs": 1, "berries": 1},
        result="minor_health_potion",
        category="Consumables",
        recipe_id="minor_health_potion",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Health Potion",
        ingredients={"herbs": 3, "berries": 2},
        result="health_potion",
        category="Consumables",
        recipe_id="health_potion"
    ),
    CraftingRecipe(
        name="Greater Health Potion",
        ingredients={"herbs": 5, "mushroom": 2, "berries": 3},
        result="greater_health_potion",
        category="Consumables",
        recipe_id="greater_health_potion"
    ),
    CraftingRecipe(
        name="Minor Mana Potion",
        ingredients={"herbs": 2, "mushroom": 1},
        result="minor_mana_potion",
        category="Consumables",
        recipe_id="minor_mana_potion",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Mana Potion",
        ingredients={"herbs": 4, "mushroom": 2},
        result="mana_potion",
        category="Consumables",
        recipe_id="mana_potion"
    ),
    CraftingRecipe(
        name="Greater Mana Potion",
        ingredients={"herbs": 6, "mushroom": 3, "berries": 1},
        result="greater_mana_potion",
        category="Consumables",
        recipe_id="greater_mana_potion"
    ),
    
    # Buff Potions
    CraftingRecipe(
        name="Speed Elixir",
        ingredients={"herbs": 2, "berries": 3, "fiber": 1},
        result="speed_elixir",
        category="Consumables",
        recipe_id="speed_elixir"
    ),
    CraftingRecipe(
        name="Fire Resistance Potion",
        ingredients={"herbs": 3, "ore": 1, "mushroom": 1},
        result="fire_resistance_potion",
        category="Consumables",
        recipe_id="fire_resistance_potion"
    ),
    CraftingRecipe(
        name="Ice Resistance Potion",
        ingredients={"herbs": 3, "berries": 2},
        result="ice_resistance_potion",
        category="Consumables",
        recipe_id="ice_resistance_potion"
    ),
    CraftingRecipe(
        name="Invisibility Potion",
        ingredients={"herbs": 5, "mushroom": 3, "cloth": 1},
        result="invisibility_potion",
        category="Consumables",
        recipe_id="invisibility_potion"
    ),
    CraftingRecipe(
        name="Night Vision Elixir",
        ingredients={"herbs": 2, "mushroom": 2},
        result="night_vision_elixir",
        category="Consumables",
        recipe_id="night_vision_elixir"
    ),
    CraftingRecipe(
        name="Water Breathing Potion",
        ingredients={"herbs": 3, "fish": 2},
        result="water_breathing_potion",
        category="Consumables",
        recipe_id="water_breathing_potion"
    ),
    CraftingRecipe(
        name="Regeneration Elixir",
        ingredients={"herbs": 4, "berries": 3, "bones": 1},
        result="regeneration_elixir",
        category="Consumables",
        recipe_id="regeneration_elixir"
    ),
    CraftingRecipe(
        name="Mana Regeneration Elixir",
        ingredients={"herbs": 4, "mushroom": 3},
        result="mana_regeneration_elixir",
        category="Consumables",
        recipe_id="mana_regeneration_elixir"
    ),
    CraftingRecipe(
        name="Fortitude Potion",
        ingredients={"ore": 1, "herbs": 3, "bones": 2},
        result="fortitude_potion",
        category="Consumables",
        recipe_id="fortitude_potion"
    ),
    CraftingRecipe(
        name="Clarity Potion",
        ingredients={"mushroom": 3, "herbs": 2},
        result="clarity_potion",
        category="Consumables",
        recipe_id="clarity_potion"
    ),
    
    # Utility Potions
    CraftingRecipe(
        name="Poison Antidote",
        ingredients={"herbs": 3, "apple": 2},
        result="poison_antidote",
        category="Consumables",
        recipe_id="poison_antidote"
    ),
    CraftingRecipe(
        name="Cure Disease Potion",
        ingredients={"herbs": 4, "mushroom": 2, "berries": 1},
        result="cure_disease_potion",
        category="Consumables",
        recipe_id="cure_disease_potion"
    ),
    CraftingRecipe(
        name="Stoneskin Potion",
        ingredients={"ore": 2, "herbs": 3, "bones": 1},
        result="stoneskin_potion",
        category="Consumables",
        recipe_id="stoneskin_potion"
    ),
    
    # ==================== WEAPONS - ADVANCED ====================
    # Melee Weapons
    CraftingRecipe(
        name="Steel Sword",
        ingredients={"ore": 5, "wood": 2, "cloth": 1},
        result="steel_sword",
        category="Weapons",
        recipe_id="steel_sword"
    ),
    CraftingRecipe(
        name="Battle Axe",
        ingredients={"ore": 4, "wood": 3},
        result="battle_axe",
        category="Weapons",
        recipe_id="battle_axe"
    ),
    CraftingRecipe(
        name="War Hammer",
        ingredients={"ore": 6, "wood": 2, "fiber": 1},
        result="war_hammer",
        category="Weapons",
        recipe_id="war_hammer"
    ),
    CraftingRecipe(
        name="Dagger",
        ingredients={"ore": 2, "fiber": 1},
        result="dagger",
        category="Weapons",
        recipe_id="dagger"
    ),
    CraftingRecipe(
        name="Scimitar",
        ingredients={"ore": 4, "cloth": 2},
        result="scimitar",
        category="Weapons",
        recipe_id="scimitar"
    ),
    CraftingRecipe(
        name="Greatsword",
        ingredients={"ore": 8, "wood": 3, "cloth": 2},
        result="greatsword",
        category="Weapons",
        recipe_id="greatsword"
    ),
    CraftingRecipe(
        name="Flail",
        ingredients={"ore": 3, "wood": 2, "rope": 2},
        result="flail",
        category="Weapons",
        recipe_id="flail"
    ),
    
    # Ranged Weapons
    CraftingRecipe(
        name="Crossbow",
        ingredients={"wood": 5, "ore": 3, "fiber": 4},
        result="crossbow",
        category="Weapons",
        recipe_id="crossbow"
    ),
    CraftingRecipe(
        name="Longbow",
        ingredients={"wood": 6, "fiber": 8, "rope": 1},
        result="longbow",
        category="Weapons",
        recipe_id="longbow"
    ),
    CraftingRecipe(
        name="Arrows",
        ingredients={"wood": 1, "ore": 1, "fiber": 1},
        result="arrows",
        result_count=20,
        category="Ammunition",
        recipe_id="arrows"
    ),
    CraftingRecipe(
        name="Fire Arrows",
        ingredients={"wood": 1, "ore": 1, "fiber": 1, "herbs": 2},
        result="fire_arrows",
        result_count=10,
        category="Ammunition",
        recipe_id="fire_arrows"
    ),
    CraftingRecipe(
        name="Poison Arrows",
        ingredients={"wood": 1, "ore": 1, "fiber": 1, "mushroom": 2},
        result="poison_arrows",
        result_count=10,
        category="Ammunition",
        recipe_id="poison_arrows"
    ),
    CraftingRecipe(
        name="Bolts",
        ingredients={"ore": 2, "wood": 1},
        result="bolts",
        result_count=15,
        category="Ammunition",
        recipe_id="bolts"
    ),
    
    # ==================== SHIELDS ====================
    CraftingRecipe(
        name="Iron Shield",
        ingredients={"ore": 5, "wood": 2},
        result="iron_shield",
        category="Shields",
        recipe_id="iron_shield"
    ),
    CraftingRecipe(
        name="Steel Shield",
        ingredients={"ore": 8, "wood": 2, "cloth": 1},
        result="steel_shield",
        category="Shields",
        recipe_id="steel_shield"
    ),
    CraftingRecipe(
        name="Buckler",
        ingredients={"ore": 3, "fiber": 2},
        result="buckler",
        category="Shields",
        recipe_id="buckler"
    ),
    CraftingRecipe(
        name="Kite Shield",
        ingredients={"ore": 6, "wood": 3, "cloth": 2},
        result="kite_shield",
        category="Shields",
        recipe_id="kite_shield"
    ),
    CraftingRecipe(
        name="Tower Shield",
        ingredients={"ore": 10, "wood": 4, "cloth": 3},
        result="tower_shield",
        category="Shields",
        recipe_id="tower_shield"
    ),
    
    # ==================== HELMETS ====================
    CraftingRecipe(
        name="Leather Cap",
        ingredients={"cloth": 3, "fiber": 2},
        result="leather_cap",
        category="Armor",
        recipe_id="leather_cap"
    ),
    CraftingRecipe(
        name="Iron Helmet",
        ingredients={"ore": 4, "cloth": 1},
        result="iron_helmet",
        category="Armor",
        recipe_id="iron_helmet"
    ),
    CraftingRecipe(
        name="Steel Helmet",
        ingredients={"ore": 6, "cloth": 2},
        result="steel_helmet",
        category="Armor",
        recipe_id="steel_helmet"
    ),
    CraftingRecipe(
        name="Bone Helmet",
        ingredients={"bones": 5, "fiber": 2},
        result="bone_helmet",
        category="Armor",
        recipe_id="bone_helmet"
    ),
    CraftingRecipe(
        name="Cloth Hood",
        ingredients={"cloth": 3, "fiber": 1},
        result="cloth_hood",
        category="Armor",
        recipe_id="cloth_hood"
    ),
    CraftingRecipe(
        name="Chainmail Coif",
        ingredients={"ore": 5, "cloth": 1},
        result="chainmail_coif",
        category="Armor",
        recipe_id="chainmail_coif"
    ),
    
    # ==================== BOOTS/LEGS ====================
    CraftingRecipe(
        name="Leather Boots",
        ingredients={"cloth": 4, "fiber": 2},
        result="leather_boots",
        category="Armor",
        recipe_id="leather_boots"
    ),
    CraftingRecipe(
        name="Iron Boots",
        ingredients={"ore": 5, "cloth": 2},
        result="iron_boots",
        category="Armor",
        recipe_id="iron_boots"
    ),
    CraftingRecipe(
        name="Steel Greaves",
        ingredients={"ore": 7, "cloth": 3},
        result="steel_greaves",
        category="Armor",
        recipe_id="steel_greaves"
    ),
    CraftingRecipe(
        name="Cloth Pants",
        ingredients={"cloth": 5, "fiber": 2},
        result="cloth_pants",
        category="Armor",
        recipe_id="cloth_pants"
    ),
    CraftingRecipe(
        name="Leather Leggings",
        ingredients={"cloth": 6, "fiber": 3},
        result="leather_leggings",
        category="Armor",
        recipe_id="leather_leggings"
    ),
    CraftingRecipe(
        name="Chainmail Leggings",
        ingredients={"ore": 6, "cloth": 2},
        result="chainmail_leggings",
        category="Armor",
        recipe_id="chainmail_leggings"
    ),
    
    # ==================== GLOVES/HANDS ====================
    CraftingRecipe(
        name="Leather Gloves",
        ingredients={"cloth": 3, "fiber": 2},
        result="leather_gloves",
        category="Armor",
        recipe_id="leather_gloves"
    ),
    CraftingRecipe(
        name="Iron Gauntlets",
        ingredients={"ore": 4, "cloth": 1},
        result="iron_gauntlets",
        category="Armor",
        recipe_id="iron_gauntlets"
    ),
    CraftingRecipe(
        name="Steel Gauntlets",
        ingredients={"ore": 6, "cloth": 2},
        result="steel_gauntlets",
        category="Armor",
        recipe_id="steel_gauntlets"
    ),
    CraftingRecipe(
        name="Fingerless Gloves",
        ingredients={"cloth": 2, "fiber": 1},
        result="fingerless_gloves",
        category="Armor",
        recipe_id="fingerless_gloves"
    ),
    CraftingRecipe(
        name="Archer's Gloves",
        ingredients={"cloth": 3, "fiber": 3},
        result="archers_gloves",
        category="Armor",
        recipe_id="archers_gloves"
    ),
    
    # ==================== UNDER-ARMOR/PADDING ====================
    CraftingRecipe(
        name="Gambeson",
        ingredients={"cloth": 8, "fiber": 5},
        result="gambeson",
        category="Armor",
        recipe_id="gambeson"
    ),
    CraftingRecipe(
        name="Padded Tunic",
        ingredients={"cloth": 5, "fiber": 3},
        result="padded_tunic",
        category="Armor",
        recipe_id="padded_tunic"
    ),
    CraftingRecipe(
        name="Cloth Shirt",
        ingredients={"cloth": 3, "fiber": 1},
        result="cloth_shirt",
        category="Armor",
        recipe_id="cloth_shirt",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Leather Padding",
        ingredients={"cloth": 6, "fiber": 4},
        result="leather_padding",
        category="Armor",
        recipe_id="leather_padding"
    ),
    CraftingRecipe(
        name="Chainmail Shirt",
        ingredients={"ore": 8, "cloth": 2},
        result="chainmail_shirt",
        category="Armor",
        recipe_id="chainmail_shirt"
    ),
    
    # ==================== JEWELRY/ACCESSORIES ====================
    # Rings
    CraftingRecipe(
        name="Iron Ring",
        ingredients={"ore": 2, "fiber": 1},
        result="iron_ring",
        category="Accessories",
        recipe_id="iron_ring"
    ),
    CraftingRecipe(
        name="Silver Ring",
        ingredients={"ore": 3},
        result="silver_ring",
        category="Accessories",
        recipe_id="silver_ring"
    ),
    CraftingRecipe(
        name="Gold Ring",
        ingredients={"ore": 5},
        result="gold_ring",
        category="Accessories",
        recipe_id="gold_ring"
    ),
    CraftingRecipe(
        name="Emerald Ring",
        ingredients={"ore": 3, "herbs": 5},
        result="emerald_ring",
        category="Accessories",
        recipe_id="emerald_ring"
    ),
    CraftingRecipe(
        name="Ruby Ring",
        ingredients={"ore": 3, "berries": 5},
        result="ruby_ring",
        category="Accessories",
        recipe_id="ruby_ring"
    ),
    CraftingRecipe(
        name="Sapphire Ring",
        ingredients={"ore": 3, "mushroom": 5},
        result="sapphire_ring",
        category="Accessories",
        recipe_id="sapphire_ring"
    ),
    
    # Necklaces
    CraftingRecipe(
        name="Bone Necklace",
        ingredients={"bones": 4, "fiber": 2},
        result="bone_necklace",
        category="Accessories",
        recipe_id="bone_necklace"
    ),
    CraftingRecipe(
        name="Cloth Scarf",
        ingredients={"cloth": 4, "fiber": 1},
        result="cloth_scarf",
        category="Accessories",
        recipe_id="cloth_scarf"
    ),
    CraftingRecipe(
        name="Iron Chain",
        ingredients={"ore": 4, "fiber": 1},
        result="iron_chain",
        category="Accessories",
        recipe_id="iron_chain"
    ),
    CraftingRecipe(
        name="Herb Sachet",
        ingredients={"herbs": 6, "cloth": 2, "fiber": 1},
        result="herb_sachet",
        category="Accessories",
        recipe_id="herb_sachet"
    ),
    CraftingRecipe(
        name="Lucky Charm",
        ingredients={"bones": 3, "cloth": 2, "berries": 2},
        result="lucky_charm",
        category="Accessories",
        recipe_id="lucky_charm"
    ),
    
    # Amulets
    CraftingRecipe(
        name="Protection Amulet",
        ingredients={"ore": 4, "cloth": 3, "bones": 2},
        result="protection_amulet",
        category="Accessories",
        recipe_id="protection_amulet"
    ),
    CraftingRecipe(
        name="Wisdom Amulet",
        ingredients={"mushroom": 5, "cloth": 3, "herbs": 2},
        result="wisdom_amulet",
        category="Accessories",
        recipe_id="wisdom_amulet"
    ),
    CraftingRecipe(
        name="Speed Amulet",
        ingredients={"berries": 5, "cloth": 3, "fiber": 4},
        result="speed_amulet",
        category="Accessories",
        recipe_id="speed_amulet"
    ),
    
    # ==================== ENCHANTMENTS & RUNES ====================
    CraftingRecipe(
        name="Minor Sharpening Stone",
        ingredients={"ore": 3, "fiber": 1},
        result="minor_sharpening_stone",
        category="Enchantments",
        recipe_id="minor_sharpening_stone"
    ),
    CraftingRecipe(
        name="Sharpening Stone",
        ingredients={"ore": 5, "fiber": 2},
        result="sharpening_stone",
        category="Enchantments",
        recipe_id="sharpening_stone"
    ),
    CraftingRecipe(
        name="Armor Polish",
        ingredients={"ore": 3, "cloth": 2},
        result="armor_polish",
        category="Enchantments",
        recipe_id="armor_polish"
    ),
    CraftingRecipe(
        name="Fire Rune",
        ingredients={"ore": 5, "herbs": 3, "mushroom": 2},
        result="fire_rune",
        category="Enchantments",
        recipe_id="fire_rune"
    ),
    CraftingRecipe(
        name="Ice Rune",
        ingredients={"ore": 5, "berries": 3, "mushroom": 2},
        result="ice_rune",
        category="Enchantments",
        recipe_id="ice_rune"
    ),
    CraftingRecipe(
        name="Lightning Rune",
        ingredients={"ore": 6, "mushroom": 4},
        result="lightning_rune",
        category="Enchantments",
        recipe_id="lightning_rune"
    ),
    CraftingRecipe(
        name="Protection Rune",
        ingredients={"ore": 5, "bones": 3, "cloth": 2},
        result="protection_rune",
        category="Enchantments",
        recipe_id="protection_rune"
    ),
    CraftingRecipe(
        name="Fortification Rune",
        ingredients={"ore": 8, "bones": 4},
        result="fortification_rune",
        category="Enchantments",
        recipe_id="fortification_rune"
    ),
    CraftingRecipe(
        name="Enchanted Thread",
        ingredients={"cloth": 4, "herbs": 5, "mushroom": 3},
        result="enchanted_thread",
        category="Enchantments",
        recipe_id="enchanted_thread"
    ),
    
    # ==================== FOOD CRAFTING ====================
    CraftingRecipe(
        name="Cooked Meat",
        ingredients={"meat": 1},
        result="cooked_meat",
        category="Food",
        recipe_id="cooked_meat",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Cooked Fish",
        ingredients={"fish": 1},
        result="cooked_fish",
        category="Food",
        recipe_id="cooked_fish",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Berry Pie",
        ingredients={"berries": 5, "cloth": 1},
        result="berry_pie",
        category="Food",
        recipe_id="berry_pie"
    ),
    CraftingRecipe(
        name="Mushroom Stew",
        ingredients={"mushroom": 3, "berries": 2},
        result="mushroom_stew",
        category="Food",
        recipe_id="mushroom_stew"
    ),
    CraftingRecipe(
        name="Apple Cider",
        ingredients={"apple": 4, "berries": 2},
        result="apple_cider",
        category="Food",
        recipe_id="apple_cider"
    ),
    CraftingRecipe(
        name="Trail Mix",
        ingredients={"berries": 3, "apple": 2, "mushroom": 1},
        result="trail_mix",
        category="Food",
        recipe_id="trail_mix"
    ),
    CraftingRecipe(
        name="Herb Tea",
        ingredients={"herbs": 2},
        result="herb_tea",
        category="Food",
        recipe_id="herb_tea"
    ),
    CraftingRecipe(
        name="Ration Pack",
        ingredients={"meat": 2, "berries": 3, "cloth": 1},
        result="ration_pack",
        result_count=3,
        category="Food",
        recipe_id="ration_pack"
    ),
    
    # ==================== ADVANCED MATERIALS ====================
    CraftingRecipe(
        name="Leather",
        ingredients={"cloth": 3, "fiber": 2},
        result="leather",
        category="Materials",
        recipe_id="leather"
    ),
    CraftingRecipe(
        name="Thread",
        ingredients={"fiber": 3},
        result="thread",
        category="Materials",
        recipe_id="thread",
        auto_discover=True
    ),
    CraftingRecipe(
        name="Glue",
        ingredients={"bones": 2, "berries": 1},
        result="glue",
        category="Materials",
        recipe_id="glue"
    ),
    CraftingRecipe(
        name="Charcoal",
        ingredients={"wood": 5},
        result="charcoal",
        category="Materials",
        recipe_id="charcoal"
    ),
    CraftingRecipe(
        name="Glass",
        ingredients={"ore": 4},
        result="glass",
        category="Materials",
        recipe_id="glass"
    ),
    CraftingRecipe(
        name="Nails",
        ingredients={"ore": 2},
        result="nails",
        category="Materials",
        recipe_id="nails"
    ),
    CraftingRecipe(
        name="Steel Ingot",
        ingredients={"ore": 8, "charcoal": 3},
        result="steel_ingot",
        category="Materials",
        recipe_id="steel_ingot"
    ),
    CraftingRecipe(
        name="Bronze Ingot",
        ingredients={"ore": 6, "ore": 2},
        result="bronze_ingot",
        category="Materials",
        recipe_id="bronze_ingot"
    ),
    
    # ==================== UTILITY & SPECIAL ITEMS ====================
    CraftingRecipe(
        name="Grappling Hook",
        ingredients={"ore": 5, "rope": 3, "fiber": 2},
        result="grappling_hook",
        category="Tools",
        recipe_id="grappling_hook"
    ),
    CraftingRecipe(
        name="Lockpick Set",
        ingredients={"ore": 3, "wood": 2},
        result="lockpick_set",
        category="Tools",
        recipe_id="lockpick_set"
    ),
    CraftingRecipe(
        name="Spyglass",
        ingredients={"ore": 4, "glass": 2, "wood": 1},
        result="spyglass",
        category="Tools",
        recipe_id="spyglass"
    ),
    CraftingRecipe(
        name="Compass",
        ingredients={"ore": 4, "glass": 1},
        result="compass",
        category="Tools",
        recipe_id="compass"
    ),
    CraftingRecipe(
        name="Map",
        ingredients={"cloth": 3, "charcoal": 1},
        result="map",
        category="Tools",
        recipe_id="map"
    ),
    CraftingRecipe(
        name="Tent",
        ingredients={"cloth": 8, "wood": 4, "rope": 3},
        result="tent",
        category="Tools",
        recipe_id="tent"
    ),
    CraftingRecipe(
        name="Bedroll",
        ingredients={"cloth": 6, "fiber": 4},
        result="bedroll",
        category="Tools",
        recipe_id="bedroll"
    ),
    CraftingRecipe(
        name="Waterskin",
        ingredients={"cloth": 4, "fiber": 3, "rope": 1},
        result="waterskin",
        category="Tools",
        recipe_id="waterskin"
    ),
    CraftingRecipe(
        name="Cooking Pot",
        ingredients={"ore": 6, "wood": 2},
        result="cooking_pot",
        category="Tools",
        recipe_id="cooking_pot"
    ),
    CraftingRecipe(
        name="Lantern",
        ingredients={"ore": 4, "glass": 2, "fiber": 1, "oil": 2},
        result="lantern",
        category="Tools",
        recipe_id="lantern"
    ),
    
    # ==================== POISONS & OFFENSIVE CONSUMABLES ====================
    CraftingRecipe(
        name="Weak Poison",
        ingredients={"mushroom": 2, "herbs": 1},
        result="weak_poison",
        result_count=3,
        category="Consumables",
        recipe_id="weak_poison"
    ),
    CraftingRecipe(
        name="Strong Poison",
        ingredients={"mushroom": 4, "herbs": 2, "berries": 1},
        result="strong_poison",
        result_count=2,
        category="Consumables",
        recipe_id="strong_poison"
    ),
    CraftingRecipe(
        name="Paralyzing Poison",
        ingredients={"mushroom": 3, "bones": 2},
        result="paralyzing_poison",
        result_count=2,
        category="Consumables",
        recipe_id="paralyzing_poison"
    ),
    CraftingRecipe(
        name="Smoke Bomb",
        ingredients={"herbs": 3, "fiber": 2, "charcoal": 1},
        result="smoke_bomb",
        result_count=3,
        category="Consumables",
        recipe_id="smoke_bomb"
    ),
    CraftingRecipe(
        name="Flash Bomb",
        ingredients={"ore": 3, "mushroom": 2, "herbs": 1},
        result="flash_bomb",
        result_count=2,
        category="Consumables",
        recipe_id="flash_bomb"
    ),
    CraftingRecipe(
        name="Acid Vial",
        ingredients={"mushroom": 4, "ore": 1, "berries": 2},
        result="acid_vial",
        result_count=2,
        category="Consumables",
        recipe_id="acid_vial"
    ),
    
    # ===== PLAGUE DOCTOR GEAR (Disease Protection) =====
    CraftingRecipe(
        name="Plague Doctor Mask",
        ingredients={"cloth": 5, "leather": 3, "herbs": 10},
        result="plague_doctor_mask",
        category="Armor",
        recipe_id="plague_doctor_mask"
    ),
    CraftingRecipe(
        name="Plague Doctor Robe",
        ingredients={"cloth": 15, "leather": 5, "fiber": 10},
        result="plague_doctor_robe",
        category="Armor",
        recipe_id="plague_doctor_robe"
    ),
    CraftingRecipe(
        name="Plague Doctor Gloves",
        ingredients={"leather": 4, "cloth": 3, "herbs": 5},
        result="plague_doctor_gloves",
        category="Armor",
        recipe_id="plague_doctor_gloves"
    ),
]

# Recipe scroll definitions - maps scroll item name to recipe ID
RECIPE_SCROLLS = {
    "recipe_wooden_shield": "wooden_shield",
    "recipe_wooden_bow": "wooden_bow",
    "recipe_health_potion": "health_potion",
    "recipe_campfire": "campfire",
    "recipe_backpack": "backpack",
    "recipe_antidote": "antidote",
    "recipe_strength_potion": "strength_potion",
    "recipe_defense_potion": "defense_potion",
    "recipe_stamina_potion": "stamina_potion",
    "recipe_iron_sword": "iron_sword",
    "recipe_iron_armor": "iron_armor",
    "recipe_lockpick": "lockpick",
    "recipe_cloth_armor": "cloth_armor",
    "recipe_bandana": "bandana",
    "recipe_bag": "bag",
    "recipe_bone_dagger": "bone_dagger",
    "recipe_bone_armor": "bone_armor",
    "recipe_bone_charm": "bone_charm",
    "recipe_bomb": "bomb",
    
    # Stick-based weapons
    "recipe_wooden_spear": "wooden_spear",
    "recipe_wooden_club": "wooden_club",
    "recipe_training_sword": "training_sword",
    "recipe_sling": "sling",
    "recipe_quarterstaff": "quarterstaff",
    "recipe_wooden_mace": "wooden_mace",
    "recipe_javelin": "javelin",
    "recipe_reinforced_spear": "reinforced_spear",
    
    # Stick-based armor
    "recipe_wooden_pauldrons": "wooden_pauldrons",
    "recipe_wooden_bracers": "wooden_bracers",
    "recipe_wooden_mask": "wooden_mask",
    "recipe_wooden_chest_guard": "wooden_chest_guard",
    "recipe_bone_studded_wooden_armor": "bone_studded_wooden_armor",
    "recipe_forest_ranger_armor": "forest_ranger_armor",
    
    # Stick-based accessories
    "recipe_wooden_charm_necklace": "wooden_charm_necklace",
    "recipe_branch_amulet": "branch_amulet",
    "recipe_bone_wood_talisman": "bone_wood_talisman",
    "recipe_forest_blessing_pendant": "forest_blessing_pendant",
    "recipe_carved_wood_ring": "carved_wood_ring",
    "recipe_fiber_wrapped_ring": "fiber_wrapped_ring",
    "recipe_natures_band": "natures_band",
    
    # Stick-based magic items
    "recipe_wooden_wand": "wooden_wand",
    "recipe_apprentice_staff": "apprentice_staff",
    "recipe_wooden_totem": "wooden_totem",
    "recipe_rune_carved_stick": "rune_carved_stick",
    "recipe_nature_spirit_charm": "nature_spirit_charm",
    "recipe_druids_focus": "druids_focus",
    
    # Stick-based tools
    "recipe_reinforced_torch": "reinforced_torch",
    "recipe_fishing_rod": "fishing_rod",
    "recipe_bear_trap": "bear_trap",
    "recipe_wooden_ladder": "wooden_ladder",
    "recipe_sign_post": "sign_post",
    "recipe_walking_stick": "walking_stick",
    "recipe_wooden_barricade": "wooden_barricade",
    
    # Stick-based furniture
    "recipe_basic_workbench": "basic_workbench",
    "recipe_drying_rack": "drying_rack",
    "recipe_weapon_rack": "weapon_rack",
    "recipe_wooden_chair": "wooden_chair",
    
    # Health/Mana potions
    "recipe_minor_health_potion": "minor_health_potion",
    "recipe_greater_health_potion": "greater_health_potion",
    "recipe_minor_mana_potion": "minor_mana_potion",
    "recipe_mana_potion": "mana_potion",
    "recipe_greater_mana_potion": "greater_mana_potion",
    
    # Buff potions
    "recipe_speed_elixir": "speed_elixir",
    "recipe_fire_resistance_potion": "fire_resistance_potion",
    "recipe_ice_resistance_potion": "ice_resistance_potion",
    "recipe_invisibility_potion": "invisibility_potion",
    "recipe_night_vision_elixir": "night_vision_elixir",
    "recipe_water_breathing_potion": "water_breathing_potion",
    "recipe_regeneration_elixir": "regeneration_elixir",
    "recipe_mana_regeneration_elixir": "mana_regeneration_elixir",
    "recipe_fortitude_potion": "fortitude_potion",
    "recipe_clarity_potion": "clarity_potion",
    
    # Utility potions
    "recipe_poison_antidote": "poison_antidote",
    "recipe_cure_disease_potion": "cure_disease_potion",
    "recipe_stoneskin_potion": "stoneskin_potion",
    
    # Advanced weapons
    "recipe_steel_sword": "steel_sword",
    "recipe_battle_axe": "battle_axe",
    "recipe_war_hammer": "war_hammer",
    "recipe_dagger": "dagger",
    "recipe_scimitar": "scimitar",
    "recipe_greatsword": "greatsword",
    "recipe_flail": "flail",
    "recipe_crossbow": "crossbow",
    "recipe_longbow": "longbow",
    "recipe_arrows": "arrows",
    "recipe_fire_arrows": "fire_arrows",
    "recipe_poison_arrows": "poison_arrows",
    "recipe_bolts": "bolts",
    
    # Shields
    "recipe_iron_shield": "iron_shield",
    "recipe_steel_shield": "steel_shield",
    "recipe_buckler": "buckler",
    "recipe_kite_shield": "kite_shield",
    "recipe_tower_shield": "tower_shield",
    
    # Helmets
    "recipe_leather_cap": "leather_cap",
    "recipe_iron_helmet": "iron_helmet",
    "recipe_steel_helmet": "steel_helmet",
    "recipe_bone_helmet": "bone_helmet",
    "recipe_cloth_hood": "cloth_hood",
    "recipe_chainmail_coif": "chainmail_coif",
    
    # Boots/Legs
    "recipe_leather_boots": "leather_boots",
    "recipe_iron_boots": "iron_boots",
    "recipe_steel_greaves": "steel_greaves",
    "recipe_cloth_pants": "cloth_pants",
    "recipe_leather_leggings": "leather_leggings",
    "recipe_chainmail_leggings": "chainmail_leggings",
    
    # Gloves/Hands
    "recipe_leather_gloves": "leather_gloves",
    "recipe_iron_gauntlets": "iron_gauntlets",
    "recipe_steel_gauntlets": "steel_gauntlets",
    "recipe_fingerless_gloves": "fingerless_gloves",
    "recipe_archers_gloves": "archers_gloves",
    
    # Under-armor
    "recipe_gambeson": "gambeson",
    "recipe_padded_tunic": "padded_tunic",
    "recipe_cloth_shirt": "cloth_shirt",
    "recipe_leather_padding": "leather_padding",
    "recipe_chainmail_shirt": "chainmail_shirt",
    
    # Jewelry/Accessories
    "recipe_iron_ring": "iron_ring",
    "recipe_silver_ring": "silver_ring",
    "recipe_gold_ring": "gold_ring",
    "recipe_emerald_ring": "emerald_ring",
    "recipe_ruby_ring": "ruby_ring",
    "recipe_sapphire_ring": "sapphire_ring",
    "recipe_bone_necklace": "bone_necklace",
    "recipe_cloth_scarf": "cloth_scarf",
    "recipe_iron_chain": "iron_chain",
    "recipe_herb_sachet": "herb_sachet",
    "recipe_lucky_charm": "lucky_charm",
    "recipe_protection_amulet": "protection_amulet",
    "recipe_wisdom_amulet": "wisdom_amulet",
    "recipe_speed_amulet": "speed_amulet",
    
    # Enchantments & Runes
    "recipe_minor_sharpening_stone": "minor_sharpening_stone",
    "recipe_sharpening_stone": "sharpening_stone",
    "recipe_armor_polish": "armor_polish",
    "recipe_fire_rune": "fire_rune",
    "recipe_ice_rune": "ice_rune",
    "recipe_lightning_rune": "lightning_rune",
    "recipe_protection_rune": "protection_rune",
    "recipe_fortification_rune": "fortification_rune",
    "recipe_enchanted_thread": "enchanted_thread",
    
    # Food crafting
    "recipe_cooked_meat": "cooked_meat",
    "recipe_cooked_fish": "cooked_fish",
    "recipe_berry_pie": "berry_pie",
    "recipe_mushroom_stew": "mushroom_stew",
    "recipe_apple_cider": "apple_cider",
    "recipe_trail_mix": "trail_mix",
    "recipe_herb_tea": "herb_tea",
    "recipe_ration_pack": "ration_pack",
    
    # Advanced materials
    "recipe_leather": "leather",
    "recipe_thread": "thread",
    "recipe_glue": "glue",
    "recipe_charcoal": "charcoal",
    "recipe_glass": "glass",
    "recipe_nails": "nails",
    "recipe_steel_ingot": "steel_ingot",
    "recipe_bronze_ingot": "bronze_ingot",
    
    # Utility items
    "recipe_grappling_hook": "grappling_hook",
    "recipe_lockpick_set": "lockpick_set",
    "recipe_spyglass": "spyglass",
    "recipe_compass": "compass",
    "recipe_map": "map",
    "recipe_tent": "tent",
    "recipe_bedroll": "bedroll",
    "recipe_waterskin": "waterskin",
    "recipe_cooking_pot": "cooking_pot",
    "recipe_lantern": "lantern",
    
    # Poisons & offensive consumables
    "recipe_weak_poison": "weak_poison",
    "recipe_strong_poison": "strong_poison",
    "recipe_paralyzing_poison": "paralyzing_poison",
    "recipe_smoke_bomb": "smoke_bomb",
    "recipe_flash_bomb": "flash_bomb",
    "recipe_acid_vial": "acid_vial",
    
    # Plague doctor gear
    "recipe_plague_doctor_mask": "plague_doctor_mask",
    "recipe_plague_doctor_robe": "plague_doctor_robe",
    "recipe_plague_doctor_gloves": "plague_doctor_gloves",
}

def get_recipe_by_id(recipe_id):
    """Get a recipe by its unique ID"""
    for recipe in CRAFTING_RECIPES:
        if recipe.recipe_id == recipe_id:
            return recipe
    return None

def discover_recipe(player, recipe_id):
    """Discover a recipe for the player"""
    if not hasattr(player, 'discovered_recipes'):
        player.discovered_recipes = set()
    
    if recipe_id not in player.discovered_recipes:
        player.discovered_recipes.add(recipe_id)
        recipe = get_recipe_by_id(recipe_id)
        if recipe:
            logger.info(f"Recipe discovered: {recipe.name} (ID: {recipe_id})")
            print(f"📚 [RECIPE DISCOVERED] You learned how to craft: {recipe.name}!")
            return True
    return False

def use_recipe_scroll(player, scroll_name):
    """Use a recipe scroll to discover a recipe"""
    if scroll_name in RECIPE_SCROLLS:
        recipe_id = RECIPE_SCROLLS[scroll_name]
        return discover_recipe(player, recipe_id)
    return False

def initialize_player_recipes(player):
    """Initialize player's recipe discovery system with auto-discover recipes"""
    if not hasattr(player, 'discovered_recipes'):
        player.discovered_recipes = set()
    
    # Auto-discover starter recipes
    for recipe in CRAFTING_RECIPES:
        if recipe.auto_discover:
            player.discovered_recipes.add(recipe.recipe_id)


class CraftingUI:
    """UI for the crafting menu"""
    
    def __init__(self, config):
        self.config = config
        self.selected_recipe_idx = 0
        self.category_idx = 0
        self.scroll_offset = 0
        self.max_visible_recipes = 8
        
        # Get all categories from recipes
        self.categories = ["All"] + sorted(list(set(recipe.category for recipe in CRAFTING_RECIPES)))
        
    def get_filtered_recipes(self, player=None):
        """Get recipes filtered by selected category and discovery status"""
        # Filter by category
        if self.categories[self.category_idx] == "All":
            recipes = CRAFTING_RECIPES
        else:
            recipes = [r for r in CRAFTING_RECIPES if r.category == self.categories[self.category_idx]]
        
        # Filter by discovered status
        if player and hasattr(player, 'discovered_recipes'):
            recipes = [r for r in recipes if r.recipe_id in player.discovered_recipes]
        
        return recipes
    
    def handle_input(self, event, player):
        """Handle keyboard input for crafting menu"""
        if event.type != pygame.KEYDOWN:
            return None
        
        filtered_recipes = self.get_filtered_recipes(player)
        
        if event.key in [pygame.K_UP, pygame.K_w]:
            self.selected_recipe_idx = max(0, self.selected_recipe_idx - 1)
            # Adjust scroll
            if self.selected_recipe_idx < self.scroll_offset:
                self.scroll_offset = self.selected_recipe_idx
            return "navigate"
        
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.selected_recipe_idx = min(len(filtered_recipes) - 1, self.selected_recipe_idx + 1)
            # Adjust scroll
            if self.selected_recipe_idx >= self.scroll_offset + self.max_visible_recipes:
                self.scroll_offset = self.selected_recipe_idx - self.max_visible_recipes + 1
            return "navigate"
        
        elif event.key in [pygame.K_LEFT, pygame.K_a]:
            self.category_idx = (self.category_idx - 1) % len(self.categories)
            self.selected_recipe_idx = 0
            self.scroll_offset = 0
            return "category_change"
        
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            self.category_idx = (self.category_idx + 1) % len(self.categories)
            self.selected_recipe_idx = 0
            self.scroll_offset = 0
            return "category_change"
        
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            # Try to craft selected recipe
            if filtered_recipes:
                recipe = filtered_recipes[self.selected_recipe_idx]
                if recipe.craft(player.inventory, player):
                    logger.info(f"Crafted {recipe.result_count}x {recipe.result}")
                    print(f"[CRAFTING] Crafted {recipe.result_count}x {recipe.result}")
                    return "crafted"
                else:
                    logger.debug(f"Not enough materials to craft {recipe.name}")
                    print(f"[CRAFTING] Not enough materials to craft {recipe.name}")
                    return "failed"
        
        elif event.key in [pygame.K_ESCAPE, pygame.K_c]:
            return "close"
        
        return None
    
    def draw(self, screen, font, player):
        """Draw the crafting menu"""
        # Semi-transparent background
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.SysFont(None, 56)
        title_text = title_font.render("Crafting", True, (255, 215, 0))
        screen.blit(title_text, (self.config.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
        
        # Category tabs
        tab_y = 100
        tab_width = 150
        tab_spacing = 10
        start_x = (self.config.SCREEN_WIDTH - (len(self.categories) * (tab_width + tab_spacing))) // 2
        
        for i, category in enumerate(self.categories):
            tab_x = start_x + i * (tab_width + tab_spacing)
            color = (100, 150, 200) if i == self.category_idx else (60, 60, 60)
            text_color = (255, 255, 255) if i == self.category_idx else (150, 150, 150)
            
            pygame.draw.rect(screen, color, (tab_x, tab_y, tab_width, 40))
            pygame.draw.rect(screen, (200, 200, 200), (tab_x, tab_y, tab_width, 40), 2)
            
            tab_text = font.render(category, True, text_color)
            screen.blit(tab_text, (tab_x + tab_width // 2 - tab_text.get_width() // 2, tab_y + 10))
        
        # Recipe list panel
        panel_x = 50
        panel_y = 160
        panel_width = 700
        panel_height = 450
        
        pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (100, 100, 100), (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Draw recipes
        filtered_recipes = self.get_filtered_recipes(player)
        recipe_y = panel_y + 10
        
        # Show recipe discovery count
        total_recipes = len(CRAFTING_RECIPES)
        discovered_count = len(player.discovered_recipes) if hasattr(player, 'discovered_recipes') else 0
        discovery_text = f"Recipes Discovered: {discovered_count}/{total_recipes}"
        discovery_font = pygame.font.SysFont(None, 24)
        discovery_render = discovery_font.render(discovery_text, True, (100, 255, 255))
        screen.blit(discovery_render, (panel_x + 10, panel_y - 35))
        
        for i in range(self.scroll_offset, min(len(filtered_recipes), self.scroll_offset + self.max_visible_recipes)):
            recipe = filtered_recipes[i]
            is_selected = (i == self.selected_recipe_idx)
            can_craft = recipe.can_craft(player.inventory)
            
            # Background highlight for selected
            if is_selected:
                pygame.draw.rect(screen, (80, 80, 100), (panel_x + 5, recipe_y, panel_width - 10, 50))
            
            # Recipe name
            name_color = (255, 255, 255) if can_craft else (150, 150, 150)
            if is_selected:
                name_color = (255, 255, 100)
            
            name_text = font.render(f"{recipe.name} -> {recipe.result_count}x {recipe.result}", True, name_color)
            screen.blit(name_text, (panel_x + 15, recipe_y + 5))
            
            # Ingredients
            ingredients_str = ", ".join([f"{count}x {item}" for item, count in recipe.ingredients.items()])
            ing_font = pygame.font.SysFont(None, 20)
            
            # Show in red if player doesn't have enough, green if they do
            for j, (item, count) in enumerate(recipe.ingredients.items()):
                player_has = player.inventory.get(item, 0)
                has_enough = player_has >= count
                ing_color = (100, 255, 100) if has_enough else (255, 100, 100)
                
                ing_text = ing_font.render(f"{count}x {item} ({player_has})", True, ing_color)
                screen.blit(ing_text, (panel_x + 15 + j * 150, recipe_y + 28))
            
            recipe_y += 55
        
        # Scroll indicator
        if len(filtered_recipes) > self.max_visible_recipes:
            scroll_text = f"Showing {self.scroll_offset + 1}-{min(len(filtered_recipes), self.scroll_offset + self.max_visible_recipes)} of {len(filtered_recipes)}"
            scroll_render = pygame.font.SysFont(None, 20).render(scroll_text, True, (180, 180, 180))
            screen.blit(scroll_render, (panel_x + 10, panel_y + panel_height - 25))
        
        # Recipe details panel (right side)
        details_x = panel_x + panel_width + 20
        details_y = panel_y
        details_width = self.config.SCREEN_WIDTH - details_x - 50
        details_height = panel_height
        
        pygame.draw.rect(screen, (40, 40, 40), (details_x, details_y, details_width, details_height))
        pygame.draw.rect(screen, (100, 100, 100), (details_x, details_y, details_width, details_height), 3)
        
        # Show selected recipe details
        if filtered_recipes and 0 <= self.selected_recipe_idx < len(filtered_recipes):
            recipe = filtered_recipes[self.selected_recipe_idx]
            detail_y = details_y + 20
            
            # Recipe name
            detail_title_font = pygame.font.SysFont(None, 32)
            detail_title = detail_title_font.render(recipe.name, True, (255, 215, 0))
            screen.blit(detail_title, (details_x + 15, detail_y))
            detail_y += 50
            
            # Category
            cat_text = font.render(f"Category: {recipe.category}", True, (200, 200, 200))
            screen.blit(cat_text, (details_x + 15, detail_y))
            detail_y += 35
            
            # Ingredients header
            ing_header = font.render("Required Materials:", True, (255, 200, 100))
            screen.blit(ing_header, (details_x + 15, detail_y))
            detail_y += 30
            
            # List ingredients
            for item, count in recipe.ingredients.items():
                player_has = player.inventory.get(item, 0)
                has_enough = player_has >= count
                color = (100, 255, 100) if has_enough else (255, 100, 100)
                
                ing_line = font.render(f"  • {count}x {item} (You have: {player_has})", True, color)
                screen.blit(ing_line, (details_x + 15, detail_y))
                detail_y += 25
            
            detail_y += 20
            
            # Result header
            result_header = font.render("Creates:", True, (255, 200, 100))
            screen.blit(result_header, (details_x + 15, detail_y))
            detail_y += 30
            
            # Result item
            result_line = font.render(f"  • {recipe.result_count}x {recipe.result}", True, (100, 255, 255))
            screen.blit(result_line, (details_x + 15, detail_y))
            detail_y += 40
            
            # Craft button hint
            can_craft = recipe.can_craft(player.inventory, player)
            if can_craft:
                craft_hint = detail_title_font.render("Press ENTER to Craft", True, (100, 255, 100))
            else:
                craft_hint = detail_title_font.render("Not Enough Materials", True, (255, 100, 100))
            screen.blit(craft_hint, (details_x + 15, detail_y))
        
        # Controls help
        help_font = pygame.font.SysFont(None, 24)
        help_y = self.config.SCREEN_HEIGHT - 40
        help_texts = [
            "Arrow Keys/WASD: Navigate  |  Left/Right: Change Category",
            "ENTER/SPACE: Craft  |  ESC/C: Close"
        ]
        
        for i, help_text in enumerate(help_texts):
            help_render = help_font.render(help_text, True, (180, 180, 180))
            screen.blit(help_render, (self.config.SCREEN_WIDTH // 2 - help_render.get_width() // 2, help_y + i * 25))


def get_crafting_ui(config):
    """Get singleton instance of crafting UI"""
    if not hasattr(get_crafting_ui, 'instance'):
        get_crafting_ui.instance = CraftingUI(config)
    return get_crafting_ui.instance
