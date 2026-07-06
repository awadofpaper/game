"""
Commodity Exchange UI - Multi-town price comparison and arbitrage finder
Progressive unlock: Level 15 (basic), 40 (regional), 60 (reports), 90 (full arbitrage)
"""

import pygame
from typing import Dict, List, Optional, Tuple
from market_system import TRADEABLE_COMMODITIES, CommodityCategory


class CommodityExchangeUI:
    """Trading floor UI showing prices across all towns"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        
        # UI state
        self.selected_commodity = None
        self.selected_category = None
        self.sort_column = 'price'  # 'town', 'price', 'supply', 'demand', 'trend'
        self.sort_ascending = True
        self.scroll_offset = 0
        
        # UI dimensions
        self.width = 1100
        self.height = 700
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.header_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.panel_color = (45, 45, 55)
        self.selected_color = (70, 130, 180)
        self.text_color = (255, 255, 255)
        self.dim_text_color = (180, 180, 180)
        self.good_price_color = (100, 220, 100)  # Buy here
        self.bad_price_color = (220, 100, 100)   # Sell here
        self.normal_price_color = (200, 200, 200)
        self.locked_color = (150, 50, 50)
        
        # References (set externally)
        self.market_manager = None
        self.player = None
        self.economics_skill_tree = None
    
    def open(self):
        """Open the exchange UI"""
        self.active = True
        self.scroll_offset = 0
    
    def close(self):
        """Close the exchange UI"""
        self.active = False
    
    def toggle(self):
        """Toggle exchange UI"""
        if self.active:
            self.close()
        else:
            self.open()
    
    def get_unlock_level(self) -> int:
        """Get player's unlock level for features"""
        if not self.player:
            return 0
        
        level = self.player.level
        
        # Check economics skill tree if available
        if self.economics_skill_tree and hasattr(self.player, 'has_economics_skill'):
            if self.player.has_economics_skill('arbitrage_master'):
                return 90  # Full access
            elif self.player.has_economics_skill('market_analyst'):
                return 60  # Can see supply/demand
            elif self.player.has_economics_skill('regional_trader'):
                return 40  # Can see nearby towns
        
        return level
    
    def can_see_multi_town(self) -> bool:
        """Check if player can see prices in multiple towns"""
        return self.get_unlock_level() >= 15
    
    def can_see_supply_demand(self) -> bool:
        """Check if player can see supply/demand data"""
        return self.get_unlock_level() >= 60
    
    def can_see_arbitrage(self) -> bool:
        """Check if player can see arbitrage opportunities"""
        return self.get_unlock_level() >= 90
    
    def handle_input(self, event) -> bool:
        """Handle input events. Returns True if consumed."""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                self.close()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
            elif event.key == pygame.K_DOWN:
                if self.selected_commodity:
                    self.scroll_offset += 1
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Commodity list selection
            commodity_list_rect = pygame.Rect(self.x + 20, self.y + 130, 300, 500)
            if commodity_list_rect.collidepoint(mouse_pos):
                relative_y = mouse_pos[1] - (self.y + 130)
                index = (relative_y // 35) + self.scroll_offset
                commodities = self._get_filtered_commodities()
                if 0 <= index < len(commodities):
                    self.selected_commodity = commodities[index]
                return True
            
            # Category filter buttons
            for i, category in enumerate([None] + list(CommodityCategory)):
                button_rect = pygame.Rect(self.x + 20 + i * 95, self.y + 80, 90, 30)
                if button_rect.collidepoint(mouse_pos):
                    self.selected_category = category
                    self.scroll_offset = 0
                    return True
            
            # Sort column headers (if data visible)
            if self.selected_commodity and self.can_see_multi_town():
                headers = ['town', 'price', 'supply', 'demand', 'trend']
                header_x = self.x + 350
                for i, header in enumerate(headers):
                    if header == 'supply' or header == 'demand':
                        if not self.can_see_supply_demand():
                            continue
                    if header == 'trend':
                        if not self.can_see_arbitrage():
                            continue
                    
                    header_rect = pygame.Rect(header_x + i * 140, self.y + 180, 130, 30)
                    if header_rect.collidepoint(mouse_pos):
                        if self.sort_column == header:
                            self.sort_ascending = not self.sort_ascending
                        else:
                            self.sort_column = header
                            self.sort_ascending = True
                        return True
        
        return False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font = None):
        """Draw the commodity exchange UI"""
        if not self.active:
            return
        
        # Background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, panel_rect)
        pygame.draw.rect(screen, self.text_color, panel_rect, 2)
        
        # Title
        title = self.title_font.render("📈 COMMODITY EXCHANGE", True, (255, 215, 0))
        title_x = self.x + (self.width - title.get_width()) // 2
        screen.blit(title, (title_x, self.y + 15))
        
        # Unlock status
        unlock_level = self.get_unlock_level()
        if unlock_level < 15:
            # Locked message
            locked_text = self.header_font.render("Exchange Unlocks at Level 15", True, self.locked_color)
            screen.blit(locked_text, (self.x + self.width // 2 - locked_text.get_width() // 2, self.y + 250))
            
            hint = self.text_font.render(f"You need {15 - self.player.level} more levels", True, self.dim_text_color)
            screen.blit(hint, (self.x + self.width // 2 - hint.get_width() // 2, self.y + 290))
            
            controls = self.small_font.render("Press M to close", True, self.dim_text_color)
            screen.blit(controls, (self.x + self.width // 2 - controls.get_width() // 2, self.y + 650))
            return
        
        # Category filters
        categories = [None] + list(CommodityCategory)
        for i, category in enumerate(categories):
            button_rect = pygame.Rect(self.x + 20 + i * 95, self.y + 80, 90, 30)
            is_selected = category == self.selected_category
            
            color = self.selected_color if is_selected else self.panel_color
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, self.text_color, button_rect, 1)
            
            label_text = "All" if category is None else category.value[:8].title()
            label = self.small_font.render(label_text, True, self.text_color)
            label_x = button_rect.x + (button_rect.width - label.get_width()) // 2
            label_y = button_rect.y + (button_rect.height - label.get_height()) // 2
            screen.blit(label, (label_x, label_y))
        
        # Commodity list panel
        list_rect = pygame.Rect(self.x + 20, self.y + 130, 300, 500)
        pygame.draw.rect(screen, self.panel_color, list_rect)
        pygame.draw.rect(screen, self.text_color, list_rect, 1)
        
        list_header = self.header_font.render("Commodities", True, self.text_color)
        screen.blit(list_header, (list_rect.x + 10, self.y + 125))
        
        # Draw commodity list
        commodities = self._get_filtered_commodities()
        visible_count = 14
        
        for i, commodity_id in enumerate(commodities[self.scroll_offset:self.scroll_offset + visible_count]):
            commodity = TRADEABLE_COMMODITIES.get(commodity_id)
            if not commodity:
                continue
            
            y_pos = list_rect.y + 10 + i * 35
            item_rect = pygame.Rect(list_rect.x + 5, y_pos, 290, 30)
            
            # Highlight selected
            if commodity_id == self.selected_commodity:
                pygame.draw.rect(screen, self.selected_color, item_rect)
            
            # Commodity name
            name_text = self.text_font.render(commodity.name, True, self.text_color)
            screen.blit(name_text, (item_rect.x + 5, item_rect.y + 5))
        
        # Price data panel
        data_rect = pygame.Rect(self.x + 340, self.y + 130, 740, 500)
        pygame.draw.rect(screen, self.panel_color, data_rect)
        pygame.draw.rect(screen, self.text_color, data_rect, 1)
        
        if self.selected_commodity:
            commodity = TRADEABLE_COMMODITIES.get(self.selected_commodity)
            
            # Commodity details header
            detail_header = self.header_font.render(commodity.name, True, self.text_color)
            screen.blit(detail_header, (data_rect.x + 10, self.y + 125))
            
            # Category label
            category_label = self.small_font.render(
                f"{commodity.category.value.title()} | Base: {commodity.base_price:.0f}g",
                True, self.dim_text_color
            )
            screen.blit(category_label, (data_rect.x + 10, data_rect.y + 5))
            
            # Column headers
            headers_y = data_rect.y + 35
            headers = [
                ('Town', 150),
                ('Price', 120),
            ]
            
            if self.can_see_supply_demand():
                headers.extend([('Supply', 100), ('Demand', 100)])
            
            if self.can_see_arbitrage():
                headers.append(('Trend', 120))
            
            header_x = data_rect.x + 10
            for header_text, width in headers:
                # Check if this column is sorted
                arrow = ""
                if self.sort_column == header_text.lower():
                    arrow = " ↑" if self.sort_ascending else " ↓"
                
                header_surf = self.text_font.render(header_text + arrow, True, self.text_color)
                screen.blit(header_surf, (header_x, headers_y))
                header_x += width
            
            # Divider line
            pygame.draw.line(screen, self.text_color,
                           (data_rect.x + 10, headers_y + 25),
                           (data_rect.x + data_rect.width - 10, headers_y + 25), 1)
            
            # Town price data
            prices = self._get_sorted_town_data()
            
            row_y = headers_y + 35
            for town_name, data in prices[:12]:  # Show top 12
                # Town name
                town_surf = self.text_font.render(town_name[:15], True, self.text_color)
                screen.blit(town_surf, (data_rect.x + 10, row_y))
                
                # Price with color coding
                price = data['price']
                price_color = self._get_price_color(price, data.get('avg_price', price))
                price_surf = self.text_font.render(f"{price:.0f}g", True, price_color)
                screen.blit(price_surf, (data_rect.x + 160, row_y))
                
                col_x = data_rect.x + 280
                
                # Supply (if unlocked)
                if self.can_see_supply_demand():
                    supply = data.get('supply', 0)
                    supply_color = self._get_supply_color(supply)
                    supply_surf = self.text_font.render(str(supply), True, supply_color)
                    screen.blit(supply_surf, (col_x, row_y))
                    col_x += 100
                    
                    # Demand (if unlocked)
                    demand = data.get('demand', 0)
                    demand_surf = self.text_font.render(str(demand), True, self.dim_text_color)
                    screen.blit(demand_surf, (col_x, row_y))
                    col_x += 100
                
                # Trend (if unlocked)
                if self.can_see_arbitrage():
                    trend = data.get('trend', 0.0)
                    trend_text = self._format_trend(trend)
                    trend_color = self.good_price_color if trend > 0 else (
                        self.bad_price_color if trend < 0 else self.dim_text_color
                    )
                    trend_surf = self.text_font.render(trend_text, True, trend_color)
                    screen.blit(trend_surf, (col_x, row_y))
                
                row_y += 30
            
            # Arbitrage opportunity box (if unlocked)
            if self.can_see_arbitrage() and self.market_manager:
                arb = self.market_manager.find_arbitrage_opportunities(self.selected_commodity)
                if arb:
                    # Arbitrage panel
                    arb_rect = pygame.Rect(data_rect.x + 10, data_rect.y + 420, data_rect.width - 20, 70)
                    pygame.draw.rect(screen, (50, 80, 50), arb_rect)
                    pygame.draw.rect(screen, (100, 220, 100), arb_rect, 2)
                    
                    # Title
                    arb_title = self.header_font.render("💡 ARBITRAGE OPPORTUNITY", True, (100, 255, 100))
                    screen.blit(arb_title, (arb_rect.x + 10, arb_rect.y + 5))
                    
                    # Buy/Sell info
                    buy_text = f"Buy: {arb['buy_town']} ({arb['buy_price']:.0f}g)"
                    sell_text = f"Sell: {arb['sell_town']} ({arb['sell_price']:.0f}g)"
                    profit_text = f"Profit: {arb['profit_percent']:.0f}%"
                    
                    buy_surf = self.text_font.render(buy_text, True, self.good_price_color)
                    sell_surf = self.text_font.render(sell_text, True, self.bad_price_color)
                    profit_surf = self.text_font.render(profit_text, True, (255, 215, 0))
                    
                    screen.blit(buy_surf, (arb_rect.x + 10, arb_rect.y + 35))
                    screen.blit(sell_surf, (arb_rect.x + 250, arb_rect.y + 35))
                    screen.blit(profit_surf, (arb_rect.x + 500, arb_rect.y + 35))
        else:
            # Prompt to select
            prompt = self.text_font.render("← Select a commodity to view prices", True, self.dim_text_color)
            screen.blit(prompt, (data_rect.x + data_rect.width // 2 - prompt.get_width() // 2, data_rect.y + 200))
        
        # Controls
        controls_y = self.y + 650
        controls_text = []
        
        if unlock_level < 40:
            controls_text.append("Level 40: See nearby towns")
        if unlock_level < 60:
            controls_text.append("Level 60: See supply/demand")
        if unlock_level < 90:
            controls_text.append("Level 90: See arbitrage opportunities")
        
        if controls_text:
            for i, text in enumerate(controls_text):
                surf = self.small_font.render(text, True, self.dim_text_color)
                screen.blit(surf, (self.x + 20, controls_y + i * 18))
        
        main_controls = self.small_font.render("↑↓: Scroll | M/ESC: Close", True, self.dim_text_color)
        screen.blit(main_controls, (self.x + self.width - main_controls.get_width() - 20, controls_y))
    
    def _get_filtered_commodities(self) -> list:
        """Get list of commodities filtered by category"""
        commodities = []
        for commodity_id, commodity in TRADEABLE_COMMODITIES.items():
            if self.selected_category is None or commodity.category == self.selected_category:
                commodities.append(commodity_id)
        return sorted(commodities)
    
    def _get_sorted_town_data(self) -> list:
        """Get town price data, sorted by current column"""
        if not self.market_manager or not self.selected_commodity:
            return []
        
        prices = self.market_manager.get_all_town_prices(self.selected_commodity)
        
        # Build data list
        town_data = []
        all_prices = list(prices.values())
        avg_price = sum(all_prices) / len(all_prices) if all_prices else 0
        
        for town_name, price in prices.items():
            town_market = self.market_manager.town_markets.get(town_name)
            if not town_market:
                continue
            
            market_data = town_market.get_market_data(self.selected_commodity)
            if not market_data:
                continue
            
            data = {
                'price': price,
                'avg_price': avg_price,
                'supply': market_data.supply,
                'demand': market_data.demand,
                'trend': market_data.history.get_price_change_percent(7) if hasattr(market_data, 'history') else 0
            }
            
            town_data.append((town_name, data))
        
        # Sort by current column
        if self.sort_column == 'town':
            town_data.sort(key=lambda x: x[0], reverse=not self.sort_ascending)
        elif self.sort_column == 'price':
            town_data.sort(key=lambda x: x[1]['price'], reverse=not self.sort_ascending)
        elif self.sort_column == 'supply':
            town_data.sort(key=lambda x: x[1]['supply'], reverse=not self.sort_ascending)
        elif self.sort_column == 'demand':
            town_data.sort(key=lambda x: x[1]['demand'], reverse=not self.sort_ascending)
        elif self.sort_column == 'trend':
            town_data.sort(key=lambda x: x[1]['trend'], reverse=not self.sort_ascending)
        
        return town_data
    
    def _get_price_color(self, price: float, avg_price: float):
        """Get color for price based on comparison to average"""
        if price < avg_price * 0.85:
            return self.good_price_color  # Good buy
        elif price > avg_price * 1.15:
            return self.bad_price_color   # Good sell
        else:
            return self.normal_price_color
    
    def _get_supply_color(self, supply: int):
        """Get color for supply level"""
        if supply < 20:
            return self.bad_price_color  # Low supply
        elif supply > 100:
            return self.good_price_color  # High supply
        else:
            return self.dim_text_color
    
    def _format_trend(self, trend_percent: float) -> str:
        """Format trend as string with arrow"""
        if trend_percent > 5:
            return f"↗ +{trend_percent:.0f}%"
        elif trend_percent < -5:
            return f"↘ {trend_percent:.0f}%"
        else:
            return f"→ {trend_percent:.0f}%"
