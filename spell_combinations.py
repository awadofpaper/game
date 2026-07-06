"""
Spell Combination System - Expands magical gameplay
Allows players to combine spells for unique effects and tactical advantages
"""

import math
import random

# Define elemental relationships and interactions
ELEMENTAL_INTERACTIONS = {
    "fire": {
        "strong_against": ["ice", "nature"],
        "weak_against": ["water"],
        "neutral": ["lightning", "dark", "light"],
        "amplified_by": ["lightning", "wind"],  # Lightning + Fire = explosion
        "dampened_by": ["water", "ice"]
    },
    "ice": {
        "strong_against": ["water", "fire"],
        "weak_against": ["fire", "lightning"],
        "neutral": ["dark", "light", "nature"],
        "amplified_by": ["water", "wind"],
        "dampened_by": ["fire"]
    },
    "lightning": {
        "strong_against": ["water", "metal"],
        "weak_against": ["earth"],
        "neutral": ["fire", "ice", "nature"],
        "amplified_by": ["water", "storm"],
        "dampened_by": ["earth"]
    },
    "water": {
        "strong_against": ["fire", "earth"],
        "weak_against": ["lightning", "nature"],
        "neutral": ["dark", "light"],
        "amplified_by": ["ice", "storm"],
        "dampened_by": ["fire"]
    }
}

# Spell combination recipes
SPELL_COMBINATIONS = {
    # Elemental combinations
    ("fireball", "ice_shard"): {
        "name": "Steam Explosion",
        "damage": 35,
        "element": "steam",
        "effects": ["blind", "burn"],
        "aoe_radius": 80,
        "mana_cost": 25,
        "description": "Fire and ice create a blinding steam explosion"
    },
    ("lightning_bolt", "water_splash"): {
        "name": "Chain Lightning", 
        "damage": 40,
        "element": "lightning",
        "effects": ["shock", "chain_3"],  # Hits up to 3 additional enemies
        "mana_cost": 30,
        "description": "Lightning travels through water to nearby enemies"
    },
    ("fireball", "lightning_bolt"): {
        "name": "Plasma Burst",
        "damage": 50,
        "element": "plasma",
        "effects": ["disintegrate", "energy_damage"],
        "mana_cost": 35,
        "description": "Pure energy that ignores most resistances"
    },
    ("ice_shard", "wind_gust"): {
        "name": "Frozen Hurricane",
        "damage": 30,
        "element": "ice",
        "effects": ["freeze", "knockback"],
        "aoe_radius": 120,
        "duration": 5,
        "mana_cost": 28,
        "description": "Swirling ice storm that freezes and pushes enemies"
    },
    
    # Utility combinations
    ("heal", "shield"): {
        "name": "Divine Protection",
        "healing": 25,
        "shield_amount": 40,
        "effects": ["blessed", "damage_immunity_3s"],
        "mana_cost": 40,
        "description": "Heal and protect with temporary invincibility"
    },
    ("teleport", "fireball"): {
        "name": "Flame Dash",
        "damage": 20,
        "teleport_range": 150,
        "effects": ["burn_trail", "surprise_attack"],
        "mana_cost": 30,
        "description": "Teleport through enemies, leaving fire in your wake"
    },
    ("summon_wolf", "blessing"): {
        "name": "Spirit Wolf",
        "summon_duration": 20,
        "summon_health": 80,
        "summon_damage": 25,
        "effects": ["pack_leader", "howl_buff"],
        "mana_cost": 45,
        "description": "Summon an enhanced wolf spirit with special abilities"
    },
    
    # Advanced combinations (require 3 spells)
    ("fireball", "ice_shard", "lightning_bolt"): {
        "name": "Elemental Chaos",
        "damage": 60,
        "element": "chaos",
        "effects": ["random_element", "chaos_storm"],
        "aoe_radius": 150,
        "mana_cost": 60,
        "description": "Unstable magic that randomly applies elemental effects"
    },
    ("heal", "shield", "blessing"): {
        "name": "Sanctuary",
        "healing": 50,
        "shield_amount": 80,
        "effects": ["sanctuary_aura", "damage_immunity_5s"],
        "aoe_radius": 100,  # Affects allies too
        "mana_cost": 70,
        "description": "Create a zone of ultimate protection and healing"
    }
}

# Spell combo difficulty levels
COMBO_DIFFICULTY = {
    2: {"timing_window": 2.0, "mana_efficiency": 0.9},  # Easy combos
    3: {"timing_window": 1.5, "mana_efficiency": 0.8},  # Hard combos
    4: {"timing_window": 1.0, "mana_efficiency": 0.7}   # Master combos
}

class SpellComboSystem:
    def __init__(self):
        self.recent_spells = []  # Track recently cast spells for combos
        self.combo_window = 3.0  # Time window for spell combinations
        self.combo_multiplier = 1.0  # Damage multiplier for successful combos
        
    def add_spell_cast(self, spell_name, timestamp):
        """Record a spell cast for combo tracking"""
        # Remove old spells outside combo window
        current_time = timestamp
        self.recent_spells = [
            (spell, time) for spell, time in self.recent_spells
            if current_time - time <= self.combo_window
        ]
        
        # Add new spell
        self.recent_spells.append((spell_name, timestamp))
    
    def check_for_combo(self):
        """Check if recent spells form a valid combination"""
        if len(self.recent_spells) < 2:
            return None
        
        # Check for 2-spell combos first
        recent_spell_names = [spell for spell, _ in self.recent_spells[-2:]]
        combo_key = tuple(recent_spell_names)
        
        if combo_key in SPELL_COMBINATIONS:
            return SPELL_COMBINATIONS[combo_key]
        
        # Check reversed order
        reversed_key = tuple(reversed(recent_spell_names))
        if reversed_key in SPELL_COMBINATIONS:
            return SPELL_COMBINATIONS[reversed_key]
        
        # Check for 3+ spell combos
        if len(self.recent_spells) >= 3:
            recent_3 = [spell for spell, _ in self.recent_spells[-3:]]
            combo_key_3 = tuple(recent_3)
            
            if combo_key_3 in SPELL_COMBINATIONS:
                return SPELL_COMBINATIONS[combo_key_3]
        
        return None
    
    def calculate_combo_effectiveness(self, player_skill, spell_count):
        """Calculate how effective a spell combo will be"""
        base_effectiveness = 1.0
        
        # Player skill bonus (from Magic stat or specific skill)
        skill_bonus = min(0.5, player_skill * 0.02)  # Max 50% bonus
        
        # Combo complexity bonus
        complexity_bonus = (spell_count - 1) * 0.2  # 20% per additional spell
        
        # Random variance
        variance = random.uniform(0.9, 1.1)
        
        return (base_effectiveness + skill_bonus + complexity_bonus) * variance
    
    def execute_combo(self, combo_data, caster, target_pos, effectiveness=1.0):
        """Execute a spell combination"""
        result = {
            "name": combo_data["name"],
            "damage": int(combo_data.get("damage", 0) * effectiveness),
            "effects": combo_data.get("effects", []),
            "description": combo_data["description"],
            "mana_used": combo_data["mana_cost"],
            "success": True
        }
        
        # Apply special combo effects
        if "aoe_radius" in combo_data:
            result["aoe_radius"] = combo_data["aoe_radius"]
            result["area_effect"] = True
        
        if "healing" in combo_data:
            result["healing"] = int(combo_data["healing"] * effectiveness)
        
        if "shield_amount" in combo_data:
            result["shield"] = int(combo_data["shield_amount"] * effectiveness)
        
        # Clear recent spells after successful combo
        self.recent_spells.clear()
        
        return result

# Environmental spell interactions
ENVIRONMENTAL_SPELL_EFFECTS = {
    "water_terrain": {
        "lightning_bolt": {"damage_multiplier": 1.4, "chain_range": 150},
        "ice_shard": {"damage_multiplier": 1.2, "freeze_chance": 0.8},
        "fireball": {"damage_multiplier": 0.7, "steam_effect": True}
    },
    "metal_terrain": {
        "lightning_bolt": {"damage_multiplier": 1.6, "guaranteed_crit": True},
        "magnetic_spells": {"range_multiplier": 2.0}
    },
    "forest_terrain": {
        "fireball": {"damage_multiplier": 1.3, "spread_fire": True},
        "nature_spells": {"mana_cost_multiplier": 0.8},
        "ice_shard": {"damage_multiplier": 0.9}
    },
    "arctic_terrain": {
        "ice_shard": {"damage_multiplier": 1.5, "duration_bonus": 2},
        "fireball": {"mana_cost_multiplier": 1.3},
        "cold_immunity": ["freeze", "slow"]
    }
}

class AdvancedSpellSystem:
    def __init__(self):
        self.combo_system = SpellComboSystem()
        self.learned_combos = set()  # Track which combos player has discovered
        self.spell_mastery = {}  # Track individual spell mastery levels
        
    def discover_combo(self, combo_name):
        """Add a combo to the player's known combinations"""
        self.learned_combos.add(combo_name)
        return f"New spell combination discovered: {combo_name}!"
    
    def can_cast_combo(self, combo_data, player):
        """Check if player can cast a specific combo"""
        # Check mana requirement
        if player.mana < combo_data["mana_cost"]:
            return False, "Insufficient mana"
        
        # Check if player knows the component spells
        component_spells = self.get_combo_components(combo_data)
        for spell in component_spells:
            if not self.knows_spell(player, spell):
                return False, f"Must know {spell} spell"
        
        return True, "Can cast"
    
    def get_combo_components(self, combo_data):
        """Get the component spells needed for a combo"""
        # This would need to be implemented based on your combo key structure
        # For now, return empty list
        return []
    
    def knows_spell(self, player, spell_name):
        """Check if player knows a specific spell"""
        # This would integrate with your existing spell learning system
        return hasattr(player, 'known_spells') and spell_name in player.known_spells
    
    def increase_spell_mastery(self, spell_name, amount=1):
        """Increase mastery level for a spell"""
        current_mastery = self.spell_mastery.get(spell_name, 0)
        self.spell_mastery[spell_name] = current_mastery + amount
        
        # Mastery milestones
        new_mastery = self.spell_mastery[spell_name]
        if new_mastery in [10, 25, 50, 100]:
            return f"{spell_name} mastery increased to {new_mastery}! New effects unlocked."
        
        return None
    
    def get_mastery_bonus(self, spell_name):
        """Get damage/effectiveness bonus from spell mastery"""
        mastery = self.spell_mastery.get(spell_name, 0)
        return min(0.5, mastery * 0.005)  # Max 50% bonus at 100 mastery
    
    def cast_spell(self, spell_id, caster, target_x, target_y):
        """
        Cast a spell and create projectile/effect
        
        Args:
            spell_id: ID of the spell to cast
            caster: Player/NPC casting the spell
            target_x: Target X coordinate
            target_y: Target Y coordinate
            
        Returns:
            SpellProjectile, InstantSpell, or effect object, or None if cast failed
        """
        # Import here to avoid circular dependencies
        from spells import SPELLS
        from spell_projectile import SpellProjectile, InstantSpell
        
        # Check if spell exists
        if spell_id not in SPELLS:
            return None
        
        spell_data = SPELLS[spell_id]
        
        # Check mana cost
        base_mana_cost = spell_data.get('mana_cost', 0)
        mana_cost = base_mana_cost
        
        # Apply racial spell cost modifiers (Tiefling: -15% all spells, -30% fire spells)
        if hasattr(caster, 'trait_manager') and caster.trait_manager:
            spell_element = spell_data.get('element', None)
            mana_cost = caster.trait_manager.apply_spell_cost_modifier(base_mana_cost, spell_element)
            
            if mana_cost != base_mana_cost:
                import logging
                logger = logging.getLogger(__name__)
                reduction = base_mana_cost - mana_cost
                element_str = f" ({spell_element})" if spell_element else ""
                logger.info(f"[RACIAL TRAIT] Spell cost{element_str}: {base_mana_cost} → {mana_cost:.0f} (-{reduction:.0f})")
        
        if hasattr(caster, 'mana') and caster.mana < mana_cost:
            return None
        
        # Deduct mana
        if hasattr(caster, 'mana'):
            caster.mana -= mana_cost
        
        # Track spell mastery
        self.increase_spell_mastery(spell_id)
        
        # Check spell type and create appropriate object
        spell_type = spell_data.get('type', 'projectile')
        
        if spell_type == 'projectile':
            # Create projectile spell
            projectile = SpellProjectile(caster.x, caster.y, target_x, target_y, spell_data, caster)
            return projectile
        elif spell_type in ['self', 'instant']:
            # Create instant spell (healing, buffs, etc.)
            instant_spell = InstantSpell(caster.x, caster.y, spell_data, caster)
            return instant_spell
        else:
            # Default to projectile
            projectile = SpellProjectile(caster.x, caster.y, target_x, target_y, spell_data, caster)
            return projectile

# Integration example for your existing spell system
def integrate_combo_system_example():
    """Example of how to integrate with existing spell casting"""
    
    # Add to Player class:
    # self.advanced_spells = AdvancedSpellSystem()
    
    def cast_spell_with_combos(self, spell_name, target_pos, current_time):
        """Enhanced spell casting with combo detection"""
        
        # Record spell cast for combo tracking
        self.advanced_spells.combo_system.add_spell_cast(spell_name, current_time)
        
        # Check for combo opportunity
        combo_data = self.advanced_spells.combo_system.check_for_combo()
        
        if combo_data:
            # Player can choose to execute combo or cast normal spell
            can_cast, message = self.advanced_spells.can_cast_combo(combo_data, self)
            
            if can_cast:
                # Calculate effectiveness based on player skill
                magic_skill = self.stats.get_stat("Magic")
                spell_count = len(self.advanced_spells.combo_system.recent_spells)
                effectiveness = self.advanced_spells.combo_system.calculate_combo_effectiveness(
                    magic_skill, spell_count
                )
                
                # Execute combo instead of normal spell
                combo_result = self.advanced_spells.combo_system.execute_combo(
                    combo_data, self, target_pos, effectiveness
                )
                
                # Discover combo if first time
                if combo_data["name"] not in self.advanced_spells.learned_combos:
                    discovery_message = self.advanced_spells.discover_combo(combo_data["name"])
                    # Show discovery message to player
                
                return combo_result
        
        # Cast normal spell if no combo or combo failed
        # ... existing spell casting logic ...
        
        # Increase spell mastery
        mastery_message = self.advanced_spells.increase_spell_mastery(spell_name)
        if mastery_message:
            # Show mastery message to player
            pass

# Example spell effects that work with the combo system
ENHANCED_SPELL_EFFECTS = {
    "burn_trail": {
        "description": "Leaves fire damage tiles behind",
        "duration": 5,
        "damage_per_tick": 2
    },
    "chain_3": {
        "description": "Spell jumps to 3 nearby enemies",
        "max_targets": 3,
        "damage_falloff": 0.7  # Each jump does 70% damage
    },
    "surprise_attack": {
        "description": "Next attack is guaranteed critical hit",
        "duration": 3
    },
    "chaos_storm": {
        "description": "Random elemental effects each turn",
        "duration": 8,
        "possible_effects": ["burn", "freeze", "shock", "poison"]
    },
    "sanctuary_aura": {
        "description": "Area that continuously heals allies", 
        "duration": 10,
        "heal_per_tick": 3,
        "radius": 100
    }
}