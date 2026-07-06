"""
Enhanced Inventory UI with Smart Management Features
Advanced inventory interface with sorting, filtering, favorites, and batch actions
"""

import pygame
import time
from collections import defaultdict

class SmartInventoryUI:
    def __init__(self, smart_inventory_manager):
        self.sim = smart_inventory_manager
        self.player = smart_inventory_manager.player  # Get player reference for stolen items
        self.active = False
        self.selected_index = 0
        self.view_mode = "grid"  # "grid", "list", "groups"
        self.search_query = ""
        self.search_active = False
        self.filtered_items = []
        
        # UI layout settings
        self.items_per_row = 8
        self.item_size = 48
        self.item_spacing = 4
        self.scroll_offset = 0
        self.max_visible_rows = 8
        
        # Colors and styling
        self.colors = {
            "background": (20, 25, 35, 240),
            "border": (100, 120, 140),
            "selected": (100, 150, 255, 100),
            "favorite": (255, 215, 0, 150),
            "junk": (120, 60, 60, 100),
            "text": (255, 255, 255),
            "text_dim": (180, 180, 180),
            "rarity_common": (150, 150, 150),
            "rarity_uncommon": (100, 255, 100),
            "rarity_rare": (100, 150, 255),
            "rarity_epic": (200, 100, 255),
            "rarity_legendary": (255, 165, 0),
            "rarity_set": (255, 215, 0)
        }
        
        # Button areas
        self.buttons = {
            "sort_type": {"x": 20, "y": 20, "w": 80, "h": 30, "text": "Type"},
            "sort_rarity": {"x": 110, "y": 20, "w": 80, "h": 30, "text": "Rarity"},
            "sort_value": {"x": 200, "y": 20, "w": 80, "h": 30, "text": "Value"},
            "sort_name": {"x": 290, "y": 20, "w": 80, "h": 30, "text": "Name"},
            "consolidate": {"x": 400, "y": 20, "w": 100, "h": 30, "text": "Stack"},
            "sell_junk": {"x": 510, "y": 20, "w": 100, "h": 30, "text": "Sell Junk"},
            "auto_sort": {"x": 620, "y": 20, "w": 80, "h": 30, "text": "Auto-Sort"}
        }
        
        # Last action feedback
        self.last_action_text = ""
        self.last_action_time = 0
        self.action_display_duration = 3.0
    
    def toggle(self):
        """Toggle inventory display"""
        self.active = not self.active
        if self.active:
            self.refresh_items()
            self.selected_index = 0
            self.scroll_offset = 0
    
    def refresh_items(self):
        """Refresh the filtered items list"""
        if self.search_query:
            self.filtered_items = self.sim.search_items(self.search_query)
        else:
            self.filtered_items = list(self.sim.inventory.items.keys())
    
    def handle_input(self, event, message_console=None):
        """Handle input events for smart inventory"""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.search_active:
                    self.search_active = False
                    self.search_query = ""
                    self.refresh_items()
                else:
                    self.active = False
                return True
            
            elif event.key == pygame.K_SLASH or event.key == pygame.K_f:
                # Activate search
                self.search_active = True
                self.search_query = ""
                return True
            
            elif self.search_active:
                if event.key == pygame.K_RETURN:
                    self.search_active = False
                    self.refresh_items()
                elif event.key == pygame.K_BACKSPACE:
                    self.search_query = self.search_query[:-1]
                    self.refresh_items()
                else:
                    # Add character to search
                    if event.unicode and event.unicode.isprintable():
                        self.search_query += event.unicode.lower()
                        self.refresh_items()
                return True
            
            # Navigation when not searching
            elif event.key == pygame.K_LEFT:
                self.move_selection(-1)
                return True
            elif event.key == pygame.K_RIGHT:
                self.move_selection(1)
                return True
            elif event.key == pygame.K_UP:
                self.move_selection(-self.items_per_row)
                return True
            elif event.key == pygame.K_DOWN:
                self.move_selection(self.items_per_row)
                return True
            
            # Actions
            elif event.key == pygame.K_SPACE:
                # Toggle favorite
                if self.selected_index < len(self.filtered_items):
                    item_id = self.filtered_items[self.selected_index]
                    is_favorite = self.sim.toggle_favorite(item_id)
                    status = "Added to" if is_favorite else "Removed from"
                    self.show_action_feedback(f"{status} favorites: {item_id}")
                return True
            
            elif event.key == pygame.K_DELETE:
                # Delete selected item
                if self.selected_index < len(self.filtered_items):
                    item_id = self.filtered_items[self.selected_index]
                    if item_id not in self.sim.favorites:  # Don't delete favorites by accident
                        del self.sim.inventory.items[item_id]
                        self.refresh_items()
                        self.show_action_feedback(f"Deleted: {item_id}")
                return True
            
            # Hotkeys for actions
            elif event.key == pygame.K_1:
                self.set_sort_mode("type")
                return True
            elif event.key == pygame.K_2:
                self.set_sort_mode("rarity")
                return True
            elif event.key == pygame.K_3:
                self.set_sort_mode("value")
                return True
            elif event.key == pygame.K_4:
                self.set_sort_mode("name")
                return True
            elif event.key == pygame.K_c:
                count = self.sim.consolidate_stacks()
                self.show_action_feedback(f"Consolidated {count} stacks")
                self.refresh_items()
                return True
            elif event.key == pygame.K_j:
                # Quick sell junk
                junk_count, value = self.sim.quick_sell_junk(self.sim.inventory.player if hasattr(self.sim.inventory, 'player') else None)
                self.show_action_feedback(f"Sold {junk_count} junk items for {value} dubloons")
                self.refresh_items()
                return True
            elif event.key == pygame.K_s:
                # Toggle auto-sort
                self.sim.auto_sort_enabled = not self.sim.auto_sort_enabled
                status = "enabled" if self.sim.auto_sort_enabled else "disabled"
                self.show_action_feedback(f"Auto-sort {status}")
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self.handle_mouse_click(event.pos)
        
        return False
    
    def move_selection(self, delta):
        """Move selection with bounds checking"""
        self.selected_index = max(0, min(len(self.filtered_items) - 1, self.selected_index + delta))
        self.update_scroll()
    
    def update_scroll(self):
        """Update scroll to keep selection visible"""
        if not self.filtered_items:
            return
        
        row = self.selected_index // self.items_per_row
        if row < self.scroll_offset:
            self.scroll_offset = row
        elif row >= self.scroll_offset + self.max_visible_rows:
            self.scroll_offset = row - self.max_visible_rows + 1
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks on buttons and items"""
        # Check button clicks
        for button_id, button in self.buttons.items():
            if (button["x"] <= pos[0] <= button["x"] + button["w"] and
                button["y"] <= pos[1] <= button["y"] + button["h"]):
                return self.handle_button_click(button_id)
        
        # Check item clicks (simplified - would need proper positioning)
        return False
    
    def handle_button_click(self, button_id):
        """Handle button clicks"""
        if button_id.startswith("sort_"):
            mode = button_id.replace("sort_", "")
            self.set_sort_mode(mode)
        elif button_id == "consolidate":
            count = self.sim.consolidate_stacks()
            self.show_action_feedback(f"Consolidated {count} stacks")
            self.refresh_items()
        elif button_id == "sell_junk":
            junk_count, value = self.sim.quick_sell_junk(None)  # Would need player reference
            self.show_action_feedback(f"Sold {junk_count} junk items for {value} dubloons")
            self.refresh_items()
        elif button_id == "auto_sort":
            self.sim.auto_sort_enabled = not self.sim.auto_sort_enabled
            status = "ON" if self.sim.auto_sort_enabled else "OFF"
            self.show_action_feedback(f"Auto-sort: {status}")
        return True
    
    def set_sort_mode(self, mode):
        """Change sort mode and resort"""
        self.sim.sort_mode = mode
        self.sim.smart_sort(force=True)
        self.refresh_items()
        self.show_action_feedback(f"Sorted by: {mode.title()}")
    
    def show_action_feedback(self, text):
        """Show feedback for actions"""
        self.last_action_text = text
        self.last_action_time = time.time()
    
    def render(self, screen, font):
        """Render the smart inventory interface"""
        if not self.active:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Main inventory window
        inv_width = 800
        inv_height = 600
        inv_x = (screen_width - inv_width) // 2
        inv_y = (screen_height - inv_height) // 2
        
        # Background
        inv_bg = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
        inv_bg.fill(self.colors["background"])
        pygame.draw.rect(inv_bg, self.colors["border"], (0, 0, inv_width, inv_height), 3)
        screen.blit(inv_bg, (inv_x, inv_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 28)
        title_text = title_font.render("SMART INVENTORY", True, self.colors["text"])
        screen.blit(title_text, (inv_x + 20, inv_y + 60))
        
        # Stats
        stats = self.sim.get_inventory_stats()
        stats_text = font.render(f"Items: {stats['total_items']} | Favorites: {stats['favorites']} | Value: {stats['total_value']}", 
                                True, self.colors["text_dim"])
        screen.blit(stats_text, (inv_x + 250, inv_y + 65))
        
        # Action buttons
        self.render_buttons(screen, font, inv_x, inv_y)
        
        # Search bar
        if self.search_active:
            search_bg = pygame.Surface((300, 30), pygame.SRCALPHA)
            search_bg.fill((50, 50, 50, 200))
            screen.blit(search_bg, (inv_x + 20, inv_y + 100))
            search_text = font.render(f"Search: {self.search_query}_", True, self.colors["text"])
            screen.blit(search_text, (inv_x + 25, inv_y + 105))
        
        # Item grid
        self.render_item_grid(screen, font, inv_x, inv_y + 140, inv_width - 40, inv_height - 200)
        
        # Action feedback
        if time.time() - self.last_action_time < self.action_display_duration:
            feedback_text = font.render(self.last_action_text, True, (100, 255, 100))
            screen.blit(feedback_text, (inv_x + 20, inv_y + inv_height - 40))
        
        # Help text
        help_text = font.render("F/Slash: Search | Space: Favorite | Del: Delete | 1-4: Sort | C: Stack | J: Sell Junk | S: Auto-Sort", 
                               True, self.colors["text_dim"])
        screen.blit(help_text, (inv_x + 20, inv_y + inv_height - 20))
    
    def render_buttons(self, screen, font, base_x, base_y):
        """Render action buttons"""
        for button_id, button in self.buttons.items():
            x = base_x + button["x"]
            y = base_y + button["y"]
            w = button["w"]
            h = button["h"]
            
            # Button background
            color = (60, 80, 100) if button_id != f"sort_{self.sim.sort_mode}" else (100, 140, 180)
            if button_id == "auto_sort":
                color = (100, 140, 100) if self.sim.auto_sort_enabled else (60, 80, 100)
            
            pygame.draw.rect(screen, color, (x, y, w, h))
            pygame.draw.rect(screen, self.colors["border"], (x, y, w, h), 2)
            
            # Button text
            text = font.render(button["text"], True, self.colors["text"])
            text_rect = text.get_rect(center=(x + w//2, y + h//2))
            screen.blit(text, text_rect)
    
    def render_item_grid(self, screen, font, x, y, width, height):
        """Render the item grid"""
        if not self.filtered_items:
            no_items_text = font.render("No items to display", True, self.colors["text_dim"])
            screen.blit(no_items_text, (x + width//2 - 80, y + height//2))
            return
        
        visible_items = self.filtered_items[self.scroll_offset * self.items_per_row:
                                          (self.scroll_offset + self.max_visible_rows) * self.items_per_row]
        
        for i, item_id in enumerate(visible_items):
            row = i // self.items_per_row
            col = i % self.items_per_row
            
            item_x = x + col * (self.item_size + self.item_spacing)
            item_y = y + row * (self.item_size + self.item_spacing)
            
            # Skip if outside visible area
            if item_y + self.item_size > y + height:
                break
            
            self.render_item_slot(screen, font, item_id, item_x, item_y, 
                                self.selected_index == (self.scroll_offset * self.items_per_row + i))
    
    def render_item_slot(self, screen, font, item_id, x, y, is_selected):
        """Render individual item slot"""
        item_data = self.sim.inventory.items.get(item_id, {})
        
        # Background
        bg_color = (40, 50, 60)
        if is_selected:
            bg_color = self.colors["selected"][:3]
        elif item_id in self.sim.favorites:
            bg_color = self.colors["favorite"][:3]
        elif item_id in self.sim.identify_junk_items():
            bg_color = self.colors["junk"][:3]
        
        pygame.draw.rect(screen, bg_color, (x, y, self.item_size, self.item_size))
        
        # Border
        border_color = self.colors["border"]
        if isinstance(item_data, dict) and "rarity" in item_data:
            rarity = item_data["rarity"]
            border_color = self.colors.get(f"rarity_{rarity}", self.colors["border"])
        
        pygame.draw.rect(screen, border_color, (x, y, self.item_size, self.item_size), 2)
        
        # Item icon (simplified - just first letter)
        icon_text = font.render(item_id[0].upper(), True, self.colors["text"])
        icon_rect = icon_text.get_rect(center=(x + self.item_size//2, y + self.item_size//2 - 5))
        screen.blit(icon_text, icon_rect)
        
        # Quantity
        if isinstance(item_data, dict):
            quantity = item_data.get("quantity", 1)
            if quantity > 1:
                qty_text = font.render(str(quantity), True, self.colors["text"])
                screen.blit(qty_text, (x + 2, y + self.item_size - 15))
        
        # Favorite indicator
        if item_id in self.sim.favorites:
            star_text = font.render("★", True, (255, 215, 0))
            screen.blit(star_text, (x + self.item_size - 12, y + 2))
        
        # Stolen item indicator (red X)
        if hasattr(self, 'player') and hasattr(self.player, 'stolen_items'):
            # Check if this item is in the stolen items list
            for stolen_item in self.player.stolen_items:
                if stolen_item.item_id == item_id and stolen_item.red_x:
                    # Draw red X overlay
                    pygame.draw.line(screen, (255, 0, 0), (x, y), 
                                   (x + self.item_size, y + self.item_size), 3)
                    pygame.draw.line(screen, (255, 0, 0), (x + self.item_size, y), 
                                   (x, y + self.item_size), 3)
                    break