"""
Basic Spell Definitions
Simple spell data for the game
"""

SPELLS = {
    # Basic attack spells
    "fireball": {
        "name": "Fireball",
        "description": "Launch a ball of fire at your enemies",
        "damage": 25,
        "mana_cost": 15,
        "cooldown": 2.0,
        "type": "projectile",
        "element": "fire",
        "range": 300
    },
    "ice_shard": {
        "name": "Ice Shard",
        "description": "Fire a sharp shard of ice",
        "damage": 20,
        "mana_cost": 12,
        "cooldown": 1.5,
        "type": "projectile",
        "element": "ice",
        "range": 250,
        "effects": ["slow"]
    },
    "lightning_bolt": {
        "name": "Lightning Bolt",
        "description": "Strike enemies with lightning",
        "damage": 30,
        "mana_cost": 20,
        "cooldown": 3.0,
        "type": "instant",
        "element": "lightning",
        "range": 400
    },
    
    # Utility spells
    "heal": {
        "name": "Heal",
        "description": "Restore health over time",
        "healing": 30,
        "mana_cost": 25,
        "cooldown": 5.0,
        "type": "self",
        "duration": 3
    },
    "shield": {
        "name": "Shield",
        "description": "Create a protective barrier",
        "shield_amount": 50,
        "mana_cost": 20,
        "cooldown": 10.0,
        "type": "self",
        "duration": 5
    },
    "teleport": {
        "name": "Teleport",
        "description": "Instantly move to target location",
        "mana_cost": 30,
        "cooldown": 8.0,
        "type": "movement",
        "range": 200
    },
    
    # Advanced spells
    "water_splash": {
        "name": "Water Splash",
        "description": "Create a wave of water",
        "damage": 15,
        "mana_cost": 10,
        "cooldown": 1.0,
        "type": "aoe",
        "element": "water",
        "aoe_radius": 80
    },
    "wind_gust": {
        "name": "Wind Gust",
        "description": "Push enemies back with wind",
        "damage": 10,
        "mana_cost": 15,
        "cooldown": 2.5,
        "type": "aoe",
        "element": "wind",
        "effects": ["knockback"],
        "aoe_radius": 100
    },
    "blessing": {
        "name": "Blessing",
        "description": "Increase stats temporarily",
        "mana_cost": 35,
        "cooldown": 15.0,
        "type": "self",
        "duration": 10,
        "effects": ["damage_boost", "speed_boost"]
    },
    
    # Summon spells
    "summon_wolf": {
        "name": "Summon Wolf",
        "description": "Summon a wolf companion",
        "mana_cost": 40,
        "cooldown": 20.0,
        "type": "summon",
        "summon_type": "wolf",
        "summon_duration": 30
    },
    "summon_fire_elemental": {
        "name": "Summon Fire Elemental",
        "description": "Summon a blazing fire elemental",
        "mana_cost": 50,
        "cooldown": 25.0,
        "type": "summon",
        "summon_type": "fire_elemental",
        "summon_duration": 30
    },
    "summon_ice_elemental": {
        "name": "Summon Ice Elemental",
        "description": "Summon a freezing ice elemental",
        "mana_cost": 50,
        "cooldown": 25.0,
        "type": "summon",
        "summon_type": "ice_elemental",
        "summon_duration": 30
    },
    "summon_lightning_elemental": {
        "name": "Summon Lightning Elemental",
        "description": "Summon a shocking lightning elemental",
        "mana_cost": 55,
        "cooldown": 25.0,
        "type": "summon",
        "summon_type": "lightning_elemental",
        "summon_duration": 25
    },
    "summon_demon": {
        "name": "Summon Demon",
        "description": "Summon a powerful demon from the abyss",
        "mana_cost": 80,
        "cooldown": 45.0,
        "type": "summon",
        "summon_type": "demon",
        "summon_duration": 40
    },
    
    # Necromancy spells
    "raise_dead": {
        "name": "Raise Dead",
        "description": "Raise a nearby corpse as undead servant",
        "mana_cost": 35,
        "cooldown": 15.0,
        "type": "necromancy",
        "summon_duration": 60,
        "range": 100
    },
    "animate_skeleton": {
        "name": "Animate Skeleton",
        "description": "Create a skeleton warrior from bones",
        "mana_cost": 30,
        "cooldown": 12.0,
        "type": "summon",
        "summon_type": "skeleton",
        "summon_duration": 45
    },
    "summon_zombie": {
        "name": "Summon Zombie",
        "description": "Raise a shambling zombie minion",
        "mana_cost": 35,
        "cooldown": 15.0,
        "type": "summon",
        "summon_type": "zombie",
        "summon_duration": 50
    },
    "summon_ghost": {
        "name": "Summon Ghost",
        "description": "Call forth a vengeful spirit",
        "mana_cost": 45,
        "cooldown": 20.0,
        "type": "summon",
        "summon_type": "ghost",
        "summon_duration": 35
    },
    "summon_bone_golem": {
        "name": "Summon Bone Golem",
        "description": "Create a massive bone construct",
        "mana_cost": 70,
        "cooldown": 40.0,
        "type": "summon",
        "summon_type": "bone_golem",
        "summon_duration": 60
    },
    "mass_raise_dead": {
        "name": "Mass Raise Dead",
        "description": "Raise all nearby corpses as undead army",
        "mana_cost": 100,
        "cooldown": 60.0,
        "type": "necromancy",
        "summon_duration": 45,
        "range": 200,
        "max_raises": 5
    },
    "empower_undead": {
        "name": "Empower Undead",
        "description": "Boost all summoned creatures' power",
        "mana_cost": 40,
        "cooldown": 30.0,
        "type": "buff",
        "duration": 20,
        "effects": ["damage_boost", "speed_boost"]
    }
}

# Starter spells that player begins with
STARTER_SPELLS = ["fireball", "heal"]

def get_spell(spell_id):
    """Get spell data by ID"""
    return SPELLS.get(spell_id, None)

def get_all_spells():
    """Get all available spells"""
    return SPELLS.copy()

def get_spell_names():
    """Get list of all spell names"""
    return list(SPELLS.keys())
