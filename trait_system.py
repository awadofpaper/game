"""
Trait System - Manages active racial traits and applies their effects

Handles trait activation, effect application, and cooldown management.
"""

import time
from typing import Dict, List, Optional, Any
from race_system import RacialTrait


class TraitManager:
    """Manages active traits and applies their effects to the player"""
    
    def __init__(self, player):
        self.player = player
        self.active_traits: List[RacialTrait] = []
        self.trait_cooldowns: Dict[str, float] = {}  # trait_id -> timestamp of next availability
        self.trait_triggers: Dict[str, int] = {}  # trait_id -> trigger count (for daily resets, etc.)
        
    def add_trait(self, trait: RacialTrait):
        """Add a trait to the active list"""
        if trait not in self.active_traits:
            self.active_traits.append(trait)
            
    def remove_trait(self, trait_id: str):
        """Remove a trait by ID"""
        self.active_traits = [t for t in self.active_traits if t.id != trait_id]
        if trait_id in self.trait_cooldowns:
            del self.trait_cooldowns[trait_id]
        if trait_id in self.trait_triggers:
            del self.trait_triggers[trait_id]
    
    def has_trait(self, trait_id: str) -> bool:
        """Check if player has a specific trait"""
        return any(t.id == trait_id for t in self.active_traits)
    
    def get_trait(self, trait_id: str) -> Optional[RacialTrait]:
        """Get a trait by ID"""
        for trait in self.active_traits:
            if trait.id == trait_id:
                return trait
        return None
    
    def is_on_cooldown(self, trait_id: str) -> bool:
        """Check if a trait is on cooldown"""
        if trait_id not in self.trait_cooldowns:
            return False
        return time.time() < self.trait_cooldowns[trait_id]
    
    def set_cooldown(self, trait_id: str, cooldown_seconds: float):
        """Set a cooldown for a trait"""
        self.trait_cooldowns[trait_id] = time.time() + cooldown_seconds
    
    def get_cooldown_remaining(self, trait_id: str) -> float:
        """Get remaining cooldown time in seconds"""
        if trait_id not in self.trait_cooldowns:
            return 0.0
        remaining = self.trait_cooldowns[trait_id] - time.time()
        return max(0.0, remaining)
    
    def apply_passive_effects(self):
        """Apply all passive trait effects to player stats"""
        # This is called during player initialization and stat recalculation
        for trait in self.active_traits:
            self._apply_trait_effects(trait)
    
    def _apply_trait_effects(self, trait: RacialTrait):
        """Apply effects from a single trait"""
        effects = trait.effects
        
        # XP multiplier (Human - Adaptable) - Now time-restricted
        if 'xp_multiplier' in effects:
            if not hasattr(self.player, 'racial_xp_multiplier'):
                self.player.racial_xp_multiplier = 1.0
            # Store base multiplier and time restriction info
            self.player.racial_xp_base = effects['xp_multiplier']
            self.player.racial_xp_time_restricted = effects.get('time_restricted', False)
            self.player.racial_xp_start_hour = effects.get('start_hour', 0)
            self.player.racial_xp_end_hour = effects.get('end_hour', 24)
        
        # Shop discount (Human - Diplomatic) - Now alignment-based with trade threshold
        if 'shop_discount_good' in effects or 'shop_discount_evil' in effects:
            if not hasattr(self.player, 'racial_shop_discount_good'):
                self.player.racial_shop_discount_good = 0.0
            if not hasattr(self.player, 'racial_shop_discount_evil'):
                self.player.racial_shop_discount_evil = 0.0
            if not hasattr(self.player, 'racial_trade_threshold'):
                self.player.racial_trade_threshold = 0
            self.player.racial_shop_discount_good = effects.get('shop_discount_good', 0.0)
            self.player.racial_shop_discount_evil = effects.get('shop_discount_evil', 0.0)
            self.player.racial_trade_threshold = effects.get('trade_threshold', 10000000)
        
        # Mana regeneration on kill (Elf - Mana Surge) - Time-restricted
        if 'mana_regen_chance' in effects:
            if not hasattr(self.player, 'mana_regen_on_kill_chance'):
                self.player.mana_regen_on_kill_chance = 0.0
            self.player.mana_regen_on_kill_chance = effects['mana_regen_chance']
            self.player.mana_regen_time_restricted = effects.get('time_restricted', False)
            self.player.mana_regen_start_hour = effects.get('start_hour', 0)
            self.player.mana_regen_end_hour = effects.get('end_hour', 24)
        
        # Gathering speed (Elf - Nature's Friend)
        if 'gathering_speed_multiplier' in effects:
            if not hasattr(self.player, 'gathering_speed_multiplier'):
                self.player.gathering_speed_multiplier = 1.0
            self.player.gathering_speed_multiplier *= effects['gathering_speed_multiplier']
        
        # Physical damage reduction (Dwarf - Stone Endurance)
        if 'physical_damage_reduction' in effects:
            if not hasattr(self.player, 'racial_physical_damage_reduction'):
                self.player.racial_physical_damage_reduction = 0.0
            self.player.racial_physical_damage_reduction += effects['physical_damage_reduction']
        
        # Crafting durability bonus (Dwarf - Master Craftsman)
        if 'crafting_durability_bonus' in effects:
            if not hasattr(self.player, 'crafting_durability_bonus'):
                self.player.crafting_durability_bonus = 0.0
            self.player.crafting_durability_bonus += effects['crafting_durability_bonus']
        
        # Berserker rage (Orc - low HP damage bonus)
        if 'low_hp_damage_bonus' in effects:
            if not hasattr(self.player, 'low_hp_damage_bonus'):
                self.player.low_hp_damage_bonus = 0.0
            self.player.low_hp_damage_bonus += effects['low_hp_damage_bonus']
            if not hasattr(self.player, 'low_hp_threshold'):
                self.player.low_hp_threshold = effects.get('low_hp_threshold', 0.30)
        
        # Intimidation (Orc - Intimidating Presence) - Now time-restricted
        if 'intimidation_bonus' in effects:
            if not hasattr(self.player, 'intimidation_bonus'):
                self.player.intimidation_bonus = 0
            self.player.intimidation_bonus += effects['intimidation_bonus']
            # Store time restriction for intimidation
            if not hasattr(self.player, 'intimidation_time_restricted'):
                self.player.intimidation_time_restricted = effects.get('time_restricted', False)
                self.player.intimidation_start_hour = effects.get('start_hour', 0)
                self.player.intimidation_end_hour = effects.get('end_hour', 24)
        
        # Ranged dodge (Halfling - Small Target)
        if 'ranged_dodge_bonus' in effects:
            if not hasattr(self.player, 'ranged_dodge_bonus'):
                self.player.ranged_dodge_bonus = 0.0
            self.player.ranged_dodge_bonus += effects['ranged_dodge_bonus']
        
        # Fire damage reduction (Tiefling - Infernal Resistance)
        if 'fire_damage_reduction' in effects:
            if not hasattr(self.player, 'fire_damage_reduction'):
                self.player.fire_damage_reduction = 0.0
            self.player.fire_damage_reduction += effects['fire_damage_reduction']
        
        # Magic damage reduction (Tiefling - Infernal Resistance)
        if 'magic_damage_reduction' in effects:
            if not hasattr(self.player, 'magic_damage_reduction'):
                self.player.magic_damage_reduction = 0.0
            self.player.magic_damage_reduction += effects['magic_damage_reduction']
        
        # Spell cost reduction (Tiefling - Dark Magic) - Now weather-restricted
        if 'spell_cost_reduction' in effects:
            if not hasattr(self.player, 'spell_cost_reduction'):
                self.player.spell_cost_reduction = 0.0
            self.player.spell_cost_reduction = effects['spell_cost_reduction']
            self.player.spell_weather_restricted = effects.get('weather_restricted', False)
    
    def check_death_dodge(self, in_dungeon=False) -> bool:
        """
        Check if Halfling's Lucky Escape trait should trigger
        Args:
            in_dungeon: Whether player is currently in a dungeon
        Returns True if death was dodged, False otherwise
        """
        if not self.has_trait('halfling_lucky_escape'):
            return False
        
        trait = self.get_trait('halfling_lucky_escape')
        if not trait:
            return False
        
        # Check if dungeon-only restriction applies
        if trait.effects.get('dungeon_only', False) and not in_dungeon:
            return False
        
        if 'death_dodge_chance' in trait.effects:
            import random
            if random.random() < trait.effects['death_dodge_chance']:
                return True
        
        return False
    
    def get_berserker_damage_multiplier(self) -> float:
        """Get Orc berserker rage damage multiplier if applicable"""
        if not self.has_trait('orc_berserker_rage'):
            return 1.0
        
        trait = self.get_trait('orc_berserker_rage')
        if not trait:
            return 1.0
        
        # Check if player is below HP threshold
        hp_percent = self.player.health / self.player.max_health
        threshold = trait.effects.get('low_hp_threshold', 0.30)
        
        if hp_percent <= threshold:
            return 1.0 + trait.effects.get('low_hp_damage_bonus', 0.0)
        
        return 1.0
    
    def get_xp_multiplier(self, game_time=None) -> float:
        """Get total XP multiplier from traits
        Args:
            game_time: Optional GameTime object to check time restrictions
        """
        if not hasattr(self.player, 'racial_xp_base'):
            return 1.0
        
        # Check if time-restricted
        if hasattr(self.player, 'racial_xp_time_restricted') and self.player.racial_xp_time_restricted:
            if game_time:
                current_hour, _ = game_time.get_time_hm()
                start = self.player.racial_xp_start_hour
                end = self.player.racial_xp_end_hour
                
                # Check if current hour is within the time range
                if start <= end:
                    # Normal range (e.g., 10-16)
                    if start <= current_hour < end:
                        return self.player.racial_xp_base
                else:
                    # Wrap-around range (e.g., 20-4)
                    if current_hour >= start or current_hour < end:
                        return self.player.racial_xp_base
                return 1.0  # Outside time window
            return 1.0  # No game_time provided
        
        return self.player.racial_xp_base
    
    def get_shop_discount(self, npc_alignment='neutral', npc_type='shopkeeper', total_traded=0) -> float:
        """Get total shop discount from traits
        Args:
            npc_alignment: 'good', 'neutral', 'evil'
            npc_type: Type of NPC (shopkeeper, thieves_guild, etc.)
            total_traded: Total amount of dubloons traded with this NPC
        """
        if not hasattr(self.player, 'racial_shop_discount_good'):
            return 0.0
        
        player_alignment = getattr(self.player, 'alignment', 'neutral')  # 'good', 'neutral', 'evil'
        
        # Check evil discount (5%)
        if hasattr(self.player, 'racial_shop_discount_evil'):
            # Player must be evil or bad alignment AND dealing with evil NPCs
            if player_alignment in ['evil', 'bad'] and npc_alignment == 'evil':
                return self.player.racial_shop_discount_evil
        
        # Check good discount (2%)
        if hasattr(self.player, 'racial_shop_discount_good'):
            # Player must be good alignment, traded 10M+ with good NPCs
            if player_alignment == 'good' and npc_alignment == 'good':
                threshold = getattr(self.player, 'racial_trade_threshold', 10000000)
                if total_traded >= threshold:
                    return self.player.racial_shop_discount_good
        
        return 0.0
    
    def check_mana_regen_on_kill(self, game_time=None) -> bool:
        """Check if Elf's Mana Surge should trigger after killing an enemy
        Args:
            game_time: Optional GameTime object to check time restrictions
        Returns True if mana should be fully regenerated
        """
        if not hasattr(self.player, 'mana_regen_on_kill_chance'):
            return False
        
        # Check time restriction
        if hasattr(self.player, 'mana_regen_time_restricted') and self.player.mana_regen_time_restricted:
            if game_time:
                current_hour, _ = game_time.get_time_hm()
                start = self.player.mana_regen_start_hour
                end = self.player.mana_regen_end_hour
                
                # Check if within time window
                if start <= end:
                    if not (start <= current_hour < end):
                        return False  # Outside time window
                else:
                    if not (current_hour >= start or current_hour < end):
                        return False  # Outside time window
            else:
                return False  # No game_time provided
        
        # Roll for chance
        import random
        return random.random() < self.player.mana_regen_on_kill_chance
    
    def check_intimidation_active(self, game_time=None) -> bool:
        """Check if Orc intimidation is currently active
        Args:
            game_time: Optional GameTime object to check time restrictions
        """
        if not hasattr(self.player, 'intimidation_bonus'):
            return False
        
        # Check time restriction for Orc trait
        if hasattr(self.player, 'intimidation_time_restricted') and self.player.intimidation_time_restricted:
            if game_time:
                current_hour, _ = game_time.get_time_hm()
                start = getattr(self.player, 'intimidation_start_hour', 0)
                end = getattr(self.player, 'intimidation_end_hour', 24)
                
                # Handle wrap-around (20-4 means 8PM to 4AM)
                if start > end:
                    return current_hour >= start or current_hour < end
                else:
                    return start <= current_hour < end
            return False  # No game_time provided
        
        return True  # No time restriction or always active
    
    def get_spell_cost_reduction(self, weather_type='clear') -> float:
        """Get spell cost reduction based on weather
        Args:
            weather_type: Current weather type ('clear', 'rain', 'snow', 'fog', etc.)
        """
        if not hasattr(self.player, 'spell_cost_reduction'):
            return 0.0
        
        # Check weather restriction for Tiefling trait
        if hasattr(self.player, 'spell_weather_restricted') and self.player.spell_weather_restricted:
            # Only active during bad weather (not clear/sunny)
            if weather_type.lower() in ['clear', 'sunny', 'normal', '']:
                return 0.0
            return self.player.spell_cost_reduction
        
        return self.player.spell_cost_reduction
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for saving"""
        return {
            'trait_ids': [trait.id for trait in self.active_traits],
            'cooldowns': self.trait_cooldowns,
            'triggers': self.trait_triggers
        }
    
    def from_dict(self, data: Dict[str, Any], race):
        """Deserialize from save data"""
        self.trait_cooldowns = data.get('cooldowns', {})
        self.trait_triggers = data.get('triggers', {})
        
        # Restore traits from race
        if race:
            self.active_traits = race.traits.copy()
        
        # Re-apply passive effects
        self.apply_passive_effects()


def create_trait_manager(player, race) -> TraitManager:
    """Create a trait manager and initialize with racial traits"""
    manager = TraitManager(player)
    
    if race:
        for trait in race.traits:
            manager.add_trait(trait)
        
        manager.apply_passive_effects()
    
    return manager
