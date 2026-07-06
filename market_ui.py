"""
Market UI - Trading interface for the market economy system
"""

import pygame
from market_system import TRADEABLE_COMMODITIES, CommodityCategory


class MarketUI:
    """UI for browsing and trading commodities"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        
        # UI state
        self.current_town = None
        self.selected_commodity = None
        self.selected_category = None
        self.quantity = 1
        self.scroll_offset = 0
        self.transaction_mode = "buy"  # "buy" or "sell"
        
        # UI dimensions
        self.width = 900
        self.height = 600
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.header_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # Colors
        self.bg_color = (40, 40, 50)
        self.panel_color = (50, 50, 60)
        self.selected_color = (70, 130, 180)
        self.text_color = (255, 255, 255)
        self.dim_text_color = (180, 180, 180)
        self.buy_color = (100, 200, 100)
        self.sell_color = (200, 100, 100)
        self.locked_color = (150, 50, 50)
        
        # Buttons
        self.buy_button_rect = pygame.Rect(self.x + 550, self.y + 500, 150, 40)
        self.sell_button_rect = pygame.Rect(self.x + 710, self.y + 500, 150, 40)
        self.close_button_rect = pygame.Rect(self.x + self.width - 40, self.y + 10, 30, 30)
        
        # Category filters
        self.categories = [None] + list(CommodityCategory)  # None = All
        self.category_buttons = []
        self._create_category_buttons()
        
    def _create_category_buttons(self):
        """Create filter buttons for each category"""
        button_width = 100
        button_height = 30
        start_x = self.x + 20
        start_y = self.y + 80
        
        for i, category in enumerate(self.categories):
            row = i // 8
            col = i % 8
            x = start_x + col * (button_width + 5)
            y = start_y + row * (button_height + 5)
            label = "All" if category is None else category.value.title()
            self.category_buttons.append({
                'rect': pygame.Rect(x, y, button_width, button_height),
                'category': category,
                'label': label
            })
    
    def open(self, town_name, player_level):
        """Open the market UI"""
        self.active = True
        self.current_town = town_name
        self.selected_commodity = None
        self.scroll_offset = 0
        self.quantity = 1
        
    def close(self):
        """Close the market UI"""
        self.active = False
        self.current_town = None
        
    def handle_event(self, event, market_manager, player):
        """Handle input events"""
        if not self.active:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Close button
            if self.close_button_rect.collidepoint(mouse_pos):
                self.close()
                return None
            
            # Category filter buttons
            for button in self.category_buttons:
                if button['rect'].collidepoint(mouse_pos):
                    self.selected_category = button['category']
                    self.scroll_offset = 0
                    return None
            
            # Commodity selection
            commodity_rect = pygame.Rect(self.x + 20, self.y + 150, 400, 330)
            if commodity_rect.collidepoint(mouse_pos):
                # Calculate which commodity was clicked
                relative_y = mouse_pos[1] - (self.y + 150)
                index = (relative_y // 40) + self.scroll_offset
                filtered_commodities = self._get_filtered_commodities()
                if 0 <= index < len(filtered_commodities):
                    self.selected_commodity = filtered_commodities[index]
                    self.quantity = 1
            
            # Buy button
            if self.buy_button_rect.collidepoint(mouse_pos) and self.selected_commodity:
                if not market_manager.is_market_unlocked(player.level):
                    return {"type": "error", "message": f"Market unlocks at level {market_manager.MARKET_UNLOCK_LEVEL}"}
                
                result = market_manager.buy_commodity(
                    player,
                    self.current_town,
                    self.selected_commodity,
                    self.quantity
                )
                return {"type": "buy", "result": result}
            
            # Sell button
            if self.sell_button_rect.collidepoint(mouse_pos) and self.selected_commodity:
                if not market_manager.is_market_unlocked(player.level):
                    return {"type": "error", "message": f"Market unlocks at level {market_manager.MARKET_UNLOCK_LEVEL}"}
                
                result = market_manager.sell_commodity(
                    player,
                    self.current_town,
                    self.selected_commodity,
                    self.quantity
                )
                return {"type": "sell", "result": result}
        
        elif event.type == pygame.KEYDOWN:
            # Quantity controls
            if event.key == pygame.K_UP:
                self.quantity = min(self.quantity + 1, 100)
            elif event.key == pygame.K_DOWN:
                self.quantity = max(self.quantity - 1, 1)
            elif event.key == pygame.K_PAGEUP:
                self.quantity = min(self.quantity + 10, 100)
            elif event.key == pygame.K_PAGEDOWN:
                self.quantity = max(self.quantity - 10, 1)
            elif event.key == pygame.K_ESCAPE:
                self.close()
        
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll commodity list
            max_scroll = max(0, len(self._get_filtered_commodities()) - 8)
            self.scroll_offset = max(0, min(self.scroll_offset - event.y, max_scroll))
        
        return None
    
    def _get_filtered_commodities(self):
        """Get list of commodities filtered by selected category"""
        if self.selected_category is None:
            return list(TRADEABLE_COMMODITIES.keys())
        else:
            return [
                cid for cid, commodity in TRADEABLE_COMMODITIES.items()
                if commodity.category == self.selected_category
            ]
    
    def draw(self, screen, market_manager, player):
        """Draw the market UI"""
        if not self.active:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.text_color, (self.x, self.y, self.width, self.height), 2)
        
        # Title
        title = self.title_font.render(f"Market - {self.current_town}", True, self.text_color)
        screen.blit(title, (self.x + 20, self.y + 20))
        
        # Close button
        pygame.draw.rect(screen, (200, 50, 50), self.close_button_rect)
        close_text = self.text_font.render("X", True, self.text_color)
        screen.blit(close_text, (self.close_button_rect.x + 8, self.close_button_rect.y + 5))
        
        # Check if market is unlocked
        if not market_manager.is_market_unlocked(player.level):
            locked_text = self.header_font.render(
                f"Market unlocks at Level {market_manager.MARKET_UNLOCK_LEVEL}",
                True, self.locked_color
            )
            screen.blit(locked_text, (self.x + self.width // 2 - locked_text.get_width() // 2, self.y + 200))
            
            levels_needed = market_manager.MARKET_UNLOCK_LEVEL - player.level
            hint_text = self.text_font.render(
                f"You need {levels_needed} more level{'s' if levels_needed > 1 else ''}",
                True, self.dim_text_color
            )
            screen.blit(hint_text, (self.x + self.width // 2 - hint_text.get_width() // 2, self.y + 240))
            return
        
        # Category filters
        for button in self.category_buttons:
            is_selected = button['category'] == self.selected_category
            color = self.selected_color if is_selected else self.panel_color
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, self.text_color, button['rect'], 1)
            
            label = self.small_font.render(button['label'], True, self.text_color)
            label_x = button['rect'].x + (button['rect'].width - label.get_width()) // 2
            label_y = button['rect'].y + (button['rect'].height - label.get_height()) // 2
            screen.blit(label, (label_x, label_y))
        
        # Commodity list panel
        list_rect = pygame.Rect(self.x + 20, self.y + 150, 400, 330)
        pygame.draw.rect(screen, self.panel_color, list_rect)
        pygame.draw.rect(screen, self.text_color, list_rect, 1)
        
        # Draw commodities
        filtered_commodities = self._get_filtered_commodities()
        town_market = market_manager.town_markets.get(self.current_town)
        
        for i, commodity_id in enumerate(filtered_commodities[self.scroll_offset:self.scroll_offset + 8]):
            commodity = TRADEABLE_COMMODITIES.get(commodity_id)
            if not commodity:
                continue
            
            y_pos = self.y + 155 + i * 40
            item_rect = pygame.Rect(self.x + 25, y_pos, 390, 35)
            
            # Highlight selected
            if commodity_id == self.selected_commodity:
                pygame.draw.rect(screen, self.selected_color, item_rect)
            
            # Get market data
            market_data = town_market.get_market_data(commodity_id) if town_market else None
            
            # Item name
            name_text = self.text_font.render(commodity.name, True, self.text_color)
            screen.blit(name_text, (self.x + 30, y_pos + 5))
            
            # Price and supply
            if market_data:
                price_text = self.text_font.render(
                    f"{market_data.current_price:.0f}g",
                    True, (255, 215, 0)
                )
                supply_text = self.small_font.render(
                    f"Supply: {market_data.supply}",
                    True, self.dim_text_color
                )
                screen.blit(price_text, (self.x + 300, y_pos + 5))
                screen.blit(supply_text, (self.x + 300, y_pos + 22))
        
        # Scroll indicator
        if len(filtered_commodities) > 8:
            scroll_text = self.small_font.render(
                f"{self.scroll_offset + 1}-{min(self.scroll_offset + 8, len(filtered_commodities))} of {len(filtered_commodities)}",
                True, self.dim_text_color
            )
            screen.blit(scroll_text, (self.x + 25, self.y + 490))
        
        # Selected item details panel
        details_rect = pygame.Rect(self.x + 440, self.y + 150, 440, 330)
        pygame.draw.rect(screen, self.panel_color, details_rect)
        pygame.draw.rect(screen, self.text_color, details_rect, 1)
        
        if self.selected_commodity:
            commodity = TRADEABLE_COMMODITIES.get(self.selected_commodity)
            market_data = town_market.get_market_data(self.selected_commodity) if town_market else None
            
            if commodity and market_data:
                # Name and category
                name = self.header_font.render(commodity.name, True, self.text_color)
                screen.blit(name, (self.x + 450, self.y + 160))
                
                category = self.text_font.render(
                    f"Category: {commodity.category.value.title()}",
                    True, self.dim_text_color
                )
                screen.blit(category, (self.x + 450, self.y + 195))
                
                # Market info
                y_offset = 230
                info_items = [
                    f"Current Price: {market_data.current_price:.0f}g",
                    f"Base Price: {commodity.base_price:.0f}g",
                    f"Supply: {market_data.supply}",
                    f"Demand: {market_data.demand}",
                    f"Rarity: {commodity.rarity.value.title()}",
                    f"Volatility: {commodity.volatility:.1%}",
                ]
                
                for info in info_items:
                    text = self.text_font.render(info, True, self.text_color)
                    screen.blit(text, (self.x + 450, self.y + y_offset))
                    y_offset += 25
                
                # Quantity selector
                y_offset += 20
                qty_label = self.text_font.render("Quantity:", True, self.text_color)
                screen.blit(qty_label, (self.x + 450, self.y + y_offset))
                
                qty_text = self.header_font.render(str(self.quantity), True, self.text_color)
                screen.blit(qty_text, (self.x + 560, self.y + y_offset - 5))
                
                hint = self.small_font.render("(Use arrow keys or PgUp/PgDn)", True, self.dim_text_color)
                screen.blit(hint, (self.x + 450, self.y + y_offset + 30))
                
                # Total cost
                y_offset += 60
                total_buy = market_data.current_price * self.quantity
                total_buy_with_fee = total_buy * (1 + town_market.transaction_fees)
                
                total_sell = market_data.current_price * self.quantity
                total_sell_with_fee = total_sell * (1 - town_market.transaction_fees)
                
                buy_label = self.text_font.render(f"Buy {self.quantity}:", True, self.buy_color)
                screen.blit(buy_label, (self.x + 450, self.y + y_offset))
                buy_cost = self.text_font.render(f"{total_buy_with_fee:.0f}g", True, self.buy_color)
                screen.blit(buy_cost, (self.x + 700, self.y + y_offset))
                
                y_offset += 30
                sell_label = self.text_font.render(f"Sell {self.quantity}:", True, self.sell_color)
                screen.blit(sell_label, (self.x + 450, self.y + y_offset))
                sell_profit = self.text_font.render(f"{total_sell_with_fee:.0f}g", True, self.sell_color)
                screen.blit(sell_profit, (self.x + 700, self.y + y_offset))
        
        # Buy/Sell buttons
        pygame.draw.rect(screen, self.buy_color, self.buy_button_rect)
        pygame.draw.rect(screen, self.text_color, self.buy_button_rect, 2)
        buy_text = self.header_font.render("BUY", True, self.text_color)
        screen.blit(buy_text, (self.buy_button_rect.centerx - buy_text.get_width() // 2,
                              self.buy_button_rect.centery - buy_text.get_height() // 2))
        
        pygame.draw.rect(screen, self.sell_color, self.sell_button_rect)
        pygame.draw.rect(screen, self.text_color, self.sell_button_rect, 2)
        sell_text = self.header_font.render("SELL", True, self.text_color)
        screen.blit(sell_text, (self.sell_button_rect.centerx - sell_text.get_width() // 2,
                               self.sell_button_rect.centery - sell_text.get_height() // 2))
        
        # Player info footer
        footer_y = self.y + self.height - 40
        player_gold = self.text_font.render(f"Dubloons: {player.dubloons:.0f}db", True, (255, 215, 0))
        screen.blit(player_gold, (self.x + 20, footer_y))
        
        player_level = self.text_font.render(f"Level: {player.level}", True, self.text_color)
        screen.blit(player_level, (self.x + 150, footer_y))
        
        # Merchant skill
        merchant_skill = player.skills_manager.get_skill("Merchant")
        if merchant_skill:
            merchant_text = self.text_font.render(
                f"Merchant: {merchant_skill.level}",
                True, (100, 200, 255)
            )
            screen.blit(merchant_text, (self.x + 280, footer_y))
