"""
Stock Market & Investment UI
- View all available stocks
- Buy/sell shares
- See player portfolio
- Track stock performance
- View trade agreements
"""

import pygame
from logger_config import logger


class StockMarketUI:
    """UI for stock market and investments"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        
        # UI state
        self.current_tab = 0  # 0=Market, 1=Portfolio, 2=Agreements
        self.tabs = ["Market", "My Portfolio", "Trade Agreements"]
        
        # Scrolling
        self.scroll_offset = 0
        self.max_visible_items = 10
        
        # Selection
        self.selected_index = 0
        
        # Input
        self.quantity_input = ""
        self.input_active = False
        
        # References (set by main.py)
        self.investment_system = None
        self.town_trade_agreement_system = None
        self.player = None
        
    def open(self):
        """Open the stock market UI"""
        self.active = True
        self.current_tab = 0
        self.selected_index = 0
        self.scroll_offset = 0
        logger.info("[STOCK UI] Opened stock market")
    
    def close(self):
        """Close the stock market UI"""
        self.active = False
        self.input_active = False
        self.quantity_input = ""
        logger.info("[STOCK UI] Closed stock market")
    
    def toggle(self):
        """Toggle stock market UI"""
        if self.active:
            self.close()
        else:
            self.open()
    
    def handle_input(self, event):
        """Handle keyboard/mouse input"""
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                # Handle quantity input
                if event.key == pygame.K_RETURN:
                    self._execute_trade()
                    self.input_active = False
                    self.quantity_input = ""
                elif event.key == pygame.K_ESCAPE:
                    self.input_active = False
                    self.quantity_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.quantity_input = self.quantity_input[:-1]
                elif event.unicode.isdigit():
                    self.quantity_input += event.unicode
            else:
                # Normal navigation
                if event.key == pygame.K_ESCAPE:
                    self.close()
                elif event.key == pygame.K_TAB or event.key == pygame.K_RIGHT:
                    self.current_tab = (self.current_tab + 1) % len(self.tabs)
                    self.selected_index = 0
                    self.scroll_offset = 0
                elif event.key == pygame.K_LEFT:
                    self.current_tab = (self.current_tab - 1) % len(self.tabs)
                    self.selected_index = 0
                    self.scroll_offset = 0
                elif event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                elif event.key == pygame.K_DOWN:
                    self.selected_index += 1
                    if self.selected_index >= self.scroll_offset + self.max_visible_items:
                        self.scroll_offset = self.selected_index - self.max_visible_items + 1
                elif event.key == pygame.K_b:
                    # Buy stock
                    if self.current_tab == 0:  # Market tab
                        self.input_active = True
                        self.quantity_input = ""
                elif event.key == pygame.K_s:
                    # Sell stock
                    if self.current_tab == 1:  # Portfolio tab
                        self.input_active = True
                        self.quantity_input = ""
    
    def _execute_trade(self):
        """Execute buy/sell trade"""
        if not self.quantity_input or not self.investment_system or not self.player:
            return
        
        try:
            quantity = int(self.quantity_input)
        except ValueError:
            return
        
        if self.current_tab == 0:  # Buy from market
            stocks = self.investment_system.stock_market.get_all_stocks()
            if 0 <= self.selected_index < len(stocks):
                stock_data = stocks[self.selected_index]
                success, message, cost = self.investment_system.stock_market.buy_stock(
                    stock_data['shop_id'],
                    id(self.player),
                    quantity,
                    self.player.dubloons
                )
                if success:
                    self.player.dubloons -= cost
                    logger.info(f"[STOCK] Player bought {quantity} shares of {stock_data['shop_name']} for {cost}g")
        
        elif self.current_tab == 1:  # Sell from portfolio
            portfolio, _ = self.investment_system.stock_market.get_player_portfolio(id(self.player))
            if 0 <= self.selected_index < len(portfolio):
                stock_data = portfolio[self.selected_index]
                success, message, revenue = self.investment_system.stock_market.sell_stock(
                    stock_data['shop_id'],
                    id(self.player),
                    quantity
                )
                if success:
                    self.player.dubloons += revenue
                    logger.info(f"[STOCK] Player sold {quantity} shares of {stock_data['shop_name']} for {revenue}g")
    
    def draw(self, screen, font):
        """Draw the stock market UI"""
        if not self.active or not self.investment_system:
            return
        
        # Background panel
        panel_width = 1000
        panel_height = 700
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Dark semi-transparent background
        background = pygame.Surface((panel_width, panel_height))
        background.set_alpha(240)
        background.fill((20, 20, 30))
        screen.blit(background, (panel_x, panel_y))
        
        # Border
        pygame.draw.rect(screen, (100, 200, 255), (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title
        title_text = "📈 STOCK MARKET & INVESTMENTS"
        title_surf = font.render(title_text, True, (255, 215, 0))
        screen.blit(title_surf, (panel_x + 20, panel_y + 15))
        
        # Market status
        market_status = self.investment_system.stock_market.get_market_status()
        status_surf = font.render(market_status, True, (200, 200, 200))
        screen.blit(status_surf, (panel_x + panel_width - 200, panel_y + 15))
        
        # Tabs
        tab_y = panel_y + 60
        tab_width = panel_width // len(self.tabs)
        for i, tab_name in enumerate(self.tabs):
            tab_x = panel_x + i * tab_width
            tab_color = (50, 150, 200) if i == self.current_tab else (40, 40, 50)
            pygame.draw.rect(screen, tab_color, (tab_x, tab_y, tab_width, 40))
            pygame.draw.rect(screen, (100, 200, 255), (tab_x, tab_y, tab_width, 40), 2)
            
            tab_text = font.render(tab_name, True, (255, 255, 255))
            text_rect = tab_text.get_rect(center=(tab_x + tab_width // 2, tab_y + 20))
            screen.blit(tab_text, text_rect)
        
        # Content area
        content_y = tab_y + 50
        content_height = panel_height - 120
        
        if self.current_tab == 0:
            self._draw_market_tab(screen, font, panel_x, content_y, panel_width, content_height)
        elif self.current_tab == 1:
            self._draw_portfolio_tab(screen, font, panel_x, content_y, panel_width, content_height)
        elif self.current_tab == 2:
            self._draw_agreements_tab(screen, font, panel_x, content_y, panel_width, content_height)
        
        # Controls
        controls_y = panel_y + panel_height - 40
        controls = "TAB: Switch Tab | ↑↓: Navigate | B: Buy | S: Sell | ESC: Close"
        controls_surf = font.render(controls, True, (150, 150, 150))
        screen.blit(controls_surf, (panel_x + 20, controls_y))
        
        # Input overlay
        if self.input_active:
            self._draw_input_overlay(screen, font)
    
    def _draw_market_tab(self, screen, font, x, y, width, height):
        """Draw market stocks list"""
        # Headers
        header_y = y + 10
        pygame.draw.line(screen, (100, 100, 100), (x + 10, header_y + 25), (x + width - 10, header_y + 25), 1)
        
        headers = ["Shop Name", "Price", "Change", "Available", "Market Cap"]
        header_positions = [x + 20, x + 300, x + 450, x + 600, x + 750]
        
        for i, header in enumerate(headers):
            header_surf = font.render(header, True, (200, 200, 200))
            screen.blit(header_surf, (header_positions[i], header_y))
        
        # Stock list
        stocks = self.investment_system.stock_market.get_all_stocks()
        
        list_y = header_y + 40
        for i in range(self.scroll_offset, min(len(stocks), self.scroll_offset + self.max_visible_items)):
            stock = stocks[i]
            item_y = list_y + (i - self.scroll_offset) * 50
            
            # Highlight selected
            if i == self.selected_index:
                pygame.draw.rect(screen, (50, 80, 120), (x + 10, item_y - 5, width - 20, 45))
            
            # Shop name
            name_surf = font.render(stock['shop_name'][:25], True, (255, 255, 255))
            screen.blit(name_surf, (header_positions[0], item_y))
            
            # Price
            price_surf = font.render(f"{stock['share_price']:.1f}g", True, (255, 215, 0))
            screen.blit(price_surf, (header_positions[1], item_y))
            
            # Price change
            change = stock['price_change']
            change_color = (0, 255, 0) if change >= 0 else (255, 50, 50)
            change_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            change_surf = font.render(change_text, True, change_color)
            screen.blit(change_surf, (header_positions[2], item_y))
            
            # Available shares
            available_surf = font.render(str(stock['available_shares']), True, (200, 200, 200))
            screen.blit(available_surf, (header_positions[3], item_y))
            
            # Market cap
            market_cap = (stock['total_shares'] - stock['available_shares']) * stock['share_price']
            cap_surf = font.render(f"{market_cap:.0f}g", True, (150, 150, 255))
            screen.blit(cap_surf, (header_positions[4], item_y))
    
    def _draw_portfolio_tab(self, screen, font, x, y, width, height):
        """Draw player's portfolio"""
        if not self.player:
            no_data_surf = font.render("Player data not available", True, (255, 50, 50))
            screen.blit(no_data_surf, (x + width // 2 - 100, y + height // 2))
            return
        
        portfolio, total_value = self.investment_system.stock_market.get_player_portfolio(id(self.player))
        
        # Portfolio summary
        summary_y = y + 10
        gold_surf = font.render(f"Cash: {self.player.dubloons}g", True, (255, 215, 0))
        screen.blit(gold_surf, (x + 20, summary_y))
        
        portfolio_value_surf = font.render(f"Portfolio Value: {total_value:.0f}g", True, (100, 255, 100))
        screen.blit(portfolio_value_surf, (x + 250, summary_y))
        
        total_wealth = self.player.dubloons + total_value
        wealth_surf = font.render(f"Total Wealth: {total_wealth:.0f}g", True, (255, 255, 255))
        screen.blit(wealth_surf, (x + 550, summary_y))
        
        # Headers
        header_y = y + 50
        pygame.draw.line(screen, (100, 100, 100), (x + 10, header_y + 25), (x + width - 10, header_y + 25), 1)
        
        headers = ["Shop", "Shares", "Price", "Value", "Ownership %", "P/L"]
        header_positions = [x + 20, x + 250, x + 380, x + 500, x + 650, x + 800]
        
        for i, header in enumerate(headers):
            header_surf = font.render(header, True, (200, 200, 200))
            screen.blit(header_surf, (header_positions[i], header_y))
        
        # Portfolio items
        if not portfolio:
            no_stocks_surf = font.render("You don't own any stocks yet", True, (150, 150, 150))
            screen.blit(no_stocks_surf, (x + width // 2 - 150, y + height // 2))
            return
        
        list_y = header_y + 40
        for i in range(self.scroll_offset, min(len(portfolio), self.scroll_offset + self.max_visible_items)):
            stock = portfolio[i]
            item_y = list_y + (i - self.scroll_offset) * 50
            
            # Highlight selected
            if i == self.selected_index:
                pygame.draw.rect(screen, (50, 80, 120), (x + 10, item_y - 5, width - 20, 45))
            
            # Shop name
            name_surf = font.render(stock['shop_name'][:20], True, (255, 255, 255))
            screen.blit(name_surf, (header_positions[0], item_y))
            
            # Shares
            shares_surf = font.render(str(stock['shares']), True, (200, 200, 200))
            screen.blit(shares_surf, (header_positions[1], item_y))
            
            # Price
            price_surf = font.render(f"{stock['share_price']:.1f}g", True, (255, 215, 0))
            screen.blit(price_surf, (header_positions[2], item_y))
            
            # Value
            value_surf = font.render(f"{stock['current_value']:.0f}g", True, (100, 255, 100))
            screen.blit(value_surf, (header_positions[3], item_y))
            
            # Ownership %
            ownership_surf = font.render(f"{stock['ownership_percent']:.1f}%", True, (150, 200, 255))
            screen.blit(ownership_surf, (header_positions[4], item_y))
            
            # P/L
            pl = stock['price_change']
            pl_color = (0, 255, 0) if pl >= 0 else (255, 50, 50)
            pl_text = f"+{pl:.1f}%" if pl >= 0 else f"{pl:.1f}%"
            pl_surf = font.render(pl_text, True, pl_color)
            screen.blit(pl_surf, (header_positions[5], item_y))
    
    def _draw_agreements_tab(self, screen, font, x, y, width, height):
        """Draw trade agreements"""
        if not self.town_trade_agreement_system:
            no_data_surf = font.render("Trade agreements system not available", True, (255, 50, 50))
            screen.blit(no_data_surf, (x + width // 2 - 200, y + height // 2))
            return
        
        agreements = self.town_trade_agreement_system.get_active_agreements()
        
        # Headers
        header_y = y + 10
        pygame.draw.line(screen, (100, 100, 100), (x + 10, header_y + 25), (x + width - 10, header_y + 25), 1)
        
        headers = ["Route", "Type", "Duration", "Volume", "Savings"]
        header_positions = [x + 20, x + 350, x + 550, x + 680, x + 820]
        
        for i, header in enumerate(headers):
            header_surf = font.render(header, True, (200, 200, 200))
            screen.blit(header_surf, (header_positions[i], header_y))
        
        # Agreements list
        if not agreements:
            no_agreements_surf = font.render("No active trade agreements", True, (150, 150, 150))
            screen.blit(no_agreements_surf, (x + width // 2 - 150, y + height // 2))
            return
        
        list_y = header_y + 40
        for i in range(self.scroll_offset, min(len(agreements), self.scroll_offset + self.max_visible_items)):
            agreement = agreements[i]
            item_y = list_y + (i - self.scroll_offset) * 50
            
            # Highlight selected
            if i == self.selected_index:
                pygame.draw.rect(screen, (50, 80, 120), (x + 10, item_y - 5, width - 20, 45))
            
            # Route
            route_text = f"{agreement['town_a']} ↔ {agreement['town_b']}"
            route_surf = font.render(route_text[:30], True, (255, 255, 255))
            screen.blit(route_surf, (header_positions[0], item_y))
            
            # Type
            type_text = agreement['type'].replace('_', ' ').title()
            type_surf = font.render(type_text[:15], True, (100, 200, 255))
            screen.blit(type_surf, (header_positions[1], item_y))
            
            # Duration
            duration_surf = font.render(f"{agreement['duration_days']}d", True, (200, 200, 200))
            screen.blit(duration_surf, (header_positions[2], item_y))
            
            # Volume
            volume_surf = font.render(f"{agreement['trade_volume']:.0f}g", True, (255, 215, 0))
            screen.blit(volume_surf, (header_positions[3], item_y))
            
            # Savings
            savings_surf = font.render(f"{agreement['total_savings']:.0f}g", True, (0, 255, 0))
            screen.blit(savings_surf, (header_positions[4], item_y))
    
    def _draw_input_overlay(self, screen, font):
        """Draw quantity input overlay"""
        overlay_width = 400
        overlay_height = 150
        overlay_x = (self.screen_width - overlay_width) // 2
        overlay_y = (self.screen_height - overlay_height) // 2
        
        # Background
        pygame.draw.rect(screen, (30, 30, 40), (overlay_x, overlay_y, overlay_width, overlay_height))
        pygame.draw.rect(screen, (100, 200, 255), (overlay_x, overlay_y, overlay_width, overlay_height), 3)
        
        # Title
        action = "Buy" if self.current_tab == 0 else "Sell"
        title_surf = font.render(f"{action} Shares", True, (255, 255, 255))
        screen.blit(title_surf, (overlay_x + 20, overlay_y + 20))
        
        # Input prompt
        prompt_surf = font.render("Enter quantity:", True, (200, 200, 200))
        screen.blit(prompt_surf, (overlay_x + 20, overlay_y + 60))
        
        # Input box
        input_box = pygame.Rect(overlay_x + 20, overlay_y + 90, overlay_width - 40, 35)
        pygame.draw.rect(screen, (50, 50, 60), input_box)
        pygame.draw.rect(screen, (100, 200, 255), input_box, 2)
        
        # Input text
        input_surf = font.render(self.quantity_input, True, (255, 255, 255))
        screen.blit(input_surf, (overlay_x + 30, overlay_y + 95))
        
        # Instructions
        inst_surf = font.render("Press ENTER to confirm, ESC to cancel", True, (150, 150, 150))
        inst_surf_small = pygame.transform.scale(inst_surf, (int(inst_surf.get_width() * 0.8), int(inst_surf.get_height() * 0.8)))
        screen.blit(inst_surf_small, (overlay_x + 40, overlay_y + 130))
