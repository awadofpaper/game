"""
Cosmetic Equip Menu - UI for managing and equipping unlocked cosmetics

Allows players to browse their collection and apply/remove cosmetics.
"""

import pygame
from typing import Optional, List, Tuple
from cosmetic_system import Cosmetic, CosmeticManager, CosmeticRarity


class CosmeticEquipMenu:
    """UI for equipping and managing cosmetics"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Menu dimensions
        self.menu_width = 800
        self.menu_height = 600
        self.menu_x = (screen_width - self.menu_width) // 2
        self.menu_y = (screen_height - self.menu_height) // 2
        
        # Tabs for different cosmetic types
        self.tabs = ['player', 'pet', 'armor', 'weapon']
        self.tab_names = {
            'player': 'Player',
            'pet': 'Pet',
            'armor': 'Armor',
            'weapon': 'Weapon'
        }
        self.current_tab = 'player'
        
        # Scrolling
        self.scroll_offset = 0
        self.items_per_row = 4
        self.item_size = 150
        self.item_padding = 20
        
        # Hover state
        self.hover_cosmetic: Optional[Cosmetic] = None
        self.hover_index: Optional[int] = None
        
    def draw(self, screen: pygame.Surface, font: pygame.font.Font, 
             cosmetic_manager: CosmeticManager):
        """Draw the cosmetic equip menu"""
        # Draw darkened background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw menu background
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(screen, (40, 40, 50), menu_rect)
        pygame.draw.rect(screen, (100, 100, 120), menu_rect, 3)
        
        # Draw title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Cosmetic Collection", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.menu_y + 40))
        screen.blit(title_text, title_rect)
        
        # Draw tabs
        self._draw_tabs(screen, font)
        
        # Draw cosmetics grid
        self._draw_cosmetics_grid(screen, font, cosmetic_manager)
        
        # Draw instructions
        instruction_text = font.render("Click to equip/unequip | ESC to close | Mouse wheel to scroll", 
                                      True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, 
                                                             self.menu_y + self.menu_height - 20))
        screen.blit(instruction_text, instruction_rect)
        
        # Draw hover tooltip
        if self.hover_cosmetic:
            self._draw_tooltip(screen, font)
    
    def _draw_tabs(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw category tabs"""
        tab_width = self.menu_width // len(self.tabs)
        tab_height = 50
        tab_y = self.menu_y + 80
        
        for i, tab in enumerate(self.tabs):
            tab_x = self.menu_x + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            # Color based on selection
            if tab == self.current_tab:
                color = (80, 80, 100)
                text_color = (255, 255, 255)
            else:
                color = (60, 60, 70)
                text_color = (180, 180, 180)
            
            pygame.draw.rect(screen, color, tab_rect)
            pygame.draw.rect(screen, (100, 100, 120), tab_rect, 2)
            
            # Tab text
            tab_text = font.render(self.tab_names[tab], True, text_color)
            tab_text_rect = tab_text.get_rect(center=tab_rect.center)
            screen.blit(tab_text, tab_text_rect)
    
    def _draw_cosmetics_grid(self, screen: pygame.Surface, font: pygame.font.Font,
                            cosmetic_manager: CosmeticManager):
        """Draw grid of cosmetics"""
        # Get cosmetics for current tab
        cosmetics = cosmetic_manager.get_unlocked_by_type(self.current_tab)
        equipped = cosmetic_manager.get_equipped(self.current_tab)
        
        if not cosmetics:
            # No cosmetics unlocked
            no_items_text = font.render("No cosmetics unlocked yet!", True, (150, 150, 150))
            no_items_rect = no_items_text.get_rect(center=(self.screen_width // 2, 
                                                           self.menu_y + 300))
            screen.blit(no_items_text, no_items_rect)
            
            hint_text = font.render("Visit MaXxS Silicon Dioxide Shop to get some!", 
                                   True, (120, 120, 120))
            hint_rect = hint_text.get_rect(center=(self.screen_width // 2, 
                                                   self.menu_y + 330))
            screen.blit(hint_text, hint_rect)
            return
        
        # Calculate grid layout
        grid_start_x = self.menu_x + self.item_padding
        grid_start_y = self.menu_y + 150
        grid_width = self.menu_width - self.item_padding * 2
        grid_height = self.menu_height - 200
        
        # Create clipping rect for scrolling
        clip_rect = pygame.Rect(self.menu_x, grid_start_y, self.menu_width, grid_height)
        screen.set_clip(clip_rect)
        
        # Draw each cosmetic
        for i, cosmetic in enumerate(cosmetics):
            row = i // self.items_per_row
            col = i % self.items_per_row
            
            x = grid_start_x + col * (self.item_size + self.item_padding)
            y = grid_start_y + row * (self.item_size + self.item_padding) - self.scroll_offset
            
            # Skip if not visible
            if y + self.item_size < grid_start_y or y > grid_start_y + grid_height:
                continue
            
            self._draw_cosmetic_item(screen, font, cosmetic, x, y, 
                                    equipped and equipped.id == cosmetic.id, i)
        
        screen.set_clip(None)
    
    def _draw_cosmetic_item(self, screen: pygame.Surface, font: pygame.font.Font,
                           cosmetic: Cosmetic, x: int, y: int, is_equipped: bool, index: int):
        """Draw a single cosmetic item"""
        item_rect = pygame.Rect(x, y, self.item_size, self.item_size)
        
        # Background
        bg_color = (60, 60, 70)
        if self.hover_index == index:
            bg_color = (80, 80, 90)
        
        pygame.draw.rect(screen, bg_color, item_rect)
        
        # Rarity border
        rarity_color = CosmeticRarity.COLORS.get(cosmetic.rarity, (150, 150, 150))
        border_width = 4 if is_equipped else 2
        pygame.draw.rect(screen, rarity_color, item_rect, border_width)
        
        # Color preview (large swatches)
        swatch_size = 50
        swatch_y = y + 20
        
        # Primary color
        primary_rect = pygame.Rect(x + 20, swatch_y, swatch_size, swatch_size)
        pygame.draw.rect(screen, cosmetic.primary_color, primary_rect)
        pygame.draw.rect(screen, (255, 255, 255), primary_rect, 1)
        
        # Secondary color
        secondary_rect = pygame.Rect(x + 80, swatch_y, swatch_size, swatch_size)
        pygame.draw.rect(screen, cosmetic.secondary_color, secondary_rect)
        pygame.draw.rect(screen, (255, 255, 255), secondary_rect, 1)
        
        # Pattern name
        small_font = pygame.font.Font(None, 18)
        pattern_text = small_font.render(cosmetic.pattern.replace('_', ' ').title(), 
                                        True, (200, 200, 200))
        pattern_rect = pattern_text.get_rect(center=(x + self.item_size // 2, y + 90))
        screen.blit(pattern_text, pattern_rect)
        
        # Rarity text
        rarity_text = small_font.render(cosmetic.rarity, True, rarity_color)
        rarity_rect = rarity_text.get_rect(center=(x + self.item_size // 2, y + 110))
        screen.blit(rarity_text, rarity_rect)
        
        # Equipped indicator
        if is_equipped:
            equipped_text = small_font.render("EQUIPPED", True, (100, 255, 100))
            equipped_rect = equipped_text.get_rect(center=(x + self.item_size // 2, y + 130))
            screen.blit(equipped_text, equipped_rect)
    
    def _draw_tooltip(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw detailed tooltip for hovered cosmetic"""
        if not self.hover_cosmetic:
            return
        
        cosmetic = self.hover_cosmetic
        
        # Tooltip dimensions
        tooltip_width = 300
        tooltip_height = 200
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Position tooltip near mouse but keep on screen
        tooltip_x = mouse_x + 20
        tooltip_y = mouse_y + 20
        
        if tooltip_x + tooltip_width > self.screen_width:
            tooltip_x = mouse_x - tooltip_width - 20
        if tooltip_y + tooltip_height > self.screen_height:
            tooltip_y = mouse_y - tooltip_height - 20
        
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        
        # Background
        pygame.draw.rect(screen, (30, 30, 40), tooltip_rect)
        pygame.draw.rect(screen, CosmeticRarity.COLORS.get(cosmetic.rarity, (150, 150, 150)), 
                        tooltip_rect, 3)
        
        # Content
        small_font = pygame.font.Font(None, 20)
        y_offset = tooltip_y + 15
        
        # Name
        name_text = font.render(cosmetic.name, True, (255, 255, 255))
        screen.blit(name_text, (tooltip_x + 15, y_offset))
        y_offset += 30
        
        # Rarity
        rarity_text = small_font.render(f"Rarity: {cosmetic.rarity}", 
                                       True, CosmeticRarity.COLORS.get(cosmetic.rarity, (150, 150, 150)))
        screen.blit(rarity_text, (tooltip_x + 15, y_offset))
        y_offset += 25
        
        # Pattern
        pattern_text = small_font.render(f"Pattern: {cosmetic.pattern.replace('_', ' ').title()}", 
                                        True, (200, 200, 200))
        screen.blit(pattern_text, (tooltip_x + 15, y_offset))
        y_offset += 25
        
        # Applies to
        applies_text = small_font.render(f"Type: {cosmetic.applies_to.title()}", 
                                        True, (200, 200, 200))
        screen.blit(applies_text, (tooltip_x + 15, y_offset))
        y_offset += 25
        
        # Color swatches with labels
        swatch_size = 30
        
        # Primary
        primary_label = small_font.render("Primary:", True, (200, 200, 200))
        screen.blit(primary_label, (tooltip_x + 15, y_offset))
        pygame.draw.rect(screen, cosmetic.primary_color, 
                        (tooltip_x + 100, y_offset, swatch_size, swatch_size))
        pygame.draw.rect(screen, (255, 255, 255), 
                        (tooltip_x + 100, y_offset, swatch_size, swatch_size), 1)
        y_offset += 35
        
        # Secondary
        secondary_label = small_font.render("Secondary:", True, (200, 200, 200))
        screen.blit(secondary_label, (tooltip_x + 15, y_offset))
        pygame.draw.rect(screen, cosmetic.secondary_color, 
                        (tooltip_x + 100, y_offset, swatch_size, swatch_size))
        pygame.draw.rect(screen, (255, 255, 255), 
                        (tooltip_x + 100, y_offset, swatch_size, swatch_size), 1)
    
    def handle_mouse_motion(self, pos: Tuple[int, int], cosmetic_manager: CosmeticManager):
        """Handle mouse movement for hover effects"""
        cosmetics = cosmetic_manager.get_unlocked_by_type(self.current_tab)
        
        grid_start_x = self.menu_x + self.item_padding
        grid_start_y = self.menu_y + 150
        
        self.hover_cosmetic = None
        self.hover_index = None
        
        for i, cosmetic in enumerate(cosmetics):
            row = i // self.items_per_row
            col = i % self.items_per_row
            
            x = grid_start_x + col * (self.item_size + self.item_padding)
            y = grid_start_y + row * (self.item_size + self.item_padding) - self.scroll_offset
            
            item_rect = pygame.Rect(x, y, self.item_size, self.item_size)
            
            if item_rect.collidepoint(pos):
                self.hover_cosmetic = cosmetic
                self.hover_index = i
                break
    
    def handle_mouse_click(self, pos: Tuple[int, int], 
                          cosmetic_manager: CosmeticManager) -> bool:
        """
        Handle mouse clicks
        
        Returns:
            bool: True if a cosmetic was equipped/unequipped
        """
        # Check tab clicks
        tab_width = self.menu_width // len(self.tabs)
        tab_height = 50
        tab_y = self.menu_y + 80
        
        for i, tab in enumerate(self.tabs):
            tab_x = self.menu_x + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            if tab_rect.collidepoint(pos):
                self.current_tab = tab
                self.scroll_offset = 0
                return False
        
        # Check cosmetic clicks
        if self.hover_cosmetic and self.hover_index is not None:
            equipped = cosmetic_manager.get_equipped(self.current_tab)
            
            if equipped and equipped.id == self.hover_cosmetic.id:
                # Unequip
                cosmetic_manager.unequip_cosmetic(self.current_tab)
            else:
                # Equip
                cosmetic_manager.equip_cosmetic(self.hover_cosmetic.id)
            
            return True
        
        return False
    
    def handle_scroll(self, amount: int, cosmetic_manager: CosmeticManager):
        """Handle mouse wheel scrolling"""
        cosmetics = cosmetic_manager.get_unlocked_by_type(self.current_tab)
        
        if not cosmetics:
            return
        
        # Calculate max scroll
        rows = (len(cosmetics) + self.items_per_row - 1) // self.items_per_row
        grid_height = self.menu_height - 200
        total_height = rows * (self.item_size + self.item_padding)
        max_scroll = max(0, total_height - grid_height)
        
        # Apply scroll
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - amount * 30))
