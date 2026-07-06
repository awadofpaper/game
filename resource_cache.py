"""
Resource caching system to prevent memory leaks from repeated pygame object creation.
Caches surfaces and fonts for reuse across frames.
"""
import pygame
from typing import Dict, Tuple, Optional


class SurfaceCache:
    """Cache for pygame surfaces to avoid repeated memory allocations"""
    
    def __init__(self):
        self._cache: Dict[Tuple, pygame.Surface] = {}
        self._hit_count = 0
        self._miss_count = 0
    
    def get_surface(self, size: Tuple[int, int], flags: int = 0, alpha: bool = False) -> pygame.Surface:
        """
        Get a cached surface or create new one if not exists.
        
        Args:
            size: (width, height) tuple
            flags: pygame surface flags
            alpha: whether to use convert_alpha() instead of convert()
            
        Returns:
            pygame.Surface ready for blitting
        """
        key = (size, flags, alpha)
        
        if key in self._cache:
            self._hit_count += 1
            return self._cache[key].copy()
        
        self._miss_count += 1
        
        # Create and optimize new surface
        surf = pygame.Surface(size, flags)
        if alpha or (flags & pygame.SRCALPHA):
            optimized = surf.convert_alpha()
        else:
            optimized = surf.convert()
        
        self._cache[key] = optimized
        return optimized.copy()
    
    def clear(self):
        """Clear the entire cache"""
        self._cache.clear()
        self._hit_count = 0
        self._miss_count = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total * 100) if total > 0 else 0
        return {
            'hits': self._hit_count,
            'misses': self._miss_count,
            'hit_rate': hit_rate,
            'cached_surfaces': len(self._cache)
        }


class FontCache:
    """Cache for pygame fonts to avoid repeated font object creation"""
    
    def __init__(self):
        self._cache: Dict[Tuple, pygame.font.Font] = {}
        self._hit_count = 0
        self._miss_count = 0
    
    def get_font(self, name: Optional[str], size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
        """
        Get a cached font or create new one if not exists.
        
        Args:
            name: Font name or None for default
            size: Font size in pixels
            bold: Whether font should be bold
            italic: Whether font should be italic
            
        Returns:
            pygame.font.Font object
        """
        key = (name, size, bold, italic)
        
        if key in self._cache:
            self._hit_count += 1
            return self._cache[key]
        
        self._miss_count += 1
        
        # Create new font
        try:
            if name is None:
                font = pygame.font.Font(None, size)
            else:
                font = pygame.font.SysFont(name, size, bold=bold, italic=italic)
        except (pygame.error, OSError, FileNotFoundError):
            # Fallback to default font
            font = pygame.font.SysFont('arial', size, bold=bold, italic=italic)
        
        self._cache[key] = font
        return font
    
    def get_sysfont(self, name: str, size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
        """
        Get a cached system font.
        Convenience wrapper around get_font() for system fonts.
        """
        return self.get_font(name, size, bold, italic)
    
    def clear(self):
        """Clear the entire cache"""
        self._cache.clear()
        self._hit_count = 0
        self._miss_count = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total * 100) if total > 0 else 0
        return {
            'hits': self._hit_count,
            'misses': self._miss_count,
            'hit_rate': hit_rate,
            'cached_fonts': len(self._cache)
        }


# Global cache instances (singleton pattern)
_surface_cache = None
_font_cache = None


def get_surface_cache() -> SurfaceCache:
    """Get the global surface cache instance"""
    global _surface_cache
    if _surface_cache is None:
        _surface_cache = SurfaceCache()
    return _surface_cache


def get_font_cache() -> FontCache:
    """Get the global font cache instance"""
    global _font_cache
    if _font_cache is None:
        _font_cache = FontCache()
    return _font_cache


def get_cached_surface(size: Tuple[int, int], flags: int = 0, alpha: bool = False) -> pygame.Surface:
    """Convenience function to get a cached surface"""
    return get_surface_cache().get_surface(size, flags, alpha)


def get_cached_font(name: Optional[str], size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    """Convenience function to get a cached font"""
    return get_font_cache().get_font(name, size, bold, italic)


def clear_caches():
    """Clear all resource caches"""
    if _surface_cache:
        _surface_cache.clear()
    if _font_cache:
        _font_cache.clear()


def get_cache_stats() -> Dict[str, Dict[str, int]]:
    """Get statistics from all caches"""
    stats = {}
    if _surface_cache:
        stats['surfaces'] = _surface_cache.get_stats()
    if _font_cache:
        stats['fonts'] = _font_cache.get_stats()
    return stats
