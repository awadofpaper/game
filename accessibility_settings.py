"""
Accessibility Settings System
Comprehensive accessibility options for inclusive gaming
"""

import pygame
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum

class ColorBlindType(Enum):
    NORMAL = "normal"
    PROTANOPIA = "protanopia"  # Red-blind
    DEUTERANOPIA = "deuteranopia"  # Green-blind
    TRITANOPIA = "tritanopia"  # Blue-blind
    MONOCHROME = "monochrome"  # Complete color blindness

class AccessibilitySettings:
    def __init__(self):
        self.settings_file = "accessibility_settings.json"
        
        # Default accessibility settings
        self.default_settings = {
            # Visual Accessibility
            "colorblind_support": ColorBlindType.NORMAL.value,
            "high_contrast": False,
            "large_text": False,
            "text_scale": 1.0,
            "ui_scale": 1.0,
            "screen_flash_reduction": True,
            "motion_reduction": False,
            "animation_speed": 1.0,
            
            # Color & Visual Aids
            "cursor_highlight": False,
            "focus_outline": True,
            "selection_highlight": True,
            "enemy_outline": False,
            "item_glow": True,
            "damage_numbers_size": 1.0,
            
            # Audio Accessibility
            "visual_sound_cues": False,
            "subtitles": False,
            "subtitle_size": 1.0,
            "audio_descriptions": False,
            "sound_visualization": False,
            
            # Input Accessibility
            "hold_to_toggle": {},  # Actions that can be toggled instead of held
            "key_repeat_delay": 0.5,
            "key_repeat_rate": 0.1,
            "mouse_sensitivity": 1.0,
            "sticky_keys": False,
            "one_handed_mode": False,
            
            # Cognitive Accessibility
            "pause_on_focus_loss": True,
            "simplified_ui": False,
            "extra_confirmation": False,
            "tutorial_hints": True,
            "objective_reminders": True,
            "auto_pause_menus": False,
            
            # Reading & Text
            "dyslexia_font": False,
            "reading_speed": 1.0,
            "text_background": False,
            "text_spacing": 1.0,
            "word_highlighting": False,
            
            # Game Difficulty Assists
            "auto_aim_assist": False,
            "enemy_health_bars": True,
            "simplified_combat": False,
            "unlimited_time": False,
            "checkpoint_frequency": 1.0,
        }
        
        # Color schemes for different types of color blindness
        self.colorblind_palettes = {
            ColorBlindType.NORMAL: {
                "health": (255, 100, 100),
                "mana": (100, 100, 255),
                "stamina": (255, 255, 100),
                "enemy": (255, 50, 50),
                "friendly": (100, 255, 100),
                "neutral": (200, 200, 200),
                "warning": (255, 180, 0),
                "error": (255, 100, 100),
                "success": (100, 255, 100),
                "info": (100, 200, 255)
            },
            ColorBlindType.PROTANOPIA: {  # Red-blind friendly
                "health": (255, 200, 0),
                "mana": (0, 150, 255),
                "stamina": (255, 255, 0),
                "enemy": (255, 150, 0),
                "friendly": (0, 200, 255),
                "neutral": (200, 200, 200),
                "warning": (255, 200, 0),
                "error": (255, 150, 0),
                "success": (0, 200, 255),
                "info": (150, 200, 255)
            },
            ColorBlindType.DEUTERANOPIA: {  # Green-blind friendly
                "health": (255, 100, 150),
                "mana": (100, 150, 255),
                "stamina": (255, 200, 0),
                "enemy": (255, 100, 150),
                "friendly": (100, 150, 255),
                "neutral": (200, 200, 200),
                "warning": (255, 200, 0),
                "error": (255, 100, 150),
                "success": (100, 150, 255),
                "info": (150, 180, 255)
            },
            ColorBlindType.TRITANOPIA: {  # Blue-blind friendly
                "health": (255, 100, 100),
                "mana": (255, 200, 100),
                "stamina": (200, 255, 100),
                "enemy": (255, 50, 50),
                "friendly": (200, 255, 100),
                "neutral": (200, 200, 200),
                "warning": (255, 200, 0),
                "error": (255, 100, 100),
                "success": (200, 255, 100),
                "info": (255, 200, 150)
            },
            ColorBlindType.MONOCHROME: {  # High contrast grayscale
                "health": (255, 255, 255),
                "mana": (200, 200, 200),
                "stamina": (150, 150, 150),
                "enemy": (255, 255, 255),
                "friendly": (180, 180, 180),
                "neutral": (128, 128, 128),
                "warning": (220, 220, 220),
                "error": (255, 255, 255),
                "success": (180, 180, 180),
                "info": (160, 160, 160)
            }
        }
        
        # High contrast color scheme
        self.high_contrast_colors = {
            "background": (0, 0, 0),
            "text": (255, 255, 255),
            "button": (255, 255, 255),
            "button_hover": (200, 200, 200),
            "selection": (255, 255, 0),
            "focus": (255, 255, 0),
            "warning": (255, 255, 0),
            "error": (255, 255, 255),
            "success": (255, 255, 255),
            "border": (255, 255, 255)
        }
        
        # Actions that can have hold-to-toggle behavior
        self.toggleable_actions = [
            "attack", "break_tile", "place_tile", "bridge_mode", 
            "attempt_theft", "use_item", "cast_primary_spell", "cast_secondary_spell"
        ]
        
        # Current settings
        self.current_settings = self.default_settings.copy()
        self.load_settings()
        
        # Runtime state
        self._flash_reduction_active = False
        self._last_flash_time = 0
        self._visual_cue_queue = []
        
    def get_color_palette(self) -> Dict[str, Tuple[int, int, int]]:
        """Get the current color palette based on accessibility settings"""
        colorblind_type = ColorBlindType(self.current_settings["colorblind_support"])
        
        if self.current_settings["high_contrast"]:
            return self.high_contrast_colors
        else:
            return self.colorblind_palettes[colorblind_type]
            
    def get_accessible_color(self, color_type: str) -> Tuple[int, int, int]:
        """Get an accessible color for a specific use case"""
        palette = self.get_color_palette()
        return palette.get(color_type, (255, 255, 255))
        
    def apply_text_scaling(self, base_size: int) -> int:
        """Apply text scaling based on accessibility settings"""
        scale = self.current_settings["text_scale"]
        if self.current_settings["large_text"]:
            scale *= 1.5
        return int(base_size * scale)
        
    def apply_ui_scaling(self, base_size: int) -> int:
        """Apply UI scaling for better visibility"""
        scale = self.current_settings["ui_scale"]
        return int(base_size * scale)
        
    def should_reduce_motion(self) -> bool:
        """Check if motion should be reduced"""
        return self.current_settings["motion_reduction"]
        
    def get_animation_speed(self) -> float:
        """Get the animation speed multiplier"""
        if self.should_reduce_motion():
            return 0.1  # Very slow animations
        return self.current_settings["animation_speed"]
        
    def should_show_visual_cues(self) -> bool:
        """Check if visual sound cues should be displayed"""
        return self.current_settings["visual_sound_cues"]
        
    def add_visual_sound_cue(self, sound_type: str, position: Tuple[int, int] = None):
        """Add a visual cue for a sound effect"""
        if self.should_show_visual_cues():
            cue = {
                "type": sound_type,
                "position": position,
                "timestamp": pygame.time.get_ticks(),
                "duration": 1000  # 1 second
            }
            self._visual_cue_queue.append(cue)
            
    def get_active_visual_cues(self) -> List[Dict[str, Any]]:
        """Get currently active visual sound cues"""
        current_time = pygame.time.get_ticks()
        active_cues = []
        
        for cue in self._visual_cue_queue[:]:
            if current_time - cue["timestamp"] < cue["duration"]:
                active_cues.append(cue)
            else:
                self._visual_cue_queue.remove(cue)
                
        return active_cues
        
    def should_reduce_flashing(self) -> bool:
        """Check if screen flashing should be reduced"""
        return self.current_settings["screen_flash_reduction"]
        
    def can_show_flash_effect(self) -> bool:
        """Check if a flash effect can be shown (rate limited)"""
        if not self.should_reduce_flashing():
            return True
            
        current_time = pygame.time.get_ticks()
        if current_time - self._last_flash_time > 500:  # Max 2 flashes per second
            self._last_flash_time = current_time
            return True
        return False
        
    def get_focus_outline_width(self) -> int:
        """Get the width for focus outlines"""
        if self.current_settings["focus_outline"]:
            return self.apply_ui_scaling(3)
        return 0
        
    def should_show_enemy_outlines(self) -> bool:
        """Check if enemy outlines should be shown"""
        return self.current_settings["enemy_outline"]
        
    def get_damage_number_scale(self) -> float:
        """Get the scaling for damage numbers"""
        return self.current_settings["damage_numbers_size"]
        
    def should_pause_on_focus_loss(self) -> bool:
        """Check if game should pause when window loses focus"""
        return self.current_settings["pause_on_focus_loss"]
        
    def is_simplified_ui_enabled(self) -> bool:
        """Check if simplified UI mode is enabled"""
        return self.current_settings["simplified_ui"]
        
    def needs_extra_confirmation(self) -> bool:
        """Check if extra confirmation dialogs should be shown"""
        return self.current_settings["extra_confirmation"]
        
    def should_show_tutorial_hints(self) -> bool:
        """Check if tutorial hints should be displayed"""
        return self.current_settings["tutorial_hints"]
        
    def is_action_toggleable(self, action: str) -> bool:
        """Check if an action should use hold-to-toggle behavior"""
        return action in self.current_settings.get("hold_to_toggle", {})
        
    def get_key_repeat_settings(self) -> Tuple[float, float]:
        """Get key repeat delay and rate"""
        delay = self.current_settings["key_repeat_delay"]
        rate = self.current_settings["key_repeat_rate"]
        return (delay, rate)
        
    def apply_mouse_sensitivity(self, movement: Tuple[int, int]) -> Tuple[int, int]:
        """Apply mouse sensitivity scaling"""
        sensitivity = self.current_settings["mouse_sensitivity"]
        return (int(movement[0] * sensitivity), int(movement[1] * sensitivity))
        
    def create_accessible_font(self, base_font: pygame.font.Font, size: int) -> pygame.font.Font:
        """Create an accessible font with proper sizing"""
        scaled_size = self.apply_text_scaling(size)
        
        if self.current_settings["dyslexia_font"]:
            # Try to use a dyslexia-friendly font
            try:
                return pygame.font.Font("fonts/OpenDyslexic-Regular.ttf", scaled_size)
            except:
                pass  # Fall back to system font
                
        return pygame.font.SysFont(None, scaled_size)
        
    def render_accessible_text(self, font: pygame.font.Font, text: str, 
                              color: Tuple[int, int, int] = None) -> pygame.Surface:
        """Render text with accessibility features"""
        if color is None:
            color = self.get_accessible_color("text")
            
        # Apply text background if enabled
        if self.current_settings["text_background"]:
            # Create text with background
            text_surface = font.render(text, True, color)
            bg_color = self.get_accessible_color("background")
            
            # Add padding
            padding = self.apply_ui_scaling(4)
            bg_surface = pygame.Surface((text_surface.get_width() + padding * 2, 
                                       text_surface.get_height() + padding * 2))
            bg_surface.fill(bg_color)
            bg_surface.blit(text_surface, (padding, padding))
            return bg_surface
        else:
            return font.render(text, True, color)
            
    def set_setting(self, key: str, value: Any):
        """Set an accessibility setting"""
        if key in self.current_settings:
            self.current_settings[key] = value
            
    def get_setting(self, key: str) -> Any:
        """Get an accessibility setting"""
        return self.current_settings.get(key, self.default_settings.get(key))
        
    def apply_preset(self, preset_name: str):
        """Apply an accessibility preset"""
        presets = {
            "visual_impairment": {
                "high_contrast": True,
                "large_text": True,
                "text_scale": 1.5,
                "ui_scale": 1.3,
                "enemy_outline": True,
                "focus_outline": True,
                "cursor_highlight": True,
                "damage_numbers_size": 1.5
            },
            "colorblind_friendly": {
                "colorblind_support": ColorBlindType.PROTANOPIA.value,
                "enemy_outline": True,
                "selection_highlight": True,
                "item_glow": True
            },
            "motor_impairment": {
                "sticky_keys": True,
                "key_repeat_delay": 1.0,
                "key_repeat_rate": 0.2,
                "one_handed_mode": True,
                "auto_pause_menus": True,
                "hold_to_toggle": {action: True for action in self.toggleable_actions}
            },
            "cognitive_support": {
                "simplified_ui": True,
                "extra_confirmation": True,
                "tutorial_hints": True,
                "objective_reminders": True,
                "pause_on_focus_loss": True,
                "unlimited_time": True
            },
            "photosensitive": {
                "screen_flash_reduction": True,
                "motion_reduction": True,
                "animation_speed": 0.5,
                "visual_sound_cues": False
            },
            "hearing_impairment": {
                "visual_sound_cues": True,
                "subtitles": True,
                "subtitle_size": 1.2,
                "sound_visualization": True
            }
        }
        
        if preset_name in presets:
            for key, value in presets[preset_name].items():
                self.current_settings[key] = value
                
    def save_settings(self):
        """Save accessibility settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save accessibility settings: {e}")
            
    def load_settings(self):
        """Load accessibility settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    for key, value in loaded.items():
                        if key in self.default_settings:
                            self.current_settings[key] = value
        except Exception as e:
            print(f"Failed to load accessibility settings: {e}")
            self.current_settings = self.default_settings.copy()
            
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.current_settings = self.default_settings.copy()
        
    def validate_settings(self) -> List[str]:
        """Validate current settings and return any issues"""
        issues = []
        
        # Check for conflicting settings
        if self.current_settings["motion_reduction"] and self.current_settings["animation_speed"] > 0.5:
            issues.append("Motion reduction enabled but animation speed is high")
            
        if self.current_settings["high_contrast"] and self.current_settings["colorblind_support"] != ColorBlindType.NORMAL.value:
            issues.append("High contrast may override colorblind support")
            
        return issues

# Global accessibility settings instance
accessibility_settings = AccessibilitySettings()

def get_accessibility_settings() -> AccessibilitySettings:
    """Get the global accessibility settings instance"""
    return accessibility_settings