"""
Status Effects System - High Priority Enhancement
Adds tactical depth to combat with buffs, debuffs, and damage over time
"""

import time
from enum import Enum

class StatusType(Enum):
    BUFF = "buff"
    DEBUFF = "debuff"
    DAMAGE = "damage"
    HEALING = "healing"

class StatusEffect:
    def __init__(self, effect_id, duration, potency=1.0):
        self.effect_id = effect_id
        self.duration = duration
        self.potency = potency
        self.start_time = time.time()
        self.last_tick = time.time()
        
    def is_expired(self):
        return time.time() - self.start_time >= self.duration
    
    def should_tick(self, tick_interval=1.0):
        """Check if enough time has passed for the next tick"""
        return time.time() - self.last_tick >= tick_interval
    
    def tick(self):
        """Mark that a tick has occurred"""
        self.last_tick = time.time()

# Status effect definitions with enhanced properties
STATUS_EFFECTS = {
    # Damage over time effects
    "burn": {
        "name": "Burning",
        "type": StatusType.DAMAGE,
        "damage_per_tick": 3,
        "tick_interval": 1.0,
        "duration": 5.0,
        "color": (255, 100, 0),
        "description": "Takes fire damage over time",
        "stacks": False
    },
    "poison": {
        "name": "Poisoned", 
        "type": StatusType.DAMAGE,
        "damage_per_tick": 2,
        "tick_interval": 1.5,
        "duration": 8.0,
        "color": (100, 255, 100),
        "description": "Takes poison damage over time",
        "stacks": True  # Multiple poison effects can stack
    },
    "bleed": {
        "name": "Bleeding",
        "type": StatusType.DAMAGE, 
        "damage_per_tick": 4,
        "tick_interval": 1.0,
        "duration": 4.0,
        "color": (200, 0, 0),
        "description": "Bleeding out from wounds",
        "stacks": True
    },
    
    # Debuffs
    "freeze": {
        "name": "Frozen",
        "type": StatusType.DEBUFF,
        "speed_multiplier": 0.3,
        "duration": 3.0,
        "color": (150, 200, 255),
        "description": "Movement and attack speed reduced",
        "prevents_action": True
    },
    "slow": {
        "name": "Slowed",
        "type": StatusType.DEBUFF,
        "speed_multiplier": 0.6,
        "duration": 5.0,
        "color": (100, 100, 150),
        "description": "Movement speed reduced"
    },
    "curse": {
        "name": "Cursed",
        "type": StatusType.DEBUFF,
        "damage_taken_multiplier": 1.3,
        "defense_multiplier": 0.7,
        "duration": 10.0,
        "color": (100, 0, 100),
        "description": "Takes more damage and has reduced defense"
    },
    "blind": {
        "name": "Blinded",
        "type": StatusType.DEBUFF,
        "accuracy_multiplier": 0.5,
        "duration": 4.0,
        "color": (50, 50, 50),
        "description": "Accuracy greatly reduced"
    },
    
    # Buffs
    "blessed": {
        "name": "Blessed",
        "type": StatusType.BUFF,
        "damage_multiplier": 1.25,
        "defense_multiplier": 1.15,
        "duration": 12.0,
        "color": (255, 255, 150),
        "description": "Increased damage and defense"
    },
    "rage": {
        "name": "Enraged",
        "type": StatusType.BUFF,
        "damage_multiplier": 1.4,
        "speed_multiplier": 1.2,
        "defense_multiplier": 0.8,  # Trade-off: less defense
        "duration": 8.0,
        "color": (255, 50, 50),
        "description": "Increased damage and speed, reduced defense"
    },
    "shield": {
        "name": "Magic Shield",
        "type": StatusType.BUFF,
        "damage_reduction": 0.4,  # 40% damage reduction
        "duration": 15.0,
        "color": (100, 150, 255),
        "description": "Magical barrier reduces incoming damage"
    },
    "haste": {
        "name": "Haste",
        "type": StatusType.BUFF,
        "speed_multiplier": 1.5,
        "attack_speed_multiplier": 1.3,
        "duration": 6.0,
        "color": (150, 255, 150),
        "description": "Increased movement and attack speed"
    },
    
    # Healing over time
    "regeneration": {
        "name": "Regenerating",
        "type": StatusType.HEALING,
        "heal_per_tick": 5,
        "tick_interval": 2.0,
        "duration": 10.0,
        "color": (0, 255, 0),
        "description": "Slowly restores health over time"
    },
    
    # Potion buffs
    "strength_boost": {
        "name": "Strength Boost",
        "type": StatusType.BUFF,
        "damage_multiplier": 1.35,
        "strength_bonus": 10,
        "duration": 30.0,
        "color": (255, 100, 100),
        "description": "Greatly increased attack damage and strength"
    },
    "defense_boost": {
        "name": "Defense Boost",
        "type": StatusType.BUFF,
        "defense_multiplier": 1.4,
        "damage_reduction": 0.25,
        "duration": 30.0,
        "color": (100, 100, 255),
        "description": "Significantly increased defense and damage resistance"
    },
    "invisibility": {
        "name": "Invisible",
        "type": StatusType.BUFF,
        "stealth_bonus": 100,
        "enemy_detection_range": 0.1,  # Enemies detect at 10% normal range
        "duration": 20.0,
        "color": (200, 200, 255),
        "description": "Near-invisible to enemies, greatly reduced detection"
    },
    "fire_resistance": {
        "name": "Fire Resistance",
        "type": StatusType.BUFF,
        "fire_damage_reduction": 0.75,  # 75% fire damage reduction
        "burn_immunity": True,
        "duration": 45.0,
        "color": (255, 150, 50),
        "description": "Strong resistance to fire damage, immune to burning"
    },
    "torch_light": {
        "name": "Torch Light",
        "type": StatusType.BUFF,
        "light_radius_bonus": 5,  # Increases visibility/light radius
        "duration": 60.0,  # 1 minute
        "color": (255, 200, 100),
        "description": "Carrying a lit torch, increased visibility"
    },
    "rope_escape": {
        "name": "Rope Escape",
        "type": StatusType.BUFF,
        "speed_multiplier": 1.5,  # 50% speed boost
        "defense_multiplier": 1.2,  # 20% defense boost while escaping
        "duration": 15.0,  # 15 seconds
        "color": (200, 150, 100),
        "description": "Using rope for quick escape, increased speed and defense"
    },
    "map_vision": {
        "name": "Map Vision",
        "type": StatusType.BUFF,
        "detection_range_bonus": 200,  # Increases enemy detection range
        "reveals_enemies": True,  # Shows enemy positions
        "duration": 30.0,  # 30 seconds
        "color": (150, 200, 255),
        "description": "Studied the map, revealing nearby enemies and landmarks"
    }
}

class StatusManager:
    def __init__(self, entity=None):
        self.active_effects = {}  # effect_id: StatusEffect
        self.entity = entity  # Store reference to entity for racial trait checks
        
    def add_status(self, effect_id, duration_override=None, potency=1.0):
        """Add a status effect with racial resistance applied"""
        if effect_id not in STATUS_EFFECTS:
            return False
            
        effect_data = STATUS_EFFECTS[effect_id]
        duration = duration_override or effect_data["duration"]
        
        # Apply racial status effect resistance
        if self.entity and hasattr(self.entity, 'trait_manager') and self.entity.trait_manager:
            resistance_multiplier = self.entity.trait_manager.get_status_effect_resistance(effect_id)
            if resistance_multiplier < 1.0:
                original_duration = duration
                duration = duration * resistance_multiplier
                
                # Log resistance
                import logging
                logger = logging.getLogger(__name__)
                reduction_percent = (1 - resistance_multiplier) * 100
                logger.info(f"[RACIAL TRAIT] Status effect resistance: {effect_id} duration {original_duration:.1f}s → {duration:.1f}s (-{reduction_percent:.0f}%)")
                
                # If duration is reduced to near zero, don't apply effect
                if duration < 0.5:
                    logger.info(f"[RACIAL TRAIT] {effect_id} resisted completely!")
                    return False
        
        # Handle stacking
        if effect_id in self.active_effects:
            if effect_data.get("stacks", False):
                # Create unique key for stacking effects
                stack_key = f"{effect_id}_{len([k for k in self.active_effects.keys() if k.startswith(effect_id)])}"
                self.active_effects[stack_key] = StatusEffect(effect_id, duration, potency)
            else:
                # Refresh duration for non-stacking effects
                self.active_effects[effect_id].duration = duration
                self.active_effects[effect_id].start_time = time.time()
        else:
            self.active_effects[effect_id] = StatusEffect(effect_id, duration, potency)
        
        return True
    
    def remove_status(self, effect_id):
        """Remove a status effect"""
        if effect_id in self.active_effects:
            del self.active_effects[effect_id]
            return True
        return False
    
    def remove_all_status(self, effect_id):
        """Remove all instances of a status effect (useful for stacking effects)"""
        removed_count = 0
        keys_to_remove = [key for key in self.active_effects.keys() if key.startswith(effect_id)]
        for key in keys_to_remove:
            del self.active_effects[key]
            removed_count += 1
        return removed_count
    
    def update_effects(self, entity):
        """Update all status effects for an entity"""
        expired_effects = []
        
        for effect_key, effect in self.active_effects.items():
            effect_id = effect.effect_id
            effect_data = STATUS_EFFECTS[effect_id]
            
            # Check if effect expired
            if effect.is_expired():
                expired_effects.append(effect_key)
                continue
            
            # Process damage/healing over time effects
            if effect_data["type"] in [StatusType.DAMAGE, StatusType.HEALING]:
                if effect.should_tick(effect_data.get("tick_interval", 1.0)):
                    effect.tick()
                    
                    if effect_data["type"] == StatusType.DAMAGE:
                        damage = effect_data.get("damage_per_tick", 0) * effect.potency
                        if hasattr(entity, 'take_damage'):
                            entity.take_damage(damage, is_status=True, status_type=effect_id)
                    
                    elif effect_data["type"] == StatusType.HEALING:
                        healing = effect_data.get("heal_per_tick", 0) * effect.potency
                        if hasattr(entity, 'heal'):
                            entity.heal(healing)
        
        # Remove expired effects
        for effect_key in expired_effects:
            del self.active_effects[effect_key]
    
    def get_stat_multipliers(self):
        """Get combined stat multipliers from all active effects"""
        multipliers = {
            "damage": 1.0,
            "defense": 1.0,
            "speed": 1.0,
            "attack_speed": 1.0,
            "accuracy": 1.0,
            "damage_reduction": 0.0,
            "damage_taken": 1.0
        }
        
        for effect in self.active_effects.values():
            effect_data = STATUS_EFFECTS[effect.effect_id]
            
            multipliers["damage"] *= effect_data.get("damage_multiplier", 1.0)
            multipliers["defense"] *= effect_data.get("defense_multiplier", 1.0)
            multipliers["speed"] *= effect_data.get("speed_multiplier", 1.0)
            multipliers["attack_speed"] *= effect_data.get("attack_speed_multiplier", 1.0)
            multipliers["accuracy"] *= effect_data.get("accuracy_multiplier", 1.0)
            multipliers["damage_reduction"] += effect_data.get("damage_reduction", 0.0)
            multipliers["damage_taken"] *= effect_data.get("damage_taken_multiplier", 1.0)
        
        return multipliers
    
    def has_effect(self, effect_id):
        """Check if entity has a specific status effect"""
        return any(k.startswith(effect_id) for k in self.active_effects.keys())
    
    def is_prevented_from_action(self):
        """Check if any effects prevent the entity from taking actions"""
        for effect in self.active_effects.values():
            effect_data = STATUS_EFFECTS[effect.effect_id]
            if effect_data.get("prevents_action", False):
                return True
        return False
    
    def get_active_effects_display(self):
        """Get list of active effects for UI display"""
        display_effects = []
        for effect in self.active_effects.values():
            effect_data = STATUS_EFFECTS[effect.effect_id]
            remaining_time = effect.duration - (time.time() - effect.start_time)
            display_effects.append({
                "name": effect_data["name"],
                "description": effect_data["description"],
                "remaining_time": remaining_time,
                "color": effect_data["color"]
            })
        return display_effects

# Integration example for player.py
def integrate_status_effects_to_player():
    """Example of how to integrate status effects into player class"""
    
    # Add to Player.__init__():
    # self.status_manager = StatusManager()
    
    # Modify Player.take_damage():
    def take_damage_with_status(self, amount, **kwargs):
        # Apply status effect multipliers
        multipliers = self.status_manager.get_stat_multipliers()
        
        # Modify damage based on status effects
        amount *= multipliers["damage_taken"]
        amount *= (1 - multipliers["damage_reduction"])
        
        # Apply status effect if attack has one
        status_effect = kwargs.get("status_effect")
        if status_effect:
            self.status_manager.add_status(status_effect)
        
        # Original damage logic...
        # self.health -= amount
    
    # Add to Player.update():
    def update_with_status(self, dt):
        # Update status effects
        self.status_manager.update_effects(self)
        
        # Check if prevented from action
        if self.status_manager.is_prevented_from_action():
            return  # Skip normal update
        
        # Apply speed multipliers to movement
        multipliers = self.status_manager.get_stat_multipliers()
        effective_speed = self.speed * multipliers["speed"]
        
        # Original update logic...

# Example weapon modifications to apply status effects
WEAPON_STATUS_EFFECTS = {
    "poison_dagger": {"status_effect": "poison", "chance": 0.3},
    "flaming_sword": {"status_effect": "burn", "chance": 0.25},
    "frost_blade": {"status_effect": "slow", "chance": 0.4},
    "cursed_mace": {"status_effect": "curse", "chance": 0.15}
}