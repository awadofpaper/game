"""
Town Instance System - Creates separate map instances for towns
"""

import pygame
import random
from tile import Tile
from town_system import BuildingType, Building
from config import Config

# Create config instance for accessing tile size and other settings
config = Config()


class TownInstance:
    """A town instance - separate map when player enters a town"""
    
    def __init__(self, town_name, town_size):
        self.name = town_name
        self.size = town_size
        self.width = 2000  # Width in pixels
        self.height = 2000  # Height in pixels
        self.tile_width = self.width // config.TILE_SIZE
        self.tile_height = self.height // config.TILE_SIZE
        
        # Create the tile map (2D array of Tile objects)
        self.tiles = [[Tile(ground='grass') for _ in range(self.tile_width)] for _ in range(self.tile_height)]
        
        # Buildings in the town instance
        self.buildings = []
        
        # Gate position (player spawns here)
        self.gate_x = self.width // 2
        self.gate_y = self.height - 100  # Near south edge
        
        # NPCs in the town
        self.npcs = []
        
        # Generate the town layout
        self._generate_layout()
    
    def _generate_layout(self):
        """Generate the town instance layout"""
        # Add path tiles leading from gate
        self._add_main_path()
        
        # Place buildings based on town size
        self._place_buildings()
        
        # Add decorative elements (trees, flowers, etc.)
        self._add_decorations()
    
    def _add_main_path(self):
        """Add a main path from the gate to the town center"""
        # Vertical path from gate upward
        path_width = 5  # tiles wide
        center_tile_x = self.gate_x // config.TILE_SIZE
        start_tile_y = (self.gate_y - 100) // config.TILE_SIZE
        end_tile_y = self.tile_height // 3  # Path goes 1/3 up the map
        
        for y in range(start_tile_y, end_tile_y):
            for offset in range(-path_width // 2, path_width // 2 + 1):
                tile_x = center_tile_x + offset
                if 0 <= tile_x < self.tile_width and 0 <= y < self.tile_height:
                    self.tiles[y][tile_x] = Tile(ground='dirt')  # Use dirt for paths
        
        # Horizontal path across the center
        center_tile_y = self.tile_height // 2
        for x in range(self.tile_width):
            for offset in range(-path_width // 2, path_width // 2 + 1):
                tile_y = center_tile_y + offset
                if 0 <= tile_y < self.tile_height:
                    self.tiles[tile_y][x] = Tile(ground='dirt')  # Use dirt for paths
    
    def _place_buildings(self):
        """Place buildings in the town instance"""
        # Determine building count and types based on size
        building_counts = {
            "small": 6,   # All 6 core buildings
            "medium": 9,  # 6 core + 2-3 optional
            "large": 12   # 6 core + 4 optional + 2 houses
        }
        num_buildings = building_counts.get(self.size, 9)
        
        # Core buildings (all towns have these)
        core_buildings = [
            (BuildingType.INN, 120, 140),
            (BuildingType.SHOP, 100, 120),
            (BuildingType.BLACKSMITH, 100, 110),
            (BuildingType.BANK, 80, 100),  # Banks are essential for global banking system
            (BuildingType.TOWN_HALL, 150, 180),
            (BuildingType.LOOTBOX_SHOP, 85, 95),  # Max's predatory shop
        ]
        
        # Optional buildings
        optional_buildings = [
            (BuildingType.MARKET, 90, 110),
            (BuildingType.TAVERN, 90, 110),
            (BuildingType.GUARD_TOWER, 60, 80),
            (BuildingType.TEMPLE, 100, 120),
        ]
        
        # Houses
        houses = [
            (BuildingType.HOUSE, 70, 80) for _ in range(3)
        ]
        
        # Combine buildings
        all_building_specs = core_buildings.copy()
        remaining = num_buildings - len(core_buildings)
        
        # Add optional buildings
        num_optional = min(remaining, len(optional_buildings))
        if self.size == "large":
            all_building_specs.extend(optional_buildings[:num_optional])
        elif self.size == "medium":
            all_building_specs.extend(random.sample(optional_buildings, min(2, num_optional)))
        
        remaining = num_buildings - len(all_building_specs)
        if remaining > 0:
            all_building_specs.extend(houses[:remaining])
        
        # Place buildings in a grid-like pattern
        self._place_buildings_grid(all_building_specs)
    
    def _place_buildings_grid(self, building_specs):
        """Place buildings in a grid pattern with spacing"""
        # Divide town into sections
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Place buildings in a rough grid around the center
        positions = [
            # Top row
            (center_x - 400, center_y - 400),
            (center_x - 150, center_y - 400),
            (center_x + 150, center_y - 400),
            (center_x + 400, center_y - 400),
            # Middle left
            (center_x - 500, center_y - 100),
            (center_x - 500, center_y + 150),
            # Middle right
            (center_x + 350, center_y - 100),
            (center_x + 350, center_y + 150),
            # Bottom row
            (center_x - 350, center_y + 400),
            (center_x, center_y + 400),
            (center_x + 300, center_y + 400),
            # Extra positions
            (center_x - 200, center_y + 100),
        ]
        
        # Place buildings at positions
        for i, (building_type, width, height) in enumerate(building_specs):
            if i < len(positions):
                x, y = positions[i]
                # Ensure buildings don't go out of bounds
                x = max(50, min(self.width - width - 50, x))
                y = max(50, min(self.height - height - 50, y))
                
                building = Building(building_type, x, y, width, height)
                self.buildings.append(building)
    
    def _add_decorations(self):
        """Add decorative elements like trees, flowers"""
        # Add some trees around the edges
        random.seed(hash(self.name))  # Consistent decorations per town
        
        for _ in range(30):
            x = random.randint(0, self.tile_width - 1)
            y = random.randint(0, self.tile_height - 1)
            
            # Don't place on paths or near buildings
            if self.tiles[y][x]['ground'] != 'dirt' and not self._near_building(x * config.TILE_SIZE, y * config.TILE_SIZE):
                # Only place near edges
                if x < 10 or x > self.tile_width - 10 or y < 10 or y > self.tile_height - 10:
                    self.tiles[y][x] = Tile(ground='tree')
    
    def _near_building(self, x, y):
        """Check if position is near any building"""
        for building in self.buildings:
            if (building.x - 100 < x < building.x + building.width + 100 and
                building.y - 100 < y < building.y + building.height + 100):
                return True
        return False
    
    def is_in_bounds(self, x, y):
        """Check if position is within town instance bounds"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_tile_at(self, x, y):
        """Get tile at world position"""
        tile_x = int(x // config.TILE_SIZE)
        tile_y = int(y // config.TILE_SIZE)
        
        if 0 <= tile_x < self.tile_width and 0 <= tile_y < self.tile_height:
            return self.tiles[tile_y][tile_x]
        return Tile(ground='grass')
    
    def draw_tiles(self, screen, camera_x, camera_y):
        """Draw the town instance tiles"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate visible tile range (ensure integers for range())
        start_x = int(max(0, camera_x // config.TILE_SIZE - 1))
        end_x = int(min(self.tile_width, (camera_x + screen_width) // config.TILE_SIZE + 2))
        start_y = int(max(0, camera_y // config.TILE_SIZE - 1))
        end_y = int(min(self.tile_height, (camera_y + screen_height) // config.TILE_SIZE + 2))
        
        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                ground_type = tile['ground'] if tile else 'grass'
                screen_x = x * config.TILE_SIZE - camera_x
                screen_y = y * config.TILE_SIZE - camera_y
                
                # Draw tile based on ground type
                if ground_type == 'grass':
                    color = (100, 180, 100)
                elif ground_type == 'tree':
                    color = (34, 139, 34)
                elif ground_type == 'dirt':
                    color = (180, 160, 120)
                else:
                    color = (100, 180, 100)
                
                pygame.draw.rect(screen, color, (screen_x, screen_y, config.TILE_SIZE, config.TILE_SIZE))
    
    def draw_buildings(self, screen, camera_x, camera_y):
        """Draw buildings in the town instance"""
        for building in self.buildings:
            building.draw(screen, camera_x, camera_y)
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the entire town instance"""
        self.draw_tiles(screen, camera_x, camera_y)
        self.draw_buildings(screen, camera_x, camera_y)
        
        # Draw gate marker
        gate_screen_x = self.gate_x - camera_x
        gate_screen_y = self.gate_y - camera_y
        pygame.draw.rect(screen, (150, 100, 50), (gate_screen_x - 40, gate_screen_y - 20, 80, 40))
        pygame.draw.rect(screen, (0, 0, 0), (gate_screen_x - 40, gate_screen_y - 20, 80, 40), 3)
        
        # Draw gate text
        font = pygame.font.SysFont(None, 20)
        gate_text = font.render("EXIT", True, (255, 255, 255))
        screen.blit(gate_text, (gate_screen_x - gate_text.get_width() // 2, gate_screen_y - 10))


def create_town_instance(town_name, town_size):
    """Create a new town instance"""
    return TownInstance(town_name, town_size)
