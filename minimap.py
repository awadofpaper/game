import pygame
import math

class Minimap:
    """Advanced minimap system with zoom, fog of war, and POI markers"""
    
    def __init__(self, size=200, position='top-right'):
        self.size = size  # Minimap dimensions (square)
        self.position = position  # 'top-right', 'top-left', 'bottom-right', 'bottom-left'
        self.zoom_level = 1.0  # Default zoom (1.0 = normal, 2.0 = zoomed in, 0.5 = zoomed out)
        self.zoom_levels = [0.5, 1.0, 1.5, 2.0, 3.0]
        self.current_zoom_idx = 1  # Start at 1.0x zoom
        
        self.enabled = True
        self.show_grid = False  # Disable grid by default to show terrain colors better
        self.show_enemies = True
        self.show_npcs = True
        self.show_poi = True  # Points of interest (dungeons, chests, etc)
        
        # Fog of war - track explored areas
        self.explored_tiles = set()  # Set of (tile_x, tile_y) tuples
        self.fog_of_war_enabled = True
        self.exploration_radius = 15  # Tiles around player that are revealed
        
        # Visual settings
        self.bg_color = (20, 20, 30, 200)
        self.border_color = (100, 100, 150, 255)
        self.player_color = (255, 255, 100)
        self.enemy_color = (255, 50, 50)
        self.npc_color = (100, 255, 100)
        self.dungeon_color = (200, 100, 255)
        self.chest_color = (255, 200, 50)
        self.town_color = (100, 200, 255)  # Light blue for towns
        self.town_border_color = (150, 220, 255)
        self.unexplored_color = (40, 40, 50)
        self.explored_color = (80, 80, 100)
        self.grid_color = (60, 60, 80, 100)
        
        # Terrain colors for minimap
        self.terrain_colors = {
            'grass': (60, 140, 60),      # Green for grass/land
            'dirt': (120, 90, 60),        # Brown for dirt
            'sand': (210, 180, 140),      # Tan for sand
            'water': (50, 100, 200),      # Blue for water
            'deep_water': (30, 70, 150),  # Darker blue for deep water
            'stone': (100, 100, 110),     # Gray for stone
            'snow': (230, 230, 240),      # White for snow
            'ice': (180, 210, 230),       # Light blue for ice
        }
        
        # Object colors for minimap overlay
        self.object_colors = {
            'tree': (40, 90, 40),         # Dark green for trees
            'bush': (70, 110, 50),        # Medium green for bushes
            'rock': (90, 90, 95),         # Gray for rocks
            'rock_group': (80, 80, 90),   # Slightly darker gray for rock groups
        }
        
        # Tile size in world units
        self.tile_size = 32
        
        # Rotation (for directional indicator)
        self.show_direction = True
        
    def toggle(self):
        """Toggle minimap on/off"""
        self.enabled = not self.enabled
        
    def zoom_in(self):
        """Increase zoom level"""
        if self.current_zoom_idx < len(self.zoom_levels) - 1:
            self.current_zoom_idx += 1
            self.zoom_level = self.zoom_levels[self.current_zoom_idx]
            
    def zoom_out(self):
        """Decrease zoom level"""
        if self.current_zoom_idx > 0:
            self.current_zoom_idx -= 1
            self.zoom_level = self.zoom_levels[self.current_zoom_idx]
            
    def reset_zoom(self):
        """Reset to default zoom"""
        self.current_zoom_idx = 1
        self.zoom_level = self.zoom_levels[self.current_zoom_idx]
        
    def update_explored_area(self, player_x, player_y):
        """Update fog of war based on player position"""
        if not self.fog_of_war_enabled:
            return
            
        # Convert player position to tile coordinates
        player_tile_x = int(player_x // self.tile_size)
        player_tile_y = int(player_y // self.tile_size)
        
        # Reveal tiles in radius around player
        for dx in range(-self.exploration_radius, self.exploration_radius + 1):
            for dy in range(-self.exploration_radius, self.exploration_radius + 1):
                # Circular exploration radius
                if dx * dx + dy * dy <= self.exploration_radius * self.exploration_radius:
                    tile_x = player_tile_x + dx
                    tile_y = player_tile_y + dy
                    self.explored_tiles.add((tile_x, tile_y))
                    
    def get_position_on_screen(self, screen_width, screen_height):
        """Calculate minimap position based on settings"""
        padding = 10
        
        if self.position == 'top-right':
            x = screen_width - self.size - padding
            y = padding
        elif self.position == 'top-left':
            x = padding
            y = padding
        elif self.position == 'bottom-right':
            x = screen_width - self.size - padding
            y = screen_height - self.size - padding
        elif self.position == 'bottom-left':
            x = padding
            y = screen_height - self.size - padding
        else:
            x = screen_width - self.size - padding
            y = padding
            
        return x, y
        
    def world_to_minimap(self, world_x, world_y, player_x, player_y):
        """Convert world coordinates to minimap coordinates"""
        # Calculate relative position to player
        rel_x = world_x - player_x
        rel_y = world_y - player_y
        
        # Apply zoom
        rel_x *= self.zoom_level
        rel_y *= self.zoom_level
        
        # Scale to minimap size (world units to minimap pixels)
        scale = self.size / (self.tile_size * 20)  # Show ~20 tiles at 1.0x zoom
        
        minimap_x = self.size / 2 + rel_x * scale
        minimap_y = self.size / 2 + rel_y * scale
        
        return minimap_x, minimap_y
        
    def is_visible_on_minimap(self, minimap_x, minimap_y):
        """Check if coordinates are within minimap bounds"""
        return 0 <= minimap_x <= self.size and 0 <= minimap_y <= self.size
        
    def draw(self, screen, player, entities, dungeon_entrances=None, chests=None, quest_manager=None, towns=None, world=None, enemies=None):
        """Draw the minimap"""
        if not self.enabled:
            return
            
        screen_width, screen_height = screen.get_size()
        map_x, map_y = self.get_position_on_screen(screen_width, screen_height)
        
        # Update explored area
        self.update_explored_area(player.x, player.y)
        
        # Create minimap surface with alpha
        minimap_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(minimap_surface, self.bg_color, (0, 0, self.size, self.size), border_radius=8)
        
        # Draw explored area tiles (fog of war)
        if self.fog_of_war_enabled:
            player_tile_x = int(player.x // self.tile_size)
            player_tile_y = int(player.y // self.tile_size)
            
            # Calculate how many tiles to show based on zoom
            tiles_visible = int(10 / self.zoom_level)
            
            for dx in range(-tiles_visible, tiles_visible + 1):
                for dy in range(-tiles_visible, tiles_visible + 1):
                    tile_x = player_tile_x + dx
                    tile_y = player_tile_y + dy
                    
                    # Convert tile to minimap coordinates
                    world_x = tile_x * self.tile_size + self.tile_size / 2
                    world_y = tile_y * self.tile_size + self.tile_size / 2
                    minimap_x, minimap_y = self.world_to_minimap(world_x, world_y, player.x, player.y)
                    
                    if self.is_visible_on_minimap(minimap_x, minimap_y):
                        tile_size_on_map = max(2, int(self.tile_size * self.size / (self.tile_size * 20) * self.zoom_level))
                        
                        if (tile_x, tile_y) in self.explored_tiles:
                            # Explored tile - show terrain color
                            tile_color = (60, 140, 60)  # Default to grass green
                            
                            # Get terrain type from world if available
                            if world:
                                # Convert tile coordinates to world pixel coordinates
                                world_tile_x = tile_x * self.tile_size
                                world_tile_y = tile_y * self.tile_size
                                
                                # Get tile from world using pixel coordinates
                                tile = world.get_tile(world_tile_x, world_tile_y)
                                if tile and hasattr(tile, 'layers') and 'ground' in tile.layers:
                                    terrain_type = tile.layers['ground']
                                    # Map terrain type to color
                                    tile_color = self.terrain_colors.get(terrain_type, (60, 140, 60))  # Default to grass green
                            
                            # Draw terrain
                            pygame.draw.rect(minimap_surface, tile_color,
                                           (minimap_x - tile_size_on_map/2, minimap_y - tile_size_on_map/2,
                                            tile_size_on_map, tile_size_on_map))
                            
                            # Draw objects on top of terrain (trees, rocks, bushes) if world available
                            if world:
                                world_tile_x = tile_x * self.tile_size
                                world_tile_y = tile_y * self.tile_size
                                tile = world.get_tile(world_tile_x, world_tile_y)
                                if tile and hasattr(tile, 'layers') and 'object' in tile.layers and tile.layers['object']:
                                    obj_type = tile.layers['object']
                                    if obj_type in self.object_colors:
                                        obj_color = self.object_colors[obj_type]
                                        # Draw slightly smaller rect for object overlay
                                        obj_size = max(1, int(tile_size_on_map * 0.7))
                                        pygame.draw.rect(minimap_surface, obj_color,
                                                       (minimap_x - obj_size/2, minimap_y - obj_size/2,
                                                        obj_size, obj_size))
                        else:
                            # Unexplored tile (fog of war)
                            pygame.draw.rect(minimap_surface, self.unexplored_color,
                                           (minimap_x - tile_size_on_map/2, minimap_y - tile_size_on_map/2,
                                            tile_size_on_map, tile_size_on_map))
        
        # Draw grid
        if self.show_grid:
            grid_spacing = max(10, int(self.size / 10))
            for i in range(0, self.size, grid_spacing):
                pygame.draw.line(minimap_surface, self.grid_color, (i, 0), (i, self.size), 1)
                pygame.draw.line(minimap_surface, self.grid_color, (0, i), (self.size, i), 1)
        
        # Draw POI markers (dungeons, chests, etc)
        if self.show_poi:
            # Draw dungeon entrances as small squares
            if dungeon_entrances:
                for entrance_x, entrance_y in dungeon_entrances:
                    minimap_x, minimap_y = self.world_to_minimap(entrance_x, entrance_y, player.x, player.y)
                    if self.is_visible_on_minimap(minimap_x, minimap_y):
                        # Check if explored
                        tile_x = int(entrance_x // self.tile_size)
                        tile_y = int(entrance_y // self.tile_size)
                        if not self.fog_of_war_enabled or (tile_x, tile_y) in self.explored_tiles:
                            # Draw dungeon icon as filled square (same color as main map)
                            square_size = 6
                            pygame.draw.rect(minimap_surface, self.dungeon_color, 
                                           (int(minimap_x) - square_size//2, int(minimap_y) - square_size//2, 
                                            square_size, square_size))
                            pygame.draw.rect(minimap_surface, (255, 255, 255), 
                                           (int(minimap_x) - square_size//2, int(minimap_y) - square_size//2, 
                                            square_size, square_size), 1)
            
            # Draw chests
            if chests:
                for chest in chests:
                    chest_x, chest_y = chest.x, chest.y
                    minimap_x, minimap_y = self.world_to_minimap(chest_x, chest_y, player.x, player.y)
                    if self.is_visible_on_minimap(minimap_x, minimap_y):
                        # Check if explored
                        tile_x = int(chest_x // self.tile_size)
                        tile_y = int(chest_y // self.tile_size)
                        if not self.fog_of_war_enabled or (tile_x, tile_y) in self.explored_tiles:
                            # Draw chest icon (square)
                            if not chest.opened:
                                pygame.draw.rect(minimap_surface, self.chest_color,
                                               (int(minimap_x) - 3, int(minimap_y) - 3, 6, 6))
                                pygame.draw.rect(minimap_surface, (255, 255, 255),
                                               (int(minimap_x) - 3, int(minimap_y) - 3, 6, 6), 1)
        
        # Draw town markers as small squares (same color as main map)
        if self.show_poi and towns:
            for town in towns:
                # Use town's center position
                town_center_x = town.center_x
                town_center_y = town.center_y
                
                minimap_x, minimap_y = self.world_to_minimap(town_center_x, town_center_y, player.x, player.y)
                
                if self.is_visible_on_minimap(minimap_x, minimap_y):
                    # Check if explored
                    tile_x = int(town_center_x // self.tile_size)
                    tile_y = int(town_center_y // self.tile_size)
                    if not self.fog_of_war_enabled or (tile_x, tile_y) in self.explored_tiles:
                        # Draw town as filled square (same color as main map)
                        square_size = 7
                        pygame.draw.rect(minimap_surface, self.town_color,
                                       (int(minimap_x) - square_size//2, 
                                        int(minimap_y) - square_size//2,
                                        square_size, square_size))
                        pygame.draw.rect(minimap_surface, self.town_border_color,
                                       (int(minimap_x) - square_size//2, 
                                        int(minimap_y) - square_size//2,
                                        square_size, square_size), 1)
                        
                        # Town name (if zoomed in enough)
                        if self.zoom_level >= 1.5:
                            name_font = pygame.font.SysFont(None, 12)
                            name_text = name_font.render(town.name[:15], True, (200, 220, 255))
                            text_x = int(minimap_x) - name_text.get_width() // 2
                            text_y = int(minimap_y) + square_size//2 + 2
                            
                            # Text background for readability
                            text_bg = pygame.Surface((name_text.get_width() + 4, name_text.get_height()), pygame.SRCALPHA)
                            text_bg.fill((20, 20, 40, 180))
                            minimap_surface.blit(text_bg, (text_x - 2, text_y))
                            minimap_surface.blit(name_text, (text_x, text_y))
        
        # Draw quest objectives and markers
        if self.show_poi and quest_manager:
            from quest_system import ObjectiveType, QuestState
            
            for quest in quest_manager.get_active_quests():
                if quest.state != QuestState.ACTIVE:
                    continue
                
                for obj in quest.objectives:
                    if obj.completed:
                        continue
                    
                    # Draw location-based objectives
                    if obj.type == ObjectiveType.REACH and obj.location:
                        obj_x, obj_y = obj.location
                        minimap_x, minimap_y = self.world_to_minimap(obj_x, obj_y, player.x, player.y)
                        
                        if self.is_visible_on_minimap(minimap_x, minimap_y):
                            # Check if explored
                            tile_x = int(obj_x // self.tile_size)
                            tile_y = int(obj_y // self.tile_size)
                            if not self.fog_of_war_enabled or (tile_x, tile_y) in self.explored_tiles:
                                # Draw quest marker (exclamation mark)
                                marker_color = (255, 255, 0) if not obj.optional else (200, 200, 100)
                                pygame.draw.circle(minimap_surface, marker_color, (int(minimap_x), int(minimap_y)), 6)
                                pygame.draw.circle(minimap_surface, (255, 255, 255), (int(minimap_x), int(minimap_y)), 6, 1)
                                
                                # Draw ! symbol
                                marker_font = pygame.font.SysFont(None, 14)
                                marker_text = marker_font.render("!", True, (0, 0, 0))
                                minimap_surface.blit(marker_text, (int(minimap_x) - 3, int(minimap_y) - 6))
            
            # Draw quest givers with available quests
            available_quests = quest_manager.get_available_quests(player)
            quest_givers = set()
            for quest in available_quests:
                if quest.giver_npc_id:
                    quest_givers.add(quest.giver_npc_id)
            
            # Mark NPCs with quests (if we can find them)
            if hasattr(entities, 'npcs'):
                for npc in entities.npcs:
                    if hasattr(npc, 'id') and npc.id in quest_givers:
                        npc_x, npc_y = npc.x, npc.y
                        minimap_x, minimap_y = self.world_to_minimap(npc_x, npc_y, player.x, player.y)
                        if self.is_visible_on_minimap(minimap_x, minimap_y):
                            # Yellow ! for quest giver
                            pygame.draw.circle(minimap_surface, (255, 255, 0), (int(minimap_x), int(minimap_y)), 7)
                            pygame.draw.circle(minimap_surface, (0, 0, 0), (int(minimap_x), int(minimap_y)), 7, 1)
        
        # Draw NPCs
        if self.show_npcs and hasattr(entities, 'npcs'):
            for npc in entities.npcs:
                npc_x, npc_y = npc.x, npc.y
                minimap_x, minimap_y = self.world_to_minimap(npc_x, npc_y, player.x, player.y)
                if self.is_visible_on_minimap(minimap_x, minimap_y):
                    # Check if explored
                    tile_x = int(npc_x // self.tile_size)
                    tile_y = int(npc_y // self.tile_size)
                    if not self.fog_of_war_enabled or (tile_x, tile_y) in self.explored_tiles:
                        pygame.draw.circle(minimap_surface, self.npc_color, (int(minimap_x), int(minimap_y)), 3)
        
        # Draw enemies
        if self.show_enemies and enemies:
            for enemy in enemies:
                if hasattr(enemy, 'health') and enemy.health > 0:
                    # Enemy position is stored in enemy.rect
                    if hasattr(enemy, 'rect'):
                        enemy_x, enemy_y = enemy.rect.x, enemy.rect.y
                    else:
                        continue  # Skip if no rect attribute
                    
                    minimap_x, minimap_y = self.world_to_minimap(enemy_x, enemy_y, player.x, player.y)
                    if self.is_visible_on_minimap(minimap_x, minimap_y):
                        # Check if explored
                        tile_x = int(enemy_x // self.tile_size)
                        tile_y = int(enemy_y // self.tile_size)
                        if not self.fog_of_war_enabled or (tile_x, tile_y) in self.explored_tiles:
                            # Color based on enemy difficulty/rarity
                            color = self.enemy_color
                            if hasattr(enemy, 'rarity'):
                                if enemy.rarity == 'Rare':
                                    color = (255, 150, 50)
                                elif enemy.rarity == 'Elite':
                                    color = (255, 100, 255)
                                elif enemy.rarity == 'Legendary':
                                    color = (255, 215, 0)
                                elif enemy.rarity == 'Boss':
                                    color = (255, 0, 0)
                            
                            pygame.draw.circle(minimap_surface, color, (int(minimap_x), int(minimap_y)), 3)
        
        # Draw player (always centered)
        center_x = self.size / 2
        center_y = self.size / 2
        
        # Draw player direction indicator
        if self.show_direction:
            # Get player facing direction
            if hasattr(player, 'facing_direction'):
                direction = player.facing_direction
            else:
                direction = 'down'  # Default
            
            # Calculate direction angle
            angle_map = {
                'up': -90,
                'down': 90,
                'left': 180,
                'right': 0,
                'up-left': -135,
                'up-right': -45,
                'down-left': 135,
                'down-right': 45
            }
            angle = math.radians(angle_map.get(direction, 0))
            
            # Draw direction cone
            cone_length = 10
            cone_width = 8
            
            # Calculate cone points
            tip_x = center_x + cone_length * math.cos(angle)
            tip_y = center_y + cone_length * math.sin(angle)
            
            left_angle = angle + math.radians(150)
            right_angle = angle - math.radians(150)
            
            left_x = center_x + cone_width * math.cos(left_angle)
            left_y = center_y + cone_width * math.sin(left_angle)
            
            right_x = center_x + cone_width * math.cos(right_angle)
            right_y = center_y + cone_width * math.sin(right_angle)
            
            pygame.draw.polygon(minimap_surface, (255, 255, 150, 150),
                              [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])
        
        # Draw player marker
        pygame.draw.circle(minimap_surface, self.player_color, (int(center_x), int(center_y)), 5)
        pygame.draw.circle(minimap_surface, (255, 255, 255), (int(center_x), int(center_y)), 5, 2)
        
        # Draw border
        pygame.draw.rect(minimap_surface, self.border_color, (0, 0, self.size, self.size), 2, border_radius=8)
        
        # Draw zoom indicator
        font = pygame.font.SysFont(None, 18)
        zoom_text = font.render(f"{self.zoom_level:.1f}x", True, (255, 255, 255))
        minimap_surface.blit(zoom_text, (5, self.size - 20))
        
        # Draw compass (N/S/E/W)
        compass_font = pygame.font.SysFont(None, 16)
        
        # North
        n_text = compass_font.render("N", True, (200, 200, 255))
        minimap_surface.blit(n_text, (self.size/2 - n_text.get_width()/2, 5))
        
        # South
        s_text = compass_font.render("S", True, (200, 200, 255))
        minimap_surface.blit(s_text, (self.size/2 - s_text.get_width()/2, self.size - 18))
        
        # East
        e_text = compass_font.render("E", True, (200, 200, 255))
        minimap_surface.blit(e_text, (self.size - 15, self.size/2 - e_text.get_height()/2))
        
        # West
        w_text = compass_font.render("W", True, (200, 200, 255))
        minimap_surface.blit(w_text, (5, self.size/2 - w_text.get_height()/2))
        
        # Blit minimap to screen
        screen.blit(minimap_surface, (map_x, map_y))
        
        # Draw controls hint
        hint_font = pygame.font.SysFont(None, 14)
        hint_text = hint_font.render("[M] Toggle | [+/-] Zoom", True, (200, 200, 200))
        hint_bg = pygame.Surface((hint_text.get_width() + 8, hint_text.get_height() + 4), pygame.SRCALPHA)
        pygame.draw.rect(hint_bg, (20, 20, 30, 180), (0, 0, hint_text.get_width() + 8, hint_text.get_height() + 4), border_radius=4)
        hint_bg.blit(hint_text, (4, 2))
        screen.blit(hint_bg, (map_x, map_y + self.size + 5))
