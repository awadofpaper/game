"""
Performance Settings User Interface
Interactive performance monitoring and configuration
"""

import pygame
import math
from performance_manager import get_performance_manager, PerformancePreset
from ui_themes import get_ui_theme
from font_size_manager import get_font_manager, FontCategory

class PerformanceSettingsUI:
    """Interactive UI for performance monitoring and settings"""
    
    def __init__(self):
        self.performance_manager = get_performance_manager()
        self.ui_theme = get_ui_theme()
        self.font_manager = get_font_manager()
        
        self.selected_option_index = 0
        self.selected_setting_index = 0
        
        # Mouse tracking
        self.mouse_pos = None
        self.mouse_click_pos = None
        self.menu_item_rects = []  # Store clickable areas
        
        # Menu modes
        self.menu_options = [
            "performance_presets",
            "detailed_settings",
            "system_monitor",
            "auto_optimization",
            "system_info"
        ]
        
        self.menu_mode = "main"  # "main", "presets", "settings", "monitor", "auto", "system"
        self.selected_preset_index = 0
        
        # Detailed settings categories
        self.settings_categories = [
            ("Graphics", ["target_fps", "vsync", "particle_density", "shadow_quality", "lighting_quality", "texture_quality"]),
            ("Rendering", ["max_visible_entities", "max_particles", "render_distance", "ui_animation_speed"]),
            ("Performance", ["ai_update_interval", "physics_update_interval", "weather_update_interval"]),
            ("Memory", ["auto_cleanup_interval", "cache_size_limit", "garbage_collection_frequency"]),
            ("Advanced", ["multi_threading", "occlusion_culling", "frustum_culling", "batched_rendering"])
        ]
        self.selected_category_index = 0
        
        # Monitor display options
        self.monitor_options = ["fps_graph", "memory_usage", "frame_times", "system_stats"]
        self.selected_monitor_index = 0
        
    def handle_event(self, event) -> str:
        """Handle input events. Returns action string or None."""
        if event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_mouse_click(event)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.menu_mode != "main":
                    self.menu_mode = "main"
                    return "mode_changed"
                else:
                    return "close"
                    
            elif event.key == pygame.K_TAB:
                # Quick cycle between main menu options
                if self.menu_mode == "main":
                    self.selected_option_index = (self.selected_option_index + 1) % len(self.menu_options)
                    return "option_changed"
                    
            elif self.menu_mode == "main":
                return self._handle_main_input(event)
                
            elif self.menu_mode == "presets":
                return self._handle_presets_input(event)
                
            elif self.menu_mode == "settings":
                return self._handle_settings_input(event)
                
            elif self.menu_mode == "monitor":
                return self._handle_monitor_input(event)
                
            elif self.menu_mode == "auto":
                return self._handle_auto_input(event)
                
        return None
    
    def _handle_main_input(self, event) -> str:
        """Handle input in main menu mode"""
        if event.key == pygame.K_UP:
            self.selected_option_index = (self.selected_option_index - 1) % len(self.menu_options)
            return "option_changed"
            
        elif event.key == pygame.K_DOWN:
            self.selected_option_index = (self.selected_option_index + 1) % len(self.menu_options)
            return "option_changed"
            
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            return self._activate_main_option()
            
        return None
    
    def _handle_mouse_motion(self, event) -> str:
        """Handle mouse motion for hover effects"""
        # Store mouse position for hover effects in draw method
        self.mouse_pos = event.pos
        return None
    
    def _handle_mouse_click(self, event) -> str:
        """Handle mouse click events"""
        # Check if click is on a menu item and trigger selection
        # This will be used in conjunction with the draw method
        self.mouse_click_pos = event.pos
        
        # Simulate ENTER key press for clicked item
        if self.menu_mode == "main":
            # Click detection will be done in draw method which knows positions
            return "mouse_click"
        elif self.menu_mode == "presets":
            return "mouse_click_preset"
        elif self.menu_mode == "settings":
            return "mouse_click_setting"
        
        return None
    
    def _handle_presets_input(self, event) -> str:
        """Handle input in presets mode"""
        presets = list(PerformancePreset)
        
        if event.key == pygame.K_UP:
            self.selected_preset_index = (self.selected_preset_index - 1) % len(presets)
            return "preset_changed"
            
        elif event.key == pygame.K_DOWN:
            self.selected_preset_index = (self.selected_preset_index + 1) % len(presets)
            return "preset_changed"
            
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Apply selected preset
            preset = presets[self.selected_preset_index]
            self.performance_manager.apply_preset(preset)
            return "preset_applied"
            
        elif event.key == pygame.K_r:
            # Reset to recommended preset
            recommended = self.performance_manager.get_recommended_preset()
            self.performance_manager.apply_preset(recommended)
            return "preset_recommended"
            
        return None
    
    def _handle_settings_input(self, event) -> str:
        """Handle input in detailed settings mode"""
        if event.key == pygame.K_UP:
            self.selected_category_index = (self.selected_category_index - 1) % len(self.settings_categories)
            return "category_changed"
            
        elif event.key == pygame.K_DOWN:
            self.selected_category_index = (self.selected_category_index + 1) % len(self.settings_categories)
            return "category_changed"
            
        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            return self._adjust_setting(event.key == pygame.K_RIGHT)
            
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            return self._toggle_setting()
            
        return None
    
    def _handle_monitor_input(self, event) -> str:
        """Handle input in monitor mode"""
        if event.key == pygame.K_UP:
            self.selected_monitor_index = (self.selected_monitor_index - 1) % len(self.monitor_options)
            return "monitor_changed"
            
        elif event.key == pygame.K_DOWN:
            self.selected_monitor_index = (self.selected_monitor_index + 1) % len(self.monitor_options)
            return "monitor_changed"
            
        elif event.key == pygame.K_c:
            # Clear performance history
            self.performance_manager.fps_history.clear()
            self.performance_manager.frame_times.clear()
            self.performance_manager.memory_usage_history.clear()
            return "history_cleared"
            
        return None
    
    def _handle_auto_input(self, event) -> str:
        """Handle input in auto optimization mode"""
        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Trigger auto adjustment
            adjusted = self.performance_manager.auto_adjust_performance()
            return "auto_adjusted" if adjusted else "auto_no_change"
            
        elif event.key == pygame.K_r:
            # Reset to recommended settings
            self.performance_manager.reset_to_preset()
            return "reset_recommended"
            
        return None
    
    def _activate_main_option(self) -> str:
        """Activate the currently selected main option"""
        option = self.menu_options[self.selected_option_index]
        
        if option == "performance_presets":
            self.menu_mode = "presets"
            return "entered_presets_mode"
            
        elif option == "detailed_settings":
            self.menu_mode = "settings"
            return "entered_settings_mode"
            
        elif option == "system_monitor":
            self.menu_mode = "monitor"
            return "entered_monitor_mode"
            
        elif option == "auto_optimization":
            self.menu_mode = "auto"
            return "entered_auto_mode"
            
        elif option == "system_info":
            self.menu_mode = "system"
            return "entered_system_mode"
            
        return None
    
    def _adjust_setting(self, increase: bool) -> str:
        """Adjust the currently selected setting"""
        category_name, settings_list = self.settings_categories[self.selected_category_index]
        
        if self.selected_setting_index < len(settings_list):
            setting_name = settings_list[self.selected_setting_index]
            current_settings = self.performance_manager.get_current_settings()
            
            if hasattr(current_settings, setting_name):
                current_value = getattr(current_settings, setting_name)
                
                # Adjust based on setting type and range
                if setting_name == "target_fps":
                    fps_options = [30, 45, 60, 75, 90, 120, 144, 240]
                    try:
                        current_index = fps_options.index(current_value)
                        if increase and current_index < len(fps_options) - 1:
                            new_value = fps_options[current_index + 1]
                        elif not increase and current_index > 0:
                            new_value = fps_options[current_index - 1]
                        else:
                            return "setting_no_change"
                    except ValueError:
                        new_value = 60  # Default
                        
                elif setting_name in ["particle_density", "ui_animation_speed"]:
                    delta = 0.1 if increase else -0.1
                    new_value = max(0.1, min(3.0, current_value + delta))
                    
                elif setting_name in ["max_visible_entities", "max_particles"]:
                    delta = 25 if increase else -25
                    min_val = 10 if "entities" in setting_name else 50
                    max_val = 1000 if "entities" in setting_name else 5000
                    new_value = max(min_val, min(max_val, current_value + delta))
                    
                elif setting_name == "render_distance":
                    delta = 100 if increase else -100
                    new_value = max(200, min(3000, current_value + delta))
                    
                elif setting_name in ["ai_update_interval", "physics_update_interval", "weather_update_interval"]:
                    delta = 1 if increase else -1
                    new_value = max(1, min(10, current_value + delta))
                    
                elif setting_name == "auto_cleanup_interval":
                    delta = 5.0 if increase else -5.0
                    new_value = max(5.0, min(120.0, current_value + delta))
                    
                elif setting_name == "cache_size_limit":
                    delta = 10 if increase else -10
                    new_value = max(10, min(500, current_value + delta))
                    
                elif setting_name in ["shadow_quality", "lighting_quality", "texture_quality"]:
                    quality_levels = ["off", "low", "medium", "high"]
                    try:
                        current_index = quality_levels.index(current_value)
                        if increase and current_index < len(quality_levels) - 1:
                            new_value = quality_levels[current_index + 1]
                        elif not increase and current_index > 0:
                            new_value = quality_levels[current_index - 1]
                        else:
                            return "setting_no_change"
                    except ValueError:
                        new_value = "medium"
                        
                else:
                    return "setting_no_change"
                
                # Apply the new value
                self.performance_manager.update_setting(setting_name, new_value)
                return "setting_adjusted"
                
        return "setting_no_change"
    
    def _toggle_setting(self) -> str:
        """Toggle a boolean setting"""
        category_name, settings_list = self.settings_categories[self.selected_category_index]
        
        if self.selected_setting_index < len(settings_list):
            setting_name = settings_list[self.selected_setting_index]
            current_settings = self.performance_manager.get_current_settings()
            
            if hasattr(current_settings, setting_name):
                current_value = getattr(current_settings, setting_name)
                
                if isinstance(current_value, bool):
                    new_value = not current_value
                    self.performance_manager.update_setting(setting_name, new_value)
                    return "setting_toggled"
                    
        return "setting_no_toggle"
    
    def render(self, screen: pygame.Surface, font: pygame.font.Font):
        """Render the performance settings interface"""
        colors = self.ui_theme.get_all_colors()
        
        # Clear screen with theme background
        screen.fill(colors.get("ui_bg_primary", (40, 40, 40)))
        
        # Get appropriate fonts
        title_font = self.font_manager.get_font(FontCategory.TITLE_TEXT)
        menu_font = self.font_manager.get_font(FontCategory.MENU_TEXT)
        ui_font = self.font_manager.get_font(FontCategory.UI_TEXT)
        
        # Title
        title_text = title_font.render("Performance Settings", True, colors.get("text_accent", (255, 215, 0)))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 30))
        screen.blit(title_text, title_rect)
        
        # Performance health indicator
        health, health_msg = self.performance_manager.get_performance_health()
        health_colors = {
            "excellent": (0, 255, 0),
            "good": (150, 255, 0),
            "fair": (255, 255, 0),
            "poor": (255, 150, 0),
            "critical": (255, 0, 0),
            "unknown": (128, 128, 128)
        }
        health_color = health_colors.get(health, (128, 128, 128))
        health_surface = ui_font.render(health_msg, True, health_color)
        health_rect = health_surface.get_rect(center=(screen.get_width() // 2, 55))
        screen.blit(health_surface, health_rect)
        
        # Mode indicator
        mode_text = f"Mode: {self.menu_mode.title()}"
        mode_surface = ui_font.render(mode_text, True, colors.get("text_secondary", (200, 200, 200)))
        mode_rect = mode_surface.get_rect(center=(screen.get_width() // 2, 80))
        screen.blit(mode_surface, mode_rect)
        
        # Render based on current mode
        if self.menu_mode == "main":
            self._render_main_menu(screen, colors, menu_font, ui_font)
        elif self.menu_mode == "presets":
            self._render_presets_menu(screen, colors, menu_font, ui_font)
        elif self.menu_mode == "settings":
            self._render_settings_menu(screen, colors, menu_font, ui_font)
        elif self.menu_mode == "monitor":
            self._render_monitor_menu(screen, colors, menu_font, ui_font)
        elif self.menu_mode == "auto":
            self._render_auto_menu(screen, colors, menu_font, ui_font)
        elif self.menu_mode == "system":
            self._render_system_menu(screen, colors, menu_font, ui_font)
    
    def _render_main_menu(self, screen: pygame.Surface, colors: dict, menu_font: pygame.font.Font, ui_font: pygame.font.Font):
        """Render main performance menu"""
        
        # Instructions
        instructions = [
            "↑/↓/Mouse - Navigate options",
            "ENTER/Click - Select option",
            "TAB - Quick navigate",
            "ESC - Close menu"
        ]
        
        y_pos = 110
        for instruction in instructions:
            text_surface = ui_font.render(instruction, True, colors.get("text_secondary", (200, 200, 200)))
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25
        
        # Main options
        y_pos = 220
        option_descriptions = {
            "performance_presets": "Performance Presets (Potato to Ultra)",
            "detailed_settings": "Detailed Settings Configuration",
            "system_monitor": "Real-time Performance Monitor",
            "auto_optimization": "Automatic Performance Tuning",
            "system_info": "System Information & Recommendations"
        }
        
        # Clear menu item rects for this render
        self.menu_item_rects = []
        
        for i, option in enumerate(self.menu_options):
            text = option_descriptions.get(option, option.replace("_", " ").title())
            
            # Create rect for this menu item
            item_rect = pygame.Rect(50, y_pos - 5, screen.get_width() - 100, 35)
            self.menu_item_rects.append(item_rect)
            
            # Check if mouse is hovering
            is_hovered = self.mouse_pos and item_rect.collidepoint(self.mouse_pos)
            
            # Highlight selected or hovered option
            if i == self.selected_option_index or is_hovered:
                pygame.draw.rect(screen, colors.get("ui_bg_accent", (60, 60, 60)), item_rect)
                text_color = colors.get("text_accent", (255, 215, 0))
            else:
                text_color = colors.get("text_primary", (255, 255, 255))
            
            text_surface = menu_font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos + 12))
            screen.blit(text_surface, text_rect)
            
            y_pos += 45
        
        # Current settings summary
        self._render_settings_summary(screen, colors, ui_font, y_pos + 20)
    
    def _render_presets_menu(self, screen: pygame.Surface, colors: dict, menu_font: pygame.font.Font, ui_font: pygame.font.Font):
        """Render performance presets menu"""
        
        # Instructions
        instructions = [
            "Performance Presets",
            "↑/↓/Mouse - Select preset",
            "ENTER/Click - Apply preset",
            "R - Apply recommended preset",
            "ESC - Back to main menu"
        ]
        
        y_pos = 100
        for i, instruction in enumerate(instructions):
            color = colors.get("text_accent", (255, 215, 0)) if i == 0 else colors.get("text_secondary", (200, 200, 200))
            text_surface = ui_font.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25
        
        # Show recommended preset
        recommended = self.performance_manager.get_recommended_preset()
        rec_text = f"Recommended for your system: {recommended.value.title()}"
        rec_surface = ui_font.render(rec_text, True, colors.get("text_info", (150, 255, 150)))
        rec_rect = rec_surface.get_rect(center=(screen.get_width() // 2, y_pos + 10))
        screen.blit(rec_surface, rec_rect)
        y_pos += 40
        
        # Preset descriptions
        preset_descriptions = {
            PerformancePreset.POTATO: "Minimum settings for very old hardware",
            PerformancePreset.LOW: "Low settings for older hardware",
            PerformancePreset.MEDIUM: "Balanced settings for average hardware",
            PerformancePreset.HIGH: "High settings for modern hardware",
            PerformancePreset.ULTRA: "Maximum settings for high-end hardware",
            PerformancePreset.CUSTOM: "Custom user-configured settings"
        }
        
        # Presets list
        y_pos = 220
        presets = list(PerformancePreset)
        current_preset = self.performance_manager.current_preset
        
        # Clear menu item rects for this render
        self.menu_item_rects = []
        
        for i, preset in enumerate(presets):
            description = preset_descriptions.get(preset, "")
            
            # Mark current preset
            preset_name = preset.value.title()
            if preset == current_preset:
                preset_name += " [ACTIVE]"
            
            # Create rect for this menu item
            item_rect = pygame.Rect(50, y_pos - 5, screen.get_width() - 100, 50)
            self.menu_item_rects.append(item_rect)
            
            # Check if mouse is hovering
            is_hovered = self.mouse_pos and item_rect.collidepoint(self.mouse_pos)
            
            # Highlight selected or hovered preset
            if i == self.selected_preset_index or is_hovered:
                pygame.draw.rect(screen, colors.get("ui_bg_accent", (60, 60, 60)), item_rect)
                text_color = colors.get("text_accent", (255, 215, 0))
            else:
                text_color = colors.get("text_primary", (255, 255, 255))
                if preset == current_preset:
                    text_color = colors.get("text_success", (150, 255, 150))
            
            # Preset name
            name_surface = menu_font.render(preset_name, True, text_color)
            name_rect = name_surface.get_rect(center=(screen.get_width() // 2, y_pos + 10))
            screen.blit(name_surface, name_rect)
            
            # Description
            desc_color = colors.get("text_secondary", (200, 200, 200))
            desc_surface = ui_font.render(description, True, desc_color)
            desc_rect = desc_surface.get_rect(center=(screen.get_width() // 2, y_pos + 30))
            screen.blit(desc_surface, desc_rect)
            
            y_pos += 60
    
    def _render_settings_menu(self, screen: pygame.Surface, colors: dict, menu_font: pygame.font.Font, ui_font: pygame.font.Font):
        """Render detailed settings menu"""
        
        # Instructions
        instructions = [
            "Detailed Performance Settings",
            "↑/↓ - Select category/setting",
            "←/→ - Adjust values",
            "ENTER - Toggle boolean settings",
            "ESC - Back to main menu"
        ]
        
        y_pos = 100
        for i, instruction in enumerate(instructions):
            color = colors.get("text_accent", (255, 215, 0)) if i == 0 else colors.get("text_secondary", (200, 200, 200))
            text_surface = ui_font.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25
        
        # Settings categories
        y_pos = 200
        current_settings = self.performance_manager.get_current_settings()
        
        for i, (category_name, settings_list) in enumerate(self.settings_categories):
            # Category header
            if i == self.selected_category_index:
                highlight_rect = pygame.Rect(30, y_pos - 5, screen.get_width() - 60, 25)
                pygame.draw.rect(screen, colors.get("ui_bg_accent", (60, 60, 60)), highlight_rect)
                text_color = colors.get("text_accent", (255, 215, 0))
            else:
                text_color = colors.get("text_primary", (255, 255, 255))
            
            category_surface = menu_font.render(f"{category_name}:", True, text_color)
            screen.blit(category_surface, (50, y_pos))
            y_pos += 30
            
            # Show settings for selected category
            if i == self.selected_category_index:
                for j, setting_name in enumerate(settings_list):
                    if hasattr(current_settings, setting_name):
                        value = getattr(current_settings, setting_name)
                        
                        # Format value display
                        if isinstance(value, bool):
                            value_str = "ON" if value else "OFF"
                        elif isinstance(value, float):
                            value_str = f"{value:.1f}"
                        else:
                            value_str = str(value)
                        
                        setting_text = f"  {setting_name.replace('_', ' ').title()}: {value_str}"
                        
                        # Highlight selected setting
                        if j == self.selected_setting_index:
                            setting_color = colors.get("text_accent", (255, 215, 0))
                        else:
                            setting_color = colors.get("text_secondary", (200, 200, 200))
                        
                        setting_surface = ui_font.render(setting_text, True, setting_color)
                        screen.blit(setting_surface, (70, y_pos))
                        y_pos += 22
                
                y_pos += 10
            else:
                y_pos += 5
    
    def _render_monitor_menu(self, screen: pygame.Surface, colors: dict, menu_font: pygame.font.Font, ui_font: pygame.font.Font):
        """Render performance monitor"""
        
        # Instructions
        instructions = [
            "Performance Monitor",
            "↑/↓ - Select display",
            "C - Clear history",
            "ESC - Back to main menu"
        ]
        
        y_pos = 100
        for i, instruction in enumerate(instructions):
            color = colors.get("text_accent", (255, 215, 0)) if i == 0 else colors.get("text_secondary", (200, 200, 200))
            text_surface = ui_font.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 25
        
        # Performance stats
        stats = self.performance_manager.get_performance_stats()
        
        y_pos = 200
        stats_display = [
            f"Current FPS: {stats.get('current_fps', 0):.1f}",
            f"Average FPS: {stats.get('average_fps', 0):.1f}",
            f"Target FPS: {stats.get('target_fps', 60)}",
            f"Frame Time: {stats.get('frame_time_ms', 0):.1f}ms",
            f"Memory Usage: {stats.get('memory_percent', 0):.1f}%",
            f"Memory Used: {stats.get('memory_used_gb', 0):.1f}GB"
        ]
        
        for stat_text in stats_display:
            stat_surface = ui_font.render(stat_text, True, colors.get("text_primary", (255, 255, 255)))
            stat_rect = stat_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(stat_surface, stat_rect)
            y_pos += 25
        
        # Simple FPS graph
        if self.performance_manager.fps_history:
            self._render_fps_graph(screen, colors, 50, y_pos + 20, screen.get_width() - 100, 100)
    
    def _render_fps_graph(self, screen: pygame.Surface, colors: dict, x: int, y: int, width: int, height: int):
        """Render a simple FPS graph"""
        fps_history = self.performance_manager.fps_history
        if not fps_history:
            return
        
        # Graph background
        pygame.draw.rect(screen, colors.get("ui_bg_secondary", (60, 60, 60)), (x, y, width, height))
        pygame.draw.rect(screen, colors.get("text_secondary", (200, 200, 200)), (x, y, width, height), 2)
        
        # Graph data
        max_fps = max(fps_history) if fps_history else 60
        min_fps = min(fps_history) if fps_history else 0
        fps_range = max_fps - min_fps if max_fps > min_fps else 1
        
        points = []
        for i, fps in enumerate(fps_history[-width//2:]):  # Show recent history
            graph_x = x + (i * 2)
            graph_y = y + height - int(((fps - min_fps) / fps_range) * height)
            points.append((graph_x, graph_y))
        
        if len(points) > 1:
            pygame.draw.lines(screen, (0, 255, 0), False, points, 2)
        
        # Target FPS line
        target_fps = self.performance_manager.current_settings.target_fps
        target_y = y + height - int(((target_fps - min_fps) / fps_range) * height)
        pygame.draw.line(screen, (255, 255, 0), (x, target_y), (x + width, target_y), 1)
    
    def _render_auto_menu(self, screen: pygame.Surface, colors: dict, menu_font: pygame.font.Font, ui_font: pygame.font.Font):
        """Render auto optimization menu"""
        
        instructions = [
            "Automatic Performance Optimization",
            "ENTER - Run auto optimization",
            "R - Reset to recommended settings",
            "ESC - Back to main menu",
            "",
            "Auto optimization analyzes your current performance",
            "and adjusts settings to improve frame rate."
        ]
        
        y_pos = 120
        for i, instruction in enumerate(instructions):
            if i == 0:
                color = colors.get("text_accent", (255, 215, 0))
            elif instruction == "":
                y_pos += 10
                continue
            elif i >= 5:
                color = colors.get("text_secondary", (200, 200, 200))
            else:
                color = colors.get("text_info", (150, 200, 255))
            
            text_surface = ui_font.render(instruction, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 30
    
    def _render_system_menu(self, screen: pygame.Surface, colors: dict, menu_font: pygame.font.Font, ui_font: pygame.font.Font):
        """Render system information menu"""
        
        system_info = self.performance_manager.system_info
        
        info_title = menu_font.render("System Information", True, colors.get("text_accent", (255, 215, 0)))
        title_rect = info_title.get_rect(center=(screen.get_width() // 2, 120))
        screen.blit(info_title, title_rect)
        
        y_pos = 160
        info_items = [
            f"CPU Cores: {system_info.get('cpu_cores', 'Unknown')}",
            f"CPU Threads: {system_info.get('cpu_threads', 'Unknown')}",
            f"Total Memory: {system_info.get('total_memory_gb', 'Unknown')} GB",
            f"Python Version: {system_info.get('python_version', 'Unknown')}",
            f"Platform: {system_info.get('platform', 'Unknown')}",
            "",
            f"Recommended Preset: {self.performance_manager.get_recommended_preset().value.title()}"
        ]
        
        for item in info_items:
            if item == "":
                y_pos += 15
                continue
                
            item_surface = ui_font.render(item, True, colors.get("text_primary", (255, 255, 255)))
            item_rect = item_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(item_surface, item_rect)
            y_pos += 25
    
    def _render_settings_summary(self, screen: pygame.Surface, colors: dict, ui_font: pygame.font.Font, start_y: int):
        """Render current settings summary"""
        summary_title = ui_font.render("Current Settings:", True, colors.get("text_accent", (255, 215, 0)))
        screen.blit(summary_title, (50, start_y))
        
        settings = self.performance_manager.get_current_settings()
        preset = self.performance_manager.current_preset
        
        y_pos = start_y + 25
        
        summary_items = [
            f"Preset: {preset.value.title()}",
            f"Target FPS: {settings.target_fps}",
            f"Particles: {settings.particle_density:.1f}x",
            f"Max Entities: {settings.max_visible_entities}",
            f"Shadow Quality: {settings.shadow_quality.title()}"
        ]
        
        for item in summary_items:
            item_surface = ui_font.render(item, True, colors.get("text_secondary", (200, 200, 200)))
            screen.blit(item_surface, (70, y_pos))
            y_pos += 20

# Global performance settings UI instance
performance_settings_ui = PerformanceSettingsUI()

def get_performance_settings_ui() -> PerformanceSettingsUI:
    """Get the global performance settings UI instance"""
    return performance_settings_ui