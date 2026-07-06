"""
Font and Text Caching System
Provides efficient text rendering with caching to eliminate redundant font operations.
"""

import pygame
from typing import Dict, Tuple, Optional, List
import hashlib


class FontCache:
    """
    Caches rendered text surfaces to avoid expensive font rendering operations.
    """
    
    def __init__(self, max_cache_size: int = 1000):
        self.cache: Dict[str, pygame.Surface] = {}
        self.access_order: list = []  # For LRU eviction
        self.max_cache_size = max_cache_size
        self.cache_hits = 0
        self.cache_misses = 0
        
    def _generate_key(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int], 
                     background: Optional[Tuple[int, int, int]] = None) -> str:
        """Generate a unique key for the cached text."""
        # Create a hash from text, font size, and color
        font_size = font.get_height()
        color_str = f"{color[0]},{color[1]},{color[2]}"
        bg_str = f"{background[0]},{background[1]},{background[2]}" if background else "None"
        
        key_string = f"{text}|{font_size}|{color_str}|{bg_str}"
        return hashlib.md5(key_string.encode()).hexdigest()[:16]  # Short hash for efficiency
    
    def get_text_surface(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int],
                        background: Optional[Tuple[int, int, int]] = None) -> pygame.Surface:
        """
        Get a rendered text surface, using cache if available.
        
        Args:
            text: The text to render
            font: The pygame font object
            color: Text color as RGB tuple
            background: Optional background color as RGB tuple
            
        Returns:
            Pygame Surface with rendered text
        """
        # Generate cache key
        cache_key = self._generate_key(text, font, color, background)
        
        # Check if we have this text cached
        if cache_key in self.cache:
            self.cache_hits += 1
            self._update_access_order(cache_key)
            return self.cache[cache_key]
        
        # Cache miss - render the text
        self.cache_misses += 1
        
        if background:
            surface = font.render(text, True, color, background)
        else:
            surface = font.render(text, True, color)
            
        # Add to cache
        self._add_to_cache(cache_key, surface)
        
        return surface
    
    def _add_to_cache(self, key: str, surface: pygame.Surface):
        """Add a surface to the cache, managing size limits."""
        # Remove oldest entries if cache is full
        while len(self.cache) >= self.max_cache_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        # Add new entry
        self.cache[key] = surface
        self.access_order.append(key)
    
    def _update_access_order(self, key: str):
        """Update the access order for LRU tracking."""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def clear_cache(self):
        """Clear all cached text surfaces."""
        self.cache.clear()
        self.access_order.clear()
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache performance statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_cache_size,
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': round(hit_rate, 2),
            'memory_usage_kb': sum(surf.get_size()[0] * surf.get_size()[1] * 4 
                                  for surf in self.cache.values()) // 1024  # Rough estimate
        }


class TileCache:
    """
    Caches tile surfaces for efficient map rendering.
    """
    
    def __init__(self, max_cache_size: int = 500):
        self.cache: Dict[Tuple[int, str], pygame.Surface] = {}
        self.max_cache_size = max_cache_size
        self.cache_hits = 0
        self.cache_misses = 0
        
    def get_tile_surface(self, tile_type: int, tile_variant: str = "default") -> Optional[pygame.Surface]:
        """
        Get a cached tile surface.
        
        Args:
            tile_type: The type/ID of the tile
            tile_variant: Variant name (for different tile states)
            
        Returns:
            Cached pygame Surface or None if not cached
        """
        cache_key = (tile_type, tile_variant)
        
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        return None
    
    def cache_tile_surface(self, tile_type: int, surface: pygame.Surface, tile_variant: str = "default"):
        """
        Cache a tile surface.
        
        Args:
            tile_type: The type/ID of the tile
            surface: The rendered tile surface
            tile_variant: Variant name (for different tile states)
        """
        cache_key = (tile_type, tile_variant)
        
        # Manage cache size
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO for tiles)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = surface
    
    def clear_cache(self):
        """Clear all cached tile surfaces."""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        
    def get_cache_stats(self) -> Dict[str, any]:
        """Get tile cache performance statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_cache_size,
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': round(hit_rate, 2)
        }


class OptimizedTextRenderer:
    """
    High-level text rendering system that combines font caching with efficient rendering.
    """
    
    def __init__(self, font_cache: Optional[FontCache] = None):
        self.font_cache = font_cache or FontCache()
        
    def render_text(self, screen: pygame.Surface, text: str, x: int, y: int, 
                   font: pygame.font.Font, color: Tuple[int, int, int],
                   background: Optional[Tuple[int, int, int]] = None) -> pygame.Rect:
        """
        Render text to screen using cached surfaces.
        
        Returns:
            pygame.Rect representing the area where text was rendered
        """
        text_surface = self.font_cache.get_text_surface(text, font, color, background)
        rect = screen.blit(text_surface, (x, y))
        return rect
    
    def render_text_centered(self, screen: pygame.Surface, text: str, center_x: int, center_y: int,
                           font: pygame.font.Font, color: Tuple[int, int, int],
                           background: Optional[Tuple[int, int, int]] = None) -> pygame.Rect:
        """Render text centered at the given position."""
        text_surface = self.font_cache.get_text_surface(text, font, color, background)
        rect = text_surface.get_rect(center=(center_x, center_y))
        screen.blit(text_surface, rect)
        return rect
    
    def get_text_size(self, text: str, font: pygame.font.Font) -> Tuple[int, int]:
        """Get the size of text without rendering it."""
        return font.size(text)
    
    def render_multiline_text(self, screen: pygame.Surface, text: str, x: int, y: int,
                             font: pygame.font.Font, color: Tuple[int, int, int],
                             line_spacing: int = 5, max_width: Optional[int] = None) -> List[pygame.Rect]:
        """
        Render multiline text with optional word wrapping.
        
        Returns:
            List of pygame.Rect objects for each line rendered
        """
        lines = text.split('\n')
        rendered_rects = []
        current_y = y
        
        for line in lines:
            if max_width and font.size(line)[0] > max_width:
                # Simple word wrapping
                wrapped_lines = self._wrap_text(line, font, max_width)
                for wrapped_line in wrapped_lines:
                    rect = self.render_text(screen, wrapped_line, x, current_y, font, color)
                    rendered_rects.append(rect)
                    current_y += rect.height + line_spacing
            else:
                rect = self.render_text(screen, line, x, current_y, font, color)
                rendered_rects.append(rect)
                current_y += rect.height + line_spacing
        
        return rendered_rects
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def clear_cache(self):
        """Clear the font cache."""
        self.font_cache.clear_cache()
        
    def get_performance_stats(self) -> Dict[str, any]:
        """Get rendering performance statistics."""
        return self.font_cache.get_cache_stats()


# Global instances for convenient import
_global_font_cache = None
_global_text_renderer = None

def get_font_cache() -> FontCache:
    """Get the global font cache instance."""
    global _global_font_cache
    if _global_font_cache is None:
        _global_font_cache = FontCache()
    return _global_font_cache

def get_text_renderer() -> OptimizedTextRenderer:
    """Get the global optimized text renderer instance."""
    global _global_text_renderer
    if _global_text_renderer is None:
        _global_text_renderer = OptimizedTextRenderer(get_font_cache())
    return _global_text_renderer
