"""
UI Theme System
Provides different visual themes for the game interface including
dark mode, light mode, high contrast, and custom color schemes.
"""

import pygame
import json
import os
from typing import Dict, Tuple, Any

class UITheme:
    """Manages UI color themes and visual customization"""
    
    def __init__(self):
        self.themes_file = "ui_themes.json"
        
        # Define built-in themes
        self.built_in_themes = {
            "Default": {
                "name": "Default Theme",
                "description": "Classic game colors",
                "colors": {
                    # UI Background colors
                    "ui_bg_primary": (40, 40, 40),        # Main UI backgrounds
                    "ui_bg_secondary": (30, 30, 30),      # Secondary panels
                    "ui_bg_accent": (60, 60, 60),         # Hover states, highlights
                    
                    # Text colors
                    "text_primary": (255, 255, 255),      # Main text
                    "text_secondary": (200, 200, 200),    # Secondary text
                    "text_accent": (255, 215, 0),         # Gold/important text
                    "text_error": (255, 80, 80),          # Error messages
                    "text_success": (100, 255, 100),      # Success messages
                    "text_warning": (255, 180, 0),        # Warning text
                    
                    # Health/Mana/Stamina
                    "health_color": (255, 100, 100),      # Health bars
                    "mana_color": (100, 100, 255),        # Mana bars  
                    "stamina_color": (255, 255, 100),     # Stamina bars
                    "xp_color": (150, 255, 150),          # XP bars
                    
                    # Interactive elements
                    "button_normal": (70, 70, 70),        # Normal buttons
                    "button_hover": (90, 90, 90),         # Hovered buttons
                    "button_pressed": (50, 50, 50),       # Pressed buttons
                    "button_disabled": (40, 40, 40),      # Disabled buttons
                    
                    # Borders and frames
                    "border_normal": (100, 100, 100),     # Normal borders
                    "border_active": (150, 150, 150),     # Active/selected borders
                    "border_accent": (255, 215, 0),       # Important borders
                    
                    # Inventory and items
                    "slot_empty": (60, 60, 60),           # Empty inventory slots
                    "slot_filled": (80, 80, 80),          # Filled inventory slots
                    "slot_selected": (120, 120, 120),     # Selected slots
                    "item_common": (255, 255, 255),       # Common items
                    "item_uncommon": (100, 255, 100),     # Uncommon items
                    "item_rare": (100, 100, 255),         # Rare items
                    "item_epic": (255, 100, 255),         # Epic items
                    "item_legendary": (255, 165, 0),      # Legendary items
                }
            },
            
            "Dark": {
                "name": "Dark Mode",
                "description": "Easy on the eyes dark theme",
                "colors": {
                    "ui_bg_primary": (25, 25, 25),
                    "ui_bg_secondary": (15, 15, 15),
                    "ui_bg_accent": (45, 45, 45),
                    
                    "text_primary": (230, 230, 230),
                    "text_secondary": (180, 180, 180),
                    "text_accent": (255, 200, 50),
                    "text_error": (255, 100, 100),
                    "text_success": (120, 255, 120),
                    "text_warning": (255, 200, 80),
                    
                    "health_color": (220, 80, 80),
                    "mana_color": (80, 120, 220),
                    "stamina_color": (200, 200, 80),
                    "xp_color": (120, 200, 120),
                    
                    "button_normal": (50, 50, 50),
                    "button_hover": (70, 70, 70),
                    "button_pressed": (30, 30, 30),
                    "button_disabled": (25, 25, 25),
                    
                    "border_normal": (80, 80, 80),
                    "border_active": (120, 120, 120),
                    "border_accent": (200, 150, 50),
                    
                    "slot_empty": (40, 40, 40),
                    "slot_filled": (60, 60, 60),
                    "slot_selected": (100, 100, 100),
                    "item_common": (200, 200, 200),
                    "item_uncommon": (120, 200, 120),
                    "item_rare": (120, 120, 200),
                    "item_epic": (200, 120, 200),
                    "item_legendary": (255, 140, 40),
                }
            },
            
            "Light": {
                "name": "Light Mode", 
                "description": "Bright and clean theme",
                "colors": {
                    "ui_bg_primary": (240, 240, 240),
                    "ui_bg_secondary": (250, 250, 250),
                    "ui_bg_accent": (220, 220, 220),
                    
                    "text_primary": (40, 40, 40),
                    "text_secondary": (80, 80, 80),
                    "text_accent": (180, 140, 0),
                    "text_error": (200, 40, 40),
                    "text_success": (40, 160, 40),
                    "text_warning": (200, 120, 0),
                    
                    "health_color": (220, 60, 60),
                    "mana_color": (60, 80, 200),
                    "stamina_color": (180, 180, 40),
                    "xp_color": (80, 180, 80),
                    
                    "button_normal": (200, 200, 200),
                    "button_hover": (180, 180, 180),
                    "button_pressed": (220, 220, 220),
                    "button_disabled": (240, 240, 240),
                    
                    "border_normal": (150, 150, 150),
                    "border_active": (100, 100, 100),
                    "border_accent": (180, 140, 0),
                    
                    "slot_empty": (220, 220, 220),
                    "slot_filled": (200, 200, 200),
                    "slot_selected": (160, 160, 160),
                    "item_common": (60, 60, 60),
                    "item_uncommon": (40, 120, 40),
                    "item_rare": (40, 40, 160),
                    "item_epic": (120, 40, 120),
                    "item_legendary": (180, 100, 20),
                }
            },
            
            "High Contrast": {
                "name": "High Contrast",
                "description": "Maximum visibility theme",
                "colors": {
                    "ui_bg_primary": (0, 0, 0),
                    "ui_bg_secondary": (20, 20, 20),
                    "ui_bg_accent": (40, 40, 40),
                    
                    "text_primary": (255, 255, 255),
                    "text_secondary": (200, 200, 200),
                    "text_accent": (255, 255, 0),
                    "text_error": (255, 0, 0),
                    "text_success": (0, 255, 0),
                    "text_warning": (255, 128, 0),
                    
                    "health_color": (255, 0, 0),
                    "mana_color": (0, 0, 255),
                    "stamina_color": (255, 255, 0),
                    "xp_color": (0, 255, 0),
                    
                    "button_normal": (80, 80, 80),
                    "button_hover": (120, 120, 120),
                    "button_pressed": (40, 40, 40),
                    "button_disabled": (20, 20, 20),
                    
                    "border_normal": (160, 160, 160),
                    "border_active": (255, 255, 255),
                    "border_accent": (255, 255, 0),
                    
                    "slot_empty": (60, 60, 60),
                    "slot_filled": (100, 100, 100),
                    "slot_selected": (200, 200, 200),
                    "item_common": (255, 255, 255),
                    "item_uncommon": (0, 255, 0),
                    "item_rare": (0, 128, 255),
                    "item_epic": (255, 0, 255),
                    "item_legendary": (255, 165, 0),
                }
            },
            
            "Ocean": {
                "name": "Ocean Theme",
                "description": "Cool blue oceanic colors",
                "colors": {
                    "ui_bg_primary": (20, 40, 60),
                    "ui_bg_secondary": (15, 30, 50),
                    "ui_bg_accent": (30, 60, 90),
                    
                    "text_primary": (200, 220, 255),
                    "text_secondary": (160, 180, 220),
                    "text_accent": (100, 200, 255),
                    "text_error": (255, 120, 120),
                    "text_success": (120, 255, 180),
                    "text_warning": (255, 200, 120),
                    
                    "health_color": (255, 100, 120),
                    "mana_color": (80, 150, 255),
                    "stamina_color": (120, 220, 200),
                    "xp_color": (100, 255, 200),
                    
                    "button_normal": (40, 70, 100),
                    "button_hover": (60, 90, 120),
                    "button_pressed": (20, 50, 80),
                    "button_disabled": (30, 50, 70),
                    
                    "border_normal": (80, 120, 160),
                    "border_active": (120, 160, 200),
                    "border_accent": (100, 200, 255),
                    
                    "slot_empty": (40, 60, 80),
                    "slot_filled": (60, 80, 100),
                    "slot_selected": (100, 120, 140),
                    "item_common": (180, 200, 220),
                    "item_uncommon": (120, 255, 200),
                    "item_rare": (120, 180, 255),
                    "item_epic": (200, 150, 255),
                    "item_legendary": (255, 200, 120),
                }
            },
            
            "Forest": {
                "name": "Forest Theme",
                "description": "Natural green forest colors",
                "colors": {
                    "ui_bg_primary": (30, 50, 30),
                    "ui_bg_secondary": (20, 40, 20),
                    "ui_bg_accent": (50, 80, 50),
                    
                    "text_primary": (220, 255, 200),
                    "text_secondary": (180, 220, 160),
                    "text_accent": (255, 220, 100),
                    "text_error": (255, 100, 100),
                    "text_success": (150, 255, 150),
                    "text_warning": (255, 180, 80),
                    
                    "health_color": (255, 120, 120),
                    "mana_color": (120, 180, 255),
                    "stamina_color": (200, 255, 120),
                    "xp_color": (180, 255, 140),
                    
                    "button_normal": (60, 90, 60),
                    "button_hover": (80, 110, 80),
                    "button_pressed": (40, 70, 40),
                    "button_disabled": (40, 60, 40),
                    
                    "border_normal": (100, 140, 100),
                    "border_active": (140, 180, 140),
                    "border_accent": (255, 220, 100),
                    
                    "slot_empty": (50, 70, 50),
                    "slot_filled": (70, 90, 70),
                    "slot_selected": (110, 130, 110),
                    "item_common": (200, 220, 180),
                    "item_uncommon": (150, 255, 150),
                    "item_rare": (150, 200, 255),
                    "item_epic": (255, 150, 200),
                    "item_legendary": (255, 200, 100),
                }
            }
        }
        
        # Load user preferences
        self.current_theme = "Default"
        self.load_settings()
        
    def get_themes_list(self) -> list:
        """Get list of available theme names"""
        return list(self.built_in_themes.keys())
        
    def get_theme_info(self, theme_name: str) -> dict:
        """Get theme information (name, description)"""
        if theme_name in self.built_in_themes:
            theme = self.built_in_themes[theme_name]
            return {
                "name": theme["name"],
                "description": theme["description"]
            }
        return {"name": "Unknown", "description": "Theme not found"}
        
    def set_theme(self, theme_name: str):
        """Set the current theme"""
        if theme_name in self.built_in_themes:
            self.current_theme = theme_name
            self.save_settings()
            
    def get_color(self, color_key: str) -> Tuple[int, int, int]:
        """Get a color from the current theme"""
        if self.current_theme in self.built_in_themes:
            colors = self.built_in_themes[self.current_theme]["colors"]
            return colors.get(color_key, (255, 255, 255))  # Default to white
        return (255, 255, 255)
        
    def get_all_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Get all colors from current theme"""
        if self.current_theme in self.built_in_themes:
            return self.built_in_themes[self.current_theme]["colors"]
        return {}
        
    def save_settings(self):
        """Save theme settings to file"""
        try:
            settings = {
                "current_theme": self.current_theme
            }
            with open(self.themes_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving theme settings: {e}")
            
    def load_settings(self):
        """Load theme settings from file"""
        try:
            if os.path.exists(self.themes_file):
                with open(self.themes_file, 'r') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get("current_theme", "Default")
        except Exception as e:
            print(f"Error loading theme settings: {e}")
            self.current_theme = "Default"

# Global theme instance
ui_theme = UITheme()

def get_ui_theme() -> UITheme:
    """Get the global UI theme instance"""
    return ui_theme