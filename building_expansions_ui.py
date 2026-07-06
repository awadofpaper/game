"""
Building Expansions UI
Unified interface for all building expansion features:
- Blacksmith Equipment Selling (integrated into blacksmith_system.py)
- Tavern Food Trading
- Market Player Stalls
- Bank Safety Deposit Boxes
"""

import pygame
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# TAVERN FOOD TRADING UI
# =============================================================================

class TavernFoodTradingUI:
    """UI for buying and selling food at taverns"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.current_tavern = None
        
        # UI state
        self.mode = "main"  # main, sell, buy
        self.selected_index = 0
        self.quantity_input = ""
        self.input_mode = False
        self.message = ""
        self.message_timer = 0
        
        # Colors
        self.bg_color = (15, 10, 25)
        self.panel_color = (35, 25, 50)
        self.selected_color = (80, 60, 100)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.green_color = (100, 255, 100)
        self.red_color = (255, 100, 100)
    
    def open(self, tavern, player):
        """Open the food trading UI"""
        self.active = True
        self.current_tavern = tavern
        self.mode = "main"
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        self.input_mode = False
        self.quantity_input = ""
        logger.info("[TAVERN FOOD TRADE] Opened")
    
    def close(self):
        """Close the UI"""
        self.active = False
        self.current_tavern = None
        self.mode = "main"
        logger.info("[TAVERN FOOD TRADE] Closed")
    
    def handle_input(self, event, player) -> str:
        """Handle input events, returns 'close' if should close"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            # Handle quantity input mode
            if self.input_mode:
                if event.key == pygame.K_RETURN:
                    self._process_quantity_input(player)
                    return None
                elif event.key == pygame.K_ESCAPE:
                    self.input_mode = False
                    self.quantity_input = ""
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    self.quantity_input = self.quantity_input[:-1]
                    return None
                elif event.unicode.isdigit() and len(self.quantity_input) < 5:
                    self.quantity_input += event.unicode
                    return None
            
            # Normal navigation
            if event.key == pygame.K_ESCAPE:
                if self.mode == "main":
                    return "close"
                else:
                    self.mode = "main"
                    self.selected_index = 0
            
            elif event.key == pygame.K_UP:
                items = self._get_current_items(player)
                if items:
                    self.selected_index = (self.selected_index - 1) % len(items)
            
            elif event.key == pygame.K_DOWN:
                items = self._get_current_items(player)
                if items:
                    self.selected_index = (self.selected_index + 1) % len(items)
            
            elif event.key == pygame.K_RETURN:
                if self.mode == "main":
                    if self.selected_index == 0:
                        self.mode = "sell"
                        self.selected_index = 0
                    elif self.selected_index == 1:
                        self.mode = "buy"
                        self.selected_index = 0
                    elif self.selected_index == 2:
                        return "close"
                else:
                    # Start quantity input
                    self.input_mode = True
                    self.quantity_input = "1"
        
        return None
    
    def _get_current_items(self, player) -> List:
        """Get items for current mode"""
        if self.mode == "main":
            return ["Sell Food", "Buy Food", "Back"]
        elif self.mode == "sell":
            return self.current_tavern.food_trading.get_sellable_food(player)
        elif self.mode == "buy":
            return self.current_tavern.food_trading.get_buyable_food()
        return []
    
    def _process_quantity_input(self, player):
        """Process the quantity input"""
        try:
            quantity = int(self.quantity_input) if self.quantity_input else 1
            quantity = max(1, quantity)
        except ValueError:
            quantity = 1
        
        self.input_mode = False
        self.quantity_input = ""
        
        items = self._get_current_items(player)
        if not items or self.selected_index >= len(items):
            return
        
        if self.mode == "sell":
            item_name, available, price_per_item = items[self.selected_index]
            quantity = min(quantity, available)
            success, message = self.current_tavern.food_trading.sell_food_to_tavern(
                player, item_name, quantity
            )
            self.message = message
            self.message_timer = 180
        
        elif self.mode == "buy":
            item_name, price_per_item = items[self.selected_index]
            success, message = self.current_tavern.food_trading.buy_food_from_tavern(
                player, item_name, quantity
            )
            self.message = message
            self.message_timer = 180
    
    def draw(self, screen, player):
        """Draw the food trading UI"""
        if not self.active:
            return
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 700
        panel_height = 550
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((self.panel_color[0], self.panel_color[1], self.panel_color[2], 240))
        pygame.draw.rect(panel, self.gold_color, (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        if self.mode == "main":
            title_text = "Food Trading"
        elif self.mode == "sell":
            title_text = "Sell Food to Tavern"
        else:
            title_text = "Buy Food from Tavern"
        
        title = title_font.render(title_text, True, self.gold_color)
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Player dubloons
        info_font = pygame.font.SysFont(None, 28)
        gold_text = info_font.render(f"Your Dubloons: {player.gold}db", True, self.gold_color)
        screen.blit(gold_text, (panel_x + 20, panel_y + 80))
        
        # Content
        content_y = panel_y + 130
        
        if self.mode == "main":
            self._draw_main_menu(screen, panel_x, content_y, panel_width)
        elif self.mode == "sell":
            self._draw_sell_menu(screen, panel_x, content_y, panel_width, player)
        elif self.mode == "buy":
            self._draw_buy_menu(screen, panel_x, content_y, panel_width, player)
        
        # Instructions
        instr_y = panel_y + panel_height - 50
        instr_font = pygame.font.SysFont(None, 24)
        
        if self.input_mode:
            instructions = ["Type quantity", "ENTER: Confirm", "ESC: Cancel"]
        elif self.mode == "main":
            instructions = ["↑↓: Select", "ENTER: Choose", "ESC: Close"]
        else:
            instructions = ["↑↓: Select", "ENTER: Set Quantity", "ESC: Back"]
        
        instr_x = panel_x + 20
        for instruction in instructions:
            instr = instr_font.render(instruction, True, (200, 180, 150))
            screen.blit(instr, (instr_x, instr_y))
            instr_x += 220
        
        # Message
        if self.message:
            msg_font = pygame.font.SysFont(None, 32)
            msg_color = self.green_color if "!" in self.message and "Not enough" not in self.message else self.red_color
            msg_surf = msg_font.render(self.message, True, msg_color)
            
            msg_x = (self.screen_width - msg_surf.get_width()) // 2
            msg_y = panel_y + panel_height + 20
            
            msg_bg = pygame.Surface((msg_surf.get_width() + 40, msg_surf.get_height() + 20), pygame.SRCALPHA)
            msg_bg.fill((20, 20, 20, 220))
            pygame.draw.rect(msg_bg, msg_color, (0, 0, msg_bg.get_width(), msg_bg.get_height()), 2)
            
            screen.blit(msg_bg, (msg_x - 20, msg_y - 10))
            screen.blit(msg_surf, (msg_x, msg_y))
        
        # Quantity input overlay
        if self.input_mode:
            self._draw_quantity_input(screen)
    
    def _draw_main_menu(self, screen, panel_x, start_y, panel_width):
        """Draw main menu options"""
        options = ["Sell Food to Tavern", "Buy Food from Tavern", "Back to Services"]
        font = pygame.font.SysFont(None, 36)
        
        for i, option in enumerate(options):
            y_pos = start_y + i * 80
            is_selected = (i == self.selected_index)
            
            # Background
            bg_color = self.selected_color if is_selected else (50, 40, 60)
            bg = pygame.Surface((panel_width - 40, 70), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                pygame.draw.rect(bg, self.gold_color, (0, 0, panel_width - 40, 70), 3)
            
            screen.blit(bg, (panel_x + 20, y_pos))
            
            # Text
            text = font.render(option, True, self.text_color)
            screen.blit(text, (panel_x + 40, y_pos + 20))
    
    def _draw_sell_menu(self, screen, panel_x, start_y, panel_width, player):
        """Draw sell food menu"""
        items = self._get_current_items(player)
        
        if not items:
            no_items_font = pygame.font.SysFont(None, 36)
            no_items = no_items_font.render("No food items to sell", True, (200, 150, 100))
            screen.blit(no_items, (panel_x + panel_width // 2 - no_items.get_width() // 2, start_y + 100))
            return
        
        font = pygame.font.SysFont(None, 28)
        
        # Show up to 6 items at a time
        visible_count = 6
        scroll_offset = max(0, self.selected_index - visible_count + 1)
        
        for i in range(scroll_offset, min(scroll_offset + visible_count, len(items))):
            item_name, quantity, price_per_item = items[i]
            y_pos = start_y + (i - scroll_offset) * 65
            is_selected = (i == self.selected_index)
            
            # Background
            bg_color = self.selected_color if is_selected else (50, 40, 60)
            bg = pygame.Surface((panel_width - 40, 60), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                pygame.draw.rect(bg, self.gold_color, (0, 0, panel_width - 40, 60), 2)
            
            screen.blit(bg, (panel_x + 20, y_pos))
            
            # Item name and quantity
            item_display = item_name.replace('_', ' ').title()
            text = font.render(f"{item_display} x{quantity}", True, self.text_color)
            screen.blit(text, (panel_x + 40, y_pos + 10))
            
            # Price (in green since selling)
            price_text = font.render(f"+{price_per_item}g each", True, self.green_color)
            screen.blit(price_text, (panel_x + panel_width - 180, y_pos + 10))
            
            # Total if selling all
            total = price_per_item * quantity
            total_text = font.render(f"(All: {total}g)", True, (150, 150, 150))
            screen.blit(total_text, (panel_x + 40, y_pos + 35))
    
    def _draw_buy_menu(self, screen, panel_x, start_y, panel_width, player):
        """Draw buy food menu"""
        items = self._get_current_items(player)
        
        if not items:
            no_items_font = pygame.font.SysFont(None, 36)
            no_items = no_items_font.render("No food available", True, (200, 150, 100))
            screen.blit(no_items, (panel_x + panel_width // 2 - no_items.get_width() // 2, start_y + 100))
            return
        
        font = pygame.font.SysFont(None, 28)
        
        for i, (item_name, price) in enumerate(items):
            y_pos = start_y + i * 70
            is_selected = (i == self.selected_index)
            
            # Background
            bg_color = self.selected_color if is_selected else (50, 40, 60)
            bg = pygame.Surface((panel_width - 40, 65), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                pygame.draw.rect(bg, self.gold_color, (0, 0, panel_width - 40, 65), 2)
            
            screen.blit(bg, (panel_x + 20, y_pos))
            
            # Item name
            item_display = item_name.replace('_', ' ').title()
            text = font.render(item_display, True, self.text_color)
            screen.blit(text, (panel_x + 40, y_pos + 20))
            
            # Price
            can_afford = player.gold >= price
            price_color = self.gold_color if can_afford else self.red_color
            price_text = font.render(f"{price}g", True, price_color)
            screen.blit(price_text, (panel_x + panel_width - 120, y_pos + 20))
    
    def _draw_quantity_input(self, screen):
        """Draw quantity input overlay"""
        overlay = pygame.Surface((400, 150), pygame.SRCALPHA)
        overlay.fill((30, 20, 40, 250))
        pygame.draw.rect(overlay, self.gold_color, (0, 0, 400, 150), 3)
        
        overlay_x = (self.screen_width - 400) // 2
        overlay_y = (self.screen_height - 150) // 2
        screen.blit(overlay, (overlay_x, overlay_y))
        
        # Title
        font = pygame.font.SysFont(None, 32)
        title = font.render("Enter Quantity:", True, self.text_color)
        screen.blit(title, (overlay_x + 20, overlay_y + 20))
        
        # Input box
        input_box = pygame.Surface((360, 50), pygame.SRCALPHA)
        input_box.fill((60, 50, 70))
        pygame.draw.rect(input_box, self.gold_color, (0, 0, 360, 50), 2)
        screen.blit(input_box, (overlay_x + 20, overlay_y + 70))
        
        # Input text
        input_font = pygame.font.SysFont(None, 40)
        input_text = input_font.render(self.quantity_input, True, self.gold_color)
        screen.blit(input_text, (overlay_x + 30, overlay_y + 80))


# =============================================================================
# MARKET PLAYER STALLS UI
# =============================================================================

class MarketStallUI:
    """UI for managing player market stalls"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.current_town = None
        self.stall_system = None
        self.player_name = None
        
        # UI state
        self.mode = "browse"  # browse, manage, add_item
        self.selected_index = 0
        self.quantity_input = ""
        self.price_input = ""
        self.input_mode = None  # None, "quantity", "price"
        self.message = ""
        self.message_timer = 0
        self.selected_item_name = None
        
        # Colors
        self.bg_color = (15, 10, 25)
        self.panel_color = (35, 25, 50)
        self.selected_color = (80, 60, 100)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.green_color = (100, 255, 100)
        self.red_color = (255, 100, 100)
    
    def open(self, town_name: str, stall_system, player):
        """Open the market stall UI"""
        self.active = True
        self.current_town = town_name
        self.stall_system = stall_system
        self.player_name = player.name if hasattr(player, 'name') else "Player"
        self.mode = "browse"
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        logger.info(f"[MARKET STALL] Opened in {town_name}")
    
    def close(self):
        """Close the UI"""
        self.active = False
        self.mode = "browse"
        logger.info("[MARKET STALL] Closed")
    
    def handle_input(self, event, player) -> str:
        """Handle input events"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            # Handle input modes
            if self.input_mode:
                if event.key == pygame.K_RETURN:
                    self._process_input(player)
                    return None
                elif event.key == pygame.K_ESCAPE:
                    self.input_mode = None
                    self.quantity_input = ""
                    self.price_input = ""
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    if self.input_mode == "quantity":
                        self.quantity_input = self.quantity_input[:-1]
                    elif self.input_mode == "price":
                        self.price_input = self.price_input[:-1]
                    return None
                elif event.unicode.isdigit():
                    if self.input_mode == "quantity" and len(self.quantity_input) < 5:
                        self.quantity_input += event.unicode
                    elif self.input_mode == "price" and len(self.price_input) < 6:
                        self.price_input += event.unicode
                    return None
            
            # Normal navigation
            if event.key == pygame.K_ESCAPE:
                if self.mode == "browse":
                    return "close"
                else:
                    self.mode = "browse"
                    self.selected_index = 0
                    self.selected_item_name = None
            
            elif event.key == pygame.K_UP:
                items = self._get_current_items(player)
                if items:
                    self.selected_index = (self.selected_index - 1) % len(items)
            
            elif event.key == pygame.K_DOWN:
                items = self._get_current_items(player)
                if items:
                    self.selected_index = (self.selected_index + 1) % len(items)
            
            elif event.key == pygame.K_RETURN:
                self._handle_selection(player)
        
        return None
    
    def _get_current_items(self, player) -> List:
        """Get items for current mode"""
        if self.mode == "browse":
            stalls = self.stall_system.get_stalls(self.current_town)
            player_stall = self.stall_system.get_player_stall(self.current_town, self.player_name)
            
            if player_stall:
                return ["Manage Your Stall", "View Other Stalls", "Back"]
            else:
                # Show available stalls to rent
                available = [s for s in stalls if not s.is_rented]
                return available + ["View Other Stalls", "Back"]
        
        elif self.mode == "manage":
            player_stall = self.stall_system.get_player_stall(self.current_town, self.player_name)
            if player_stall:
                options = ["Add Item", "Remove Item", "Collect Revenue", f"Days Left: {player_stall.days_remaining}", "Back"]
                return options
            return ["Back"]
        
        elif self.mode == "add_item":
            # Show player inventory
            return [(name, qty) for name, qty in player.inventory.items() if qty > 0]
        
        return []
    
    def _handle_selection(self, player):
        """Handle ENTER key selection"""
        items = self._get_current_items(player)
        if not items or self.selected_index >= len(items):
            return
        
        selected = items[self.selected_index]
        
        if self.mode == "browse":
            if isinstance(selected, str):
                if selected == "Manage Your Stall":
                    self.mode = "manage"
                    self.selected_index = 0
                elif selected == "Back":
                    self.close()
            else:
                # Rent stall
                stall = selected
                days = 7  # Rent for 7 days
                total_cost = stall.rental_cost * days
                
                if player.gold >= total_cost:
                    player.gold -= total_cost
                    success, message = stall.rent(self.player_name, days)
                    self.message = f"{message} Cost: {total_cost}db"
                    self.message_timer = 180
                else:
                    self.message = f"Not enough dubloons! Need {total_cost}db"
                    self.message_timer = 120
        
        elif self.mode == "manage":
            if isinstance(selected, str):
                if selected == "Add Item":
                    self.mode = "add_item"
                    self.selected_index = 0
                elif selected == "Collect Revenue":
                    player_stall = self.stall_system.get_player_stall(self.current_town, self.player_name)
                    if player_stall and player_stall.total_revenue > 0:
                        revenue = player_stall.total_revenue
                        player.gold += revenue
                        player_stall.total_revenue = 0
                        self.message = f"Collected {revenue}g in revenue!"
                        self.message_timer = 180
                    else:
                        self.message = "No revenue to collect"
                        self.message_timer = 120
                elif selected == "Back":
                    self.mode = "browse"
                    self.selected_index = 0
        
        elif self.mode == "add_item":
            item_name, quantity = selected
            self.selected_item_name = item_name
            self.input_mode = "quantity"
            self.quantity_input = "1"
    
    def _process_input(self, player):
        """Process quantity/price input"""
        if self.input_mode == "quantity":
            try:
                quantity = int(self.quantity_input) if self.quantity_input else 1
                quantity = max(1, quantity)
            except ValueError:
                quantity = 1
            
            # Check if player has enough
            if self.selected_item_name not in player.inventory or player.inventory[self.selected_item_name] < quantity:
                self.message = "Not enough items!"
                self.message_timer = 120
                self.input_mode = None
                return
            
            # Move to price input
            self.input_mode = "price"
            self.price_input = "10"
        
        elif self.input_mode == "price":
            try:
                price = int(self.price_input) if self.price_input else 10
                price = max(1, price)
            except ValueError:
                price = 10
            
            quantity = int(self.quantity_input) if self.quantity_input else 1
            
            # Remove from player inventory
            player.inventory[self.selected_item_name] -= quantity
            if player.inventory[self.selected_item_name] <= 0:
                del player.inventory[self.selected_item_name]
            
            # Add to stall
            player_stall = self.stall_system.get_player_stall(self.current_town, self.player_name)
            if player_stall:
                success, message = player_stall.add_item(self.selected_item_name, quantity, price)
                self.message = message
                self.message_timer = 180
            
            self.input_mode = None
            self.quantity_input = ""
            self.price_input = ""
            self.mode = "manage"
            self.selected_index = 0
    
    def draw(self, screen, player):
        """Draw the market stall UI"""
        if not self.active:
            return
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 750
        panel_height = 600
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((self.panel_color[0], self.panel_color[1], self.panel_color[2], 240))
        pygame.draw.rect(panel, self.gold_color, (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title_text = f"Market Stalls - {self.current_town}"
        title = title_font.render(title_text, True, self.gold_color)
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Player dubloons
        info_font = pygame.font.SysFont(None, 28)
        gold_text = info_font.render(f"Your Dubloons: {player.gold}db", True, self.gold_color)
        screen.blit(gold_text, (panel_x + 20, panel_y + 80))
        
        # Content
        content_y = panel_y + 130
        self._draw_content(screen, panel_x, content_y, panel_width, player)
        
        # Instructions
        instr_y = panel_y + panel_height - 50
        instr_font = pygame.font.SysFont(None, 24)
        
        if self.input_mode:
            if self.input_mode == "quantity":
                instructions = ["Enter quantity:", "ENTER: Next", "ESC: Cancel"]
            else:
                instructions = ["Enter price per item:", "ENTER: Confirm", "ESC: Cancel"]
        else:
            instructions = ["↑↓: Select", "ENTER: Choose", "ESC: Back"]
        
        instr_x = panel_x + 20
        for instruction in instructions:
            instr = instr_font.render(instruction, True, (200, 180, 150))
            screen.blit(instr, (instr_x, instr_y))
            instr_x += 240
        
        # Message
        if self.message:
            self._draw_message(screen, panel_y + panel_height)
        
        # Input overlay
        if self.input_mode:
            self._draw_input_overlay(screen)
    
    def _draw_content(self, screen, panel_x, start_y, panel_width, player):
        """Draw content based on mode"""
        items = self._get_current_items(player)
        
        if not items:
            no_items_font = pygame.font.SysFont(None, 36)
            no_items = no_items_font.render("No items available", True, (200, 150, 100))
            screen.blit(no_items, (panel_x + panel_width // 2 - no_items.get_width() // 2, start_y + 100))
            return
        
        font = pygame.font.SysFont(None, 28)
        
        visible_count = 7
        scroll_offset = max(0, self.selected_index - visible_count + 1)
        
        for i in range(scroll_offset, min(scroll_offset + visible_count, len(items))):
            item = items[i]
            y_pos = start_y + (i - scroll_offset) * 60
            is_selected = (i == self.selected_index)
            
            # Background
            bg_color = self.selected_color if is_selected else (50, 40, 60)
            bg = pygame.Surface((panel_width - 40, 55), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                pygame.draw.rect(bg, self.gold_color, (0, 0, panel_width - 40, 55), 2)
            
            screen.blit(bg, (panel_x + 20, y_pos))
            
            # Draw item based on type
            if isinstance(item, str):
                text = font.render(item, True, self.text_color)
                screen.blit(text, (panel_x + 40, y_pos + 15))
            elif hasattr(item, 'stall_id'):
                # Stall object
                size_text = f" ({item.size.title()})" if hasattr(item, 'size') else ""
                stall_text = f"Stall #{item.stall_id + 1}{size_text} - {item.rental_cost}g/day"
                text = font.render(stall_text, True, self.text_color)
                screen.blit(text, (panel_x + 40, y_pos + 15))
            else:
                # Inventory item tuple
                item_name, quantity = item
                item_display = item_name.replace('_', ' ').title()
                text = font.render(f"{item_display} x{quantity}", True, self.text_color)
                screen.blit(text, (panel_x + 40, y_pos + 15))
    
    def _draw_message(self, screen, y_pos):
        """Draw message"""
        msg_font = pygame.font.SysFont(None, 32)
        msg_color = self.green_color if "!" in self.message and "Not enough" not in self.message else self.red_color
        msg_surf = msg_font.render(self.message, True, msg_color)
        
        msg_x = (self.screen_width - msg_surf.get_width()) // 2
        msg_y = y_pos + 20
        
        msg_bg = pygame.Surface((msg_surf.get_width() + 40, msg_surf.get_height() + 20), pygame.SRCALPHA)
        msg_bg.fill((20, 20, 20, 220))
        pygame.draw.rect(msg_bg, msg_color, (0, 0, msg_bg.get_width(), msg_bg.get_height()), 2)
        
        screen.blit(msg_bg, (msg_x - 20, msg_y - 10))
        screen.blit(msg_surf, (msg_x, msg_y))
    
    def _draw_input_overlay(self, screen):
        """Draw input overlay"""
        overlay = pygame.Surface((450, 180), pygame.SRCALPHA)
        overlay.fill((30, 20, 40, 250))
        pygame.draw.rect(overlay, self.gold_color, (0, 0, 450, 180), 3)
        
        overlay_x = (self.screen_width - 450) // 2
        overlay_y = (self.screen_height - 180) // 2
        screen.blit(overlay, (overlay_x, overlay_y))
        
        # Title
        font = pygame.font.SysFont(None, 28)
        if self.input_mode == "quantity":
            title = font.render(f"How many {self.selected_item_name}?", True, self.text_color)
            current_input = self.quantity_input
        else:
            title = font.render("Price per item (dubloons):", True, self.text_color)
            current_input = self.price_input
        
        screen.blit(title, (overlay_x + 20, overlay_y + 20))
        
        # Input box
        input_box = pygame.Surface((410, 60), pygame.SRCALPHA)
        input_box.fill((60, 50, 70))
        pygame.draw.rect(input_box, self.gold_color, (0, 0, 410, 60), 2)
        screen.blit(input_box, (overlay_x + 20, overlay_y + 70))
        
        # Input text
        input_font = pygame.font.SysFont(None, 48)
        input_text = input_font.render(current_input, True, self.gold_color)
        screen.blit(input_text, (overlay_x + 35, overlay_y + 82))


# =============================================================================
# BANK SAFETY DEPOSIT BOX UI
# =============================================================================

class SafetyDepositBoxUI:
    """UI for bank safety deposit boxes"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.current_bank = None
        self.deposit_system = None
        self.player_name = None
        
        # UI state
        self.mode = "main"  # main, rent, deposit, withdraw
        self.selected_index = 0
        self.quantity_input = ""
        self.input_mode = False
        self.message = ""
        self.message_timer = 0
        self.selected_item_name = None
        
        # Colors
        self.bg_color = (15, 10, 25)
        self.panel_color = (35, 25, 50)
        self.selected_color = (80, 60, 100)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.green_color = (100, 255, 100)
        self.red_color = (255, 100, 100)
    
    def open(self, bank_location: str, deposit_system, player):
        """Open the safety deposit box UI"""
        self.active = True
        self.current_bank = bank_location
        self.deposit_system = deposit_system
        self.player_name = player.name if hasattr(player, 'name') else "Player"
        self.mode = "main"
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        logger.info(f"[SAFETY DEPOSIT] Opened at {bank_location}")
    
    def close(self):
        """Close the UI"""
        self.active = False
        self.mode = "main"
        logger.info("[SAFETY DEPOSIT] Closed")
    
    def handle_input(self, event, player) -> str:
        """Handle input events"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            # Handle quantity input
            if self.input_mode:
                if event.key == pygame.K_RETURN:
                    self._process_quantity_input(player)
                    return None
                elif event.key == pygame.K_ESCAPE:
                    self.input_mode = False
                    self.quantity_input = ""
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    self.quantity_input = self.quantity_input[:-1]
                    return None
                elif event.unicode.isdigit() and len(self.quantity_input) < 5:
                    self.quantity_input += event.unicode
                    return None
            
            # Normal navigation
            if event.key == pygame.K_ESCAPE:
                if self.mode == "main":
                    return "close"
                else:
                    self.mode = "main"
                    self.selected_index = 0
                    self.selected_item_name = None
            
            elif event.key == pygame.K_UP:
                items = self._get_current_items(player)
                if items:
                    self.selected_index = (self.selected_index - 1) % len(items)
            
            elif event.key == pygame.K_DOWN:
                items = self._get_current_items(player)
                if items:
                    self.selected_index = (self.selected_index + 1) % len(items)
            
            elif event.key == pygame.K_RETURN:
                self._handle_selection(player)
        
        return None
    
    def _get_current_items(self, player) -> List:
        """Get items for current mode"""
        player_box = self.deposit_system.get_player_box(self.current_bank, self.player_name)
        
        if self.mode == "main":
            if player_box:
                return ["Deposit Items", "Withdraw Items", f"Box Status ({player_box.days_remaining} days left)", "Back"]
            else:
                available = self.deposit_system.get_available_boxes(self.current_bank)
                return available + ["Back"]
        
        elif self.mode == "deposit":
            # Show player inventory
            return [(name, qty) for name, qty in player.inventory.items() if qty > 0]
        
        elif self.mode == "withdraw":
            if player_box:
                return [(name, qty) for name, qty in player_box.items.items()]
            return []
        
        return []
    
    def _handle_selection(self, player):
        """Handle ENTER key selection"""
        items = self._get_current_items(player)
        if not items or self.selected_index >= len(items):
            return
        
        selected = items[self.selected_index]
        player_box = self.deposit_system.get_player_box(self.current_bank, self.player_name)
        
        if self.mode == "main":
            if isinstance(selected, str):
                if selected == "Deposit Items":
                    self.mode = "deposit"
                    self.selected_index = 0
                elif selected == "Withdraw Items":
                    self.mode = "withdraw"
                    self.selected_index = 0
                elif selected == "Back":
                    self.close()
            else:
                # Rent box
                box = selected
                days = 30  # Rent for 30 days
                total_cost = box.rental_cost * days
                
                if player.gold >= total_cost:
                    player.gold -= total_cost
                    success, message = box.rent(self.player_name, days)
                    self.message = f"{message} Cost: {total_cost}db"
                    self.message_timer = 180
                else:
                    self.message = f"Not enough dubloons! Need {total_cost}db"
                    self.message_timer = 120
        
        elif self.mode == "deposit":
            item_name, quantity = selected
            self.selected_item_name = item_name
            self.input_mode = True
            self.quantity_input = "1"
        
        elif self.mode == "withdraw":
            item_name, quantity = selected
            self.selected_item_name = item_name
            self.input_mode = True
            self.quantity_input = "1"
    
    def _process_quantity_input(self, player):
        """Process quantity input"""
        try:
            quantity = int(self.quantity_input) if self.quantity_input else 1
            quantity = max(1, quantity)
        except ValueError:
            quantity = 1
        
        self.input_mode = False
        self.quantity_input = ""
        
        player_box = self.deposit_system.get_player_box(self.current_bank, self.player_name)
        if not player_box:
            self.message = "No box rented!"
            self.message_timer = 120
            return
        
        if self.mode == "deposit":
            # Check if player has enough
            if self.selected_item_name not in player.inventory or player.inventory[self.selected_item_name] < quantity:
                self.message = "Not enough items!"
                self.message_timer = 120
                return
            
            # Remove from player
            player.inventory[self.selected_item_name] -= quantity
            if player.inventory[self.selected_item_name] <= 0:
                del player.inventory[self.selected_item_name]
            
            # Add to box
            success, message = player_box.deposit_item(self.selected_item_name, quantity)
            self.message = message
            self.message_timer = 180
        
        elif self.mode == "withdraw":
            # Withdraw from box
            success, message, withdrawn = player_box.withdraw_item(self.selected_item_name, quantity)
            
            if success:
                # Add to player inventory
                player.inventory[self.selected_item_name] = player.inventory.get(self.selected_item_name, 0) + withdrawn
            
            self.message = message
            self.message_timer = 180
    
    def draw(self, screen, player):
        """Draw the safety deposit box UI"""
        if not self.active:
            return
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 700
        panel_height = 550
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((self.panel_color[0], self.panel_color[1], self.panel_color[2], 240))
        pygame.draw.rect(panel, self.gold_color, (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        if self.mode == "main":
            title_text = "Safety Deposit Boxes"
        elif self.mode == "deposit":
            title_text = "Deposit Items"
        else:
            title_text = "Withdraw Items"
        
        title = title_font.render(title_text, True, self.gold_color)
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Player dubloons
        info_font = pygame.font.SysFont(None, 28)
        gold_text = info_font.render(f"Your Dubloons: {player.gold}db", True, self.gold_color)
        screen.blit(gold_text, (panel_x + 20, panel_y + 80))
        
        # Content
        content_y = panel_y + 130
        self._draw_content(screen, panel_x, content_y, panel_width, player)
        
        # Instructions
        instr_y = panel_y + panel_height - 50
        instr_font = pygame.font.SysFont(None, 24)
        
        if self.input_mode:
            instructions = ["Enter quantity:", "ENTER: Confirm", "ESC: Cancel"]
        else:
            instructions = ["↑↓: Select", "ENTER: Choose", "ESC: Back"]
        
        instr_x = panel_x + 20
        for instruction in instructions:
            instr = instr_font.render(instruction, True, (200, 180, 150))
            screen.blit(instr, (instr_x, instr_y))
            instr_x += 220
        
        # Message
        if self.message:
            self._draw_message(screen, panel_y + panel_height)
        
        # Input overlay
        if self.input_mode:
            self._draw_input_overlay(screen)
    
    def _draw_content(self, screen, panel_x, start_y, panel_width, player):
        """Draw content based on mode"""
        items = self._get_current_items(player)
        
        if not items:
            no_items_font = pygame.font.SysFont(None, 36)
            if self.mode == "deposit":
                text = "No items in inventory"
            elif self.mode == "withdraw":
                text = "No items in box"
            else:
                text = "No boxes available"
            
            no_items = no_items_font.render(text, True, (200, 150, 100))
            screen.blit(no_items, (panel_x + panel_width // 2 - no_items.get_width() // 2, start_y + 100))
            return
        
        font = pygame.font.SysFont(None, 28)
        small_font = pygame.font.SysFont(None, 22)
        
        visible_count = 6
        scroll_offset = max(0, self.selected_index - visible_count + 1)
        
        for i in range(scroll_offset, min(scroll_offset + visible_count, len(items))):
            item = items[i]
            y_pos = start_y + (i - scroll_offset) * 65
            is_selected = (i == self.selected_index)
            
            # Background
            bg_color = self.selected_color if is_selected else (50, 40, 60)
            bg = pygame.Surface((panel_width - 40, 60), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                pygame.draw.rect(bg, self.gold_color, (0, 0, panel_width - 40, 60), 2)
            
            screen.blit(bg, (panel_x + 20, y_pos))
            
            # Draw item based on type
            if isinstance(item, str):
                text = font.render(item, True, self.text_color)
                screen.blit(text, (panel_x + 40, y_pos + 18))
            elif hasattr(item, 'box_id'):
                # Box object
                box_text = f"{item.size.title()} Box (#{item.box_id + 1}) - {item.slots} slots"
                text = font.render(box_text, True, self.text_color)
                screen.blit(text, (panel_x + 40, y_pos + 10))
                
                cost_text = f"Rent: {item.rental_cost}g for 30 days"
                cost = small_font.render(cost_text, True, (180, 180, 180))
                screen.blit(cost, (panel_x + 40, y_pos + 35))
            else:
                # Item tuple
                item_name, quantity = item
                item_display = item_name.replace('_', ' ').title()
                text = font.render(f"{item_display} x{quantity}", True, self.text_color)
                screen.blit(text, (panel_x + 40, y_pos + 18))
    
    def _draw_message(self, screen, y_pos):
        """Draw message"""
        msg_font = pygame.font.SysFont(None, 32)
        msg_color = self.green_color if "!" in self.message and "Not enough" not in self.message else self.red_color
        msg_surf = msg_font.render(self.message, True, msg_color)
        
        msg_x = (self.screen_width - msg_surf.get_width()) // 2
        msg_y = y_pos + 20
        
        msg_bg = pygame.Surface((msg_surf.get_width() + 40, msg_surf.get_height() + 20), pygame.SRCALPHA)
        msg_bg.fill((20, 20, 20, 220))
        pygame.draw.rect(msg_bg, msg_color, (0, 0, msg_bg.get_width(), msg_bg.get_height()), 2)
        
        screen.blit(msg_bg, (msg_x - 20, msg_y - 10))
        screen.blit(msg_surf, (msg_x, msg_y))
    
    def _draw_input_overlay(self, screen):
        """Draw input overlay"""
        overlay = pygame.Surface((400, 150), pygame.SRCALPHA)
        overlay.fill((30, 20, 40, 250))
        pygame.draw.rect(overlay, self.gold_color, (0, 0, 400, 150), 3)
        
        overlay_x = (self.screen_width - 400) // 2
        overlay_y = (self.screen_height - 150) // 2
        screen.blit(overlay, (overlay_x, overlay_y))
        
        # Title
        font = pygame.font.SysFont(None, 32)
        title = font.render("Enter Quantity:", True, self.text_color)
        screen.blit(title, (overlay_x + 20, overlay_y + 20))
        
        # Input box
        input_box = pygame.Surface((360, 50), pygame.SRCALPHA)
        input_box.fill((60, 50, 70))
        pygame.draw.rect(input_box, self.gold_color, (0, 0, 360, 50), 2)
        screen.blit(input_box, (overlay_x + 20, overlay_y + 70))
        
        # Input text
        input_font = pygame.font.SysFont(None, 40)
        input_text = input_font.render(self.quantity_input, True, self.gold_color)
        screen.blit(input_text, (overlay_x + 30, overlay_y + 80))
