"""
Weather-specific items and equipment for The Best Yet RPG
Adds weather-appropriate gear that NPCs can sell during different weather conditions
"""

import time
import random

# Weather-specific equipment data
WEATHER_EQUIPMENT = {
    "waterproof_cloak": {
        "name": "Waterproof Cloak",
        "type": "cloak",
        "slot": "chest",
        "stats": {"defense": 2, "water_resistance": 15},
        "special": "rain_protection",
        "description": "Keeps you dry in the wettest weather",
        "price": 25,
        "weather_availability": ["rain", "storm"]
    },
    "umbrella": {
        "name": "Sturdy Umbrella", 
        "type": "tool",
        "slot": "off_hand",
        "stats": {"rain_protection": 20},
        "special": "rain_shield", 
        "description": "Blocks rain and provides shelter",
        "price": 10,
        "weather_availability": ["rain", "storm"]
    },
    "winter_cloak": {
        "name": "Thick Winter Cloak",
        "type": "cloak", 
        "slot": "chest",
        "stats": {"defense": 3, "cold_resistance": 20},
        "special": "cold_protection",
        "description": "Insulated against freezing temperatures",
        "price": 30,
        "weather_availability": ["snow"]
    },
    "fur_boots": {
        "name": "Fur-Lined Boots",
        "type": "boots",
        "slot": "feet", 
        "stats": {"defense": 2, "cold_resistance": 10, "ice_grip": 15},
        "special": "ice_walking",
        "description": "Warm feet and sure footing on ice",
        "price": 20,
        "weather_availability": ["snow"]
    },
    "storm_lantern": {
        "name": "Storm Lantern",
        "type": "light",
        "slot": "off_hand",
        "stats": {"light_radius": 8, "wind_resistance": 25},
        "special": "storm_light",
        "description": "Burns bright even in fierce storms", 
        "price": 35,
        "weather_availability": ["storm", "fog"]
    },
    "compass": {
        "name": "Reliable Compass",
        "type": "tool",
        "slot": "accessory",
        "stats": {"navigation": 20},
        "special": "direction_finding",
        "description": "Never lose your way, even in thick fog",
        "price": 15,
        "weather_availability": ["fog"]
    },
    "lightning_rod": {
        "name": "Personal Lightning Rod",
        "type": "accessory", 
        "slot": "accessory",
        "stats": {"lightning_protection": 50},
        "special": "lightning_safety",
        "description": "Redirects lightning strikes away from you",
        "price": 50,
        "weather_availability": ["storm"]
    }
}

# Weather consumables
WEATHER_CONSUMABLES = {
    "hot_soup": {
        "name": "Hot Soup",
        "type": "consumable",
        "effects": {"health": 30, "warmth": 10, "cold_resistance": 5},
        "duration": 300,  # 5 minutes
        "description": "Warms you up from the inside",
        "price": 5,
        "weather_availability": ["rain", "snow", "storm"]
    },
    "hot_cider": {
        "name": "Mulled Cider", 
        "type": "consumable",
        "effects": {"health": 15, "warmth": 15, "cold_resistance": 8},
        "duration": 240,  # 4 minutes
        "description": "Spiced warmth for cold weather",
        "price": 3,
        "weather_availability": ["snow"]
    },
    "energy_ration": {
        "name": "Emergency Rations",
        "type": "consumable", 
        "effects": {"health": 40, "stamina": 25},
        "duration": 0,  # Instant
        "description": "Dense nutrition for harsh conditions",
        "price": 8,
        "weather_availability": ["storm"]
    },
    "clarity_potion": {
        "name": "Clarity Draught",
        "type": "consumable",
        "effects": {"vision_range": 5, "fog_resistance": 15},
        "duration": 600,  # 10 minutes
        "description": "See clearly through fog and mist",
        "price": 12,
        "weather_availability": ["fog"]
    }
}

def get_weather_appropriate_items(current_weather: str) -> dict:
    """Get items appropriate for current weather conditions"""
    appropriate_items = {}
    
    # Normalize weather types
    if current_weather.lower() in ["thunder", "thunderstorm"]:
        current_weather = "storm"
    elif current_weather.lower() == "light_rain":
        current_weather = "rain"
    
    # Get appropriate equipment
    for item_id, item_data in WEATHER_EQUIPMENT.items():
        if current_weather in item_data.get("weather_availability", []):
            appropriate_items[item_id] = item_data.copy()
    
    # Get appropriate consumables
    for item_id, item_data in WEATHER_CONSUMABLES.items():
        if current_weather in item_data.get("weather_availability", []):
            appropriate_items[item_id] = item_data.copy()
    
    return appropriate_items

def get_weather_price_modifier(current_weather: str, item_type: str) -> float:
    """Get price modifier for items based on weather demand"""
    modifiers = {
        "rain": {
            "water_protection": 1.5,
            "shelter_items": 1.3,
            "outdoor_gear": 0.8
        },
        "storm": {
            "safety_equipment": 2.0,
            "emergency_supplies": 1.8,
            "luxury_items": 0.5
        },
        "snow": {
            "warm_clothing": 1.6,
            "heating_supplies": 1.4,
            "cold_weather_gear": 1.3
        },
        "fog": {
            "navigation_tools": 1.4,
            "light_sources": 1.2,
            "visibility_aids": 1.5
        },
        "clear": {
            "travel_supplies": 1.1,
            "outdoor_activities": 1.0
        }
    }
    
    weather_mods = modifiers.get(current_weather.lower(), {"default": 1.0})
    return weather_mods.get(item_type, weather_mods.get("default", 1.0))

def apply_weather_effects_to_player(player, weather: str, dt: float):
    """Apply weather effects directly to player"""
    import time
    if not hasattr(player, 'weather_effects'):
        player.weather_effects = {}
    
    # Clear old weather effects
    current_time = time.time()
    expired_effects = []
    for effect_name, effect_data in player.weather_effects.items():
        if current_time > effect_data.get('expires_at', 0):
            expired_effects.append(effect_name)
    
    for effect_name in expired_effects:
        del player.weather_effects[effect_name]
    
    # Apply current weather effects
    weather_effects = {
        "rain": {
            "stamina_drain_modifier": 1.15,  # Slightly more tiring
            "vision_reduction": 0.9
        },
        "storm": {
            "stamina_drain_modifier": 1.25,  # More exhausting
            "vision_reduction": 0.7,
            "distraction_chance": 0.002  # Lightning flashes may distract
        },
        "snow": {
            "movement_speed_modifier": 0.85,  # Slower movement
            "stamina_drain_modifier": 1.2,  # More tiring
            "visibility_reduction": 0.8
        },
        "fog": {
            "vision_reduction": 0.6,
            "navigation_difficulty": 1.5
        },
        # RARE WEATHER EFFECTS (NEW!)
        "tornado": {
            "movement_speed_modifier": 0.6,  # Very difficult to move
            "stamina_drain_modifier": 2.0,  # Extremely exhausting
            "damage_chance": 0.01,  # 1% chance per frame of taking damage
            "damage_amount": 5,  # 5 HP per hit from debris
            "knockback_chance": 0.005,  # 0.5% chance to be pushed
            "vision_reduction": 0.4  # Very poor visibility
        },
        "tsunami": {
            "movement_speed_modifier": 0.3,  # Nearly impossible to move
            "stamina_drain_modifier": 3.0,  # Fighting the water
            "damage_chance": 0.02,  # 2% chance per frame of drowning damage
            "damage_amount": 8,  # 8 HP per hit
            "vision_reduction": 0.3  # Terrible visibility underwater
        },
        "meteor_shower": {
            "damage_chance": 0.003,  # 0.3% chance per frame
            "damage_amount": 15,  # Meteors hit hard!
            "vision_reduction": 0.8  # Mostly clear but falling debris
        },
        "aurora": {
            "stamina_regen_modifier": 1.5,  # Magical energy boosts stamina
            "mana_regen_modifier": 2.0,  # Boosts mana regeneration
            "vision_bonus": 1.2  # Enhanced visibility
        },
        "blood_moon": {
            "damage_bonus": 1.25,  # 25% more damage dealt
            "enemy_spawn_rate": 2.0,  # Enemies spawn 2x more
            "enemy_aggression": 1.5,  # Enemies more aggressive
            "vision_reduction": 0.7  # Eerie red lighting
        }
    }
    
    if weather.lower() in weather_effects:
        effects = weather_effects[weather.lower()]
        
        # Apply movement speed reduction in snow
        if "movement_speed_modifier" in effects and weather.lower() == "snow":
            if not hasattr(player, '_base_movement_speed'):
                player._base_movement_speed = getattr(player, 'movement_speed', 5)
            player.movement_speed = player._base_movement_speed * effects["movement_speed_modifier"]
        
        # Weather warnings and atmospheric effects
        # Cold weather warning (no damage, just notification)
        if weather.lower() == "snow" and random.random() < 0.0002:
            if not player.has_cold_protection():
                return "The cold is biting! Consider finding shelter or warm clothing."
        
        # Storm lightning effects (visual/distraction, no damage)
        if "distraction_chance" in effects and random.random() < effects["distraction_chance"]:
            if not player.has_lightning_protection():
                # Visual flash is handled by graphics system - no message needed
                pass
        
        # RARE WEATHER DAMAGE EFFECTS (NEW!)
        if "damage_chance" in effects and random.random() < effects["damage_chance"]:
            damage = effects["damage_amount"]
            
            # Check for shelter/protection
            has_protection = False
            if weather.lower() == "tornado" and hasattr(player, 'in_building') and player.in_building:
                has_protection = True
            elif weather.lower() == "tsunami" and hasattr(player, 'z_position') and player.z_position > 100:
                has_protection = True  # High ground
            elif weather.lower() == "meteor_shower" and hasattr(player, 'in_building') and player.in_building:
                has_protection = True
            
            if not has_protection:
                # Apply damage
                player.health = max(0, getattr(player, 'health', 100) - damage)
                
                # Return appropriate message
                if weather.lower() == "tornado":
                    return f"⚠️ TORNADO! Flying debris hits you for {damage} damage! SEEK SHELTER!"
                elif weather.lower() == "tsunami":
                    return f"⚠️ TSUNAMI! The water crashes into you for {damage} damage! GET TO HIGH GROUND!"
                elif weather.lower() == "meteor_shower":
                    return f"⚠️ METEOR! A space rock strikes you for {damage} damage! FIND COVER!"
        
        # POSITIVE RARE WEATHER EFFECTS (NEW!)
        if weather.lower() == "aurora":
            if "stamina_regen_modifier" in effects:
                bonus_stamina = 0.05 * effects["stamina_regen_modifier"]
                player.stamina = min(player.max_stamina, player.stamina + bonus_stamina)
            if "mana_regen_modifier" in effects and hasattr(player, 'mana'):
                bonus_mana = 0.05 * effects["mana_regen_modifier"]
                player.mana = min(player.max_mana, player.mana + bonus_mana)
            if random.random() < 0.001:
                return "✨ The aurora's magical energy fills you with power!"
        
        if weather.lower() == "blood_moon":
            if random.random() < 0.0005:
                return "🌙 The blood moon enhances your combat prowess, but beware - enemies grow stronger too!"
    
    return None

def player_has_weather_protection(player, protection_type: str) -> bool:
    """Check if player has specific weather protection"""
    if not hasattr(player, 'equipment') or not hasattr(player.equipment, 'equipped'):
        return False
    
    for slot, item in player.equipment.equipped.items():
        if item and isinstance(item, str) and item in WEATHER_EQUIPMENT:
            item_data = WEATHER_EQUIPMENT[item]
            if protection_type in item_data.get('special', ''):
                return True
        elif item and isinstance(item, dict):
            special = item.get('special', '')
            if protection_type in special:
                return True
    
    return False

# Add methods to player for weather protection checks
def add_weather_protection_methods_to_player(player):
    """Add weather protection check methods to player object"""
    def has_cold_protection(self):
        return player_has_weather_protection(self, 'cold_protection')
    
    def has_rain_protection(self):
        return player_has_weather_protection(self, 'rain_protection')
    
    def has_lightning_protection(self):
        return player_has_weather_protection(self, 'lightning_safety')
    
    def has_storm_protection(self):
        return player_has_weather_protection(self, 'storm_light')
    
    # Bind methods to player object
    import types
    player.has_cold_protection = types.MethodType(has_cold_protection, player)
    player.has_rain_protection = types.MethodType(has_rain_protection, player) 
    player.has_lightning_protection = types.MethodType(has_lightning_protection, player)
    player.has_storm_protection = types.MethodType(has_storm_protection, player)