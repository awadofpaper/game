"""
Shop UI - Visual interface for buying and selling items
"""

import pygame
from shop_system import ShopItem
from haggling_ui import HagglingUI

class ShopUI:
    """Visual interface for merchant shops"""
    
    def __init__(self):
        self.active = False
        self.current_shop = None
        self.current_merchant_id = None
        self.player = None
        
        # System references (set by main.py)
        self.shop_manager = None
        self.embargo_system = None
        self.town_treasury_system = None
        
        # Haggling UI
        self.haggling_ui = HagglingUI()
        self.haggling_active = False
        self.negotiated_price = None
        
        # UI state
        self.mode = "buy"  # "buy" or "sell"
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_items = 8
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.panel_color = (50, 50, 60)
        self.selected_color = (80, 120, 180)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.can_afford_color = (100, 255, 100)
        self.cannot_afford_color = (255, 100, 100)
        
        # Message display
        self.message = ""
        self.message_timer = 0
        self.message_duration = 120  # frames
    
    def open(self, shop, merchant_id, player):
        """Open the shop UI"""
        self.active = True
        self.current_shop = shop
        self.current_merchant_id = merchant_id
        self.player = player
        self.mode = "buy"
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = ""
    
    def close(self):
        """Close the shop UI"""
        self.active = False
        self.current_shop = None
        self.current_merchant_id = None
        self.player = None
    
    def toggle_mode(self):
        """Switch between buy and sell modes"""
        self.mode = "sell" if self.mode == "buy" else "buy"
        self.selected_index = 0
        self.scroll_offset = 0
    
    def get_display_items(self):
        """Get items to display based on current mode"""
        if self.mode == "buy":
            # Show shop inventory
            return self.current_shop.inventory
        else:
            # Show player inventory (items that can be sold)
            if not hasattr(self.player, 'inventory'):
                return []
            
            # Convert player's dict inventory to list of shop items for selling
            sellable_items = []
            for item_id, quantity in self.player.inventory.items():
                # Find matching shop item to get price
                for shop_item in self.current_shop.inventory:
                    if shop_item.item_id == item_id and quantity > 0:
                        # Create temporary item with quantity info
                        temp_item = ShopItem(
                            item_id, shop_item.name, shop_item.category,
                            shop_item.buy_price, shop_item.sell_price,
                            quantity, shop_item.description, shop_item.stats
                        )
                        sellable_items.append(temp_item)
                        break
            return sellable_items
    
    def handle_input(self, event):
        """Handle keyboard input"""
        # Handle haggling UI if active
        if self.haggling_active:
            result = self.haggling_ui.handle_input(event)
            if result == "close":
                # Haggling finished
                success, final_price = self.haggling_ui.close()
                self.haggling_active = False
                
                if success:
                    # Use negotiated price
                    self.negotiated_price = final_price
                    # Get the item and execute purchase with negotiated price
                    items = self.get_display_items()
                    if 0 <= self.selected_index < len(items):
                        self._execute_transaction(items[self.selected_index], override_price=final_price)
                    self.negotiated_price = None
            return None
        
        if event.type == pygame.KEYDOWN:
            items = self.get_display_items()
            
            if event.key == pygame.K_ESCAPE:
                self.close()
                return "closed"
            
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                # Scroll up if needed
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = self.selected_index
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(items) - 1, self.selected_index + 1)
                # Scroll down if needed
                if self.selected_index >= self.scroll_offset + self.max_visible_items:
                    self.scroll_offset = self.selected_index - self.max_visible_items + 1
            
            elif event.key == pygame.K_TAB:
                # Switch between buy/sell modes
                self.toggle_mode()
            
            elif event.key == pygame.K_h or event.key == pygame.K_h:
                # Start haggling
                if self.mode == "buy" and 0 <= self.selected_index < len(items):
                    item = items[self.selected_index]
                    if item.has_stock():
                        self._start_haggling(item)
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Purchase/sell selected item
                if 0 <= self.selected_index < len(items):
                    self._execute_transaction(items[self.selected_index])
        
        return None
    
    def _start_haggling(self, item):
        """Start haggling for an item"""
        # Get base price with reputation discount
        base_price = item.buy_price
        if self.current_shop.reputation_manager and self.current_shop.shop_id:
            rep = self.current_shop.reputation_manager.get_or_create_reputation(
                self.current_shop.shop_id,
                self.current_shop.merchant_name
            )
            discount_mult = rep.get_discount_multiplier()
            base_price = int(base_price * discount_mult)
        
        # Apply price events and loyalty
        if self.current_shop.price_event_manager and self.current_shop.town_name and hasattr(item, 'category'):
            event_modifier = self.current_shop.price_event_manager.get_price_modifier(item.category, self.current_shop.town_name)
            base_price = int(base_price * event_modifier)
        
        if self.current_shop.merchant_quest_manager and self.current_shop.shop_id:
            loyalty_discount = self.current_shop.merchant_quest_manager.get_loyalty_discount(self.current_shop.shop_id)
            base_price = int(base_price * (1.0 - loyalty_discount))
        
        # Open haggling UI
        self.haggling_ui.open(
            self.current_shop.haggling_system,
            self.current_shop.reputation_manager,
            self.player,
            self.current_shop.shop_id,
            self.current_shop.merchant_name,
            item,
            base_price,
            is_buying=True
        )
        self.haggling_active = True
    
    def _execute_transaction(self, item, override_price=None):
        """Execute buy or sell transaction"""
        if self.mode == "buy":
            # Buy item from merchant
            if override_price is not None:
                # Use haggled price - manually execute transaction
                if not item.has_stock():
                    self.message = "Out of stock!"
                    self.message_timer = self.message_duration
                    return
                
                if self.player.dubloons < override_price:
                    self.message = f"Not enough dubloons! Need {override_price}"
                    self.message_timer = self.message_duration
                    return
                
                # Deduct gold
                self.player.dubloons -= override_price
                
                # Decrease stock
                item.purchase()
                
                # Add to inventory
                if not hasattr(self.player, 'inventory'):
                    self.player.inventory = {}
                self.player.inventory[item.item_id] = self.player.inventory.get(item.item_id, 0) + 1
                
                # Record for reputation (using haggled price)
                if self.current_shop.reputation_manager and self.current_shop.shop_id:
                    self.current_shop.reputation_manager.record_purchase(
                        self.current_shop.shop_id,
                        self.current_shop.merchant_name,
                        override_price
                    )
                
                # Record for demand
                if self.current_shop.dynamic_inventory_manager and self.current_shop.shop_id:
                    self.current_shop.dynamic_inventory_manager.record_sale(
                        self.current_shop.shop_id,
                        item.item_id,
                        1
                    )
                
                # Record for loyalty
                if self.current_shop.merchant_quest_manager and self.current_shop.shop_id:
                    self.current_shop.merchant_quest_manager.record_purchase(
                        self.current_shop.shop_id,
                        override_price
                    )
                
                self.message = f"Purchased {item.name} for {override_price} gold! (Haggled)"
                self.message_timer = self.message_duration
            else:
                # Normal purchase
                success, message = self.current_shop.buy_item(item, self.player)
                self.message = message
                self.message_timer = self.message_duration
        else:
            # Sell item to merchant with embargo fee support
            town_name = None
            if self.shop_manager and self.current_merchant_id:
                shop_data = self.shop_manager.shops.get(self.current_merchant_id)
                if shop_data:
                    town_name = shop_data.get('town_name')
            
            success, message = self.current_shop.sell_item_to_merchant(
                item.item_id, 
                self.player,
                embargo_system=self.embargo_system,
                town_treasury_system=self.town_treasury_system,
                town_name=town_name
            )
            self.message = message
            self.message_timer = self.message_duration
    
    def update(self):
        """Update UI timers"""
        if self.message_timer > 0:
            self.message_timer -= 1
        
        if self.haggling_active:
            self.haggling_ui.update()
    
    def draw(self, screen, font):
        """Draw the shop UI"""
        if not self.active or not self.current_shop:
            return
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Main shop panel
        panel_width = 700
        panel_height = 550
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, self.bg_color, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, self.text_color, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Header
        header_font = pygame.font.SysFont(None, 36)
        header_text = f"{self.current_shop.merchant_name}'s Shop"
        header_surf = header_font.render(header_text, True, self.gold_color)
        screen.blit(header_surf, (panel_x + 20, panel_y + 15))
        
        # Reputation display (if reputation manager available)
        if self.current_shop.reputation_manager and self.current_shop.shop_id:
            rep = self.current_shop.reputation_manager.get_or_create_reputation(
                self.current_shop.shop_id, 
                self.current_shop.merchant_name
            )
            tier = rep.get_current_tier()
            
            # Display reputation tier
            rep_font = pygame.font.SysFont(None, 22)
            tier_text = f"Reputation: {tier.name} ({rep.reputation} points)"
            tier_surf = rep_font.render(tier_text, True, (150, 200, 255))
            screen.blit(tier_surf, (panel_x + 20, panel_y + 45))
            
            # Display discount/markup
            discount_percent = int(tier.discount * 100)
            if discount_percent > 0:
                discount_text = f"✓ {discount_percent}% discount on purchases"
                discount_color = (100, 255, 100)
            elif discount_percent < 0:
                discount_text = f"✗ {abs(discount_percent)}% markup on purchases"
                discount_color = (255, 100, 100)
            else:
                discount_text = "Standard pricing"
                discount_color = (200, 200, 200)
            
            discount_surf = rep_font.render(discount_text, True, discount_color)
            screen.blit(discount_surf, (panel_x + 320, panel_y + 45))
        
        # Mode tabs (Buy/Sell)
        tab_y = panel_y + 75
        buy_tab_rect = pygame.Rect(panel_x + 20, tab_y, 150, 40)
        sell_tab_rect = pygame.Rect(panel_x + 180, tab_y, 150, 40)
        
        buy_color = self.selected_color if self.mode == "buy" else self.panel_color
        sell_color = self.selected_color if self.mode == "sell" else self.panel_color
        
        pygame.draw.rect(screen, buy_color, buy_tab_rect)
        pygame.draw.rect(screen, self.text_color, buy_tab_rect, 2)
        pygame.draw.rect(screen, sell_color, sell_tab_rect)
        pygame.draw.rect(screen, self.text_color, sell_tab_rect, 2)
        
        tab_font = pygame.font.SysFont(None, 28)
        buy_text = tab_font.render("BUY", True, self.text_color)
        sell_text = tab_font.render("SELL", True, self.text_color)
        screen.blit(buy_text, (buy_tab_rect.centerx - buy_text.get_width()//2, 
                              buy_tab_rect.centery - buy_text.get_height()//2))
        screen.blit(sell_text, (sell_tab_rect.centerx - sell_text.get_width()//2,
                               sell_tab_rect.centery - sell_text.get_height()//2))
        
        # Player gold display
        gold_text = f"Your Dubloons: {self.player.dubloons}"
        gold_surf = font.render(gold_text, True, self.gold_color)
        screen.blit(gold_surf, (panel_x + panel_width - gold_surf.get_width() - 20, panel_y + 70))
        
        # Item list
        list_y = panel_y + 120
        list_height = panel_height - 180
        
        items = self.get_display_items()
        visible_items = items[self.scroll_offset:self.scroll_offset + self.max_visible_items]
        
        item_font = pygame.font.SysFont(None, 24)
        small_font = pygame.font.SysFont(None, 20)
        
        for i, item in enumerate(visible_items):
            item_index = i + self.scroll_offset
            item_y = list_y + (i * 60)
            
            # Item background
            item_rect = pygame.Rect(panel_x + 20, item_y, panel_width - 40, 55)
            if item_index == self.selected_index:
                pygame.draw.rect(screen, self.selected_color, item_rect)
            else:
                pygame.draw.rect(screen, self.panel_color, item_rect)
            pygame.draw.rect(screen, self.text_color, item_rect, 1)
            
            # Item name
            name_text = item_font.render(item.name, True, self.text_color)
            screen.blit(name_text, (item_rect.x + 10, item_rect.y + 5))
            
            # Item description
            desc_text = small_font.render(item.description[:50], True, (180, 180, 180))
            screen.blit(desc_text, (item_rect.x + 10, item_rect.y + 28))
            
            # Price
            if self.mode == "buy":
                # Get base price and apply reputation discount
                base_price = item.buy_price
                price = base_price
                
                # Apply reputation discount if available
                if self.current_shop.reputation_manager and self.current_shop.shop_id:
                    rep = self.current_shop.reputation_manager.get_or_create_reputation(
                        self.current_shop.shop_id, 
                        self.current_shop.merchant_name
                    )
                    discount_mult = rep.get_discount_multiplier()
                    price = int(base_price * discount_mult)
                
                can_afford = self.player.dubloons >= price
                price_color = self.can_afford_color if can_afford else self.cannot_afford_color
                
                # Show discounted price and original if different
                if price < base_price:
                    price_text = f"{price}g ({base_price}g)"
                else:
                    price_text = f"{price}g"
                
                # Stock indicator
                if item.stock > 0:
                    stock_text = f"Stock: {item.stock}"
                elif item.stock == -1:
                    stock_text = "∞"
                else:
                    stock_text = "OUT"
                    price_color = self.cannot_afford_color
                
                stock_surf = small_font.render(stock_text, True, self.text_color)
                screen.blit(stock_surf, (item_rect.right - 150, item_rect.y + 28))
            else:
                # Get base sell price and apply reputation bonus
                base_sell_price = item.sell_price
                price = base_sell_price
                
                # Apply reputation bonus to sell price
                if self.current_shop.reputation_manager and self.current_shop.shop_id:
                    rep = self.current_shop.reputation_manager.get_or_create_reputation(
                        self.current_shop.shop_id, 
                        self.current_shop.merchant_name
                    )
                    buy_multiplier = rep.get_discount_multiplier()
                    # Better reputation = better sell prices (inverse of buy discount)
                    sell_multiplier = 2.0 - buy_multiplier
                    price = int(base_sell_price * sell_multiplier)
                
                price_color = self.can_afford_color
                price_text = f"+{price}g"
            
            price_surf = font.render(price_text, True, price_color)
            screen.blit(price_surf, (item_rect.right - price_surf.get_width() - 10, item_rect.y + 5))
        
        # Scroll indicators
        if self.scroll_offset > 0:
            scroll_up = small_font.render("▲ More items above", True, self.text_color)
            screen.blit(scroll_up, (panel_x + panel_width//2 - scroll_up.get_width()//2, list_y - 20))
        
        if self.scroll_offset + self.max_visible_items < len(items):
            scroll_down = small_font.render("▼ More items below", True, self.text_color)
            screen.blit(scroll_down, (panel_x + panel_width//2 - scroll_down.get_width()//2, 
                                     list_y + list_height))
        
        # Controls help
        controls_y = panel_y + panel_height - 45
        controls = [
            "↑↓: Navigate",
            "TAB: Switch Mode",
            "ENTER: Buy/Sell",
            "ESC: Close"
        ]
        control_text = " | ".join(controls)
        control_surf = small_font.render(control_text, True, (200, 200, 200))
        screen.blit(control_surf, (panel_x + panel_width//2 - control_surf.get_width()//2, controls_y))
        
        # Message display
        if self.message and self.message_timer > 0:
            msg_surf = font.render(self.message, True, self.gold_color)
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10))
            msg_bg.set_alpha(220)
            msg_bg.fill((0, 0, 0))
            msg_x = screen_width//2 - msg_surf.get_width()//2
            msg_y = screen_height - 100
            screen.blit(msg_bg, (msg_x - 10, msg_y - 5))
            screen.blit(msg_surf, (msg_x, msg_y))
        
        # Controls hint
        controls_y = panel_y + panel_height - 30
        controls_font = pygame.font.SysFont(None, 20)
        
        if self.mode == "buy":
            controls_text = "↑↓: Select | ENTER: Buy | H: Haggle | TAB: Sell Mode | ESC: Exit"
        else:
            controls_text = "↑↓: Select | ENTER: Sell | TAB: Buy Mode | ESC: Exit"
        
        controls_surf = controls_font.render(controls_text, True, (150, 150, 150))
        screen.blit(controls_surf, (panel_x + panel_width//2 - controls_surf.get_width()//2, controls_y))
        
        # Render haggling UI on top if active
        if self.haggling_active:
            self.haggling_ui.draw(screen, font)
