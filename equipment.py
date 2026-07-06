import pygame

# Stat abbreviations
STAT_ABBREVIATIONS = {
    "Strength": "STR",
    "Magic": "MAG",
    "Defense": "DEF",
    "Agility": "AGI",
    "Willpower": "WIL",
    "Stamina": "STA",
    "Luck": "LCK",
    "Speed": "SPD",
    "Health": "HP",
    "Range_Damage": "RNG",
    "Ice_Damage": "ICE",
    "Fire_Resistance": "FRS",
    "Stealth": "STL",
    "Critical_Chance": "CRT",
    "Critical_Damage": "CRD",
    "Mana_Regen": "MNR",
    "Talking": "TLK",
    "Attack_Speed": "ASP",
    "Freeze_Chance": "FRZ",
    "Light_Radius": "LGT",
    "Damage": "DMG"
}

# Stat icon mapping: each stat gets a shape-drawing function
def draw_stat_icon(surface, stat, pos, color=(150,150,150), size=32):
    x, y = pos
    if stat == "Strength":
        pygame.draw.rect(surface, color, (x, y, size, size))  # Square
    elif stat == "Magic":
        pygame.draw.circle(surface, color, (x + size//2, y + size//2), size//2)  # Circle
    elif stat == "Defense":
        pygame.draw.polygon(surface, color, [
            (x + size//2, y),
            (x + size, y + size//2),
            (x + size//2, y + size),
            (x, y + size//2)
        ])  # Diamond (shield-like)
    elif stat == "Agility":
        pygame.draw.polygon(surface, color, [
            (x + size//2, y),
            (x + size, y + size),
            (x, y + size)
        ])  # Triangle
    elif stat == "Willpower":
        pygame.draw.ellipse(surface, color, (x, y + size//4, size, size//2))  # Horizontal ellipse
    elif stat == "Stamina":
        pygame.draw.rect(surface, color, (x, y + size//4, size, size//2), border_radius=8)  # Rounded rectangle
    elif stat == "Luck":
        pygame.draw.polygon(surface, color, [
            (x + size//2, y),
            (x + size, y + size//2),
            (x + size//2, y + size),
            (x, y + size//2),
            (x + size//2, y)
        ])  # Star (simple)
    elif stat == "Speed":
        pygame.draw.line(surface, color, (x, y + size//2), (x + size, y + size//2), 4)  # Horizontal line
    elif stat == "Health":
        pygame.draw.rect(surface, color, (x + size//8, y + size//8, size*3//4, size*3//4), border_radius=size//2)  # Heart-like
    elif stat == "Range_Damage":
        pygame.draw.line(surface, color, (x, y + size//2), (x + size, y + size//2), 2)
        pygame.draw.circle(surface, color, (x + size, y + size//2), size//6)  # Arrow + circle
    elif stat == "Ice_Damage":
        pygame.draw.polygon(surface, color, [
            (x + size//2, y),
            (x + size, y + size),
            (x, y + size)
        ])  # Triangle (ice shard)
    elif stat == "Fire_Resistance":
        pygame.draw.arc(surface, color, (x, y, size, size), 3.14, 2*3.14, 4)  # Arc (flame)
    elif stat == "Stealth":
        pygame.draw.ellipse(surface, color, (x, y + size//3, size, size//3))  # Thin ellipse
    elif stat == "Critical_Chance":
        pygame.draw.circle(surface, color, (x + size//2, y + size//2), size//2)
        pygame.draw.line(surface, (0,0,0), (x + size//2, y), (x + size//2, y + size), 2)  # Circle with line
    elif stat == "Critical_Damage":
        pygame.draw.polygon(surface, color, [
            (x, y + size),
            (x + size//2, y),
            (x + size, y + size)
        ])  # V shape
    elif stat == "Mana_Regen":
        pygame.draw.arc(surface, color, (x, y, size, size), 0, 3.14, 4)  # Arc (mana wave)
    elif stat == "Talking":
        pygame.draw.rect(surface, color, (x, y + size//4, size, size//2))  # Rectangle (speech bubble)
    elif stat == "Attack_Speed":
        pygame.draw.line(surface, color, (x, y + size//2), (x + size, y + size//2), 2)
        pygame.draw.line(surface, color, (x + size//2, y), (x + size//2, y + size), 2)  # Crossed lines
    elif stat == "Freeze_Chance":
        pygame.draw.circle(surface, color, (x + size//2, y + size//2), size//2)
        pygame.draw.line(surface, (0,0,255), (x + size//2, y), (x + size//2, y + size), 2)  # Blue line
    elif stat == "Light_Radius":
        pygame.draw.circle(surface, color, (x + size//2, y + size//2), size//2, 2)  # Circle outline
    elif stat == "Damage":
        pygame.draw.rect(surface, color, (x, y, size, size//2))  # Wide rectangle
    else:
        pygame.draw.rect(surface, color, (x, y, size, size))  # Default: square

# Example usage:
# draw_stat_icon(screen, "Strength", (x, y), color=(0,255,0) if positive else (255,0,0), size=32)

# equipment.py - Complete version with descriptions added

# Equipment rarity levels  
EQUIPMENT_RARITY = {
    "common": {"color": (200, 200, 200), "multiplier": 1.0},      # Gray
    "uncommon": {"color": (0, 255, 0), "multiplier": 1.2},       # Green  
    "rare": {"color": (0, 100, 255), "multiplier": 1.5},         # Blue
    "epic": {"color": (150, 0, 255), "multiplier": 2.0},         # Purple
    "legendary": {"color": (255, 165, 0), "multiplier": 3.0},    # Orange
    "artifact": {"color": (255, 215, 0), "multiplier": 4.0},     # Gold - Ultra rare
    "set": {"color": (50, 255, 150), "multiplier": 1.8}          # Cyan-Green - Set items
}

# Visual representations for weapons (colors for now, could be sprites later)
WEAPON_VISUALS = {
    "sword": {"color": (180, 180, 180), "size": (8, 2)},          # Silver blade
    "dual_swords": {"color": (180, 180, 180), "size": (6, 2)},    # Smaller twin blades
    "axe": {"color": (139, 69, 19), "size": (6, 8)},             # Brown handle
    "bow": {"color": (139, 69, 19), "size": (3, 12)},            # Wooden bow
    "spear": {"color": (139, 69, 19), "size": (2, 14)},          # Long weapon
    "stick": {"color": (139, 90, 43), "size": (4, 11)},          # Simple wooden stick
    "mace": {"color": (105, 105, 105), "size": (4, 10)},         # Gray mace
    "club": {"color": (101, 67, 33), "size": (6, 12)},           # Thick wooden club
    "magic_staff": {"color": (75, 0, 130), "size": (3, 16)},     # Purple staff
    "ice_wand": {"color": (173, 216, 230), "size": (2, 10)},     # Light blue wand
    "lightning_rod": {"color": (255, 255, 0), "size": (2, 12)},  # Yellow rod
    "crystal_shard": {"color": (0, 191, 255), "size": (4, 4)},   # Blue crystal
    "fire_orb": {"color": (255, 69, 0), "size": (6, 6)},         # Red orb
    "magic_beam": {"color": (138, 43, 226), "size": (4, 8)},     # Blue violet beam
    "bite": {"color": (255, 255, 255), "size": (0, 0)},          # No visual (natural weapon)
    "claws": {"color": (255, 255, 255), "size": (0, 0)},         # No visual
    "fist": {"color": (255, 255, 255), "size": (0, 0)},          # No visual
    "body_slam": {"color": (255, 255, 255), "size": (0, 0)},     # No visual
    "none": {"color": (255, 255, 255), "size": (0, 0)}           # No weapon
}

# Equipment sets - EPIC+ ONLY for true endgame progression
# Only the rarest equipment can form sets with unique abilities
EQUIPMENT_SETS = {
    # ===== EPIC SETS (5 pieces each) =====
    
    "dragonslayer_arsenal": {
        "name": "Dragonslayer's Arsenal",
        "description": "Legendary weapons and armor forged from dragonbone, imbued with ancient draconic power.",
        "min_rarity": "epic",
        "pieces": ["dragonbone_sword", "dragonscale_helm", "dragonscale_armor", "dragonbone_shield", "dragonheart_amulet"],
        "bonuses": {
            2: {"positive": {"Strength": 8, "Defense": 5}, "negative": {"dubloon_find_rate": -0.1}},
            3: {"positive": {"Strength": 15, "Defense": 10, "Fire_Resistance": 25}, "negative": {"dubloon_find_rate": -0.15}},
            4: {"positive": {"Strength": 25, "Defense": 18, "Fire_Resistance": 40}, "negative": {"dubloon_find_rate": -0.2}},
            5: {
                "positive": {"Strength": 35, "Defense": 25, "Fire_Resistance": 60, "Critical_Damage": 30},
                "negative": {"dubloon_find_rate": -0.25},
                "special_ability": "dragonfire_immunity",
                "description": "Immunity to fire damage and 15% chance on critical hit to deal bonus fire damage"
            }
        }
    },
    
    "voidwalker_regalia": {
        "name": "Voidwalker's Regalia",
        "description": "Mystical garments that bend reality itself, worn by those who walk between worlds.",
        "min_rarity": "epic",
        "pieces": ["voidcloak", "shadowmask", "voidstep_boots", "reality_blade", "void_ring"],
        "bonuses": {
            2: {"positive": {"Stealth": 15, "Magic": 8}, "negative": {"resource_find_rate": -0.1}},
            3: {"positive": {"Stealth": 25, "Magic": 15, "Agility": 10}, "negative": {"resource_find_rate": -0.15}},
            4: {"positive": {"Stealth": 40, "Magic": 25, "Agility": 18}, "negative": {"resource_find_rate": -0.2}},
            5: {
                "positive": {"Stealth": 60, "Magic": 35, "Agility": 25, "Critical_Chance": 20},
                "negative": {"resource_find_rate": -0.25},
                "special_ability": "phase_step",
                "description": "10% chance to phase through enemy attacks, taking no damage"
            }
        }
    },
    
    "archmage_vestments": {
        "name": "Archmage's Vestments",
        "description": "The ultimate magical regalia, channeling the raw power of the arcane planes.",
        "min_rarity": "epic",
        "pieces": ["arcane_crown", "stormweave_robes", "manaforge_staff", "spellbind_gloves", "astral_boots"],
        "bonuses": {
            2: {"positive": {"Magic": 12, "Willpower": 8}, "negative": {"loot_drop_rate": -0.1}},
            3: {"positive": {"Magic": 20, "Willpower": 15, "Mana_Regen": 20}, "negative": {"loot_drop_rate": -0.15}},
            4: {"positive": {"Magic": 32, "Willpower": 25, "Mana_Regen": 35}, "negative": {"loot_drop_rate": -0.2}},
            5: {
                "positive": {"Magic": 45, "Willpower": 35, "Mana_Regen": 50, "Ice_Damage": 40},
                "negative": {"loot_drop_rate": -0.25},
                "special_ability": "mana_overflow",
                "description": "Spells cost no mana when cast at full mana (10 second cooldown)"
            }
        }
    },
    
    "shadowbane_arsenal": {
        "name": "Shadowbane Arsenal",
        "description": "Holy weapons blessed to destroy creatures of darkness and undeath.",
        "min_rarity": "epic",
        "pieces": ["blessed_blade", "radiant_helm", "sanctified_mail", "lightbringer_shield", "holy_symbol"],
        "bonuses": {
            2: {"positive": {"Strength": 8, "Willpower": 8}, "negative": {"dubloon_find_rate": -0.1}},
            3: {"positive": {"Strength": 15, "Willpower": 15, "Light_Radius": 30}, "negative": {"dubloon_find_rate": -0.15}},
            4: {"positive": {"Strength": 25, "Willpower": 25, "Light_Radius": 50}, "negative": {"dubloon_find_rate": -0.2}},
            5: {
                "positive": {"Strength": 35, "Willpower": 35, "Light_Radius": 80, "Critical_Chance": 15},
                "negative": {"dubloon_find_rate": -0.25},
                "special_ability": "undead_bane",
                "description": "Deal 200% damage to undead enemies and regenerate 2 HP per second in combat"
            }
        }
    },
    
    # ===== LEGENDARY SETS (6 pieces each) =====
    
    "eternal_champion": {
        "name": "Eternal Champion's Legacy",
        "description": "The complete armament of the legendary Eternal Champion, said to grant dominion over life and death.",
        "min_rarity": "legendary",
        "pieces": ["eternity_blade", "champion_crown", "eternal_plate", "timeless_boots", "destiny_cloak", "eternity_ring"],
        "bonuses": {
            2: {"positive": {"Strength": 15, "Defense": 10}, "negative": {"loot_drop_rate": -0.15}},
            3: {"positive": {"Strength": 25, "Defense": 18, "Health": 25}, "negative": {"loot_drop_rate": -0.2}},
            4: {"positive": {"Strength": 40, "Defense": 30, "Health": 50}, "negative": {"loot_drop_rate": -0.25}},
            5: {"positive": {"Strength": 55, "Defense": 42, "Health": 75, "Stamina": 30}, "negative": {"loot_drop_rate": -0.3}},
            6: {
                "positive": {"Strength": 75, "Defense": 60, "Health": 100, "Stamina": 50, "Critical_Damage": 50},
                "negative": {"loot_drop_rate": -0.35},
                "special_ability": "champions_resolve",
                "description": "When health drops below 25%, gain 100% damage and immunity to death for 5 seconds (once per combat)"
            }
        }
    },
    
    "astral_archon": {
        "name": "Astral Archon's Dominion",
        "description": "Artifacts from beyond the mortal plane, granting mastery over space, time, and magic itself.",
        "min_rarity": "legendary",
        "pieces": ["cosmic_scepter", "astral_diadem", "starweave_vestments", "voidstep_sandals", "nebula_cloak", "constellation_orb"],
        "bonuses": {
            2: {"positive": {"Magic": 18, "Willpower": 12}, "negative": {"resource_find_rate": -0.15}},
            3: {"positive": {"Magic": 30, "Willpower": 20, "Mana_Regen": 30}, "negative": {"resource_find_rate": -0.2}},
            4: {"positive": {"Magic": 50, "Willpower": 35, "Mana_Regen": 50}, "negative": {"resource_find_rate": -0.25}},
            5: {"positive": {"Magic": 70, "Willpower": 50, "Mana_Regen": 75, "Ice_Damage": 60}, "negative": {"resource_find_rate": -0.3}},
            6: {
                "positive": {"Magic": 95, "Willpower": 70, "Mana_Regen": 100, "Ice_Damage": 80, "Freeze_Chance": 25},
                "negative": {"resource_find_rate": -0.35},
                "special_ability": "temporal_mastery",
                "description": "All abilities have 25% chance to not trigger cooldowns, and see enemy health/mana bars"
            }
        }
    }
}

# Equipment types and base stats
EQUIPMENT_DATA = {
    # MELEE WEAPONS
    "rusty_sword": {
        "name": "Rusty Sword",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 8,
        "stat_bonuses": {"Strength": 1},
        "rarity": "common",
        "weight": 3,
        "value": 2,
        "description": "A worn blade with patches of rust, but still sharp enough to cut through flesh and leather."
    },
    
    "stick": {
        "name": "stick",
        "slot": "main_hand",
        "base_damage": 2,
        "type": "weapon",
        "stackable": True,  # Custom field for your stacking mechanic
        "blade_color": (139, 90, 43),  # Medium brown wood color
        "handle_color": (139, 90, 43),  # Same brown for consistency
        "rarity": "common",
        "description": "A simple stick. Stack more sticks to increase its power!"
    },
    "iron_sword": {
        "name": "Iron Sword", 
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 12,
        "stat_bonuses": {"Strength": 2},
        "rarity": "common",
        "weight": 4,
        "value": 3,
        "description": "A well-crafted iron blade with a solid grip. Reliable and durable for any warrior."
    },
    "steel_sword": {
        "name": "Steel Sword",
        "type": "weapon", 
        "slot": "main_hand",
        "base_damage": 16,
        "stat_bonuses": {"Strength": 3, "Agility": 1},
        "rarity": "uncommon",
        "weight": 4,
        "value": 4,
        "description": "Forged from high-quality steel, this blade gleams with deadly precision and perfect balance."
    },
    "enchanted_blade": {
        "name": "Enchanted Blade",
        "type": "weapon",
        "slot": "main_hand", 
        "base_damage": 20,
        "magic_damage": 8,
        "stat_bonuses": {"Strength": 4, "Willpower": 2},
        "rarity": "rare",
        "weight": 3,
        "value": 8,
        "description": "Ancient runes glow along this blade's edge, channeling mystical energy into every strike."
    },
    "battleaxe": {
        "name": "Battleaxe",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 18,
        "stat_bonuses": {"Strength": 4},
        "rarity": "uncommon",
        "weight": 6,
        "value": 5,
        "description": "A massive two-handed axe designed for cleaving through armor and bone with devastating force."
    },
    "war_hammer": {
        "name": "War Hammer",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 20,
        "stat_bonuses": {"Strength": 5, "Stamina": 1},
        "rarity": "rare",
        "weight": 8,
        "value": 4,
        "description": "A brutal weapon of war, its heavy head can crush the strongest armor and shatter bones."
    },
    "crystal_dagger": {
        "name": "Crystal Dagger",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 10,
        "stat_bonuses": {"Agility": 4, "Luck": 2},
        "rarity": "rare",
        "weight": 1,
        "value": 9,
        "description": "Carved from pure crystal, this dagger seems to shimmer with luck and strikes with supernatural precision."
    },
    
    # RANGED WEAPONS
    "wooden_bow": {
        "name": "Wooden Bow",
        "type": "weapon",
        "slot": "main_hand", 
        "base_damage": 10,
        "stat_bonuses": {"Agility": 2},
        "rarity": "common",
        "weight": 2,
        "value": 2,
        "description": "A simple hunting bow made from seasoned yew wood. Perfect for beginners and forest dwellers."
    },
    "longbow": {
        "name": "Longbow",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 15,
        "stat_bonuses": {"Agility": 3, "Strength": 1},
        "rarity": "uncommon",
        "weight": 3,
        "value": 3,
        "description": "A masterwork bow of impressive length, capable of sending arrows vast distances with deadly accuracy."
    },
    "crossbow": {
        "name": "Crossbow",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 18,
        "stat_bonuses": {"Agility": 2, "Strength": 2},
        "rarity": "rare",
        "weight": 5,
        "value": 8,
        "description": "A mechanical marvel that launches bolts with tremendous force, requiring less skill but more strength."
    },
    
    # MAGIC WEAPONS  
    "magic_staff": {
        "name": "Magic Staff",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 6,
        "magic_damage": 14,
        "stat_bonuses": {"Willpower": 3},
        "rarity": "uncommon", 
        "weight": 2,
        "value": 6,
        "description": "A staff carved with arcane symbols that amplifies the wielder's magical abilities and focus."
    },
    "fire_wand": {
        "name": "Fire Wand",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 4,
        "magic_damage": 16,
        "stat_bonuses": {"Willpower": 4},
        "rarity": "rare",
        "weight": 1,
        "value": 7,
        "special": "fire_damage",
        "description": "This ruby-tipped wand crackles with contained flames, turning every spell into a blazing inferno."
    },
    "ice_scepter": {
        "name": "Ice Scepter", 
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 5,
        "magic_damage": 18,
        "stat_bonuses": {"Willpower": 5, "Stamina": 1},
        "rarity": "epic",
        "weight": 3,
        "value": 5,
        "special": "ice_damage",
        "description": "An ancient scepter crowned with eternal ice, its touch can freeze blood and shatter souls."
    },
    
    # SHIELDS
    "wooden_shield": {
        "name": "Wooden Shield",
        "type": "shield",
        "slot": "off_hand",
        "defense": 4,
        "stat_bonuses": {"Stamina": 2},
        "rarity": "common",
        "weight": 4,
        "value": 1,
        "description": "A basic round shield made from sturdy oak, reinforced with iron bands for extra protection."
    },
    "iron_shield": {
        "name": "Iron Shield",
        "type": "shield", 
        "slot": "off_hand",
        "defense": 7,
        "stat_bonuses": {"Stamina": 3, "Strength": 1},
        "rarity": "uncommon",
        "weight": 6,
        "value": 2,
        "description": "A solid iron shield with a polished surface that can deflect both blades and arrows with ease."
    },
    "tower_shield": {
        "name": "Tower Shield",
        "type": "shield",
        "slot": "off_hand",
        "defense": 12,
        "stat_bonuses": {"Stamina": 5},
        "rarity": "rare",
        "weight": 10,
        "value": 6,
        "description": "A massive shield that covers the entire body, providing unmatched protection at the cost of mobility."
    },
    
    # CHEST ARMOR
    "leather_armor": {
        "name": "Leather Armor",
        "type": "armor",
        "slot": "chest",
        "defense": 3,
        "stat_bonuses": {"Stamina": 1, "Agility": 1},
        "rarity": "common",
        "weight": 5,
        "value": 3,
        "description": "Supple leather armor that provides basic protection while maintaining freedom of movement."
    },
    "chain_mail": {
        "name": "Chain Mail",
        "type": "armor", 
        "slot": "chest",
        "defense": 6,
        "stat_bonuses": {"Stamina": 2, "Strength": 1},
        "rarity": "uncommon",
        "weight": 8,
        "value": 3,
        "description": "Interlocking metal rings form this flexible armor that distributes impact across its surface."
    },
    "plate_armor": {
        "name": "Plate Armor",
        "type": "armor",
        "slot": "chest", 
        "defense": 10,
        "stat_bonuses": {"Stamina": 4, "Strength": 2},
        "rarity": "rare",
        "weight": 15,
        "value": 4,
        "description": "Masterfully crafted steel plates that transform the wearer into an armored fortress on the battlefield."
    },
    # === WANDERING GUIDE LEGENDARY ITEMS ===
    "guides_compass": {
        "name": "Guide's Compass",
        "type": "accessory",
        "slot": "necklace",
        "defense": 0,
        "stat_bonuses": {"Charisma": 5, "Willpower": 3},
        "rarity": "legendary",
        "weight": 1,
        "value": 500,
        "special": "reveals_towns",
        "description": "A mystical compass that always points toward civilization. The Wandering Guide used it to never get lost. Reveals all nearby towns on the map within 500 pixels."
    },
    "wayfarers_staff": {
        "name": "Wayfarer's Staff",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 18,
        "magic_damage": 5,
        "stat_bonuses": {"Stamina": 5, "Dexterity": 3},
        "rarity": "legendary",
        "weight": 2,
        "value": 450,
        "special": "movement_speed",
        "description": "A worn oak staff carried across countless miles. It seems lighter than it should be. Grants +20% movement speed when equipped."
    },
    "travelers_cloak": {
        "name": "Traveler's Cloak",
        "type": "armor",
        "slot": "chest",
        "defense": 10,
        "stat_bonuses": {"Charisma": 5, "Agility": 2},
        "rarity": "epic",
        "weight": 3,
        "value": 300,
        "special": "shop_discount",
        "description": "A weathered blue cloak that marks its wearer as a friend to travelers. Reduces shop prices by 10% in all towns."
    },
    "tutorial_masters_badge": {
        "name": "Tutorial Master's Badge",
        "type": "accessory",
        "slot": "necklace",
        "defense": 0,
        "stat_bonuses": {"Willpower": 3, "Charisma": 2},
        "rarity": "legendary",
        "weight": 0,
        "value": 400,
        "special": "xp_boost",
        "description": "Proof that you bested a master teacher. Perhaps you learned something. Grants +50% XP gain for 2 in-game days."
    },
    "map_of_the_ancients": {
        "name": "Map of the Ancients",
        "type": "consumable",
        "slot": None,
        "rarity": "legendary",
        "weight": 0,
        "value": 600,
        "special": "reveal_map",
        "description": "The Wandering Guide's personal map, marked with decades of travels. One-time use reveals all towns and dungeons on the entire map permanently."
    },
    
    "mage_robes": {
        "name": "Mage Robes",
        "type": "armor",
        "slot": "chest",
        "defense": 2,
        "stat_bonuses": {"Willpower": 4, "Magic": 20},
        "rarity": "uncommon",
        "weight": 2,
        "value": 4,
        "description": "Flowing robes woven with silver threads that enhance magical conductivity and spell power."
    },
    
    # HELMETS
    "leather_cap": {
        "name": "Leather Cap",
        "type": "armor",
        "slot": "head",
        "defense": 1,
        "stat_bonuses": {"Agility": 1},
        "rarity": "common",
        "weight": 1,
        "value": 2,
        "description": "A simple leather cap that provides minimal protection while keeping your head cool and mobile."
    },
    "iron_helmet": {
        "name": "Iron Helmet",
        "type": "armor",
        "slot": "head",
        "defense": 3,
        "stat_bonuses": {"Stamina": 2},
        "rarity": "common", 
        "weight": 3,
        "value": 2,
        "description": "A sturdy iron helmet with cheek guards that protects against both blade and blunt force trauma."
    },
    "crown_of_wisdom": {
        "name": "Crown of Wisdom",
        "type": "armor",
        "slot": "head",
        "defense": 2,
        "stat_bonuses": {"Willpower": 5, "Talking": 3},
        "rarity": "epic",
        "weight": 2,
        "value": 5,
        "description": "An ancient crown that sharpens the mind and grants the wearer supernatural insight and charisma."
    },
    
    # BOOTS
    "leather_boots": {
        "name": "Leather Boots",
        "type": "armor",
        "slot": "feet",
        "defense": 1,
        "stat_bonuses": {"Agility": 2},
        "rarity": "common",
        "weight": 2,
        "value": 2,
        "description": "Comfortable leather boots perfect for long journeys and silent movement through any terrain."
    },
    "iron_boots": {
        "name": "Iron Boots",
        "type": "armor",
        "slot": "feet",
        "defense": 2,
        "stat_bonuses": {"Stamina": 2, "Strength": 1},
        "rarity": "uncommon",
        "weight": 4,
        "value": 4,
        "description": "Heavy metal boots that protect the feet and ankles while adding weight to every kick."
    },
    "boots_of_speed": {
        "name": "Boots of Speed",
        "type": "armor",
        "slot": "feet",
        "defense": 1,
        "stat_bonuses": {"Agility": 4, "Speed": 2},
        "rarity": "rare",
        "weight": 1,
        "value": 8,
        "description": "Enchanted boots that seem to barely touch the ground, granting supernatural speed and agility."
    },
    
    # GLOVES
    "leather_gloves": {
        "name": "Leather Gloves",
        "type": "armor",
        "slot": "hands",
        "defense": 1,
        "stat_bonuses": {"Agility": 1},
        "rarity": "common",
        "weight": 1,
        "value": 1,
        "description": "Simple leather gloves that protect the hands while maintaining dexterity for fine work."
    },
    "gauntlets_of_power": {
        "name": "Gauntlets of Power",
        "type": "armor",
        "slot": "hands",
        "defense": 2,
        "stat_bonuses": {"Strength": 4},
        "rarity": "rare",
        "weight": 3,
        "value": 8,
        "description": "Heavy gauntlets infused with strength-enhancing magic that amplify every grip and strike."
    },
    "iron_gauntlets": {
        "name": "Iron Gauntlets",
        "type": "armor",
        "slot": "hands",
        "defense": 2,
        "stat_bonuses": {"Strength": 2},
        "rarity": "common",
        "weight": 2,
        "value": 3,
        "description": "Sturdy iron gloves that protect the hands while allowing firm grips on weapons and shields."
    },
    
    # LEGS
    "leather_pants": {
        "name": "Leather Pants",
        "type": "armor",
        "slot": "legs",
        "defense": 2,
        "stat_bonuses": {"Agility": 1, "Stamina": 1},
        "rarity": "common",
        "weight": 3,
        "value": 2,
        "description": "Durable leather trousers that provide basic protection while allowing freedom of movement."
    },
    "iron_greaves": {
        "name": "Iron Greaves",
        "type": "armor",
        "slot": "legs",
        "defense": 4,
        "stat_bonuses": {"Stamina": 2, "Strength": 1},
        "rarity": "common",
        "weight": 5,
        "value": 3,
        "description": "Metal leg guards that shield the shins and thighs from incoming strikes."
    },
    "chain_leggings": {
        "name": "Chain Leggings",
        "type": "armor",
        "slot": "legs",
        "defense": 5,
        "stat_bonuses": {"Stamina": 3, "Agility": 1},
        "rarity": "uncommon",
        "weight": 6,
        "value": 4,
        "description": "Interlocking metal rings form flexible leg armor that moves with your stride."
    },
    "steel_greaves": {
        "name": "Steel Greaves",
        "type": "armor",
        "slot": "legs",
        "defense": 7,
        "stat_bonuses": {"Stamina": 4, "Strength": 2},
        "rarity": "rare",
        "weight": 8,
        "value": 6,
        "description": "Heavy steel plates that transform your legs into armored pillars of strength."
    },
    "mage_pants": {
        "name": "Mage Pants",
        "type": "armor",
        "slot": "legs",
        "defense": 2,
        "stat_bonuses": {"Willpower": 3, "Magic": 15},
        "rarity": "uncommon",
        "weight": 2,
        "value": 4,
        "description": "Flowing cloth leggings woven with arcane threads that enhance magical energy flow."
    },
    "shadow_leggings": {
        "name": "Shadow Leggings",
        "type": "armor",
        "slot": "legs",
        "defense": 3,
        "stat_bonuses": {"Agility": 5, "Luck": 2},
        "rarity": "rare",
        "weight": 2,
        "value": 8,
        "description": "Dark leather pants that seem to absorb light, granting supernatural stealth and agility."
    },
    "dragon_scale_leggings": {
        "name": "Dragon Scale Leggings",
        "type": "armor",
        "slot": "legs",
        "defense": 9,
        "stat_bonuses": {"Stamina": 5, "Strength": 3, "Fire_Resist": 20},
        "rarity": "epic",
        "weight": 7,
        "value": 15,
        "description": "Legendary leg armor crafted from dragon scales, nearly impervious to blade and flame."
    },
    
    # ARMS (Shoulder/Arm Armor)
    "leather_shoulderpads": {
        "name": "Leather Shoulderpads",
        "type": "armor",
        "slot": "arms",
        "defense": 1,
        "stat_bonuses": {"Agility": 1},
        "rarity": "common",
        "weight": 2,
        "value": 2,
        "description": "Simple leather pads that protect the shoulders without restricting arm movement."
    },
    "iron_pauldrons": {
        "name": "Iron Pauldrons",
        "type": "armor",
        "slot": "arms",
        "defense": 3,
        "stat_bonuses": {"Strength": 2, "Stamina": 1},
        "rarity": "common",
        "weight": 4,
        "value": 3,
        "description": "Solid iron shoulder plates that deflect downward strikes and protect the upper arms."
    },
    "steel_pauldrons": {
        "name": "Steel Pauldrons",
        "type": "armor",
        "slot": "arms",
        "defense": 5,
        "stat_bonuses": {"Strength": 3, "Stamina": 2},
        "rarity": "uncommon",
        "weight": 5,
        "value": 5,
        "description": "Expertly crafted steel shoulder guards that provide excellent protection and intimidating presence."
    },
    "spiked_pauldrons": {
        "name": "Spiked Pauldrons",
        "type": "armor",
        "slot": "arms",
        "defense": 4,
        "stat_bonuses": {"Strength": 4, "Damage": 3},
        "rarity": "uncommon",
        "weight": 6,
        "value": 6,
        "description": "Fearsome shoulder armor adorned with sharp spikes that can injure attackers and add force to strikes."
    },
    "mage_mantle": {
        "name": "Mage Mantle",
        "type": "armor",
        "slot": "arms",
        "defense": 1,
        "stat_bonuses": {"Willpower": 4, "Magic": 20},
        "rarity": "rare",
        "weight": 1,
        "value": 7,
        "description": "An enchanted shoulder cape that channels magical energy and reduces spell casting time."
    },
    "berserker_pauldrons": {
        "name": "Berserker Pauldrons",
        "type": "armor",
        "slot": "arms",
        "defense": 6,
        "stat_bonuses": {"Strength": 5, "Stamina": 3, "Damage": 5},
        "rarity": "rare",
        "weight": 7,
        "value": 9,
        "description": "Brutal shoulder armor worn by legendary warriors, enhancing devastating melee combat prowess."
    },
    "dragon_pauldrons": {
        "name": "Dragon Pauldrons",
        "type": "armor",
        "slot": "arms",
        "defense": 8,
        "stat_bonuses": {"Strength": 6, "Stamina": 4, "Fire_Resist": 25},
        "rarity": "epic",
        "weight": 6,
        "value": 20,
        "description": "Shoulder plates crafted from dragon bone and scale, radiating ancient power and near-invulnerability."
    },
    
    # ACCESSORIES
    "silver_ring": {
        "name": "Silver Ring",
        "type": "accessory",
        "slot": "ring",
        "stat_bonuses": {"Luck": 2},
        "rarity": "uncommon",
        "weight": 0,
        "value": 5,
        "description": "A polished silver band that seems to attract good fortune and deflect minor misfortunes."
    },
    "ring_of_protection": {
        "name": "Ring of Protection",
        "type": "accessory", 
        "slot": "ring",
        "defense": 2,
        "stat_bonuses": {"Stamina": 3},
        "rarity": "rare",
        "weight": 0,
        "value": 8,
        "description": "An enchanted ring that creates an invisible barrier around the wearer, deflecting harmful energies."
    },
    "amulet_of_power": {
        "name": "Amulet of Power",
        "type": "accessory",
        "slot": "neck",
        "stat_bonuses": {"Strength": 3, "Willpower": 2},
        "rarity": "epic",
        "weight": 1,
        "value": 29,
        "description": "A mysterious amulet that pulses with inner power, enhancing both physical and mental capabilities."
    },
    
    # ===== EPIC SET ITEMS =====
    # Dragonslayer Arsenal
    "dragonbone_sword": {
        "name": "Dragonbone Sword",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 25,
        "stat_bonuses": {"Strength": 8, "Critical_Chance": 5},
        "rarity": "epic",
        "weight": 6,
        "value": 150,
        "set": "dragonslayer_arsenal",
        "description": "A blade forged from ancient dragonbone, eternally sharp and burning with draconic fury."
    },
    "dragonscale_helm": {
        "name": "Dragonscale Helm",
        "type": "armor",
        "slot": "head",
        "defense": 8,
        "stat_bonuses": {"Defense": 6, "Fire_Resistance": 15},
        "rarity": "epic",
        "weight": 4,
        "value": 120,
        "set": "dragonslayer_arsenal",
        "description": "A helm crafted from overlapping dragon scales, providing unmatched protection from flame."
    },
    "dragonscale_armor": {
        "name": "Dragonscale Armor",
        "type": "armor",
        "slot": "chest",
        "defense": 12,
        "stat_bonuses": {"Defense": 10, "Strength": 4},
        "rarity": "epic",
        "weight": 15,
        "value": 200,
        "set": "dragonslayer_arsenal",
        "description": "Armor woven from the scales of an elder dragon, both beautiful and impenetrable."
    },
    "dragonbone_shield": {
        "name": "Dragonbone Shield",
        "type": "shield",
        "slot": "off_hand",
        "defense": 10,
        "stat_bonuses": {"Defense": 8, "Stamina": 5},
        "rarity": "epic",
        "weight": 8,
        "value": 140,
        "set": "dragonslayer_arsenal",
        "description": "A shield carved from a single piece of dragonbone, capable of deflecting the mightiest blows."
    },
    "dragonheart_amulet": {
        "name": "Dragonheart Amulet",
        "type": "accessory",
        "slot": "neck",
        "stat_bonuses": {"Strength": 6, "Fire_Resistance": 20, "Health": 15},
        "rarity": "epic",
        "weight": 1,
        "value": 180,
        "set": "dragonslayer_arsenal",
        "description": "Contains the crystallized heart of a dragon, pulsing with eternal flame and power."
    },
    
    # Voidwalker Regalia
    "voidcloak": {
        "name": "Voidcloak",
        "type": "armor",
        "slot": "chest",
        "defense": 5,
        "stat_bonuses": {"Stealth": 20, "Magic": 6},
        "rarity": "epic",
        "weight": 3,
        "value": 160,
        "set": "voidwalker_regalia",
        "description": "A cloak woven from the fabric of the void itself, bending light around the wearer."
    },
    "shadowmask": {
        "name": "Shadowmask",
        "type": "armor",
        "slot": "head",
        "defense": 3,
        "stat_bonuses": {"Stealth": 15, "Agility": 4},
        "rarity": "epic",
        "weight": 1,
        "value": 130,
        "set": "voidwalker_regalia",
        "description": "A mask that shifts and writhes like living shadow, concealing the wearer's identity."
    },
    "voidstep_boots": {
        "name": "Voidstep Boots",
        "type": "armor",
        "slot": "feet",
        "defense": 2,
        "stat_bonuses": {"Agility": 8, "Speed": 10},
        "rarity": "epic",
        "weight": 2,
        "value": 110,
        "set": "voidwalker_regalia",
        "description": "Boots that allow the wearer to step through shadows and move without sound."
    },
    "reality_blade": {
        "name": "Reality Blade",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 20,
        "stat_bonuses": {"Magic": 8, "Critical_Chance": 8},
        "rarity": "epic",
        "weight": 3,
        "value": 170,
        "set": "voidwalker_regalia",
        "description": "A blade that exists partially outside reality, phasing through armor to strike true."
    },
    "void_ring": {
        "name": "Void Ring",
        "type": "accessory",
        "slot": "finger",
        "stat_bonuses": {"Magic": 6, "Stealth": 10, "Mana_Regen": 8},
        "rarity": "epic",
        "weight": 0,
        "value": 140,
        "set": "voidwalker_regalia",
        "description": "A ring containing a fragment of the void, whispering secrets of shadow magic."
    },
    
    # ===== LEGENDARY SET ITEMS =====
    # Eternal Champion
    "eternity_blade": {
        "name": "Eternity Blade",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 35,
        "stat_bonuses": {"Strength": 12, "Critical_Damage": 20},
        "rarity": "legendary",
        "weight": 8,
        "value": 500,
        "set": "eternal_champion",
        "description": "The legendary sword of the Eternal Champion, said to cut through time itself."
    },
    "champion_crown": {
        "name": "Champion's Crown",
        "type": "armor",
        "slot": "head",
        "defense": 15,
        "stat_bonuses": {"Strength": 8, "Willpower": 8, "Health": 20},
        "rarity": "legendary",
        "weight": 5,
        "value": 450,
        "set": "eternal_champion",
        "description": "The golden crown worn by champions throughout the ages, inspiring courage in allies."
    },
    "eternal_plate": {
        "name": "Eternal Plate",
        "type": "armor",
        "slot": "chest",
        "defense": 20,
        "stat_bonuses": {"Defense": 15, "Stamina": 12},
        "rarity": "legendary",
        "weight": 25,
        "value": 600,
        "set": "eternal_champion",
        "description": "Armor that has protected countless heroes, growing stronger with each victory."
    },
    "timeless_boots": {
        "name": "Timeless Boots",
        "type": "armor",
        "slot": "feet",
        "defense": 8,
        "stat_bonuses": {"Stamina": 10, "Speed": 15},
        "rarity": "legendary",
        "weight": 6,
        "value": 350,
        "set": "eternal_champion",
        "description": "Boots that have walked through countless battles across the ages."
    },
    "destiny_cloak": {
        "name": "Destiny Cloak",
        "type": "armor",
        "slot": "back",
        "defense": 5,
        "stat_bonuses": {"Luck": 15, "Critical_Chance": 10},
        "rarity": "legendary",
        "weight": 2,
        "value": 400,
        "set": "eternal_champion",
        "description": "A cloak that shimmers with the threads of fate, guiding its wearer toward destiny."
    },
    "eternity_ring": {
        "name": "Eternity Ring",
        "type": "accessory",
        "slot": "finger",
        "stat_bonuses": {"Health": 25, "Mana_Regen": 15, "Willpower": 8},
        "rarity": "legendary",
        "weight": 0,
        "value": 480,
        "set": "eternal_champion",
        "description": "A ring containing the essence of eternity itself, granting its wearer longevity."
    },
    "lucky_charm": {
        "name": "Lucky Charm",
        "type": "accessory",
        "slot": "neck",
        "stat_bonuses": {"Luck": 5},
        "rarity": "rare",
        "weight": 0,
        "value": 3,
        "description": "A small trinket passed down through generations, said to bring extraordinary luck to its bearer."
    },
    
    # Archmage Vestments (Epic)
    "arcane_crown": {
        "name": "Arcane Crown",
        "type": "armor",
        "slot": "head",
        "defense": 4,
        "stat_bonuses": {"Magic": 10, "Willpower": 6, "Mana_Regen": 10},
        "rarity": "epic",
        "weight": 2,
        "value": 200,
        "set": "archmage_vestments",
        "description": "A crown of crystallized magic that amplifies the wearer's arcane powers."
    },
    "stormweave_robes": {
        "name": "Stormweave Robes",
        "type": "armor",
        "slot": "chest",
        "defense": 6,
        "stat_bonuses": {"Magic": 12, "Mana_Regen": 15},
        "rarity": "epic",
        "weight": 4,
        "value": 220,
        "set": "archmage_vestments",
        "description": "Robes woven from storm clouds themselves, crackling with elemental energy."
    },
    "manaforge_staff": {
        "name": "Manaforge Staff",
        "type": "weapon",
        "slot": "main_hand",
        "magic_damage": 30,
        "stat_bonuses": {"Magic": 15, "Willpower": 8},
        "rarity": "epic",
        "weight": 5,
        "value": 250,
        "set": "archmage_vestments",
        "description": "A staff that channels raw mana, forging spells of incredible power."
    },
    "spellbind_gloves": {
        "name": "Spellbind Gloves",
        "type": "armor",
        "slot": "hands",
        "defense": 2,
        "stat_bonuses": {"Magic": 8, "Ice_Damage": 12},
        "rarity": "epic",
        "weight": 1,
        "value": 180,
        "set": "archmage_vestments",
        "description": "Gloves that bind spells to the wearer's will, enhancing magical manipulation."
    },
    "astral_boots": {
        "name": "Astral Boots",
        "type": "armor",
        "slot": "feet",
        "defense": 3,
        "stat_bonuses": {"Willpower": 6, "Speed": 8, "Mana_Regen": 5},
        "rarity": "epic",
        "weight": 2,
        "value": 160,
        "set": "archmage_vestments",
        "description": "Boots that allow the wearer to walk on astral winds and channel planar energy."
    },
    
    # Shadowbane Arsenal (Epic)
    "blessed_blade": {
        "name": "Blessed Blade",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 22,
        "stat_bonuses": {"Strength": 8, "Willpower": 6, "Critical_Chance": 6},
        "rarity": "epic",
        "weight": 4,
        "value": 190,
        "set": "shadowbane_arsenal",
        "description": "A sword blessed by divine light, burning with holy power against the forces of darkness."
    },
    "radiant_helm": {
        "name": "Radiant Helm",
        "type": "armor",
        "slot": "head",
        "defense": 7,
        "stat_bonuses": {"Willpower": 8, "Light_Radius": 20},
        "rarity": "epic",
        "weight": 3,
        "value": 170,
        "set": "shadowbane_arsenal",
        "description": "A helm that shines with inner light, banishing shadows and fear from the wearer's path."
    },
    "sanctified_mail": {
        "name": "Sanctified Mail",
        "type": "armor",
        "slot": "chest",
        "defense": 10,
        "stat_bonuses": {"Defense": 8, "Willpower": 6},
        "rarity": "epic",
        "weight": 12,
        "value": 200,
        "set": "shadowbane_arsenal",
        "description": "Chain mail blessed in sacred rituals, providing protection both physical and spiritual."
    },
    "lightbringer_shield": {
        "name": "Lightbringer Shield",
        "type": "shield",
        "slot": "off_hand",
        "defense": 9,
        "stat_bonuses": {"Defense": 6, "Light_Radius": 25, "Willpower": 4},
        "rarity": "epic",
        "weight": 6,
        "value": 180,
        "set": "shadowbane_arsenal",
        "description": "A shield that radiates divine light, turning away both blade and shadow."
    },
    "holy_symbol": {
        "name": "Holy Symbol",
        "type": "accessory",
        "slot": "neck",
        "stat_bonuses": {"Willpower": 10, "Light_Radius": 15, "Mana_Regen": 8},
        "rarity": "epic",
        "weight": 1,
        "value": 150,
        "set": "shadowbane_arsenal",
        "description": "A sacred symbol that channels divine power, protecting the faithful from evil."
    },
    
    # Astral Archon (Legendary)
    "cosmic_scepter": {
        "name": "Cosmic Scepter",
        "type": "weapon",
        "slot": "main_hand",
        "magic_damage": 45,
        "stat_bonuses": {"Magic": 18, "Willpower": 12, "Ice_Damage": 20},
        "rarity": "legendary",
        "weight": 6,
        "value": 800,
        "set": "astral_archon",
        "description": "A scepter containing the power of dying stars, channeling cosmic forces beyond mortal comprehension."
    },
    "astral_diadem": {
        "name": "Astral Diadem",
        "type": "armor",
        "slot": "head",
        "defense": 8,
        "stat_bonuses": {"Magic": 15, "Willpower": 10, "Mana_Regen": 20},
        "rarity": "legendary",
        "weight": 2,
        "value": 700,
        "set": "astral_archon",
        "description": "A diadem forged from crystallized starlight, granting sight beyond the physical realm."
    },
    "starweave_vestments": {
        "name": "Starweave Vestments",
        "type": "armor",
        "slot": "chest",
        "defense": 10,
        "stat_bonuses": {"Magic": 20, "Willpower": 8, "Mana_Regen": 15},
        "rarity": "legendary",
        "weight": 6,
        "value": 750,
        "set": "astral_archon",
        "description": "Robes woven from the fabric of space itself, shimmering with the light of distant galaxies."
    },
    "voidstep_sandals": {
        "name": "Voidstep Sandals",
        "type": "armor",
        "slot": "feet",
        "defense": 5,
        "stat_bonuses": {"Magic": 10, "Speed": 20, "Mana_Regen": 10},
        "rarity": "legendary",
        "weight": 2,
        "value": 600,
        "set": "astral_archon",
        "description": "Sandals that allow the wearer to step between dimensions, moving through space and time."
    },
    "nebula_cloak": {
        "name": "Nebula Cloak",
        "type": "armor",
        "slot": "back",
        "defense": 6,
        "stat_bonuses": {"Magic": 12, "Willpower": 8, "Ice_Damage": 15},
        "rarity": "legendary",
        "weight": 3,
        "value": 650,
        "set": "astral_archon",
        "description": "A cloak that swirls with cosmic dust and newborn stars, channeling the power of creation."
    },
    "constellation_orb": {
        "name": "Constellation Orb",
        "type": "accessory",
        "slot": "finger",
        "stat_bonuses": {"Magic": 15, "Willpower": 12, "Freeze_Chance": 8},
        "rarity": "legendary",
        "weight": 1,
        "value": 720,
        "set": "astral_archon",
        "description": "An orb containing a miniature constellation, its stars dancing with infinite magical energy."
    },
    
    # ========== CRAFTED BASIC ARMOR ==========
    # Armor crafted from basic materials (fiber, wood, stone, rubble)
    "fiber_vest": {
        "name": "Fiber Vest",
        "type": "armor",
        "slot": "chest",
        "base_defense": 3,
        "stat_bonuses": {"Agility": 1},
        "rarity": "common",
        "weight": 2,
        "value": 8,
        "description": "Woven plant fibers provide basic protection while maintaining mobility."
    },
    "fiber_boots": {
        "name": "Fiber Boots",
        "type": "armor", 
        "slot": "boots",
        "base_defense": 1,
        "stat_bonuses": {"Agility": 2},
        "rarity": "common",
        "weight": 1,
        "value": 5,
        "description": "Light woven boots designed for quiet movement and comfort."
    },
    "wooden_breastplate": {
        "name": "Wooden Breastplate",
        "type": "armor",
        "slot": "chest", 
        "base_defense": 8,
        "stat_bonuses": {"Defense": 2},
        "rarity": "common",
        "weight": 5,
        "value": 15,
        "description": "Carved wooden plates bound with fiber provide solid protection."
    },
    "stone_helm": {
        "name": "Stone Helmet",
        "type": "armor",
        "slot": "helmet",
        "base_defense": 6,
        "stat_bonuses": {"Defense": 3, "Agility": -1},
        "rarity": "uncommon",
        "weight": 4,
        "value": 20,
        "description": "Heavy stone helm with fiber padding - excellent protection but reduces mobility."
    },
    "stone_gauntlets": {
        "name": "Stone Gauntlets",
        "type": "armor",
        "slot": "gloves",
        "base_defense": 4,
        "stat_bonuses": {"Strength": 2, "Agility": -1},
        "rarity": "uncommon", 
        "weight": 3,
        "value": 18,
        "description": "Stone-reinforced gloves that enhance punching power but slow hand movements."
    },
    "rubble_padding": {
        "name": "Rubble Padding",
        "type": "armor",
        "slot": "chest",
        "base_defense": 5,
        "stat_bonuses": {"Defense": 1},
        "rarity": "common",
        "weight": 6,
        "value": 8,
        "description": "Makeshift armor from bound rubble pieces - crude but effective protection."
    },
    
    # ========== INTERMEDIATE EQUIPMENT TIERS ==========
    # These items fill progression gaps to smooth player advancement
    # Added by Equipment Upgrade System - preserves stick mechanics
    
    # MELEE WEAPONS - Fill early progression gaps
    "sharpened_blade": {
        "name": "Sharpened Blade",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 10,
        "stat_bonuses": {"Strength": 1, "Agility": 1},
        "rarity": "common",
        "weight": 3,
        "value": 3,
        "description": "A rusty sword that has been carefully sharpened and cleaned. Better balanced than before."
    },
    "quality_iron_sword": {
        "name": "Quality Iron Sword",
        "type": "weapon",
        "slot": "main_hand", 
        "base_damage": 14,
        "stat_bonuses": {"Strength": 2, "Agility": 1},
        "rarity": "uncommon",
        "weight": 4,
        "value": 4,
        "description": "A well-crafted iron sword with superior balance and edge retention."
    },
    
    # MAGIC WEAPONS - Bridge magic weapon gaps  
    "apprentice_wand": {
        "name": "Apprentice Wand",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 3,
        "magic_damage": 8,
        "stat_bonuses": {"Willpower": 2},
        "rarity": "common",
        "weight": 1,
        "value": 3,
        "description": "A simple wand for beginning spellcasters. Focuses magical energy with basic efficiency."
    },
    "journeyman_staff": {
        "name": "Journeyman Staff",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 5,
        "magic_damage": 11,
        "stat_bonuses": {"Willpower": 3, "Stamina": 1},
        "rarity": "uncommon",
        "weight": 2,
        "value": 5,
        "description": "A well-crafted staff that channels magical energy more effectively than basic wands."
    },
    
    # CRAFTABLE EQUIPMENT
    "wooden_club": {
        "name": "Wooden Club",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 6,
        "stat_bonuses": {"Strength": 1},
        "rarity": "common",
        "weight": 2,
        "value": 1,
        "description": "A simple wooden club, heavy enough to deal decent damage. Crafted from sturdy wood and reinforced with bindings."
    },
    "wooden_shield": {
        "name": "Wooden Shield",
        "type": "armor",
        "slot": "off_hand",
        "defense": 3,
        "stat_bonuses": {"Defense": 1},
        "rarity": "common",
        "weight": 3,
        "value": 1,
        "description": "A basic wooden shield bound with fiber. Provides modest protection for beginning warriors."
    },
    "simple_bow": {
        "name": "Simple Bow",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 8,
        "stat_bonuses": {"Agility": 1},
        "rarity": "common",
        "weight": 2,
        "value": 1,
        "description": "A basic hunting bow made from flexible wood and strung with plant fiber. Reliable for hunting small game."
    },
    "stone_knife": {
        "name": "Stone Knife",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 9,
        "stat_bonuses": {"Strength": 1, "Agility": 1},
        "rarity": "common",
        "weight": 1,
        "value": 1,
        "description": "A sharp blade knapped from quality stone and bound to a wooden handle. Cuts better than wood but duller than metal."
    },
    "stone_spear": {
        "name": "Stone Spear",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 11,
        "stat_bonuses": {"Strength": 2},
        "rarity": "common",
        "weight": 3,
        "value": 1,
        "description": "A long wooden shaft tipped with a sharp stone point. Excellent reach and piercing power."
    },
    "reinforced_shield": {
        "name": "Reinforced Shield",
        "type": "armor",
        "slot": "off_hand",
        "defense": 5,
        "stat_bonuses": {"Defense": 2},
        "rarity": "uncommon",
        "weight": 4,
        "value": 2,
        "description": "A wooden shield reinforced with stone plates and bound with strong fibers. Much sturdier than basic shields."
    },
    "iron_blade": {
        "name": "Iron Blade",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 14,
        "stat_bonuses": {"Strength": 3},
        "rarity": "uncommon",
        "weight": 3,
        "value": 3,
        "description": "A well-forged iron blade with a sharp edge. Made from smelted rubble and tempered with ash."
    },
    "battle_staff": {
        "name": "Battle Staff",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 7,
        "magic_damage": 13,
        "stat_bonuses": {"Magic": 3, "Willpower": 1},
        "rarity": "uncommon",
        "weight": 2,
        "value": 3,
        "description": "A reinforced wooden staff with metal fittings. Channels magical energy while being sturdy enough for combat."
    },
    
    # ARMOR - Fill protection progression gaps
    "padded_cloth": {
        "name": "Padded Cloth",
        "type": "armor",
        "slot": "chest",
        "defense": 2,
        "stat_bonuses": {"Stamina": 1},
        "rarity": "common",
        "weight": 2,
        "value": 1,
        "description": "Thick cloth with padding. Provides minimal protection but better than nothing."
    },
    "reinforced_leather": {
        "name": "Reinforced Leather",
        "type": "armor",
        "slot": "chest", 
        "defense": 5,
        "stat_bonuses": {"Stamina": 2, "Agility": 1},
        "rarity": "uncommon",
        "weight": 4,
        "value": 3,
        "description": "Leather armor with metal studs and reinforced stitching for enhanced protection."
    },
    "light_mail": {
        "name": "Light Mail",
        "type": "armor",
        "slot": "chest",
        "defense": 7,
        "stat_bonuses": {"Stamina": 2, "Defense": 1},
        "rarity": "uncommon", 
        "weight": 6,
        "value": 5,
        "description": "Lightweight chainmail that balances protection with mobility."
    },
    
    # SHIELDS - Bridge shield defense gaps
    "reinforced_buckler": {
        "name": "Reinforced Buckler",
        "type": "shield",
        "slot": "off_hand",
        "defense": 5,
        "stat_bonuses": {"Stamina": 2, "Agility": 1},
        "rarity": "uncommon",
        "weight": 3,
        "value": 2,
        "description": "A small shield with metal reinforcement, offering good protection without hindering movement."
    },
    
    # HEAD ARMOR - Add early game head protection options
    "cloth_hood": {
        "name": "Cloth Hood",
        "type": "armor",
        "slot": "head",
        "defense": 1,
        "stat_bonuses": {"Stealth": 2},
        "rarity": "common",
        "weight": 1,
        "value": 1,
        "description": "A simple hood that provides minimal protection but helps conceal identity."
    },
    "leather_cap": {
        "name": "Leather Cap",
        "type": "armor",
        "slot": "head",
        "defense": 2,
        "stat_bonuses": {"Stamina": 1, "Agility": 1},
        "rarity": "common",
        "weight": 1,
        "value": 2,
        "description": "A flexible leather cap that protects the head without restricting movement."
    },
    "mail_coif": {
        "name": "Mail Coif",
        "type": "armor", 
        "slot": "head",
        "defense": 4,
        "stat_bonuses": {"Stamina": 2},
        "rarity": "uncommon",
        "weight": 3,
        "value": 4,
        "description": "Chainmail head protection that covers the head and neck."
    },
    
    # SET ITEMS - Guardian Set
    "guardian_helmet": {
        "name": "Guardian's Helm",
        "type": "armor",
        "slot": "head",
        "defense": 12,
        "stat_bonuses": {"Stamina": 4},
        "rarity": "set",
        "weight": 4,
        "value": 200,
        "description": "A blessed helm worn by the ancient guardians. Part of the Guardian's Protection set.",
        "set": "guardian_set"
    },
    "guardian_armor": {
        "name": "Guardian's Plate",
        "type": "armor",
        "slot": "chest",
        "defense": 20,
        "stat_bonuses": {"Stamina": 6, "Strength": 2},
        "rarity": "set",
        "weight": 15,
        "value": 350,
        "description": "Heavy plate armor blessed by divine magic. Part of the Guardian's Protection set.",
        "set": "guardian_set"
    },
    "guardian_shield": {
        "name": "Guardian's Aegis",
        "type": "shield",
        "slot": "off_hand",
        "defense": 15,
        "stat_bonuses": {"Stamina": 5},
        "rarity": "set",
        "weight": 8,
        "value": 280,
        "description": "A divine shield that has protected countless heroes. Part of the Guardian's Protection set.",
        "set": "guardian_set"
    },
    
    # SET ITEMS - Shadow Set
    "shadow_cloak": {
        "name": "Shadow Cloak",
        "type": "armor",
        "slot": "chest",
        "defense": 8,
        "stat_bonuses": {"Agility": 5, "Luck": 3},
        "rarity": "set",
        "weight": 3,
        "value": 240,
        "description": "A cloak woven from shadows themselves. Part of the Shadow Walker set.",
        "set": "shadow_set"
    },
    "shadow_boots": {
        "name": "Shadow Stride Boots",
        "type": "armor",
        "slot": "feet",
        "defense": 6,
        "stat_bonuses": {"Agility": 4},
        "rarity": "set",
        "weight": 2,
        "value": 180,
        "description": "Boots that make no sound when walking. Part of the Shadow Walker set.",
        "set": "shadow_set"
    },
    "shadow_dagger": {
        "name": "Shadowfang Dagger",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 18,
        "stat_bonuses": {"Agility": 3, "Luck": 2},
        "rarity": "set",
        "weight": 1,
        "value": 220,
        "description": "A blade forged from crystallized shadows. Part of the Shadow Walker set.",
        "set": "shadow_set"
    },
    
    # SET ITEMS - Arcane Set
    "arcane_staff": {
        "name": "Staff of Arcane Mastery",
        "type": "weapon",
        "slot": "main_hand",
        "base_damage": 12,
        "stat_bonuses": {"Willpower": 6},
        "rarity": "set",
        "weight": 4,
        "value": 320,
        "description": "A staff crackling with arcane energy. Part of the Arcane Mastery set.",
        "set": "arcane_set"
    },
    "arcane_robes": {
        "name": "Robes of Arcane Power",
        "type": "armor",
        "slot": "chest",
        "defense": 5,
        "stat_bonuses": {"Willpower": 5, "Stamina": 2},
        "rarity": "set",
        "weight": 2,
        "value": 280,
        "description": "Robes that amplify magical power. Part of the Arcane Mastery set.",
        "set": "arcane_set"
    },
    "arcane_amulet": {
        "name": "Amulet of Arcane Focus",
        "type": "accessory",
        "slot": "necklace",
        "stat_bonuses": {"Willpower": 4},
        "rarity": "set",
        "weight": 0,
        "value": 200,
        "description": "An amulet that focuses magical energy. Part of the Arcane Mastery set.",
        "set": "arcane_set"
    },
    
    # PLAGUE DOCTOR GEAR (Disease Protection Set)
    "plague_doctor_mask": {
        "name": "Plague Doctor Mask",
        "type": "armor",
        "slot": "head",
        "defense": 2,
        "stat_bonuses": {"Willpower": 2, "Stamina": 1},
        "rarity": "uncommon",
        "weight": 2,
        "value": 150,
        "description": "A distinctive beaked mask filled with aromatic herbs. Provides 30% resistance to disease infection. Part of the Plague Doctor set.",
        "set": "plague_doctor_set",
        "special": "disease_resist_30"
    },
    "plague_doctor_robe": {
        "name": "Plague Doctor Robe",
        "type": "armor",
        "slot": "chest",
        "defense": 4,
        "stat_bonuses": {"Stamina": 3, "Willpower": 2},
        "rarity": "uncommon",
        "weight": 4,
        "value": 200,
        "description": "A long waxed canvas robe that repels disease-carrying fluids. Provides 30% resistance to disease infection. Part of the Plague Doctor set.",
        "set": "plague_doctor_set",
        "special": "disease_resist_30"
    },
    "plague_doctor_gloves": {
        "name": "Plague Doctor Gloves",
        "type": "armor",
        "slot": "hands",
        "defense": 1,
        "stat_bonuses": {"Agility": 1, "Willpower": 1},
        "rarity": "uncommon",
        "weight": 1,
        "value": 100,
        "description": "Thick leather gloves treated with protective oils. Provides 30% resistance to disease infection. Part of the Plague Doctor set.",
        "set": "plague_doctor_set",
        "special": "disease_resist_30"
    },
    
    # DUNGEON INGREDIENTS (For Magical Disease Cures)
    "arcane_crystal": {
        "name": "Arcane Crystal",
        "type": "ingredient",
        "slot": "none",
        "stat_bonuses": {},
        "rarity": "rare",
        "weight": 1,
        "value": 500,
        "description": "A glowing crystal pulsing with raw magical energy. Used to cure Mana Rot and Arcane Flu.",
        "special": "cure_magical_disease"
    },
    "shadow_essence": {
        "name": "Shadow Essence",
        "type": "ingredient",
        "slot": "none",
        "stat_bonuses": {},
        "rarity": "rare",
        "weight": 1,
        "value": 600,
        "description": "Distilled darkness from the deepest dungeons. Used to cure Shadow Plague.",
        "special": "cure_magical_disease"
    },
    "fey_dust": {
        "name": "Fey Dust",
        "type": "ingredient",
        "slot": "none",
        "stat_bonuses": {},
        "rarity": "rare",
        "weight": 0,
        "value": 450,
        "description": "Shimmering dust from fey creatures. Used to cure Fey Fever.",
        "special": "cure_magical_disease"
    },
    "infernal_ash": {
        "name": "Infernal Ash",
        "type": "ingredient",
        "slot": "none",
        "stat_bonuses": {},
        "rarity": "rare",
        "weight": 1,
        "value": 550,
        "description": "Ash from fire-breathing creatures. Used to cure Fire Sneezing Curse.",
        "special": "cure_magical_disease"
    },
    "soul_fragment": {
        "name": "Soul Fragment",
        "type": "ingredient",
        "slot": "none",
        "stat_bonuses": {},
        "rarity": "epic",
        "weight": 0,
        "value": 750,
        "description": "A corrupted fragment of a soul. Used to cure Soul Binding Sickness.",
        "special": "cure_magical_disease"
    }
}

# Add durability values to all equipment
for item_id, item_data in EQUIPMENT_DATA.items():
    # Skip items that shouldn't degrade (like accessories)
    if item_data["type"] in ["weapon", "armor", "shield"]:
        # Base durability depends on item type and rarity
        base_durability = {
            "common": 100,
            "uncommon": 150,
            "rare": 200,
            "epic": 300,
            "legendary": 500,
            "artifact": 1000
        }.get(item_data.get("rarity", "common"), 100)
        
        # Some items are more durable based on type
        if item_data["type"] == "armor":
            if "plate" in item_id or "iron" in item_id:
                base_durability *= 1.5  # Metal armor is more durable
        
        # Add durability to item data
        item_data["max_durability"] = base_durability
        item_data["durability"] = base_durability  # Start at max

# Update existing equipment entries to include set information
for set_id, set_data in EQUIPMENT_SETS.items():
    for piece_id in set_data["pieces"]:
        if piece_id in EQUIPMENT_DATA:
            # Only add set info for items that actually exist
            EQUIPMENT_DATA[piece_id]["set"] = set_id
            
def get_durability_status(item_id):
    """
    Returns a tuple: (status_text, status_color, percent)
    Example: ("Good", (100,255,100), 0.8)
    """
    if item_id not in EQUIPMENT_DATA:
        return ("N/A", (200, 200, 200), 1.0)
    item_data = EQUIPMENT_DATA[item_id]
    durability = item_data.get("durability", 0)
    max_durability = item_data.get("max_durability", 1)
    if max_durability == 0:
        return ("N/A", (200, 200, 200), 1.0)
    percent = durability / max_durability
    if percent > 0.7:
        return ("Good", (100, 255, 100), percent)
    elif percent > 0.3:
        return ("Worn", (255, 255, 100), percent)
    else:
        return ("Broken", (255, 100, 100), percent)
            
def get_active_sets(equipped_items):
    """
    Calculate which equipment sets are active based on equipped items
    Returns a dictionary with set_id: count of equipped pieces
    """
    active_sets = {}
    set_pieces = {}
    
    # Count equipped items from each set
    for slot, item_id in equipped_items.items():
        if item_id and isinstance(item_id, str) and item_id in EQUIPMENT_DATA:    
            item = EQUIPMENT_DATA[item_id]
            if "set" in item:
                set_id = item["set"]
                if set_id not in active_sets:
                    active_sets[set_id] = 0
                    set_pieces[set_id] = []
                active_sets[set_id] += 1
                set_pieces[set_id].append(item_id)
    
    return active_sets, set_pieces

def apply_set_bonuses(player, equipped_items):
    """Apply all active equipment set bonuses to the player"""
    # Reset any previously applied set bonuses (you'll need to track these)
    player.reset_set_bonuses()
    
    # Get active sets
    active_sets, set_pieces = get_active_sets(equipped_items)
    
    # Apply bonuses for each active set
    for set_id, piece_count in active_sets.items():
        set_data = EQUIPMENT_SETS[set_id]
        
        # Apply the highest applicable tier of bonuses
        # (e.g. if 3 pieces are equipped, apply the 3-piece bonus but not the 2-piece bonus)
        if piece_count in set_data["bonuses"]:
            bonuses = set_data["bonuses"][piece_count]
            
            # Apply positive effects (regular stats)
            for stat, value in bonuses["positive"].items():
                player.apply_set_bonus(stat, value)
            
            # Apply negative effects (loot penalties)
            for stat, value in bonuses["negative"].items():
                if stat in ["dubloon_find_rate", "resource_find_rate", "loot_drop_rate"]:
                    # These are percentage penalties (e.g., -0.25 = 25% less loot)
                    player.apply_loot_penalty(stat, value)
                else:
                    # Regular stat penalties
                    player.apply_set_bonus(stat, value)
            
            # Apply special abilities for full sets
            if "special_ability" in bonuses:
                player.apply_special_ability(bonuses["special_ability"], bonuses.get("description", ""))
            
    return active_sets  # Return for UI display

def get_item_description(item_id):
    """Generate a complete item description including set information if applicable"""
    if item_id not in EQUIPMENT_DATA:
        return "Unknown item"
        
    item = EQUIPMENT_DATA[item_id]
    description = item["description"]
    
    # Add set information if this item belongs to a set
    if "set" in item:
        set_id = item["set"]
        set_data = EQUIPMENT_SETS[set_id]
        
        # Add set name and description
        description += f"\n\nPart of the {set_data['name']}\n{set_data['description']}"
        
        # Add set bonuses info
        description += "\n\nSet Bonuses:"
        for piece_count, bonuses in set_data["bonuses"].items():
            description += f"\n{piece_count} Pieces: "
            
            # Positive effects
            pos_effects = [f"+{val}% {stat}" for stat, val in bonuses["positive"].items()]
            description += ", ".join(pos_effects)
            
            # Negative effects
            neg_effects = [f"{val}% {stat}" for stat, val in bonuses["negative"].items()]
            description += " | " + ", ".join(neg_effects)
    
    return description

def reduce_durability(item_id, amount=1):
    """
    Reduce the durability of an item
    
    Args:
        item_id: ID of the equipment
        amount: Amount to reduce durability by (default 1)
        
    Returns:
        tuple: (new_durability, is_broken)
    """
    if item_id not in EQUIPMENT_DATA:
        return 0, True
    
    item = EQUIPMENT_DATA[item_id]
    
    # Skip items that don't have durability
    if "durability" not in item:
        return None, False
        
    # Reduce durability
    item["durability"] = max(0, item["durability"] - amount)
    
    # Check if item is broken
    is_broken = item["durability"] <= 0
    
    return item["durability"], is_broken

def get_durability_status(item_id):
    """
    Get the status of an item based on its durability
    
    Args:
        item_id: ID of the equipment
        
    Returns:
        tuple: (status_text, color, performance_multiplier)
    """
    if item_id not in EQUIPMENT_DATA:
        return "Unknown", (150, 150, 150), 1.0
    
    item = EQUIPMENT_DATA[item_id]
    
    # Items without durability are always in perfect condition
    if "durability" not in item or "max_durability" not in item:
        return "Perfect", (0, 255, 0), 1.0
        
    # Calculate percentage
    durability_percent = (item["durability"] / item["max_durability"]) * 100
    
    # Determine status and performance multiplier
    if durability_percent <= 0:
        return "Broken", (150, 0, 0), 0.0
    elif durability_percent < 20:
        return "Severely Damaged", (255, 0, 0), 0.5
    elif durability_percent < 40:
        return "Damaged", (255, 150, 0), 0.75
    elif durability_percent < 70:
        return "Worn", (255, 255, 0), 0.9
    elif durability_percent < 90:
        return "Good", (150, 255, 150), 1.0
    else:
        return "Excellent", (0, 255, 0), 1.0

def repair_item(item_id, amount=None):
    """
    Repair an item's durability
    
    Args:
        item_id: ID of the equipment to repair
        amount: Amount to repair (if None, fully repair)
        
    Returns:
        new_durability: The item's durability after repair
    """
    if item_id not in EQUIPMENT_DATA:
        return 0
    
    item = EQUIPMENT_DATA[item_id]
    
    # Skip items that don't have durability
    if "durability" not in item or "max_durability" not in item:
        return None
        
    # Repair the item
    if amount is None:
        item["durability"] = item["max_durability"]  # Full repair
    else:
        item["durability"] = min(item["max_durability"], item["durability"] + amount)
        
    return item["durability"]

def get_repair_cost(item_id, full_repair=True):
    """
    Calculate the cost to repair an item
    
    Args:
        item_id: ID of the equipment to repair
        full_repair: Whether to calculate cost for full repair
        
    Returns:
        tuple: (cost, materials_required)
    """
    if item_id not in EQUIPMENT_DATA:
        return 0, {}
    
    item = EQUIPMENT_DATA[item_id]
    
    # Skip items that don't have durability
    if "durability" not in item or "max_durability" not in item:
        return 0, {}
        
    # Calculate repair amount
    if full_repair:
        repair_amount = item["max_durability"] - item["durability"]
    else:
        repair_amount = min(item["max_durability"] - item["durability"], 
                          item["max_durability"] * 0.25)  # Repair 25% at a time
    
    # No repair needed
    if repair_amount <= 0:
        return 0, {}
        
    # Base cost on item value and amount of repair needed
    base_cost = item.get("value", 10)
    repair_percent = repair_amount / item["max_durability"]
    cost = int(base_cost * repair_percent * 0.4)  # 40% of value for full repair
    
    # Materials required based on item type
    materials = {}
    if "type" in item:
        if item["type"] == "weapon":
            materials = {"metal_scrap": int(repair_percent * 3) + 1}
        elif item["type"] == "armor":
            if "leather" in item_id:
                materials = {"leather_scraps": int(repair_percent * 3) + 1}
            else:
                materials = {"metal_scrap": int(repair_percent * 2) + 1, 
                           "cloth": int(repair_percent * 1) + 1}
        elif item["type"] == "shield":
            materials = {"wood": int(repair_percent * 2) + 1, 
                       "metal_scrap": int(repair_percent * 1) + 1}
    
    return cost, materials

# Add this to equipment.py
EQUIPMENT_CATEGORIES = {
    "metal": ["iron_sword", "iron_helmet", "iron_chestplate", "iron_leggings", "iron_boots", 
              "steel_sword", "steel_shield", "enchanted_knight", "crystal_golem"],
    
    "leather": ["leather_cap", "leather_tunic", "leather_pants", "ranger_boots", "hunting_bow"],
    
    "cloth": ["wizard_hat", "mage_robe", "enchanted_leggings", "magical_boots"],
    
    "wood": ["wooden_staff", "wooden_bow", "wooden_shield", "arcane_staff"]
}

# Function to get equipment category
def get_equipment_category(item_id):
    """Return the material category for a given equipment item"""
    for category, items in EQUIPMENT_CATEGORIES.items():
        if item_id in items:
            return category
    
    # Try to determine category from item name if not explicitly listed
    if "iron" in item_id or "steel" in item_id or "metal" in item_id or "sword" in item_id:
        return "metal"
    elif "leather" in item_id:
        return "leather"
    elif "robe" in item_id or "cloth" in item_id:
        return "cloth"
    elif "wood" in item_id or "staff" in item_id or "bow" in item_id:
        return "wood"
        
    return "unknown"

# Add this to equipment.py
def get_repair_efficiency(target_id, donor_id):
    """
    Calculate repair efficiency between two equipment pieces
    
    Returns:
        float: Efficiency ratio (0.0-1.0)
    """
    # Exact match is most efficient
    if target_id == donor_id:
        return 1.0
    
    # Same category is moderately efficient
    target_category = get_equipment_category(target_id)
    donor_category = get_equipment_category(donor_id)
    
    if target_category == donor_category:
        return 0.5  # 50% efficiency
    
    # Different categories are least efficient
    return 0.25  # 25% efficiency

# Add this to equipment.py
def repair_with_equipment(target_id, donor_id):
    """
    Repair target equipment using donor equipment
    
    Args:
        target_id (str): Equipment ID to repair
        donor_id (str): Equipment ID to use as repair material
    
    Returns:
        tuple: (durability_gained, max_durability) or (0, 0) if repair failed
    """
    # Get equipment data
    if target_id not in EQUIPMENT_DATA or donor_id not in EQUIPMENT_DATA:
        return 0, 0
    
    target = EQUIPMENT_DATA[target_id]
    donor = EQUIPMENT_DATA[donor_id]
    
    # Check if both have durability
    if "durability" not in target or "max_durability" not in target:
        return 0, 0
    if "durability" not in donor or "max_durability" not in donor:
        return 0, 0
    
    # Calculate repair amount based on donor's durability and efficiency
    efficiency = get_repair_efficiency(target_id, donor_id)
    donor_durability = donor["durability"]
    repair_amount = donor_durability * efficiency
    
    # Apply repair up to max durability
    max_durability = target["max_durability"]
    current_durability = target["durability"]
    new_durability = min(current_durability + repair_amount, max_durability)
    durability_gained = new_durability - current_durability
    
    # Update target durability
    target["durability"] = new_durability
    
    return durability_gained, max_durability

def get_scaled_equipment_stats(item_id, player_level):
    """
    Return equipment stats scaled by player level.
    Scaling increases base stats by a percentage per level.
    """
    if item_id not in EQUIPMENT_DATA:
        return {}
    item = EQUIPMENT_DATA[item_id].copy()
    scale_factor = 1.0 + (player_level - 1) * 0.05  # 5% per level above 1

    # Scale base_damage, magic_damage, defense, stat_bonuses
    for key in ["base_damage", "magic_damage", "defense"]:
        if key in item:
            item[key] = int(item[key] * scale_factor)
    if "stat_bonuses" in item:
        item["stat_bonuses"] = {stat: int(val * scale_factor) for stat, val in item["stat_bonuses"].items()}
    return item

class Equipment:
    def __init__(self, owner=None):
        self.owner = owner
        # Dictionary to store equipped items by slot
        self.equipped = {
            "head": None,
            "chest": None,
            "legs": None,
            "feet": None,
            "main_hand": None,
            "off_hand": None,
            "ring": None,
            "necklace": None,
            "hands": None
        }
        
        # Track active set bonuses
        self.active_sets = {}
        self.set_pieces = {}
        
        # Equipment loadouts system
        self.loadouts = {}  # Dictionary: loadout_name -> equipped items dict
        self.max_loadouts = 10  # Maximum number of loadouts per player
    
    def equip_item(self, item_id, inventory):
        """
        Equip an item from inventory

        Args:
            item_id (str): ID of the item to equip
            inventory (Inventory): Player's inventory object

        Returns:
            tuple: (success, message)
        """
        # Special logic for stacking sticks
        if item_id == "stick":
            stick_count = inventory.get("stick", 0)
            if stick_count <= 0:
                return False, "You don't have any sticks"
            slot = "main_hand"
            # Unequip current item in that slot if any
            currently_equipped = self.equipped[slot]
            if currently_equipped:
                # Only add string items back to inventory, not dicts
                if isinstance(currently_equipped, dict) and currently_equipped.get("item") == "stick":
                    inventory.add_item("stick", currently_equipped.get("stack_count", 1))
                else:
                    inventory.add_item(currently_equipped)
            # Equip all sticks as a stack
            self.equipped[slot] = {"item": "stick", "stack_count": stick_count}
            inventory.remove_item("stick", stick_count)  # Remove all sticks from inventory
            self.active_sets, self.set_pieces = get_active_sets(self.equipped)
            return True, f"Equipped Stick x{stick_count}!"

        # --- original code for other items ---
        if item_id not in EQUIPMENT_DATA:
            return False, f"Unknown item: {item_id}"

        item_data = EQUIPMENT_DATA[item_id]

        if "slot" not in item_data:
            return False, f"{item_id} cannot be equipped"

        slot = item_data["slot"]

        if slot not in self.equipped:
            return False, f"No {slot} equipment slot available"

        if not inventory.has_item(item_id):
            return False, f"You don't have {item_id}"

        currently_equipped = self.equipped[slot]
        if currently_equipped:
            # Only add string items back to inventory, not dicts
            if isinstance(currently_equipped, dict) and currently_equipped.get("item") == "stick":
                inventory.add_item("stick", currently_equipped.get("stack_count", 1))
            else:
                inventory.add_item(currently_equipped)

        self.equipped[slot] = item_id
        inventory.remove_item(item_id)

        self.active_sets, self.set_pieces = get_active_sets(self.equipped)

        return True, f"Equipped {item_id}"

    def unequip_item(self, slot, inventory):
        """
        Unequip an item from a specified slot and put it in inventory

        Args:
            slot (str): Equipment slot to unequip from
            inventory (Inventory): Player's inventory object

        Returns:
            tuple: (success, message)
        """
        # Check if the slot exists
        if slot not in self.equipped:
            return False, f"Invalid equipment slot: {slot}"

        # Check if there's anything equipped in that slot
        item_id = self.equipped[slot]
        if not item_id:
            return False, f"Nothing equipped in {slot}"

        # Special logic for unequipping a stack of sticks
        if isinstance(item_id, dict) and item_id.get("item") == "stick":
            stack_count = item_id.get("stack_count", 1)
            inventory.add_item("stick", stack_count)
            self.equipped[slot] = None
            self.active_sets, self.set_pieces = get_active_sets(self.equipped)
            return True, f"Unequipped Stick x{stack_count} from {slot}"

        # Add the item to inventory (normal equipment)
        inventory.add_item(item_id)
        self.equipped[slot] = None
        self.active_sets, self.set_pieces = get_active_sets(self.equipped)
        return True, f"Unequipped {item_id} from {slot}"
    
    def update_stats(self, stats, player_level):
        """
        Update a Stats component with bonuses from equipment
        
        Args:
            stats (Stats): Stats component to update
            player_level (int): Player level for scaling equipment stats
        """
        # Import from within the method to avoid circular imports
        from stats import Stats
        
        # Make sure the input is a Stats object
        if not isinstance(stats, Stats):
            return
            
        # Calculate all equipment bonuses and update the stats component
        stats.update_equipment_bonuses(self, player_level)
        
        # Update active set bonuses
        self.active_sets, self.set_pieces = get_active_sets(self.equipped)
        
    def get_active_set_bonuses(self):
        """Return the bonuses for currently active sets."""
        bonuses = {}
        for set_id, piece_count in self.active_sets.items():
            set_data = EQUIPMENT_SETS[set_id]
            if piece_count in set_data["bonuses"]:
                bonuses[set_id] = set_data["bonuses"][piece_count]
        return bonuses
    
    def get_equipped_item(self, slot):
        """
        Returns the item equipped in the given slot, or None if empty.
        Example slots: "main_hand", "off_hand", "head", etc.
        """
        return self.equipped.get(slot, None)
    
    # ===== EQUIPMENT LOADOUT SYSTEM =====
    
    def save_loadout(self, loadout_name):
        """
        Save current equipment configuration as a named loadout.
        
        Args:
            loadout_name (str): Name for this loadout
            
        Returns:
            tuple: (success, message)
        """
        # Validate loadout name
        if not loadout_name or not loadout_name.strip():
            return False, "Loadout name cannot be empty"
        
        loadout_name = loadout_name.strip()
        
        # Check if max loadouts reached (only for new loadouts)
        if loadout_name not in self.loadouts and len(self.loadouts) >= self.max_loadouts:
            return False, f"Maximum loadouts ({self.max_loadouts}) reached"
        
        # Deep copy current equipment state
        loadout_data = {}
        for slot, item in self.equipped.items():
            if item is not None:
                # Handle stick stacking special case
                if isinstance(item, dict) and item.get("item") == "stick":
                    loadout_data[slot] = {
                        "item": "stick",
                        "stack_count": item.get("stack_count", 1)
                    }
                else:
                    loadout_data[slot] = item
            else:
                loadout_data[slot] = None
        
        # Save the loadout
        self.loadouts[loadout_name] = loadout_data
        
        action = "updated" if loadout_name in self.loadouts else "saved"
        return True, f"Loadout '{loadout_name}' {action} successfully!"
    
    def load_loadout(self, loadout_name, inventory):
        """
        Load a saved equipment loadout.
        
        Args:
            loadout_name (str): Name of the loadout to load
            inventory (Inventory): Player's inventory object
            
        Returns:
            tuple: (success, message)
        """
        # Check if loadout exists
        if loadout_name not in self.loadouts:
            return False, f"Loadout '{loadout_name}' not found"
        
        loadout_data = self.loadouts[loadout_name]
        
        # First, unequip all current items and return them to inventory
        for slot, item in list(self.equipped.items()):
            if item is not None:
                # Handle stick stacking
                if isinstance(item, dict) and item.get("item") == "stick":
                    stack_count = item.get("stack_count", 1)
                    inventory.add_item("stick", stack_count)
                else:
                    inventory.add_item(item)
                self.equipped[slot] = None
        
        # Now equip items from the loadout
        missing_items = []
        for slot, item in loadout_data.items():
            if item is not None:
                # Handle stick stacking
                if isinstance(item, dict) and item.get("item") == "stick":
                    stack_count = item.get("stack_count", 1)
                    available_sticks = inventory.get("stick", 0)
                    
                    if available_sticks < stack_count:
                        missing_items.append(f"stick x{stack_count} (have {available_sticks})")
                        # Equip what we have
                        if available_sticks > 0:
                            self.equipped[slot] = {"item": "stick", "stack_count": available_sticks}
                            inventory.remove_item("stick", available_sticks)
                    else:
                        self.equipped[slot] = {"item": "stick", "stack_count": stack_count}
                        inventory.remove_item("stick", stack_count)
                else:
                    # Regular equipment
                    if inventory.has_item(item):
                        self.equipped[slot] = item
                        inventory.remove_item(item)
                    else:
                        missing_items.append(item)
        
        # Update set bonuses
        self.active_sets, self.set_pieces = get_active_sets(self.equipped)
        
        # Generate result message
        if missing_items:
            return True, f"Loadout '{loadout_name}' loaded (missing: {', '.join(missing_items)})"
        else:
            return True, f"Loadout '{loadout_name}' loaded successfully!"
    
    def delete_loadout(self, loadout_name):
        """
        Delete a saved loadout.
        
        Args:
            loadout_name (str): Name of the loadout to delete
            
        Returns:
            tuple: (success, message)
        """
        if loadout_name not in self.loadouts:
            return False, f"Loadout '{loadout_name}' not found"
        
        del self.loadouts[loadout_name]
        return True, f"Loadout '{loadout_name}' deleted successfully!"
    
    def list_loadouts(self):
        """
        Get a list of all saved loadout names.
        
        Returns:
            list: List of loadout names
        """
        return list(self.loadouts.keys())
    
    def get_loadout_preview(self, loadout_name):
        """
        Get a preview of what items are in a loadout.
        
        Args:
            loadout_name (str): Name of the loadout
            
        Returns:
            dict: Dictionary of slot -> item_id, or None if loadout doesn't exist
        """
        if loadout_name not in self.loadouts:
            return None
        
        return self.loadouts[loadout_name].copy()
    
    def rename_loadout(self, old_name, new_name):
        """
        Rename a loadout.
        
        Args:
            old_name (str): Current loadout name
            new_name (str): New loadout name
            
        Returns:
            tuple: (success, message)
        """
        if old_name not in self.loadouts:
            return False, f"Loadout '{old_name}' not found"
        
        if not new_name or not new_name.strip():
            return False, "New loadout name cannot be empty"
        
        new_name = new_name.strip()
        
        if new_name in self.loadouts:
            return False, f"Loadout '{new_name}' already exists"
        
        # Rename the loadout
        self.loadouts[new_name] = self.loadouts[old_name]
        del self.loadouts[old_name]
        
        return True, f"Loadout renamed from '{old_name}' to '{new_name}'"