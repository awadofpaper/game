"""
Additional Performance Optimizations
Viewport culling, sprite batching, and rendering optimizations
"""

import pygame
from typing import Dict, List, Tuple, Set
from collections import defaultdict

class ViewportCuller:
    """
    Optimizes rendering by only processing entities/tiles visible on screen.
    Reduces overhead from 10,000x10,000 world to just visible portion.
    """
    
    def __init__(self, screen_width, screen_height, tile_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        
        # Calculate visible tile range with buffer
        self.visible_tiles_x = (screen_width // tile_size) + 2  # Reduced buffer from 4 to 2
        self.visible_tiles_y = (screen_height // tile_size) + 2
        
    def get_visible_tile_range(self, player_x: int, player_y: int) -> Tuple[int, int, int, int]:
        """
        Get the range of tiles visible on screen.
        Returns: (start_x, start_y, end_x, end_y) in world coordinates
        """
        # Center camera on player
        camera_x = player_x - self.screen_width // 2
        camera_y = player_y - self.screen_height // 2
        
        # Calculate tile boundaries (aligned to tile grid)
        start_tile_x = (camera_x // self.tile_size) - 1  # Reduced buffer from 2 to 1
        start_tile_y = (camera_y // self.tile_size) - 1
        end_tile_x = start_tile_x + self.visible_tiles_x
        end_tile_y = start_tile_y + self.visible_tiles_y
        
        # Convert back to world coordinates
        start_x = start_tile_x * self.tile_size
        start_y = start_tile_y * self.tile_size
        end_x = end_tile_x * self.tile_size
        end_y = end_tile_y * self.tile_size
        
        return start_x, start_y, end_x, end_y
    
    def is_entity_visible(self, entity_x: int, entity_y: int, player_x: int, player_y: int) -> bool:
        """Check if an entity is within visible range"""
        start_x, start_y, end_x, end_y = self.get_visible_tile_range(player_x, player_y)
        return start_x <= entity_x <= end_x and start_y <= entity_y <= end_y


class SpriteCache:
    """
    Cache for pre-rendered sprites to avoid redrawing identical tiles every frame.
    Massive performance boost for repetitive terrain.
    """
    
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.cache: Dict[str, pygame.Surface] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    def get_tile_surface(self, tile_type: str, color: Tuple[int, int, int]) -> pygame.Surface:
        """
        Get cached tile surface or create new one.
        
        Args:
            tile_type: Type of tile (grass, rock, water, etc.)
            color: RGB color tuple
            
        Returns:
            Pre-rendered pygame Surface
        """
        cache_key = f"{tile_type}_{color}"
        
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        # Create new surface
        self.cache_misses += 1
        surface = pygame.Surface((self.tile_size, self.tile_size))
        surface.fill(color)
        
        # Add tile-specific details (grass blades, rock texture, etc.)
        if tile_type == 'grass':
            # Draw grass details once and cache
            pygame.draw.line(surface, (0, 120, 0), (5, 10), (5, 20), 1)
            pygame.draw.line(surface, (0, 130, 0), (15, 12), (15, 22), 1)
            pygame.draw.line(surface, (0, 110, 0), (25, 8), (25, 18), 1)
        elif tile_type == 'rock_group':
            # Rock highlights
            pygame.draw.circle(surface, (140, 140, 140), (10, 10), 5)
            pygame.draw.circle(surface, (120, 120, 120), (20, 15), 4)
        
        self.cache[cache_key] = surface
        return surface
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': hit_rate
        }
    
    def clear_cache(self):
        """Clear sprite cache (useful when changing graphics settings)"""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0


class BatchRenderer:
    """
    Batches similar draw calls to reduce overhead.
    Groups tiles by type and draws them together.
    """
    
    def __init__(self):
        self.draw_batches: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
        
    def add_tile(self, tile_type: str, x: int, y: int):
        """Add a tile to the batch queue"""
        self.draw_batches[tile_type].append((x, y))
    
    def render_batches(self, screen: pygame.Surface, sprite_cache: SpriteCache, 
                       tile_colors: Dict[str, Tuple[int, int, int]]):
        """
        Render all batched tiles efficiently.
        
        Args:
            screen: Pygame surface to draw on
            sprite_cache: Sprite cache for tile surfaces
            tile_colors: Mapping of tile types to colors
        """
        for tile_type, positions in self.draw_batches.items():
            if tile_type in tile_colors:
                color = tile_colors[tile_type]
                cached_surface = sprite_cache.get_tile_surface(tile_type, color)
                
                # Batch blit all tiles of this type
                for x, y in positions:
                    screen.blit(cached_surface, (x, y))
        
        # Clear batches for next frame
        self.draw_batches.clear()


class EntitySpatialHash:
    """
    Spatial hash grid for fast entity lookups.
    Reduces O(n) collision checks to O(1) average case.
    """
    
    def __init__(self, cell_size: int = 500):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], List] = defaultdict(list)
        
    def clear(self):
        """Clear the spatial hash"""
        self.grid.clear()
    
    def _get_cell(self, x: int, y: int) -> Tuple[int, int]:
        """Convert world coordinates to grid cell"""
        return (x // self.cell_size, y // self.cell_size)
    
    def insert(self, entity, x: int, y: int):
        """Insert entity at given position"""
        cell = self._get_cell(x, y)
        self.grid[cell].append(entity)
    
    def query_nearby(self, x: int, y: int, radius: int = 1) -> List:
        """
        Query entities near a position.
        
        Args:
            x, y: World coordinates
            radius: Number of cells to search in each direction
            
        Returns:
            List of nearby entities
        """
        center_cell = self._get_cell(x, y)
        nearby = []
        
        # Check surrounding cells
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                nearby.extend(self.grid.get(cell, []))
        
        return nearby


class FrameRateLimiter:
    """
    Smart frame rate limiting that adapts to system performance.
    Prevents wasted CPU cycles while maintaining smooth gameplay.
    """
    
    def __init__(self, target_fps: int = 60, adaptive: bool = True):
        self.target_fps = target_fps
        self.adaptive = adaptive
        self.min_fps = 30
        self.max_fps = 144
        
        self.frame_times = []
        self.max_samples = 60  # Track last 60 frames
        
    def update(self, clock: pygame.time.Clock) -> float:
        """
        Update frame timing and return delta time.
        
        Args:
            clock: Pygame clock object
            
        Returns:
            Delta time in seconds
        """
        dt = clock.tick(self.target_fps) / 1000.0
        
        if self.adaptive:
            self.frame_times.append(dt)
            if len(self.frame_times) > self.max_samples:
                self.frame_times.pop(0)
            
            # Calculate average frame time
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 60
            
            # Adjust target FPS if system is struggling
            if avg_fps < self.min_fps:
                # System struggling - reduce target
                self.target_fps = max(30, self.target_fps - 5)
            elif avg_fps > self.target_fps * 1.5 and self.target_fps < self.max_fps:
                # System has headroom - increase target
                self.target_fps = min(self.max_fps, self.target_fps + 5)
        
        return dt
    
    def get_current_fps(self) -> float:
        """Get current average FPS"""
        if not self.frame_times:
            return self.target_fps
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 60


class DirtyRectManager:
    """
    Tracks which screen regions need redrawing.
    Only updates changed portions instead of entire screen.
    """
    
    def __init__(self):
        self.dirty_rects: Set[Tuple[int, int, int, int]] = set()
        self.full_redraw = True
        
    def mark_dirty(self, x: int, y: int, width: int, height: int):
        """Mark a screen region as needing redraw"""
        self.dirty_rects.add((x, y, width, height))
    
    def mark_full_redraw(self):
        """Force full screen redraw"""
        self.full_redraw = True
    
    def get_dirty_rects(self) -> List[Tuple[int, int, int, int]]:
        """Get list of dirty rectangles"""
        if self.full_redraw:
            return []  # Empty list means full redraw
        return list(self.dirty_rects)
    
    def clear(self):
        """Clear dirty rects after redraw"""
        self.dirty_rects.clear()
        self.full_redraw = False


# Global instances (singleton pattern)
_viewport_culler = None
_sprite_cache = None
_batch_renderer = None
_spatial_hash = None
_frame_limiter = None
_dirty_rect_manager = None

def get_viewport_culler(screen_width=800, screen_height=600, tile_size=52):
    global _viewport_culler
    if _viewport_culler is None:
        _viewport_culler = ViewportCuller(screen_width, screen_height, tile_size)
    return _viewport_culler

def get_sprite_cache(tile_size=52):
    global _sprite_cache
    if _sprite_cache is None:
        _sprite_cache = SpriteCache(tile_size)
    return _sprite_cache

def get_batch_renderer():
    global _batch_renderer
    if _batch_renderer is None:
        _batch_renderer = BatchRenderer()
    return _batch_renderer

def get_spatial_hash(cell_size=500):
    global _spatial_hash
    if _spatial_hash is None:
        _spatial_hash = EntitySpatialHash(cell_size)
    return _spatial_hash

def get_frame_limiter(target_fps=60, adaptive=True):
    global _frame_limiter
    if _frame_limiter is None:
        _frame_limiter = FrameRateLimiter(target_fps, adaptive)
    return _frame_limiter

def get_dirty_rect_manager():
    global _dirty_rect_manager
    if _dirty_rect_manager is None:
        _dirty_rect_manager = DirtyRectManager()
    return _dirty_rect_manager
