"""
Town System - Towns, Buildings, and Zones
"""

import pygame
import random

# Pre-create fonts for performance (don't recreate on every draw)
_building_name_font = None
_town_name_font = None

def _get_building_font():
    """Get or create building name font"""
    global _building_name_font
    if _building_name_font is None:
        _building_name_font = pygame.font.SysFont(None, 18)
    return _building_name_font

def _get_town_font():
    """Get or create town name font"""
    global _town_name_font
    if _town_name_font is None:
        _town_name_font = pygame.font.SysFont(None, 32)
    return _town_name_font

class BuildingType:
    """Building types available in towns"""
    INN = "inn"
    BLACKSMITH = "blacksmith"
    SHOP = "shop"
    MARKET = "market"
    BANK = "bank"
    HOUSE = "house"
    GUARD_TOWER = "guard_tower"
    TAVERN = "tavern"
    TEMPLE = "temple"
    TOWN_HALL = "town_hall"
    LOOTBOX_SHOP = "lootbox_shop"  # The predatory microtransaction parody
    JAIL = "jail"  # Central jail for all criminals
    SHACK = "shack"  # Small shack for tutorial NPC
    MAGE_TOWER = "mage_tower"  # Arcane sanctum for magical disease cures

class Building:
    """A building in a town"""
    
    def __init__(self, building_type, x, y, width, height, name=None):
        self.type = building_type
        self.x = x  # World coordinates
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name or self._generate_name()
        self.door_x = x + width // 2  # Door position (center of building)
        self.door_y = y + height
        self.npc_id = None  # NPC associated with this building
        self.is_enterable = True
        
        # Visual properties
        self.color = self._get_building_color()
        self.roof_color = self._get_roof_color()
        
        # Performance: Pre-render name sign (created on first draw)
        self._name_sign = None
        self._name_sign_created = False
    
    def _generate_name(self):
        """Generate a name based on building type"""
        names = {
            BuildingType.INN: ["The Cozy Rest", "Traveler's Inn", "The Golden Bed", "Sleepy Hollow Inn"],
            BuildingType.BLACKSMITH: ["Iron Works", "The Anvil", "Forge & Hammer", "Blacksmith's Shop"],
            BuildingType.SHOP: ["General Store", "Trader's Post", "The Market", "Merchant's Goods"],
            BuildingType.MARKET: ["Town Market", "Bazaar", "Trading Square", "Merchant Plaza"],
            BuildingType.BANK: ["Riverside Bank", "Gold Vault", "Secure Storage", "Town Treasury"],
            BuildingType.HOUSE: ["Residence", "Home", "Cottage", "House"],
            BuildingType.GUARD_TOWER: ["Guard Post", "Watch Tower", "Town Guards", "Security Post"],
            BuildingType.TAVERN: ["The Drunken Dragon", "Ale & Tales", "The Broken Barrel", "Merry Mug Tavern"],
            BuildingType.TEMPLE: ["Sacred Temple", "Chapel", "House of Light", "Divine Sanctuary"],
            BuildingType.TOWN_HALL: ["Town Hall", "Mayor's Office", "Council Building", "Administration"],
            BuildingType.LOOTBOX_SHOP: ["MaXxS Silicon Dioxide Shop"],  # Only one name - it's a franchise!
            BuildingType.JAIL: ["Iron Gate Penitentiary", "The Dungeon", "Blackrock Prison", "High Security Jail"],
            BuildingType.SHACK: ["Wandering Guide's Shack", "Small Shelter", "Traveler's Shack"],
            BuildingType.MAGE_TOWER: ["Arcane Sanctum", "Tower of Mysteries", "The Spire", "Wizard's Keep", "Mystic Academy"]
        }
        return random.choice(names.get(self.type, ["Building"]))
    
    def _get_building_color(self):
        """Get color based on building type"""
        colors = {
            BuildingType.INN: (139, 90, 43),  # Brown
            BuildingType.BLACKSMITH: (80, 80, 80),  # Dark gray
            BuildingType.SHOP: (180, 140, 100),  # Light brown
            BuildingType.MARKET: (200, 180, 140),  # Tan
            BuildingType.BANK: (150, 120, 60),  # Gold-ish
            BuildingType.HOUSE: (160, 120, 80),  # Wood brown
            BuildingType.GUARD_TOWER: (100, 100, 120),  # Blue-gray
            BuildingType.TAVERN: (120, 80, 40),  # Dark brown
            BuildingType.TEMPLE: (200, 200, 220),  # Light gray/white
            BuildingType.TOWN_HALL: (140, 100, 100),  # Reddish brown
            BuildingType.LOOTBOX_SHOP: (255, 20, 147),  # Hot pink - obnoxious and attention-grabbing
            BuildingType.JAIL: (50, 50, 50),  # Very dark gray - imposing and forbidding
            BuildingType.SHACK: (100, 80, 60),  # Weathered dark brown
            BuildingType.MAGE_TOWER: (80, 60, 140),  # Dark purple - mystical and arcane
        }
        return colors.get(self.type, (120, 120, 120))
    
    def _get_roof_color(self):
        """Get roof color (usually darker than building)"""
        base = self.color
        return (max(0, base[0] - 40), max(0, base[1] - 40), max(0, base[2] - 40))
    
    def is_near_door(self, x, y, radius=50):
        """Check if position is near the door"""
        distance = ((x - self.door_x) ** 2 + (y - self.door_y) ** 2) ** 0.5
        return distance < radius
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the building with distinct visuals per type"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Don't draw if off-screen (with margin)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        if (screen_x + self.width < -50 or screen_x > screen_width + 50 or
            screen_y + self.height < -50 or screen_y > screen_height + 50):
            return
        
        # Draw building body
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, self.width, self.height), 3)  # Outline
        
        # Draw building-specific details
        if self.type == BuildingType.BLACKSMITH:
            # Blacksmith: No roof, chimney smoke effect
            chimney_x = screen_x + self.width - 20
            chimney_y = screen_y + 5
            pygame.draw.rect(screen, (60, 60, 60), (chimney_x, chimney_y, 15, 25))
            # Anvil symbol
            pygame.draw.polygon(screen, (100, 100, 100), [
                (screen_x + self.width // 2 - 8, screen_y + self.height // 2),
                (screen_x + self.width // 2 + 8, screen_y + self.height // 2),
                (screen_x + self.width // 2 + 5, screen_y + self.height // 2 + 10),
                (screen_x + self.width // 2 - 5, screen_y + self.height // 2 + 10)
            ])
        elif self.type == BuildingType.TEMPLE:
            # Temple: Tall spire roof
            roof_height = 50
            roof_points = [
                (screen_x, screen_y),
                (screen_x + self.width // 2, screen_y - roof_height),
                (screen_x + self.width, screen_y)
            ]
            pygame.draw.polygon(screen, (180, 180, 200), roof_points)
            pygame.draw.polygon(screen, (0, 0, 0), roof_points, 2)
            # Cross on top
            cross_x = screen_x + self.width // 2
            cross_y = screen_y - roof_height
            pygame.draw.line(screen, (255, 215, 0), (cross_x, cross_y - 15), (cross_x, cross_y - 5), 3)
            pygame.draw.line(screen, (255, 215, 0), (cross_x - 4, cross_y - 11), (cross_x + 4, cross_y - 11), 3)
        elif self.type == BuildingType.GUARD_TOWER:
            # Guard Tower: Crenellations on top (castle-like)
            for i in range(0, self.width, 20):
                if i % 40 < 20:
                    pygame.draw.rect(screen, (80, 80, 100), (screen_x + i, screen_y - 10, 15, 10))
        elif self.type == BuildingType.TOWN_HALL:
            # Town Hall: Large flat roof with flag
            roof_height = 25
            pygame.draw.rect(screen, self.roof_color, (screen_x - 5, screen_y - roof_height, self.width + 10, roof_height))
            pygame.draw.rect(screen, (0, 0, 0), (screen_x - 5, screen_y - roof_height, self.width + 10, roof_height), 2)
            # Flag pole
            flag_x = screen_x + self.width // 2
            pygame.draw.line(screen, (80, 80, 80), (flag_x, screen_y - roof_height), (flag_x, screen_y - roof_height - 30), 2)
            # Flag
            pygame.draw.polygon(screen, (200, 50, 50), [
                (flag_x, screen_y - roof_height - 30),
                (flag_x + 15, screen_y - roof_height - 25),
                (flag_x, screen_y - roof_height - 20)
            ])
        elif self.type == BuildingType.BANK:
            # Bank: Pillars on front
            pillar_width = 8
            pillar_color = (130, 100, 40)
            pygame.draw.rect(screen, pillar_color, (screen_x + 15, screen_y + 10, pillar_width, self.height - 10))
            pygame.draw.rect(screen, pillar_color, (screen_x + self.width - 23, screen_y + 10, pillar_width, self.height - 10))
            # Vault symbol (circle)
            pygame.draw.circle(screen, (255, 215, 0), (screen_x + self.width // 2, screen_y + self.height // 2), 15)
            pygame.draw.circle(screen, (0, 0, 0), (screen_x + self.width // 2, screen_y + self.height // 2), 15, 2)
        else:
            # Default buildings: Standard triangular roof
            roof_height = 30
            roof_points = [
                (screen_x, screen_y),
                (screen_x + self.width // 2, screen_y - roof_height),
                (screen_x + self.width, screen_y)
            ]
            pygame.draw.polygon(screen, self.roof_color, roof_points)
            pygame.draw.polygon(screen, (0, 0, 0), roof_points, 2)  # Roof outline
        
        # Draw door (all buildings)
        door_width = 20
        door_height = 30
        door_x = screen_x + (self.width - door_width) // 2
        door_y = screen_y + self.height - door_height
        pygame.draw.rect(screen, (80, 50, 20), (door_x, door_y, door_width, door_height))
        pygame.draw.rect(screen, (0, 0, 0), (door_x, door_y, door_width, door_height), 2)
        
        # Draw windows (vary by building type)
        window_size = 12
        window_color = (200, 230, 255)
        
        if self.type == BuildingType.SHOP or self.type == BuildingType.MARKET:
            # Shop/Market: Large display windows
            window_width = 25
            window_height = 20
            pygame.draw.rect(screen, window_color, 
                            (screen_x + 10, screen_y + self.height // 2, window_width, window_height))
            pygame.draw.rect(screen, (0, 0, 0), 
                            (screen_x + 10, screen_y + self.height // 2, window_width, window_height), 2)
            pygame.draw.rect(screen, window_color,
                            (screen_x + self.width - 10 - window_width, screen_y + self.height // 2, window_width, window_height))
            pygame.draw.rect(screen, (0, 0, 0),
                            (screen_x + self.width - 10 - window_width, screen_y + self.height // 2, window_width, window_height), 2)
        else:
            # Standard windows
            pygame.draw.rect(screen, window_color, 
                            (screen_x + 15, screen_y + 20, window_size, window_size))
            pygame.draw.rect(screen, (0, 0, 0), 
                            (screen_x + 15, screen_y + 20, window_size, window_size), 1)
            pygame.draw.rect(screen, window_color,
                            (screen_x + self.width - 15 - window_size, screen_y + 20, window_size, window_size))
            pygame.draw.rect(screen, (0, 0, 0),
                            (screen_x + self.width - 15 - window_size, screen_y + 20, window_size, window_size), 1)
        
        # Draw building name sign (pre-render for performance)
        if not self._name_sign_created:
            font = _get_building_font()
            name_text = font.render(self.name, True, (255, 255, 255))
            self._name_sign = pygame.Surface((name_text.get_width() + 8, name_text.get_height() + 4))
            self._name_sign.set_alpha(200)
            self._name_sign.fill((0, 0, 0))
            self._name_sign.blit(name_text, (4, 2))
            self._name_sign_created = True
        
        sign_x = screen_x + (self.width - self._name_sign.get_width()) // 2
        sign_y = screen_y - 25
        
        screen.blit(self._name_sign, (sign_x, sign_y))


class Town:
    """A town with multiple buildings and NPCs"""
    
    def __init__(self, name, center_x, center_y, size="medium"):
        self.name = name
        self.center_x = center_x
        self.center_y = center_y
        self.size = size  # small, medium, large
        self.buildings = []
        self.npcs = []
        self.radius = self._get_radius()
        self.discovered = False
        
        # Town zone (rectangular boundary)
        self.zone_width = self.radius * 2
        self.zone_height = self.radius * 2
        self.zone_rect = pygame.Rect(
            center_x - self.radius,
            center_y - self.radius,
            self.zone_width,
            self.zone_height
        )
        
        # Performance: Pre-create zone surface once
        self._zone_surface = pygame.Surface((self.zone_width, self.zone_height))
        self._zone_surface.set_alpha(40)
        self._zone_surface.fill((100, 150, 100))
        
        # Performance: Pre-render town name sign
        self._name_sign = None
        self._name_sign_created = False
        
        # Generate buildings
        self._generate_buildings()
    
    def _get_radius(self):
        """Get town radius based on size"""
        sizes = {
            "small": 200,
            "medium": 350,
            "large": 500
        }
        return sizes.get(self.size, 350)
    
    def _generate_buildings(self):
        """Generate buildings in the town"""
        # Determine building count based on size
        building_counts = {
            "small": 5,
            "medium": 8,
            "large": 12
        }
        num_buildings = building_counts.get(self.size, 8)
        
        # Core buildings (every town has these)
        core_buildings = [
            (BuildingType.INN, 80, 100),
            (BuildingType.SHOP, 70, 90),
            (BuildingType.BLACKSMITH, 70, 80),
            (BuildingType.TOWN_HALL, 100, 120),  # Core building - every town has a town hall
            (BuildingType.LOOTBOX_SHOP, 85, 95),  # The predatory shop - in EVERY town!
        ]
        
        # Optional buildings
        optional_buildings = [
            (BuildingType.MARKET, 90, 80),
            (BuildingType.BANK, 80, 90),
            (BuildingType.TAVERN, 75, 95),
            (BuildingType.GUARD_TOWER, 60, 100),
            (BuildingType.TEMPLE, 85, 110),
        ]
        
        # Add houses
        for _ in range(3):
            optional_buildings.append((BuildingType.HOUSE, random.randint(50, 70), random.randint(60, 80)))
        
        # Place buildings in a grid-like pattern around town center
        buildings_to_place = core_buildings + optional_buildings[:num_buildings - len(core_buildings)]
        
        # Arrange in circular pattern
        angle_step = (2 * 3.14159) / len(buildings_to_place)
        radius_offset = self.radius * 0.6
        
        for i, (building_type, width, height) in enumerate(buildings_to_place):
            angle = i * angle_step
            
            # Try multiple positions if buildings overlap
            placed = False
            for attempt in range(10):
                if attempt == 0:
                    random_factor = 0.5 + random.random() * 0.5
                else:
                    random_factor = 0.3 + random.random() * 0.7  # Wider range for retries
                
                x = self.center_x + int(radius_offset * random_factor * pygame.math.Vector2(1, 0).rotate_rad(angle).x) - width // 2
                y = self.center_y + int(radius_offset * random_factor * pygame.math.Vector2(0, 1).rotate_rad(angle).y) - height // 2
                
                # Check collision with existing buildings
                new_rect = pygame.Rect(x, y, width, height)
                collision = False
                for existing in self.buildings:
                    # Add padding between buildings
                    padded_rect = existing.rect.inflate(20, 20)
                    if new_rect.colliderect(padded_rect):
                        collision = True
                        break
                
                if not collision:
                    building = Building(building_type, x, y, width, height)
                    self.buildings.append(building)
                    placed = True
                    break
            
            # If couldn't place after 10 attempts, skip this building
            if not placed:
                pass  # Could log this for debugging
    
    def get_building_by_type(self, building_type):
        """Get first building of specific type"""
        for building in self.buildings:
            if building.type == building_type:
                return building
        return None
    
    def is_in_town(self, x, y):
        """Check if position is within town boundaries"""
        return self.zone_rect.collidepoint(x, y)
    
    def get_nearest_building(self, x, y):
        """Get the nearest building to a position"""
        nearest = None
        min_dist = float('inf')
        
        for building in self.buildings:
            dist = ((x - building.door_x) ** 2 + (y - building.door_y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest = building
        
        return nearest, min_dist
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the town (buildings and zone)"""
        # Performance: Check if town is visible on screen first
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        zone_screen_x = self.zone_rect.x - camera_x
        zone_screen_y = self.zone_rect.y - camera_y
        
        # Skip if town is completely off-screen
        if (zone_screen_x + self.zone_width < -100 or zone_screen_x > screen_width + 100 or
            zone_screen_y + self.zone_height < -100 or zone_screen_y > screen_height + 100):
            return
        
        # Draw town zone background (use pre-created surface)
        screen.blit(self._zone_surface, (zone_screen_x, zone_screen_y))
        
        # Town boundary
        pygame.draw.rect(screen, (139, 90, 43), 
                        (zone_screen_x, zone_screen_y, self.zone_width, self.zone_height), 3)
        
        # Draw town name sign at entrance (create once, reuse)
        if not self._name_sign_created:
            font = _get_town_font()
            name_text = font.render(self.name, True, (255, 215, 0))
            self._name_sign = pygame.Surface((name_text.get_width() + 20, name_text.get_height() + 10))
            self._name_sign.set_alpha(220)
            self._name_sign.fill((50, 30, 10))
            self._name_sign.blit(name_text, (10, 5))
            pygame.draw.rect(self._name_sign, (139, 90, 43), 
                           (0, 0, self._name_sign.get_width(), self._name_sign.get_height()), 2)
            self._name_sign_created = True
        
        sign_x = zone_screen_x + (self.zone_width - self._name_sign.get_width()) // 2
        sign_y = zone_screen_y - 50
        screen.blit(self._name_sign, (sign_x, sign_y))
        
        # Draw all buildings
        for building in self.buildings:
            building.draw(screen, camera_x, camera_y)


class TownManager:
    """Manages all towns in the game world"""
    
    def __init__(self):
        self.towns = []
    
    def create_town(self, name, center_x, center_y, size="medium"):
        """Create a new town"""
        town = Town(name, center_x, center_y, size)
        self.towns.append(town)
        return town
    
    def get_town_at_position(self, x, y):
        """Get town at specific position (if any)"""
        for town in self.towns:
            if town.is_in_town(x, y):
                return town
        return None
    
    def get_nearest_town(self, x, y):
        """Get nearest town to position"""
        if not self.towns:
            return None, float('inf')
        
        nearest = None
        min_dist = float('inf')
        
        for town in self.towns:
            dist = ((x - town.center_x) ** 2 + (y - town.center_y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest = town
        
        return nearest, min_dist
    
    def draw_all(self, screen, camera_x, camera_y):
        """Draw all towns"""
        for town in self.towns:
            town.draw(screen, camera_x, camera_y)
    
    def retrofit_lootbox_shops(self):
        """Add loot box shop to towns that don't have one (for existing saves)"""
        for town in self.towns:
            # Check if town already has a loot box shop
            has_lootbox_shop = any(b.type == BuildingType.LOOTBOX_SHOP for b in town.buildings)
            
            if not has_lootbox_shop:
                import random
                
                # Find a good spot for the new building
                width, height = 85, 95
                max_attempts = 50
                placed = False
                
                for attempt in range(max_attempts):
                    # Try to place near the edge of town
                    angle = random.uniform(0, 2 * 3.14159)
                    radius = town.radius * random.uniform(0.5, 0.8)
                    
                    x = int(town.center_x + radius * (1 if attempt % 2 == 0 else -1) * abs(pygame.math.Vector2(1, 0).rotate_rad(angle).x)) - width // 2
                    y = int(town.center_y + radius * (1 if attempt % 2 == 0 else -1) * abs(pygame.math.Vector2(0, 1).rotate_rad(angle).y)) - height // 2
                    
                    # Check collision with existing buildings
                    new_rect = pygame.Rect(x, y, width, height)
                    collision = False
                    for existing in town.buildings:
                        padded_rect = existing.rect.inflate(30, 30)  # Extra padding for hot pink monstrosity
                        if new_rect.colliderect(padded_rect):
                            collision = True
                            break
                    
                    if not collision:
                        building = Building(BuildingType.LOOTBOX_SHOP, x, y, width, height)
                        town.buildings.append(building)
                        placed = True
                        print(f"[RETROFIT] Added MaXxS Silicon Dioxide Shop to {town.name} at ({x}, {y})")
                        break
                
                if not placed:
                    # Fallback: place it on the outskirts even if it overlaps slightly
                    angle = random.uniform(0, 2 * 3.14159)
                    radius = town.radius * 0.75
                    x = int(town.center_x + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).x) - width // 2
                    y = int(town.center_y + radius * pygame.math.Vector2(0, 1).rotate_rad(angle).y) - height // 2
                    building = Building(BuildingType.LOOTBOX_SHOP, x, y, width, height)
                    town.buildings.append(building)
                    print(f"[RETROFIT] Forcefully added MaXxS Silicon Dioxide Shop to {town.name} (fallback placement)")
