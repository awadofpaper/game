"""
Accessibility Settings UI
Comprehensive interface for accessibility customization
"""

import pygame
import time
from typing import Dict, Any, List, Optional, Tuple
from accessibility_settings import get_accessibility_settings, ColorBlindType

class AccessibilitySettingsUI:
    def __init__(self):
        self.settings = get_accessibility_settings()
        self.active = False
        self.selected_tab = 0
        self.selected_item = 0
        self.scroll_offset = 0
        
        # UI Configuration
        self.tabs = ["Visual", "Audio", "Input", "Cognitive", "Presets", "Advanced"]
        self.max_visible_items = 12
        
        # Colors (will be updated based on accessibility settings)
        self.update_colors()
        
        # Menu structure for each tab
        self.menu_structure = {
            0: [  # Visual Tab
                {"type": "header", "text": "═══ COLOR & CONTRAST ═══"},
                {"type": "dropdown", "key": "colorblind_support", "text": "Colorblind Support", 
                 "options": [cb_type.value for cb_type in ColorBlindType]},
                {"type": "toggle", "key": "high_contrast", "text": "High Contrast Mode"},
                {"type": "toggle", "key": "enemy_outline", "text": "Enemy Outlines"},
                {"type": "toggle", "key": "focus_outline", "text": "Focus Outlines"},
                {"type": "toggle", "key": "cursor_highlight", "text": "Cursor Highlighting"},
                
                {"type": "header", "text": "═══ TEXT & UI ═══"},
                {"type": "toggle", "key": "large_text", "text": "Large Text"},
                {"type": "slider", "key": "text_scale", "text": "Text Size", 
                 "min": 0.5, "max": 3.0, "step": 0.1, "format": "{}x"},
                {"type": "slider", "key": "ui_scale", "text": "UI Scale", 
                 "min": 0.5, "max": 2.5, "step": 0.1, "format": "{}x"},
                {"type": "toggle", "key": "text_background", "text": "Text Backgrounds"},
                {"type": "toggle", "key": "dyslexia_font", "text": "Dyslexia-Friendly Font"},
                
                {"type": "header", "text": "═══ MOTION & EFFECTS ═══"},
                {"type": "toggle", "key": "screen_flash_reduction", "text": "Reduce Screen Flashing"},
                {"type": "toggle", "key": "motion_reduction", "text": "Reduce Motion"},
                {"type": "slider", "key": "animation_speed", "text": "Animation Speed", 
                 "min": 0.1, "max": 2.0, "step": 0.1, "format": "{}x"},
                {"type": "slider", "key": "damage_numbers_size", "text": "Damage Numbers Size", 
                 "min": 0.5, "max": 3.0, "step": 0.1, "format": "{}x"}
            ],
            
            1: [  # Audio Tab
                {"type": "header", "text": "═══ AUDIO ACCESSIBILITY ═══"},
                {"type": "toggle", "key": "visual_sound_cues", "text": "Visual Sound Cues"},
                {"type": "toggle", "key": "sound_visualization", "text": "Sound Visualization"},
                {"type": "info", "text": "Visual indicators for audio events"},
                
                {"type": "header", "text": "═══ SUBTITLES ═══"},
                {"type": "toggle", "key": "subtitles", "text": "Enable Subtitles"},
                {"type": "slider", "key": "subtitle_size", "text": "Subtitle Size", 
                 "min": 0.5, "max": 2.5, "step": 0.1, "format": "{}x"},
                {"type": "toggle", "key": "audio_descriptions", "text": "Audio Descriptions"},
                
                {"type": "header", "text": "═══ INFORMATION ═══"},
                {"type": "info", "text": "Visual sound cues show on-screen"},
                {"type": "info", "text": "indicators for important sounds"},
                {"type": "info", "text": "like enemy attacks or item pickups"}
            ],
            
            2: [  # Input Tab
                {"type": "header", "text": "═══ INPUT ASSISTANCE ═══"},
                {"type": "toggle", "key": "sticky_keys", "text": "Sticky Keys"},
                {"type": "toggle", "key": "one_handed_mode", "text": "One-Handed Mode"},
                {"type": "slider", "key": "key_repeat_delay", "text": "Key Repeat Delay", 
                 "min": 0.1, "max": 2.0, "step": 0.1, "format": "{:.1f}s"},
                {"type": "slider", "key": "key_repeat_rate", "text": "Key Repeat Rate", 
                 "min": 0.05, "max": 0.5, "step": 0.05, "format": "{:.2f}s"},
                
                {"type": "header", "text": "═══ MOUSE SETTINGS ═══"},
                {"type": "slider", "key": "mouse_sensitivity", "text": "Mouse Sensitivity", 
                 "min": 0.1, "max": 3.0, "step": 0.1, "format": "{}x"},
                
                {"type": "header", "text": "═══ GAME ASSISTS ═══"},
                {"type": "toggle", "key": "auto_aim_assist", "text": "Auto-Aim Assist"},
                {"type": "toggle", "key": "simplified_combat", "text": "Simplified Combat"},
                {"type": "toggle", "key": "auto_pause_menus", "text": "Auto-Pause in Menus"}
            ],
            
            3: [  # Cognitive Tab
                {"type": "header", "text": "═══ INTERFACE SIMPLIFICATION ═══"},
                {"type": "toggle", "key": "simplified_ui", "text": "Simplified UI"},
                {"type": "toggle", "key": "extra_confirmation", "text": "Extra Confirmations"},
                {"type": "toggle", "key": "pause_on_focus_loss", "text": "Pause When Window Loses Focus"},
                
                {"type": "header", "text": "═══ GUIDANCE & HELP ═══"},
                {"type": "toggle", "key": "tutorial_hints", "text": "Tutorial Hints"},
                {"type": "toggle", "key": "objective_reminders", "text": "Objective Reminders"},
                {"type": "toggle", "key": "enemy_health_bars", "text": "Show Enemy Health Bars"},
                
                {"type": "header", "text": "═══ TIME & DIFFICULTY ═══"},
                {"type": "toggle", "key": "unlimited_time", "text": "No Time Limits"},
                {"type": "slider", "key": "checkpoint_frequency", "text": "Save Frequency", 
                 "min": 0.5, "max": 3.0, "step": 0.5, "format": "{}x"},
                {"type": "slider", "key": "reading_speed", "text": "Text Display Speed", 
                 "min": 0.5, "max": 3.0, "step": 0.1, "format": "{}x"}
            ],
            
            4: [  # Presets Tab
                {"type": "header", "text": "═══ ACCESSIBILITY PRESETS ═══"},
                {"type": "button", "key": "visual_impairment", "text": "Visual Impairment Support"},
                {"type": "info", "text": "High contrast, large text, outlines"},
                
                {"type": "button", "key": "colorblind_friendly", "text": "Colorblind-Friendly"},
                {"type": "info", "text": "Adjusted colors and extra visual cues"},
                
                {"type": "button", "key": "motor_impairment", "text": "Motor Impairment Support"},
                {"type": "info", "text": "Sticky keys, auto-pause, hold-to-toggle"},
                
                {"type": "button", "key": "cognitive_support", "text": "Cognitive Support"},
                {"type": "info", "text": "Simplified UI, extra help, no time limits"},
                
                {"type": "button", "key": "photosensitive", "text": "Photosensitive Protection"},
                {"type": "info", "text": "Reduced flashing and motion"},
                
                {"type": "button", "key": "hearing_impairment", "text": "Hearing Impairment Support"},
                {"type": "info", "text": "Visual sound cues and subtitles"},
                
                {"type": "header", "text": "═══ RESET OPTIONS ═══"},
                {"type": "button", "key": "reset_defaults", "text": "Reset All to Defaults"}
            ],
            
            5: [  # Advanced Tab
                {"type": "header", "text": "═══ ADVANCED OPTIONS ═══"},
                {"type": "slider", "key": "text_spacing", "text": "Text Line Spacing", 
                 "min": 0.8, "max": 2.0, "step": 0.1, "format": "{}x"},
                {"type": "toggle", "key": "word_highlighting", "text": "Word Highlighting"},
                {"type": "toggle", "key": "selection_highlight", "text": "Enhanced Selection"},
                {"type": "toggle", "key": "item_glow", "text": "Item Glow Effects"},
                
                {"type": "header", "text": "═══ CURRENT STATUS ═══"},
                {"type": "info", "text": "Colorblind: " + self.settings.get_setting("colorblind_support")},
                {"type": "info", "text": "High Contrast: " + str(self.settings.get_setting("high_contrast"))},
                {"type": "info", "text": "Text Scale: " + f"{self.settings.get_setting('text_scale'):.1f}x"},
                
                {"type": "header", "text": "═══ HELP ═══"},
                {"type": "info", "text": "F9: Open Accessibility Settings"},
                {"type": "info", "text": "Tab: Switch categories | ESC: Close"},
                {"type": "info", "text": "Arrow keys navigate | Enter selects"}
            ]
        }
        
        # State tracking
        self.last_input_time = 0
        self.pending_changes = False
        
    def update_colors(self):
        """Update UI colors based on accessibility settings"""
        if self.settings.get_setting("high_contrast"):
            self.colors = {
                "bg": (0, 0, 0),
                "panel": (20, 20, 20),
                "tab_active": (255, 255, 255),
                "tab_inactive": (128, 128, 128),
                "text": (255, 255, 255),
                "text_dim": (200, 200, 200),
                "accent": (255, 255, 0),
                "button": (255, 255, 255),
                "button_hover": (200, 200, 200),
                "slider_track": (128, 128, 128),
                "slider_handle": (255, 255, 255),
                "warning": (255, 255, 0),
                "success": (255, 255, 255),
                "error": (255, 255, 255)
            }
        else:
            palette = self.settings.get_color_palette()
            self.colors = {
                "bg": (30, 30, 40),
                "panel": (50, 50, 60),
                "tab_active": (80, 140, 200),
                "tab_inactive": (60, 60, 70),
                "text": palette.get("info", (255, 255, 255)),
                "text_dim": (180, 180, 180),
                "accent": palette.get("info", (120, 200, 255)),
                "button": (70, 130, 180),
                "button_hover": (90, 150, 200),
                "slider_track": (80, 80, 90),
                "slider_handle": (120, 160, 200),
                "warning": palette.get("warning", (255, 200, 100)),
                "success": palette.get("success", (100, 255, 150)),
                "error": palette.get("error", (255, 120, 120))
            }
            
    def toggle(self):
        """Toggle the accessibility settings UI"""
        self.active = not self.active
        if self.active:
            self.selected_item = 0
            self.scroll_offset = 0
            self.update_colors()
            
    def handle_input(self, event) -> bool:
        """Handle input events. Returns True if event was consumed."""
        if not self.active:
            return False
            
        current_time = time.time()
        self.last_input_time = current_time
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                if self.pending_changes:
                    self.settings.save_settings()
                    self.pending_changes = False
                return True
                
            elif event.key == pygame.K_TAB:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self.selected_tab = (self.selected_tab - 1) % len(self.tabs)
                else:
                    self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
                self.selected_item = 0
                self.scroll_offset = 0
                return True
                
            elif event.key == pygame.K_UP:
                self._navigate_up()
                return True
                
            elif event.key == pygame.K_DOWN:
                self._navigate_down()
                return True
                
            elif event.key == pygame.K_LEFT:
                self._adjust_value(-1)
                return True
                
            elif event.key == pygame.K_RIGHT:
                self._adjust_value(1)
                return True
                
            elif event.key == pygame.K_RETURN:
                self._activate_item()
                return True
                
        return False
        
    def _navigate_up(self):
        """Navigate to previous menu item"""
        menu_items = self.menu_structure[self.selected_tab]
        interactive_items = [i for i, item in enumerate(menu_items) 
                           if item["type"] not in ["header", "info"]]
        
        if interactive_items:
            if self.selected_item in interactive_items:
                current_idx = interactive_items.index(self.selected_item)
                new_idx = (current_idx - 1) % len(interactive_items)
                self.selected_item = interactive_items[new_idx]
            else:
                self.selected_item = interactive_items[0]
            self._update_scroll()
            
    def _navigate_down(self):
        """Navigate to next menu item"""
        menu_items = self.menu_structure[self.selected_tab]
        interactive_items = [i for i, item in enumerate(menu_items) 
                           if item["type"] not in ["header", "info"]]
        
        if interactive_items:
            if self.selected_item in interactive_items:
                current_idx = interactive_items.index(self.selected_item)
                new_idx = (current_idx + 1) % len(interactive_items)
                self.selected_item = interactive_items[new_idx]
            else:
                self.selected_item = interactive_items[0]
            self._update_scroll()
            
    def _update_scroll(self):
        """Update scroll offset to keep selected item visible"""
        if self.selected_item < self.scroll_offset:
            self.scroll_offset = self.selected_item
        elif self.selected_item >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_item - self.max_visible_items + 1
            
    def _adjust_value(self, direction: int):
        """Adjust the value of the current item"""
        menu_items = self.menu_structure[self.selected_tab]
        if self.selected_item < len(menu_items):
            item = menu_items[self.selected_item]
            
            if item["type"] == "toggle":
                current = self.settings.get_setting(item["key"])
                self.settings.set_setting(item["key"], not current)
                self.pending_changes = True
                self.update_colors()  # Update colors if accessibility settings changed
                
            elif item["type"] == "slider":
                current = self.settings.get_setting(item["key"])
                step = item.get("step", 1)
                min_val = item.get("min", 0)
                max_val = item.get("max", 100)
                
                new_val = current + (direction * step)
                new_val = max(min_val, min(max_val, new_val))
                
                self.settings.set_setting(item["key"], new_val)
                self.pending_changes = True
                
            elif item["type"] == "dropdown":
                options = item["options"]
                current = self.settings.get_setting(item["key"])
                try:
                    current_idx = options.index(current)
                    new_idx = (current_idx + direction) % len(options)
                    self.settings.set_setting(item["key"], options[new_idx])
                    self.pending_changes = True
                    self.update_colors()  # Update colors for colorblind support changes
                except (ValueError, IndexError):
                    pass
                    
    def _activate_item(self):
        """Activate/click the current item"""
        menu_items = self.menu_structure[self.selected_tab]
        if self.selected_item < len(menu_items):
            item = menu_items[self.selected_item]
            
            if item["type"] == "button":
                key = item["key"]
                if key in ["visual_impairment", "colorblind_friendly", "motor_impairment", 
                          "cognitive_support", "photosensitive", "hearing_impairment"]:
                    self.settings.apply_preset(key)
                    self.pending_changes = True
                    self.update_colors()
                elif key == "reset_defaults":
                    self.settings.reset_to_defaults()
                    self.pending_changes = True
                    self.update_colors()
                    
    def render(self, screen: pygame.Surface, font: pygame.font.Font):
        """Render the accessibility settings UI"""
        if not self.active:
            return
            
        # Use accessibility-aware rendering
        accessible_font = self.settings.create_accessible_font(font, 24)
        
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))
        
        # Main panel - adjust size based on UI scaling
        base_width = 850
        base_height = 650
        panel_width = min(self.settings.apply_ui_scaling(base_width), screen_width - 80)
        panel_height = min(self.settings.apply_ui_scaling(base_height), screen_height - 80)
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, self.colors["bg"], panel_rect)
        
        # Focus outline if enabled
        outline_width = self.settings.get_focus_outline_width()
        if outline_width > 0:
            pygame.draw.rect(screen, self.colors["accent"], panel_rect, outline_width)
        else:
            pygame.draw.rect(screen, self.colors["accent"], panel_rect, 3)
        
        # Title
        title_text = self.settings.render_accessible_text(accessible_font, 
                                                         "Accessibility Settings", 
                                                         self.colors["text"])
        title_x = panel_x + (panel_width - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, panel_y + 15))
        
        # Tabs
        tab_y = panel_y + 50
        tab_width = panel_width // len(self.tabs)
        
        for i, tab_name in enumerate(self.tabs):
            tab_x = panel_x + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 35)
            
            color = self.colors["tab_active"] if i == self.selected_tab else self.colors["tab_inactive"]
            pygame.draw.rect(screen, color, tab_rect)
            
            # Tab border
            border_width = 3 if i == self.selected_tab else 1
            pygame.draw.rect(screen, self.colors["accent"], tab_rect, border_width)
            
            tab_text = self.settings.render_accessible_text(accessible_font, tab_name, self.colors["text"])
            text_x = tab_x + (tab_width - tab_text.get_width()) // 2
            text_y = tab_y + (35 - tab_text.get_height()) // 2
            screen.blit(tab_text, (text_x, text_y))
        
        # Content area
        content_y = tab_y + 40
        content_height = panel_height - 100
        content_rect = pygame.Rect(panel_x + 10, content_y, panel_width - 20, content_height)
        
        self._render_tab_content(screen, accessible_font, content_rect)
        
        # Status bar
        status_y = panel_y + panel_height - 25
        if self.pending_changes:
            status_text = "Changes pending | ESC to save and close"
            color = self.colors["warning"]
        else:
            status_text = "ESC to close | Tab to switch | Arrow keys to navigate"
            color = self.colors["text_dim"]
            
        status_surface = self.settings.render_accessible_text(accessible_font, status_text, color)
        screen.blit(status_surface, (panel_x + 10, status_y))
        
    def _render_tab_content(self, screen: pygame.Surface, font: pygame.font.Font, content_rect: pygame.Rect):
        """Render the content of the current tab"""
        menu_items = self.menu_structure[self.selected_tab]
        item_height = self.settings.apply_ui_scaling(35)
        
        visible_start = self.scroll_offset
        visible_end = min(len(menu_items), visible_start + self.max_visible_items)
        
        for i in range(visible_start, visible_end):
            item = menu_items[i]
            y_pos = content_rect.y + (i - visible_start) * item_height
            
            # Highlight selected item
            if i == self.selected_item:
                highlight_rect = pygame.Rect(content_rect.x, y_pos, content_rect.width, item_height)
                pygame.draw.rect(screen, self.colors["panel"], highlight_rect)
                
                # Focus outline if enabled
                outline_width = self.settings.get_focus_outline_width()
                if outline_width > 0:
                    pygame.draw.rect(screen, self.colors["accent"], highlight_rect, outline_width)
                
            self._render_menu_item(screen, font, item, content_rect.x, y_pos, content_rect.width)
            
    def _render_menu_item(self, screen: pygame.Surface, font: pygame.font.Font, 
                         item: Dict[str, Any], x: int, y: int, width: int):
        """Render a single menu item with accessibility features"""
        item_type = item["type"]
        
        if item_type == "header":
            text = self.settings.render_accessible_text(font, item["text"], self.colors["accent"])
            screen.blit(text, (x + 10, y + 8))
            
        elif item_type == "info":
            text = self.settings.render_accessible_text(font, item["text"], self.colors["text_dim"])
            screen.blit(text, (x + 20, y + 8))
            
        elif item_type == "toggle":
            # Label
            label = self.settings.render_accessible_text(font, item["text"], self.colors["text"])
            screen.blit(label, (x + 10, y + 8))
            
            # Toggle switch with enhanced visibility
            value = self.settings.get_setting(item["key"])
            switch_x = x + width - self.settings.apply_ui_scaling(80)
            switch_width = self.settings.apply_ui_scaling(60)
            switch_height = self.settings.apply_ui_scaling(20)
            switch_rect = pygame.Rect(switch_x, y + 8, switch_width, switch_height)
            
            switch_color = self.colors["success"] if value else self.colors["slider_track"]
            pygame.draw.rect(screen, switch_color, switch_rect, border_radius=10)
            
            # Handle position
            handle_size = self.settings.apply_ui_scaling(16)
            handle_x = switch_x + (switch_width - handle_size - 4 if value else 4)
            handle_rect = pygame.Rect(handle_x, y + 10, handle_size, handle_size)
            pygame.draw.circle(screen, self.colors["text"], handle_rect.center, handle_size // 2)
            
        elif item_type == "slider":
            # Label
            label = self.settings.render_accessible_text(font, item["text"], self.colors["text"])
            screen.blit(label, (x + 10, y + 8))
            
            # Value
            value = self.settings.get_setting(item["key"])
            format_str = item.get("format", "{}")
            value_text = format_str.format(value)
            value_surface = self.settings.render_accessible_text(font, value_text, self.colors["accent"])
            screen.blit(value_surface, (x + width - 120, y + 8))
            
            # Slider track with better visibility
            slider_x = x + 200
            slider_width = width - 340
            track_height = self.settings.apply_ui_scaling(8)
            track_rect = pygame.Rect(slider_x, y + 15, slider_width, track_height)
            pygame.draw.rect(screen, self.colors["slider_track"], track_rect)
            
            # Slider handle
            min_val = item.get("min", 0)
            max_val = item.get("max", 100)
            if max_val > min_val:
                progress = (value - min_val) / (max_val - min_val)
                handle_x = slider_x + int(progress * slider_width)
                handle_size = self.settings.apply_ui_scaling(12)
                pygame.draw.circle(screen, self.colors["slider_handle"], 
                                 (handle_x, y + 19), handle_size)
                
        elif item_type == "dropdown":
            # Label
            label = self.settings.render_accessible_text(font, item["text"], self.colors["text"])
            screen.blit(label, (x + 10, y + 8))
            
            # Current value with better contrast
            value = self.settings.get_setting(item["key"])
            value_surface = self.settings.render_accessible_text(font, str(value), self.colors["accent"])
            value_x = x + width - value_surface.get_width() - 30
            screen.blit(value_surface, (value_x, y + 8))
            
            # Arrow indicators
            arrow_size = self.settings.apply_ui_scaling(15)
            arrow_left = self.settings.render_accessible_text(font, "◀", self.colors["text_dim"])
            arrow_right = self.settings.render_accessible_text(font, "▶", self.colors["text_dim"])
            screen.blit(arrow_left, (value_x - 25, y + 8))
            screen.blit(arrow_right, (x + width - 20, y + 8))
            
        elif item_type == "button":
            # Button background with accessibility considerations
            button_height = self.settings.apply_ui_scaling(30)
            button_rect = pygame.Rect(x + 10, y + 5, width - 20, button_height)
            
            button_color = self.colors["button_hover"] if item == self.selected_item else self.colors["button"]
            pygame.draw.rect(screen, button_color, button_rect, border_radius=5)
            
            # Button border for better visibility
            border_width = self.settings.get_focus_outline_width() or 2
            pygame.draw.rect(screen, self.colors["accent"], button_rect, border_width)
            
            # Button text
            button_text = self.settings.render_accessible_text(font, item["text"], self.colors["text"])
            text_x = x + (width - button_text.get_width()) // 2
            text_y = y + (button_height - button_text.get_height()) // 2 + 5
            screen.blit(button_text, (text_x, text_y))

# Global UI instance
accessibility_ui = AccessibilitySettingsUI()

def get_accessibility_ui() -> AccessibilitySettingsUI:
    """Get the global accessibility UI instance"""
    return accessibility_ui