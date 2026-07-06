import pygame
import random
import time
import math
import loot
from equipment import WEAPON_VISUALS, EQUIPMENT_DATA, EQUIPMENT_RARITY
from equipment_renderer import EquipmentRenderer
from dropped_equipment import DroppedEquipment
from dropped_equipment import DroppedEquipment, DroppedDubloon, DroppedFiller,  DroppedConsumable
from collections import namedtuple
from logger_config import get_logger
from config import Config

# AI Behavior Tree System imports (top-level to avoid repeated imports in __init__)
from ai_behavior_trees import get_behavior_tree_factory
from ai_personality_system import Personality, EmotionalProfile, PersonalityTraits, BehaviorResult

logger = get_logger(__name__)

# Rarity font caching system for improved enemy UI performance
class RarityFontCache:
    def __init__(self):
        self.cache = {}  # Cache for pre-rendered rarity letter surfaces
        self.font = None  # Will be created when first needed
    
    def _ensure_font(self):
        """Ensure font is initialized (lazy loading)"""
        if self.font is None:
            self.font = pygame.font.SysFont(None, 20)
    
    def get_rarity_text(self, rarity):
        """Get cached rarity letter surface or create new one"""
        self._ensure_font()  # Make sure font is ready
        
        # Use first letter of rarity as cache key
        key = rarity[0].upper()
        
        if key not in self.cache:
            # Render new rarity text surface and cache it
            text_surface = self.font.render(key, True, (255, 255, 255))
            self.cache[key] = text_surface
        
        return self.cache[key]

# Collision result caching system for improved enemy pathfinding performance
class TileCollisionCache:
    def __init__(self):
        self.cache = {}  # Cache for collision results by tile coordinate
        self.walkable_types = {"grass", "sand", "rubble", "fiber", "ash", "wood", "puddle", "dirt", "snow"}  # Include all traversable terrain
        
    def is_walkable(self, tilemap, x, y):
        """Check if a tile coordinate is walkable with caching"""
        if x < 0 or y < 0 or y >= len(tilemap) or x >= len(tilemap[0]):
            return False
            
        cache_key = (x, y)
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        is_walkable = tilemap[y][x]["type"] in self.walkable_types
        self.cache[cache_key] = is_walkable
        return is_walkable
        
    def clear_cache(self):
        """Clear the cache when tilemap changes"""
        self.cache.clear()

# Global instances
tile_collision_cache = TileCollisionCache()

# Global rarity font cache instance
rarity_font_cache = RarityFontCache()

PACK_TYPES = ["wolf", "shadow_wolf", "goblin", "slime", "mud_slime", "golden_slime", "bat", "zombie"]
PACK_RADIUS_TILES = 20
PACK_MAX_SIZE = 5
PACK_COORDINATION_INTERVAL = 4.0  # seconds

class SplashParticle:
    def __init__(self, pos, color=(80, 120, 200)):
        self.pos = pos
        self.radius = 4
        self.max_radius = 16
        self.color = color
        self.life = 0.2  # seconds
        self.start_time = time.time()

    def update(self):
        elapsed = time.time() - self.start_time
        self.radius = 4 + (self.max_radius - 4) * (elapsed / self.life)
        return elapsed < self.life

    def draw(self, screen, offset, tilemap=None):
        if self.radius > 0:
            center = (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1]))
            pygame.draw.circle(screen, self.color, center, int(self.radius), 2)

class EnvironmentalHazard:
    """Boss arena environmental hazards"""
    def __init__(self, hazard_type, x, y, duration=5.0, damage=10):
        self.hazard_type = hazard_type  # "falling_rock", "poison_pool", "flame_wall"
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - 25, y - 25, 50, 50)
        self.duration = duration
        self.damage = damage
        self.start_time = time.time()
        self.alive = True
        self.last_damage_time = 0
        self.damage_interval = 0.5  # Damage every 0.5s
        
        # Visual properties
        if hazard_type == "falling_rock":
            self.color = (120, 100, 80)
            self.warn_duration = 1.0  # 1 second warning
            self.fall_y = y - 200  # Start above
        elif hazard_type == "poison_pool":
            self.color = (100, 200, 50)
            self.warn_duration = 0.5
        elif hazard_type == "flame_wall":
            self.color = (255, 100, 0)
            self.warn_duration = 0.5
        elif hazard_type == "stone_wall":
            self.color = (80, 80, 80)
            self.duration = 8.0  # Walls last longer
            self.warn_duration = 0.0
            self.rect = pygame.Rect(x - 15, y - 15, 30, 30)  # Smaller blocking walls
    
    def update(self, dt):
        """Update hazard"""
        elapsed = time.time() - self.start_time
        if elapsed > self.duration:
            self.alive = False
    
    def check_damage(self, player, companions=None):
        """Check if hazard damages entities"""
        elapsed = time.time() - self.start_time
        
        # Skip if still warning
        if elapsed < self.warn_duration:
            return
        
        # Check damage interval
        if time.time() - self.last_damage_time < self.damage_interval:
            return
        
        targets = [player]
        if companions:
            targets.extend(companions)
        
        for target in targets:
            if hasattr(target, 'rect') and self.rect.colliderect(target.rect):
                if hasattr(target, 'take_damage'):
                    target.take_damage(self.damage, source=self.hazard_type.replace('_', ' ').title())
                    self.last_damage_time = time.time()
    
    def blocks_movement(self):
        """Check if this hazard blocks movement"""
        return self.hazard_type == "stone_wall"
    
    def draw(self, screen, offset):
        """Draw hazard"""
        elapsed = time.time() - self.start_time
        pr = self.rect.move(-offset[0], -offset[1])
        
        # Warning phase
        if elapsed < self.warn_duration:
            # Pulsating warning indicator
            pulse = (math.sin(elapsed * 20) + 1) * 0.5
            warning_alpha = int(100 + pulse * 155)
            warning_surface = pygame.Surface((pr.width, pr.height), pygame.SRCALPHA)
            pygame.draw.rect(warning_surface, (255, 0, 0, warning_alpha), (0, 0, pr.width, pr.height))
            screen.blit(warning_surface, (pr.x, pr.y))
            return
        
        # Active hazard rendering
        if self.hazard_type == "falling_rock":
            # Rock falling animation
            fall_progress = min(1.0, (elapsed - self.warn_duration) / 0.3)
            current_y = self.fall_y + (self.y - self.fall_y) * fall_progress
            rock_rect = pygame.Rect(pr.x, int(current_y - offset[1]), pr.width, pr.height)
            pygame.draw.ellipse(screen, self.color, rock_rect)
            pygame.draw.ellipse(screen, (80, 60, 40), rock_rect, 3)
            
        elif self.hazard_type == "poison_pool":
            # Bubbling poison pool
            pulse = (math.sin(elapsed * 3) + 1) * 0.5
            pool_alpha = int(150 + pulse * 105)
            pool_surface = pygame.Surface((pr.width, pr.height), pygame.SRCALPHA)
            pygame.draw.ellipse(pool_surface, (*self.color, pool_alpha), (0, 0, pr.width, pr.height))
            screen.blit(pool_surface, (pr.x, pr.y))
            # Bubbles
            for i in range(3):
                bubble_x = pr.centerx + math.cos(elapsed * 2 + i * 2) * 15
                bubble_y = pr.centery + math.sin(elapsed * 2 + i * 2) * 15
                pygame.draw.circle(screen, (150, 255, 100), (int(bubble_x), int(bubble_y)), 3)
                
        elif self.hazard_type == "flame_wall":
            # Animated flames
            flame_height = pr.height + int(math.sin(elapsed * 5) * 10)
            flame_rect = pygame.Rect(pr.x, pr.y, pr.width, flame_height)
            # Multiple flame layers
            pygame.draw.rect(screen, (255, 50, 0, 200), flame_rect)
            pygame.draw.rect(screen, (255, 150, 0, 150), flame_rect.inflate(-10, -10))
            pygame.draw.rect(screen, (255, 255, 0, 100), flame_rect.inflate(-20, -20))
            
        elif self.hazard_type == "stone_wall":
            # Solid blocking wall
            pygame.draw.rect(screen, self.color, pr)
            pygame.draw.rect(screen, (120, 120, 120), pr, 3)
            # Stone texture lines
            pygame.draw.line(screen, (60, 60, 60), (pr.left, pr.centery), (pr.right, pr.centery), 2)
            pygame.draw.line(screen, (60, 60, 60), (pr.centerx, pr.top), (pr.centerx, pr.bottom), 2)

class AttackVisual:
    def __init__(self, visual_type, pos, direction, color, start_time, duration, extra=None):
        self.visual_type = visual_type  # e.g. "melee_arc", "projectile", "spell"
        self.pos = pos                  # (x, y) tuple (center)
        self.direction = direction      # angle in degrees or radians
        self.color = color              # (R, G, B)
        self.start_time = start_time    # time.time() when created
        self.duration = duration        # seconds to display
        self.extra = extra or {}        # dict for any extra info (e.g. projectile speed, spell radius)

# Add this near the top with your other constants

ENEMY_RARITIES = {
    "Common": {
        "description": "Standard enemies with no special traits.",
        "health_multiplier": 1.0,
        "damage_multiplier": 1.0,
        "loot_multiplier": 1.0,
        "spawn_rate": 0.5,  # 50% chance to spawn
        "color_modifier": (0, 0, 0)  # No color change
    },
    "Uncommon": {
        "description": "Enemies with slightly enhanced abilities.",
        "health_multiplier": 1.5,
        "damage_multiplier": 1.2,
        "loot_multiplier": 1,
        "spawn_rate": 0.2,  # 20% chance to spawn
        "color_modifier": (0, 50, 0)  # Slightly greenish tint
    },
    "Rare": {
        "description": "Powerful enemies with unique skills.",
        "health_multiplier": 2.0,
        "damage_multiplier": 1.5,
        "loot_multiplier": 1.0,
        "spawn_rate": 0.10,  # 10% chance to spawn
        "color_modifier": (0, 0, 80)  # Blue tint
    },
    "Epic": {
        "description": "Very strong enemies with significant bonuses.",
        "health_multiplier": 3.0,
        "damage_multiplier": 2.0,
        "loot_multiplier": 1.0,
        "spawn_rate": 0.03,  # 3% chance to spawn
        "color_modifier": (100, 0, 100)  # Purple tint
    },
    "Legendary": {
        "description": "The most powerful enemies with extraordinary abilities.",
        "health_multiplier": 5.0,
        "damage_multiplier": 3.0,
        "loot_multiplier": 1.0,
        "spawn_rate": 0.01,  # 1% chance to spawn
        "color_modifier": (180, 120, 0)  # Gold tint
    }
}

ENEMY_SPELLS = {
    "fireball": {
        "damage": 18,
        "element": "fire",
        "effect": "burn",
        "range": 200,
        "cooldown": 2.0,
    },
    "ice_shard": {
        "damage": 14,
        "element": "ice",
        "effect": "slow",
        "range": 180,
        "cooldown": 2.5,
    },
    "lightning": {
        "damage": 22,
        "element": "electric",
        "effect": "shock",
        "range": 220,
        "cooldown": 3.0,
    },
    "summon_skeleton": {
        "effect": "summon",
        "summon_type": "skeleton",
        "cooldown": 8.0,
    },
    "curse": {
        "effect": "curse",
        "damage": 0,
        "cooldown": 6.0,
    },
    "heal": {
        "effect": "heal",
        "amount": 20,
        "cooldown": 5.0,
    },
    "fire_ground": {
        "damage": 10,
        "element": "fire",
        "effect": "burn_area",
        "range": 100,
        "cooldown": 4.0,
    },
    "freeze": {
        "effect": "freeze",
        "damage": 0,
        "cooldown": 5.0,
    },
    "ice_shield": {
        "effect": "shield",
        "amount": 15,
        "cooldown": 8.0,
    },
    "storm_aoe": {
        "damage": 16,
        "element": "electric",
        "effect": "area_shock",
        "range": 120,
        "cooldown": 6.0,
    },
    "teleport": {
        "effect": "teleport",
        "cooldown": 10.0,
    },
    "fear": {
        "effect": "fear",
        "cooldown": 7.0,
    },
    "magic_beam": {
        "damage": 25,
        "element": "arcane",
        "effect": "beam",
        "range": 250,
        "cooldown": 5.0,
    },
    "magic_barrier": {
        "effect": "barrier",
        "amount": 20,
        "cooldown": 10.0,
    },
    "lifesteal": {
        "damage": 10,
        "effect": "lifesteal",
        "cooldown": 6.0,
    },
    "hex": {
        "effect": "hex",
        "cooldown": 8.0,
    },
    "heal": {
        "effect": "heal",
        "amount": 20,
        "cooldown": 5.0,
    },
    "root": {
        "effect": "root",
        "cooldown": 7.0,
    },
    "clone": {
        "effect": "clone",
        "cooldown": 12.0,
    },
    "confuse": {
        "effect": "confuse",
        "cooldown": 8.0,
    },
    "magic_sword": {
        "damage": 20,
        "element": "arcane",
        "effect": "slash",
        "cooldown": 4.0,
    },
    "protective_spell": {
        "effect": "protect",
        "amount": 15,
        "cooldown": 10.0,
    },
}



ENEMY_TYPES = {
    "slime": {
        "color": (100, 255, 100),
        "max_health": 120,  # Increased from 24 - now takes 2-3 hits with moderate equipment
        "damage": 18,       # Increased from 6 - more threatening to unarmored players
        "speed": 150,
        "xp_reward": 1,
        "perception_range": 3,  # tiles - simple organism with poor awareness
        "size": (20, 20),
        "stats": {"Strength": 4, "Stamina": 6, "Willpower": 2, "Luck": 1, "Agility": 2},
        "weapon": "body_slam",
        "dubloon_drop": {"chance": 0.4, "min": 1, "max": 2},
        "drops": {
            "slime_gel": {"chance": 0.3, "amount": [1, 2]}
        }
    },
    "mud_slime": {
        "color": (80, 120, 80),
        "max_health": 150,  # Increased from 28
        "damage": 22,       # Increased from 8
        "speed": 150,
        "xp_reward": 2,
        "perception_range": 3,  # tiles - simple organism
        "size": (32, 32),
        "stats": {"Strength": 6, "Stamina": 8, "Willpower": 3, "Luck": 1, "Agility": 1},
        "weapon": "body_slam",
        "dubloon_drop": {"chance": 0.5, "min": 1, "max": 3},
        "drops": {
            "slime_gel": {"chance": 0.4, "amount": [1, 3]}
        }
    },
    "golden_slime": {
        "color": (255, 215, 0),
        "max_health": 200,  # Increased from 40
        "damage": 28,       # Increased from 12
        "speed": 180,
        "xp_reward": 5,
        "perception_range": 4,  # tiles - rare variant, slightly more aware
        "size": (32, 32),
        "stats": {"Strength": 8, "Stamina": 10, "Willpower": 6, "Luck": 10, "Agility": 4},
        "weapon": "body_slam",
        "dubloon_drop": {"chance": 1.0, "min": 5, "max": 12},
        "equipment_drops": {
            "gold_ring": {"chance": 0.05}
        },
        "drops": {
            "slime_gel": {"chance": 0.8, "amount": [2, 5]}
        }
    },
    "wolf": {
        "color": (120, 120, 120),
        "max_health": 180,  # Increased from 32 - now a serious threat
        "damage": 25,       # Increased from 13
        "speed": 180,
        "xp_reward": 5,
        "perception_range": 8,  # tiles - excellent sense of smell and hearing
        "size": (24, 18),
        "stats": {"Strength": 10, "Stamina": 8, "Willpower": 4, "Luck": 2, "Agility": 7},
        "weapon": "bite",
        "dubloon_drop": {"chance": 0.5, "min": 2, "max": 4},
        "equipment_drops": {
            "leather_armor": {"chance": 0.12}
        },
        "drops": {
            "wolf_pelt": {"chance": 0.6, "amount": [1, 1]},
            "meat": {"chance": 0.4, "amount": [1, 2]}
        }
    },
    "shadow_wolf": {
        "color": (40, 40, 80),
        "max_health": 220,  # Increased from 36
        "damage": 30,       # Increased from 14
        "speed": 180,
        "xp_reward": 5,
        "perception_range": 8,  # tiles - supernatural hunter with enhanced senses
        "size": (36, 28),
        "stats": {"Strength": 12, "Stamina": 10, "Willpower": 8, "Luck": 4, "Agility": 9},
        "weapon": "bite",
        "dubloon_drop": {"chance": 0.7, "min": 3, "max": 6},
        "equipment_drops": {
            "shadow_cloak": {"chance": 0.08},
            "leather_armor": {"chance": 0.15}
        },
        "drops": {
            "shadow_essence": {"chance": 0.5, "amount": [1, 2]},
            "wolf_pelt": {"chance": 0.7, "amount": [1, 2]}
        }
    },
    "golem": {
        "color": (120, 120, 160),
        "max_health": 320,  # Increased from 60 - tank enemy
        "damage": 40,       # Increased from 18
        "speed": 150,
        "xp_reward": 8,
        "perception_range": 4,  # tiles - construct with limited sensory capabilities
        "size": (40, 40),
        "stats": {"Strength": 18, "Stamina": 20, "Willpower": 4, "Luck": 1, "Agility": 1},
        "weapon": "fist",
        "dubloon_drop": {"chance": 0.6, "min": 3, "max": 7},
        "equipment_drops": {
            "stone_hammer": {"chance": 0.15},
            "iron_helmet": {"chance": 0.10}
        },
        "drops": {
            "stone": {"chance": 0.8, "amount": [2, 4]},
            "iron_ore": {"chance": 0.3, "amount": [1, 2]}
        }
    },
    "crystal_golem": {
        "color": (180, 220, 255),
        "max_health": 450,  # Increased from 90 - elite enemy
        "damage": 55,       # Increased from 28
        "speed": 180,
        "xp_reward": 12,
        "perception_range": 4,  # tiles - construct, no true senses
        "size": (44, 44),
        "stats": {"Strength": 24, "Stamina": 25, "Willpower": 12, "Luck": 3, "Agility": 2},
        "weapon": "crystal_shard",
        "dubloon_drop": {"chance": 0.8, "min": 5, "max": 10},
        "equipment_drops": {
            "crystal_sword": {"chance": 0.20},
            "crystal_dagger": {"chance": 0.15},
            "plate_armor": {"chance": 0.10}
        },
        "drops": {
            "crystal": {"chance": 0.9, "amount": [2, 5]},
            "mana_crystal": {"chance": 0.4, "amount": [1, 2]}
        }
    },
    "caterpillar": {
        "color": (40, 120, 40),
        "max_health": 40,   # Increased from 8 - even weak enemies should survive a hit
        "damage": 8,        # Increased from 2
        "speed": 80,
        "xp_reward": .01,
        "perception_range": 2,  # tiles - tiny creature with minimal awareness
        "size": (18, 18),
        "stats": {"Strength": 2, "Stamina": 3, "Willpower": 1, "Luck": 1, "Agility": 3},
        "weapon": "bite",
        "dubloon_drop": {"chance": 0.2, "min": 1, "max": 1},
        "drops": {
            "fiber": {"chance": 0.5, "amount": [1, 2]}
        }
    },
    "goblin": {
        "color": (60, 180, 60),
        "max_health": 200,  # Increased from 38 - humanoid enemies are more durable
        "damage": 28,       # Increased from 11
        "speed": 150,
        "xp_reward": 15,
        "perception_range": 6,  # tiles - alert and intelligent
        "size": (24, 28),
        "stats": {"Strength": 8, "Stamina": 8, "Willpower": 4, "Luck": 3, "Agility": 5},
        "weapon": "spear",
        "dubloon_drop": {"chance": 0.6, "min": 1, "max": 4},
        "equipment_drops": {
            "rusty_sword": {"chance": 0.15},
            "wooden_shield": {"chance": 0.10}
        }
    },
    "orc": {
        "color": (80, 120, 40),
        "max_health": 300,  # Increased from 60 - strong warrior enemy
        "damage": 42,       # Increased from 18
        "speed": 180,
        "xp_reward": 18,
        "perception_range": 6,  # tiles - trained warrior, vigilant
        "size": (32, 38),
        "stats": {"Strength": 16, "Stamina": 14, "Willpower": 5, "Luck": 2, "Agility": 3},
        "weapon": "axe",
        "dubloon_drop": {"chance": 0.7, "min": 2, "max": 6},
        "equipment_drops": {
            "battleaxe": {"chance": 0.20},
            "leather_armor": {"chance": 0.15}
        }
    },
    "skeleton": {
        "color": (220, 220, 220),
        "max_health": 160,  # Increased from 35 - undead are resilient
        "damage": 32,       # Increased from 15
        "speed": 80,
        "xp_reward": 15,
        "perception_range": 5,  # tiles - undead but aware through magic
        "size": (20, 28),
        "stats": {"Strength": 8, "Stamina": 8, "Willpower": 6, "Luck": 2, "Agility": 4},
        "weapon": "mace",
        "dubloon_drop": {"chance": 0.5, "min": 2, "max": 5},
        "equipment_drops": {
            "bone_mace": {"chance": 0.15},
            "rusty_sword": {"chance": 0.12}
        },
        "drops": {
            "bone": {"chance": 0.8, "amount": [1, 3]}
        }
    },
    "bat": {
        "color": (70, 70, 120),
        "max_health": 80,   # Increased from 18 - fast, evasive enemy
        "damage": 15,       # Increased from 7
        "speed": 90,
        "xp_reward": 1,
        "perception_range": 8,  # tiles - echolocation grants excellent detection
        "size": (22, 10),
        "stats": {"Strength": 4, "Stamina": 4, "Willpower": 2, "Luck": 2, "Agility": 8},
        "weapon": "bite",
        "dubloon_drop": {"chance": 0.3, "min": 1, "max": 2},
        "drops": {
            "bat_wing": {"chance": 0.5, "amount": [1, 2]}
        }
    },
    "zombie": {
        "color": (80, 140, 80),
        "max_health": 280,  # Increased from 55 - zombies are tough
        "damage": 35,       # Increased from 15
        "speed": 100,
        "xp_reward": 10,
        "perception_range": 3,  # tiles - slow and dull senses
        "size": (28, 34),
        "stats": {"Strength": 12, "Stamina": 16, "Willpower": 3, "Luck": 1, "Agility": 1},
        "weapon": "bite",
        "dubloon_drop": {"chance": 0.4, "min": 1, "max": 4},
        "equipment_drops": {
            "rusty_sword": {"chance": 0.10},
            "leather_armor": {"chance": 0.08}
        },
        "drops": {
            "rotten_flesh": {"chance": 0.7, "amount": [1, 2]}
        }
    },
    "spider": {
        "color": (40, 40, 40),
        "max_health": 110,  # Increased from 22 - agile predator
        "damage": 20,       # Increased from 8
        "speed": 150,
        "xp_reward": 2,
        "perception_range": 7,  # tiles - sensitive to vibrations
        "size": (26, 16),
        "stats": {"Strength": 6, "Stamina": 5, "Willpower": 3, "Luck": 3, "Agility": 7},
        "weapon": "claws",
        "dubloon_drop": {"chance": 0.4, "min": 1, "max": 3},
        "drops": {
            "spider_silk": {"chance": 0.7, "amount": [1, 3]},
            "poison_gland": {"chance": 0.3, "amount": [1, 1]}
        }
    },
    "troll": {
        "color": (100, 70, 30),
        "max_health": 350,  # Reduced from 550 - still tough but not boss-tier
        "damage": 65,       # Increased from 26
        "speed": 100,
        "xp_reward": 20,
        "perception_range": 5,  # tiles - experienced hunter despite low intelligence
        "size": (44, 54),
        "stats": {"Strength": 28, "Stamina": 24, "Willpower": 8, "Luck": 2, "Agility": 1},
        "weapon": "club",
        "dubloon_drop": {"chance": 0.8, "min": 6, "max": 12},
        "equipment_drops": {
            "great_axe": {"chance": 0.22},
            "plate_armor": {"chance": 0.18},
            "iron_helmet": {"chance": 0.15}
        },
        "drops": {
            "troll_hide": {"chance": 0.8, "amount": [1, 2]},
            "meat": {"chance": 0.6, "amount": [2, 4]}
        }
    },
    "buried_zombie": {
        "color": (60, 100, 60),
        "max_health": 45,
        "damage": 16,
        "speed": 100,
        "xp_reward": 5,
        "perception_range": 3,  # tiles - detects footsteps when buried
        "size": (28, 34),
        "stats": {"Strength": 9, "Stamina": 11, "Willpower": 2, "Luck": 1, "Agility": 1},
        "weapon": "bite",
        "special": "emerges_when_player_steps",
        "dubloon_drop": {"chance": 0.3, "min": 1, "max": 3},
        "drops": {
            "rotten_flesh": {"chance": 0.5, "amount": [1, 1]},
            "bone": {"chance": 0.4, "amount": [1, 2]}
        }
    },
    "bandit_sword_shield": {
        "color": (160, 90, 60),
        "max_health": 40,
        "damage": 10,
        "speed": 150,
        "xp_reward": 8,
        "perception_range": 6,  # tiles - trained guards stay alert
        "size": (28, 34),
        "stats": {"Strength": 7, "Stamina": 5, "Willpower": 2, "Luck": 3, "Agility": 4},
        "weapon": "sword",
        "dubloon_drop": {"chance": 0.8, "min": 2, "max": 5},
        "equipment_drops": {
            "iron_sword": {"chance": 0.25},
            "iron_shield": {"chance": 0.20},
            "leather_armor": {"chance": 0.15}
        }
    },
    "bandit_dual_swords": {
        "color": (180, 70, 70),
        "max_health": 38,
        "damage": 14,
        "speed": 150,
        "xp_reward": 12,
        "perception_range": 6,  # tiles - agile fighter, vigilant
        "size": (28, 34),
        "stats": {"Strength": 8, "Stamina": 4, "Willpower": 2, "Luck": 3, "Agility": 6},
        "weapon": "dual_swords",
        "dubloon_drop": {"chance": 0.8, "min": 3, "max": 7},
        "equipment_drops": {
            "steel_sword": {"chance": 0.18},
            "crystal_dagger": {"chance": 0.12}
        }
    },
    "bandit_bow": {
        "color": (110, 90, 35),
        "max_health": 32,
        "damage": 12,
        "speed": 150,
        "xp_reward": 15,
        "perception_range": 9,  # tiles - archer needs excellent vision
        "size": (28, 34),
        "stats": {"Strength": 6, "Stamina": 4, "Willpower": 2, "Luck": 3, "Agility": 5},
        "weapon": "bow",
        "dubloon_drop": {"chance": 0.8, "min": 2, "max": 6},
        "equipment_drops": {
            "wooden_bow": {"chance": 0.25},
            "longbow": {"chance": 0.10}
        }
    },
    "necromancer": {
        "color": (70, 0, 70),
        "max_health": 52,
        "damage": 15,
        "speed": 180,
        "xp_reward": 20,
        "perception_range": 7,  # tiles - magical awareness of life force
        "size": (28, 36),
        "stats": {"Strength": 4, "Stamina": 5, "Willpower": 10, "Luck": 4, "Agility": 3},
        "weapon": "magic_staff",
        "magic": ["summon_skeleton", "curse"],
        "dubloon_drop": {"chance": 0.9, "min": 3, "max": 8},
        "equipment_drops": {
            "magic_staff": {"chance": 0.30},
            "mage_robes": {"chance": 0.25}
        }
    },
    "fire_elemental": {
        "color": (255, 80, 0),
        "max_health": 40,
        "damage": 17,
        "speed": 150,
        "xp_reward": 23,
        "perception_range": 6,  # tiles - senses heat and life energy
        "size": (22, 22),
        "stats": {"Strength": 7, "Stamina": 6, "Willpower": 8, "Luck": 2, "Agility": 4},
        "weapon": "fire_orb",
        "magic": ["fireball", "fire_ground"],
        "immune": ["fire"],
        "dubloon_drop": {"chance": 0.7, "min": 3, "max": 7},
        "equipment_drops": {
            "flame_staff": {"chance": 0.18},
            "fire_ring": {"chance": 0.12}
        },
        "drops": {
            "fire_essence": {"chance": 0.8, "amount": [1, 3]},
            "ash": {"chance": 0.5, "amount": [1, 2]}
        }
    },
    "frost_witch": {
        "color": (130, 210, 255),
        "max_health": 34,
        "damage": 13,
        "speed": 150,
        "xp_reward": 22,
        "perception_range": 7,  # tiles - magical senses
        "size": (26, 36),
        "stats": {"Strength": 3, "Stamina": 4, "Willpower": 11, "Luck": 4, "Agility": 3},
        "weapon": "ice_wand",
        "magic": ["ice_shard", "freeze", "ice_shield"],
        "dubloon_drop": {"chance": 0.8, "min": 2, "max": 7},
        "equipment_drops": {
            "ice_scepter": {"chance": 0.15},
            "mage_robes": {"chance": 0.20}
        }
    },
    "storm_mage": {
        "color": (180, 180, 255),
        "max_health": 28,
        "damage": 18,
        "speed": 150,
        "xp_reward": 23,
        "perception_range": 7,  # tiles - senses disturbances in the air
        "size": (26, 36),
        "stats": {"Strength": 3, "Stamina": 4, "Willpower": 12, "Luck": 4, "Agility": 4},
        "weapon": "lightning_rod",
        "magic": ["lightning", "storm_aoe"],
        "dubloon_drop": {"chance": 0.8, "min": 2, "max": 7},
        "equipment_drops": {
            "lightning_staff": {"chance": 0.20},
            "mage_robes": {"chance": 0.15}
        },
        "drops": {
            "storm_essence": {"chance": 0.7, "amount": [1, 2]}
        }
    },
    "shadow_phantom": {
        "color": (40, 0, 40),
        "max_health": 22,
        "damage": 15,
        "speed": 150,
        "xp_reward": 20,
        "perception_range": 7,  # tiles - supernatural awareness
        "size": (22, 28),
        "stats": {"Strength": 5, "Stamina": 3, "Willpower": 9, "Luck": 7, "Agility": 8},
        "weapon": "magic_staff",
        "magic": ["teleport", "fear"],
        "dubloon_drop": {"chance": 0.6, "min": 2, "max": 6},
        "equipment_drops": {
            "shadow_cloak": {"chance": 0.15},
            "shadow_dagger": {"chance": 0.12}
        },
        "drops": {
            "shadow_essence": {"chance": 0.8, "amount": [1, 3]}
        }
    },
    "arcane_golem": {
        "color": (180, 140, 240),
        "max_health": 85,
        "damage": 22,
        "speed": 100,
        "xp_reward": 30,
        "perception_range": 5,  # tiles - magically enhanced sensors
        "size": (36, 48),
        "stats": {"Strength": 15, "Stamina": 16, "Willpower": 10, "Luck": 2, "Agility": 1},
        "weapon": "magic_beam",
        "magic": ["magic_beam", "magic_barrier"],
        "dubloon_drop": {"chance": 0.7, "min": 4, "max": 9},
        "equipment_drops": {
            "magic_staff": {"chance": 0.18},
            "mage_robes": {"chance": 0.15}
        },
        "drops": {
            "arcane_essence": {"chance": 0.6, "amount": [1, 3]},
            "mana_crystal": {"chance": 0.5, "amount": [1, 2]}
        }
    },
    "warlock": {
        "color": (80, 0, 40),
        "max_health": 35,
        "damage": 13,
        "speed": 150,
        "xp_reward": 23,
        "perception_range": 7,  # tiles - dark magic grants keen awareness
        "size": (26, 36),
        "stats": {"Strength": 4, "Stamina": 4, "Willpower": 10, "Luck": 5, "Agility": 3},
        "weapon": "magic_staff",
        "magic": ["lifesteal", "hex"],
        "dubloon_drop": {"chance": 0.8, "min": 2, "max": 7},
        "equipment_drops": {
            "warlock_staff": {"chance": 0.20},
            "dark_robes": {"chance": 0.15}
        },
        "drops": {
            "dark_essence": {"chance": 0.7, "amount": [1, 2]},
            "soul_fragment": {"chance": 0.3, "amount": [1, 1]}
        }
    },
    "spirit_of_forest": {
        "color": (90, 200, 90),
        "max_health": 42,
        "damage": 11,
        "speed": 150,
        "xp_reward": 22,
        "perception_range": 6,  # tiles - senses disturbances in nature
        "size": (28, 32),
        "stats": {"Strength": 5, "Stamina": 7, "Willpower": 9, "Luck": 5, "Agility": 4},
        "weapon": "staff",
        "magic": ["heal", "root"],
        "dubloon_drop": {"chance": 0.6, "min": 2, "max": 5},
        "equipment_drops": {
            "nature_staff": {"chance": 0.15}
        },
        "drops": {
            "nature_essence": {"chance": 0.7, "amount": [1, 2]},
            "herb": {"chance": 0.6, "amount": [1, 3]}
        }
    },
    "illusionist": {
        "color": (170, 170, 255),
        "max_health": 23,
        "damage": 12,
        "speed": 180,
        "xp_reward": 20,
        "perception_range": 6,  # tiles - keen observer, trickster
        "size": (26, 32),
        "stats": {"Strength": 3, "Stamina": 3, "Willpower": 8, "Luck": 8, "Agility": 7},
        "weapon": "none",
        "magic": ["clone", "confuse"],
        "dubloon_drop": {"chance": 0.7, "min": 1, "max": 5}
    },
    "enchanted_knight": {
        "color": (100, 100, 255),
        "max_health": 65,
        "damage": 19,
        "speed": 150,
        "xp_reward": 28,
        "perception_range": 6,  # tiles - magically enhanced warrior
        "size": (32, 40),
        "stats": {"Strength": 12, "Stamina": 12, "Willpower": 7, "Luck": 3, "Agility": 3},
        "weapon": "magic_sword",
        "magic": ["magic_sword", "protective_spell"],
        "dubloon_drop": {"chance": 0.9, "min": 4, "max": 8},
        "equipment_drops": {
            "enchanted_blade": {"chance": 0.25},
            "plate_armor": {"chance": 0.20},
            "iron_helmet": {"chance": 0.15}
        }
    },
    # --- BOSS ENEMY TYPES ---
    "stone_titan": {
        "color": (120, 90, 60),
        "max_health": 3000,
        "damage": 60,
        "speed": 80,
        "xp_reward": 200,
        "perception_range": 15,  # tiles - boss-level awareness
        "size": (64, 64),
        "stats": {"Strength": 30, "Stamina": 35, "Willpower": 15, "Luck": 5, "Agility": 5},
        "weapon": "boulder_throw",
        "boss_type": "cave",
        "is_boss": True,
    },
    "lich_king": {
        "color": (80, 50, 120),
        "max_health": 2800,
        "damage": 55,
        "speed": 100,
        "xp_reward": 250,
        "perception_range": 15,  # tiles - powerful undead lord, senses all living things
        "size": (56, 72),
        "stats": {"Strength": 15, "Stamina": 25, "Willpower": 40, "Luck": 10, "Agility": 8},
        "weapon": "dark_magic",
        "boss_type": "crypt",
        "is_boss": True,
    },
}

ENEMY_TYPE_NAMES = [
    "slime",
    "mud_slime",
    "golden_slime",
    "wolf",
    "shadow_wolf",
    "golem",
    "crystal_golem",
    "caterpillar",
    "goblin",
    "orc",
    "skeleton",
    "bat",
    "zombie",
    "spider",
    "troll",
    "buried_zombie",
    "bandit_sword_shield",
    "bandit_dual_swords",
    "bandit_bow",
    "necromancer",
    "fire_elemental",
    "frost_witch",
    "storm_mage",
    "shadow_phantom",
    "arcane_golem",
    "warlock",
    "spirit_of_forest",
    "illusionist",
    "enchanted_knight"
]

# Boss-only enemy types (not spawned randomly)
BOSS_ENEMY_TYPES = [
    "stone_titan", "lich_king"
]

# AI Behavior Tree Integration
# Map enemy types to AI personalities for behavior tree system
from ai_personality_system import Personality

ENEMY_PERSONALITIES = {
    # Aggressive predators - direct attackers
    "wolf": (Personality.AGGRESSIVE, "melee"),
    "shadow_wolf": (Personality.BERSERKER, "melee"),  # More ferocious
    "bat": (Personality.AGGRESSIVE, "melee"),  # Fast, aggressive diver
    
    # Pack animals - tactical coordination
    "goblin": (Personality.COWARDLY, "melee"),  # Opportunistic, flee when alone
    "orc": (Personality.AGGRESSIVE, "melee"),
    "spider": (Personality.CAUTIOUS, "melee"),  # Patient ambush hunter
    
    # Undead - fearless and stubborn
    "zombie": (Personality.STUBBORN, "melee"),  # Relentless, never retreats
    "skeleton": (Personality.AGGRESSIVE, "melee"),
    "buried_zombie": (Personality.AGGRESSIVE, "melee"),
    
    # Magical enemies - tactical and cautious
    "necromancer": (Personality.TACTICAL, "ranged"),  # Commands minions
    "fire_elemental": (Personality.AGGRESSIVE, "ranged"),  # Relentless fire attacks
    "frost_witch": (Personality.CAUTIOUS, "ranged"),  # Maintains distance
    "storm_mage": (Personality.TACTICAL, "ranged"),
    "warlock": (Personality.TACTICAL, "ranged"),
    "illusionist": (Personality.ADAPTIVE, "ranged"),  # Changes tactics
    "shadow_phantom": (Personality.ADAPTIVE, "melee"),
    "spirit_of_forest": (Personality.PROTECTIVE, "ranged"),  # Defends nature
    
    # Bandits - varying tactics
    "bandit_sword_shield": (Personality.CAUTIOUS, "melee"),  # Defensive fighter
    "bandit_dual_swords": (Personality.AGGRESSIVE, "melee"),  # Reckless attacker
    "bandit_bow": (Personality.CAUTIOUS, "ranged"),  # Sniper
    
    # Golems and constructs - protective and stubborn
    "golem": (Personality.PROTECTIVE, "melee"),  # Guards territory
    "crystal_golem": (Personality.STUBBORN, "melee"),
    "arcane_golem": (Personality.TACTICAL, "ranged"),
    "enchanted_knight": (Personality.AGGRESSIVE, "melee"),  # Honorable warrior
    
    # Large creatures - stubborn or berserker
    "troll": (Personality.BERSERKER, "melee"),  # Goes into rage
    "caterpillar": (Personality.STUBBORN, "melee"),
    
    # Simple creatures - basic aggression or cowardly
    "slime": (Personality.STUBBORN, "melee"),  # Mindless approach
    "mud_slime": (Personality.STUBBORN, "melee"),
    "golden_slime": (Personality.COWARDLY, "melee"),  # Rare, tries to flee
    
    # Bosses - adaptive and tactical
    "stone_titan": (Personality.STUBBORN, "melee"),  # Unstoppable force
    "lich_king": (Personality.TACTICAL, "ranged"),  # Master strategist
}

def get_personality_for_enemy(enemy_type: str) -> tuple:
    """
    Get the personality and combat role for an enemy type.
    
    Args:
        enemy_type: The enemy type string (e.g., "wolf", "goblin")
    
    Returns:
        tuple: (Personality enum, combat_role string) or (Personality.AGGRESSIVE, "melee") as default
    """
    return ENEMY_PERSONALITIES.get(enemy_type, (Personality.AGGRESSIVE, "melee"))

__all__ = ["ENEMY_TYPE_NAMES", "BOSS_ENEMY_TYPES", "ENEMY_PERSONALITIES", "get_personality_for_enemy"]

def bfs_pathfind(tilemap, start, goal, walkable_types):
    from collections import deque
    width, height = len(tilemap[0]), len(tilemap)
    visited = set()
    queue = deque()
    queue.append((start, []))
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited and tilemap[ny][nx]["type"] in walkable_types:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return []  # No path found

def has_line_of_sight(tilemap, start_pos, end_pos, tilemap_offset=(0, 0)):
    """
    Check if there's a clear line of sight between two positions (no walls blocking).
    Uses Bresenham's line algorithm to check tiles along the line.
    
    Args:
        tilemap: The game tilemap (local array)
        start_pos: (x, y) pixel coordinates of start position
        end_pos: (x, y) pixel coordinates of end_pos
        tilemap_offset: (offset_x, offset_y) The world tile coordinates that map to tilemap[0][0]
    
    Returns:
        bool: True if line of sight is clear, False if blocked by walls/obstacles
    """
    TILE_SIZE = Config.TILE_SIZE
    # Only these types BLOCK line of sight (walls, obstacles, impassable terrain)
    blocking_types = {"rock_group", "tree", "wall"}
    
    offset_x, offset_y = tilemap_offset
    
    # Convert pixel positions to world tile coordinates
    x0_world = int(start_pos[0] // TILE_SIZE)
    y0_world = int(start_pos[1] // TILE_SIZE)
    x1_world = int(end_pos[0] // TILE_SIZE)
    y1_world = int(end_pos[1] // TILE_SIZE)
    
    # ALWAYS log for debugging
    # PERFORMANCE: Removed excessive LOS logging
    
    # Bresenham's line algorithm
    dx = abs(x1_world - x0_world)
    dy = abs(y1_world - y0_world)
    sx = 1 if x0_world < x1_world else -1
    sy = 1 if y0_world < y1_world else -1
    err = dx - dy
    
    x_world, y_world = x0_world, y0_world
    
    steps = 0
    while True:
        steps += 1
        if steps > 1000:
            logger.error(f"[LOS] INFINITE LOOP DETECTED! start=({x0_world},{y0_world}), end=({x1_world},{y1_world})")
            return False
            
        # Convert world coordinates to local tilemap indices
        x_local = x_world - offset_x
        y_local = y_world - offset_y
        
        # Check bounds in local tilemap
        if 0 <= x_local < len(tilemap[0]) and 0 <= y_local < len(tilemap):
            tile = tilemap[y_local][x_local]
            tile_type = tile.get("type", "grass")
            tile_ground = tile.get("ground", "")
            tile_object = tile.get("object", "")
            
            # Check if blocked
            if (tile_type in blocking_types or 
                tile_ground in blocking_types or 
                tile_object in blocking_types):
                logger.info(f"[LOS] BLOCKED at world ({x_world},{y_world}) local ({x_local},{y_local}): type={tile_type}, ground={tile_ground}, object={tile_object}")
                return False
        else:
            # Out of bounds = blocked
            logger.info(f"[LOS] OUT OF BOUNDS at world ({x_world},{y_world}) local ({x_local},{y_local}), tilemap_size={len(tilemap)}x{len(tilemap[0])}")
            return False
        
        # Reached the endpoint
        if x_world == x1_world and y_world == y1_world:
            # PERFORMANCE: Removed excessive LOS logging
            break
        
        # Calculate error and step
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x_world += sx
        if e2 < dx:
            err += dx
            y_world += sy
    
    # PERFORMANCE: Removed excessive LOS logging
    return True

def scale_enemy_stats(base_stats, player_level, hp_per_level=15, dmg_per_level=6, max_level=50):
    """
    Enhanced enemy scaling that provides more aggressive stat growth to keep enemies challenging.
    Uses exponential scaling for higher levels to match player power growth.
    """
    level = min(player_level, max_level)
    scaled_stats = base_stats.copy()
    
    # Non-linear scaling - increases more at higher levels
    level_modifier = (level - 1)
    exponential_modifier = 1 + (level_modifier * 0.08)  # 8% compound growth per level
    
    # Health scaling: base linear + exponential for higher levels
    base_hp_increase = hp_per_level * level_modifier
    exponential_hp_increase = base_stats['max_health'] * (exponential_modifier - 1)
    scaled_stats['max_health'] = int(base_stats['max_health'] + base_hp_increase + exponential_hp_increase)
    
    # Damage scaling: similar approach
    base_dmg_increase = dmg_per_level * level_modifier
    exponential_dmg_increase = base_stats['damage'] * (exponential_modifier - 1) * 0.6  # Slightly less aggressive than HP
    scaled_stats['damage'] = int(base_stats['damage'] + base_dmg_increase + exponential_dmg_increase)
    
    # Stat scaling: more aggressive to improve enemy performance
    if "stats" in base_stats:
        scaled_stats["stats"] = base_stats["stats"].copy()
        for stat in scaled_stats["stats"]:
            stat_increase = int(level_modifier * 0.5) + int(scaled_stats["stats"][stat] * (exponential_modifier - 1) * 0.3)
            scaled_stats["stats"][stat] += stat_increase
    
    return scaled_stats

# Set item definitions - items that grant bonuses when worn together
SET_ITEMS = {
    "guardian_set": {
        "name": "Guardian's Protection",
        "pieces": ["guardian_helmet", "guardian_armor", "guardian_shield"],
        "bonuses": {
            2: {"defense_bonus": 0.15, "description": "+15% Defense"},
            3: {"defense_bonus": 0.25, "health_bonus": 50, "description": "+25% Defense, +50 Health"}
        }
    },
    "shadow_set": {
        "name": "Shadow Walker", 
        "pieces": ["shadow_cloak", "shadow_boots", "shadow_dagger"],
        "bonuses": {
            2: {"speed_bonus": 0.20, "description": "+20% Movement Speed"},
            3: {"speed_bonus": 0.35, "crit_chance": 0.15, "description": "+35% Speed, +15% Crit"}
        }
    },
    "arcane_set": {
        "name": "Arcane Mastery",
        "pieces": ["arcane_staff", "arcane_robes", "arcane_amulet"], 
        "bonuses": {
            2: {"magic_damage": 0.20, "description": "+20% Magic Damage"},
            3: {"magic_damage": 0.35, "mana_bonus": 100, "description": "+35% Magic Damage, +100 Mana"}
        }
    }
}

def upgrade_rarity_for_streak(base_rarity):
    """Upgrade item rarity due to streak bonus"""
    rarity_order = ["common", "rare", "epic", "legendary"]
    try:
        current_index = rarity_order.index(base_rarity)
        if current_index < len(rarity_order) - 1:
            return rarity_order[current_index + 1]
    except ValueError:
        pass
    return base_rarity  # Return original if can't upgrade

def get_equipment_with_rarity_redistribution(equipment_id, base_chance, streak_rarity_bonus=False):
    """Convert a single equipment drop chance into rarity-distributed drops"""
    if random.random() > base_chance:
        return None  # No drop
    
    # Rarity distribution (keeping same total drop rate)
    rare_chance = base_chance * 0.15      # 15% of drops are rare
    epic_chance = base_chance * 0.05      # 5% of drops are epic  
    legendary_chance = base_chance * 0.02  # 2% of drops are legendary
    set_chance = base_chance * 0.08       # 8% of drops are set pieces
    
    rarity_roll = random.random()
    
    base_rarity = "common"
    if rarity_roll < legendary_chance:
        base_rarity = "legendary"
    elif rarity_roll < epic_chance:
        base_rarity = "epic"
    elif rarity_roll < rare_chance:
        base_rarity = "rare"
    elif rarity_roll < set_chance:
        # Choose random set piece of similar type
        item_type = equipment_id.split('_')[-1]  # Get type (sword, armor, etc)
        matching_sets = []
        for set_id, set_data in SET_ITEMS.items():
            for piece in set_data["pieces"]:
                if item_type in piece or piece.endswith(item_type):
                    matching_sets.append(piece)
        
        if matching_sets:
            set_piece = random.choice(matching_sets)
            return {"item": set_piece, "rarity": "set", "set_id": get_set_id_for_piece(set_piece)}
    
    # Apply streak rarity bonus if applicable
    if streak_rarity_bonus and base_rarity != "set":
        base_rarity = upgrade_rarity_for_streak(base_rarity)
    
    return {"item": equipment_id, "rarity": base_rarity}

def get_set_id_for_piece(piece_name):
    """Get the set ID for a given piece name"""
    for set_id, set_data in SET_ITEMS.items():
        if piece_name in set_data["pieces"]:
            return set_id
    return None

def handle_enemy_drops(enemy, player, messages, dropped_equipment_list):
    """Handle item and equipment drops when an enemy dies"""
    from enhanced_loot import get_enhanced_loot_system
    from dropped_equipment import DroppedEquipment
    
    loot_system = get_enhanced_loot_system()
    
    # Check if this is a boss with unique drops
    if hasattr(enemy, 'boss_type'):
        # Boss guaranteed unique drop
        guaranteed_drop = loot_system.get_boss_guaranteed_drop(enemy.boss_type)
        if guaranteed_drop:
            dropped_item = DroppedEquipment(
                guaranteed_drop["item"],
                enemy.rect.centerx,
                enemy.rect.centery
            )
            dropped_item.item_rarity = guaranteed_drop["rarity"]
            dropped_equipment_list.append(dropped_item)
            
            messages.add_message(f"💎 {guaranteed_drop['name']} (LEGENDARY)!")
            logger.info(f"[LOOT] Boss dropped unique: {guaranteed_drop['name']}")
        
        # Boss rare drops (chance-based)
        rare_drops = loot_system.get_boss_rare_drops(enemy.boss_type)
        for drop in rare_drops:
            dropped_item = DroppedEquipment(
                drop["item"],
                enemy.rect.centerx + random.randint(-20, 20),
                enemy.rect.centery + random.randint(-20, 20)
            )
            dropped_item.item_rarity = drop["rarity"]
            dropped_equipment_list.append(dropped_item)
            
            item_name = drop["item"].replace('_', ' ').title()
            messages.add_message(f"⭐ {item_name} ({drop['rarity'].upper()})!")
        
        # Bonus dubloons for bosses
        boss_gold = random.randint(200, 500)
        player.dubloons += boss_gold
        messages.add_message(f"Boss dropped {boss_gold} dubloons!")
        
        return  # Skip normal drops for bosses
    
    # Normal enemy drops (existing logic)
    enemy_data = ENEMY_TYPES[enemy.type]
    
    # Get rarity loot multiplier
    loot_multiplier = enemy.loot_multiplier  # From the enemy's rarity
    
    # Handle dubloon drops WITH rarity multiplier (keep this as is)
    if "dubloon_drop" in enemy_data:
        dubloon_data = enemy_data["dubloon_drop"]
        # Increase drop chance based on rarity
        chance = min(1.0, dubloon_data["chance"] * loot_multiplier)
        if random.random() < chance:
            # Increase amount based on rarity
            base_amount = random.randint(dubloon_data["min"], dubloon_data["max"])
            bonus_amount = int(base_amount * (loot_multiplier - 1))
            total_amount = base_amount + bonus_amount
            player.dubloons += total_amount
            messages.add_message(f"{enemy.rarity} enemy dropped {total_amount} dubloons!")
    
    # Handle equipment drops WITH rarity redistribution
    if "equipment_drops" in enemy_data:
        equipment_drops = enemy_data["equipment_drops"]
        
        # Check if streak bonuses are due
        streak_rarity_bonus = hasattr(player, 'total_kills') and (player.total_kills - getattr(player, 'last_rarity_bonus_at', 0)) >= 170
        bonus_roll_due = hasattr(player, 'total_kills') and (player.total_kills - getattr(player, 'last_bonus_roll_at', 0)) >= 230
        
        for equipment_id, drop_data in equipment_drops.items():
            # Use rarity redistribution system with streak bonus
            drop_result = get_equipment_with_rarity_redistribution(equipment_id, drop_data["chance"], streak_rarity_bonus)
            if drop_result:
                # Create enhanced dropped equipment with rarity
                dropped_item = DroppedEquipment(
                    drop_result["item"], 
                    enemy.rect.centerx - 8, 
                    enemy.rect.centery - 8
                )
                # Add rarity information for visual effects
                dropped_item.item_rarity = drop_result["rarity"]
                if "set_id" in drop_result:
                    dropped_item.set_id = drop_result["set_id"]
                
                dropped_equipment_list.append(dropped_item)
                
                # Enhanced message based on rarity
                item_name = EQUIPMENT_DATA.get(drop_result["item"], {}).get("name", drop_result["item"])
                rarity_text = drop_result["rarity"].upper()
                if drop_result["rarity"] == "set":
                    set_name = SET_ITEMS[drop_result["set_id"]]["name"]
                    messages.append((f"{enemy.rarity} enemy dropped {rarity_text} {item_name} ({set_name} Set)!", time.time()))
                else:
                    messages.append((f"{enemy.rarity} enemy dropped {rarity_text} {item_name}!", time.time()))
        
        # Handle bonus roll (extra drop) if due
        if bonus_roll_due and equipment_drops:
            bonus_equipment_id = random.choice(list(equipment_drops.keys()))
            bonus_drop_data = equipment_drops[bonus_equipment_id]
            bonus_result = get_equipment_with_rarity_redistribution(bonus_equipment_id, bonus_drop_data["chance"])
            
            if bonus_result:
                bonus_item = DroppedEquipment(
                    bonus_result["item"], 
                    enemy.rect.centerx + random.randint(-15, 15), 
                    enemy.rect.centery + random.randint(-15, 15)
                )
                bonus_item.item_rarity = bonus_result["rarity"]
                if "set_id" in bonus_result:
                    bonus_item.set_id = bonus_result["set_id"]
                
                dropped_equipment_list.append(bonus_item)
                
                bonus_item_name = EQUIPMENT_DATA.get(bonus_result["item"], {}).get("name", bonus_result["item"])
                bonus_rarity_text = bonus_result["rarity"].upper()
                messages.append((f"BONUS ROLL: {bonus_rarity_text} {bonus_item_name}!", time.time()))
    
    # Handle regular item drops WITHOUT rarity multiplier
    if "drops" in enemy_data:
        drops = enemy_data["drops"]
        for item, drop_data in drops.items():
            # Use base chance only, no multiplier
            chance = drop_data["chance"]
            if random.random() < chance:
                # Use base amount only, no bonus
                amount = random.randint(drop_data["amount"][0], drop_data["amount"][1])
                player.inventory[item] = player.inventory.get(item, 0) + amount
                messages.append((f"{enemy.rarity} enemy dropped {amount} {item}!", time.time()))
    
    # Special drops for Epic and Legendary enemies
    if enemy.rarity == "Epic" or enemy.rarity == "Legendary":
        # Add some extra gold for Epic+
        bonus_dubloons = 10 if enemy.rarity == "Epic" else 25
        player.dubloons += bonus_dubloons
        messages.append((f"{enemy.rarity} enemy dropped {bonus_dubloons} bonus dubloons!", time.time()))

def spawn_enemy(x, y, enemy_type=None, player_level=0, force_rarity=None):
    """
    Spawn an enemy with appropriate rarity
    
    Parameters:
    - x, y: Position to spawn at
    - enemy_type: Type of enemy (if None, random type will be selected)
    - player_level: Used to scale stats and influence rarity chances
    - force_rarity: Override random rarity selection (optional)
    
    Returns:
    - Enemy instance
    """
    # Determine enemy type if not specified
    if enemy_type is None:
        enemy_type = random.choice(ENEMY_TYPE_NAMES)
    
    # Determine rarity
    rarity = force_rarity or determine_enemy_rarity(player_level)
    
    # Create and return the enemy with the determined rarity
    return Enemy(enemy_type, x, y, player_level, rarity)

def spawn_boss(x, y, boss_type=None, player_level=1, dungeon_type="cave"):
    """
    Spawn a boss enemy appropriate for the dungeon type
    
    Parameters:
    - x, y: Position to spawn at
    - boss_type: Specific boss type (if None, choose based on dungeon_type)
    - player_level: Used to scale boss stats and abilities
    - dungeon_type: Type of dungeon ("cave", "crypt", "temple", "mine")
    
    Returns:
    - BossEnemy instance
    """
    # Determine boss type based on dungeon type if not specified
    if boss_type is None:
        boss_mapping = {
            "cave": "stone_titan",
            "crypt": "lich_king",
            "temple": "stone_titan",  # Fallback for now
            "mine": "stone_titan",    # Fallback for now
            "rooms": "lich_king",     # Room-style dungeons get lich king
        }
        boss_type = boss_mapping.get(dungeon_type, "stone_titan")
    
    # Ensure boss type exists
    if boss_type not in BOSS_ENEMY_TYPES:
        boss_type = "stone_titan"  # Default fallback
    
    # Create and return the boss enemy
    return BossEnemy(boss_type, x, y, player_level)

def determine_enemy_rarity(player_level=0):
    """Determine enemy rarity based on probabilities and player level"""
    # Adjust rates based on player level (higher levels = better chance for rare enemies)
    level_factor = min(0.5, player_level * 0.01)  # Caps at 50% boost at level 50
    
    rarities = []
    weights = []
    
    for rarity, data in ENEMY_RARITIES.items():
        rarities.append(rarity)
        
        # Increase rare+ spawn rates based on player level
        if rarity == "Common":
            weights.append(max(0.1, data["spawn_rate"] - level_factor))  # Decrease common with level
        else:
            # Distribute the reduced common chance among higher rarities
            weights.append(data["spawn_rate"] + (level_factor / 4))
            
    return random.choices(rarities, weights=weights)[0]

def get_scaled_equipment_stats(item_id, player_level):
    """
    Return equipment stats scaled by player level.
    Scaling increases base stats by a percentage per level.
    """
    if item_id not in EQUIPMENT_DATA:
        return {}
    item = EQUIPMENT_DATA[item_id].copy()
    scale_factor = 1.0 + (player_level - 1) * 0.05  # 5% per level above 1

    # Scale base_damage, magic_damage, defense, stat_bonuses
    for key in ["base_damage", "magic_damage", "defense"]:
        if key in item:
            item[key] = int(item[key] * scale_factor)
    if "stat_bonuses" in item:
        item["stat_bonuses"] = {stat: int(val * scale_factor) for stat, val in item["stat_bonuses"].items()}
    return item

class BossEnemy:
    """Base class for boss enemies with phase management and special abilities"""
    def __init__(self, boss_type, x, y, level):
        self.boss_type = boss_type
        self.level = level
        self.phase = 1
        self.max_phase = 4
        self.phase_transition_immunity = 0
        self.last_ability_time = 0
        self.ability_cooldown = 3.0  # Base cooldown between abilities
        self.minions = []
        self.arena_effects = []  # Environmental hazards
        self.enrage_timer = 300.0  # 5 minutes until enrage
        self.enraged = False
        self.start_time = time.time()
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        
        # Initialize as regular enemy first
        stats = scale_enemy_stats(ENEMY_TYPES[boss_type], level)
        self.type = boss_type
        self.rarity = "Boss"
        
        # Boss-specific stat multipliers
        boss_multiplier = 3.0 + (level * 0.1)  # Scale with level
        base_color = stats["color"]
        self.color = (
            min(255, int(base_color[0] * 1.2)),
            min(255, int(base_color[1] * 1.1)),
            min(255, int(base_color[2] * 1.3))
        )
        
        # Massively increased boss stats
        self.max_health = int(stats["max_health"] * boss_multiplier)
        self.health = self.max_health
        self.damage = stats["damage"] * 1.5
        self.speed = stats["speed"] * 0.8  # Slightly slower but more strategic
        self.xp_reward = stats["xp_reward"] * 10
        
        self.size = (stats["size"][0] * 2, stats["size"][1] * 2)  # Double size
        self.stats = stats.get("stats", {"Strength": 20, "Stamina": 25, "Willpower": 15, "Luck": 8, "Agility": 5})
        self.weapon = ENEMY_TYPES[boss_type].get("weapon", "none")
        self.rect = pygame.Rect(x, y, *self.size)
        self.alive = True
        
        # Standard enemy attributes for compatibility
        self.moving = False
        self.state = "aggro"  # Bosses always start aggressive
        self.aggro_radius = ENEMY_TYPES[boss_type].get("perception_range", 15)  # Boss perception range
        self.last_damage_time = 0
        self.combat_mode = True
        self.idle_target = None
        self.idle_timer = 0
        self.target_reached = False
        self.path = []
        self.tactical_target = None
        self.attack_visuals = []
        self.last_attack_time = 0
        self.attack_cooldown = 2.0
        
        # --- Detection optimization for bosses ---
        self.last_detection_check = 0  # Time of last detection check
        self.detection_cooldown = 0.15  # Only check every 0.15 seconds
        self.cached_detection_result = True  # Bosses always detect (aggro)
        self.last_state = "aggro"  # Track state changes
        
        # Boss-specific initialization
        self.initialize_boss_abilities()
        
        # Telegraph system for boss attacks
        self.telegraph_active = False
        self.telegraph_start_time = 0.0
        self.telegraph_duration = 2.0  # 2 seconds warning
        self.telegraph_ability = None
        self.telegraph_color = (255, 255, 0)  # Yellow warning
        self.last_telegraph_time = 0.0
        
    def initialize_boss_abilities(self):
        """Initialize boss-specific abilities based on type"""
        if self.boss_type == "stone_titan":
            self.abilities = {
                1: ["boulder_throw"],
                2: ["boulder_throw", "rock_wall", "ground_slam"],
                3: ["boulder_throw", "rock_wall", "ground_slam", "cave_in"],
                4: ["boulder_throw", "rock_wall", "ground_slam", "cave_in", "berserker_mode"]
            }
        elif self.boss_type == "lich_king":
            self.abilities = {
                1: ["dark_bolt"],
                2: ["dark_bolt", "skeleton_summon", "life_drain"],
                3: ["dark_bolt", "skeleton_summon", "life_drain", "bone_prison"],
                4: ["dark_bolt", "skeleton_summon", "life_drain", "bone_prison", "necromantic_explosion"]
            }
    
    def get_current_phase(self):
        """Calculate current phase based on health percentage"""
        health_percent = self.health / self.max_health
        if health_percent > 0.75:
            return 1
        elif health_percent > 0.50:
            return 2
        elif health_percent > 0.25:
            return 3
        else:
            return 4
    
    def check_phase_transition(self, all_enemies=None, message_console=None):
        """Check if boss should transition to new phase with dramatic effects"""
        new_phase = self.get_current_phase()
        if new_phase > self.phase:
            old_phase = self.phase
            self.phase = new_phase
            self.phase_transition_immunity = time.time() + 3.0  # 3 seconds of immunity
            
            # Screen shake effect
            self.screen_shake_intensity = 15
            self.screen_shake_duration = 1.5
            
            # Heal boss partially (20% max health)
            heal_amount = int(self.max_health * 0.2)
            self.health = min(self.max_health, self.health + heal_amount)
            
            if message_console:
                message_console.add_message(f"⚠ {self.type.replace('_', ' ').title()} enters Phase {self.phase}! ⚠")
                message_console.add_message(f"Boss heals for {heal_amount} HP!")
            
            # Spawn minions on phase transition
            if all_enemies and new_phase >= 2:
                minion_count = min(3, new_phase)  # More minions in later phases
                for i in range(minion_count):
                    angle = (2 * math.pi * i / minion_count)
                    spawn_distance = 150
                    minion_x = self.rect.centerx + int(math.cos(angle) * spawn_distance)
                    minion_y = self.rect.centery + int(math.sin(angle) * spawn_distance)
                    
                    try:
                        if self.boss_type == "stone_titan":
                            minion = Enemy("goblin", minion_x, minion_y, max(1, self.level - 5), "Uncommon")
                        elif self.boss_type == "lich_king":
                            minion = Enemy("skeleton", minion_x, minion_y, max(1, self.level - 5), "Uncommon")
                        else:
                            minion = Enemy("zombie", minion_x, minion_y, max(1, self.level - 5), "Common")
                        
                        self.minions.append(minion)
                        all_enemies.append(minion)
                        
                        if message_console and i == 0:
                            message_console.add_message(f"⚔ {minion_count} minions spawn to aid the boss!")
                    except Exception as e:
                        pass
            
            # Create arena hazards on phase transition
            self.spawn_phase_hazards(new_phase)
            
            return True
        return False
    
    def spawn_phase_hazards(self, phase):
        """Spawn environmental hazards when entering new phase"""
        hazard_count = phase * 2  # More hazards in later phases
        
        for i in range(hazard_count):
            # Random position around boss
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(100, 300)
            hazard_x = self.rect.centerx + int(math.cos(angle) * distance)
            hazard_y = self.rect.centery + int(math.sin(angle) * distance)
            
            # Choose hazard type based on boss
            if self.boss_type == "stone_titan":
                hazard_type = random.choice(["falling_rock", "stone_wall"])
                damage = int(self.damage * 0.8)
            elif self.boss_type == "lich_king":
                hazard_type = random.choice(["poison_pool", "flame_wall"])
                damage = int(self.damage * 0.6)
            else:
                hazard_type = random.choice(["falling_rock", "poison_pool", "flame_wall"])
                damage = int(self.damage * 0.7)
            
            hazard = EnvironmentalHazard(hazard_type, hazard_x, hazard_y, duration=8.0, damage=damage)
            self.arena_effects.append(hazard)
    
    def is_immune(self):
        """Check if boss is currently immune to damage"""
        return time.time() < self.phase_transition_immunity
    
    def use_boss_ability(self, player, all_enemies, tilemap, **kwargs):
        """Use a random boss ability from current phase with telegraph system"""
        # Check if currently telegraphing
        if self.telegraph_active:
            elapsed = time.time() - self.telegraph_start_time
            if elapsed >= self.telegraph_duration:
                # Telegraph complete, execute ability
                self.execute_ability(self.telegraph_ability, player, all_enemies, tilemap, **kwargs)
                self.telegraph_active = False
                self.telegraph_ability = None
                self.last_ability_time = time.time()
            return  # Wait for telegraph to complete
        
        if self.is_immune() or time.time() - self.last_ability_time < self.ability_cooldown:
            return
            
        current_abilities = self.abilities.get(self.phase, [])
        if not current_abilities:
            return
            
        ability = random.choice(current_abilities)
        
        # Start telegraph for major abilities
        major_abilities = ["boulder_throw", "ground_slam", "cave_in", 
                          "dark_bolt", "necromantic_explosion", "life_drain"]
        
        if ability in major_abilities:
            self.telegraph_active = True
            self.telegraph_start_time = time.time()
            self.telegraph_ability = ability
            self.last_telegraph_time = time.time()
            
            # Set telegraph color based on ability type
            if ability in ["boulder_throw", "ground_slam", "cave_in"]:
                self.telegraph_color = (200, 100, 50)  # Orange for physical
            elif ability in ["dark_bolt", "necromantic_explosion", "life_drain"]:
                self.telegraph_color = (150, 50, 255)  # Purple for magic
            
            # Add message to console
            message_console = kwargs.get("message_console")
            if message_console:
                ability_name = ability.replace("_", " ").title()
                message_console.add_message(f"{self.type.replace('_', ' ').title()} prepares {ability_name}!")
        else:
            # Execute minor abilities immediately
            self.execute_ability(ability, player, all_enemies, tilemap, **kwargs)
            self.last_ability_time = time.time()
    
    def execute_ability(self, ability, player, all_enemies, tilemap, **kwargs):
        """Execute specific boss ability"""
        if self.boss_type == "stone_titan":
            self.execute_stone_titan_ability(ability, player, all_enemies, tilemap, **kwargs)
        elif self.boss_type == "lich_king":
            self.execute_lich_king_ability(ability, player, all_enemies, tilemap, **kwargs)
    
    def execute_stone_titan_ability(self, ability, player, all_enemies, tilemap, **kwargs):
        """Execute Stone Titan specific abilities"""
        message_console = kwargs.get("message_console")
        companions = kwargs.get("companions", [])
        
        if ability == "boulder_throw":
            # High damage projectile attack
            damage = self.damage * 2.0
            if hasattr(player, "take_damage"):
                distance = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
                if distance < 300:  # Boulder range
                    player.take_damage(damage, source="Stone Titan Boulder")
                    if message_console:
                        message_console.add_message(f"Stone Titan hurls a massive boulder for {damage:.0f} damage!")
        
        elif ability == "ground_slam":
            # AOE attack around boss - damages player and companions
            slam_damage = self.damage * 1.5
            distance = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            if distance < 150:  # Close range AOE
                if hasattr(player, "take_damage"):
                    player.take_damage(slam_damage, source="Ground Slam")
                    if message_console:
                        message_console.add_message(f"Ground Slam hits for {slam_damage:.0f} damage!")
            
            # Also damage nearby companions
            for companion in companions:
                comp_dist = math.hypot(companion.rect.centerx - self.rect.centerx, companion.rect.centery - self.rect.centery)
                if comp_dist < 150:
                    companion.take_damage(slam_damage, source="Ground Slam")
            
            # Screen shake for ground slam
            self.screen_shake_intensity = 10
            self.screen_shake_duration = 0.5
        
        elif ability == "cave_in":
            # Spawn multiple falling rocks
            for i in range(3):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.randint(50, 250)
                rock_x = self.rect.centerx + int(math.cos(angle) * distance)
                rock_y = self.rect.centery + int(math.sin(angle) * distance)
                
                rock_damage = int(self.damage * 1.2)
                hazard = EnvironmentalHazard("falling_rock", rock_x, rock_y, duration=3.0, damage=rock_damage)
                self.arena_effects.append(hazard)
            
            if message_console:
                message_console.add_message("Rocks fall from the ceiling!")
        
        elif ability == "rock_wall":
            # Create stone walls to block player movement
            wall_count = 4
            for i in range(wall_count):
                # Create walls in a line between boss and player
                progress = (i + 1) / (wall_count + 1)
                wall_x = int(self.rect.centerx + (player.rect.centerx - self.rect.centerx) * progress)
                wall_y = int(self.rect.centery + (player.rect.centery - self.rect.centery) * progress)
                
                wall = EnvironmentalHazard("stone_wall", wall_x, wall_y, duration=8.0, damage=0)
                self.arena_effects.append(wall)
            
            if message_console:
                message_console.add_message("Stone walls rise from the ground!")
    
    def execute_lich_king_ability(self, ability, player, all_enemies, tilemap, **kwargs):
        """Execute Lich King specific abilities"""
        message_console = kwargs.get("message_console")
        companions = kwargs.get("companions", [])
        
        if ability == "dark_bolt":
            # Basic ranged magic attack
            damage = self.damage * 1.3
            distance = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            if distance < 400:  # Magic range
                if hasattr(player, "take_damage"):
                    player.take_damage(damage, source="Dark Bolt")
                    if message_console:
                        message_console.add_message(f"Dark magic strikes for {damage:.0f} damage!")
        
        elif ability == "skeleton_summon":
            # Summon skeleton minions OR revive dead enemies
            if all_enemies:
                # Try to revive dead enemies first (unique mechanic!)
                dead_enemies = [e for e in all_enemies if not e.alive and e.type in ["skeleton", "zombie", "ghoul"]]
                
                if dead_enemies and random.random() < 0.6:  # 60% chance to revive instead
                    # Revive up to 2 dead enemies
                    revive_count = min(2, len(dead_enemies))
                    for i in range(revive_count):
                        enemy = random.choice(dead_enemies)
                        enemy.alive = True
                        enemy.health = int(enemy.max_health * 0.5)  # Revive at 50% health
                        dead_enemies.remove(enemy)
                        
                        if message_console and i == 0:
                            message_console.add_message(f"⚰ Lich King revives {revive_count} fallen enemies!")
                
                elif len(self.minions) < 4:  # Max 4 minions
                    # Summon new skeleton
                    minion_x = self.rect.x + random.randint(-100, 100)
                    minion_y = self.rect.y + random.randint(-100, 100)
                    try:
                        minion = Enemy("skeleton", minion_x, minion_y, max(1, self.level - 5), "Common")
                        self.minions.append(minion)
                        all_enemies.append(minion)
                        if message_console:
                            message_console.add_message("Lich King summons a skeleton minion!")
                    except (ValueError, TypeError, AttributeError) as e:
                        pass  # Ignore summon failures
        
        elif ability == "life_drain":
            # Heal boss while damaging player and companions
            drain_damage = self.damage * 0.8
            targets = [player] + companions
            total_healed = 0
            
            for target in targets:
                distance = math.hypot(target.rect.centerx - self.rect.centerx, target.rect.centery - self.rect.centery)
                if distance < 350:  # Drain range
                    if hasattr(target, "take_damage"):
                        target.take_damage(drain_damage, source="Life Drain")
                        heal_amount = drain_damage * 0.5
                        total_healed += heal_amount
            
            if total_healed > 0:
                self.health = min(self.max_health, self.health + total_healed)
                if message_console:
                    message_console.add_message(f"Life Drain: Lich heals {total_healed:.0f} HP!")
        
        elif ability == "necromantic_explosion":
            # Powerful AOE attack with poison pools
            explosion_damage = self.damage * 2.5
            
            # Damage all nearby entities
            targets = [player] + companions
            for target in targets:
                distance = math.hypot(target.rect.centerx - self.rect.centerx, target.rect.centery - self.rect.centery)
                if distance < 250:  # Large AOE
                    if hasattr(target, "take_damage"):
                        target.take_damage(explosion_damage, source="Necromantic Explosion")
            
            # Create poison pools as aftermath
            for i in range(4):
                angle = (2 * math.pi * i / 4) + random.uniform(-0.3, 0.3)
                distance = random.randint(100, 200)
                pool_x = self.rect.centerx + int(math.cos(angle) * distance)
                pool_y = self.rect.centery + int(math.sin(angle) * distance)
                
                poison_damage = int(self.damage * 0.5)
                hazard = EnvironmentalHazard("poison_pool", pool_x, pool_y, duration=10.0, damage=poison_damage)
                self.arena_effects.append(hazard)
            
            if message_console:
                message_console.add_message(f"Necromantic Explosion creates poison pools!")
            
            # Screen shake
            self.screen_shake_intensity = 12
            self.screen_shake_duration = 0.7
    
    # Add all other Enemy methods to maintain compatibility
    def update(self, player, tilemap, message_console=None, dt=1/60, all_enemies=None, *args, **kwargs):
        """Boss-specific update logic with enrage mechanic"""
        TILE_SIZE = Config.TILE_SIZE
        
        # Check for enrage mechanic (after 5 minutes)
        combat_duration = time.time() - self.start_time
        if not self.enraged and combat_duration >= self.enrage_timer:
            self.enraged = True
            # Massive stat boost
            self.damage *= 1.5
            self.speed *= 1.3
            self.ability_cooldown *= 0.7  # Faster abilities
            
            # Visual effects
            self.screen_shake_intensity = 20
            self.screen_shake_duration = 2.0
            
            if message_console:
                message_console.add_message(f"⚠⚠ {self.type.replace('_', ' ').title()} ENRAGES! ⚠⚠")
                message_console.add_message("Boss damage +50%, Speed +30%, Abilities faster!")
            
            # Spawn extra hazards on enrage
            for i in range(6):
                angle = (2 * math.pi * i / 6)
                distance = random.randint(100, 250)
                hazard_x = self.rect.centerx + int(math.cos(angle) * distance)
                hazard_y = self.rect.centery + int(math.sin(angle) * distance)
                
                if self.boss_type == "stone_titan":
                    hazard_type = "falling_rock"
                elif self.boss_type == "lich_king":
                    hazard_type = "flame_wall"
                else:
                    hazard_type = random.choice(["falling_rock", "poison_pool", "flame_wall"])
                
                hazard = EnvironmentalHazard(hazard_type, hazard_x, hazard_y, duration=12.0, damage=int(self.damage))
                self.arena_effects.append(hazard)
        
        # Update screen shake
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= dt
            if self.screen_shake_duration <= 0:
                self.screen_shake_intensity = 0
        
        # Update environmental hazards
        companions = kwargs.get('companions', [])
        for hazard in self.arena_effects[:]:
            hazard.update(dt)
            if not hazard.alive:
                self.arena_effects.remove(hazard)
            else:
                hazard.check_damage(player, companions)
        
        # Check for phase transitions with enhanced effects
        if self.check_phase_transition(all_enemies, message_console):
            pass  # Message already shown in check_phase_transition
        
        # Use boss abilities
        self.use_boss_ability(player, all_enemies, tilemap, message_console=message_console, **kwargs)
        
        # Clean up dead minions
        self.minions = [m for m in self.minions if m.alive]
        
        # Basic movement towards player (bosses don't flee)
        # Check for stone walls blocking movement
        px, py = player.rect.centerx, player.rect.centery
        ex, ey = self.rect.centerx, self.rect.centery
        dist = ((px - ex) ** 2 + (py - ey) ** 2) ** 0.5
        
        if dist > 50:  # Move towards player if not in melee range
            move_x = (px - ex) / dist * self.speed * dt
            move_y = (py - ey) / dist * self.speed * dt
            
            new_x = self.rect.x + move_x
            new_y = self.rect.y + move_y
            
            # Simple collision check (also check stone walls)
            blocked = False
            new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
            for hazard in self.arena_effects:
                if hazard.blocks_movement() and new_rect.colliderect(hazard.rect):
                    blocked = True
                    break
            
            if not blocked:
                self.rect.x = max(0, min(new_x, len(tilemap[0]) * TILE_SIZE - self.rect.width))
                self.rect.y = max(0, min(new_y, len(tilemap) * TILE_SIZE - self.rect.height))
    
    def take_damage(self, amount, is_crit=False, *args, **kwargs):
        """Boss damage handling with phase immunity"""
        # Input validation
        if not isinstance(amount, (int, float)):
            logger.warning(f"Invalid damage amount type for boss: {type(amount)}. Expected number.")
            return
        if amount < 0:
            logger.warning(f"Negative damage amount for boss: {amount}. Clamping to 0.")
            amount = 0
        
        # Check for boss phase transition immunity
        if self.is_immune():
            floating_texts = kwargs.get("floating_texts")
            if floating_texts is not None:
                try:
                    from floating_text import FloatingText
                    floating_texts.append(FloatingText("IMMUNE!", (self.rect.centerx, self.rect.top - 20), color=(255, 255, 0)))
                except (ImportError, AttributeError) as e:
                    pass  # Floating text module not available
            return  # No damage taken during phase transition
        
        # Boss damage resistance (20% base resistance)
        resistance = 0.2
        amount = max(10, int(amount * (1 - resistance)))  # Minimum 10 damage
        
        # Apply damage
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            # Boss loot handled elsewhere
    
    def draw(self, screen, offset, player=None, current_weather=None, tilemap=None):
        """Draw boss enemy with enhanced visuals and environmental hazards"""
        # Draw environmental hazards first (under boss)
        for hazard in self.arena_effects:
            hazard.draw(screen, offset)
        
        pr = self.rect.move(-offset[0], -offset[1])
        
        # Enrage visual effect - red pulsating aura
        if self.enraged:
            enrage_pulse = (math.sin(time.time() * 8) + 1) * 0.5
            enrage_glow_size = int(15 + enrage_pulse * 10)
            enrage_alpha = int(150 + enrage_pulse * 105)
            
            enrage_surface = pygame.Surface((pr.width + enrage_glow_size*2, pr.height + enrage_glow_size*2), pygame.SRCALPHA)
            pygame.draw.rect(enrage_surface, (255, 0, 0, enrage_alpha), 
                            (0, 0, pr.width + enrage_glow_size*2, pr.height + enrage_glow_size*2), 0, 8)
            screen.blit(enrage_surface, (pr.x - enrage_glow_size, pr.y - enrage_glow_size))
            
            # Enrage text above boss
            enrage_font = pygame.font.SysFont(None, 22, bold=True)
            enrage_text = enrage_font.render("ENRAGED!", True, (255, 50, 50))
            enrage_shadow = enrage_font.render("ENRAGED!", True, (100, 0, 0))
            screen.blit(enrage_shadow, (pr.centerx - enrage_text.get_width()//2 + 2, pr.y - 57))
            screen.blit(enrage_text, (pr.centerx - enrage_text.get_width()//2, pr.y - 55))
        
        # Boss glow effect - pulsating aura
        pulse = (math.sin(time.time() * 3) + 1) * 0.5  # Slower pulse for bosses
        glow_alpha = int(100 + pulse * 155)
        glow_size = 10
        
        # Draw large glow
        glow_surface = pygame.Surface((pr.width + glow_size*2, pr.height + glow_size*2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*self.color, glow_alpha), 
                        (0, 0, pr.width + glow_size*2, pr.height + glow_size*2), 0, 6)
        screen.blit(glow_surface, (pr.x - glow_size, pr.y - glow_size))
        
        # Draw boss body
        pygame.draw.rect(screen, self.color, pr, border_radius=4)
        pygame.draw.rect(screen, (255, 255, 255), pr, 3, border_radius=4)  # White border
        
        # Draw equipped items on boss
        cx, cy = pr.center
        EquipmentRenderer.draw_equipment(screen, self, (cx, cy), entity_type="enemy")
        
        # Boss crown/icon
        crown_points = [
            (pr.centerx, pr.top - 10),
            (pr.centerx - 8, pr.top - 3),
            (pr.centerx - 5, pr.top),
            (pr.centerx, pr.top - 5),
            (pr.centerx + 5, pr.top),
            (pr.centerx + 8, pr.top - 3)
        ]
        pygame.draw.polygon(screen, (255, 215, 0), crown_points)
        pygame.draw.polygon(screen, (255, 255, 255), crown_points, 2)
        
        # Health bar (larger for bosses)
        hp_ratio = self.health / self.max_health
        bar_w = pr.width
        bar_h = 10
        
        # Health bar background
        pygame.draw.rect(screen, (60, 0, 0), (pr.x, pr.y - 20, bar_w, bar_h))
        
        # Health bar fill with gradient effect
        for i in range(int(bar_w * hp_ratio)):
            color_ratio = i / bar_w
            r = int(200 + (255 - 200) * color_ratio)
            g = int(0 + (50 - 0) * color_ratio)
            pygame.draw.rect(screen, (r, g, 0), (pr.x + i, pr.y - 20, 1, bar_h))
        
        # Health bar border
        pygame.draw.rect(screen, (255, 255, 255), (pr.x, pr.y - 20, bar_w, bar_h), 2)
        
        # Phase indicator
        phase_font = pygame.font.SysFont(None, 20)
        phase_text = phase_font.render(f"Phase {self.phase}", True, (255, 215, 0))
        screen.blit(phase_text, (pr.centerx - phase_text.get_width()//2, pr.y - 35))
        
        # Boss name
        name_font = pygame.font.SysFont(None, 24)
        
        # Draw telegraph warning if active
        if self.telegraph_active:
            elapsed = time.time() - self.telegraph_start_time
            progress = elapsed / self.telegraph_duration
            
            # Pulsating telegraph circle
            pulse_speed = 5.0
            pulse = (math.sin(time.time() * pulse_speed) + 1) * 0.5
            telegraph_radius = int(100 + pulse * 50)  # Expanding circle
            telegraph_alpha = int(100 + pulse * 100)
            
            # Draw telegraph indicator
            telegraph_surface = pygame.Surface((telegraph_radius * 2, telegraph_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(telegraph_surface, (*self.telegraph_color, telegraph_alpha),
                             (telegraph_radius, telegraph_radius), telegraph_radius, 5)
            screen.blit(telegraph_surface, (pr.centerx - telegraph_radius, pr.centery - telegraph_radius))
            
            # Draw progress arc
            arc_rect = pygame.Rect(pr.centerx - 60, pr.centery - 60, 120, 120)
            arc_angle = int(360 * progress)
            if arc_angle > 0:
                pygame.draw.arc(screen, (255, 0, 0), arc_rect, 0, math.radians(arc_angle), 8)
            
            # Warning text
            warning_font = pygame.font.SysFont(None, 28, bold=True)
            warning_text = warning_font.render("WARNING!", True, (255, 0, 0))
            warning_shadow = warning_font.render("WARNING!", True, (0, 0, 0))
            screen.blit(warning_shadow, (pr.centerx - warning_text.get_width()//2 + 2, pr.y - 52))
            screen.blit(warning_text, (pr.centerx - warning_text.get_width()//2, pr.y - 50))
        boss_name = self.type.replace('_', ' ').title()
        name_text = name_font.render(boss_name, True, (255, 255, 100))
        screen.blit(name_text, (pr.centerx - name_text.get_width()//2, pr.bottom + 5))

class Enemy:
    def __init__(self, etype, x, y, level, rarity="Common"):
        stats = scale_enemy_stats(ENEMY_TYPES[etype], level)
        self.type = etype
        self.rarity = rarity
        
        self.splash_particles = []
        
        # Apply rarity multipliers
        rarity_data = ENEMY_RARITIES[rarity]
        
        # Base color and apply rarity color modifier
        base_color = stats["color"]
        modifier = rarity_data["color_modifier"]
        self.color = (
            min(255, base_color[0] + modifier[0]),
            min(255, base_color[1] + modifier[1]),
            min(255, base_color[2] + modifier[2])
        )
        
        # Apply stat multipliers
        self.max_health = int(stats["max_health"] * rarity_data["health_multiplier"])
        self.health = self.max_health
        self.damage = stats["damage"] * rarity_data["damage_multiplier"]
        self.speed = stats["speed"]
        self.xp_reward = stats["xp_reward"] * rarity_data["loot_multiplier"]
        self.loot_multiplier = rarity_data["loot_multiplier"]
        
        self.size = stats.get("size", (24, 24))
        self.stats = stats.get("stats", {"Strength": 2, "Stamina": 2, "Willpower": 1, "Luck": 1, "Agility": 2})
        self.weapon = ENEMY_TYPES[etype].get("weapon", "none")
        self.magic = ENEMY_TYPES[etype].get("magic", [])
        self.spell_cooldowns = {spell: 0 for spell in self.magic}
        self.rect = pygame.Rect(x, y, *self.size)
        self.level = level
        self.alive = True
        self.last_attack_time = 0
        # --- NEW: Store active attack visuals (max 3 at a time) ---
        self.attack_visuals = []

        # --- AI State ---
        self.state = "idle"  # "idle", "alert", "aggro", or "flee"
        self.aggro_radius = ENEMY_TYPES[etype].get("perception_range", 4)  # tiles - varies by creature
        self.alert_radius = min(self.aggro_radius + 3, 12)  # tiles - investigation range (slightly beyond perception)
        self.idle_target = None
        self.idle_timer = 0
        
        # --- Search/Chase Behavior ---
        self.last_seen_position = None  # Track where player was last seen
        self.search_timer = 0  # How long to search before giving up
        self.chase_timeout = 8.0  # Seconds before giving up chase
        
        # --- Patrol System ---
        self.patrol_mode = random.choice(["wander", "patrol"])  # 50% chance of each
        self.patrol_points = []  # Will be set if patrol mode
        self.patrol_index = 0
        self.patrol_direction = 1  # 1 for forward, -1 for reverse
        
        # Generate patrol route if in patrol mode
        if self.patrol_mode == "patrol":
            # Create 3-5 patrol points in a rough circle or line
            num_points = random.randint(3, 5)
            patrol_radius = random.randint(4, 8)  # tiles
            for i in range(num_points):
                angle = (2 * math.pi * i / num_points) + random.uniform(-0.3, 0.3)
                px = int((x // 50) + patrol_radius * math.cos(angle))
                py = int((y // 50) + patrol_radius * math.sin(angle))
                self.patrol_points.append((px, py))

        # --- Pathfinding cache ---
        self.current_path = []
        self.last_player_tile = None
        self.last_enemy_tile = None

        # --- Detection optimization ---
        self.last_detection_check = 0  # Time of last detection check
        self.detection_cooldown = 0.15  # Only check every 0.15 seconds (not every frame!)
        self.cached_detection_result = False  # Cache the last detection result
        self.last_state = "idle"  # Track state changes for logging
        
        # --- Attack cooldown ---
        self.attack_cooldown = 0  # seconds
        self.last_attack_time = 0
        
        # Attack range varies by enemy size and type
        # Base range considers enemy size + reasonable melee reach
        base_size = max(self.size)
        self.attack_range = base_size + 50  # Enemy size plus ~1 tile reach (50-90 pixels typically)
        
        # Adjust for specific enemy types
        if etype in ["wolf", "shadow_wolf", "bat"]:
            # Fast agile enemies get extended lunge range
            self.attack_range = base_size + 60
        elif etype in ["spider"]:
            # Spiders have web/bite attacks with good reach
            self.attack_range = base_size + 70
        elif etype in ["troll", "golem", "crystal_golem"]:
            # Large enemies have massive reach
            self.attack_range = base_size + 40  # Already big, don't add too much
        elif etype in ["bandit_bow", "necromancer", "fire_elemental", "frost_witch", "storm_mage"]:
            # Ranged enemies have much longer attack range
            self.attack_range = 200  # ~4 tiles for ranged attacks
        
        self.attack_cooldown = 1.0  # seconds between attacks
        self.last_attack_time = 0
        
        # Attack telegraph system
        self.attack_telegraphing = False
        self.attack_telegraph_start_time = 0
        self.attack_telegraph_duration = 0.4  # 0.4 second warning (0.3-0.5 range)
        self.attack_telegraph_target = None  # Store telegraph target
        
        # Add visual indicators for rare+ enemies
        self.glow_effect = rarity != "Common"
        self.glow_color = self.color
        self.glow_size = 2 if rarity == "Uncommon" else 4 if rarity == "Rare" else 6 if rarity == "Epic" else 8
        
        self.last_tile_type = None  # Track last tile type for splash effect
        
        # --- Pack AI ---
        self.pack_id = None
        self.is_pack_leader = False
        self.pack_last_coordination = 0
        self.pack_tactic = None  # "focus", "surround", "synchronized"
        self.is_in_attack_position = False  # For synchronized attacks
        self.wait_for_pack = False  # Wait for other pack members
        
        # --- Smart flee AI ---
        self._call_for_help_on_flee = True
        self._cached_all_enemies = None  # Cache for all_enemies in update
        self._is_fake_fleeing = False  # Ambush tactic
        self._fake_flee_start_time = 0.0
        self._fake_flee_duration = 3.0  # seconds before ambush
        self._ambush_capable = etype in ["goblin", "orc", "bandit_sword_shield", "bandit_dual_swords"]
        
        # --- Threat Assessment ---
        self.current_target = None  # Can be player or companion
        self.target_priority = 0.0  # Higher = more threatening
        self.last_target_assessment = 0.0  # Time of last threat check
        self.prefer_casters = etype in ["necromancer", "fire_elemental", "frost_witch", "storm_mage", "warlock"]  # Ranged enemies prioritize spellcasters
        
        # --- AI BEHAVIOR TREE SYSTEM (Lazy Initialization) ---
        # Get personality and combat role for this enemy type
        personality, combat_role = get_personality_for_enemy(etype)
        self.personality = personality
        self.combat_role = combat_role
        
        # Behavior tree will be created on first use (lazy loading for performance)
        self.behavior_tree = None
        self._behavior_tree_initialized = False
        
        # Initialize emotional profile
        self.emotional_profile = EmotionalProfile()
        
        # Initialize personality traits based on personality type  
        self.personality_traits = self._create_personality_traits(personality)
        
        # AI behavior tree execution flag (can be disabled for performance if needed)
        self.use_behavior_tree = True
    
    def _create_personality_traits(self, personality):
        """Create personality traits based on personality type"""
        traits = PersonalityTraits()
        
        if personality == Personality.AGGRESSIVE:
            traits.aggression = 0.9
            traits.courage = 0.8
            traits.patience = 0.2
        elif personality == Personality.COWARDLY:
            traits.aggression = 0.3
            traits.courage = 0.2
            traits.caution = 0.9
        elif personality == Personality.TACTICAL:
            traits.intelligence = 0.8
            traits.patience = 0.7
            traits.caution = 0.6
        elif personality == Personality.BERSERKER:
            traits.aggression = 1.0
            traits.courage = 0.9
            traits.patience = 0.1
            traits.caution = 0.1
        elif personality == Personality.CAUTIOUS:
            traits.caution = 0.9
            traits.intelligence = 0.6
            traits.patience = 0.8
        elif personality == Personality.STUBBORN:
            traits.persistence = 0.9
            traits.courage = 0.7
            traits.adaptability = 0.2
        elif personality == Personality.ADAPTIVE:
            traits.intelligence = 0.8
            traits.adaptability = 0.9
            traits.patience = 0.6
        elif personality == Personality.PROTECTIVE:
            traits.loyalty = 0.9
            traits.courage = 0.7
            traits.caution = 0.5
        
        return traits
    
    def _ensure_behavior_tree(self):
        """Lazy initialize behavior tree on first use"""
        if not self._behavior_tree_initialized:
            behavior_tree_factory = get_behavior_tree_factory()
            self.behavior_tree = behavior_tree_factory.create_tree_for_enemy(
                self.type, self.personality, self.combat_role
            )
            self._behavior_tree_initialized = True
        

    def can_cast(self, spell_name):
        return time.time() >= self.spell_cooldowns.get(spell_name, 0)

    def set_spell_cooldown(self, spell_name, cooldown):
        self.spell_cooldowns[spell_name] = time.time() + cooldown
    
    def calculate_detection_range(self, player, tilemap):
        """
        Calculate effective detection range based on stealth, movement, line of sight, and distance.
        
        Returns:
            float: Effective detection range in tiles (can be reduced from base aggro_radius)
        """
        try:
            TILE_SIZE = Config.TILE_SIZE
            base_range = self.aggro_radius
            
            # Check if player is in stealth mode
            in_stealth = getattr(player, 'in_stealth_mode', False)
            
            if not in_stealth:
                # Not sneaking - full detection range
                return base_range
            
            # Player is sneaking - apply modifiers
            # Base stealth reduces detection by 50%
            stealth_modifier = 0.5
            
            # Movement penalty - check if player moved recently
            # If player has velocity or is_moving attribute, use it
            if hasattr(player, 'is_moving') and player.is_moving:
                # Moving while sneaking increases detection by 40%
                stealth_modifier += 0.4
            elif hasattr(player, 'vx') and hasattr(player, 'vy'):
                # Check velocity
                if abs(player.vx) > 1 or abs(player.vy) > 1:
                    stealth_modifier += 0.4
            
            # Player Agility bonus - higher agility = harder to detect
            player_agility = player.stats.get_stat('Agility') if hasattr(player, 'stats') else 0
            agility_bonus = player_agility * 0.02  # 2% per agility point
            stealth_modifier -= agility_bonus
            
            # Enemy Perception bonus - higher perception = better at spotting
            enemy_perception = self.stats.get('Willpower', 5)  # Use Willpower as perception
            perception_bonus = enemy_perception * 0.015  # 1.5% per perception point
            stealth_modifier += perception_bonus
            
            # Clamp modifier between 0.2 (minimum 20% detection) and 1.0 (full detection)
            stealth_modifier = max(0.2, min(1.0, stealth_modifier))
            
            # Apply stealth modifier to base range
            effective_range = base_range * stealth_modifier
            
            # Apply racial detection range modifiers (Elf -40%, Halfling -50%)
            if hasattr(player, 'trait_manager') and player.trait_manager:
                racial_modifier = player.trait_manager.get_detection_range_modifier()
                if racial_modifier != 1.0:
                    effective_range *= racial_modifier
                    # Debug logging (only log occasionally)
                    if random.random() < 0.01:  # 1% chance to log
                        logger.info(f"[RACIAL TRAIT] {self.type} detection: base={base_range}, stealth={stealth_modifier:.2f}, racial={racial_modifier:.2f}, final={effective_range:.1f}")
            
            # Debug logging (only log occasionally)
            if random.random() < 0.005:  # 0.5% chance to log
                logger.info(f"[STEALTH] {self.type}: base={base_range}, modifier={stealth_modifier:.2f}, effective={effective_range:.1f}, agility={player_agility}")
            
            return effective_range
        except Exception as e:
            logger.error(f"[DETECTION ERROR] {self.type} calculate_detection_range failed: {e}")
            # Fallback: return base range
            return self.aggro_radius
    
    def can_detect_player(self, player, tilemap, dist_tiles):
        """
        Check if enemy can detect the player based on distance, line of sight, and stealth.
        
        Args:
            player: Player object
            tilemap: Game tilemap
            dist_tiles: Distance to player in tiles
        
        Returns:
            bool: True if player is detected, False otherwise
        """
        # ONE-TIME DIAGNOSTIC: Check tilemap structure
        if not hasattr(self, '_tilemap_diagnostic_done'):
            self._tilemap_diagnostic_done = True
            if tilemap:
                # Check if it's a world object or array
                if hasattr(tilemap, 'get_tile'):
                    logger.warning(f"[TILEMAP DIAGNOSTIC] Using world object with get_tile() method")
                elif len(tilemap) > 0 and len(tilemap[0]) > 0:
                    sample_tile = tilemap[0][0]
                    logger.warning(f"[TILEMAP DIAGNOSTIC] Sample tile keys: {list(sample_tile.keys())}, values: {sample_tile}")
                else:
                    logger.error(f"[TILEMAP DIAGNOSTIC] Tilemap is empty or invalid! len={len(tilemap)}")
        
        try:
            # PERFORMANCE: Only do expensive checks periodically, not every frame!
            current_time = time.time()
            time_since_last_check = current_time - self.last_detection_check
            
            # If already in combat and recently checked, use cached result
            if self.state == "aggro" and time_since_last_check < self.detection_cooldown:
                return self.cached_detection_result
            
            # Time for a new detection check
            self.last_detection_check = current_time
            
            # Calculate effective detection range with stealth modifiers
            effective_range = self.calculate_detection_range(player, tilemap)
            
            # Check if player is within effective range
            if dist_tiles > effective_range:
                self.cached_detection_result = False
                return False
            
            # Check line of sight - can't detect through walls
            enemy_pos = (self.rect.centerx, self.rect.centery)
            player_pos = (player.rect.centerx, player.rect.centery)
            
            # Get tilemap offset if available
            tilemap_offset = getattr(self, 'tilemap_offset', (0, 0))
            has_los = has_line_of_sight(tilemap, enemy_pos, player_pos, tilemap_offset)
            if not has_los:
                self.cached_detection_result = False
                return False
            
            # Detection successful! Only log if this is a NEW detection
            if not self.cached_detection_result:
                logger.warning(f"[DETECT!!!] {self.type}: PLAYER DETECTED at {dist_tiles:.1f} tiles!")
            self.cached_detection_result = True
            return True
        except Exception as e:
            # If detection fails, log error and default to basic distance check
            logger.error(f"[DETECTION ERROR] {self.type} detection failed: {e}")
            # Fallback: basic distance check without stealth
            result = dist_tiles <= self.aggro_radius
            self.cached_detection_result = result
            return result
    
    def try_get_all_enemies(self):
        """Try to get all_enemies from cached value or return empty list"""
        return self._cached_all_enemies if self._cached_all_enemies else []
    
    def assess_threats(self, player, companions=None):
        """Assess and select the best target based on threat level"""
        # Only reassess every 2 seconds
        now = time.time()
        if now - self.last_target_assessment < 2.0 and self.current_target:
            return self.current_target
        
        self.last_target_assessment = now
        
        # Build list of potential targets
        targets = []
        
        # Add player
        player_dist = math.hypot(player.rect.centerx - self.rect.centerx,
                                 player.rect.centery - self.rect.centery)
        player_threat = 100.0  # Base threat
        
        # Increase threat based on distance (closer = more threatening)
        if player_dist < 100:
            player_threat += 50
        elif player_dist < 200:
            player_threat += 25
        
        # Increase threat if player is low health
        if hasattr(player, 'health') and hasattr(player, 'stats'):
            health_percent = player.health / player.stats.get_stat("Max_Health")
            if health_percent < 0.3:  # Low health targets are priority
                player_threat += 100
        
        # Ranged enemies prioritize casters (check if player has mana/spells)
        if self.prefer_casters:
            if hasattr(player, 'known_spells') and len(player.known_spells) > 0:
                player_threat += 75
        
        targets.append((player, player_threat, player_dist))
        
        # Add companions
        if companions:
            for companion in companions:
                if not companion.alive:
                    continue
                    
                comp_dist = math.hypot(companion.x - self.rect.centerx,
                                      companion.y - self.rect.centery)
                comp_threat = 50.0  # Base threat for companions
                
                # Closer companions are more threatening
                if comp_dist < 100:
                    comp_threat += 60
                elif comp_dist < 200:
                    comp_threat += 30
                
                # Low health companions are priority
                if hasattr(companion, 'health') and hasattr(companion, 'max_health'):
                    health_percent = companion.health / companion.max_health
                    if health_percent < 0.3:
                        comp_threat += 120  # Even higher priority than player
                
                # Companions doing more damage are more threatening
                if hasattr(companion, 'damage'):
                    comp_threat += companion.damage * 0.5
                
                targets.append((companion, comp_threat, comp_dist))
        
        # Select highest threat target
        if targets:
            best_target = max(targets, key=lambda t: t[1])
            self.current_target = best_target[0]
            self.target_priority = best_target[1]
            return self.current_target
        
        return player  # Default to player
    
    def call_for_help(self, all_enemies, radius=300):
        """Call for help - aggro nearby idle/alert enemies"""
        if not all_enemies:
            return
        
        help_count = 0
        for enemy in all_enemies:
            if enemy == self or not enemy.alive:
                continue
            
            dist = math.hypot(enemy.rect.centerx - self.rect.centerx,
                            enemy.rect.centery - self.rect.centery)
            
            if dist <= radius and enemy.state in ["idle", "alert"]:
                enemy.state = "aggro"
                help_count += 1
        
        return help_count
        
    def use_special_ability(self, player, all_enemies, tilemap, **kwargs):
        """Enhanced abilities for elite enemies to make them more challenging."""
        
        if self.rarity == "Rare":
            # Rare enemies get damage boost and speed increase
            if not hasattr(self, "ability_active"):
                self.ability_active = True
                self.damage = int(self.damage * 1.3)  # 30% damage boost
                self.speed = int(self.speed * 1.2)   # 20% speed boost
                
                # Visual effect for ability activation
                if len(self.attack_visuals) < 3:
                    self.attack_visuals.append(
                        AttackVisual(
                            visual_type="ability_aura",
                            pos=(self.rect.centerx, self.rect.centery),
                            direction=0,  # Direction not relevant for aura effect
                            color=(255, 100, 100),  # Red aura
                            start_time=time.time(),
                            duration=0.5
                        )
                    )
                    
        elif self.rarity == "Epic":
            # Epic enemies can call for reinforcements or heal nearby allies
            if all_enemies and random.choice([True, False]):
                # Heal nearby allies
                for ally in all_enemies:
                    if (ally != self and ally.alive and ally.type == self.type and
                        math.hypot(ally.rect.centerx - self.rect.centerx, 
                                 ally.rect.centery - self.rect.centery) <= 150):
                        heal_amount = int(ally.max_health * 0.25)
                        ally.health = min(ally.max_health, ally.health + heal_amount)
            else:
                # Temporary damage immunity (brief invincibility)
                self.damage_immunity_until = time.time() + 2.0
                
        elif self.rarity == "Legendary":
            # Legendary enemies get multiple abilities
            ability_choice = random.randint(1, 3)
            
            if ability_choice == 1:
                # Teleport near player for surprise attack
                angle = random.uniform(0, 2 * math.pi)
                teleport_distance = 80  # pixels
                new_x = player.rect.centerx + math.cos(angle) * teleport_distance
                new_y = player.rect.centery + math.sin(angle) * teleport_distance
                
                # Ensure teleport location is valid
                tile_x = int(new_x // 50)
                tile_y = int(new_y // 50)
                if (0 <= tile_x < len(tilemap[0]) and 0 <= tile_y < len(tilemap) and
                    tilemap[tile_y][tile_x]["type"] in {"grass", "sand", "rubble", "fiber", "ash", "wood"}):
                    self.rect.centerx = int(new_x)
                    self.rect.centery = int(new_y)
                    
            elif ability_choice == 2:
                # Area damage attack
                damage_radius = 100
                area_damage = int(self.damage * 0.7)
                distance_to_player = math.hypot(player.rect.centerx - self.rect.centerx,
                                              player.rect.centery - self.rect.centery)
                if distance_to_player <= damage_radius:
                    player.take_damage(area_damage, **kwargs)
                    
            else:
                # Summon ability - enhance nearby enemies
                for ally in all_enemies or []:
                    if (ally != self and ally.alive and
                        math.hypot(ally.rect.centerx - self.rect.centerx, 
                                 ally.rect.centery - self.rect.centery) <= 200):
                        if not hasattr(ally, "legendary_boost"):
                            ally.legendary_boost = time.time() + 10.0  # 10 second boost
                            ally.damage = int(ally.damage * 1.4)
                            ally.speed = int(ally.speed * 1.3)

    # ========== REFACTORED: Enemy.update() broken into focused methods ==========
    
    def _handle_boss_abilities(self, player, all_enemies, tilemap, kwargs):
        """Handle boss-specific abilities and phase transitions"""
        if not isinstance(self, BossEnemy):
            return
        
        # Check for phase transitions
        if self.check_phase_transition():
            message_console = kwargs.get("message_console")
            if message_console:
                message_console.add_message(f"{self.type.title()} enters phase {self.phase}!")
        
        # Use boss abilities
        self.use_boss_ability(player, all_enemies, tilemap, **kwargs)
        
        # Clean up dead minions
        self.minions = [m for m in self.minions if m.alive]
    
    def _handle_elite_abilities(self, player, all_enemies, tilemap, kwargs):
        """Handle elite enemy (Rare+) special abilities"""
        if isinstance(self, BossEnemy):
            return  # Skip if boss
        
        if self.rarity not in ["Rare", "Epic", "Legendary"]:
            return  # Skip if not elite
        
        now = time.time()
        if not hasattr(self, "last_special_ability"):
            self.last_special_ability = now
            return
        
        if now - self.last_special_ability > 8.0:
            self.use_special_ability(player, all_enemies, tilemap, **kwargs)
            self.last_special_ability = now
    
    def _handle_tactical_positioning(self, player, tilemap, dist_tiles):
        """Handle type-specific tactical positioning (flanking, blocking, distancing)"""
        TILE_SIZE = Config.TILE_SIZE
        
        if dist_tiles > 8:
            return  # Out of tactical range
        
        px, py = player.rect.centerx, player.rect.centery
        now = time.time()
        
        # Wolves try to flank the player
        if self.type in ["wolf", "shadow_wolf"]:
            if not hasattr(self, "flank_angle"):
                self.flank_angle = random.choice([math.pi/2, -math.pi/2, math.pi])
            
            flank_distance = 3  # tiles away
            target_x = px + math.cos(self.flank_angle) * flank_distance * TILE_SIZE
            target_y = py + math.sin(self.flank_angle) * flank_distance * TILE_SIZE
            self.tactical_target = (int(target_x // TILE_SIZE), int(target_y // TILE_SIZE))
        
        # Ranged enemies maintain distance
        elif self.type in ["goblin"] and hasattr(self, "magic") and self.magic:
            if dist_tiles < 4:  # Too close, back away
                ex, ey = self.rect.centerx, self.rect.centery
                away_x = ex + (ex - px) * 0.3
                away_y = ey + (ey - py) * 0.3
                self.tactical_target = (int(away_x // TILE_SIZE), int(away_y // TILE_SIZE))
        
        # Golems block player movement
        elif self.type in ["golem", "crystal_golem"]:
            if not hasattr(self, "block_position_timer") or now - self.block_position_timer > 3.0:
                walkable_types = {"grass", "sand", "rubble", "fiber", "ash", "wood", "dirt", "snow", "puddle"}
                for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]:
                    block_x = px + math.cos(angle) * 2 * TILE_SIZE
                    block_y = py + math.sin(angle) * 2 * TILE_SIZE
                    block_tile_x, block_tile_y = int(block_x // TILE_SIZE), int(block_y // TILE_SIZE)
                    if (0 <= block_tile_x < len(tilemap[0]) and 0 <= block_tile_y < len(tilemap) and
                        tilemap[block_tile_y][block_tile_x]["type"] in walkable_types):
                        self.tactical_target = (block_tile_x, block_tile_y)
                        break
                self.block_position_timer = now
    
    def _update_ai_state(self, player, tilemap, dist_tiles, dt):
        """Update AI state machine (idle -> alert -> aggro -> flee) with smart flee behavior"""
        TILE_SIZE = Config.TILE_SIZE
        walkable_types = {"grass", "sand", "rubble", "fiber", "ash", "wood", "dirt", "snow", "puddle"}
        
        # Flee if low health (25% or below)
        if self.health < self.max_health * 0.25 and self.state != "flee":
            self.state = "flee"
            
            # Call for help when starting to flee (one time)
            if self._call_for_help_on_flee:
                all_enemies = self.try_get_all_enemies()
                help_count = self.call_for_help(all_enemies, radius=300)
                if help_count > 0:
                    logger.info(f"[AI] {self.type} called for help, {help_count} enemies responded")
                self._call_for_help_on_flee = False  # Only call once per flee session
            
            # Ambush-capable enemies might fake flee (30% chance)
            if self._ambush_capable and not self._is_fake_fleeing and random.random() < 0.3:
                self._is_fake_fleeing = True
                self._fake_flee_start_time = time.time()
                logger.info(f"[AI] {self.type} is fake fleeing for ambush")
        
        if self.state == "flee":
            # Check for fake flee ambush
            if self._is_fake_fleeing:
                elapsed = time.time() - self._fake_flee_start_time
                if elapsed >= self._fake_flee_duration:
                    # Ambush! Return to combat
                    self.state = "aggro"
                    self._is_fake_fleeing = False
                    self.health = min(self.max_health, self.health + int(self.max_health * 0.2))  # Heal 20%
                    logger.info(f"[AI] {self.type} ambushed from fake flee!")
                    return
            
            # Smart flee behavior
            # Calculate direction away from player
            dx = self.rect.centerx - player.rect.centerx
            dy = self.rect.centery - player.rect.centery
            dist = math.hypot(dx, dy)
            
            # Option 1: Seek nearby allies (safety in numbers)
            all_enemies = self.try_get_all_enemies()
            nearest_ally = None
            nearest_ally_dist = float('inf')
            
            if all_enemies:
                for enemy in all_enemies:
                    if enemy != self and enemy.alive and enemy.type == self.type:
                        enemy_dist = math.hypot(enemy.rect.centerx - self.rect.centerx,
                                               enemy.rect.centery - self.rect.centery)
                        if enemy_dist < nearest_ally_dist and enemy_dist < TILE_SIZE * 8:
                            nearest_ally = enemy
                            nearest_ally_dist = enemy_dist
            
            # Option 2: Find cover (look for areas with more walls nearby)
            cover_target = None
            if random.random() < 0.3:  # 30% chance to seek cover
                best_cover_score = 0
                for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                    rad = math.radians(angle)
                    check_x = self.rect.centerx + math.cos(rad) * TILE_SIZE * 4
                    check_y = self.rect.centery + math.sin(rad) * TILE_SIZE * 4
                    tile_x = int(check_x // TILE_SIZE)
                    tile_y = int(check_y // TILE_SIZE)
                    
                    # Count walls nearby (cover score)
                    cover_score = 0
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            tx, ty = tile_x + dx, tile_y + dy
                            if (0 <= tx < len(tilemap[0]) and 0 <= ty < len(tilemap) and
                                tilemap[ty][tx]["type"] == "wall"):
                                cover_score += 1
                    
                    if cover_score > best_cover_score:
                        best_cover_score = cover_score
                        cover_target = (check_x, check_y)
            
            # Decide flee strategy
            if nearest_ally and nearest_ally_dist < TILE_SIZE * 5:
                # Move toward ally for safety
                target_x = nearest_ally.rect.centerx
                target_y = nearest_ally.rect.centery
                move_dx = target_x - self.rect.centerx
                move_dy = target_y - self.rect.centery
                move_dist = math.hypot(move_dx, move_dy)
                if move_dist > 0:
                    move_distance = min(self.speed * dt, move_dist)
                    move_x = int(round(move_distance * move_dx / move_dist))
                    move_y = int(round(move_distance * move_dy / move_dist))
                    self.try_move(tilemap, player, move_x, move_y)
            elif cover_target:
                # Move toward cover
                target_x, target_y = cover_target
                move_dx = target_x - self.rect.centerx
                move_dy = target_y - self.rect.centery
                move_dist = math.hypot(move_dx, move_dy)
                if move_dist > 0:
                    move_distance = min(self.speed * dt, move_dist)
                    move_x = int(round(move_distance * move_dx / move_dist))
                    move_y = int(round(move_distance * move_dy / move_dist))
                    self.try_move(tilemap, player, move_x, move_y)
            else:
                # Default: run directly away from player
                if dist > 0:
                    move_dist = min(self.speed * dt, dist)
                    move_x = int(round(move_dist * dx / dist))
                    move_y = int(round(move_dist * dy / dist))
                    self.try_move(tilemap, player, move_x, move_y)
            
            # Return to idle if safe distance reached
            if dist > TILE_SIZE * (self.aggro_radius + 3):
                self.state = "idle"
                self._call_for_help_on_flee = True  # Reset for next flee
            return  # Skip rest of update while fleeing
        
        # Check if player can be detected (considers stealth, line of sight, distance)
        player_detected = self.can_detect_player(player, tilemap, dist_tiles)
        
        # Only log state changes, not every frame!
        state_changed = (self.state != self.last_state)
        if state_changed:
            logger.info(f"[STATE CHANGE] {self.type}: {self.last_state} -> {self.state}, detected={player_detected}, dist={dist_tiles:.1f}")
            self.last_state = self.state
        
        # State transitions with improved chase/search behavior
        # AGGRO state transitions
        if self.state == "aggro":
            if player_detected:
                # Player still detected - maintain chase
                self.search_timer = self.chase_timeout  # Reset timer
                self.last_seen_position = (player.rect.centerx, player.rect.centery)
            elif dist_tiles <= self.alert_radius + 3:
                # Player escaped detection but still within extended search area
                self.state = "alert"
                logger.debug(f"[AI] {self.type} lost direct sight, entering search mode")
            else:
                # Player completely escaped - give up immediately if too far
                self.state = "idle"
                self.last_seen_position = None
                logger.debug(f"[AI] {self.type} lost player completely")
        
        # IDLE → ALERT/AGGRO transitions
        elif self.state == "idle":
            if player_detected:
                old_state = self.state
                self.state = "aggro"
                self.last_seen_position = (player.rect.centerx, player.rect.centery)
                self.search_timer = self.chase_timeout
                logger.warning(f"[STATE CHANGE!!!] {self.type} IDLE -> AGGRO at {dist_tiles:.1f} tiles")
            # Note: Removed automatic ALERT state on proximity - stealth should prevent detection entirely
        
        # ALERT state transitions and behavior
        elif self.state == "alert":
            # Decrease search timer
            self.search_timer -= dt
            
            if player_detected:
                # Found player again - aggressive!
                self.state = "aggro"
                self.last_seen_position = (player.rect.centerx, player.rect.centery)
                logger.debug(f"[AI] {self.type} re-acquired target")
            elif self.search_timer <= 0:
                # Gave up searching
                self.state = "idle"
                self.idle_target = None
                self.last_seen_position = None
                logger.debug(f"[AI] {self.type} gave up search")
            elif dist_tiles > self.alert_radius + 5:
                # Player got too far away - give up faster
                self.state = "idle"
                self.idle_target = None
                self.last_seen_position = None
        
        # Execute state behaviors
        if self.state == "idle":
            self._handle_idle_movement(tilemap, dt, walkable_types, player)
        
        elif self.state == "alert":
            # Search behavior - move to last seen position with pathfinding
            if self.last_seen_position:
                target_x, target_y = self.last_seen_position
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery
                dist = math.hypot(dx, dy)
                
                # Use pathfinding for alert state
                enemy_tile = (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)
                target_tile = (target_x // TILE_SIZE, target_y // TILE_SIZE)
                
                # Only recalculate path if target moved significantly
                if (not hasattr(self, 'alert_path') or not self.alert_path or 
                    not hasattr(self, 'alert_target_tile') or self.alert_target_tile != target_tile):
                    self.alert_path = bfs_pathfind(tilemap, enemy_tile, target_tile, walkable_types)
                    self.alert_target_tile = target_tile
                
                # Follow path
                if hasattr(self, 'alert_path') and self.alert_path:
                    next_x, next_y = self.alert_path[0]
                    path_target_x = next_x * TILE_SIZE + TILE_SIZE // 2
                    path_target_y = next_y * TILE_SIZE + TILE_SIZE // 2
                    dx = path_target_x - self.rect.centerx
                    dy = path_target_y - self.rect.centery
                    dist = math.hypot(dx, dy)
                    
                    if dist > 4:
                        move_dist = min(self.speed * 0.85 * dt, dist)  # 85% speed while searching
                        move_x = int(round(move_dist * dx / dist))
                        move_y = int(round(move_dist * dy / dist))
                        self.try_move(tilemap, player, move_x, move_y)
                    
                    # Check if reached waypoint
                    new_enemy_tile = (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)
                    if new_enemy_tile == (next_x, next_y):
                        self.alert_path.pop(0)
                elif dist > 4:
                    # Fallback: direct movement if pathfinding failed
                    move_dist = min(self.speed * 0.7 * dt, dist)
                    move_x = int(round(move_dist * dx / dist))
                    move_y = int(round(move_dist * dy / dist))
                    self.try_move(tilemap, player, move_x, move_y)
            else:
                # No last seen position in alert state - shouldn't happen, return to idle
                self.state = "idle"
                logger.debug(f"[AI] {self.type} in alert with no last seen position, returning to idle")
    
    def _handle_idle_movement(self, tilemap, dt, walkable_types, player):
        """Handle idle patrol/wander behavior"""
        TILE_SIZE = Config.TILE_SIZE
        
        if self.patrol_mode == "patrol" and self.patrol_points:
            if self.idle_target is None or self.idle_timer <= 0:
                self.idle_target = self.patrol_points[self.patrol_index]
                self.idle_timer = random.uniform(0.3, 0.8)
                
                if self.idle_target:
                    target_x = self.idle_target[0] * TILE_SIZE + TILE_SIZE // 2
                    target_y = self.idle_target[1] * TILE_SIZE + TILE_SIZE // 2
                    dist_to_target = math.hypot(target_x - self.rect.centerx, target_y - self.rect.centery)
                    if dist_to_target < TILE_SIZE:
                        self.patrol_index += self.patrol_direction
                        if self.patrol_index >= len(self.patrol_points):
                            self.patrol_index = len(self.patrol_points) - 2
                            self.patrol_direction = -1
                        elif self.patrol_index < 0:
                            self.patrol_index = 1
                            self.patrol_direction = 1
                        self.idle_target = None
        else:
            # Wander mode
            if self.idle_target is None or self.idle_timer <= 0:
                cx, cy = self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE
                candidates = []
                for dx in range(-5, 6):
                    for dy in range(-5, 6):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < len(tilemap[0]) and 0 <= ny < len(tilemap):
                            if tilemap[ny][nx]["type"] in walkable_types:
                                candidates.append((nx, ny))
                if candidates:
                    self.idle_target = random.choice(candidates)
                    self.idle_timer = random.uniform(0.5, 1.2)
                else:
                    self.idle_target = None
                    self.idle_timer = random.uniform(0.3, 0.8)
        
        if self.idle_target:
            target_x = self.idle_target[0] * TILE_SIZE + TILE_SIZE // 2
            target_y = self.idle_target[1] * TILE_SIZE + TILE_SIZE // 2
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 4:
                move_dist = min(self.speed * dt, dist)
                move_x = int(round(move_dist * dx / dist))
                move_y = int(round(move_dist * dy / dist))
                self.try_move(tilemap, player, move_x, move_y)
            else:
                self.idle_target = None
        
        self.idle_timer -= dt
    
    def _handle_aggro_movement(self, player, tilemap, all_enemies, dt):
        """Handle aggro state pathfinding and movement with synchronized attacks"""
        # Pause movement during attack telegraph
        if self.attack_telegraphing:
            return  # Don't move while telegraphing attack
        
        TILE_SIZE = Config.TILE_SIZE
        walkable_types = {"grass", "sand", "rubble", "fiber", "ash", "wood", "dirt", "snow", "puddle"}
        px, py = player.rect.centerx, player.rect.centery
        player_tile = (px // TILE_SIZE, py // TILE_SIZE)
        enemy_tile = (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)
        
        # Pack tactics with synchronized attacks
        if self.type in PACK_TYPES and hasattr(self, "pack_tactic") and self.pack_id is not None:
            pack_members = [e for e in all_enemies if e.pack_id == self.pack_id and e.alive]
            pack_members.sort(key=lambda e: id(e))
            
            if self.pack_tactic == "focus":
                target_tile = player_tile
            elif self.pack_tactic == "surround":
                idx = pack_members.index(self)
                angle = 2 * math.pi * idx / max(1, len(pack_members))
                radius = 2
                tx = player_tile[0] + int(round(radius * math.cos(angle)))
                ty = player_tile[1] + int(round(radius * math.sin(angle)))
                tx = max(0, min(tx, len(tilemap[0]) - 1))
                ty = max(0, min(ty, len(tilemap) - 1))
                target_tile = (tx, ty)
            elif self.pack_tactic == "synchronized":
                # Synchronized attack: wait for all pack members to be in position
                idx = pack_members.index(self)
                angle = 2 * math.pi * idx / max(1, len(pack_members))
                radius = 2
                tx = player_tile[0] + int(round(radius * math.cos(angle)))
                ty = player_tile[1] + int(round(radius * math.sin(angle)))
                tx = max(0, min(tx, len(tilemap[0]) - 1))
                ty = max(0, min(ty, len(tilemap) - 1))
                target_tile = (tx, ty)
                
                # Check if this enemy is in position (within 2 tiles of target)
                dist_to_target = abs(enemy_tile[0] - tx) + abs(enemy_tile[1] - ty)
                self.is_in_attack_position = dist_to_target <= 2
                
                # Check if all pack members are in position
                all_in_position = all(
                    getattr(member, 'is_in_attack_position', False) 
                    for member in pack_members
                )
                
                if not all_in_position:
                    # Wait for others
                    self.wait_for_pack = True
                    # Move to position but don't attack yet
                else:
                    # All ready, attack!
                    self.wait_for_pack = False
                    if hasattr(self, 'is_pack_leader') and self.is_pack_leader:
                        logger.info(f"[PACK] Synchronized attack initiated by {len(pack_members)} {self.type}s!")
            else:
                target_tile = player_tile
        else:
            # Use tactical target if available
            if hasattr(self, "tactical_target") and self.tactical_target:
                target_tile = self.tactical_target
            else:
                target_tile = player_tile
        
        # Pathfinding with caching
        tile_distance = abs(target_tile[0] - enemy_tile[0]) + abs(target_tile[1] - enemy_tile[1])
        if tile_distance <= 2:
            self.current_path = [target_tile]
        elif (self.last_player_tile != target_tile or
              self.last_enemy_tile != enemy_tile or
              not self.current_path):
            self.current_path = bfs_pathfind(tilemap, enemy_tile, target_tile, walkable_types)
            self.last_player_tile = target_tile
            self.last_enemy_tile = enemy_tile
        
        # Movement
        if self.current_path:
            next_x, next_y = self.current_path[0]
            target_x = next_x * TILE_SIZE + TILE_SIZE // 2
            target_y = next_y * TILE_SIZE + TILE_SIZE // 2
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            dist = math.hypot(dx, dy)
            
            speed = self.speed
            if 0 <= next_y < len(tilemap) and 0 <= next_x < len(tilemap[0]):
                tile_type = tilemap[next_y][next_x]["type"]
                if tile_type == "puddle":
                    speed *= 0.5
                    if self.last_tile_type != "puddle":
                        self.splash_particles.append(SplashParticle((self.rect.centerx, self.rect.centery)))
                self.last_tile_type = tile_type
            else:
                self.last_tile_type = "grass"
            
            if dist > 0:
                move_dist = min(speed * dt, dist)
                move_x = int(round(move_dist * dx / dist))
                move_y = int(round(move_dist * dy / dist))
                self.try_move(tilemap, player, move_x, move_y)
            
            new_enemy_tile = (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)
            if new_enemy_tile == (next_x, next_y):
                self.current_path.pop(0)
        
        # Clear snow tiles
        tile_x = self.rect.centerx // TILE_SIZE
        tile_y = self.rect.centery // TILE_SIZE
        if 0 <= tile_x < len(tilemap[0]) and 0 <= tile_y < len(tilemap):
            tile = tilemap[tile_y][tile_x]
            if tile["type"] == "snow":
                tile["type"] = "grass"
                tile["cleared"] = True
    
    def _handle_combat(self, player, all_enemies, dt, kwargs):
        """Handle combat: attack detection, damage calculation, visuals with threat assessment"""
        # Check if waiting for pack (synchronized attack)
        if hasattr(self, 'wait_for_pack') and self.wait_for_pack:
            return  # Don't attack yet, waiting for pack members
        
        # Threat assessment - select best target
        companions = kwargs.get('companions', [])
        target = self.assess_threats(player, companions)
        
        # Calculate distance to target
        if hasattr(target, 'rect'):
            target_x = target.rect.centerx
            target_y = target.rect.centery
        else:
            target_x = target.x
            target_y = target.y
        
        distance = math.hypot(self.rect.centerx - target_x, self.rect.centery - target_y)
        
        # Enhanced attack range
        enhanced_attack_range = self.attack_range
        if self.type in ["wolf", "shadow_wolf"]:
            enhanced_attack_range *= 1.3
        elif self.type == "spider":
            enhanced_attack_range *= 1.5
        
        # PERFORMANCE: Only log during actual attacks, not every frame
        if distance <= enhanced_attack_range:
            now = time.time()
            
            # Type-specific cooldowns
            base_cooldown = 1.0
            if self.type in ["wolf", "shadow_wolf", "spider"]:
                base_cooldown = 0.7
            elif self.type in ["troll", "golem", "crystal_golem"]:
                base_cooldown = 1.5
            elif self.rarity in ["Rare", "Epic", "Legendary"]:
                base_cooldown *= 0.8
            
            # Check if we're currently telegraphing an attack
            if self.attack_telegraphing:
                # Check if telegraph duration has elapsed
                if now - self.attack_telegraph_start_time >= self.attack_telegraph_duration:
                    # Telegraph complete - execute the attack!
                    self.attack_telegraphing = False
                    logger.warning(f"[ATTACK!!!] {self.type} attacking with damage {self.damage}")
                else:
                    # Still telegraphing, don't attack yet
                    return
            elif now - self.last_attack_time >= base_cooldown:
                # Start telegraph warning
                self.attack_telegraphing = True
                self.attack_telegraph_start_time = now
                self.attack_telegraph_target = target
                logger.info(f"[TELEGRAPH] {self.type} telegraphing attack...")
                return  # Don't attack this frame, wait for telegraph
                if hasattr(target, "take_damage"):
                    # Calculate critical hit chance
                    enemy_crit_chance = 0.05
                    if self.rarity == "Uncommon":
                        enemy_crit_chance = 0.08
                    elif self.rarity == "Rare":
                        enemy_crit_chance = 0.12
                    elif self.rarity in ["Epic", "Legendary"]:
                        enemy_crit_chance = 0.15
                    
                    # Pack coordination bonus
                    damage_bonus = 1.0
                    if hasattr(self, "pack_id") and self.pack_id is not None and all_enemies:
                        nearby_pack_members = [e for e in all_enemies 
                                             if e.pack_id == self.pack_id and e.alive and e != self
                                             and math.hypot(e.rect.centerx - self.rect.centerx,
                                                          e.rect.centery - self.rect.centery) <= 100]
                        if len(nearby_pack_members) > 0:
                            damage_bonus = 1.0 + (len(nearby_pack_members) * 0.15)
                    
                    # Synchronized attack bonus
                    if hasattr(self, 'pack_tactic') and self.pack_tactic == "synchronized":
                        damage_bonus *= 1.5  # 50% bonus for coordinated strikes!
                    
                    # Apply damage
                    is_crit = random.random() < enemy_crit_chance
                    final_damage = int(self.damage * damage_bonus)
                    if is_crit:
                        final_damage = int(final_damage * 1.5)
                    
                    logger.error(f"[DAMAGE!!!] {self.type} dealing {final_damage} damage to player!")
                    target.take_damage(final_damage, is_crit=is_crit, **kwargs)
                    
                    # Log target switch if attacking companion
                    if target != player:
                        target_name = getattr(target, 'name', 'companion')
                        logger.info(f"[THREAT] {self.type} switched target to {target_name}")
                
                self.last_attack_time = now
                self.attack_cooldown = base_cooldown
                
                # Spawn attack visual toward target
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery
                dy = player.rect.centery - self.rect.centery
                angle = math.atan2(dy, dx)
                arc_size = max(self.size) * 1.2
                
                if len(self.attack_visuals) < 3:
                    self.attack_visuals.append(
                        AttackVisual(
                            visual_type="melee_arc",
                            pos=(self.rect.centerx, self.rect.centery),
                            direction=angle,
                            color=self.color,
                            start_time=time.time(),
                            duration=0.15,
                            extra={"arc_size": arc_size, "arc_angle": math.radians(70)}
                        )
                    )

    def update(self, player, tilemap, message_console=None, dt=1/60, all_enemies=None, *args, **kwargs):
        """Orchestrates enemy AI update - calls focused helper methods"""
        TILE_SIZE = Config.TILE_SIZE
        px, py = player.rect.centerx, player.rect.centery
        ex, ey = self.rect.centerx, self.rect.centery
        dist_tiles = max(abs(px - ex), abs(py - ey)) // TILE_SIZE
        
        # Cache all_enemies for helper methods
        self._cached_all_enemies = all_enemies
        
        # === AI BEHAVIOR TREE EXECUTION ===
        if hasattr(self, 'use_behavior_tree') and self.use_behavior_tree:
            # Lazy initialize behavior tree on first use
            if hasattr(self, '_ensure_behavior_tree'):
                self._ensure_behavior_tree()
            
            if self.behavior_tree:
                # Update emotional profile
                if hasattr(self, 'emotional_profile'):
                    self.emotional_profile.update(dt)
                
                # Build context for behavior tree
                context = self._build_behavior_tree_context(player, tilemap, all_enemies, kwargs)
                
                # Execute behavior tree
                result = self.behavior_tree.execute(self, context)
                
                # If behavior tree successfully handled this frame, skip traditional AI
                if result == BehaviorResult.SUCCESS:
                    return  # Behavior tree handled everything
                # If behavior tree is running an action, let it continue
                elif result == BehaviorResult.RUNNING:
                    return
                # If behavior tree failed or returned pending, fall back to traditional AI
        
        # === TRADITIONAL AI (fallback or when behavior trees disabled) ===
        # Handle boss abilities
        self._handle_boss_abilities(player, all_enemies, tilemap, kwargs)
        
        # Handle elite abilities
        self._handle_elite_abilities(player, all_enemies, tilemap, kwargs)
        
        # Handle tactical positioning
        self._handle_tactical_positioning(player, tilemap, dist_tiles)
        
        # Pack coordination
        if self.type in PACK_TYPES and self.rarity == "Common":
            self.handle_pack_coordination(player, all_enemies, tilemap)
        
        # Update AI state machine (handles flee, idle, alert transitions)
        self._update_ai_state(player, tilemap, dist_tiles, dt)
        
        # Handle aggro state movement
        if self.state == "aggro":
            # PERFORMANCE: Removed excessive logging from every frame
            self._handle_aggro_movement(player, tilemap, all_enemies, dt)
            self._handle_combat(player, all_enemies, dt, kwargs)
    
    def _build_behavior_tree_context(self, player, tilemap, all_enemies, kwargs):
        """Build context dictionary for behavior tree execution"""
        context = {
            'player_pos': (player.rect.centerx, player.rect.centery),
            'player_health': player.hp / player.max_hp if hasattr(player, 'max_hp') else 1.0,
            'player_stats': {
                'Strength': getattr(player, 'strength', 10),
                'level': getattr(player, 'level', 1)
            },
            'tilemap': tilemap,
            'all_enemies': all_enemies,
            'ai_group': None,  # Will be set if enemy is in a group
            'personality_system': self.emotional_profile if hasattr(self, 'emotional_profile') else None,
            'personality_traits': self.personality_traits if hasattr(self, 'personality_traits') else None,
            'companions': kwargs.get('companions', []),
            'dt': kwargs.get('dt', 1/60),
        }
        
        # Add AI group context if enemy is in a pack
        if hasattr(self, 'pack_id') and self.pack_id and all_enemies:
            from advanced_ai_system import EnemyGroup
            pack_members = [e for e in all_enemies if hasattr(e, 'pack_id') and e.pack_id == self.pack_id and e.alive]
            if len(pack_members) > 1:
                # Create a simple group object for context
                class SimpleGroup:
                    def __init__(self, members):
                        self.members = members
                context['ai_group'] = SimpleGroup(pack_members)
        
        return context
                 
    def cast_spells(self, player, message_console, current_weather=None):
        if hasattr(self, "magic") and self.magic:
            for spell_name in self.magic:
                spell = ENEMY_SPELLS.get(spell_name)
                if spell and self.can_cast(spell_name):
                    dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
                    if dist <= spell.get("range", 150):
                        if spell.get("damage"):
                            magic_def = player.stats["Willpower"] * 0.12
                            spell_damage = max(1, spell["damage"] - magic_def)
                            # Thunderstorm bonus for electric spells
                            if current_weather == "thunderstorm" and spell.get("element") == "electric":
                                spell_damage *= 1.12
                            player.health -= spell_damage
                            if message_console:
                                if current_weather == "thunderstorm" and spell.get("element") == "electric":
                                    message_console.add_message(f"{self.type} casts {spell_name} (storm boosted!) for {spell_damage:.1f}!")
                                else:
                                    message_console.add_message(f"{self.type} casts {spell_name} for {spell_damage:.1f}!")
                                    
                            # If it's a thunderstorm and this is an electric spell, boost damage by 12%
                            if current_weather == "thunderstorm" and spell.get("element") == "electric":
                                spell_damage *= 1.12                                    
                        
    def spawn_projectile(self, direction, color, speed, duration, proj_type="projectile", extra=None):
        if len(self.attack_visuals) < 3:
            self.attack_visuals.append(
                AttackVisual(
                    visual_type=proj_type,
                    pos=(self.rect.centerx, self.rect.centery),
                    direction=direction,
                    color=color,
                    start_time=time.time(),
                    duration=duration,
                    extra=extra or {"speed": speed}
                )
            )

    def collides(self, tilemap):
        for x in range(self.rect.left // 50, self.rect.right // 50 + 1):
            for y in range(self.rect.top // 50, self.rect.bottom // 50 + 1):
                if 0 <= x < len(tilemap[0]) and 0 <= y < len(tilemap):
                    if tilemap[y][x]["type"] not in {"grass", "sand", "rubble", "fiber", "ash", "wood"}:
                        return True
        return False

    def collides_optimized(self, tilemap, rect=None):
        """Optimized collision detection with early exits and reduced calculations"""
        if rect is None:
            rect = self.rect
            
        # Early bounds check - if completely outside tilemap, no collision
        if rect.right < 0 or rect.left >= len(tilemap[0]) * 50:
            return False
        if rect.bottom < 0 or rect.top >= len(tilemap) * 50:
            return False
            
        # Get tile bounds (using integer division for efficiency)
        left_tile = max(0, rect.left // 50)
        right_tile = min(len(tilemap[0]) - 1, rect.right // 50)
        top_tile = max(0, rect.top // 50) 
        bottom_tile = min(len(tilemap) - 1, rect.bottom // 50)
        
        # Check only necessary tiles with cached walkability results
        for y in range(top_tile, bottom_tile + 1):
            for x in range(left_tile, right_tile + 1):
                if not tile_collision_cache.is_walkable(tilemap, x, y):
                    return True
        return False

    def try_move(self, tilemap, player, move_x, move_y):
        """Optimized movement with single collision check"""
        if move_x == 0 and move_y == 0:
            return True
            
        old_rect = self.rect.copy()
        
        # Try combined movement first (most efficient)
        self.rect.x += move_x
        self.rect.y += move_y
        
        # Single collision check for combined movement
        if not self.collides_optimized(tilemap) and not self.rect.colliderect(player.rect):
            return True
            
        # If combined movement failed, try separate axes
        self.rect = old_rect.copy()
        
        # Try X movement only
        moved_x = False
        if move_x != 0:
            self.rect.x += move_x
            if not self.collides_optimized(tilemap) and not self.rect.colliderect(player.rect):
                moved_x = True
            else:
                self.rect.x = old_rect.x
                
        # Try Y movement only  
        moved_y = False
        if move_y != 0:
            self.rect.y += move_y
            if not self.collides_optimized(tilemap) and not self.rect.colliderect(player.rect):
                moved_y = True
            else:
                self.rect.y = old_rect.y
                
        return moved_x or moved_y

    def draw(self, screen, offset, player=None, current_weather=None, tilemap=None):
        pr = self.rect.move(-offset[0], -offset[1])
        
        # Draw attack telegraph warning (red tint)
        if self.attack_telegraphing:
            # Red pulsating overlay
            pulse = (math.sin(time.time() * 12) + 1) * 0.5  # Fast pulse
            red_alpha = int(80 + pulse * 120)  # 80-200 alpha
            
            red_surface = pygame.Surface((pr.width, pr.height), pygame.SRCALPHA)
            pygame.draw.rect(red_surface, (255, 0, 0, red_alpha), (0, 0, pr.width, pr.height))
            screen.blit(red_surface, (pr.x, pr.y))
            
            # Red outline
            pygame.draw.rect(screen, (255, 0, 0), pr, 3)
        
        # Draw enemy body
        pygame.draw.rect(screen, self.color, pr)
        cx, cy = pr.center

        # Draw equipped armor and weapons on the enemy using shared renderer
        EquipmentRenderer.draw_equipment(screen, self, (cx, cy), entity_type="enemy")
        
        # Health bar
        hp_ratio = self.health / self.max_health
        bar_w = pr.width
        pygame.draw.rect(screen, (200, 0, 0), (pr.x, pr.y - 8, int(bar_w * hp_ratio), 6))
        pygame.draw.rect(screen, (60, 0, 0), (pr.x, pr.y - 8, bar_w, 6), 1)

        # Add this new code right here:
        # Draw rarity indicators for non-common enemies
        if self.rarity != "Common":
            # Draw glow effect
            if self.glow_effect:
                # Create a surface for the glow with alpha channel
                glow_surface = pygame.Surface((pr.width + self.glow_size*2, pr.height + self.glow_size*2), pygame.SRCALPHA)
                
                # Pulsating effect
                pulse = (math.sin(time.time() * 5) + 1) * 0.5  # Value between 0 and 1
                glow_alpha = int(100 + pulse * 155)  # Value between 100 and 255
                
                # Draw the glow rectangle
                pygame.draw.rect(glow_surface, (*self.glow_color, glow_alpha), 
                                (0, 0, pr.width + self.glow_size*2, pr.height + self.glow_size*2), 0, 4)
                
                # Draw the glow surface
                screen.blit(glow_surface, (pr.x - self.glow_size, pr.y - self.glow_size))
            
            # Draw rarity label (first letter) - using cached font
            rarity_text = rarity_font_cache.get_rarity_text(self.rarity)
            screen.blit(rarity_text, (pr.x + pr.width - 10, pr.y - 15))
        
        # Draw attack telegraph exclamation mark
        if self.attack_telegraphing:
            # Draw exclamation mark above enemy
            try:
                warning_font = pygame.font.SysFont(None, 36, bold=True)
                exclamation_text = warning_font.render("!", True, (255, 0, 0))
                exclamation_shadow = warning_font.render("!", True, (100, 0, 0))
                
                # Bobbing effect
                bob_offset = int(math.sin(time.time() * 8) * 3)
                
                # Draw shadow
                screen.blit(exclamation_shadow, (pr.centerx - exclamation_shadow.get_width()//2 + 2, 
                                                 pr.y - 40 + bob_offset + 2))
                # Draw exclamation
                screen.blit(exclamation_text, (pr.centerx - exclamation_text.get_width()//2, 
                                               pr.y - 40 + bob_offset))
            except:
                pass  # Font loading failed, skip indicator

                
        # --- NEW: Draw attack visuals (melee arcs) ---
        now = time.time()
        offset = (0, 0)  # Default offset for drawing
        for visual in self.attack_visuals[:]:
            if visual.visual_type == "melee_arc":
                elapsed = now - visual.start_time
                if elapsed > visual.duration:
                    self.attack_visuals.remove(visual)
                    continue
                # Draw arc
                arc_center = (int(visual.pos[0] - offset[0]), int(visual.pos[1] - offset[1]))
                arc_radius = int(visual.extra.get("arc_size", 30))
                arc_angle = visual.extra.get("arc_angle", math.radians(70))
                start_angle = visual.direction - arc_angle / 2
                end_angle = visual.direction + arc_angle / 2
                points = [arc_center]
                steps = 12
                for i in range(steps + 1):
                    angle = start_angle + (end_angle - start_angle) * i / steps
                    x = arc_center[0] + arc_radius * math.cos(angle)
                    y = arc_center[1] + arc_radius * math.sin(angle)
                    points.append((x, y))
                s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                pygame.draw.polygon(s, visual.color + (90,), points)
                screen.blit(s, (0, 0))
            elif visual.visual_type in ("arrow", "crystal_shard", "fireball", "ice_shard", "lightning", "magic_beam"):
                elapsed = now - visual.start_time
                if elapsed > visual.duration:
                    self.attack_visuals.remove(visual)
                    continue
                # Move projectile
                speed = visual.extra.get("speed", 5)
                dx = math.cos(visual.direction) * speed
                dy = math.sin(visual.direction) * speed
                visual.pos = (visual.pos[0] + dx, visual.pos[1] + dy)
                # Draw projectile (simple circle)
                proj_center = (int(visual.pos[0] - offset[0]), int(visual.pos[1] - offset[1]))
                proj_radius = 7
                pygame.draw.circle(screen, visual.color, proj_center, proj_radius)

        # --- Bandit Bow (arrow projectile) ---
        if self.weapon == "bow":
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            min_range = 80
            max_range = 350
            
            # Check if we're currently telegraphing
            if self.attack_telegraphing and hasattr(self, 'ranged_attack_pending'):
                # Check if telegraph duration has elapsed
                if now - self.attack_telegraph_start_time >= self.attack_telegraph_duration:
                    # Telegraph complete - fire the projectile!
                    self.attack_telegraphing = False
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx)
                    proj_speed = self.speed * 1.2 + 2
                    proj_duration = 0.7
                    proj_color = (120, 80, 30)
                    self.spawn_projectile(
                        direction=angle,
                        color=proj_color,
                        speed=proj_speed,
                        duration=proj_duration,
                        proj_type="arrow"
                    )
                    self.last_attack_time = now
                    self.attack_cooldown = 1.2
                    delattr(self, 'ranged_attack_pending')
            elif min_range < dist < max_range and now - self.last_attack_time >= self.attack_cooldown:
                # Start telegraph
                self.attack_telegraphing = True
                self.attack_telegraph_start_time = now
                self.ranged_attack_pending = True

        # --- Crystal Golem (crystal shard projectile) ---
        if self.weapon == "crystal_shard":
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            min_range = 60
            max_range = 300
            
            if self.attack_telegraphing and hasattr(self, 'ranged_attack_pending_crystal'):
                if now - self.attack_telegraph_start_time >= self.attack_telegraph_duration:
                    self.attack_telegraphing = False
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx)
                    proj_speed = self.speed * 1.2 + 2
                    proj_duration = 0.7
                    proj_color = (180, 220, 255)
                    self.spawn_projectile(
                        direction=angle,
                        color=proj_color,
                        speed=proj_speed,
                        duration=proj_duration,
                        proj_type="crystal_shard"
                    )
                    self.last_attack_time = now
                    self.attack_cooldown = 1.5
                    delattr(self, 'ranged_attack_pending_crystal')
            elif min_range < dist < max_range and now - self.last_attack_time >= self.attack_cooldown:
                self.attack_telegraphing = True
                self.attack_telegraph_start_time = now
                self.ranged_attack_pending_crystal = True

        # --- Fire Elemental (fireball projectile) ---
        if self.weapon == "fire_orb":
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            min_range = 60
            max_range = 300
            
            if self.attack_telegraphing and hasattr(self, 'ranged_attack_pending_fire'):
                if now - self.attack_telegraph_start_time >= self.attack_telegraph_duration:
                    self.attack_telegraphing = False
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx)
                    proj_speed = self.speed * 1.2 + 2
                    proj_duration = 0.7
                    proj_color = (255, 80, 0)
                    self.spawn_projectile(
                        direction=angle,
                        color=proj_color,
                        speed=proj_speed,
                        duration=proj_duration,
                        proj_type="fireball"
                    )
                    self.last_attack_time = now
                    self.attack_cooldown = 1.5
                    delattr(self, 'ranged_attack_pending_fire')
            elif min_range < dist < max_range and now - self.last_attack_time >= self.attack_cooldown:
                self.attack_telegraphing = True
                self.attack_telegraph_start_time = now
                self.ranged_attack_pending_fire = True

        # --- Frost Witch (ice shard projectile) ---
        if self.weapon == "ice_wand":
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            min_range = 60
            max_range = 300
            
            if self.attack_telegraphing and hasattr(self, 'ranged_attack_pending_ice'):
                if now - self.attack_telegraph_start_time >= self.attack_telegraph_duration:
                    self.attack_telegraphing = False
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx)
                    proj_speed = self.speed * 1.2 + 2
                    proj_duration = 0.7
                    proj_color = (130, 210, 255)
                    self.spawn_projectile(
                        direction=angle,
                        color=proj_color,
                        speed=proj_speed,
                        duration=proj_duration,
                        proj_type="ice_shard"
                    )
                    self.last_attack_time = now
                    self.attack_cooldown = 1.5
                    delattr(self, 'ranged_attack_pending_ice')
            elif min_range < dist < max_range and now - self.last_attack_time >= self.attack_cooldown:
                self.attack_telegraphing = True
                self.attack_telegraph_start_time = now
                self.ranged_attack_pending_ice = True

        # --- Storm Mage (lightning bolt projectile) ---
        if self.weapon == "lightning_rod":
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            min_range = 60
            max_range = 300
            
            if self.attack_telegraphing and hasattr(self, 'ranged_attack_pending_lightning'):
                if now - self.attack_telegraph_start_time >= self.attack_telegraph_duration:
                    self.attack_telegraphing = False
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx)
                    proj_speed = self.speed * 1.2 + 2
                    proj_duration = 0.7
                    proj_color = (180, 180, 255)
                    self.spawn_projectile(
                        direction=angle,
                        color=proj_color,
                        speed=proj_speed,
                        duration=proj_duration,
                        proj_type="lightning"
                    )
                    self.last_attack_time = now
                    self.attack_cooldown = 1.5
                    delattr(self, 'ranged_attack_pending_lightning')
            elif min_range < dist < max_range and now - self.last_attack_time >= self.attack_cooldown:
                self.attack_telegraphing = True
                self.attack_telegraph_start_time = now
                self.ranged_attack_pending_lightning = True

        # --- Arcane Golem (magic beam projectile) ---
        if self.weapon == "magic_beam":
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            min_range = 60
            max_range = 300
            
            if self.attack_telegraphing and hasattr(self, 'ranged_attack_pending_magic'):
                if now - self.attack_telegraph_start_time >= self.attack_telegraph_duration:
                    self.attack_telegraphing = False
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx)
                    proj_speed = self.speed * 1.2 + 2
                    proj_duration = 0.7
                    proj_color = (180, 140, 240)
                    self.spawn_projectile(
                        direction=angle,
                        color=proj_color,
                        speed=proj_speed,
                        duration=proj_duration,
                        proj_type="magic_beam"
                    )
                    self.last_attack_time = now
                    self.attack_cooldown = 1.5
                    delattr(self, 'ranged_attack_pending_magic')
            elif min_range < dist < max_range and now - self.last_attack_time >= self.attack_cooldown:
                self.attack_telegraphing = True
                self.attack_telegraph_start_time = now
                self.ranged_attack_pending_magic = True
                
        # --- Handle projectile collisions and cleanup ---
        for visual in self.attack_visuals[:]:
            # Remove if projectile has expired (failsafe)
            if visual.visual_type in ("arrow", "crystal_shard", "fireball", "ice_shard", "lightning", "magic_beam"):
                if time.time() - visual.start_time > visual.duration:
                    self.attack_visuals.remove(visual)
                    continue
            if visual.visual_type in ("arrow", "crystal_shard", "fireball", "ice_shard", "lightning", "magic_beam"):
                # Build a rect for the projectile
                proj_rect = pygame.Rect(
                    int(visual.pos[0] - 7), int(visual.pos[1] - 7), 14, 14
                )
                # Check collision with player
                if proj_rect.colliderect(player.rect):
                    if hasattr(player, "take_damage"):
                        # Pass basic damage parameters
                        player.take_damage(
                            self.damage,
                            floating_texts=None,
                            floating_combat_text_enabled=True
                        )
                    self.attack_visuals.remove(visual)
                    continue
                # Check collision with obstacles/tiles
                tile_x = int(visual.pos[0]) // 50
                tile_y = int(visual.pos[1]) // 50
                if (
                    tile_x < 0 or tile_y < 0 or
                    tile_x >= len(tilemap[0]) or tile_y >= len(tilemap)
                ):
                    self.attack_visuals.remove(visual)
                    continue
                if tilemap[tile_y][tile_x]["type"] not in {"grass", "sand", "rubble", "fiber", "ash", "wood"}:
                    self.attack_visuals.remove(visual)
                    continue
                
    def take_damage(self, amount, is_crit=False, *args, **kwargs):
        """
        Apply damage to the enemy with resistance calculations.
        Higher level and rarer enemies have better damage resistance.
        """
        # Input validation
        if not isinstance(amount, (int, float)):
            logger.warning(f"Invalid damage amount type: {type(amount)}. Expected number.")
            return
        if amount < 0:
            logger.warning(f"Negative damage amount: {amount}. Clamping to 0.")
            amount = 0
        
        # Check for boss phase transition immunity
        if isinstance(self, BossEnemy) and self.is_immune():
            floating_texts = kwargs.get("floating_texts")
            if floating_texts is not None:
                from floating_text import FloatingText
                floating_texts.append(FloatingText("IMMUNE!", (self.rect.centerx, self.rect.top - 20), color=(255, 255, 0)))
            return  # No damage taken during phase transition
            
        # Check for special ability immunity
        if hasattr(self, "damage_immunity_until") and time.time() < self.damage_immunity_until:
            # Show immunity indicator
            floating_texts = kwargs.get("floating_texts")
            if floating_texts is not None:
                from floating_text import FloatingText
                floating_texts.append(FloatingText("IMMUNE!", (self.rect.centerx, self.rect.top - 20), color=(255, 255, 0)))
            return  # No damage taken
            
        original_amount = amount

        # Calculate damage resistance based on enemy stats and type
        if hasattr(self, 'stats') and isinstance(self.stats, dict):
            # Base resistance from Stamina stat (tanky enemies resist more)
            stamina = self.stats.get("Stamina", 0)
            base_resistance = min(0.4, stamina * 0.015)  # Max 40% resistance, 1.5% per Stamina
            
            # Rarity-based resistance bonus
            rarity_resistance = {
                "Common": 0.0,
                "Uncommon": 0.05,    # 5% additional resistance
                "Rare": 0.1,         # 10% additional resistance
                "Epic": 0.15,        # 15% additional resistance
                "Legendary": 0.2     # 20% additional resistance
            }
            rarity_bonus = rarity_resistance.get(self.rarity, 0.0)
            
            # Enemy type-specific resistance
            type_resistance = {
                "golem": 0.15,       # Stone creatures are naturally tough
                "crystal_golem": 0.20,
                "troll": 0.12,
                "zombie": 0.08,      # Undead resist some damage
                "skeleton": 0.10,
                "orc": 0.05,         # Armored enemies
                "goblin": 0.03
            }
            type_bonus = type_resistance.get(self.type, 0.0)
            
            # Total resistance calculation (capped at 60%)
            total_resistance = min(0.6, base_resistance + rarity_bonus + type_bonus)
            
            # Apply resistance to damage
            amount = max(5, int(amount * (1 - total_resistance)))  # Minimum 5 damage

        # Floating combat text for enemies (optional)
        floating_texts = kwargs.get("floating_texts")
        floating_combat_text_enabled = kwargs.get("floating_combat_text_enabled", True)
        fx, fy = self.rect.centerx, self.rect.top - 20
        if floating_texts is not None and floating_combat_text_enabled:
            from floating_text import FloatingText  # Import here to avoid circular import
            if is_crit:
                floating_texts.append(FloatingText("Critical!", (fx, fy), color=(139,0,0)))
            elif amount < original_amount * 0.7:  # Show "Resist!" if significant damage reduction
                floating_texts.append(FloatingText("Resist!", (fx, fy), color=(100,100,255)))
            else:
                floating_texts.append(FloatingText(str(amount), (fx, fy), color=(255,0,0)))

        self.health -= amount
        if self.health <= 0:
            self.alive = False
            # --- Loot drop logic ---
            if self.rarity in ("Epic", "Legendary"):
                loot_items = loot.get_boss_loot()
            else:
                loot_items = loot.get_regular_enemy_loot()
            # Drop loot on ground at enemy's position
            dropped_equipment_list = kwargs.get("dropped_equipment_list", [])
            for item in loot_items:
                if item["type"] == "dubloon":
                    dropped_equipment_list.append(DroppedDubloon(
                        self.rect.centerx - 8,
                        self.rect.centery - 8,
                        item["amount"]
                    ))
                elif item["type"] in loot.LOOT_TABLE["filler_items"]:
                    dropped_equipment_list.append(DroppedFiller(
                        item["type"],
                        self.rect.centerx - 8,
                        self.rect.centery - 8
                    ))
                elif item["type"] in loot.LOOT_TABLE["consumables"]:
                    dropped_equipment_list.append(DroppedConsumable(
                        item["type"],
                        self.rect.centerx - 8,
                        self.rect.centery - 8
                    ))
                elif item["type"] in loot.LOOT_TABLE["recipe_scrolls"]:
                    # Recipe scrolls are treated as consumable items
                    dropped_equipment_list.append(DroppedConsumable(
                        item["type"],
                        self.rect.centerx - 8,
                        self.rect.centery - 8
                    ))
                else:
                    dropped_equipment_list.append(DroppedEquipment(
                        item["type"],
                        self.rect.centerx - 8,
                        self.rect.centery - 8,
                        rarity=item.get("rarity", "common")
                    ))
            logger.debug(f"Loot dropped: {loot_items}")
        # --- Aggro on being attacked ---
        self.state = "aggro"

        # --- Pack aggro: alert packmates ---
        all_enemies = kwargs.get("all_enemies")
        player = kwargs.get("player")
        if self.type in PACK_TYPES and self.pack_id is not None and all_enemies is not None and player is not None:
            TILE_SIZE = Config.TILE_SIZE
            ex, ey = self.rect.centerx, self.rect.centery
            for enemy in all_enemies:
                if (
                    enemy is not self and
                    enemy.type == self.type and
                    enemy.pack_id == self.pack_id and
                    enemy.alive and
                    enemy.on_screen(player) and
                    math.hypot(enemy.rect.centerx - ex, enemy.rect.centery - ey) <= PACK_RADIUS_TILES * TILE_SIZE
                ):
                    enemy.state = "aggro"

    def handle_pack_coordination(self, player, all_enemies, tilemap):
        now = time.time()
        if now - self.pack_last_coordination < PACK_COORDINATION_INTERVAL:
            return  # Only coordinate every PACK_COORDINATION_INTERVAL seconds

        # Find all visible, alive, same-type, common-rarity enemies within PACK_RADIUS_TILES
        TILE_SIZE = Config.TILE_SIZE
        ex, ey = self.rect.centerx, self.rect.centery
        pack_members = []
        for enemy in all_enemies:
            if (
                enemy is not self and
                enemy.type == self.type and
                enemy.rarity == "Common" and
                enemy.alive and
                enemy.on_screen(player) and
                math.hypot(enemy.rect.centerx - ex, enemy.rect.centery - ey) <= PACK_RADIUS_TILES * TILE_SIZE
            ):
                pack_members.append(enemy)
        pack_members.append(self)  # Include self

        # Limit pack size
        if len(pack_members) > PACK_MAX_SIZE:
            pack_members = sorted(pack_members, key=lambda e: e.pack_last_coordination)[:PACK_MAX_SIZE]

        # Assign pack_id (use id of first spawned/lowest pack_last_coordination)
        pack_id = min(id(e) for e in pack_members)
        for enemy in pack_members:
            enemy.pack_id = pack_id

        # Choose leader: highest health
        leader = max(pack_members, key=lambda e: e.health)
        old_leader_id = id(leader) if hasattr(self, 'pack_leader_id') else None
        
        # Check if leader died (retreat mechanic)
        if old_leader_id and old_leader_id != id(leader):
            # Old leader died, pack retreats temporarily
            for enemy in pack_members:
                if enemy.state == "aggro":
                    enemy.state = "flee"
                    enemy._call_for_help_on_flee = False  # Don't call for help during leader death retreat
            logger.info(f"[PACK] Pack leader died, {len(pack_members)} members retreating!")
        
        for enemy in pack_members:
            enemy.is_pack_leader = (enemy is leader)
            enemy.pack_leader_id = id(leader)

        # Enhanced tactics: focus, surround, or synchronized
        if len(pack_members) >= 3:
            # Large packs can do synchronized attacks
            tactic = random.choice(["focus", "surround", "synchronized"])
        else:
            tactic = random.choice(["focus", "surround"])
        
        for enemy in pack_members:
            enemy.pack_tactic = tactic
            
            # Initialize synchronized attack state
            if tactic == "synchronized":
                enemy.is_in_attack_position = False
                enemy.wait_for_pack = True

        self.pack_last_coordination = now
        
    def on_screen(self, player):
        # Checks if the enemy is within the visible screen area around the player
        SCREEN_WIDTH = 1280  # Or your actual screen width
        SCREEN_HEIGHT = 720  # Or your actual screen height
        px, py = player.rect.centerx, player.rect.centery
        ex, ey = self.rect.centerx, self.rect.centery
        return (
            abs(ex - px) < SCREEN_WIDTH // 2 + 100 and
            abs(ey - py) < SCREEN_HEIGHT // 2 + 100
        )
