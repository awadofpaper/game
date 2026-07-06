"""
Font Manager - Cache pygame font objects to avoid expensive font creation
Creating fonts with pygame.font.SysFont() is EXTREMELY slow - cache them!
"""
import pygame

class FontManager:
    """Singleton font manager that caches font objects"""
    _instance = None
    _fonts = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._fonts = {}
            self._initialized = True
    
    def get_font(self, name, size):
        """
        Get a cached font object. Creates it if it doesn't exist.
        
        Args:
            name: Font name (e.g., None for default, 'arial', 'courier', etc.)
            size: Font size in pixels
            
        Returns:
            pygame.font.Font object
        """
        cache_key = (name, size)
        
        if cache_key not in self._fonts:
            # Create font and cache it
            self._fonts[cache_key] = pygame.font.SysFont(name, size)
        
        return self._fonts[cache_key]
    
    def clear_cache(self):
        """Clear all cached fonts (useful if changing system fonts)"""
        self._fonts.clear()

# Global singleton instance
_font_manager = None

def get_font_manager():
    """Get the global FontManager singleton"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager

def get_font(name, size):
    """
    Convenience function to get a cached font.
    
    Usage:
        from font_manager import get_font
        font = get_font(None, 24)  # Returns cached font object
        text = font.render("Hello", True, (255, 255, 255))
    
    This is MUCH faster than:
        font = pygame.font.SysFont(None, 24)  # Creates new font every time!
    """
    return get_font_manager().get_font(name, size)
