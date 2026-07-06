# Stats component for the player
class Stats:
    def __init__(self, base_stats=None):
        # Initialize with default stats if none provided
        self.base_stats = base_stats or {
            "Strength": 10,
            "Defense": 10,
            "Magic": 10,
            "Health": 100,
            "Max_Health": 100,
            "Mana": 50,
            "Max_Mana": 50,
            "Stamina": 10,  # This is the stat attribute (like Strength), NOT current stamina pool
            # Current_Stamina will be set by update_derived_attributes to match Max_Stamina
            "Speed": 10,
            "Agility": 10,
            "Willpower": 10,
            "Luck": 10,
            "Talking": 10,  # Added for Social skill tree
            "Intelligence": 10,  # Added for consistency
            "Perception": 10  # Detects disguises, stealth, traps, hidden items, lies, etc.
        }
        
        # Equipment bonuses tracked separately
        self.equipment_bonuses = {}
        
        # Set bonuses tracked separately
        self.set_bonuses = {}
        
        # Temporary effects (buffs/debuffs)
        self.temp_effects = {}
        
    def get_stat(self, stat_name):
        """
        Calculate total value of a stat including all bonuses
        
        Args:
            stat_name (str): Name of the stat to calculate
            
        Returns:
            int: Total value of the stat
        """
        # Start with base value
        total = self.base_stats.get(stat_name, 0)
        
        # Add equipment bonuses
        total += self.equipment_bonuses.get(stat_name, 0)
        
        # Add set bonuses
        total += self.set_bonuses.get(stat_name, 0)
        
        # Add temporary effects
        total += self.temp_effects.get(stat_name, 0)
        
        return total
    
    def update_equipment_bonuses(self, equipment, player_level=1):
        """
        Update stat bonuses from equipped items
        
        Args:
            equipment (Equipment): Equipment component with equipped items
            player_level (int): Player level for scaling equipment stats
        """
        # Reset equipment bonuses
        self.equipment_bonuses = {}
        
        # Import necessary functions
        from equipment import get_scaled_equipment_stats, EQUIPMENT_DATA
        
        # Process each equipped item
        for slot, item_id in equipment.equipped.items():
            if not item_id:
                continue
                
            # Get scaled stats for this item
            item_stats = get_scaled_equipment_stats(item_id, player_level)
            
            # Add bonuses from this item
            if "stat_bonuses" in item_stats:
                for stat, bonus in item_stats["stat_bonuses"].items():
                    if stat in self.equipment_bonuses:
                        self.equipment_bonuses[stat] += bonus
                    else:
                        self.equipment_bonuses[stat] = bonus
        
        # Process set bonuses
        self.set_bonuses = {}
        from equipment import EQUIPMENT_SETS
        
        for set_id, count in equipment.active_sets.items():
            if set_id in EQUIPMENT_SETS:
                set_data = EQUIPMENT_SETS[set_id]
                # Apply active bonuses for the number of pieces we have
                if count in set_data["bonuses"]:
                    bonuses = set_data["bonuses"][count]
                    for stat, value in bonuses.items():
                        if stat in self.set_bonuses:
                            self.set_bonuses[stat] += value
                        else:
                            self.set_bonuses[stat] = value
                            
    def add_temp_effect(self, effect_id, stats, duration=None):
        """
        Add a temporary stat effect (buff/debuff)
        
        Args:
            effect_id (str): Unique identifier for the effect
            stats (dict): Dictionary of stat bonuses
            duration (int, optional): Duration in turns/updates, None for permanent
        """
        self.temp_effects[effect_id] = {
            "stats": stats,
            "duration": duration,
            "remaining": duration
        }
    
    def remove_temp_effect(self, effect_id):
        """
        Remove a temporary effect
        
        Args:
            effect_id (str): ID of the effect to remove
        
        Returns:
            bool: True if effect was removed, False if not found
        """
        if effect_id in self.temp_effects:
            del self.temp_effects[effect_id]
            return True
        return False
        
    def update_effects(self):
        """
        Update all temporary effects, removing expired ones
        Should be called once per game update/turn
        """
        effects_to_remove = []
        
        for effect_id, effect_data in self.temp_effects.items():
            if effect_data["duration"] is not None:
                effect_data["remaining"] -= 1
                if effect_data["remaining"] <= 0:
                    effects_to_remove.append(effect_id)
                    
        for effect_id in effects_to_remove:
            self.remove_temp_effect(effect_id)
            
    def update_derived_attributes(self, base_speed=250):
        """
        Update all attributes derived from stats and equipment bonuses
        
        Args:
            base_speed (int): The base movement speed to use for calculations
        """
        # Calculate maximum health
        base_health = 100
        health_per_stamina = 5
        
        stamina_value = self.get_stat("Stamina")
        willpower_value = self.get_stat("Willpower")
        
        # Update max health
        max_health = base_health + (stamina_value * health_per_stamina)
        self.base_stats["Max_Health"] = max_health
        
        # Ensure health doesn't exceed max_health
        if "Health" in self.base_stats:
            self.base_stats["Health"] = min(self.base_stats["Health"], max_health)
        else:
            self.base_stats["Health"] = max_health
        
        # Update max mana (affected by both Willpower and Magic)
        willpower_mana = willpower_value * 5  # 5 mana per Willpower
        magic_value = self.get_stat("Magic")
        magic_mana = magic_value * 3  # 3 mana per Magic
        max_mana = 100 + willpower_mana + magic_mana
        self.base_stats["Max_Mana"] = max_mana
        
        # Ensure mana doesn't exceed max_mana
        if "Mana" in self.base_stats:
            self.base_stats["Mana"] = min(self.base_stats["Mana"], max_mana)
        else:
            self.base_stats["Mana"] = max_mana
        
        # Calculate spell power multiplier (1% damage per Magic point)
        spell_power = 1.0 + (magic_value * 0.01)
        self.base_stats["Spell_Power"] = spell_power
        
        # Calculate mana cost reduction (0.5% per Magic point, max 50%)
        mana_cost_reduction = min(0.5, magic_value * 0.005)
        self.base_stats["Mana_Cost_Reduction"] = mana_cost_reduction
            
        # Update max stamina
        stamina_max = 100 + (stamina_value * health_per_stamina)
        self.base_stats["Max_Stamina"] = stamina_max
        
        # Always set current stamina to max on initialization/level up (fill the bar)
        # Only keep it lower if player has used some stamina during gameplay
        if "Current_Stamina" not in self.base_stats:
            self.base_stats["Current_Stamina"] = stamina_max
        elif self.base_stats.get("Current_Stamina", 0) > stamina_max:
            # Cap at new max if max decreased
            self.base_stats["Current_Stamina"] = stamina_max