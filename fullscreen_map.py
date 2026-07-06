"""
Full-screen map system with fog of war, terrain colors, and POI markers
Opens with Tab key, pauses game, shows entire explored world
"""
import pygame
import math


class FullscreenMap:
    """Full-screen map overlay showing entire world with zoom"""
    
    def __init__(self, tile_size=32):
        self.active = False
        self.tile_size = tile_size
        
        # World center (where POIs are located)
        self.world_center_x = 0
        self.world_center_y = 0
        
        # Zoom settings - extended range to show entire world
        self.zoom_level = 0.01
        self.zoom_levels = [0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
        self.current_zoom_idx = 1  # Start at 0.01x (fully zoomed out to see entire world)
        self.initial_zoom_calculated = False
        
        # Pan/scroll
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Terrain colors (same as minimap)
        self.terrain_colors = {
            'grass': (60, 140, 60),
            'dirt': (120, 90, 60),
            'sand': (210, 180, 140),
            'water': (50, 100, 200),
            'deep_water': (30, 70, 150),
            'stone': (100, 100, 110),
            'snow': (230, 230, 240),
            'ice': (180, 210, 230),
        }
        
        # Visual settings
        self.bg_color = (15, 15, 20)
        self.unexplored_color = (25, 25, 30)
        self.border_color = (100, 100, 150)
        
        # POI colors (larger and brighter than minimap)
        self.player_color = (255, 255, 100)
        self.town_color = (100, 200, 255)
        self.dungeon_color = (200, 100, 255)
        self.chest_color = (255, 200, 50)
        self.quest_color = (255, 255, 0)
        self.enemy_color = (255, 50, 50)
        self.npc_color = (100, 255, 100)
        
        # Legend
        self.show_legend = True
        
    def toggle(self):
        """Toggle map on/off"""
        self.active = not self.active
        # Reset to full world view when opening map
        if self.active:
            self.initial_zoom_calculated = False
            self.offset_x = 0
            self.offset_y = 0
        return self.active
    
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
        """Reset to full world view"""
        self.initial_zoom_calculated = False
        self.offset_x = 0
        self.offset_y = 0
    
    def handle_mouse_down(self, pos):
        """Handle mouse button down for dragging"""
        self.dragging = True
        self.drag_start_x = pos[0]
        self.drag_start_y = pos[1]
    
    def handle_mouse_up(self):
        """Handle mouse button up"""
        self.dragging = False
    
    def handle_mouse_motion(self, pos):
        """Handle mouse motion for panning"""
        if self.dragging:
            dx = pos[0] - self.drag_start_x
            dy = pos[1] - self.drag_start_y
            self.offset_x += dx
            self.offset_y += dy
            self.drag_start_x = pos[0]
            self.drag_start_y = pos[1]
    
    def world_to_screen(self, world_x, world_y, screen_width, screen_height, player_x, player_y):
        """Convert world coordinates to screen coordinates"""
        # Center on world center (where POIs are) instead of player
        center_x = screen_width / 2
        center_y = screen_height / 2
        
        # Calculate position relative to world center
        rel_x = (world_x - self.world_center_x) * self.zoom_level
        rel_y = (world_y - self.world_center_y) * self.zoom_level
        
        # Apply offset for panning
        screen_x = center_x + rel_x + self.offset_x
        screen_y = center_y + rel_y + self.offset_y
        
        return screen_x, screen_y
    
    def draw(self, screen, world, player, explored_tiles, entities=None, dungeon_entrances=None, 
             chests=None, quest_manager=None, towns=None):
        """Draw the full-screen map"""
        if not self.active:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Calculate initial zoom to fit entire world on first open
        if not self.initial_zoom_calculated:
            # Calculate zoom needed to fit entire world (in pixels)
            world_width_pixels = world.width  # Already in pixels from config
            world_height_pixels = world.height
            
            # Calculate zoom to fit width and height, use smaller value to ensure both fit
            zoom_width = (screen_width * 0.9) / world_width_pixels  # 0.9 for margins
            zoom_height = (screen_height * 0.9) / world_height_pixels
            needed_zoom = min(zoom_width, zoom_height)
            
            # Find closest zoom level in our list
            closest_idx = min(range(len(self.zoom_levels)), 
                            key=lambda i: abs(self.zoom_levels[i] - needed_zoom))
            self.current_zoom_idx = closest_idx
            self.zoom_level = self.zoom_levels[closest_idx]
            
            # Center view on world center (middle of world)
            self.world_center_x = world_width_pixels / 2
            self.world_center_y = world_height_pixels / 2
            
            # Reset pan offset to show centered view
            self.offset_x = 0
            self.offset_y = 0
            
            self.initial_zoom_calculated = True
        
        # Initialize world center on first use (find center of all POIs)
        if self.world_center_x == 0 and self.world_center_y == 0:
            # Use world dimensions to find POI area
            # POIs are typically near world origin, not world center where player spawns
            if towns and len(towns) > 0:
                # Calculate center of all towns
                avg_x = sum(t.center_x for t in towns) / len(towns)
                avg_y = sum(t.center_y for t in towns) / len(towns)
                self.world_center_x = avg_x
                self.world_center_y = avg_y
        
        # Create full-screen surface with slight transparency
        map_surface = pygame.Surface((screen_width, screen_height))
        map_surface.fill(self.bg_color)
        
        # Calculate visible tile range based on zoom and screen size
        tile_pixel_size = int(self.tile_size * self.zoom_level)
        if tile_pixel_size < 1:
            tile_pixel_size = 1
        
        # OPTIMIZATION: Skip detailed tile rendering if zoomed out too far
        # When each tile is less than 2 pixels, just draw a simplified world overview
        if self.zoom_level < 0.05:
            # Draw simplified world overview with major terrain features
            world_width_screen = world.width * self.zoom_level
            world_height_screen = world.height * self.zoom_level
            
            world_screen_x = screen_width / 2 - world_width_screen / 2 + self.offset_x
            world_screen_y = screen_height / 2 - world_height_screen / 2 + self.offset_y
            
            # Draw world background as grassland
            pygame.draw.rect(map_surface, (60, 140, 60), 
                           (int(world_screen_x), int(world_screen_y), 
                            int(world_width_screen), int(world_height_screen)))
            
            # Draw major water features (ocean, river, lakes) for visual interest
            tile_size = self.tile_size
            
            # Ocean region (bottom right - 1/3 of world)
            ocean_tiles_w = (world.width // 3) // tile_size
            ocean_tiles_h = (world.height // 3) // tile_size
            ocean_start_x = (world.width // tile_size - ocean_tiles_w) * tile_size
            ocean_start_y = (world.height // tile_size - ocean_tiles_h) * tile_size
            
            ocean_screen_x = world_screen_x + ocean_start_x * self.zoom_level
            ocean_screen_y = world_screen_y + ocean_start_y * self.zoom_level
            ocean_screen_w = (ocean_tiles_w * tile_size) * self.zoom_level
            ocean_screen_h = (ocean_tiles_h * tile_size) * self.zoom_level
            
            pygame.draw.rect(map_surface, (50, 100, 200),  # Water color
                           (int(ocean_screen_x), int(ocean_screen_y), 
                            int(ocean_screen_w), int(ocean_screen_h)))
            
            # Beach around ocean
            beach_start_x = ocean_start_x - tile_size * 3
            beach_start_y = ocean_start_y - tile_size * 3
            beach_width = (ocean_tiles_w * tile_size + tile_size * 6)
            beach_height = (ocean_tiles_h * tile_size + tile_size * 6)
            
            beach_screen_x = world_screen_x + beach_start_x * self.zoom_level
            beach_screen_y = world_screen_y + beach_start_y * self.zoom_level
            beach_screen_w = beach_width * self.zoom_level
            beach_screen_h = beach_height * self.zoom_level
            
            pygame.draw.rect(map_surface, (210, 180, 140),  # Sand color
                           (int(beach_screen_x), int(beach_screen_y), 
                            int(beach_screen_w), int(beach_screen_h)), 3)
            
            # River (from center to ocean)
            center_x = world.width / 2
            river_y = ocean_start_y + (ocean_tiles_h // 2) * tile_size
            river_start_x = center_x
            river_end_x = ocean_start_x
            river_screen_y = world_screen_y + river_y * self.zoom_level
            river_screen_start_x = world_screen_x + river_start_x * self.zoom_level
            river_screen_end_x = world_screen_x + river_end_x * self.zoom_level
            river_width = max(2, int(tile_size * 2 * self.zoom_level))
            
            pygame.draw.line(map_surface, (50, 100, 200),  # Water color
                           (int(river_screen_start_x), int(river_screen_y)),
                           (int(river_screen_end_x), int(river_screen_y)), river_width)
            
            # Lakes (3 lakes near river)
            for i in range(3):
                lake_x = ocean_start_x - (i+2)*tile_size*8
                lake_y = river_y + (i-1)*tile_size*12
                lake_radius_x = 4 * tile_size
                lake_radius_y = 3 * tile_size
                
                lake_screen_x = world_screen_x + lake_x * self.zoom_level
                lake_screen_y = world_screen_y + lake_y * self.zoom_level
                lake_screen_w = lake_radius_x * 2 * self.zoom_level
                lake_screen_h = lake_radius_y * 2 * self.zoom_level
                
                if lake_screen_w > 2 and lake_screen_h > 2:
                    pygame.draw.ellipse(map_surface, (50, 100, 200),  # Water color
                                      (int(lake_screen_x - lake_screen_w/2), 
                                       int(lake_screen_y - lake_screen_h/2),
                                       int(lake_screen_w), int(lake_screen_h)))
            
            # Draw border around world
            pygame.draw.rect(map_surface, self.border_color, 
                           (int(world_screen_x), int(world_screen_y), 
                            int(world_width_screen), int(world_height_screen)), 2)
        else:
            # Normal detailed tile rendering for closer zoom levels
            # Calculate the world position we're viewing (accounting for pan offset)
            # Offset moves the view in screen space, so we need to convert back to world space
            view_center_x = self.world_center_x - (self.offset_x / self.zoom_level)
            view_center_y = self.world_center_y - (self.offset_y / self.zoom_level)
            
            # Center tile position (where we're looking at on the map)
            center_tile_x = int(view_center_x // self.tile_size)
            center_tile_y = int(view_center_y // self.tile_size)
            
            # Calculate how many tiles fit on screen (with safety limit)
            tiles_wide = min(int(screen_width / tile_pixel_size) + 4, 200)  # Cap at 200 tiles wide
            tiles_high = min(int(screen_height / tile_pixel_size) + 4, 200)  # Cap at 200 tiles high
            
            # Draw terrain tiles
            for dy in range(-tiles_high, tiles_high):
                for dx in range(-tiles_wide, tiles_wide):
                    tile_x = center_tile_x + dx
                    tile_y = center_tile_y + dy
                    
                    # Check bounds
                    if tile_x < 0 or tile_y < 0 or tile_x >= world.width or tile_y >= world.height:
                        continue
                    
                    # Calculate screen position
                    world_x = tile_x * self.tile_size + self.tile_size / 2
                    world_y = tile_y * self.tile_size + self.tile_size / 2
                    screen_x, screen_y = self.world_to_screen(world_x, world_y, screen_width, screen_height, player.x, player.y)
                    
                    # Check if on screen
                    if -tile_pixel_size <= screen_x <= screen_width + tile_pixel_size and \
                       -tile_pixel_size <= screen_y <= screen_height + tile_pixel_size:
                        
                        # Show all terrain (no fog of war)
                        tile = world.get_tile(tile_x, tile_y)
                        tile_color = (60, 140, 60)  # Default grass green
                        
                        if tile and hasattr(tile, 'layers') and 'ground' in tile.layers:
                            terrain_type = tile.layers['ground']
                            tile_color = self.terrain_colors.get(terrain_type, (60, 140, 60))
                        
                        pygame.draw.rect(map_surface, tile_color,
                                       (int(screen_x - tile_pixel_size/2), int(screen_y - tile_pixel_size/2),
                                        tile_pixel_size, tile_pixel_size))
        
        # Draw POI markers (larger than minimap)
        # Scale markers appropriately - larger when zoomed out so they're visible
        if self.zoom_level < 0.1:
            # Very zoomed out - use large fixed-size markers
            marker_base_size = 20
        else:
            # Normal zoom - scale with zoom level
            marker_base_size = max(12, int(24 * self.zoom_level))
        
        # Draw towns
        if towns:
            for town in towns:
                screen_x, screen_y = self.world_to_screen(town.center_x, town.center_y, screen_width, screen_height, player.x, player.y)
                
                # Expanded boundary check to catch partially visible POIs
                margin = 100
                if -margin <= screen_x <= screen_width + margin and -margin <= screen_y <= screen_height + margin:
                    # Draw town icon (larger house) - ensure minimum size
                    size = max(16, marker_base_size * 2)
                    pygame.draw.rect(map_surface, self.town_color,
                                   (int(screen_x - size/2), int(screen_y - size/2), size, size))
                    pygame.draw.rect(map_surface, (150, 220, 255),
                                   (int(screen_x - size/2), int(screen_y - size/2), size, size), 2)
                    
                    # Draw town name (show even at low zoom)
                    if self.zoom_level >= 0.25:
                        font = pygame.font.SysFont(None, max(14, int(18 * self.zoom_level)))
                        text = font.render(town.name, True, (200, 220, 255))
                        map_surface.blit(text, (int(screen_x - text.get_width()/2), int(screen_y + size/2 + 4)))
        
        # Draw dungeons
        if dungeon_entrances:
            for entrance_x, entrance_y in dungeon_entrances:
                screen_x, screen_y = self.world_to_screen(entrance_x, entrance_y, screen_width, screen_height, player.x, player.y)
                
                # Expanded boundary check
                margin = 100
                if -margin <= screen_x <= screen_width + margin and -margin <= screen_y <= screen_height + margin:
                    dungeon_size = max(10, marker_base_size)
                    pygame.draw.circle(map_surface, self.dungeon_color, (int(screen_x), int(screen_y)), dungeon_size)
                    pygame.draw.circle(map_surface, (255, 255, 255), (int(screen_x), int(screen_y)), dungeon_size, 2)
        
        # Draw chests (unopened only)
        if chests:
            for chest in chests:
                if not chest.opened:
                    screen_x, screen_y = self.world_to_screen(chest.x, chest.y, screen_width, screen_height, player.x, player.y)
                    
                    # Expanded boundary check
                    margin = 100
                    if -margin <= screen_x <= screen_width + margin and -margin <= screen_y <= screen_height + margin:
                        size = max(8, marker_base_size)
                        pygame.draw.rect(map_surface, self.chest_color,
                                       (int(screen_x - size/2), int(screen_y - size/2), size, size))
                        pygame.draw.rect(map_surface, (255, 255, 255),
                                       (int(screen_x - size/2), int(screen_y - size/2), size, size), 2)
        
        # Draw quest objectives
        if quest_manager:
            from quest_system import ObjectiveType, QuestState
            
            for quest in quest_manager.get_active_quests():
                if quest.state != QuestState.ACTIVE:
                    continue
                
                for obj in quest.objectives:
                    if obj.completed:
                        continue
                    
                    if obj.type == ObjectiveType.REACH and obj.location:
                        obj_x, obj_y = obj.location
                        screen_x, screen_y = self.world_to_screen(obj_x, obj_y, screen_width, screen_height, player.x, player.y)
                        
                        # Expanded boundary check
                        margin = 100
                        if -margin <= screen_x <= screen_width + margin and -margin <= screen_y <= screen_height + margin:
                            pygame.draw.circle(map_surface, self.quest_color, (int(screen_x), int(screen_y)), marker_base_size)
                            pygame.draw.circle(map_surface, (0, 0, 0), (int(screen_x), int(screen_y)), marker_base_size, 2)
        
        # Draw player (show indicator if off-screen, or full marker if on-screen)
        player_screen_x, player_screen_y = self.world_to_screen(player.x, player.y, screen_width, screen_height, player.x, player.y)
        
        # Check if player is on screen
        player_on_screen = 0 <= player_screen_x <= screen_width and 0 <= player_screen_y <= screen_height
        
        if player_on_screen:
            # Draw player direction arrow (on screen)
            arrow_size = max(16, marker_base_size * 2)
            
            # Get player direction
            if hasattr(player, 'facing_direction'):
                direction = player.facing_direction
            else:
                direction = 'down'
            
            # Direction angle mapping
            angle_map = {
                'up': -90, 'down': 90, 'left': 180, 'right': 0,
                'up-left': -135, 'up-right': -45, 'down-left': 135, 'down-right': 45
            }
            angle = math.radians(angle_map.get(direction, 0))
            
            # Calculate arrow points
            tip_x = player_screen_x + arrow_size * math.cos(angle)
            tip_y = player_screen_y + arrow_size * math.sin(angle)
            
            left_angle = angle + math.radians(140)
            right_angle = angle - math.radians(140)
            
            left_x = player_screen_x + arrow_size * 0.6 * math.cos(left_angle)
            left_y = player_screen_y + arrow_size * 0.6 * math.sin(left_angle)
            
            right_x = player_screen_x + arrow_size * 0.6 * math.cos(right_angle)
            right_y = player_screen_y + arrow_size * 0.6 * math.sin(right_angle)
            
            # Draw arrow
            pygame.draw.polygon(map_surface, self.player_color,
                              [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])
            pygame.draw.polygon(map_surface, (255, 255, 255),
                              [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)], 2)
        else:
            # Player is off-screen - draw indicator on edge
            # Calculate direction to player
            dx = player_screen_x - screen_width / 2
            dy = player_screen_y - screen_height / 2
            
            # Normalize and find edge intersection
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                # Calculate edge position
                edge_padding = 40
                if abs(dx) / screen_width > abs(dy) / screen_height:
                    # Hit left or right edge
                    if dx > 0:
                        edge_x = screen_width - edge_padding
                        edge_y = screen_height / 2 + (dy / abs(dx)) * (screen_width / 2 - edge_padding)
                    else:
                        edge_x = edge_padding
                        edge_y = screen_height / 2 - (dy / abs(dx)) * (screen_width / 2 - edge_padding)
                else:
                    # Hit top or bottom edge  
                    if dy > 0:
                        edge_y = screen_height - edge_padding
                        edge_x = screen_width / 2 + (dx / abs(dy)) * (screen_height / 2 - edge_padding)
                    else:
                        edge_y = edge_padding
                        edge_x = screen_width / 2 - (dx / abs(dy)) * (screen_height / 2 - edge_padding)
                
                # Draw arrow pointing to player
                arrow_angle = math.atan2(dy, dx)
                arrow_size = 12
                tip_x = edge_x + arrow_size * math.cos(arrow_angle)
                tip_y = edge_y + arrow_size * math.sin(arrow_angle)
                
                left_angle = arrow_angle + math.radians(140)
                right_angle = arrow_angle - math.radians(140)
                
                left_x = edge_x + arrow_size * 0.6 * math.cos(left_angle)
                left_y = edge_y + arrow_size * 0.6 * math.sin(left_angle)
                
                right_x = edge_x + arrow_size * 0.6 * math.cos(right_angle)
                right_y = edge_y + arrow_size * 0.6 * math.sin(right_angle)
                
                # Draw off-screen indicator
                pygame.draw.polygon(map_surface, self.player_color,
                                  [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])
                pygame.draw.polygon(map_surface, (255, 255, 255),
                                  [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)], 2)
        
        # Draw legend
        if self.show_legend:
            self._draw_legend(map_surface, screen_width, screen_height)
        
        # Draw title bar
        self._draw_title(map_surface, screen_width)
        
        # Draw controls hint
        self._draw_controls(map_surface, screen_width, screen_height)
        
        # Blit to screen
        screen.blit(map_surface, (0, 0))
    
    def _draw_legend(self, surface, screen_width, screen_height):
        """Draw legend showing what each icon means"""
        legend_x = 20
        legend_y = 80
        line_height = 30
        
        # Background
        legend_items = [
            ("Player", self.player_color, "triangle"),
            ("Town", self.town_color, "square"),
            ("Dungeon", self.dungeon_color, "circle"),
            ("Chest", self.chest_color, "square"),
            ("Quest", self.quest_color, "circle"),
        ]
        
        legend_height = len(legend_items) * line_height + 40
        legend_bg = pygame.Surface((200, legend_height), pygame.SRCALPHA)
        pygame.draw.rect(legend_bg, (20, 20, 30, 220), (0, 0, 200, legend_height), border_radius=8)
        pygame.draw.rect(legend_bg, (100, 100, 150), (0, 0, 200, legend_height), 2, border_radius=8)
        surface.blit(legend_bg, (legend_x, legend_y))
        
        # Title
        font_title = pygame.font.SysFont(None, 24, bold=True)
        title_text = font_title.render("Legend", True, (255, 255, 255))
        surface.blit(title_text, (legend_x + 10, legend_y + 10))
        
        # Items
        font = pygame.font.SysFont(None, 20)
        for i, (label, color, shape) in enumerate(legend_items):
            y = legend_y + 40 + i * line_height
            
            # Draw icon
            icon_x = legend_x + 20
            icon_y = y + 10
            
            if shape == "circle":
                pygame.draw.circle(surface, color, (icon_x, icon_y), 8)
                pygame.draw.circle(surface, (255, 255, 255), (icon_x, icon_y), 8, 1)
            elif shape == "square":
                pygame.draw.rect(surface, color, (icon_x - 8, icon_y - 8, 16, 16))
                pygame.draw.rect(surface, (255, 255, 255), (icon_x - 8, icon_y - 8, 16, 16), 1)
            elif shape == "triangle":
                points = [(icon_x, icon_y - 10), (icon_x - 8, icon_y + 6), (icon_x + 8, icon_y + 6)]
                pygame.draw.polygon(surface, color, points)
                pygame.draw.polygon(surface, (255, 255, 255), points, 1)
            
            # Draw label
            text = font.render(label, True, (220, 220, 220))
            surface.blit(text, (icon_x + 25, icon_y - 8))
    
    def _draw_title(self, surface, screen_width):
        """Draw title bar at top"""
        title_bg = pygame.Surface((screen_width, 60), pygame.SRCALPHA)
        pygame.draw.rect(title_bg, (20, 20, 30, 220), (0, 0, screen_width, 60))
        pygame.draw.line(title_bg, (100, 100, 150), (0, 59), (screen_width, 59), 2)
        surface.blit(title_bg, (0, 0))
        
        # Title text
        font = pygame.font.SysFont(None, 36, bold=True)
        title = font.render("World Map", True, (255, 255, 255))
        surface.blit(title, (screen_width // 2 - title.get_width() // 2, 15))
        
        # Zoom level
        zoom_font = pygame.font.SysFont(None, 24)
        zoom_text = zoom_font.render(f"Zoom: {self.zoom_level:.2f}x", True, (200, 200, 200))
        surface.blit(zoom_text, (screen_width - zoom_text.get_width() - 20, 20))
    
    def _draw_controls(self, surface, screen_width, screen_height):
        """Draw controls hint at bottom"""
        controls_y = screen_height - 50
        
        controls_bg = pygame.Surface((screen_width, 50), pygame.SRCALPHA)
        pygame.draw.rect(controls_bg, (20, 20, 30, 220), (0, 0, screen_width, 50))
        pygame.draw.line(controls_bg, (100, 100, 150), (0, 0), (screen_width, 0), 2)
        surface.blit(controls_bg, (0, controls_y))
        
        # Controls text
        font = pygame.font.SysFont(None, 22)
        controls = "[Tab/ESC] Close  |  [+/-] Zoom  |  [0] Full World View  |  [Mouse Drag] Pan"
        text = font.render(controls, True, (200, 200, 200))
        surface.blit(text, (screen_width // 2 - text.get_width() // 2, controls_y + 15))
