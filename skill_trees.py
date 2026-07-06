# This file contains all skill tree definitions and related functions

# Main skill tree data structure
SKILL_TREES = {
    "Warrior": {
    "description": "Masters of physical combat and defense",
    "primary_stats": ["Strength", "Stamina"],
    "tiers": [
        # Tier 1
        {
            "strength_training": {
                "name": "Strength Training",
                "description": "Rigorous training increases physical might.",
                "effects": {"melee_damage_percent": 5},
                "cost": 2,
                "stat_requirements": {"Strength": 5},
                "icon": "strength_icon",
                "type": "passive",
                "max_points": 5,
                "per_point_effect": {"melee_damage_percent": 1}
            },
            "toughness": {
                "name": "Toughness",
                "description": "Hardened body increases maximum health.",
                "effects": {"max_health_percent": 5},
                "cost": 2,
                "stat_requirements": {"Strength": 5},
                "icon": "toughness_icon",
                "type": "passive",
                "max_points": 5,
                "per_point_effect": {"max_health_percent": 1}
            },
            "combat_reflexes": {
                "name": "Combat Reflexes",
                "description": "Improved reaction time helps avoid attacks.",
                "effects": {"dodge_chance": 5},
                "cost": 2,
                "stat_requirements": {"Strength": 5},
                "icon": "reflexes_icon",
                "type": "passive",
                "max_points": 5,
                "per_point_effect": {"dodge_chance": 1}
            }
        },
        # Tier 2
        {
            "mighty_strike": {
                "name": "Mighty Strike",
                "description": "Channel strength into a powerful blow.",
                "effects": {"attack_damage_percent": 25},
                "cost": 3,
                "stat_requirements": {"Strength": 10, "Stamina": 8},
                "icon": "mighty_strike_icon",
                "type": "active",
                "cooldown": 8,
                "max_points": 3,
                "per_point_effect": {"attack_damage_percent": 8}
            },
            "shield_expert": {
                "name": "Shield Expert",
                "description": "Master shield techniques for better defense.",
                "effects": {"block_chance": 10},
                "cost": 3,
                "stat_requirements": {"Strength": 10, "Stamina": 8},
                "icon": "shield_icon",
                "type": "passive",
                "max_points": 5,
                "per_point_effect": {"block_chance": 2}
            },
            "weapon_specialization": {
                "name": "Weapon Specialization",
                "description": "Specialize in a weapon type for increased damage.",
                "effects": {"weapon_damage_percent": 10},
                "cost": 4,
                "stat_requirements": {"Strength": 10, "Stamina": 8},
                "icon": "weapon_spec_icon",
                "type": "passive",
                "choose_option": ["sword", "axe", "dagger", "spear"],
                "max_points": 5,
                "per_point_effect": {"weapon_damage_percent": 2}
            }
        },
        # Tier 3
        {
            "berserker_rage": {
                "name": "Berserker Rage",
                "description": "Enter a state of rage to boost damage output.",
                "effects": {"damage_boost_percent": 15},
                "cost": 5,
                "stat_requirements": {"Strength": 15, "Stamina": 12},
                "icon": "rage_icon",
                "type": "active",
                "cooldown": 30,
                "duration": 5,
                "max_points": 3,
                "per_point_effect": {"damage_boost_percent": 5}
            },
            "cleave": {
                "name": "Cleave",
                "description": "Attacks have a chance to hit adjacent enemies.",
                "effects": {"cleave_chance": 25},
                "cost": 5,
                "stat_requirements": {"Strength": 15, "Stamina": 12},
                "icon": "cleave_icon",
                "type": "passive",
                "max_points": 5,
                "per_point_effect": {"cleave_chance": 5}
            },
            "second_wind": {
                "name": "Second Wind",
                "description": "Regain health when critically injured.",
                "effects": {"health_recovery_percent": 15, "health_threshold_percent": 25},
                "cost": 6,
                "stat_requirements": {"Strength": 15, "Stamina": 12},
                "icon": "second_wind_icon",
                "type": "passive",
                "cooldown": 60,
                "max_points": 3,
                "per_point_effect": {"health_recovery_percent": 5}
            }
        },
        # Tier 4
        {
            "devastating_blow": {
                "name": "Devastating Blow",
                "description": "Critical hits can deal massively increased damage.",
                "effects": {"critical_damage_multiplier": 3, "critical_chance_bonus": 10},
                "cost": 7,
                "stat_requirements": {"Strength": 25, "Stamina": 20},
                "icon": "devastating_blow_icon",
                "type": "passive",
                "max_points": 3,
                "per_point_effect": {"critical_damage_multiplier": 1, "critical_chance_bonus": 3}
            },
            "unwavering_stance": {
                "name": "Unwavering Stance",
                "description": "Defensive stance reduces incoming damage when injured.",
                "effects": {"damage_reduction_percent": 10, "health_threshold_percent": 50},
                "cost": 8,
                "stat_requirements": {"Strength": 25, "Stamina": 20},
                "icon": "stance_icon",
                "type": "passive",
                "max_points": 5,
                "per_point_effect": {"damage_reduction_percent": 2}
            }
        },
        # Tier 5
        {
            "battle_master": {
                "name": "Battle Master",
                "description": "Become invulnerable briefly and deal double damage.",
                "effects": {"invulnerable_duration": 3, "damage_multiplier": 2},
                "cost": 10,
                "stat_requirements": {"Strength": 35, "Stamina": 25},
                "icon": "master_icon",
                "type": "active",
                "cooldown": 120,
                "max_points": 2,
                "per_point_effect": {"invulnerable_duration": 1, "damage_multiplier": 0.5}
            }
        }
    ]
},
    "Mage": {
        "description": "Masters of magical arts and spellcasting",
        "primary_stats": ["Willpower"],
        "tiers": [
            # Tier 1
            {
                "mana_pool": {
                    "name": "Mana Pool",
                    "description": "Expand your capacity for magical energy.",
                    "effects": {"max_mana_percent": 5},
                    "cost": 2,
                    "stat_requirements": {"Willpower": 5},
                    "icon": "mana_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"max_mana_percent": 1}
                },
                "spell_efficiency": {
                    "name": "Spell Efficiency",
                    "description": "Cast spells with less magical energy.",
                    "effects": {"spell_cost_reduction": 5},
                    "cost": 2,
                    "stat_requirements": {"Willpower": 5},
                    "icon": "efficiency_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"spell_cost_reduction": 1}
                },
                "elemental_basics": {
                    "name": "Elemental Basics",
                    "description": "Fundamental understanding of elemental magic.",
                    "effects": {"elemental_damage_percent": 5},
                    "cost": 2,
                    "stat_requirements": {"Willpower": 5},
                    "icon": "elemental_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"elemental_damage_percent": 1}
                }
            },
            # Tier 2
            {
                "mana_shield": {
                    "name": "Mana Shield",
                    "description": "Convert incoming damage to mana loss.",
                    "effects": {"damage_to_mana_percent": 50},
                    "cost": 3,
                    "stat_requirements": {"Willpower": 12},
                    "icon": "mana_shield_icon",
                    "type": "active",
                    "cooldown": 15,
                    "duration": 8,
                    "max_points": 5,
                    "per_point_effect": {"damage_to_mana_percent": 10}
                },
                "spell_focus": {
                    "name": "Spell Focus",
                    "description": "Improve concentration for more powerful spells.",
                    "effects": {"spell_damage_percent": 10},
                    "cost": 3,
                    "stat_requirements": {"Willpower": 12},
                    "icon": "focus_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"spell_damage_percent": 2}
                },
                "elemental_specialization": {
                    "name": "Elemental Specialization",
                    "description": "Specialize in an element for increased damage.",
                    "effects": {"specialized_element_damage_percent": 10},
                    "cost": 4,
                    "stat_requirements": {"Willpower": 12},
                    "icon": "specialization_icon",
                    "type": "passive",
                    "choose_option": ["fire", "frost", "lightning", "arcane"],
                    "max_points": 5,
                    "per_point_effect": {"specialized_element_damage_percent": 2}
                }
            },
            # Tier 3
            {
                "arcane_recovery": {
                    "name": "Arcane Recovery",
                    "description": "Recover mana when defeating enemies.",
                    "effects": {"mana_recovery_percent": 5},
                    "cost": 5,
                    "stat_requirements": {"Willpower": 20},
                    "icon": "recovery_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"mana_recovery_percent": 1}
                },
                "spell_echo": {
                    "name": "Spell Echo",
                    "description": "Chance to cast spells twice.",
                    "effects": {"spell_echo_chance": 10},
                    "cost": 5,
                    "stat_requirements": {"Willpower": 20},
                    "icon": "echo_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"spell_echo_chance": 2}
                },
                "elemental_mastery": {
                    "name": "Elemental Mastery",
                    "description": "Mastery over your chosen element.",
                    "effects": {"elemental_mastery_damage_percent": 15},
                    "cost": 6,
                    "stat_requirements": {"Willpower": 20},
                    "icon": "mastery_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"elemental_mastery_damage_percent": 3}
                }
            },
            # Tier 4
            {
                "spell_weaving": {
                    "name": "Spell Weaving",
                    "description": "Sequential spellcasting increases damage.",
                    "effects": {"sequential_spell_bonus": 15},
                    "cost": 7,
                    "stat_requirements": {"Willpower": 30},
                    "icon": "weaving_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"sequential_spell_bonus": 3}
                },
                "mana_attunement": {
                    "name": "Mana Attunement",
                    "description": "Low mana enhances spell damage.",
                    "effects": {"low_mana_damage_bonus": 15, "mana_threshold_percent": 25},
                    "cost": 8,
                    "stat_requirements": {"Willpower": 30},
                    "icon": "attunement_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"low_mana_damage_bonus": 3}
                }
            },
            # Tier 5
            {
                "archmage_power": {
                    "name": "Archmage's Power",
                    "description": "Cast spells without mana cost temporarily.",
                    "effects": {"free_casting_duration": 10},
                    "cost": 10,
                    "stat_requirements": {"Willpower": 40},
                    "icon": "archmage_icon",
                    "type": "active",
                    "cooldown": 120,
                    "max_points": 3,
                    "per_point_effect": {"free_casting_duration": 3.3}
                }
            }
        ]
    }, 
    "Survivalist": {
        "description": "Masters of resource gathering, crafting and survival",
        "primary_stats": ["Luck", "Stamina"],
        "tiers": [
            # Tier 1
            {
                "resource_sensing": {
                    "name": "Resource Sensing",
                    "description": "Detect resources from greater distances.",
                    "effects": {"resource_detection_range": 25},
                    "cost": 2,
                    "stat_requirements": {"Luck": 5},
                    "icon": "sensing_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"resource_detection_range": 5}
                },
                "efficient_gathering": {
                    "name": "Efficient Gathering",
                    "description": "Gather more resources with each attempt.",
                    "effects": {"gathering_yield_percent": 10},
                    "cost": 2,
                    "stat_requirements": {"Luck": 5},
                    "icon": "gathering_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"gathering_yield_percent": 2}
                },
                "basic_crafting": {
                    "name": "Basic Crafting",
                    "description": "Fundamental crafting knowledge reduces material needs.",
                    "effects": {"crafting_cost_reduction": 5},
                    "cost": 2,
                    "stat_requirements": {"Luck": 5},
                    "icon": "crafting_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"crafting_cost_reduction": 1}
                }
            },
            # Tier 2
            {
                "herbalism": {
                    "name": "Herbalism",
                    "description": "Knowledge of herbs improves healing item effects.",
                    "effects": {"healing_item_bonus": 10},
                    "cost": 3,
                    "stat_requirements": {"Luck": 8, "Stamina": 8},
                    "icon": "herb_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"healing_item_bonus": 2}
                },
                "advanced_gathering": {
                    "name": "Advanced Gathering",
                    "description": "Chance to find double resources when gathering.",
                    "effects": {"double_gather_chance": 10},
                    "cost": 3,
                    "stat_requirements": {"Luck": 8, "Stamina": 8},
                    "icon": "advanced_gathering_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"double_gather_chance": 2}
                },
                "material_knowledge": {
                    "name": "Material Knowledge",
                    "description": "Understanding of materials improves crafted item quality.",
                    "effects": {"crafted_item_quality": 5},
                    "cost": 4,
                    "stat_requirements": {"Luck": 8, "Stamina": 8},
                    "icon": "material_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"crafted_item_quality": 1}
                }
            },
            # Tier 3
            {
                "alchemist": {
                    "name": "Alchemist",
                    "description": "Create potions with extended duration.",
                    "effects": {"potion_duration_percent": 25},
                    "cost": 5,
                    "stat_requirements": {"Luck": 12, "Stamina": 12},
                    "icon": "alchemist_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"potion_duration_percent": 5}
                },
                "scavenger": {
                    "name": "Scavenger",
                    "description": "Find better loot from defeated enemies.",
                    "effects": {"loot_quality_bonus": 15},
                    "cost": 5,
                    "stat_requirements": {"Luck": 12, "Stamina": 12},
                    "icon": "scavenger_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"loot_quality_bonus": 3}
                },
                "master_crafter": {
                    "name": "Master Crafter",
                    "description": "Chance for crafted items to have bonus effects.",
                    "effects": {"crafting_bonus_effect_chance": 15},
                    "cost": 6,
                    "stat_requirements": {"Luck": 12, "Stamina": 12},
                    "icon": "master_crafter_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"crafting_bonus_effect_chance": 3}
                }
            },
            # Tier 4
            {
                "potion_mastery": {
                    "name": "Potion Mastery",
                    "description": "Create potions with doubled effect strength.",
                    "effects": {"potion_effect_multiplier": 2},
                    "cost": 7,
                    "stat_requirements": {"Luck": 18, "Stamina": 15},
                    "icon": "potion_master_icon",
                    "type": "passive",
                    "max_points": 4,
                    "per_point_effect": {"potion_effect_multiplier": 0.5}
                },
                "resource_master": {
                    "name": "Resource Master",
                    "description": "Chance to not consume materials when crafting.",
                    "effects": {"material_preservation_chance": 25},
                    "cost": 8,
                    "stat_requirements": {"Luck": 18, "Stamina": 15},
                    "icon": "resource_master_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"material_preservation_chance": 5}
                }
            },
            # Tier 5
            {
                "survival_expert": {
                    "name": "Survival Expert",
                    "description": "Auto-use healing items when critically injured.",
                    "effects": {"auto_heal_threshold": 20},
                    "cost": 10,
                    "stat_requirements": {"Luck": 25, "Stamina": 20},
                    "icon": "survival_expert_icon",
                    "type": "passive",
                    "max_points": 4,
                    "per_point_effect": {"auto_heal_threshold": 5}
                }
            }
        ]
    },
    "Social": {
        "description": "Masters of conversation and social influence",
        "primary_stats": ["Talking", "Luck"],
        "tiers": [
            # Tier 1
            {
                "basic_persuasion": {
                    "name": "Basic Persuasion",
                    "description": "Fundamental skills to convince others.",
                    "effects": {"persuasion_success_chance": 10},
                    "cost": 2,
                    "stat_requirements": {"Talking": 5},
                    "icon": "persuasion_icon",
                    "type": "passive",
                    "failure_effects": {"subsequent_check_penalty": 5}
                },
                "haggling": {
                    "name": "Haggling",
                    "description": "Negotiate better prices with merchants.",
                    "effects": {"merchant_price_percent": 5},
                    "cost": 2,
                    "stat_requirements": {"Talking": 5},
                    "icon": "haggle_icon",
                    "type": "passive",
                    "failure_effects": {"price_increase_percent": 3, "price_penalty_duration": 1}
                },
                "first_impressions": {
                    "name": "First Impressions",
                    "description": "Make better initial impressions on NPCs.",
                    "effects": {"initial_disposition_bonus": 5},
                    "cost": 2,
                    "stat_requirements": {"Talking": 5},
                    "icon": "impression_icon",
                    "type": "passive",
                    "failure_effects": {"disposition_penalty": 5}
                }
            },
            # Tier 2
            {
                "silver_tongue": {
                    "name": "Silver Tongue",
                    "description": "Persuasive speaking improves success chances.",
                    "effects": {"persuasion_success_bonus": 15},
                    "cost": 3,
                    "stat_requirements": {"Talking": 10, "Luck": 5},
                    "icon": "silver_tongue_icon",
                    "type": "passive",
                    "failure_effects": {"reputation_penalty": 10}
                },
                "intimidation": {
                    "name": "Intimidation",
                    "description": "Force cooperation through intimidation.",
                    "effects": {"intimidation_success_bonus": 10},
                    "cost": 3,
                    "stat_requirements": {"Talking": 10, "Strength": 8},
                    "icon": "intimidation_icon",
                    "type": "passive",
                    "failure_effects": {"reputation_penalty": 15, "hostility_chance": 25}
                },
                "reputation_management": {
                    "name": "Reputation Management",
                    "description": "Reduce penalties to reputation.",
                    "effects": {"reputation_penalty_reduction": 10},
                    "cost": 4,
                    "stat_requirements": {"Talking": 10, "Luck": 5},
                    "icon": "reputation_icon",
                    "type": "passive",
                    "failure_effects": {"reputation_penalty_multiplier": 2}
                }
            },
            # Tier 3
            {
                "expert_negotiator": {
                    "name": "Expert Negotiator",
                    "description": "Master negotiation for better prices and rewards.",
                    "effects": {"merchant_price_percent": 10, "quest_reward_bonus_chance": 15},
                    "cost": 5,
                    "stat_requirements": {"Talking": 18, "Luck": 8},
                    "icon": "negotiator_icon",
                    "type": "passive",
                    "failure_effects": {"price_increase_percent": 8, "transaction_refusal_chance": 15}
                },
                "charm": {
                    "name": "Charm",
                    "description": "Temporarily improve NPC disposition.",
                    "effects": {"charm_disposition_bonus": 15, "charm_duration": 300},
                    "cost": 5,
                    "stat_requirements": {"Talking": 18, "Luck": 8},
                    "icon": "charm_icon",
                    "type": "active",
                    "cooldown": 60,
                    "failure_effects": {"disposition_penalty": 15, "gender_faction_penalty": 15}
                },
                "lie_detection": {
                    "name": "Lie Detection",
                    "description": "Detect when NPCs are lying.",
                    "effects": {"lie_detection_chance": 20},
                    "cost": 6,
                    "stat_requirements": {"Talking": 18, "Luck": 8},
                    "icon": "lie_detection_icon",
                    "type": "passive",
                    "failure_effects": {"misinformation_chance": 25}
                }
            },
            # Tier 4
            {
                "inspiring_speech": {
                    "name": "Inspiring Speech",
                    "description": "Rally allies to increase their damage.",
                    "effects": {"ally_damage_bonus": 10, "speech_duration": 30},
                    "cost": 7,
                    "stat_requirements": {"Talking": 25, "Luck": 12},
                    "icon": "inspiring_speech_icon",
                    "type": "active",
                    "cooldown": 90,
                    "failure_effects": {"ally_damage_penalty": 5, "speech_duration": 30}
                },
                "master_manipulator": {
                    "name": "Master Manipulator",
                    "description": "Manipulate difficult social situations.",
                    "effects": {"difficult_persuasion_bonus": 25},
                    "cost": 8,
                    "stat_requirements": {"Talking": 25, "Luck": 12},
                    "icon": "manipulator_icon",
                    "type": "passive",
                    "failure_effects": {"hostility_chance": 50, "alert_others_chance": 35}
                }
            },
            # Tier 5
            {
                "legendary_charisma": {
                    "name": "Legendary Charisma",
                    "description": "Guarantee success on one critical dialogue check per day.",
                    "effects": {"guaranteed_persuasion_uses": 1},
                    "cost": 10,
                    "stat_requirements": {"Talking": 35, "Luck": 15},
                    "icon": "legendary_charisma_icon",
                    "type": "active",
                    "cooldown": 86400,  # 24 hours in seconds
                    "failure_effects": {"faction_reputation_penalty": 30}
                }
            }
        ]
    },  
    "Subterfuge": {
        "description": "Masters of stealth, lockpicking and deception",
        "primary_stats": ["Luck", "Stamina"],
        "tiers": [
            # Tier 1
            {
                "basic_lock_picking": {
                    "name": "Basic Lock Picking",
                    "description": "Fundamental skills to pick simple locks.",
                    "effects": {"lockpick_success_chance": 10},
                    "cost": 2,
                    "stat_requirements": {"Luck": 5},
                    "icon": "lockpick_icon",
                    "type": "passive",
                    "failure_effects": {"lockpick_break_chance": 50, "noise_alert_radius": 10, "lock_jam_chance": 20}
                },
                "light_fingers": {
                    "name": "Light Fingers",
                    "description": "Find extra items in containers.",
                    "effects": {"extra_loot_chance": 10},
                    "cost": 2,
                    "stat_requirements": {"Luck": 5},
                    "icon": "light_fingers_icon",
                    "type": "passive",
                    "failure_effects": {"trap_damage_multiplier": 2, "trap_trigger_chance": 15}
                },
                "quiet_movement": {
                    "name": "Quiet Movement",
                    "description": "Move more quietly to avoid detection.",
                    "effects": {"noise_reduction": 10},
                    "cost": 2,
                    "stat_requirements": {"Luck": 5},
                    "icon": "quiet_movement_icon",
                    "type": "passive",
                    "failure_effects": {"detection_radius_increase": 20, "stumble_duration": 30}
                }
            },
            # Tier 2
            {
                "improved_lock_picking": {
                    "name": "Improved Lock Picking",
                    "description": "Better techniques for lock manipulation.",
                    "effects": {"lockpick_success_bonus": 15},
                    "cost": 3,
                    "stat_requirements": {"Luck": 10, "Stamina": 8},
                    "icon": "improved_lockpick_icon",
                    "type": "passive",
                    "failure_effects": {"lock_jam_chance": 40, "tool_break_chance": 10}
                },
                "trap_detection": {
                    "name": "Trap Detection",
                    "description": "Spot traps before triggering them.",
                    "effects": {"trap_detection_chance": 20},
                    "cost": 3,
                    "stat_requirements": {"Luck": 10, "Stamina": 8},
                    "icon": "trap_detection_icon",
                    "type": "passive",
                    "failure_effects": {"trap_trigger_chance_increase": 25}
                },
                "pickpocketing": {
                    "name": "Pickpocketing",
                    "description": "Steal items from NPCs.",
                    "effects": {"pickpocket_success_rate": 15},
                    "cost": 4,
                    "stat_requirements": {"Luck": 10, "Stamina": 8},
                    "icon": "pickpocket_icon",
                    "type": "passive",
                    "failure_effects": {"caught_hostility_chance": 90, "area_reputation_penalty": 20}
                }
            },
            # Tier 3
            {
                "advanced_lock_manipulation": {
                    "name": "Advanced Lock Manipulation",
                    "description": "Master techniques for difficult locks.",
                    "effects": {"lockpick_success_bonus": 20, "lockpick_speed_percent": 15},
                    "cost": 5,
                    "stat_requirements": {"Luck": 15, "Stamina": 12},
                    "icon": "advanced_lockpick_icon",
                    "type": "passive",
                    "failure_effects": {"security_trigger_chance": 30, "lock_break_chance": 30}
                },
                "trap_disarming": {
                    "name": "Trap Disarming",
                    "description": "Safely disarm detected traps.",
                    "effects": {"trap_disarm_chance": 25},
                    "cost": 5,
                    "stat_requirements": {"Luck": 15, "Stamina": 12},
                    "icon": "trap_disarm_icon",
                    "type": "passive",
                    "failure_effects": {"trap_damage_multiplier": 1.25, "shaky_hands_duration": 60, "shaky_hands_penalty": 10}
                },
                "shadow_stride": {
                    "name": "Shadow Stride",
                    "description": "Move through shadows with reduced detection.",
                    "effects": {"stealth_detection_reduction": 25},
                    "cost": 6,
                    "stat_requirements": {"Luck": 15, "Stamina": 12},
                    "icon": "shadow_stride_icon",
                    "type": "passive",
                    "failure_effects": {"detection_bonus_against_you": 15, "detection_duration": 600}
                }
            },
            # Tier 4
            {
                "master_lock_picker": {
                    "name": "Master Lock Picker",
                    "description": "Automatically succeed on simple locks.",
                    "effects": {"simple_lock_auto_success": 1, "complex_lock_bonus": 30},
                    "cost": 7,
                    "stat_requirements": {"Luck": 20, "Stamina": 15},
                    "icon": "master_lockpick_icon",
                    "type": "passive",
                    "failure_effects": {"alarm_trigger_chance": 50, "guard_alert_radius": 100}
                },
                "treasure_hunter": {
                    "name": "Treasure Hunter",
                    "description": "Find hidden compartments with rare items.",
                    "effects": {"secret_compartment_chance": 25},
                    "cost": 8,
                    "stat_requirements": {"Luck": 20, "Stamina": 15},
                    "icon": "treasure_hunter_icon",
                    "type": "passive",
                    "failure_effects": {"item_quality_reduction_chance": 20, "item_destruction_chance": 5}
                }
            },
            # Tier 5
            {
                "ghost": {
                    "name": "Ghost",
                    "description": "Become nearly invisible temporarily.",
                    "effects": {"invisibility_percent": 80, "invisibility_duration": 30},
                    "cost": 10,
                    "stat_requirements": {"Luck": 30, "Stamina": 20},
                    "icon": "ghost_icon",
                    "type": "active",
                    "cooldown": 300,
                    "failure_effects": {"position_reveal_radius": 100, "exposed_duration": 300, "exposed_penalty": 50}
                }
            }
        ]
    },

    "Stealth": {
        "description": "Masters of sneaking, evasion, and remaining unseen.",
        "primary_stats": ["Agility", "Luck", "Stamina"],
        "tiers": [
            # Tier 1
            {
                "soft_steps": {
                    "name": "Soft Steps",
                    "description": "Move more quietly, reducing the distance enemies can hear you.",
                    "effects": {"stealth_noise_reduction_percent": 2},
                    "cost": 1,
                    "stat_requirements": {"Agility": 5},
                    "icon": "soft_steps_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"stealth_noise_reduction_percent": 2},
                },
                "shadow_blend": {
                    "name": "Shadow Blend",
                    "description": "Blend into shadows, making you harder to see.",
                    "effects": {"stealth_visibility_reduction_percent": 2},
                    "cost": 1,
                    "stat_requirements": {"Agility": 5},
                    "icon": "shadow_blend_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"stealth_visibility_reduction_percent": 2},
                },
                "steady_breath": {
                    "name": "Steady Breath",
                    "description": "Improved stamina efficiency while sneaking.",
                    "effects": {"stealth_stamina_reduction_percent": 2},
                    "cost": 1,
                    "stat_requirements": {"Stamina": 5},
                    "icon": "steady_breath_icon",
                    "type": "passive",
                    "max_points": 5,
                    "per_point_effect": {"stealth_stamina_reduction_percent": 2},
                }

            },
            {                "catlike_balance": {
                    "name": "Catlike Balance",
                    "description": "Move across unstable surfaces without making noise.",
                    "effects": {"stealth_fall_noise_reduction": 50},
                    "cost": 3,
                    "stat_requirements": {"Agility": 10, "Stamina": 8},
                    "icon": "catlike_balance_icon",
                    "type": "passive"
                },
                "night_vision": {
                    "name": "Night Vision",
                    "description": "See better in darkness, improving stealth at night.",
                    "effects": {"stealth_dark_bonus": 15},
                    "cost": 3,
                    "stat_requirements": {"Luck": 10, "Agility": 8},
                    "icon": "night_vision_icon",
                    "type": "passive"
                },
                "distraction": {
                    "name": "Distraction",
                    "description": "Create a noise to lure enemies away.",
                    "effects": {"distraction_radius": 30, "distraction_duration": 5},
                    "cost": 4,
                    "stat_requirements": {"Agility": 10, "Luck": 8},
                    "icon": "distraction_icon",
                    "type": "active",
                    "cooldown": 20
                }
            },  
            {                "silent_takedown": {
                    "name": "Silent Takedown",
                    "description": "Perform silent takedowns on unaware enemies.",
                    "effects": {"takedown_success_chance": 60, "takedown_noise_reduction": 90},
                    "cost": 5,
                    "stat_requirements": {"Agility": 15, "Stamina": 12},
                    "icon": "silent_takedown_icon",
                    "type": "active",
                    "cooldown": 30
                },
                "chameleon": {
                    "name": "Chameleon",
                    "description": "Blend with surroundings for a short time.",
                    "effects": {"stealth_visibility_reduction_percent": 30, "duration": 8},
                    "cost": 6,
                    "stat_requirements": {"Agility": 15, "Luck": 12},
                    "icon": "chameleon_icon",
                    "type": "active",
                    "cooldown": 60
                },
                "keen_hearing": {
                    "name": "Keen Hearing",
                    "description": "Detect nearby enemies through sound.",
                    "effects": {"enemy_detection_radius": 25, "detect_through_walls": True},
                    "cost": 5,
                    "stat_requirements": {"Luck": 15, "Stamina": 12},
                    "icon": "keen_hearing_icon",
                    "type": "passive"
                }
            },  
            {                "vanish": {
                    "name": "Vanish",
                    "description": "Instantly become invisible for a short duration.",
                    "effects": {"invisibility_duration": 6, "invisibility_percent": 100},
                    "cost": 7,
                    "stat_requirements": {"Agility": 22, "Luck": 15},
                    "icon": "vanish_icon",
                    "type": "active",
                    "cooldown": 60
                },
                "evasion_mastery": {
                    "name": "Evasion Mastery",
                    "description": "Greatly increases dodge chance while sneaking.",
                    "effects": {"stealth_dodge_bonus": 20},
                    "cost": 8,
                    "stat_requirements": {"Agility": 22, "Stamina": 18},
                    "icon": "evasion_mastery_icon",
                    "type": "passive"
                },
                "silent_kill": {
                    "name": "Silent Kill",
                    "description": "Attacks from stealth deal massive bonus damage.",
                    "effects": {"stealth_attack_damage_percent": 50},
                    "cost": 8,
                    "stat_requirements": {"Agility": 22, "Luck": 18},
                    "icon": "silent_kill_icon",
                    "type": "passive"
                }
            },  # Tier 5
            {
                "shadow_master": {
                    "name": "Shadow Master",
                    "description": "Become nearly undetectable for a short time. Attacks from stealth deal triple damage.",
                    "effects": {
                        "invisibility_percent": 100,
                        "invisibility_duration": 12,
                        "stealth_attack_damage_multiplier": 3
                    },
                    "cost": 10,
                    "stat_requirements": {"Agility": 30, "Luck": 22, "Stamina": 20},
                    "icon": "shadow_master_icon",
                    "type": "active",
                    "cooldown": 180
                }
            }
        ]
    },
}

# Cross-tree skills defined separately
CROSS_TREE_SKILLS = {
    # Tier 2-3 level hybrids
    "battle_mage": {
        "name": "Battle Mage",
        "description": "Blend of martial and magical abilities.",
        "effects": {"melee_to_mana_percent": 2},
        "cost": 4,
        "stat_requirements": {"Strength": 12, "Willpower": 12},
        "skill_requirements": {"strength_training": True, "mana_pool": True},
        "icon": "battle_mage_icon",
        "type": "passive"
    },
    "enchanter": {
        "name": "Enchanter",
        "description": "Add magical effects to crafted items.",
        "effects": {"enchantment_chance": 15},
        "cost": 4,
        "stat_requirements": {"Willpower": 12, "Luck": 10},
        "skill_requirements": {"spell_efficiency": True, "basic_crafting": True},
        "icon": "enchanter_icon",
        "type": "passive"
    },
    "ranger": {
        "name": "Ranger",
        "description": "Swift movement and improved awareness.",
        "effects": {"movement_speed_percent": 10},
        "cost": 4,
        "stat_requirements": {"Stamina": 12, "Luck": 12},
        "skill_requirements": {"combat_reflexes": True, "resource_sensing": True},
        "icon": "ranger_icon",
        "type": "passive"
    },
    
    # Tier 3-4 level hybrids
    "elemental_weapon": {
        "name": "Elemental Weapon",
        "description": "Imbue weapons with elemental damage.",
        "effects": {"weapon_elemental_damage": 8},
        "cost": 6,
        "stat_requirements": {"Strength": 15, "Willpower": 15},
        "skill_requirements": {"battle_mage": True, "weapon_specialization": True},
        "icon": "elemental_weapon_icon",
        "type": "passive"
    },
    "potion_master": {
        "name": "Potion Master",
        "description": "Craft potions that grant temporary skills.",
        "effects": {"skill_potion_duration": 60},
        "cost": 6,
        "stat_requirements": {"Willpower": 15, "Luck": 15},
        "skill_requirements": {"enchanter": True, "alchemist": True},
        "icon": "potion_master_icon",
        "type": "passive"
    },
    "shadowstep": {
        "name": "Shadowstep",
        "description": "Quick dash that grants brief invulnerability.",
        "effects": {"dash_distance": 100, "invulnerable_duration": 0.5},
        "cost": 6,
        "stat_requirements": {"Stamina": 15, "Luck": 15},
        "skill_requirements": {"ranger": True, "combat_reflexes": True},
        "icon": "shadowstep_icon",
        "type": "active",
        "cooldown": 15
    },
    
    # Tier 4-5 level hybrid
    "arcane_warrior": {
        "name": "Arcane Warrior",
        "description": "Blend weapon and spell damage.",
        "effects": {"spell_to_weapon_conversion": 15, "weapon_to_spell_conversion": 15},
        "cost": 7,
        "stat_requirements": {"Strength": 20, "Willpower": 20},
        "skill_requirements": {"elemental_weapon": True, "spell_focus": True},
        "icon": "arcane_warrior_icon",
        "type": "passive"
    },
    
    # Social/Subterfuge hybrids
    "silver_tongued_merchant": {
        "name": "Silver-Tongued Merchant",
        "description": "Sell items for higher prices.",
        "effects": {"selling_price_percent": 15},
        "cost": 4,
        "stat_requirements": {"Talking": 10, "Luck": 10},
        "skill_requirements": {"haggling": True, "efficient_gathering": True},
        "icon": "merchant_icon",
        "type": "passive"
    },
    "trap_maker": {
        "name": "Trap Maker",
        "description": "Craft traps to damage and slow enemies.",
        "effects": {"trap_damage": 20, "trap_slow_percent": 30, "trap_duration": 60},
        "cost": 5,
        "stat_requirements": {"Luck": 12, "Stamina": 10},
        "skill_requirements": {"basic_crafting": True, "trap_detection": True},
        "icon": "trap_maker_icon",
        "type": "passive"
    },
    "diplomatic_immunity": {
        "name": "Diplomatic Immunity",
        "description": "Talk your way out of combat situations.",
        "effects": {"combat_escape_chance": 15},
        "cost": 6,
        "stat_requirements": {"Talking": 15, "Willpower": 12},
        "skill_requirements": {"silver_tongue": True, "mana_shield": True},
        "icon": "diplomatic_immunity_icon",
        "type": "active",
        "cooldown": 300
    },
    "distraction_tactics": {
        "name": "Distraction Tactics",
        "description": "Create distractions to confuse enemies.",
        "effects": {"distraction_duration": 5, "distraction_radius": 50},
        "cost": 6,
        "stat_requirements": {"Luck": 15, "Talking": 12},
        "skill_requirements": {"shadow_stride": True, "combat_reflexes": True},
        "icon": "distraction_icon",
        "type": "active",
        "cooldown": 60
    }
}

# Helper functions for skill system
def can_acquire_skill(player, tree_id, tier, skill_id):
    """Check if player can acquire a skill based on prerequisites and stats"""
    # Invalid tree or tier
    if tree_id not in SKILL_TREES or tier >= len(SKILL_TREES[tree_id]["tiers"]):
        return False, "Invalid skill tree or tier"
    
    # Check if skill exists
    if skill_id not in SKILL_TREES[tree_id]["tiers"][tier]:
        return False, "Skill not found"
    
    skill_data = SKILL_TREES[tree_id]["tiers"][tier][skill_id]
    
    # Check if already acquired
    if skill_id in player.acquired_skills:
        return False, "Skill already acquired"
    
    # Check perk point cost (skills now use perk points)
    if not hasattr(player, 'perk_points'):
        player.perk_points = 0  # Initialize if missing
    if player.perk_points < skill_data["cost"]:
        return False, f"Not enough perk points. Need {skill_data['cost']}"
    
    # Check stat requirements (can be met through equipment/other perks over time)
    for stat, req_value in skill_data["stat_requirements"].items():
        if hasattr(player, 'stats') and hasattr(player.stats, 'get_stat'):
            if player.stats.get_stat(stat) < req_value:
                return False, f"Need {stat} {req_value}"
        else:
            if getattr(player, stat.lower(), 0) < req_value:
                return False, f"Need {stat} {req_value}"
    
    # Remove tier completion requirement - allow any skill if stats/points are met
    # This allows players to eventually unlock everything over time
    
    return True, "Can acquire skill"

def can_acquire_cross_skill(player, skill_id):
    """Check if player can acquire a cross-tree skill"""
    if skill_id not in CROSS_TREE_SKILLS:
        return False, "Skill not found"
    
    skill_data = CROSS_TREE_SKILLS[skill_id]
    
    # Check if already acquired
    if skill_id in player.acquired_skills:
        return False, "Skill already acquired"
    
    # Check perk point cost (cross-tree skills now use perk points)
    if not hasattr(player, 'perk_points'):
        player.perk_points = 0
    if player.perk_points < skill_data["cost"]:
        return False, f"Not enough perk points. Need {skill_data['cost']}"
    
    # Check stat requirements
    for stat, req_value in skill_data["stat_requirements"].items():
        if player.stats.get(stat, 0) < req_value:
            return False, f"Need {stat} {req_value}"
    
    # Check skill requirements
    for req_skill, needed in skill_data["skill_requirements"].items():
        if needed and req_skill not in player.acquired_skills:
            return False, f"Need {req_skill.replace('_', ' ').title()} skill first"
    
    return True, "Can acquire skill"

def get_all_skill_trees():
    """Return a list of all skill tree names"""
    return list(SKILL_TREES.keys())

def get_cross_tree_skills():
    """Return cross-tree skills data"""
    return CROSS_TREE_SKILLS