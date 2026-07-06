"""
Save/Load UI System
Provides enhanced save/load interface with multiple slots, previews, and metadata
"""

import pygame
import os
from datetime import datetime
from typing import List, Optional, Callable
from save_system import SaveSlot, get_save_slots, get_save_slot_summary


class SaveLoadUI:
    """Enhanced Save/Load UI with multiple slots and previews"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.mode = "save"  # "save" or "load"
        
        # UI Layout
        self.panel_width = min(700, screen_width - 100)
        self.panel_height = min(500, screen_height - 100)
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        self.slot_height = 70
        self.slot_margin = 10
        self.visible_slots = 5
        self.scroll_offset = 0
        self.selected_slot = 1  # Default to slot 1 (slot 0 is auto-save)
        
        # Colors
        self.colors = {
            'panel_bg': (40, 40, 50, 240),
            'panel_border': (100, 100, 120),
            'slot_bg': (60, 60, 70),
            'slot_selected': (80, 120, 160),
            'slot_empty': (50, 50, 60),
            'text_normal': (220, 220, 220),
            'text_selected': (255, 255, 255),
            'text_dim': (150, 150, 150),
            'button_bg': (70, 100, 140),
            'button_hover': (90, 120, 160),
            'auto_save_bg': (100, 80, 60)
        }
        
        # Fonts
        self.fonts = {}
        self._init_fonts()
        
        # UI State
        self.save_slots = []
        self.refresh_saves()
        
        # Callbacks
        self.on_save: Optional[Callable] = None
        self.on_load: Optional[Callable] = None
        self.on_delete: Optional[Callable] = None
        self.on_cancel: Optional[Callable] = None
        
        # Mouse state
        self.mouse_pos = (0, 0)
    
    def _init_fonts(self):
        """Initialize fonts with fallbacks"""
        try:
            self.fonts['title'] = pygame.font.SysFont('Arial', 36, bold=True)
            self.fonts['normal'] = pygame.font.SysFont('Arial', 20)
            self.fonts['small'] = pygame.font.SysFont('Arial', 16)
        except (pygame.error, OSError) as e:
            self.fonts['title'] = pygame.font.Font(None, 36)
            self.fonts['normal'] = pygame.font.Font(None, 20)
            self.fonts['small'] = pygame.font.Font(None, 16)
    
    def refresh_saves(self):
        """Refresh save slot information"""
        self.save_slots = get_save_slots()
    
    def open_save_dialog(self):
        """Open save dialog"""
        self.mode = "save"
        self.active = True
        self.selected_slot = 1
        self.refresh_saves()
    
    def open_load_dialog(self):
        """Open load dialog"""
        self.mode = "load"
        self.active = True
        self.selected_slot = 1
        self.refresh_saves()
    
    def close(self):
        """Close the save/load dialog"""
        self.active = False
    
    def handle_event(self, event):
        """Handle pygame events"""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            return self._handle_key_event(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_event(event)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            return self._handle_scroll_event(event)
        
        return True  # Consume all events when active
    
    def _handle_key_event(self, event):
        """Handle keyboard events"""
        if event.key == pygame.K_ESCAPE:
            if self.on_cancel:
                self.on_cancel()
            self.close()
            return True
        
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            self.selected_slot = max(0, self.selected_slot - 1)
            self._ensure_slot_visible()
            return True
        
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.selected_slot = min(len(self.save_slots) - 1, self.selected_slot + 1)
            self._ensure_slot_visible()
            return True
        
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self._execute_action()
            return True
        
        elif event.key == pygame.K_DELETE and self.mode == "load":
            self._delete_selected_slot()
            return True
        
        return True
    
    def _handle_mouse_event(self, event):
        """Handle mouse events"""
        mouse_x, mouse_y = event.pos
        
        # Check if click is within panel
        if not (self.panel_x <= mouse_x <= self.panel_x + self.panel_width and
                self.panel_y <= mouse_y <= self.panel_y + self.panel_height):
            return True
        
        # Calculate clicked slot
        slot_area_y = self.panel_y + 70
        relative_y = mouse_y - slot_area_y
        
        if 0 <= relative_y <= self.visible_slots * (self.slot_height + self.slot_margin):
            clicked_index = relative_y // (self.slot_height + self.slot_margin) + self.scroll_offset
            if 0 <= clicked_index < len(self.save_slots):
                if self.selected_slot == clicked_index:
                    # Double-click action
                    self._execute_action()
                else:
                    self.selected_slot = clicked_index
            return True
        
        # Check button clicks
        self._handle_button_clicks(mouse_x, mouse_y)
        
        return True
    
    def _handle_scroll_event(self, event):
        """Handle mouse wheel scrolling"""
        if event.y > 0 and self.scroll_offset > 0:
            self.scroll_offset -= 1
        elif event.y < 0 and self.scroll_offset < max(0, len(self.save_slots) - self.visible_slots):
            self.scroll_offset += 1
        return True
    
    def _handle_button_clicks(self, mouse_x, mouse_y):
        """Handle clicks on UI buttons"""
        button_y = self.panel_y + self.panel_height - 60
        button_height = 40
        button_width = 120
        
        # Action button (Save/Load)
        action_button_x = self.panel_x + self.panel_width - button_width - 150
        if (action_button_x <= mouse_x <= action_button_x + button_width and
            button_y <= mouse_y <= button_y + button_height):
            self._execute_action()
        
        # Cancel button
        cancel_button_x = self.panel_x + self.panel_width - button_width - 20
        if (cancel_button_x <= mouse_x <= cancel_button_x + button_width and
            button_y <= mouse_y <= button_y + button_height):
            if self.on_cancel:
                self.on_cancel()
            self.close()
    
    def _ensure_slot_visible(self):
        """Ensure selected slot is visible in the scroll area"""
        if self.selected_slot < self.scroll_offset:
            self.scroll_offset = self.selected_slot
        elif self.selected_slot >= self.scroll_offset + self.visible_slots:
            self.scroll_offset = self.selected_slot - self.visible_slots + 1
    
    def _execute_action(self):
        """Execute save or load action"""
        if self.mode == "save":
            if self.on_save:
                self.on_save(self.selected_slot)
        elif self.mode == "load":
            if self.save_slots[self.selected_slot].exists and self.on_load:
                self.on_load(self.selected_slot)
        
        self.close()
    
    def _delete_selected_slot(self):
        """Delete the selected save slot"""
        if (self.mode == "load" and 
            self.selected_slot < len(self.save_slots) and
            self.save_slots[self.selected_slot].exists and
            self.selected_slot != 0):  # Can't delete auto-save
            
            if self.on_delete:
                self.on_delete(self.selected_slot)
            self.refresh_saves()
    
    def _format_playtime(self, seconds: float) -> str:
        """Format playtime in hours and minutes"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def draw(self, screen):
        """Draw the save/load UI"""
        if not self.active:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel.fill(self.colors['panel_bg'])
        pygame.draw.rect(panel, self.colors['panel_border'], 
                        (0, 0, self.panel_width, self.panel_height), 3)
        
        # Title
        title_text = "Save Game" if self.mode == "save" else "Load Game"
        title_surface = self.fonts['title'].render(title_text, True, self.colors['text_selected'])
        panel.blit(title_surface, (20, 15))
        
        screen.blit(panel, (self.panel_x, self.panel_y))
        
        # Draw save slots
        self._draw_save_slots(screen)
        
        # Draw buttons
        self._draw_buttons(screen)
        
        # Draw instructions
        self._draw_instructions(screen)
    
    def _draw_save_slots(self, screen):
        """Draw the save slot list"""
        start_y = self.panel_y + 70
        
        for i in range(self.visible_slots):
            slot_index = self.scroll_offset + i
            if slot_index >= len(self.save_slots):
                break
            
            slot = self.save_slots[slot_index]
            y_pos = start_y + i * (self.slot_height + self.slot_margin)
            
            # Slot background
            is_selected = (slot_index == self.selected_slot)
            if slot_index == 0:
                bg_color = self.colors['auto_save_bg']
            elif is_selected:
                bg_color = self.colors['slot_selected']
            elif slot.exists:
                bg_color = self.colors['slot_bg']
            else:
                bg_color = self.colors['slot_empty']
            
            slot_rect = pygame.Rect(self.panel_x + 20, y_pos, 
                                   self.panel_width - 40, self.slot_height)
            pygame.draw.rect(screen, bg_color, slot_rect)
            pygame.draw.rect(screen, self.colors['panel_border'], slot_rect, 2)
            
            # Slot content
            self._draw_slot_content(screen, slot, slot_rect)
    
    def _draw_slot_content(self, screen, slot: SaveSlot, rect: pygame.Rect):
        """Draw content for a single save slot"""
        x = rect.x + 10
        y = rect.y + 8
        
        # Slot number/name
        if slot.slot_id == 0:
            slot_name = "AUTO-SAVE"
        else:
            slot_name = f"Slot {slot.slot_id}"
        
        name_surface = self.fonts['normal'].render(slot_name, True, self.colors['text_selected'])
        screen.blit(name_surface, (x, y))
        
        if slot.exists:
            # Character info
            char_info = f"{slot.character_name} - Level {slot.level}"
            char_surface = self.fonts['small'].render(char_info, True, self.colors['text_normal'])
            screen.blit(char_surface, (x, y + 25))
            
            # Location and time
            if slot.save_time:
                time_str = slot.save_time.strftime("%m/%d/%y %H:%M")
                location_str = f"{slot.location} | {time_str}"
            else:
                location_str = slot.location
            
            loc_surface = self.fonts['small'].render(location_str, True, self.colors['text_dim'])
            screen.blit(loc_surface, (x, y + 45))
            
            # File size
            if slot.file_size > 0:
                size_str = self._format_file_size(slot.file_size)
                size_surface = self.fonts['small'].render(size_str, True, self.colors['text_dim'])
                screen.blit(size_surface, (rect.right - 100, y + 45))
        else:
            # Empty slot
            empty_surface = self.fonts['small'].render("Empty", True, self.colors['text_dim'])
            screen.blit(empty_surface, (x, y + 25))
    
    def _draw_buttons(self, screen):
        """Draw action buttons"""
        button_y = self.panel_y + self.panel_height - 60
        button_height = 40
        button_width = 120
        
        # Action button (Save/Load)
        action_text = "Save" if self.mode == "save" else "Load"
        action_button_x = self.panel_x + self.panel_width - button_width - 150
        action_button_rect = pygame.Rect(action_button_x, button_y, button_width, button_height)
        
        # Check if mouse is over button
        mouse_over_action = action_button_rect.collidepoint(self.mouse_pos)
        action_color = self.colors['button_hover'] if mouse_over_action else self.colors['button_bg']
        
        pygame.draw.rect(screen, action_color, action_button_rect)
        pygame.draw.rect(screen, self.colors['panel_border'], action_button_rect, 2)
        
        action_surface = self.fonts['normal'].render(action_text, True, self.colors['text_selected'])
        text_x = action_button_x + (button_width - action_surface.get_width()) // 2
        text_y = button_y + (button_height - action_surface.get_height()) // 2
        screen.blit(action_surface, (text_x, text_y))
        
        # Cancel button
        cancel_button_x = self.panel_x + self.panel_width - button_width - 20
        cancel_button_rect = pygame.Rect(cancel_button_x, button_y, button_width, button_height)
        
        mouse_over_cancel = cancel_button_rect.collidepoint(self.mouse_pos)
        cancel_color = self.colors['button_hover'] if mouse_over_cancel else self.colors['button_bg']
        
        pygame.draw.rect(screen, cancel_color, cancel_button_rect)
        pygame.draw.rect(screen, self.colors['panel_border'], cancel_button_rect, 2)
        
        cancel_surface = self.fonts['normal'].render("Cancel", True, self.colors['text_selected'])
        text_x = cancel_button_x + (button_width - cancel_surface.get_width()) // 2
        text_y = button_y + (button_height - cancel_surface.get_height()) // 2
        screen.blit(cancel_surface, (text_x, text_y))
    
    def _draw_instructions(self, screen):
        """Draw control instructions"""
        instructions = [
            "Arrow Keys/Mouse: Select slot",
            "Enter/Click: Confirm",
            "Delete: Remove save (Load mode)",
            "Esc: Cancel"
        ]
        
        y_pos = self.panel_y + self.panel_height - 25
        full_text = " | ".join(instructions)
        inst_surface = self.fonts['small'].render(full_text, True, self.colors['text_dim'])
        
        x_pos = self.panel_x + (self.panel_width - inst_surface.get_width()) // 2
        screen.blit(inst_surface, (x_pos, y_pos))
