"""
Diablo-style Equipment UI
Visual paper doll interface for managing equipment
"""
import pygame
import logging
from equipment_manager import EquipmentManager

logger = logging.getLogger(__name__)


class EquipmentUI:
    """Diablo-style equipment screen with visual paper doll"""
    
    def __init__(self, config, screen):
        self.config = config
        self.screen = screen
        self.active = False
        
        # UI dimensions
        self.width = min(1400, config.SCREEN_WIDTH - 40)
        self.height = min(900, config.SCREEN_HEIGHT - 40)
        self.x = (config.SCREEN_WIDTH - self.width) // 2
        self.y = (config.SCREEN_HEIGHT - self.height) // 2
        
        # Panels
        self.paperdoll_width = 400
        self.inventory_width = self.width - self.paperdoll_width - 60
        self.stats_height = 200
        
        # Inventory grid
        self.grid_cols = 6
        self.grid_rows = 8
        self.cell_size = 70
        self.grid_padding = 5
        
        # Selection and interaction
        self.selected_item = None
        self.selected_slot = None
        self.hovered_item = None
        self.hovered_slot = None
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Equipment manager reference (set when opening)
        self.equipment_manager = None
        self.player = None
        
        # Drag and drop
        self.dragging_item = None
        self.dragging_from_slot = None
        self.drag_offset = (0, 0)
        
        # Filters
        self.filter_type = 'all'  # 'all', 'weapons', 'armor', 'accessories'
        self.sort_by = 'type'  # 'type', 'rarity', 'name', 'slot'
        
        # Message display
        self.message = ""
        self.message_timer = 0
        self.message_color = (255, 255, 255)
        
    def open(self, player):
        """Open the equipment UI"""
        self.active = True
        self.player = player
        self.equipment_manager = EquipmentManager(player)
        self.selected_item = None
        self.selected_slot = None
        self.scroll_offset = 0
        self.message = ""
        logger.info("[EQUIPMENT UI] Opened")
    
    def close(self):
        """Close the equipment UI"""
        self.active = False
        self.selected_item = None
        self.selected_slot = None
        self.dragging_item = None
        logger.info("[EQUIPMENT UI] Closed")
    
    def handle_input(self, event):
        """Handle keyboard and mouse input"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_e:
                self.close()
                return 'close'
            elif event.key == pygame.K_TAB:
                # Cycle through filters
                filters = ['all', 'weapons', 'armor', 'accessories']
                current_idx = filters.index(self.filter_type)
                self.filter_type = filters[(current_idx + 1) % len(filters)]
                self.scroll_offset = 0
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_left_click(event.pos)
            elif event.button == 3:  # Right click
                return self._handle_right_click(event.pos)
            elif event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_item:
                return self._handle_drop(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)
            if self.dragging_item:
                # Update drag position
                pass
        
        return None
    
    def _handle_left_click(self, pos):
        """Handle left mouse click"""
        # Check if clicking on paper doll slots
        slot_clicked = self._get_slot_at_pos(pos)
        if slot_clicked:
            item = self.player.equipment.get(slot_clicked)
            if item:
                # Start dragging from slot
                self.dragging_item = item
                self.dragging_from_slot = slot_clicked
                logger.info(f"[EQUIPMENT UI] Started dragging {self.equipment_manager.get_item_name(item)} from {slot_clicked}")
            return None
        
        # Check if clicking on inventory items
        item_idx = self._get_inventory_item_at_pos(pos)
        if item_idx is not None:
            items = self._get_filtered_items()
            if item_idx < len(items):
                item = items[item_idx]['item']
                # Start dragging from inventory
                self.dragging_item = item
                self.dragging_from_slot = None
                logger.info(f"[EQUIPMENT UI] Started dragging {self.equipment_manager.get_item_name(item)} from inventory")
            return None
        
        return None
    
    def _handle_right_click(self, pos):
        """Handle right mouse click (quick equip/unequip)"""
        # Right-click on paper doll = unequip
        slot_clicked = self._get_slot_at_pos(pos)
        if slot_clicked:
            success, message = self.equipment_manager.unequip_item(slot_clicked)
            self._show_message(message, (0, 255, 0) if success else (255, 100, 100))
            return None
        
        # Right-click on inventory item = quick equip
        item_idx = self._get_inventory_item_at_pos(pos)
        if item_idx is not None:
            items = self._get_filtered_items()
            if item_idx < len(items):
                item = items[item_idx]['item']
                success, message, old_item = self.equipment_manager.equip_item(item)
                if old_item:
                    # Put old item back in inventory
                    self.player.inventory['items'].append(old_item)
                self._show_message(message, (0, 255, 0) if success else (255, 100, 100))
            return None
        
        return None
    
    def _handle_drop(self, pos):
        """Handle dropping a dragged item"""
        if not self.dragging_item:
            return None
        
        item = self.dragging_item
        from_slot = self.dragging_from_slot
        
        # Check if dropping on a paper doll slot
        target_slot = self._get_slot_at_pos(pos)
        if target_slot:
            if from_slot:
                # Moving from slot to slot
                success, message = self.equipment_manager.swap_equipment(from_slot, target_slot)
                self._show_message(message, (0, 255, 0) if success else (255, 100, 100))
            else:
                # Equipping from inventory to slot
                success, message, old_item = self.equipment_manager.equip_item(item, target_slot)
                if success and old_item:
                    self.player.inventory['items'].append(old_item)
                self._show_message(message, (0, 255, 0) if success else (255, 100, 100))
        else:
            # Dropping elsewhere
            if from_slot:
                # Unequip if dragging from a slot
                success, message = self.equipment_manager.unequip_item(from_slot)
                self._show_message(message, (0, 255, 0) if success else (255, 100, 100))
        
        # Clear drag state
        self.dragging_item = None
        self.dragging_from_slot = None
        return None
    
    def _update_hover(self, pos):
        """Update hovered item/slot"""
        self.hovered_slot = self._get_slot_at_pos(pos)
        item_idx = self._get_inventory_item_at_pos(pos)
        
        if item_idx is not None:
            items = self._get_filtered_items()
            if item_idx < len(items):
                self.hovered_item = items[item_idx]['item']
            else:
                self.hovered_item = None
        else:
            self.hovered_item = None
    
    def _show_message(self, message, color=(255, 255, 255)):
        """Show a temporary message"""
        self.message = message
        self.message_color = color
        self.message_timer = 180  # 3 seconds at 60 FPS
    
    def update(self, dt):
        """Update UI state"""
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def draw(self):
        """Draw the equipment UI"""
        if not self.active or not self.player:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Main panel background
        panel_bg = pygame.Surface((self.width, self.height))
        panel_bg.fill((30, 30, 40))
        self.screen.blit(panel_bg, (self.x, self.y))
        pygame.draw.rect(self.screen, (100, 100, 120), (self.x, self.y, self.width, self.height), 3)
        
        # Title
        title_font = pygame.font.SysFont(None, 56)
        title = title_font.render("Equipment", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.x + self.width // 2, self.y + 40))
        self.screen.blit(title, title_rect)
        
        # Instructions
        inst_font = pygame.font.SysFont(None, 22)
        instructions = [
            "Left-Click & Drag: Move Item | Right-Click: Quick Equip/Unequip",
            "TAB: Filter Items | Mouse Wheel: Scroll | E/ESC: Close"
        ]
        inst_y = self.y + 80
        for inst in instructions:
            inst_text = inst_font.render(inst, True, (180, 180, 180))
            inst_rect = inst_text.get_rect(center=(self.x + self.width // 2, inst_y))
            self.screen.blit(inst_text, inst_rect)
            inst_y += 25
        
        # Draw panels
        content_y = self.y + 140
        self._draw_paperdoll_panel(self.x + 20, content_y)
        self._draw_inventory_panel(self.x + self.paperdoll_width + 40, content_y)
        self._draw_stats_panel(self.x + 20, content_y + 500)
        
        # Draw message if active
        if self.message_timer > 0:
            msg_font = pygame.font.SysFont(None, 36)
            msg_text = msg_font.render(self.message, True, self.message_color)
            msg_rect = msg_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, self.y + self.height + 30))
            self.screen.blit(msg_text, msg_rect)
        
        # Draw dragged item
        if self.dragging_item:
            mouse_pos = pygame.mouse.get_pos()
            self._draw_dragged_item(mouse_pos)
    
    def _draw_paperdoll_panel(self, x, y):
        """Draw the paper doll character with equipment slots"""
        # Panel background
        pygame.draw.rect(self.screen, (40, 40, 50), (x, y, self.paperdoll_width, 480))
        pygame.draw.rect(self.screen, (80, 80, 100), (x, y, self.paperdoll_width, 480), 2)
        
        # Title
        font = pygame.font.SysFont(None, 28)
        title = font.render("Equipped", True, (200, 200, 255))
        self.screen.blit(title, (x + 10, y + 10))
        
        # Character silhouette (simplified)
        center_x = x + self.paperdoll_width // 2
        center_y = y + 250
        
        # Draw character outline
        pygame.draw.circle(self.screen, (100, 100, 100), (center_x, center_y - 80), 30, 2)  # Head
        pygame.draw.rect(self.screen, (100, 100, 100), (center_x - 30, center_y - 40, 60, 80), 2)  # Body
        pygame.draw.line(self.screen, (100, 100, 100), (center_x, center_y + 40), (center_x - 25, center_y + 100), 2)  # Left leg
        pygame.draw.line(self.screen, (100, 100, 100), (center_x, center_y + 40), (center_x + 25, center_y + 100), 2)  # Right leg
        pygame.draw.line(self.screen, (100, 100, 100), (center_x - 30, center_y - 30), (center_x - 70, center_y + 10), 2)  # Left arm
        pygame.draw.line(self.screen, (100, 100, 100), (center_x + 30, center_y - 30), (center_x + 70, center_y + 10), 2)  # Right arm
        
        # Equipment slot positions (relative to character)
        slot_positions = {
            'head': (center_x, center_y - 140),
            'neck': (center_x, center_y - 90),
            'chest': (center_x, center_y),
            'main_hand': (center_x + 100, center_y),
            'off_hand': (center_x - 100, center_y),
            'hands': (center_x, center_y + 50),
            'legs': (center_x, center_y + 90),
            'feet': (center_x, center_y + 130),
            'ring1': (center_x - 130, center_y + 90),
            'ring2': (center_x + 130, center_y + 90),
        }
        
        # Draw equipment slots
        for slot, pos in slot_positions.items():
            self._draw_equipment_slot(pos[0], pos[1], slot)
    
    def _draw_equipment_slot(self, x, y, slot):
        """Draw a single equipment slot"""
        slot_size = 50
        slot_rect = pygame.Rect(x - slot_size // 2, y - slot_size // 2, slot_size, slot_size)
        
        # Determine color based on hover/selection
        border_color = (120, 120, 140)
        if self.hovered_slot == slot:
            border_color = (255, 255, 100)
        
        # Background
        pygame.draw.rect(self.screen, (50, 50, 60), slot_rect)
        pygame.draw.rect(self.screen, border_color, slot_rect, 2)
        
        # Get equipped item
        item = self.player.equipment.get(slot)
        
        if item:
            # Draw item representation
            self._draw_item_icon(self.screen, item, slot_rect.centerx, slot_rect.centery, slot_size - 10)
        else:
            # Draw slot icon/text
            small_font = pygame.font.SysFont(None, 16)
            slot_name = self.equipment_manager.slots.get(slot, {}).get('name', slot)
            # Abbreviate slot name
            abbrev = self._get_slot_abbreviation(slot_name)
            text = small_font.render(abbrev, True, (100, 100, 100))
            text_rect = text.get_rect(center=slot_rect.center)
            self.screen.blit(text, text_rect)
    
    def _get_slot_abbreviation(self, slot_name):
        """Get abbreviation for slot name"""
        abbrevs = {
            'Head': 'HD',
            'Neck': 'NK',
            'Chest': 'CH',
            'Main Hand': 'MH',
            'Off Hand': 'OH',
            'Hands': 'GL',
            'Legs': 'LG',
            'Feet': 'FT',
            'Ring 1': 'R1',
            'Ring 2': 'R2',
        }
        return abbrevs.get(slot_name, slot_name[:2].upper())
    
    def _draw_inventory_panel(self, x, y):
        """Draw the inventory grid"""
        # Panel background
        panel_height = 480
        pygame.draw.rect(self.screen, (40, 40, 50), (x, y, self.inventory_width, panel_height))
        pygame.draw.rect(self.screen, (80, 80, 100), (x, y, self.inventory_width, panel_height), 2)
        
        # Title with filter
        font = pygame.font.SysFont(None, 28)
        title = font.render(f"Inventory - {self.filter_type.title()}", True, (200, 200, 255))
        self.screen.blit(title, (x + 10, y + 10))
        
        # Get filtered items
        items = self._get_filtered_items()
        
        # Calculate grid
        grid_x = x + 20
        grid_y = y + 50
        
        # Draw items in grid
        visible_items = min(self.grid_cols * self.grid_rows, len(items))
        start_idx = self.scroll_offset * self.grid_cols
        
        for i in range(visible_items):
            idx = start_idx + i
            if idx >= len(items):
                break
            
            item_data = items[idx]
            item = item_data['item']
            
            # Calculate grid position
            grid_col = i % self.grid_cols
            grid_row = i // self.grid_cols
            
            cell_x = grid_x + grid_col * (self.cell_size + self.grid_padding)
            cell_y = grid_y + grid_row * (self.cell_size + self.grid_padding)
            
            # Draw cell
            self._draw_inventory_cell(cell_x, cell_y, item, idx == self._get_hovered_inventory_idx())
        
        # Update max scroll
        total_rows = (len(items) + self.grid_cols - 1) // self.grid_cols
        self.max_scroll = max(0, total_rows - self.grid_rows)
        
        # Draw scrollbar if needed
        if self.max_scroll > 0:
            self._draw_scrollbar(x + self.inventory_width - 15, grid_y, panel_height - 60)
    
    def _draw_inventory_cell(self, x, y, item, is_hovered):
        """Draw a single inventory cell"""
        cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        
        # Background color based on rarity
        rarity_colors = {
            'common': (80, 80, 80),
            'uncommon': (50, 150, 50),
            'rare': (50, 100, 200),
            'epic': (150, 50, 200),
            'legendary': (255, 150, 0),
        }
        
        rarity = getattr(item, 'rarity', 'common')
        bg_color = rarity_colors.get(rarity, (80, 80, 80))
        
        # Draw background
        pygame.draw.rect(self.screen, bg_color, cell_rect)
        
        # Border
        border_color = (255, 255, 100) if is_hovered else (120, 120, 120)
        pygame.draw.rect(self.screen, border_color, cell_rect, 2)
        
        # Draw item icon
        self._draw_item_icon(self.screen, item, cell_rect.centerx, cell_rect.centery, self.cell_size - 10)
        
        # Item name (truncated)
        name_font = pygame.font.SysFont(None, 14)
        name = self.equipment_manager.get_item_name(item)
        if len(name) > 10:
            name = name[:9] + '...'
        name_text = name_font.render(name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(cell_rect.centerx, cell_rect.bottom - 8))
        self.screen.blit(name_text, name_rect)
    
    def _draw_item_icon(self, screen, item, x, y, size):
        """Draw a simple icon representation of an item"""
        item_type = self.equipment_manager.get_item_type(item)
        if not item_type:
            return
        
        item_type_lower = item_type.lower()
        
        # Draw different shapes based on item type
        if 'sword' in item_type_lower or 'weapon' in item_type_lower or 'stick' in item_type_lower:
            # Sword shape
            pygame.draw.line(screen, (200, 200, 200), (x, y - size//2), (x, y + size//2), 4)
            pygame.draw.line(screen, (150, 150, 150), (x - size//3, y - size//4), (x + size//3, y - size//4), 3)
        elif 'shield' in item_type_lower:
            # Shield shape
            pygame.draw.circle(screen, (180, 150, 100), (x, y), size//2, 0)
            pygame.draw.circle(screen, (100, 100, 100), (x, y), size//2, 2)
        elif 'helmet' in item_type_lower or 'head' in item_type_lower:
            # Helmet shape
            pygame.draw.arc(screen, (150, 150, 150), (x - size//2, y - size//2, size, size), 0, 3.14, 3)
        elif 'armor' in item_type_lower or 'chest' in item_type_lower:
            # Armor shape
            rect = pygame.Rect(x - size//3, y - size//2, size*2//3, size)
            pygame.draw.rect(screen, (150, 150, 150), rect, 3)
        elif 'ring' in item_type_lower:
            # Ring shape
            pygame.draw.circle(screen, (255, 215, 0), (x, y), size//3, 3)
        else:
            # Generic shape
            pygame.draw.rect(screen, (150, 150, 150), (x - size//3, y - size//3, size*2//3, size*2//3), 2)
    
    def _draw_stats_panel(self, x, y):
        """Draw the stats comparison panel"""
        panel_width = self.width - 40
        pygame.draw.rect(self.screen, (40, 40, 50), (x, y, panel_width, self.stats_height))
        pygame.draw.rect(self.screen, (80, 80, 100), (x, y, panel_width, self.stats_height), 2)
        
        # Title
        font = pygame.font.SysFont(None, 28)
        title = font.render("Stats", True, (200, 200, 255))
        self.screen.blit(title, (x + 10, y + 10))
        
        # Display total equipment stats
        total_stats = self.equipment_manager.get_total_stats()
        
        stat_font = pygame.font.SysFont(None, 24)
        stat_x = x + 20
        stat_y = y + 50
        col_width = panel_width // 3
        
        stat_names = ['damage', 'defense', 'Defense', 'attack', 'health', 'mana', 'stamina']
        displayed_stats = {}
        
        # Combine similar stats
        for stat in stat_names:
            if stat in total_stats:
                # Normalize stat name
                normalized = stat.lower()
                if normalized in displayed_stats:
                    displayed_stats[normalized] += total_stats[stat]
                else:
                    displayed_stats[normalized] = total_stats[stat]
        
        # Display stats in columns
        col = 0
        row = 0
        for stat_name, stat_value in displayed_stats.items():
            if stat_value == 0:
                continue
            
            display_name = stat_name.title()
            stat_text = stat_font.render(f"{display_name}: +{stat_value}", True, (100, 255, 100))
            self.screen.blit(stat_text, (stat_x + col * col_width, stat_y + row * 30))
            
            row += 1
            if row >= 4:
                row = 0
                col += 1
        
        # Show comparison if hovering over an item
        if self.hovered_item and self.hovered_slot:
            equipped_item = self.player.equipment.get(self.hovered_slot)
            comparison = self.equipment_manager.compare_items(equipped_item, self.hovered_item)
            
            comp_y = y + 140
            comp_title = font.render("Item Comparison", True, (255, 215, 0))
            self.screen.blit(comp_title, (x + 10, comp_y))
            
            comp_y += 30
            for stat_name, (old_val, new_val, diff) in comparison.items():
                if diff == 0:
                    continue
                
                color = (100, 255, 100) if diff > 0 else (255, 100, 100)
                sign = '+' if diff > 0 else ''
                comp_text = stat_font.render(f"{stat_name.title()}: {old_val} → {new_val} ({sign}{diff})", True, color)
                self.screen.blit(comp_text, (x + 20, comp_y))
                comp_y += 25
    
    def _draw_scrollbar(self, x, y, height):
        """Draw a scrollbar"""
        # Track
        pygame.draw.rect(self.screen, (60, 60, 70), (x, y, 10, height))
        
        # Thumb
        if self.max_scroll > 0:
            thumb_height = max(20, height * self.grid_rows / (self.max_scroll + self.grid_rows))
            thumb_y = y + (height - thumb_height) * (self.scroll_offset / self.max_scroll)
            pygame.draw.rect(self.screen, (150, 150, 160), (x, thumb_y, 10, thumb_height))
    
    def _draw_dragged_item(self, pos):
        """Draw the item being dragged"""
        if not self.dragging_item:
            return
        
        # Draw item at mouse position
        size = 60
        x, y = pos
        
        # Semi-transparent background
        drag_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        drag_surf.fill((100, 100, 100, 150))
        self.screen.blit(drag_surf, (x - size // 2, y - size // 2))
        
        # Draw item icon
        self._draw_item_icon(self.screen, self.dragging_item, x, y, size - 10)
        
        # Item name
        font = pygame.font.SysFont(None, 20)
        name = self.equipment_manager.get_item_name(self.dragging_item)
        name_text = font.render(name, True, (255, 255, 255))
        self.screen.blit(name_text, (x - name_text.get_width() // 2, y + size // 2 + 5))
    
    def _get_slot_at_pos(self, pos):
        """Get the equipment slot at a mouse position"""
        if not self.active:
            return None
        
        content_y = self.y + 140
        center_x = self.x + 20 + self.paperdoll_width // 2
        center_y = content_y + 250
        
        slot_positions = {
            'head': (center_x, center_y - 140),
            'neck': (center_x, center_y - 90),
            'chest': (center_x, center_y),
            'main_hand': (center_x + 100, center_y),
            'off_hand': (center_x - 100, center_y),
            'hands': (center_x, center_y + 50),
            'legs': (center_x, center_y + 90),
            'feet': (center_x, center_y + 130),
            'ring1': (center_x - 130, center_y + 90),
            'ring2': (center_x + 130, center_y + 90),
        }
        
        slot_size = 50
        for slot, (sx, sy) in slot_positions.items():
            slot_rect = pygame.Rect(sx - slot_size // 2, sy - slot_size // 2, slot_size, slot_size)
            if slot_rect.collidepoint(pos):
                return slot
        
        return None
    
    def _get_inventory_item_at_pos(self, pos):
        """Get the inventory item index at a mouse position"""
        if not self.active:
            return None
        
        content_y = self.y + 140
        grid_x = self.x + self.paperdoll_width + 40 + 20
        grid_y = content_y + 50
        
        # Check if pos is within inventory grid
        relative_x = pos[0] - grid_x
        relative_y = pos[1] - grid_y
        
        if relative_x < 0 or relative_y < 0:
            return None
        
        # Calculate grid position
        cell_total_size = self.cell_size + self.grid_padding
        grid_col = relative_x // cell_total_size
        grid_row = relative_y // cell_total_size
        
        if grid_col >= self.grid_cols or grid_row >= self.grid_rows:
            return None
        
        # Check if actually within cell (not in padding)
        cell_x = relative_x % cell_total_size
        cell_y = relative_y % cell_total_size
        
        if cell_x > self.cell_size or cell_y > self.cell_size:
            return None
        
        # Calculate item index
        item_idx = self.scroll_offset * self.grid_cols + grid_row * self.grid_cols + grid_col
        
        return item_idx
    
    def _get_hovered_inventory_idx(self):
        """Get the currently hovered inventory item index"""
        if not self.hovered_item:
            return None
        
        items = self._get_filtered_items()
        for idx, item_data in enumerate(items):
            if item_data['item'] == self.hovered_item:
                return idx
        
        return None
    
    def _get_filtered_items(self):
        """Get inventory items filtered by current filter"""
        all_items = self.equipment_manager.get_equippable_items()
        
        if self.filter_type == 'all':
            return all_items
        
        filtered = []
        for item_data in all_items:
            item_type = self.equipment_manager.get_item_type(item_data['item'])
            if not item_type:
                continue
            
            item_type_lower = item_type.lower()
            
            if self.filter_type == 'weapons':
                if any(w in item_type_lower for w in ['weapon', 'sword', 'axe', 'staff', 'wand', 'dagger', 'spear', 'stick']):
                    filtered.append(item_data)
            elif self.filter_type == 'armor':
                if any(a in item_type_lower for a in ['armor', 'helmet', 'chest', 'legs', 'boots', 'gloves', 'shield']):
                    filtered.append(item_data)
            elif self.filter_type == 'accessories':
                if any(a in item_type_lower for a in ['ring', 'necklace', 'amulet', 'accessory']):
                    filtered.append(item_data)
        
        return filtered
