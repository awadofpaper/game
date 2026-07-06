"""
Bartering UI - Item-for-item trading interface
Allows players to trade items directly with merchants without using gold
"""

import pygame
from typing import Optional, List, Tuple


class BarteringUI:
    """Visual interface for bartering (item-for-item trading)"""
    
    # UI states
    STATE_SELECTING_OFFER = "selecting_offer"  # Selecting items to offer from player inventory
    STATE_SELECTING_REQUEST = "selecting_request"  # Selecting items to request from merchant
    STATE_CONFIRM = "confirm"  # Reviewing and confirming trade
    
    def __init__(self):
        self.active = False
        self.state = self.STATE_SELECTING_OFFER
        
        # System references
        self.bartering_system = None
        self.reputation_manager = None
        self.player = None
        self.shop = None
        self.merchant_id = None
        self.merchant_name = None
        
        # Selection state
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible = 6
        
        # Barter items (local tracking for UI)
        self.player_offer = []  # List of (item_id, name, quantity, value)
        self.merchant_request = []  # List of (item_id, name, quantity, value)
        
        # Quantity input
        self.quantity_input = ""
        self.entering_quantity = False
        self.current_item_for_quantity = None
        
        # Message display
        self.message = ""
        self.message_timer = 0
        self.message_color = (255, 255, 255)
        
        # Colors
        self.bg_color = (20, 15, 30)
        self.panel_color = (45, 35, 60)
        self.header_color = (65, 50, 85)
        self.selected_color = (90, 70, 120)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.green_color = (100, 255, 100)
        self.red_color = (255, 100, 100)
        self.gray_color = (150, 150, 150)
        self.accent_color = (180, 140, 220)
        self.offer_color = (100, 150, 255)  # Blue for player offers
        self.request_color = (255, 150, 100)  # Orange for merchant requests
        
    def open(self, bartering_system, reputation_manager, player, shop, merchant_id, merchant_name):
        """Open the bartering interface"""
        self.active = True
        self.bartering_system = bartering_system
        self.reputation_manager = reputation_manager
        self.player = player
        self.shop = shop
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name
        
        # Reset state
        self.state = self.STATE_SELECTING_OFFER
        self.selected_index = 0
        self.scroll_offset = 0
        self.player_offer = []
        self.merchant_request = []
        self.quantity_input = ""
        self.entering_quantity = False
        self.current_item_for_quantity = None
        
        # Start bartering session
        self.bartering_system.start_barter(merchant_id, merchant_name, shop)
        
        self._show_message(f"Bartering with {merchant_name} - Select items to offer", self.accent_color)
        
    def close(self):
        """Close the bartering interface"""
        self.active = False
        self.player_offer = []
        self.merchant_request = []
        
    def update(self):
        """Update timers"""
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
                
    def _show_message(self, message: str, color=(255, 255, 255), duration=180):
        """Display a message"""
        self.message = message
        self.message_color = color
        self.message_timer = duration
        
    def _get_player_inventory_items(self) -> List[Tuple[str, str, int, int]]:
        """Get player's inventory as list of (item_id, name, quantity, value)"""
        items = []
        if not hasattr(self.player, 'inventory'):
            return items
            
        for item_id, quantity in self.player.inventory.items():
            if quantity <= 0:
                continue
                
            # Find item in shop to get name and value
            item_name = item_id
            item_value = 10  # Default value
            
            for shop_item in self.shop.inventory:
                if shop_item.item_id == item_id:
                    item_name = shop_item.name
                    item_value = shop_item.sell_price  # Use sell price as value
                    break
                    
            items.append((item_id, item_name, quantity, item_value))
            
        return items
        
    def _get_merchant_inventory_items(self) -> List[Tuple[str, str, int, int]]:
        """Get merchant's inventory as list of (item_id, name, quantity, value)"""
        items = []
        
        for shop_item in self.shop.inventory:
            if shop_item.stock <= 0:
                continue
                
            items.append((
                shop_item.item_id,
                shop_item.name,
                shop_item.stock,
                shop_item.buy_price  # Use buy price as value
            ))
            
        return items
        
    def _calculate_totals(self) -> Tuple[int, int]:
        """Calculate total values of player offer and merchant request"""
        player_total = sum(value * qty for _, _, qty, value in self.player_offer)
        merchant_total = sum(value * qty for _, _, qty, value in self.merchant_request)
        return player_total, merchant_total
        
    def _calculate_fairness(self) -> Tuple[float, str, float]:
        """Calculate fairness ratio and required threshold"""
        player_total, merchant_total = self._calculate_totals()
        
        if merchant_total == 0:
            return 0.0, "Merchant offers nothing", 0.85
            
        fairness = player_total / merchant_total
        
        # Get required fairness based on reputation
        min_fairness = 0.85
        if self.reputation_manager:
            rep = self.reputation_manager.get_or_create_reputation(
                self.merchant_id, self.merchant_name
            )
            tier = rep.get_current_tier()
            tier_index = next((i for i, t in enumerate(rep.TIERS) if t.name == tier.name), 2)
            min_fairness = max(0.70, 0.85 - (tier_index * 0.03))
        
        # Description
        if fairness >= 1.2:
            desc = "Very favorable for merchant"
        elif fairness >= 1.05:
            desc = "Slightly favorable for merchant"
        elif fairness >= 0.95:
            desc = "Fair trade"
        elif fairness >= 0.8:
            desc = "Slightly favorable for you"
        else:
            desc = "Very favorable for you"
            
        return fairness, desc, min_fairness
        
    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.active:
            return None
            
        if event.type == pygame.KEYDOWN:
            # Quantity input mode
            if self.entering_quantity:
                if event.key == pygame.K_RETURN:
                    self._confirm_quantity_input()
                elif event.key == pygame.K_ESCAPE:
                    self.entering_quantity = False
                    self.quantity_input = ""
                    self.current_item_for_quantity = None
                elif event.key == pygame.K_BACKSPACE:
                    self.quantity_input = self.quantity_input[:-1]
                elif event.unicode.isdigit():
                    self.quantity_input += event.unicode
                return None
                
            # Normal navigation
            if event.key == pygame.K_ESCAPE:
                if self.state == self.STATE_CONFIRM:
                    self.state = self.STATE_SELECTING_REQUEST
                    self._show_message("Continue selecting items", self.accent_color)
                elif self.state == self.STATE_SELECTING_REQUEST:
                    self.state = self.STATE_SELECTING_OFFER
                    self._show_message("Select items to offer", self.offer_color)
                else:
                    return "close"
                    
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                self._adjust_scroll()
                
            elif event.key == pygame.K_DOWN:
                max_index = self._get_max_index()
                self.selected_index = min(max_index, self.selected_index + 1)
                self._adjust_scroll()
                
            elif event.key == pygame.K_RETURN:
                self._handle_selection()
                
            elif event.key == pygame.K_TAB:
                # Switch between offer and request states
                if self.state == self.STATE_SELECTING_OFFER:
                    self.state = self.STATE_SELECTING_REQUEST
                    self.selected_index = 0
                    self.scroll_offset = 0
                    self._show_message("Select items to request from merchant", self.request_color)
                elif self.state == self.STATE_SELECTING_REQUEST:
                    self.state = self.STATE_SELECTING_OFFER
                    self.selected_index = 0
                    self.scroll_offset = 0
                    self._show_message("Select items to offer", self.offer_color)
                    
            elif event.key == pygame.K_SPACE:
                # Go to confirm state
                if len(self.player_offer) > 0 and len(self.merchant_request) > 0:
                    self.state = self.STATE_CONFIRM
                    self._show_message("Review trade and press ENTER to confirm", self.green_color)
                else:
                    self._show_message("Add items to both sides of the trade!", self.red_color)
                    
            elif event.key == pygame.K_c:
                # Clear current list
                if self.state == self.STATE_SELECTING_OFFER:
                    self.player_offer = []
                    self._show_message("Cleared your offer", self.gray_color)
                elif self.state == self.STATE_SELECTING_REQUEST:
                    self.merchant_request = []
                    self._show_message("Cleared your request", self.gray_color)
                    
        return None
        
    def _get_max_index(self):
        """Get maximum index for current state"""
        if self.state == self.STATE_SELECTING_OFFER:
            items = self._get_player_inventory_items()
            return max(0, len(items) - 1)
        elif self.state == self.STATE_SELECTING_REQUEST:
            items = self._get_merchant_inventory_items()
            return max(0, len(items) - 1)
        else:  # CONFIRM
            return 0
            
    def _adjust_scroll(self):
        """Adjust scroll to keep selection visible"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible:
            self.scroll_offset = self.selected_index - self.max_visible + 1
            
    def _handle_selection(self):
        """Handle Enter key selection"""
        if self.state == self.STATE_CONFIRM:
            # Attempt the barter
            self._attempt_trade()
            
        elif self.state == self.STATE_SELECTING_OFFER:
            items = self._get_player_inventory_items()
            if 0 <= self.selected_index < len(items):
                item = items[self.selected_index]
                self.current_item_for_quantity = item
                self.entering_quantity = True
                self.quantity_input = ""
                self._show_message(f"Enter quantity for {item[1]} (max {item[2]})", self.offer_color)
                
        elif self.state == self.STATE_SELECTING_REQUEST:
            items = self._get_merchant_inventory_items()
            if 0 <= self.selected_index < len(items):
                item = items[self.selected_index]
                self.current_item_for_quantity = item
                self.entering_quantity = True
                self.quantity_input = ""
                self._show_message(f"Enter quantity for {item[1]} (max {item[2]})", self.request_color)
                
    def _confirm_quantity_input(self):
        """Confirm quantity input and add item to offer/request"""
        if not self.quantity_input or not self.current_item_for_quantity:
            self.entering_quantity = False
            return
            
        try:
            quantity = int(self.quantity_input)
            item_id, name, max_qty, value = self.current_item_for_quantity
            
            if quantity <= 0 or quantity > max_qty:
                self._show_message(f"Invalid quantity! (1-{max_qty})", self.red_color)
                self.entering_quantity = False
                self.quantity_input = ""
                return
                
            if self.state == self.STATE_SELECTING_OFFER:
                # Add to player offer
                self.player_offer.append((item_id, name, quantity, value))
                self._show_message(f"Added {quantity}x {name} to your offer", self.offer_color)
            elif self.state == self.STATE_SELECTING_REQUEST:
                # Add to merchant request
                self.merchant_request.append((item_id, name, quantity, value))
                self._show_message(f"Added {quantity}x {name} to your request", self.request_color)
                
        except ValueError:
            self._show_message("Invalid number!", self.red_color)
            
        self.entering_quantity = False
        self.quantity_input = ""
        self.current_item_for_quantity = None
        
    def _attempt_trade(self):
        """Attempt to complete the barter trade"""
        # Sync with bartering system
        self.bartering_system.active_barter['player_items'] = [
            (item_id, qty, value) for item_id, _, qty, value in self.player_offer
        ]
        self.bartering_system.active_barter['merchant_items'] = [
            (item_id, qty, value) for item_id, _, qty, value in self.merchant_request
        ]
        
        # Attempt trade
        success, message = self.bartering_system.attempt_barter(
            self.player, self.reputation_manager
        )
        
        if success:
            self._show_message(message, self.green_color, 240)
            # Clear trade
            self.player_offer = []
            self.merchant_request = []
            self.state = self.STATE_SELECTING_OFFER
        else:
            self._show_message(message, self.red_color, 240)
            
    def draw(self, screen):
        """Draw the bartering interface"""
        if not self.active:
            return
            
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill(self.bg_color)
        overlay.set_alpha(220)
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 1000
        panel_height = 700
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, self.panel_color,
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, self.accent_color,
                        (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title
        font_large = pygame.font.Font(None, 44)
        title_text = f"Bartering with {self.merchant_name}"
        title_surf = font_large.render(title_text, True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=panel_x + panel_width // 2, top=panel_y + 15)
        screen.blit(title_surf, title_rect)
        
        # Draw based on state
        if self.state == self.STATE_CONFIRM:
            self._draw_confirm_view(screen, panel_x, panel_y, panel_width, panel_height)
        else:
            self._draw_trading_view(screen, panel_x, panel_y, panel_width, panel_height)
            
        # Message
        if self.message:
            self._draw_message(screen, screen_width, screen_height)
            
        # Quantity input overlay
        if self.entering_quantity:
            self._draw_quantity_input(screen, screen_width, screen_height)
            
    def _draw_trading_view(self, screen, panel_x, panel_y, panel_width, panel_height):
        """Draw the main trading view with two columns"""
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 22)
        
        # Split into two columns
        col_width = (panel_width - 60) // 2
        left_x = panel_x + 20
        right_x = panel_x + panel_width // 2 + 10
        list_y = panel_y + 70
        
        # Left column: Player's offer
        self._draw_column(screen, left_x, list_y, col_width, 400,
                         "Your Offer", self.offer_color,
                         self._get_player_inventory_items(),
                         self.player_offer,
                         self.state == self.STATE_SELECTING_OFFER)
        
        # Right column: Merchant's request
        self._draw_column(screen, right_x, list_y, col_width, 400,
                         "You Request", self.request_color,
                         self._get_merchant_inventory_items(),
                         self.merchant_request,
                         self.state == self.STATE_SELECTING_REQUEST)
        
        # Center divider
        divider_x = panel_x + panel_width // 2
        pygame.draw.line(screen, self.accent_color,
                        (divider_x, panel_y + 60), (divider_x, panel_y + 500), 2)
        
        # Fairness display at bottom
        fairness_y = panel_y + 510
        self._draw_fairness_display(screen, panel_x, fairness_y, panel_width)
        
        # Controls at bottom
        controls_y = panel_y + panel_height - 50
        controls_font = pygame.font.Font(None, 20)
        if self.state == self.STATE_SELECTING_OFFER:
            controls_text = "↑↓: Navigate  ENTER: Add Item  TAB: Switch to Request  C: Clear Offer  SPACE: Review  ESC: Close"
        else:
            controls_text = "↑↓: Navigate  ENTER: Add Item  TAB: Switch to Offer  C: Clear Request  SPACE: Review  ESC: Back"
        controls_surf = controls_font.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=panel_x + panel_width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_column(self, screen, x, y, width, height, title, title_color, 
                     available_items, selected_items, is_active):
        """Draw a single column (offer or request)"""
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        
        # Header
        header_rect = pygame.Rect(x, y, width, 35)
        pygame.draw.rect(screen, self.header_color, header_rect)
        pygame.draw.rect(screen, title_color, header_rect, 2)
        
        title_surf = font_medium.render(title, True, title_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, centery=y + 17)
        screen.blit(title_surf, title_rect)
        
        # Available items list
        list_y = y + 45
        for i, (item_id, name, quantity, value) in enumerate(available_items):
            if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible:
                continue
                
            item_y = list_y + (i - self.scroll_offset) * 55
            is_selected = is_active and i == self.selected_index
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 5, item_y, width - 10, 50)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, title_color, highlight_rect, 2)
            
            # Item name
            name_surf = font_small.render(name, True, self.text_color)
            screen.blit(name_surf, (x + 10, item_y + 5))
            
            # Quantity and value
            info_text = f"Qty: {quantity}  |  Value: {value}g each"
            info_surf = font_small.render(info_text, True, self.gray_color)
            screen.blit(info_surf, (x + 10, item_y + 28))
        
        # Selected items summary
        summary_y = y + height - 100
        summary_rect = pygame.Rect(x, summary_y, width, 100)
        pygame.draw.rect(screen, self.header_color, summary_rect)
        pygame.draw.rect(screen, title_color, summary_rect, 2)
        
        summary_title = font_small.render("Selected:", True, title_color)
        screen.blit(summary_title, (x + 10, summary_y + 5))
        
        if not selected_items:
            none_surf = font_small.render("(none)", True, self.gray_color)
            screen.blit(none_surf, (x + 10, summary_y + 30))
        else:
            item_y_offset = 28
            for item_id, name, quantity, value in selected_items[:3]:  # Show first 3
                item_text = f"{quantity}x {name} ({value * quantity}g)"
                item_surf = font_small.render(item_text, True, self.text_color)
                screen.blit(item_surf, (x + 10, summary_y + item_y_offset))
                item_y_offset += 22
                
            if len(selected_items) > 3:
                more_text = f"... and {len(selected_items) - 3} more"
                more_surf = font_small.render(more_text, True, self.gray_color)
                screen.blit(more_surf, (x + 10, summary_y + item_y_offset))
                
    def _draw_fairness_display(self, screen, panel_x, y, panel_width):
        """Draw fairness calculation display"""
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 22)
        
        player_total, merchant_total = self._calculate_totals()
        fairness, description, min_fairness = self._calculate_fairness()
        
        # Background
        fairness_rect = pygame.Rect(panel_x + 20, y, panel_width - 40, 110)
        pygame.draw.rect(screen, self.header_color, fairness_rect)
        pygame.draw.rect(screen, self.accent_color, fairness_rect, 2)
        
        # Title
        title_surf = font_medium.render("Trade Fairness", True, self.gold_color)
        screen.blit(title_surf, (panel_x + 40, y + 10))
        
        # Totals
        offer_text = f"Your Offer: {player_total}g"
        offer_surf = font_small.render(offer_text, True, self.offer_color)
        screen.blit(offer_surf, (panel_x + 40, y + 40))
        
        request_text = f"You Request: {merchant_total}g"
        request_surf = font_small.render(request_text, True, self.request_color)
        screen.blit(request_surf, (panel_x + 40, y + 65))
        
        # Fairness ratio
        if merchant_total > 0:
            fairness_text = f"Fairness: {fairness:.2f} ({description})"
            
            # Color based on acceptability
            if fairness >= min_fairness:
                fairness_color = self.green_color
            else:
                fairness_color = self.red_color
                
            fairness_surf = font_medium.render(fairness_text, True, fairness_color)
            screen.blit(fairness_surf, (panel_x + 300, y + 45))
            
            # Required threshold
            threshold_text = f"Required: {min_fairness:.2f}"
            threshold_surf = font_small.render(threshold_text, True, self.gray_color)
            screen.blit(threshold_surf, (panel_x + 300, y + 75))
        
    def _draw_confirm_view(self, screen, panel_x, panel_y, panel_width, panel_height):
        """Draw confirmation view"""
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        content_y = panel_y + 80
        
        # Title
        confirm_title = font_large.render("Confirm Trade", True, self.gold_color)
        confirm_rect = confirm_title.get_rect(centerx=panel_x + panel_width // 2, top=content_y)
        screen.blit(confirm_title, confirm_rect)
        
        # Your offer
        offer_y = content_y + 60
        offer_title = font_medium.render("You Give:", True, self.offer_color)
        screen.blit(offer_title, (panel_x + 50, offer_y))
        
        item_y = offer_y + 35
        for item_id, name, quantity, value in self.player_offer:
            item_text = f"• {quantity}x {name} ({value * quantity}g value)"
            item_surf = font_small.render(item_text, True, self.text_color)
            screen.blit(item_surf, (panel_x + 70, item_y))
            item_y += 28
            
        # Merchant offer
        request_y = content_y + 280
        request_title = font_medium.render("You Receive:", True, self.request_color)
        screen.blit(request_title, (panel_x + 50, request_y))
        
        item_y = request_y + 35
        for item_id, name, quantity, value in self.merchant_request:
            item_text = f"• {quantity}x {name} ({value * quantity}g value)"
            item_surf = font_small.render(item_text, True, self.text_color)
            screen.blit(item_surf, (panel_x + 70, item_y))
            item_y += 28
            
        # Fairness
        fairness_y = content_y + 480
        self._draw_fairness_display(screen, panel_x, fairness_y, panel_width)
        
        # Controls
        controls_y = panel_y + panel_height - 50
        controls_font = pygame.font.Font(None, 24)
        controls_text = "ENTER: Confirm Trade  ESC: Go Back"
        controls_surf = controls_font.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=panel_x + panel_width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_quantity_input(self, screen, screen_width, screen_height):
        """Draw quantity input overlay"""
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # Input box
        box_width = 400
        box_height = 120
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2
        
        pygame.draw.rect(screen, self.panel_color, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, self.gold_color, (box_x, box_y, box_width, box_height), 3)
        
        # Prompt
        if self.current_item_for_quantity:
            item_id, name, max_qty, value = self.current_item_for_quantity
            prompt_text = f"Quantity for {name}"
            prompt_surf = font_small.render(prompt_text, True, self.text_color)
            prompt_rect = prompt_surf.get_rect(centerx=box_x + box_width // 2, top=box_y + 15)
            screen.blit(prompt_surf, prompt_rect)
            
            max_text = f"(max: {max_qty})"
            max_surf = font_small.render(max_text, True, self.gray_color)
            max_rect = max_surf.get_rect(centerx=box_x + box_width // 2, top=box_y + 40)
            screen.blit(max_surf, max_rect)
        
        # Input field
        input_rect = pygame.Rect(box_x + 50, box_y + 70, box_width - 100, 35)
        pygame.draw.rect(screen, self.header_color, input_rect)
        pygame.draw.rect(screen, self.accent_color, input_rect, 2)
        
        input_text = self.quantity_input or ""
        input_surf = font_medium.render(input_text, True, self.text_color)
        screen.blit(input_surf, (box_x + 60, box_y + 75))
        
    def _draw_message(self, screen, screen_width, screen_height):
        """Draw message overlay"""
        font = pygame.font.Font(None, 28)
        
        # Message background
        msg_surf = font.render(self.message, True, self.message_color)
        msg_width = msg_surf.get_width() + 40
        msg_height = 50
        msg_x = (screen_width - msg_width) // 2
        msg_y = screen_height - 100
        
        pygame.draw.rect(screen, self.panel_color, (msg_x, msg_y, msg_width, msg_height))
        pygame.draw.rect(screen, self.message_color, (msg_x, msg_y, msg_width, msg_height), 2)
        
        msg_rect = msg_surf.get_rect(center=(screen_width // 2, msg_y + msg_height // 2))
        screen.blit(msg_surf, msg_rect)
