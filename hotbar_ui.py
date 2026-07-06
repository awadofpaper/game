"""
Hotbar UI - Visual rendering and interaction for the hotbar system

Renders the hotbar at the bottom of the screen with:
- 9 slots with number labels (1-9)
- Item/spell names and icons
- Cooldown overlays
- Drag & drop support
- Visual feedback for locked/empty slots
"""

import pygame
from typing import Optional, Tuple
from hotbar_system import HotbarSystem, HotbarSlotType


class HotbarUI:
    """Renders and manages hotbar UI"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Layout configuration
        self.slot_size = 50
        self.slot_padding = 8
        self.num_slots = 9
        self.hotbar_height = self.slot_size + self.slot_padding * 2
        
        # Calculate centered position at bottom of screen
        total_width = self.num_slots * (self.slot_size + self.slot_padding) + self.slot_padding
        self.hotbar_x = (screen_width - total_width) // 2
        self.hotbar_y = screen_height - self.hotbar_height - 10
        
        # Colors
        self.bg_color = (40, 40, 40, 200)  # Semi-transparent dark gray
        self.slot_color = (60, 60, 60)
        self.slot_hover_color = (80, 80, 80)
        self.slot_empty_color = (50, 50, 50)
        self.slot_border_color = (100, 100, 100)
        self.slot_active_color = (120, 200, 255)
        self.cooldown_overlay_color = (0, 0, 0, 180)
        self.locked_color = (180, 50, 50)
        
        # Drag & drop state
        self.dragging_slot = None
        self.drag_start_pos = None
        self.hover_slot = None
        
        # Animation state
        self.slot_animations = [0.0] * self.num_slots  # Animation progress for each slot
        
    def get_slot_rect(self, slot_id: int) -> pygame.Rect:
        """Get the rectangle for a specific slot"""
        x = self.hotbar_x + self.slot_padding + slot_id * (self.slot_size + self.slot_padding)
        y = self.hotbar_y + self.slot_padding
        return pygame.Rect(x, y, self.slot_size, self.slot_size)
    
    def get_slot_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """Get the slot ID at the given screen position"""
        for i in range(self.num_slots):
            if self.get_slot_rect(i).collidepoint(pos):
                return i
        return None
    
    def handle_mouse_down(self, pos: Tuple[int, int], button: int, hotbar: HotbarSystem) -> bool:
        """
        Handle mouse button press
        
        Returns:
            bool: True if event was handled
        """
        if button == 1:  # Left click
            slot_id = self.get_slot_at_position(pos)
            if slot_id is not None:
                slot = hotbar.get_slot(slot_id)
                if slot and slot.type != HotbarSlotType.EMPTY:
                    # Start dragging
                    self.dragging_slot = slot_id
                    self.drag_start_pos = pos
                    return True
        
        elif button == 3:  # Right click
            slot_id = self.get_slot_at_position(pos)
            if slot_id is not None and not hotbar.locked:
                # Clear the slot
                hotbar.clear_slot(slot_id)
                return True
        
        return False
    
    def handle_mouse_up(self, pos: Tuple[int, int], button: int, hotbar: HotbarSystem) -> bool:
        """
        Handle mouse button release
        
        Returns:
            bool: True if event was handled
        """
        if button == 1 and self.dragging_slot is not None:
            # Check if released over a different slot
            target_slot = self.get_slot_at_position(pos)
            
            if target_slot is not None and target_slot != self.dragging_slot:
                # Swap slots
                hotbar.swap_slots(self.dragging_slot, target_slot)
                # Animate both slots
                self.slot_animations[self.dragging_slot] = 1.0
                self.slot_animations[target_slot] = 1.0
            
            self.dragging_slot = None
            self.drag_start_pos = None
            return True
        
        return False
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse movement for hover effects"""
        self.hover_slot = self.get_slot_at_position(pos)
    
    def update(self, dt: float):
        """Update animations"""
        for i in range(len(self.slot_animations)):
            if self.slot_animations[i] > 0:
                self.slot_animations[i] = max(0, self.slot_animations[i] - dt * 3.0)
    
    def draw(self, screen: pygame.Surface, hotbar: HotbarSystem, font: pygame.font.Font):
        """Draw the hotbar UI"""
        # Create semi-transparent background
        bg_surface = pygame.Surface((
            self.num_slots * (self.slot_size + self.slot_padding) + self.slot_padding * 2,
            self.hotbar_height
        ))
        bg_surface.set_alpha(200)
        bg_surface.fill((40, 40, 40))
        screen.blit(bg_surface, (self.hotbar_x, self.hotbar_y))
        
        # Draw each slot
        for i in range(self.num_slots):
            self._draw_slot(screen, hotbar, i, font)
        
        # Draw locked indicator if hotbar is locked
        if hotbar.locked:
            lock_text = font.render("🔒 LOCKED", True, self.locked_color)
            lock_x = self.hotbar_x + (bg_surface.get_width() - lock_text.get_width()) // 2
            lock_y = self.hotbar_y - 25
            screen.blit(lock_text, (lock_x, lock_y))
    
    def _draw_slot(self, screen: pygame.Surface, hotbar: HotbarSystem, slot_id: int, font: pygame.font.Font):
        """Draw a single hotbar slot"""
        slot = hotbar.get_slot(slot_id)
        if not slot:
            return
        
        rect = self.get_slot_rect(slot_id)
        
        # Determine slot color
        if self.dragging_slot == slot_id:
            color = self.slot_active_color
        elif self.hover_slot == slot_id:
            color = self.slot_hover_color
        elif slot.type == HotbarSlotType.EMPTY:
            color = self.slot_empty_color
        else:
            color = self.slot_color
        
        # Apply animation (scale effect)
        anim = self.slot_animations[slot_id]
        if anim > 0:
            # Slight scale pulse
            scale = 1.0 + (anim * 0.1)
            center = rect.center
            scaled_rect = rect.inflate(int(rect.width * (scale - 1)), int(rect.height * (scale - 1)))
            scaled_rect.center = center
            rect = scaled_rect
        
        # Draw slot background
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, self.slot_border_color, rect, 2)
        
        # Draw slot number (keybinding)
        key_label = str(slot_id + 1)
        key_text = font.render(key_label, True, (200, 200, 200))
        key_x = rect.x + 3
        key_y = rect.y + 2
        screen.blit(key_text, (key_x, key_y))
        
        # Draw item/spell name if slot is not empty
        if slot.type != HotbarSlotType.EMPTY and slot.item_name:
            # Truncate name if too long
            display_name = slot.item_name
            if len(display_name) > 8:
                display_name = display_name[:7] + "…"
            
            # Draw item name
            name_font = pygame.font.Font(None, 16)
            name_text = name_font.render(display_name, True, (255, 255, 255))
            name_x = rect.centerx - name_text.get_width() // 2
            name_y = rect.centery - name_text.get_height() // 2
            screen.blit(name_text, (name_x, name_y))
            
            # Draw type indicator
            type_colors = {
                HotbarSlotType.ITEM: (100, 255, 100),
                HotbarSlotType.SPELL: (100, 150, 255),
                HotbarSlotType.ABILITY: (255, 200, 100),
                HotbarSlotType.EQUIPMENT: (200, 200, 200)
            }
            type_color = type_colors.get(slot.type, (200, 200, 200))
            pygame.draw.circle(screen, type_color, (rect.x + rect.width - 6, rect.y + 6), 3)
        
        # Draw cooldown overlay
        if slot.is_on_cooldown():
            cooldown_remaining = slot.get_cooldown_remaining()
            cooldown_progress = cooldown_remaining / slot.cooldown if slot.cooldown > 0 else 0
            
            # Semi-transparent overlay
            overlay = pygame.Surface((rect.width, rect.height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            
            # Calculate overlay height based on cooldown progress
            overlay_height = int(rect.height * cooldown_progress)
            overlay_rect = pygame.Rect(0, rect.height - overlay_height, rect.width, overlay_height)
            screen.blit(overlay, rect, area=overlay_rect)
            
            # Draw cooldown text
            cooldown_text = font.render(f"{cooldown_remaining:.1f}s", True, (255, 100, 100))
            text_x = rect.centerx - cooldown_text.get_width() // 2
            text_y = rect.bottom - cooldown_text.get_height() - 3
            screen.blit(cooldown_text, (text_x, text_y))
    
    def draw_tooltip(self, screen: pygame.Surface, hotbar: HotbarSystem, font: pygame.font.Font, mouse_pos: Tuple[int, int]):
        """Draw tooltip for hovered slot"""
        if self.hover_slot is None or self.dragging_slot is not None:
            return
        
        slot = hotbar.get_slot(self.hover_slot)
        if not slot or slot.type == HotbarSlotType.EMPTY:
            return
        
        # Build tooltip text
        tooltip_lines = []
        tooltip_lines.append(f"{slot.item_name}")
        
        type_names = {
            HotbarSlotType.ITEM: "Consumable",
            HotbarSlotType.SPELL: "Spell",
            HotbarSlotType.ABILITY: "Ability",
            HotbarSlotType.EQUIPMENT: "Equipment"
        }
        tooltip_lines.append(f"Type: {type_names.get(slot.type, 'Unknown')}")
        
        if slot.is_on_cooldown():
            tooltip_lines.append(f"Cooldown: {slot.get_cooldown_remaining():.1f}s")
        else:
            tooltip_lines.append("Ready to use")
        
        tooltip_lines.append(f"Hotkey: {slot.slot_id + 1}")
        tooltip_lines.append("Right-click to remove")
        
        # Calculate tooltip size
        line_height = 20
        padding = 10
        max_width = max(font.size(line)[0] for line in tooltip_lines)
        tooltip_width = max_width + padding * 2
        tooltip_height = len(tooltip_lines) * line_height + padding * 2
        
        # Position tooltip above the hotbar
        tooltip_x = mouse_pos[0] - tooltip_width // 2
        tooltip_y = self.hotbar_y - tooltip_height - 10
        
        # Keep tooltip on screen
        tooltip_x = max(10, min(tooltip_x, self.screen_width - tooltip_width - 10))
        tooltip_y = max(10, tooltip_y)
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height))
        tooltip_surface.set_alpha(240)
        tooltip_surface.fill((30, 30, 30))
        screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
        
        # Draw tooltip border
        pygame.draw.rect(screen, (100, 100, 100), tooltip_rect, 2)
        
        # Draw tooltip text
        small_font = pygame.font.Font(None, 18)
        for i, line in enumerate(tooltip_lines):
            if i == 0:
                # First line (name) is brighter
                text = font.render(line, True, (255, 255, 100))
            else:
                text = small_font.render(line, True, (200, 200, 200))
            
            text_x = tooltip_x + padding
            text_y = tooltip_y + padding + i * line_height
            screen.blit(text, (text_x, text_y))
    
    def trigger_slot_animation(self, slot_id: int):
        """Trigger visual feedback animation for a slot"""
        if 0 <= slot_id < len(self.slot_animations):
            self.slot_animations[slot_id] = 1.0
