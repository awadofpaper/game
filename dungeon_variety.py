"""
Dungeon variety system - modifiers, mini-bosses, traps, secrets, and difficulty tiers
"""
import random
import pygame
from typing import Dict, List, Tuple, Optional
import math

# Dungeon modifiers
DUNGEON_MODIFIERS = {
    "cursed": {
        "name": "Cursed Dungeon",
        "description": "All enemies are elite with enhanced stats",
        "icon": "💀",
        "enemy_multiplier": 1.5,
        "all_elite": True,
        "loot_bonus": 1.3,
        "color": (180, 50, 180)
    },
    "speed_run": {
        "name": "Speed Run Challenge",
        "description": "Complete within 5 minutes for bonus loot",
        "icon": "⏱️",
        "time_limit": 300,  # 5 minutes in seconds
        "loot_bonus": 1.8,
        "bonus_xp": 1.5,
        "color": (255, 215, 0)
    },
    "darkness": {
        "name": "Shrouded in Darkness",
        "description": "Limited vision, enemies lurk in shadows",
        "icon": "🌑",
        "vision_radius": 150,  # Reduced vision in pixels
        "enemy_stealth": True,
        "loot_bonus": 1.4,
        "color": (50, 50, 100)
    },
    "infested": {
        "name": "Monster Infestation",
        "description": "Triple enemy count, overwhelming numbers",
        "icon": "🦗",
        "enemy_count_multiplier": 3.0,
        "loot_bonus": 1.5,
        "color": (150, 255, 100)
    },
    "treasure_hunt": {
        "name": "Treasure Hunter's Paradise",
        "description": "Reduced enemies, massive loot increase",
        "icon": "💎",
        "enemy_count_multiplier": 0.5,
        "loot_multiplier": 3.0,
        "secret_rooms": True,
        "color": (255, 200, 50)
    },
    "boss_rush": {
        "name": "Boss Rush",
        "description": "Multiple mini-bosses, no regular enemies",
        "icon": "👹",
        "mini_boss_count": 5,
        "no_regular_enemies": True,
        "loot_bonus": 2.0,
        "color": (255, 100, 100)
    },
    "trap_master": {
        "name": "Trap Master's Domain",
        "description": "Deadly traps everywhere, reduced enemies",
        "icon": "⚠️",
        "trap_density": 3.0,
        "enemy_count_multiplier": 0.6,
        "loot_bonus": 1.3,
        "color": (255, 150, 50)
    }
}

# Difficulty tiers
DIFFICULTY_TIERS = {
    "normal": {
        "name": "Normal",
        "description": "Standard dungeon difficulty",
        "icon": "⚔️",
        "enemy_health_mult": 1.0,
        "enemy_damage_mult": 1.0,
        "loot_quality_mult": 1.0,
        "xp_mult": 1.0,
        "color": (200, 200, 200)
    },
    "hard": {
        "name": "Hard",
        "description": "Tougher enemies, better rewards",
        "icon": "⚔️⚔️",
        "enemy_health_mult": 1.5,
        "enemy_damage_mult": 1.3,
        "loot_quality_mult": 1.4,
        "xp_mult": 1.5,
        "color": (255, 200, 100)
    },
    "nightmare": {
        "name": "Nightmare", 
        "description": "Extremely dangerous, great rewards",
        "icon": "💀⚔️",
        "enemy_health_mult": 2.0,
        "enemy_damage_mult": 1.6,
        "loot_quality_mult": 2.0,
        "xp_mult": 2.0,
        "elite_chance": 0.5,  # 50% elite enemies
        "color": (180, 50, 255)
    },
    "hell": {
        "name": "Hell",
        "description": "Only for the bravest, legendary rewards",
        "icon": "🔥💀🔥",
        "enemy_health_mult": 3.0,
        "enemy_damage_mult": 2.0,
        "loot_quality_mult": 3.0,
        "xp_mult": 3.0,
        "elite_chance": 0.8,  # 80% elite enemies
        "mini_boss_mult": 1.5,
        "color": (255, 50, 50)
    }
}

# Trap types
class DungeonTrap:
    """Base class for dungeon traps"""
    def __init__(self, x: int, y: int, trap_type: str):
        self.x = x
        self.y = y
        self.trap_type = trap_type
        self.activated = False
        self.cooldown = 0.0
        self.detection_radius = 32  # Pixels
        
        # Trap-specific properties
        self.properties = TRAP_TYPES.get(trap_type, {})
        self.damage = self.properties.get("damage", 20)
        self.cooldown_duration = self.properties.get("cooldown", 2.0)
        self.trigger_delay = self.properties.get("trigger_delay", 0.5)
        self.warning_time = 0.0
        self.is_warning = False
        
    def update(self, dt: float, player_x: float, player_y: float) -> bool:
        """Update trap state, returns True if trap should trigger"""
        if self.cooldown > 0:
            self.cooldown -= dt
            return False
        
        # Check if player is in range
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
        
        if distance <= self.detection_radius and not self.activated:
            if not self.is_warning:
                self.is_warning = True
                self.warning_time = self.trigger_delay
            else:
                self.warning_time -= dt
                if self.warning_time <= 0:
                    self.activated = True
                    self.cooldown = self.cooldown_duration
                    self.is_warning = False
                    return True
        elif distance > self.detection_radius:
            # Reset warning if player moves away
            self.is_warning = False
            self.warning_time = 0.0
            self.activated = False
            
        return False

TRAP_TYPES = {
    "spike_pit": {
        "name": "Spike Pit",
        "damage": 30,
        "cooldown": 3.0,
        "trigger_delay": 0.3,
        "visual": "spikes_up",
        "color": (120, 120, 120),
        "description": "Sharp spikes emerge from the floor"
    },
    "arrow_trap": {
        "name": "Arrow Trap",
        "damage": 25,
        "cooldown": 2.0,
        "trigger_delay": 0.5,
        "visual": "arrow_shot",
        "color": (180, 140, 100),
        "description": "Fires a volley of arrows"
    },
    "pressure_plate": {
        "name": "Pressure Plate",
        "damage": 40,
        "cooldown": 5.0,
        "trigger_delay": 0.2,
        "visual": "explosion",
        "color": (200, 50, 50),
        "description": "Triggers an explosive blast"
    },
    "poison_gas": {
        "name": "Poison Gas",
        "damage": 15,
        "cooldown": 1.0,
        "trigger_delay": 0.4,
        "visual": "gas_cloud",
        "color": (100, 255, 100),
        "description": "Releases toxic gas that damages over time"
    },
    "fire_geyser": {
        "name": "Fire Geyser",
        "damage": 50,
        "cooldown": 4.0,
        "trigger_delay": 0.6,
        "visual": "fire_burst",
        "color": (255, 150, 50),
        "description": "Erupts with intense flames"
    }
}

# Secret room types
class SecretRoom:
    """Secret room with treasure or challenges"""
    def __init__(self, x: int, y: int, width: int, height: int, room_type: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type
        self.discovered = False
        self.loot_spawned = False
        
        # Hidden wall location (entrance to secret)
        self.hidden_wall_x = x
        self.hidden_wall_y = y
        
        # Room type properties
        self.properties = SECRET_ROOM_TYPES.get(room_type, {})

SECRET_ROOM_TYPES = {
    "treasure_vault": {
        "name": "Treasure Vault",
        "loot_count": 8,
        "loot_quality": "epic",
        "enemies": 0,
        "description": "A hidden cache of valuable treasures"
    },
    "mini_boss_lair": {
        "name": "Mini-Boss Lair",
        "loot_count": 4,
        "loot_quality": "rare",
        "enemies": 1,
        "enemy_type": "elite",
        "description": "An elite guardian protects this chamber"
    },
    "ancient_library": {
        "name": "Ancient Library",
        "loot_count": 3,
        "loot_quality": "rare",
        "skill_book_chance": 0.5,
        "description": "Forgotten knowledge lies within"
    },
    "cursed_shrine": {
        "name": "Cursed Shrine",
        "loot_count": 5,
        "loot_quality": "rare",
        "curse_chance": 0.3,
        "buff_chance": 0.7,
        "description": "Risk and reward in equal measure"
    }
}

# Mini-boss types
class MiniBoss:
    """Elite enemy that spawns in side rooms"""
    def __init__(self, boss_type: str, x: int, y: int):
        self.boss_type = boss_type
        self.x = x
        self.y = y
        self.defeated = False
        self.properties = MINI_BOSS_TYPES.get(boss_type, {})
        
MINI_BOSS_TYPES = {
    "armored_champion": {
        "name": "Armored Champion",
        "health_mult": 3.0,
        "damage_mult": 1.5,
        "defense_mult": 2.0,
        "loot_bonus": 1.5,
        "abilities": ["shield_bash", "heavy_strike"],
        "color": (150, 150, 180)
    },
    "shadow_assassin": {
        "name": "Shadow Assassin",
        "health_mult": 2.0,
        "damage_mult": 2.0,
        "speed_mult": 1.8,
        "loot_bonus": 1.6,
        "abilities": ["stealth", "backstab", "poison_blade"],
        "color": (80, 80, 120)
    },
    "corrupt_mage": {
        "name": "Corrupt Mage",
        "health_mult": 1.8,
        "damage_mult": 2.5,
        "magic_mult": 3.0,
        "loot_bonus": 1.8,
        "abilities": ["fireball", "ice_lance", "lightning_bolt"],
        "color": (150, 100, 255)
    },
    "berserker_champion": {
        "name": "Berserker Champion",
        "health_mult": 3.5,
        "damage_mult": 2.0,
        "speed_mult": 1.3,
        "loot_bonus": 1.7,
        "abilities": ["rage", "cleave", "leap_attack"],
        "color": (255, 100, 100)
    }
}


class DungeonVarietySystem:
    """Manages dungeon modifiers, traps, secrets, and difficulty"""
    
    def __init__(self):
        self.active_modifier = None
        self.active_difficulty = "normal"
        self.traps = []
        self.secret_rooms = []
        self.mini_bosses = []
        self.speed_run_timer = None
        self.speed_run_active = False
        
    def roll_random_modifier(self, chance: float = 0.3) -> Optional[str]:
        """Roll for a random dungeon modifier"""
        if random.random() < chance:
            return random.choice(list(DUNGEON_MODIFIERS.keys()))
        return None
    
    def apply_modifier_to_dungeon(self, dungeon, modifier_id: str):
        """Apply modifier effects to a dungeon"""
        if modifier_id not in DUNGEON_MODIFIERS:
            return
        
        modifier = DUNGEON_MODIFIERS[modifier_id]
        dungeon.modifier = modifier_id
        dungeon.modifier_data = modifier
        
        # Apply enemy modifications
        if "enemy_multiplier" in modifier:
            for enemy in dungeon.enemies:
                enemy.max_health = int(enemy.max_health * modifier["enemy_multiplier"])
                enemy.health = enemy.max_health
                enemy.damage = int(enemy.damage * modifier["enemy_multiplier"])
        
        if modifier.get("all_elite"):
            for enemy in dungeon.enemies:
                enemy.is_elite = True
                enemy.elite_type = "cursed"
        
        if "enemy_count_multiplier" in modifier:
            # Adjust enemy count (will be applied during spawning)
            dungeon.enemy_count_modifier = modifier["enemy_count_multiplier"]
        
        # Speed run setup
        if "time_limit" in modifier:
            self.speed_run_active = True
            self.speed_run_timer = modifier["time_limit"]
        
        # Darkness modifier
        if "vision_radius" in modifier:
            dungeon.darkness_active = True
            dungeon.vision_radius = modifier["vision_radius"]
    
    def apply_difficulty_to_dungeon(self, dungeon, difficulty: str):
        """Apply difficulty tier to dungeon"""
        if difficulty not in DIFFICULTY_TIERS:
            return
        
        tier = DIFFICULTY_TIERS[difficulty]
        dungeon.difficulty = difficulty
        dungeon.difficulty_data = tier
        
        # Apply multipliers to all enemies
        for enemy in dungeon.enemies:
            enemy.max_health = int(enemy.max_health * tier["enemy_health_mult"])
            enemy.health = enemy.max_health
            enemy.damage = int(enemy.damage * tier["enemy_damage_mult"])
            
            # Elite chance
            if "elite_chance" in tier and not enemy.is_elite:
                if random.random() < tier["elite_chance"]:
                    enemy.is_elite = True
                    enemy.elite_type = "nightmare" if difficulty == "nightmare" else "hell"
    
    def spawn_traps_in_dungeon(self, dungeon, density: float = 1.0):
        """Spawn traps throughout the dungeon"""
        self.traps.clear()
        
        # Get floor tiles
        floor_tiles = [(x, y) for y in range(dungeon.height) 
                      for x in range(dungeon.width)
                      if dungeon.tilemap[y][x]["type"] == "floor"]
        
        # Calculate trap count based on dungeon size and density
        base_trap_count = int(len(floor_tiles) * 0.05)  # 5% of floor tiles
        trap_count = int(base_trap_count * density)
        
        # Spawn traps
        random.shuffle(floor_tiles)
        for i in range(min(trap_count, len(floor_tiles))):
            x, y = floor_tiles[i]
            trap_type = random.choice(list(TRAP_TYPES.keys()))
            trap = DungeonTrap(x * 16, y * 16, trap_type)
            self.traps.append(trap)
            
            # Mark tile as having a trap
            dungeon.tilemap[y][x]["trap"] = trap_type
    
    def spawn_secret_rooms(self, dungeon, count: int = 2):
        """Generate secret rooms in the dungeon"""
        self.secret_rooms.clear()
        
        if not hasattr(dungeon, 'rooms') or not dungeon.rooms:
            return  # Only works with room-based layouts
        
        # Pick random existing rooms to convert to secret rooms
        available_rooms = [r for r in dungeon.rooms if r != dungeon.rooms[0]]  # Skip first room (entrance)
        
        for i in range(min(count, len(available_rooms))):
            room = available_rooms[i]
            x, y, w, h = room
            
            room_type = random.choice(list(SECRET_ROOM_TYPES.keys()))
            secret = SecretRoom(x, y, w, h, room_type)
            self.secret_rooms.append(secret)
            
            # Hide one of the walls (create hidden entrance)
            wall_side = random.choice(["north", "south", "east", "west"])
            if wall_side == "north":
                secret.hidden_wall_x = x + w // 2
                secret.hidden_wall_y = y
            elif wall_side == "south":
                secret.hidden_wall_x = x + w // 2
                secret.hidden_wall_y = y + h - 1
            elif wall_side == "east":
                secret.hidden_wall_x = x + w - 1
                secret.hidden_wall_y = y + h // 2
            else:  # west
                secret.hidden_wall_x = x
                secret.hidden_wall_y = y + h // 2
            
            dungeon.tilemap[secret.hidden_wall_y][secret.hidden_wall_x]["secret"] = True
    
    def spawn_mini_bosses(self, dungeon, count: int = 2):
        """Spawn elite mini-bosses in side rooms"""
        self.mini_bosses.clear()
        
        if not hasattr(dungeon, 'rooms') or len(dungeon.rooms) < 3:
            return
        
        # Use side rooms for mini-bosses (not entrance or boss room)
        available_rooms = dungeon.rooms[1:-1]  # Skip first and last
        
        for i in range(min(count, len(available_rooms))):
            room = available_rooms[i]
            x, y, w, h = room
            
            # Center of room
            boss_x = (x + w // 2) * 16
            boss_y = (y + h // 2) * 16
            
            boss_type = random.choice(list(MINI_BOSS_TYPES.keys()))
            mini_boss = MiniBoss(boss_type, boss_x, boss_y)
            self.mini_bosses.append(mini_boss)
    
    def update_speed_run_timer(self, dt: float) -> Dict:
        """Update speed run timer and return status"""
        if not self.speed_run_active or self.speed_run_timer is None:
            return {"active": False}
        
        self.speed_run_timer -= dt
        
        if self.speed_run_timer <= 0:
            return {
                "active": True,
                "failed": True,
                "time_remaining": 0
            }
        
        return {
            "active": True,
            "failed": False,
            "time_remaining": self.speed_run_timer,
            "bonus_active": self.speed_run_timer > 0
        }
    
    def check_trap_triggers(self, player_x: float, player_y: float, dt: float) -> List[Dict]:
        """Check all traps for triggers, returns list of triggered traps"""
        triggered = []
        
        for trap in self.traps:
            if trap.update(dt, player_x, player_y):
                triggered.append({
                    "type": trap.trap_type,
                    "x": trap.x,
                    "y": trap.y,
                    "damage": trap.damage,
                    "properties": trap.properties
                })
        
        return triggered
    
    def check_secret_discovery(self, player_x: float, player_y: float, interaction_range: float = 32) -> Optional[SecretRoom]:
        """Check if player discovers a secret room"""
        for secret in self.secret_rooms:
            if secret.discovered:
                continue
            
            # Check distance to hidden wall
            wall_x = secret.hidden_wall_x * 16
            wall_y = secret.hidden_wall_y * 16
            distance = math.sqrt((player_x - wall_x)**2 + (player_y - wall_y)**2)
            
            if distance <= interaction_range:
                secret.discovered = True
                return secret
        
        return None


# Global instance
dungeon_variety_system = DungeonVarietySystem()


def get_dungeon_variety_system() -> DungeonVarietySystem:
    """Get the global dungeon variety system"""
    return dungeon_variety_system
