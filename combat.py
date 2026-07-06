import random
from status_effects import StatusManager, STATUS_EFFECTS


# Combat component for the player
class Combat:
    def __init__(self, stats, equipment):
        """
        Initialize combat component
        
        Args:
            stats (Stats): Reference to the player's stats component
            equipment (Equipment): Reference to the player's equipment component
        """
        self.stats = stats
        self.equipment = equipment
        self.attack_cooldown = 0
        self.magic_cooldown = 0
        self.ability_cooldowns = {}
        
        # Combat stats that don't belong in base stats
        self.critical_chance = 0.05  # 5% base critical chance
        self.critical_multiplier = 1.5  # 50% extra damage on crits
        self.dodge_chance = 0.05  # 5% base dodge chance
        
        # Status effects system
        self.status_manager = StatusManager(entity=self)
 
    def calculate_damage(self, is_magic=False):
        """
        Calculate damage for an attack based on player stats

        Args:
            is_magic (bool): Whether this is a magic attack

        Returns:
            tuple: (base_damage, critical_hit)
        """
        from equipment import EQUIPMENT_DATA

        if is_magic:
            base_stat = self.stats.get_stat("Magic")
            weapon_damage = 0  # Base magic damage

            # Check for equipped staff/wand that might add magic damage
            main_hand = self.equipment.get_equipped_item("main_hand")
            main_hand_id = None
            if isinstance(main_hand, dict):
                main_hand_id = main_hand.get("item")
            elif isinstance(main_hand, str):
                main_hand_id = main_hand

            if main_hand_id and main_hand_id in EQUIPMENT_DATA:
                weapon_damage = EQUIPMENT_DATA[main_hand_id].get("magic_damage", 0)
        else:
            base_stat = self.stats.get_stat("Strength")
            weapon_damage = 5  # Base physical damage

            # Check for equipped weapon
            main_hand = self.equipment.get_equipped_item("main_hand")
            main_hand_id = None
            stick_count = 1

            if isinstance(main_hand, dict):
                main_hand_id = main_hand.get("item")
                if main_hand_id == "stick":
                    stick_count = main_hand.get("stack_count", 1)
            elif isinstance(main_hand, str):
                main_hand_id = main_hand
                if main_hand_id == "stick":
                    # Try to access the player's inventory for legacy support
                    player = getattr(self.equipment, "owner", None)
                    if player and hasattr(player, "inventory"):
                        stick_count = player.inventory.items.get("stick", 1)
                    else:
                        stick_count = 1

            if main_hand_id and main_hand_id in EQUIPMENT_DATA:
                if main_hand_id == "stick":
                    weapon_damage = min(stick_count, 300)
                else:
                    weapon_damage = EQUIPMENT_DATA[main_hand_id].get("base_damage", 5)

        # Calculate base damage with improved scaling
        if is_magic:
            # Magic damage: weapon + (magic_stat * 1.5) for better scaling
            damage = weapon_damage + (base_stat * 1.5)
        else:
            # Physical damage: weapon + (strength_stat * 1.2) for balanced scaling
            damage = weapon_damage + (base_stat * 1.2)

        # Check for critical hit
        critical = False
        crit_chance = self.critical_chance + (self.stats.get_stat("Luck") * 0.005)  # +0.5% per Luck point
        if crit_chance > 0 and random.random() < crit_chance:
            critical = True
            # Enhanced critical multiplier based on stats
            base_crit_mult = self.critical_multiplier + (self.stats.get_stat("Luck") * 0.01)  # +1% per Luck point
            if is_magic:
                # Magic crits benefit from Magic stat
                crit_mult = base_crit_mult + (self.stats.get_stat("Magic") * 0.005)
            else:
                # Physical crits benefit from Strength stat  
                crit_mult = base_crit_mult + (self.stats.get_stat("Strength") * 0.005)
            damage *= crit_mult

        # Apply status effect multipliers
        status_multipliers = self.status_manager.get_stat_multipliers()
        damage *= status_multipliers["damage"]
        
        # Check if prevented from attacking due to status effects
        if self.status_manager.is_prevented_from_action():
            return 0, False  # Can't attack if frozen, stunned, etc.

        return int(damage), critical

    def process_attack(self, target, is_magic=False, enemies=None, player=None, dropped_equipment=None):
        """
        Process an attack against a target
        
        Args:
            target: Target entity to attack
            is_magic (bool): Whether this is a magic attack
        
        Returns:
            dict: Result of the attack with damage and effects
        """
        # Check cooldowns
        if is_magic and self.magic_cooldown > 0:
            return {"success": False, "message": "Magic on cooldown"}
        elif not is_magic and self.attack_cooldown > 0:
            return {"success": False, "message": "Attack on cooldown"}
        
        # Calculate damage
        damage, is_critical = self.calculate_damage(is_magic)
        
        # Apply dodge chance
        if hasattr(target, 'dodge_chance') and random.random() < target.dodge_chance:
            return {"success": True, "dodged": True, "message": "Attack dodged!"}
        
        # Store original damage for minimum calculation
        original_damage = damage
        
        # Apply defense reduction
        if hasattr(target, 'stats') and hasattr(target.stats, 'get_stat'):
            if is_magic:
                # Magic attacks use magic resistance
                magic_resistance = target.stats.get_stat("Magic_Resistance") if hasattr(target.stats, 'get_stat') else 0
                # Prevent division by zero: if magic_resistance is -60 or less, denominator would be <= 0
                denominator = magic_resistance + 60
                if denominator > 0:
                    resistance_reduction = min(0.7, magic_resistance / denominator)  # Max 70% reduction for magic
                else:
                    resistance_reduction = 0  # No reduction if denominator is invalid
            else:
                # Physical attacks use defense
                defense = target.stats.get_stat("Defense")
                
                # Apply racial armor effectiveness bonus (Dwarf: +25%)
                if hasattr(target, 'trait_manager') and target.trait_manager:
                    armor_bonus = target.trait_manager.get_armor_effectiveness_bonus()
                    if armor_bonus > 0:
                        defense = defense * (1 + armor_bonus)
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"[RACIAL TRAIT] Dwarf armor effectiveness: {target.stats.get_stat('Defense')} → {defense:.0f} defense (+{armor_bonus*100:.0f}%)")
                
                # Prevent division by zero: if defense is -50 or less, denominator would be <= 0
                denominator = defense + 50
                if denominator > 0:
                    resistance_reduction = min(0.75, defense / denominator)  # Max 75% reduction for physical
                else:
                    resistance_reduction = 0  # No reduction if denominator is invalid
            
            damage = int(damage * (1 - resistance_reduction))
            
        # Ensure minimum damage (10% of original damage, minimum 1)
        min_damage = max(1, int(original_damage * 0.1))
        damage = max(damage, min_damage)
        
        # Set cooldown
        if is_magic:
            self.magic_cooldown = 10  # Example cooldown of 10 frames/ticks
        else:
            self.attack_cooldown = 5   # Example cooldown of 5 frames/ticks
        
        # Check for weapon status effects
        status_effect_applied = self.check_weapon_status_effects(target)
        
        # Apply damage to target
        if hasattr(target, 'take_damage'):
            # Pass status effect info to take_damage method
            take_damage_kwargs = {
                'is_crit': is_critical, 
                'all_enemies': enemies, 
                'player': player, 
                'dropped_equipment_list': dropped_equipment
            }
            
            # Add status effect if weapon applied one
            if status_effect_applied:
                take_damage_kwargs['status_effect'] = status_effect_applied
                
            target.take_damage(damage, **take_damage_kwargs)
        
        # Prepare result
        result_message = f"Hit for {damage} damage"
        if is_critical:
            result_message += " (Critical!)"
        if status_effect_applied:
            effect_name = STATUS_EFFECTS[status_effect_applied]["name"]
            result_message += f" - {effect_name} applied!"
            
        result = {
            "success": True,
            "damage": damage,
            "critical": is_critical,
            "status_effect": status_effect_applied,
            "message": result_message
        }
        
        return result
    
    def check_weapon_status_effects(self, target):
        """Check if equipped weapon applies status effects"""
        from equipment import EQUIPMENT_DATA
        
        # Get equipped main hand weapon
        main_hand = self.equipment.get_equipped_item("main_hand")
        main_hand_id = None
        
        if isinstance(main_hand, dict):
            main_hand_id = main_hand.get("item")
        elif isinstance(main_hand, str):
            main_hand_id = main_hand
        
        if not main_hand_id or main_hand_id not in EQUIPMENT_DATA:
            return None
        
        weapon_data = EQUIPMENT_DATA[main_hand_id]
        
        # Check for status effect properties on weapon
        status_effect = weapon_data.get("status_effect")
        if status_effect:
            # Check chance to apply
            chance = weapon_data.get("status_chance", 0.2)  # Default 20% chance
            if random.random() <= chance:
                return status_effect
        
        # Check for specific weapon types that apply effects
        weapon_type_effects = {
            "poison_dagger": {"effect": "poison", "chance": 0.3},
            "flaming_sword": {"effect": "burn", "chance": 0.25},
            "frost_blade": {"effect": "freeze", "chance": 0.15},
            "cursed_mace": {"effect": "curse", "chance": 0.2},
            "lightning_spear": {"effect": "shock", "chance": 0.3}
        }
        
        if main_hand_id in weapon_type_effects:
            weapon_effect = weapon_type_effects[main_hand_id]
            if random.random() <= weapon_effect["chance"]:
                return weapon_effect["effect"]
        
        return None
    
    def apply_status_effect(self, effect_id, duration_override=None):
        """Apply a status effect to this combat entity"""
        return self.status_manager.add_status(effect_id, duration_override)
    
    def remove_status_effect(self, effect_id):
        """Remove a status effect from this combat entity"""
        return self.status_manager.remove_status(effect_id)
    
    def has_status_effect(self, effect_id):
        """Check if entity has a specific status effect"""
        return self.status_manager.has_effect(effect_id)
    
    def get_status_effects_display(self):
        """Get active status effects for UI display"""
        return self.status_manager.get_active_effects_display()
    
    def update(self, dt=1):
        """
        Update combat timers and cooldowns
        
        Args:
            dt (float): Time delta (amount to decrement cooldowns by)
        """
        # Update status effects first (this may affect other updates)
        # Note: The entity (player/enemy) should be passed to update_effects
        # This will be handled in the player/enemy update methods
        
        # Update main cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - dt)
            
        if self.magic_cooldown > 0:
            self.magic_cooldown = max(0, self.magic_cooldown - dt)
        
        # Update ability cooldowns
        for ability_id in list(self.ability_cooldowns.keys()):
            self.ability_cooldowns[ability_id] -= dt
            if self.ability_cooldowns[ability_id] <= 0:
                del self.ability_cooldowns[ability_id]
    
    def update_status_effects(self, entity):
        """
        Update status effects for the combat entity
        
        Args:
            entity: The entity (player or enemy) that has this combat component
        """
        self.status_manager.update_effects(entity)