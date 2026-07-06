import random
import math
from enemies import ENEMY_TYPE_NAMES
from enemies import spawn_enemy
from loot import DUNGEON_LOOT_TYPES
from loot import LOOT_TABLE
from enemies import Enemy
from dropped_equipment import DroppedEquipment, DroppedDubloon, DroppedFiller, DroppedConsumable
from dungeon_variety import (
    DungeonVarietySystem, DUNGEON_MODIFIERS, DIFFICULTY_TIERS,
    get_dungeon_variety_system
)

class Dungeon:
    def __init__(self, width, height, theme="default", layout_style="cave", difficulty="normal", modifier=None):
        self.width = width
        self.height = height
        self.theme = theme  # For future expansion
        self.layout_style = layout_style  # "cave" or "rooms"
        self.tilemap = [[{"type": "wall"} for _ in range(width)] for _ in range(height)]
        self.entrance = None
        self.exit = None
        self.boss_pos = None
        self.generated = False
        self.cleared = False
        self.last_cleared_day = None
        self.enemies = []
        self.loot = []
        self.reset_days = random.randint(3, 5)  # Number of days until reset
        
        # Dungeon variety additions
        self.difficulty = difficulty
        self.modifier = modifier
        self.modifier_data = DUNGEON_MODIFIERS.get(modifier, {}) if modifier else {}
        self.difficulty_data = DIFFICULTY_TIERS.get(difficulty, DIFFICULTY_TIERS["normal"])
        self.enemy_count_modifier = 1.0
        self.darkness_active = False
        self.vision_radius = None
        self.traps = []
        self.secret_rooms = []
        self.mini_bosses = []
       
    def generate_cave_layout(self, fill_prob=0.45, steps=5):
        # Initialize with random walls/floors
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    self.tilemap[y][x]["type"] = "wall"
                else:
                    self.tilemap[y][x]["type"] = "floor" if random.random() > fill_prob else "wall"

        # Cellular automata steps
        for _ in range(steps):
            new_map = [[{"type": "wall"} for _ in range(self.width)] for _ in range(self.height)]
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    wall_count = 0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            if self.tilemap[y + dy][x + dx]["type"] == "wall":
                                wall_count += 1
                    if wall_count >= 5:
                        new_map[y][x]["type"] = "wall"
                    else:
                        new_map[y][x]["type"] = "floor"
            self.tilemap = new_map
            
    def generate_rooms_layout(self, room_attempts=30, min_room_size=6, max_room_size=16):
        rooms = []
        for _ in range(room_attempts):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)
            new_room = (x, y, w, h)
            # Check for overlap
            if any(self._rooms_overlap(new_room, other) for other in rooms):
                continue
            rooms.append(new_room)
            # Carve out the room
            for ry in range(y, y + h):
                for rx in range(x, x + w):
                    self.tilemap[ry][rx]["type"] = "floor"
        # Connect rooms with corridors
        for i in range(1, len(rooms)):
            x1, y1, _, _ = rooms[i - 1]
            x2, y2, _, _ = rooms[i]
            if random.random() < 0.5:
                self._carve_h_corridor(x1, x2, y1)
                self._carve_v_corridor(y1, y2, x2)
            else:
                self._carve_v_corridor(y1, y2, x1)
                self._carve_h_corridor(x1, x2, y2)
        self.rooms = rooms

    def _rooms_overlap(self, room1, room2, padding=2):
        x1, y1, w1, h1 = room1
        x2, y2, w2, h2 = room2
        return (x1 - padding < x2 + w2 and x1 + w1 + padding > x2 and
                y1 - padding < y2 + h2 and y1 + h1 + padding > y2)

    def _carve_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tilemap[y][x]["type"] = "floor"

    def _carve_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tilemap[y][x]["type"] = "floor"
            
    def generate(self):
        if self.layout_style == "cave":
            self.generate_cave_layout()
        elif self.layout_style == "rooms":
            self.generate_rooms_layout()
        else:
            self.generate_cave_layout()
        self.generated = True
        
    def place_entrance_and_boss(self):
        # Find all floor tiles
        floor_tiles = [(x, y) for y in range(self.height) for x in range(self.width) if self.tilemap[y][x]["type"] == "floor"]
        if not floor_tiles:
            return
        
        # Find floor tiles with adequate movement space (at least 2 adjacent walkable tiles)
        good_entrance_tiles = []
        for x, y in floor_tiles:
            adjacent_floors = 0
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    self.tilemap[ny][nx]["type"] == "floor"):
                    adjacent_floors += 1
            # Require at least 2 adjacent floor tiles for good movement
            if adjacent_floors >= 2:
                good_entrance_tiles.append((x, y))
        
        # Use good entrance tiles if available, otherwise fallback to any floor tile
        entrance_candidates = good_entrance_tiles if good_entrance_tiles else floor_tiles
        self.entrance = random.choice(entrance_candidates)
        self.tilemap[self.entrance[1]][self.entrance[0]]["type"] = "entrance"
        
        # Ensure entrance has adequate movement space by clearing adjacent walls
        ex, ey = self.entrance
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = ex + dx, ey + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    self.tilemap[ny][nx]["type"] == "wall"):
                    # Only clear if it's not on the border (maintain dungeon boundaries)
                    if not (nx == 0 or ny == 0 or nx == self.width - 1 or ny == self.height - 1):
                        self.tilemap[ny][nx]["type"] = "floor"
        # Place boss at the furthest floor tile from entrance
        def dist(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])
        self.boss_pos = max(floor_tiles, key=lambda pos: dist(pos, self.entrance))
        self.tilemap[self.boss_pos[1]][self.boss_pos[0]]["type"] = "boss"
        
        # Store boss enemy for later spawning
        self.boss_enemy = None  # Will be spawned when dungeon is entered
        # Place exit near boss (adjacent floor tile)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            ex, ey = self.boss_pos[0]+dx, self.boss_pos[1]+dy
            if 0 <= ex < self.width and 0 <= ey < self.height and self.tilemap[ey][ex]["type"] == "floor":
                self.exit = (ex, ey)
                self.tilemap[ey][ex]["type"] = "exit"
                break
            
    def check_and_reset(self, current_day):
        if self.cleared and self.last_cleared_day is not None:
            if current_day - self.last_cleared_day >= self.reset_days:
                self.reset()

    def reset(self):
        self.enemies = []
        self.loot = []
        # Regenerate the dungeon layout and reset state
        self.generate()
        self.place_entrance_and_boss()
        self.spawn_enemies(ENEMY_TYPE_NAMES, num_enemies=12)
        self.spawn_loot(DUNGEON_LOOT_TYPES, num_loot=6)
        self.cleared = False
        self.last_cleared_day = None
        self.reset_days = random.randint(3, 5)
        
    def spawn_enemies(self, enemy_types, num_enemies=10, player_level=1):
        floor_tiles = [(x, y) for y in range(self.height) for x in range(self.width)
                    if self.tilemap[y][x]["type"] == "floor"]
        
        # Remove tiles near entrance and boss to keep spawn areas clear
        safe_tiles = []
        for x, y in floor_tiles:
            valid_tile = True
            if self.entrance:
                # Keep a 2-tile radius around entrance clear of enemies
                dist_to_entrance = abs(x - self.entrance[0]) + abs(y - self.entrance[1])
                if dist_to_entrance < 3:
                    valid_tile = False
            if self.boss_pos:
                # Keep a 3-tile radius around boss clear of regular enemies
                dist_to_boss = abs(x - self.boss_pos[0]) + abs(y - self.boss_pos[1])
                if dist_to_boss < 4:
                    valid_tile = False
            if valid_tile:
                safe_tiles.append((x, y))
        
        random.shuffle(safe_tiles)
        for i in range(min(num_enemies, len(safe_tiles))):
            x, y = safe_tiles[i]
            enemy_type = random.choice(enemy_types)
            # Use spawn_enemy function for proper rarity scaling
            self.enemies.append(spawn_enemy(x * 50, y * 50, enemy_type, player_level))
        
        # Spawn the boss enemy at the boss position
        if self.boss_pos:
            from enemies import spawn_boss
            boss_x, boss_y = self.boss_pos[0] * 50, self.boss_pos[1] * 50
            self.boss_enemy = spawn_boss(boss_x, boss_y, None, player_level, self.layout_style)
            self.enemies.append(self.boss_enemy)

    def spawn_loot(self, loot_types, num_loot=5):
        floor_tiles = [(x, y) for y in range(self.height) for x in range(self.width)
                    if self.tilemap[y][x]["type"] == "floor"]
        random.shuffle(floor_tiles)
        for i in range(min(num_loot, len(floor_tiles))):
            x, y = floor_tiles[i]
            loot_type = random.choice(loot_types)
            px, py = x * 16, y * 16  # Use your actual pickup size or TILE_SIZE

            if loot_type == "dubloon":
                amount = random.choice(LOOT_TABLE["dubloon_amounts"]["regular_enemy"])
                self.loot.append(DroppedDubloon(px, py, amount))
            elif loot_type in LOOT_TABLE["filler_items"]:
                self.loot.append(DroppedFiller(loot_type, px, py))
            elif loot_type in LOOT_TABLE["consumables"]:
                self.loot.append(DroppedConsumable(loot_type, px, py))
            elif loot_type in LOOT_TABLE["equipment_types"]:
                self.loot.append(DroppedEquipment(loot_type, px, py))
            
def create_dungeon(width, height, theme="default", layout_style=None, difficulty="normal", modifier=None, player_level=1):
    if layout_style is None:
        layout_style = random.choice(["cave", "rooms"])
    
    # Roll for random modifier if not specified
    if modifier is None:
        variety_system = get_dungeon_variety_system()
        modifier = variety_system.roll_random_modifier(chance=0.25)  # 25% chance
    
    dungeon = Dungeon(width, height, theme=theme, layout_style=layout_style, difficulty=difficulty, modifier=modifier)
    dungeon.generate()
    dungeon.place_entrance_and_boss()
    
    # Apply enemy count modifiers
    base_enemies = 12
    if modifier and "enemy_count_multiplier" in DUNGEON_MODIFIERS.get(modifier, {}):
        base_enemies = int(base_enemies * DUNGEON_MODIFIERS[modifier]["enemy_count_multiplier"])
    
    dungeon.spawn_enemies(ENEMY_TYPE_NAMES, num_enemies=base_enemies, player_level=player_level)
    
    # Apply loot modifiers
    base_loot = 6
    if modifier and "loot_multiplier" in DUNGEON_MODIFIERS.get(modifier, {}):
        base_loot = int(base_loot * DUNGEON_MODIFIERS[modifier]["loot_multiplier"])
    
    dungeon.spawn_loot(DUNGEON_LOOT_TYPES, num_loot=base_loot)
    
    # Apply variety system enhancements
    variety_system = get_dungeon_variety_system()
    
    # Apply difficulty tier
    variety_system.apply_difficulty_to_dungeon(dungeon, difficulty)
    
    # Apply modifier effects
    if modifier:
        variety_system.apply_modifier_to_dungeon(dungeon, modifier)
    
    # Spawn traps (density based on modifier)
    trap_density = 1.0
    if modifier == "trap_master":
        trap_density = DUNGEON_MODIFIERS[modifier].get("trap_density", 3.0)
    variety_system.spawn_traps_in_dungeon(dungeon, density=trap_density)
    dungeon.traps = variety_system.traps
    
    # Spawn secret rooms (if room-based layout)
    if layout_style == "rooms" or (modifier == "treasure_hunt" and DUNGEON_MODIFIERS[modifier].get("secret_rooms")):
        secret_count = 3 if modifier == "treasure_hunt" else 2
        variety_system.spawn_secret_rooms(dungeon, count=secret_count)
        dungeon.secret_rooms = variety_system.secret_rooms
    
    # Spawn mini-bosses
    mini_boss_count = 2
    if modifier == "boss_rush":
        mini_boss_count = DUNGEON_MODIFIERS[modifier].get("mini_boss_count", 5)
    elif difficulty in ["nightmare", "hell"] and layout_style == "rooms":
        mini_boss_count = 3
    
    if layout_style == "rooms":
        variety_system.spawn_mini_bosses(dungeon, count=mini_boss_count)
        dungeon.mini_bosses = variety_system.mini_bosses
    
    # Add preview metadata
    dungeon.preview_info = {
        "estimated_difficulty": min(5, max(1, int((width * height) / 1000) + 1)),
        "theme_description": {
            "cave": "Ancient caverns carved by time and nature",
            "rooms": "Forgotten chambers of a lost civilization"
        }.get(layout_style, "A mysterious underground structure"),
        "recommended_level": max(1, int((width + height) / 50)),
        "estimated_time": f"{max(5, int((width * height) / 500))} minutes"
    }
    
    return dungeon