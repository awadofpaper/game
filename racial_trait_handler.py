"""
Racial Trait Handler - Manages application of racial trait effects

Handles all racial trait bonuses, modifiers, and special abilities.
Includes achievement tracking and sound effects for trait activations.
"""

import random
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RacialTraitHandler:
    """Handles application of racial trait effects for a player"""
    
    def __init__(self, player, audio_system=None, achievement_manager=None):
        self.player = player
        self.orc_rage_active = False
        self.orc_rage_timer = 0.0
        self.audio_system = audio_system
        self.achievement_manager = achievement_manager
        
        # Achievement tracking counters
        self.orc_rage_activations = 0
        self.halfling_dodges = 0
        self.halfling_double_loots = 0
        self.dwarf_free_repairs = 0
        self.elf_mana_regen_total = 0.0
        self.human_bonus_xp_total = 0.0
        self.tiefling_fire_damage_total = 0.0
        self.orc_dual_2h_equipped = False
        
    def update(self, dt: float):
        """Update trait effects that need per-frame updates"""
        # Elf: Passive mana regeneration (0.8% max mana per second)
        if self.player.race and self.player.race.id == 'elf':
            if self.player.mana < self.player.max_mana:
                mana_regen = self.player.max_mana * 0.008 * dt  # 0.8% per second
                self.player.mana = min(self.player.mana + mana_regen, self.player.max_mana)
                # Track total mana regenerated for achievements
                self.elf_mana_regen_total += mana_regen
        
        # Orc: Rage state management
        if self.player.race and self.player.race.id == 'orc':
            self._update_orc_rage(dt)
        
        # Update achievements periodically (every second)
        if hasattr(self, '_achievement_timer'):
            self._achievement_timer += dt
            if self._achievement_timer >= 1.0:
                self._check_trait_achievements()
                self._achievement_timer = 0.0
        else:
            self._achievement_timer = 0.0
    
    def _update_orc_rage(self, dt: float):
        """Update Orc rage state"""
        hp_percent = self.player.hp / self.player.max_hp if self.player.max_hp > 0 else 1.0
        
        # Activate rage if HP below 40%
        if hp_percent < 0.40:
            if not self.orc_rage_active:
                self.orc_rage_active = True
                self.orc_rage_timer = 12.0  # 12 second duration after HP recovers
                self.orc_rage_activations += 1
                # Play rage activation sound
                if self.audio_system:
                    self.audio_system.play_orc_rage_activate()
                logger.info(f"[TRAIT] Orc rage activated! Total activations: {self.orc_rage_activations}")
        else:
            # HP recovered, count down timer
            if self.orc_rage_active:
                self.orc_rage_timer -= dt
                if self.orc_rage_timer <= 0:
                    self.orc_rage_active = False
                    self.orc_rage_timer = 0.0
                    # Play rage deactivation sound
                    if self.audio_system:
                        self.audio_system.play_orc_rage_deactivate()
                    logger.info("[TRAIT] Orc rage deactivated")
    
    def is_orc_rage_active(self) -> bool:
        """Check if Orc rage is currently active"""
        return self.orc_rage_active
    
    # ==================== XP MODIFIERS ====================
    
    def apply_xp_modifier(self, base_xp: float, xp_type: str = 'combat') -> float:
        """
        Apply racial XP modifiers
        
        Args:
            base_xp: Base XP amount
            xp_type: Type of XP ('combat', 'mining', 'woodcutting', 'fishing', 'cooking', 'gathering')
        
        Returns:
            Modified XP amount
        """
        if not self.player.race:
            return base_xp
        
        original_xp = base_xp
        
        # Human: +5% XP to all systems
        if self.player.race.id == 'human':
            base_xp *= 1.05
            bonus_xp = base_xp - original_xp
            self.human_bonus_xp_total += bonus_xp
        
        # Dwarf: +100% mining XP (2x)
        if self.player.race.id == 'dwarf' and xp_type == 'mining':
            base_xp *= 2.0
        
        # Elf: +50% gathering XP for herbs/wood
        if self.player.race.id == 'elf' and xp_type in ['woodcutting', 'gathering']:
            base_xp *= 1.5
        
        return base_xp
    
    # ==================== DAMAGE MODIFIERS ====================
    
    def apply_outgoing_damage_modifier(self, base_damage: float, damage_type: str = 'physical') -> float:
        """
        Apply racial outgoing damage modifiers
        
        Args:
            base_damage: Base damage amount
            damage_type: Type of damage ('physical', 'melee', 'spell', 'fire')
        
        Returns:
            Modified damage amount
        """
        if not self.player.race:
            return base_damage
        
        multiplier = 1.0
        
        # Orc: +15% melee damage
        if self.player.race.id == 'orc' and damage_type in ['physical', 'melee']:
            multiplier *= 1.15
            
            # Orc Rage: +30% damage when active
            if self.orc_rage_active:
                multiplier *= 1.30
        
        # Tiefling: +25% spell damage
        if self.player.race.id == 'tiefling' and damage_type in ['spell', 'magic']:
            multiplier *= 1.25
            
            # Tiefling Fire: +40% fire spell damage (stacks with +25% spell)
            if damage_type == 'fire':
                multiplier *= 1.40
        
        return base_damage * multiplier
    
    def apply_incoming_damage_reduction(self, damage: float, damage_type: str = 'physical') -> float:
        """
        Apply racial damage reduction
        
        Args:
            damage: Incoming damage amount
            damage_type: Type of damage ('physical', 'magic', 'fire')
        
        Returns:
            Reduced damage amount
        """
        if not self.player.race:
            return damage
        
        reduction = 0.0
        
        # Dwarf: 12% physical damage reduction
        if self.player.race.id == 'dwarf' and damage_type == 'physical':
            reduction += 0.12
        
        # Orc Rage: 10% damage reduction when raging
        if self.player.race.id == 'orc' and self.orc_rage_active:
            reduction += 0.10
        
        # Tiefling: 15% magic, 25% fire damage reduction
        if self.player.race.id == 'tiefling':
            if damage_type == 'magic':
                reduction += 0.15
            elif damage_type == 'fire':
                reduction += 0.25
        
        return damage * (1.0 - min(reduction, 0.75))  # Cap at 75% reduction
    
    # ==================== ATTACK SPEED MODIFIERS ====================
    
    def get_attack_speed_modifier(self) -> float:
        """
        Get attack speed multiplier
        
        Returns:
            Attack speed multiplier (1.0 = normal, 1.2 = 20% faster)
        """
        if not self.player.race:
            return 1.0
        
        # Orc Rage: +20% attack speed
        if self.player.race.id == 'orc' and self.orc_rage_active:
            return 1.20
        
        return 1.0
    
    # ==================== MOVEMENT SPEED MODIFIERS ====================
    
    def get_movement_speed_modifier(self, terrain_type: Optional[str] = None) -> float:
        """
        Get movement speed multiplier
        
        Args:
            terrain_type: Current terrain type (e.g., 'forest', 'grassland')
        
        Returns:
            Movement speed multiplier (1.0 = normal, 1.25 = 25% faster)
        """
        if not self.player.race:
            return 1.0
        
        multiplier = 1.0
        
        # Elf: +30% speed in forests/grasslands
        if self.player.race.id == 'elf' and terrain_type in ['forest', 'grassland']:
            multiplier *= 1.30
        
        # Halfling: +25% speed always
        if self.player.race.id == 'halfling':
            multiplier *= 1.25
        
        return multiplier
    
    # ==================== COMBAT CHECKS ====================
    
    def check_dodge_chance(self) -> bool:
        """
        Check if an attack is dodged
        
        Returns:
            True if attack should be dodged
        """
        if not self.player.race:
            return False
        
        # Halfling: 8% chance to dodge any attack
        if self.player.race.id == 'halfling':
            if random.random() < 0.08:
                self.halfling_dodges += 1
                if self.audio_system:
                    self.audio_system.play_halfling_dodge()
                logger.info(f"[TRAIT] Halfling dodged attack! Total dodges: {self.halfling_dodges}")
                return True
        
        return False
    
    def get_critical_hit_bonus(self) -> float:
        """
        Get critical hit chance bonus
        
        Returns:
            Critical hit chance bonus (0.05 = +5%)
        """
        if not self.player.race:
            return 0.0
        
        # Halfling: +5% crit chance
        if self.player.race.id == 'halfling':
            return 0.05
        
        return 0.0
    
    def check_double_loot(self) -> bool:
        """
        Check if loot should be doubled
        
        Returns:
            True if loot should be doubled
        """
        if not self.player.race:
            return False
        
        # Halfling: 12% chance for double loot
        if self.player.race.id == 'halfling':
            if random.random() < 0.12:
                self.halfling_double_loots += 1
                if self.audio_system:
                    self.audio_system.play_halfling_double_loot()
                logger.info(f"[TRAIT] Halfling doubled loot! Total: {self.halfling_double_loots}")
                return True
        
        return False
    
    # ==================== SHOP & ECONOMY ====================
    
    def apply_shop_price_modifier(self, base_price: int, is_buying: bool = True) -> int:
        """
        Apply racial shop price modifiers
        
        Args:
            base_price: Base price in gold
            is_buying: True if buying from shop, False if selling to shop
        
        Returns:
            Modified price
        """
        if not self.player.race:
            return base_price
        
        # Human: -15% when buying, +15% when selling
        if self.player.race.id == 'human':
            if is_buying:
                return int(base_price * 0.85)  # 15% discount
            else:
                return int(base_price * 1.15)  # 15% bonus
        
        return base_price
    
    def apply_quest_gold_modifier(self, base_gold: int) -> int:
        """
        Apply racial quest gold modifiers
        
        Args:
            base_gold: Base quest reward gold
        
        Returns:
            Modified gold amount
        """
        if not self.player.race:
            return base_gold
        
        # Human: +10% quest gold
        if self.player.race.id == 'human':
            return int(base_gold * 1.10)
        
        return base_gold
    
    def get_reputation_bonus(self) -> int:
        """
        Get starting reputation bonus with NPCs
        
        Returns:
            Reputation bonus amount
        """
        if not self.player.race:
            return 0
        
        # Human: +15 starting reputation
        if self.player.race.id == 'human':
            return 15
        
        return 0
    
    # ==================== CRAFTING & REPAIRS ====================
    
    def get_repair_cost_modifier(self) -> float:
        """
        Get repair cost modifier
        
        Returns:
            Cost multiplier (0.0 = free, 1.0 = normal cost)
        """
        if not self.player.race:
            return 1.0
        
        # Dwarf: Free repairs
        if self.player.race.id == 'dwarf':
            self.dwarf_free_repairs += 1
            if self.audio_system:
                self.audio_system.play_dwarf_repair()
            logger.info(f"[TRAIT] Dwarf free repair! Total: {self.dwarf_free_repairs}")
            return 0.0
        
        return 1.0
    
    def get_crafting_durability_bonus(self) -> float:
        """
        Get durability bonus for crafted/repaired items
        
        Returns:
            Durability multiplier bonus (0.20 = +20%)
        """
        if not self.player.race:
            return 0.0
        
        # Dwarf: +20% durability on crafted equipment
        if self.player.race.id == 'dwarf':
            return 0.20
        
        return 0.0
    
    # ==================== SPELL & MANA ====================
    
    def apply_spell_cost_modifier(self, base_cost: float, spell_element: Optional[str] = None) -> float:
        """
        Apply racial spell cost modifiers
        
        Args:
            base_cost: Base mana cost
            spell_element: Element type ('fire', 'ice', etc.)
        
        Returns:
            Modified mana cost
        """
        if not self.player.race:
            return base_cost
        
        # Tiefling: -15% all spell costs
        if self.player.race.id == 'tiefling':
            base_cost *= 0.85  # 15% reduction
            
            # Tiefling Fire: -30% fire spell costs (replaces the -15%)
            if spell_element == 'fire':
                base_cost = base_cost / 0.85 * 0.70  # Remove general discount, apply fire discount
        
        return max(1.0, base_cost)  # Minimum 1 mana
    
    def apply_mana_regen_modifier(self, base_regen: float, source: str = 'natural') -> float:
        """
        Apply racial mana regen modifiers
        
        Args:
            base_regen: Base mana regeneration amount
            source: Source of regen ('natural', 'potion', 'rest')
        
        Returns:
            Modified regen amount
        """
        if not self.player.race:
            return base_regen
        
        # Elf: +20% mana regen from resting/potions
        if self.player.race.id == 'elf' and source in ['potion', 'rest']:
            return base_regen * 1.20
        
        return base_regen
    
    # ==================== DETECTION & STEALTH ====================
    
    def get_detection_range_modifier(self) -> float:
        """
        Get enemy detection range modifier
        
        Returns:
            Detection range multiplier (0.6 = enemies detect at 60% normal range)
        """
        if not self.player.race:
            return 1.0
        
        # Elf: -40% detection range
        if self.player.race.id == 'elf':
            return 0.60
        
        # Halfling: -50% detection range
        if self.player.race.id == 'halfling':
            return 0.50
        
        return 1.0
    
    # ==================== EQUIPMENT CHECKS ====================
    
    def can_dual_wield_two_handed(self) -> bool:
        """
        Check if player can dual-wield two-handed weapons
        
        Returns:
            True if dual-wielding 2H weapons is allowed
        """
        if not self.player.race:
            return False
        
        # Orc: Can dual-wield 2H weapons
        return self.player.race.id == 'orc'
    
    def get_dual_2h_attack_speed_penalty(self) -> float:
        """
        Get attack speed penalty when dual-wielding 2H weapons
        
        Returns:
            Attack speed penalty (0.20 = 20% slower)
        """
        # Orc: -20% attack speed when dual-wielding 2H
        if self.player.race and self.player.race.id == 'orc':
            return 0.20
        
        return 0.0
    
    def get_armor_effectiveness_bonus(self) -> float:
        """
        Get armor effectiveness bonus
        
        Returns:
            Armor effectiveness multiplier (0.25 = +25% armor value)
        """
        if not self.player.race:
            return 0.0
        
        # Dwarf: +25% armor effectiveness
        if self.player.race.id == 'dwarf':
            return 0.25
        
        return 0.0
    
    def has_knockback_immunity(self) -> bool:
        """
        Check if player is immune to knockback
        
        Returns:
            True if immune to knockback effects
        """
        if not self.player.race:
            return False
        
        # Dwarf: Immune to knockback
        return self.player.race.id == 'dwarf'
    
    # ==================== STAMINA ====================
    
    def get_sprint_stamina_modifier(self) -> float:
        """
        Get stamina cost modifier for sprinting
        
        Returns:
            Stamina cost multiplier (0.9 = 10% less stamina cost)
        """
        if not self.player.race:
            return 1.0
        
        # Halfling: -10% stamina cost for sprinting
        if self.player.race.id == 'halfling':
            return 0.90
        
        return 1.0
    
    # ==================== LEVELING ====================
    
    def get_bonus_stat_points_per_level(self) -> int:
        """
        Get bonus stat points awarded per level
        
        Returns:
            Additional stat points per level
        """
        if not self.player.race:
            return 0
        
        # Human: +1 extra stat point per level (4 total instead of 3)
        if self.player.race.id == 'human':
            return 1
        
        return 0
    
    # ==================== STATUS EFFECTS ====================
    
    def get_status_effect_resistance(self, effect_type: str = None) -> float:
        """
        Get resistance to status effects (reduces duration)
        
        Args:
            effect_type: Type of status effect (e.g., 'burn', 'poison', 'freeze')
        
        Returns:
            Resistance multiplier (0.7 = 30% reduced duration, 0.0 = immune)
        """
        if not self.player.race:
            return 1.0
        
        race_id = self.player.race.id
        
        # Dwarf: 50% resistance to physical status effects (bleed, stun)
        if race_id == 'dwarf':
            if effect_type in ['bleed', 'bleeding', 'stun', 'stunned', 'slow', 'slowed']:
                return 0.5  # 50% reduced duration
        
        # Tiefling: 30% resistance to fire/burn, 25% to other magic effects
        if race_id == 'tiefling':
            if effect_type in ['burn', 'burning', 'fire']:
                return 0.7  # 30% reduced duration (stronger)
            elif effect_type in ['freeze', 'frozen', 'poison', 'poisoned', 'curse', 'cursed']:
                return 0.75  # 25% reduced duration
        
        # Orc: 40% resistance to status effects during rage
        if race_id == 'orc' and hasattr(self, 'orc_rage_active') and self.orc_rage_active:
            return 0.6  # 40% reduced duration when raging
        
        # Elf: 20% resistance to nature-based effects
        if race_id == 'elf':
            if effect_type in ['poison', 'poisoned', 'slow', 'slowed']:
                return 0.8  # 20% reduced duration
        
        return 1.0  # No resistance
    
    # ==================== STATUS EFFECTS ====================
    
    def get_status_effect_resistance(self) -> float:
        """
        Get resistance to status effects
        
        Returns:
            Resistance chance (0.30 = 30% chance to resist)
        """
        if not self.player.race:
            return 0.0
        
        # Tiefling: +30% status effect resistance
        if self.player.race.id == 'tiefling':
            return 0.30
        
        return 0.0
    
    def get_status_effect_duration_modifier(self) -> float:
        """
        Get status effect duration modifier
        
        Returns:
            Duration multiplier (0.60 = 40% shorter duration)
        """
        if not self.player.race:
            return 1.0
        
        # Tiefling: -40% status effect duration
        if self.player.race.id == 'tiefling':
            return 0.60
        
        return 1.0
    
    # ==================== ACHIEVEMENT TRACKING ====================
    
    def _check_trait_achievements(self):
        """Check and update racial trait achievements"""
        if not self.achievement_manager or not self.player.race:
            return
        
        # Check if dual-wielding 2H weapons as Orc
        if self.player.race.id == 'orc':
            weapon = self.player.equipment.get('weapon')
            offhand = self.player.equipment.get('offhand')
            if weapon and offhand:
                weapon_is_2h = getattr(weapon, 'two_handed', False)
                offhand_is_2h = getattr(offhand, 'two_handed', False)
                if weapon_is_2h and offhand_is_2h:
                    self.orc_dual_2h_equipped = True
        
        # Update all trait achievements
        self.achievement_manager.check_all_racial_traits(
            self.orc_rage_activations,
            self.halfling_dodges,
            self.halfling_double_loots,
            self.dwarf_free_repairs,
            self.elf_mana_regen_total,
            self.human_bonus_xp_total,
            self.tiefling_fire_damage_total,
            self.orc_dual_2h_equipped
        )
    
    # ==================== UTILITY ====================
    
    def get_active_trait_info(self) -> list:
        """
        Get information about currently active racial traits
        
        Returns:
            List of dicts with trait info
        """
        if not self.player.race:
            return []
        
        info = []
        
        # Add all racial traits
        for trait in self.player.race.traits:
            trait_info = {
                'name': trait.name,
                'description': trait.description,
                'active': True
            }
            info.append(trait_info)
        
        # Add dynamic status (e.g., Orc rage)
        if self.player.race.id == 'orc' and self.orc_rage_active:
            info.append({
                'name': 'RAGE ACTIVE',
                'description': f'Berserking! ({self.orc_rage_timer:.1f}s remaining)',
                'active': True
            })
        
        return info
    
    def to_dict(self) -> dict:
        """Serialize trait handler state for saving"""
        return {
            'orc_rage_active': self.orc_rage_active,
            'orc_rage_timer': self.orc_rage_timer,
            # Achievement tracking counters
            'orc_rage_activations': getattr(self, 'orc_rage_activations', 0),
            'halfling_dodges': getattr(self, 'halfling_dodges', 0),
            'halfling_double_loots': getattr(self, 'halfling_double_loots', 0),
            'dwarf_free_repairs': getattr(self, 'dwarf_free_repairs', 0),
            'elf_mana_regen_total': getattr(self, 'elf_mana_regen_total', 0.0),
            'human_bonus_xp_total': getattr(self, 'human_bonus_xp_total', 0.0),
            'tiefling_fire_damage_total': getattr(self, 'tiefling_fire_damage_total', 0.0),
            'orc_dual_2h_equipped': getattr(self, 'orc_dual_2h_equipped', False)
        }
    
    @staticmethod
    def from_dict(data: dict, player, audio_system=None, achievement_manager=None):
        """Deserialize trait handler from save data"""
        handler = RacialTraitHandler(player, audio_system, achievement_manager)
        handler.orc_rage_active = data.get('orc_rage_active', False)
        handler.orc_rage_timer = data.get('orc_rage_timer', 0.0)
        # Restore achievement tracking counters
        handler.orc_rage_activations = data.get('orc_rage_activations', 0)
        handler.halfling_dodges = data.get('halfling_dodges', 0)
        handler.halfling_double_loots = data.get('halfling_double_loots', 0)
        handler.dwarf_free_repairs = data.get('dwarf_free_repairs', 0)
        handler.elf_mana_regen_total = data.get('elf_mana_regen_total', 0.0)
        handler.human_bonus_xp_total = data.get('human_bonus_xp_total', 0.0)
        handler.tiefling_fire_damage_total = data.get('tiefling_fire_damage_total', 0.0)
        handler.orc_dual_2h_equipped = data.get('orc_dual_2h_equipped', False)
        return handler
