"""
Font Settings Interface
Provides menu-based font size customization
"""

import pygame
from font_size_manager import get_font_manager, FontCategory
from ui_themes import get_ui_theme

class FontSettingsUI:
    """Menu interface for font size customization"""
    
    def __init__(self):
        self.font_manager = get_font_manager()
        self.ui_theme = get_ui_theme()
        self.active = False
        
        self.selected_category_index = 0
        self.selected_option_index = 0
        
        # Available categories for individual adjustment
        self.categories_list = list(FontCategory)
        
        # Menu options
        self.menu_options = [
            "global_scale",
            "category_adjustment", 
            "presets",
            "preview",
            "reset"
        ]
        
        self.menu_mode = "main"  # "main", "category", "presets"
        self.preview_text = "Sample text for preview - The quick brown fox jumps over the lazy dog."
        
    def handle_event(self, event) -> str:
        """Handle input events. Returns action string or None."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.menu_mode != "main":
                    self.menu_mode = "main"
                    return "mode_changed"
                else:
                    self.active = False
                    self.font_manager.save_settings()
                    return "close"
                    
            elif event.key == pygame.K_TAB:
                # Quick cycle between main menu options
                if self.menu_mode == "main":
                    self.selected_option_index = (self.selected_option_index + 1) % len(self.menu_options)
                    return "option_changed"
                    
            elif self.menu_mode == "main":
                return self._handle_main_input(event)
                
            elif self.menu_mode == "category":
                return self._handle_category_input(event)
                
            elif self.menu_mode == "presets":
                return self._handle_presets_input(event)
                
        return None
        
    def _handle_main_input(self, event) -> str:
        """Handle input in main menu mode"""
        if event.key == pygame.K_UP:
            self.selected_option_index = (self.selected_option_index - 1) % len(self.menu_options)
            return "option_changed"
            
        elif event.key == pygame.K_DOWN:
            self.selected_option_index = (self.selected_option_index + 1) % len(self.menu_options)
            return "option_changed"
            
        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            return self._adjust_main_option(event.key == pygame.K_RIGHT)
            
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            return self._activate_main_option()
            
        return None
        
    def _handle_category_input(self, event) -> str:
        """Handle input in category adjustment mode"""
        if event.key == pygame.K_UP:
            self.selected_category_index = (self.selected_category_index - 1) % len(self.categories_list)
            return "category_changed"
            
        elif event.key == pygame.K_DOWN:
            self.selected_category_index = (self.selected_category_index + 1) % len(self.categories_list)
            return "category_changed"
            
        elif event.key == pygame.K_LEFT:
            category = self.categories_list[self.selected_category_index]
            self.font_manager.decrease_category_size(category, 0.1)
            return "font_adjusted"
            
        elif event.key == pygame.K_RIGHT:
            category = self.categories_list[self.selected_category_index]
            self.font_manager.increase_category_size(category, 0.1)
            return "font_adjusted"
            
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Reset selected category to default
            category = self.categories_list[self.selected_category_index]
            self.font_manager.reset_category_to_default(category)
            return "category_reset"
            
        return None
        
    def _handle_presets_input(self, event) -> str:
        """Handle input in presets mode"""
        presets = self.font_manager.get_available_presets()
        
        if event.key == pygame.K_UP:
            self.selected_preset_index = (getattr(self, 'selected_preset_index', 0) - 1) % len(presets)
            return "preset_changed"
            
        elif event.key == pygame.K_DOWN:
            self.selected_preset_index = (getattr(self, 'selected_preset_index', 0) + 1) % len(presets)
            return "preset_changed"
            
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Apply selected preset
            preset_name = presets[getattr(self, 'selected_preset_index', 0)]
            self.font_manager.apply_preset(preset_name)
            self.font_manager.save_settings()
            return "preset_applied"
            
        return None
        
    def _adjust_main_option(self, increase: bool) -> str:
        """Adjust the currently selected main option"""
        option = self.menu_options[self.selected_option_index]
        
        if option == "global_scale":
            if increase:
                self.font_manager.increase_global_size(0.1)
            else:
                self.font_manager.decrease_global_size(0.1)
            self.font_manager.save_settings()
            return "global_scale_adjusted"
            
        return None
        
    def _activate_main_option(self) -> str:
        """Activate the currently selected main option"""
        option = self.menu_options[self.selected_option_index]
        
        if option == "category_adjustment":
            self.menu_mode = "category"
            return "entered_category_mode"
            
        elif option == "presets":
            self.menu_mode = "presets"
            if not hasattr(self, 'selected_preset_index'):
                self.selected_preset_index = 1  # Default preset
            return "entered_presets_mode"
            
        elif option == "reset":
            self.font_manager.reset_all_to_defaults()
            self.font_manager.save_settings()
            return "all_fonts_reset"
            
        return None
        
    def render(self, screen: pygame.Surface, font: pygame.font.Font):
        """Render the font settings interface"""
        colors = self.ui_theme.get_all_colors()
        
        # Clear screen with theme background
        screen.fill(colors.get("ui_bg_primary", (40, 40, 40)))
        
        # Title
        title_font = self.font_manager.get_font(FontCategory.TITLE_TEXT)
        title_text = title_font.render("Font Size Settings", True, colors.get("text_accent", (255, 215, 0)))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 40))
        screen.blit(title_text, title_rect)
        
        # Mode indicator
        mode_font = self.font_manager.get_font(FontCategory.UI_TEXT)
        mode_text = f"Mode: {self.menu_mode.title()}"
        mode_surface = mode_font.render(mode_text, True, colors.get("text_secondary", (200, 200, 200)))
        mode_rect = mode_surface.get_rect(center=(screen.get_width() // 2, 70))
        screen.blit(mode_surface, mode_rect)
        
        # Render based on current mode
        if self.menu_mode == "main":
            self._render_main_menu(screen, colors)
        elif self.menu_mode == "category":
            self._render_category_menu(screen, colors)
        elif self.menu_mode == "presets":
            self._render_presets_menu(screen, colors)
            
    def _render_main_menu(self, screen: pygame.Surface, colors: dict):
        """Render main font settings menu"""
        menu_font = self.font_manager.get_font(FontCategory.MENU_TEXT)
        
        # Instructions
        instructions = [
            "↑/↓ - Navigate options",
            "←/→ - Adjust global scale",
            "ENTER - Select option",
            "TAB - Quick navigate",
            "ESC - Save and exit"
        ]
        
        y_pos = 110
        for instruction in instructions:
            text_surface = menu_font.render(instruction, True, colors.get("text_secondary", (200, 200, 200)))
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25
            
        # Main options
        y_pos = 240
        for i, option in enumerate(self.menu_options):
            if option == "global_scale":
                text = f"Global Scale: {self.font_manager.get_global_scale():.1f}x"
            elif option == "category_adjustment":
                text = "Individual Categories"
            elif option == "presets":
                text = "Font Presets"
            elif option == "preview":
                text = "Font Preview"
            elif option == "reset":
                text = "Reset All to Defaults"
            else:
                text = option.replace("_", " ").title()
                
            # Highlight selected option
            if i == self.selected_option_index:
                highlight_rect = pygame.Rect(50, y_pos - 5, screen.get_width() - 100, 35)
                pygame.draw.rect(screen, colors.get("ui_bg_accent", (60, 60, 60)), highlight_rect)
                text_color = colors.get("text_accent", (255, 215, 0))
            else:
                text_color = colors.get("text_primary", (255, 255, 255))
                
            text_surface = menu_font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos + 12))
            screen.blit(text_surface, text_rect)
            
            y_pos += 45
            
        # Font preview section
        if self.selected_option_index == 3:  # Preview option selected
            self._render_font_preview(screen, colors, y_pos + 20)
            
    def _render_category_menu(self, screen: pygame.Surface, colors: dict):
        """Render individual category adjustment menu"""
        menu_font = self.font_manager.get_font(FontCategory.MENU_TEXT)
        
        # Instructions
        instructions = [
            "Individual Font Category Adjustment",
            "↑/↓ - Select category",
            "←/→ - Adjust size",
            "ENTER - Reset to default",
            "ESC - Back to main menu"
        ]
        
        y_pos = 100
        for i, instruction in enumerate(instructions):
            color = colors.get("text_accent", (255, 215, 0)) if i == 0 else colors.get("text_secondary", (200, 200, 200))
            text_surface = menu_font.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25
            
        # Category list
        y_pos = 220
        for i, category in enumerate(self.categories_list):
            category_name = category.value.replace("_", " ").title()
            scale = self.font_manager.get_category_scale(category)
            size = self.font_manager.get_font_size(category)
            
            text = f"{category_name}: {scale:.1f}x ({size}px)"
            
            # Highlight selected category
            if i == self.selected_category_index:
                highlight_rect = pygame.Rect(50, y_pos - 5, screen.get_width() - 100, 30)
                pygame.draw.rect(screen, colors.get("ui_bg_accent", (60, 60, 60)), highlight_rect)
                text_color = colors.get("text_accent", (255, 215, 0))
            else:
                text_color = colors.get("text_primary", (255, 255, 255))
                
            text_surface = menu_font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos + 10))
            screen.blit(text_surface, text_rect)
            
            y_pos += 35
            
    def _render_presets_menu(self, screen: pygame.Surface, colors: dict):
        """Render font presets menu"""
        menu_font = self.font_manager.get_font(FontCategory.MENU_TEXT)
        
        # Instructions
        instructions = [
            "Font Size Presets",
            "↑/↓ - Select preset",
            "ENTER - Apply preset",
            "ESC - Back to main menu"
        ]
        
        y_pos = 100
        for i, instruction in enumerate(instructions):
            color = colors.get("text_accent", (255, 215, 0)) if i == 0 else colors.get("text_secondary", (200, 200, 200))
            text_surface = menu_font.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25
            
        # Preset descriptions
        preset_descriptions = {
            "Small": "Compact fonts for more screen space",
            "Default": "Standard font sizes",
            "Large": "Larger fonts for better readability", 
            "Extra Large": "Very large fonts",
            "Low Vision": "Optimized for visual accessibility",
            "Reading Focused": "Optimized for text-heavy content"
        }
        
        # Preset list
        y_pos = 200
        presets = self.font_manager.get_available_presets()
        selected_index = getattr(self, 'selected_preset_index', 1)
        
        for i, preset_name in enumerate(presets):
            description = preset_descriptions.get(preset_name, "")
            
            # Highlight selected preset
            if i == selected_index:
                highlight_rect = pygame.Rect(50, y_pos - 5, screen.get_width() - 100, 50)
                pygame.draw.rect(screen, colors.get("ui_bg_accent", (60, 60, 60)), highlight_rect)
                text_color = colors.get("text_accent", (255, 215, 0))
            else:
                text_color = colors.get("text_primary", (255, 255, 255))
                
            # Preset name
            name_surface = menu_font.render(preset_name, True, text_color)
            name_rect = name_surface.get_rect(center=(screen.get_width() // 2, y_pos + 10))
            screen.blit(name_surface, name_rect)
            
            # Description
            desc_color = colors.get("text_secondary", (200, 200, 200))
            desc_surface = menu_font.render(description, True, desc_color)
            desc_rect = desc_surface.get_rect(center=(screen.get_width() // 2, y_pos + 30))
            screen.blit(desc_surface, desc_rect)
            
            y_pos += 60
            
    def _render_font_preview(self, screen: pygame.Surface, colors: dict, start_y: int):
        """Render font preview showing all categories"""
        preview_samples = [
            (FontCategory.TITLE_TEXT, "Title Text Sample"),
            (FontCategory.MENU_TEXT, "Menu Text Sample"),
            (FontCategory.UI_TEXT, "General UI Text Sample"),
            (FontCategory.HUD_TEXT, "HUD: HP 100/100 MP 50/50"),
            (FontCategory.CONSOLE_TEXT, "Console: Player gained 50 XP"),
            (FontCategory.TOOLTIP_TEXT, "Tooltip: This is a helpful tooltip")
        ]
        
        y_pos = start_y
        for category, sample_text in preview_samples:
            category_font = self.font_manager.get_font(category)
            
            # Category label
            label_font = self.font_manager.get_font(FontCategory.UI_TEXT)
            label_text = f"{category.value.replace('_', ' ').title()}:"
            label_surface = label_font.render(label_text, True, colors.get("text_secondary", (200, 200, 200)))
            screen.blit(label_surface, (50, y_pos))
            
            # Sample text
            sample_surface = category_font.render(sample_text, True, colors.get("text_primary", (255, 255, 255)))
            screen.blit(sample_surface, (220, y_pos))
            
            y_pos += max(30, category_font.get_height() + 5)

# Global font settings UI instance
font_settings_ui = None

def get_font_settings_ui() -> FontSettingsUI:
    """Get the global font settings UI instance"""
    global font_settings_ui
    if font_settings_ui is None:
        font_settings_ui = FontSettingsUI()
    return font_settings_ui
