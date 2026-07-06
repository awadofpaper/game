"""
Font Size Customization System
Allows players to adjust font sizes for better readability
"""

import pygame
import json
import os
from typing import Dict, Optional
from enum import Enum

class FontCategory(Enum):
    """Different categories of text that can have different sizes"""
    UI_TEXT = "ui_text"              # General UI text
    HUD_TEXT = "hud_text"            # Health/mana/stats text
    MENU_TEXT = "menu_text"          # Menu and dialogue text
    CONSOLE_TEXT = "console_text"    # Message console text
    TOOLTIP_TEXT = "tooltip_text"    # Tooltips and help text
    TITLE_TEXT = "title_text"        # Title screens and headers

class FontSizeManager:
    """Manages font sizes and provides scaled fonts"""
    
    def __init__(self):
        self.config_file = "font_settings.json"
        
        # Base font sizes (at 100% scale)
        self.base_sizes = {
            FontCategory.UI_TEXT: 24,
            FontCategory.HUD_TEXT: 20,
            FontCategory.MENU_TEXT: 28,
            FontCategory.CONSOLE_TEXT: 18,
            FontCategory.TOOLTIP_TEXT: 16,
            FontCategory.TITLE_TEXT: 36
        }
        
        # Current scale multipliers (0.5 to 2.0)
        self.scale_multipliers = {
            FontCategory.UI_TEXT: 1.0,
            FontCategory.HUD_TEXT: 1.0,
            FontCategory.MENU_TEXT: 1.0,
            FontCategory.CONSOLE_TEXT: 1.0,
            FontCategory.TOOLTIP_TEXT: 1.0,
            FontCategory.TITLE_TEXT: 1.0
        }
        
        # Global scale (affects all fonts)
        self.global_scale = 1.0
        
        # Font cache to avoid recreating fonts
        self.font_cache: Dict[tuple, pygame.font.Font] = {}
        
        # Load settings
        self.load_settings()
        
    def get_font_size(self, category: FontCategory) -> int:
        """Get the current font size for a category"""
        base_size = self.base_sizes[category]
        category_scale = self.scale_multipliers[category]
        return int(base_size * category_scale * self.global_scale)
        
    def get_font(self, category: FontCategory, font_name: Optional[str] = None) -> pygame.font.Font:
        """Get a font object for the given category"""
        size = self.get_font_size(category)
        
        # Create cache key
        cache_key = (font_name or "default", size)
        
        # Return cached font if available
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
            
        # Create new font
        if font_name:
            try:
                font = pygame.font.Font(font_name, size)
            except:
                # Fallback to system font if custom font fails
                font = pygame.font.SysFont(None, size)
        else:
            font = pygame.font.SysFont(None, size)
            
        # Cache and return
        self.font_cache[cache_key] = font
        return font
        
    def set_category_scale(self, category: FontCategory, scale: float):
        """Set the scale multiplier for a specific font category"""
        self.scale_multipliers[category] = max(0.5, min(2.0, scale))
        self.clear_font_cache()
        
    def set_global_scale(self, scale: float):
        """Set the global scale that affects all fonts"""
        self.global_scale = max(0.5, min(2.0, scale))
        self.clear_font_cache()
        
    def get_category_scale(self, category: FontCategory) -> float:
        """Get the current scale multiplier for a category"""
        return self.scale_multipliers[category]
        
    def get_global_scale(self) -> float:
        """Get the current global scale"""
        return self.global_scale
        
    def increase_category_size(self, category: FontCategory, amount: float = 0.1):
        """Increase font size for a category"""
        current_scale = self.scale_multipliers[category]
        self.set_category_scale(category, current_scale + amount)
        
    def decrease_category_size(self, category: FontCategory, amount: float = 0.1):
        """Decrease font size for a category"""
        current_scale = self.scale_multipliers[category]
        self.set_category_scale(category, current_scale - amount)
        
    def increase_global_size(self, amount: float = 0.1):
        """Increase global font size"""
        self.set_global_scale(self.global_scale + amount)
        
    def decrease_global_size(self, amount: float = 0.1):
        """Decrease global font size"""
        self.set_global_scale(self.global_scale - amount)
        
    def reset_category_to_default(self, category: FontCategory):
        """Reset a category to default scale"""
        self.scale_multipliers[category] = 1.0
        self.clear_font_cache()
        
    def reset_all_to_defaults(self):
        """Reset all font sizes to defaults"""
        for category in FontCategory:
            self.scale_multipliers[category] = 1.0
        self.global_scale = 1.0
        self.clear_font_cache()
        
    def apply_preset(self, preset_name: str):
        """Apply a font size preset"""
        presets = {
            "Small": {
                "global_scale": 0.8,
                "scales": {category: 1.0 for category in FontCategory}
            },
            "Default": {
                "global_scale": 1.0,
                "scales": {category: 1.0 for category in FontCategory}
            },
            "Large": {
                "global_scale": 1.3,
                "scales": {category: 1.0 for category in FontCategory}
            },
            "Extra Large": {
                "global_scale": 1.6,
                "scales": {category: 1.0 for category in FontCategory}
            },
            "Low Vision": {
                "global_scale": 2.0,
                "scales": {
                    FontCategory.UI_TEXT: 1.2,
                    FontCategory.HUD_TEXT: 1.3,
                    FontCategory.MENU_TEXT: 1.1,
                    FontCategory.CONSOLE_TEXT: 1.4,
                    FontCategory.TOOLTIP_TEXT: 1.5,
                    FontCategory.TITLE_TEXT: 1.0
                }
            },
            "Reading Focused": {
                "global_scale": 1.1,
                "scales": {
                    FontCategory.UI_TEXT: 1.2,
                    FontCategory.HUD_TEXT: 0.9,
                    FontCategory.MENU_TEXT: 1.3,
                    FontCategory.CONSOLE_TEXT: 1.4,
                    FontCategory.TOOLTIP_TEXT: 1.3,
                    FontCategory.TITLE_TEXT: 1.1
                }
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.global_scale = preset["global_scale"]
            self.scale_multipliers.update(preset["scales"])
            self.clear_font_cache()
            
    def get_available_presets(self) -> list:
        """Get list of available font presets"""
        return ["Small", "Default", "Large", "Extra Large", "Low Vision", "Reading Focused"]
        
    def clear_font_cache(self):
        """Clear the font cache (forces font recreation)"""
        self.font_cache.clear()
        
    def save_settings(self):
        """Save font settings to file"""
        try:
            settings = {
                "global_scale": self.global_scale,
                "category_scales": {cat.value: scale for cat, scale in self.scale_multipliers.items()}
            }
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving font settings: {e}")
            
    def load_settings(self):
        """Load font settings from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    
                self.global_scale = settings.get("global_scale", 1.0)
                
                category_scales = settings.get("category_scales", {})
                for category in FontCategory:
                    if category.value in category_scales:
                        self.scale_multipliers[category] = category_scales[category.value]
                        
        except Exception as e:
            print(f"Error loading font settings: {e}")
            
    def get_size_info(self) -> dict:
        """Get current size information for all categories"""
        return {
            "global_scale": self.global_scale,
            "categories": {
                category.value: {
                    "base_size": self.base_sizes[category],
                    "scale": self.scale_multipliers[category],
                    "actual_size": self.get_font_size(category)
                } for category in FontCategory
            }
        }

# Global font manager instance
font_manager = None

def get_font_manager() -> FontSizeManager:
    """Get the global font size manager instance"""
    global font_manager
    if font_manager is None:
        font_manager = FontSizeManager()
    return font_manager

# Convenience functions for common use cases
def get_ui_font() -> pygame.font.Font:
    """Get font for general UI text"""
    return get_font_manager().get_font(FontCategory.UI_TEXT)

def get_hud_font() -> pygame.font.Font:
    """Get font for HUD elements"""
    return get_font_manager().get_font(FontCategory.HUD_TEXT)

def get_menu_font() -> pygame.font.Font:
    """Get font for menus and dialogues"""
    return get_font_manager().get_font(FontCategory.MENU_TEXT)

def get_console_font() -> pygame.font.Font:
    """Get font for message console"""
    return get_font_manager().get_font(FontCategory.CONSOLE_TEXT)

def get_tooltip_font() -> pygame.font.Font:
    """Get font for tooltips"""
    return get_font_manager().get_font(FontCategory.TOOLTIP_TEXT)

def get_title_font() -> pygame.font.Font:
    """Get font for titles"""
    return get_font_manager().get_font(FontCategory.TITLE_TEXT)