"""
Trade Route UI
Shows trade routes, caravans, contracts, and allows contract fulfillment
"""
import pygame
from logger_config import logger


class TradeRouteUI:
    """UI for viewing trade routes, caravans, and managing contracts"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.selected_tab = 0  # 0=routes, 1=caravans, 2=contracts
        self.scroll_offset = 0
        self.selected_index = 0
        self.tabs = ["Trade Routes", "Caravans", "Contracts"]
        
        # Colors
        self.bg_color = (20, 20, 30, 230)
        self.panel_color = (40, 40, 50)
        self.highlight_color = (80, 120, 180)
        self.text_color = (220, 220, 220)
        self.tab_active_color = (60, 100, 160)
        self.tab_inactive_color = (30, 30, 40)
        
    def toggle(self):
        """Toggle UI visibility"""
        self.active = not self.active
        if self.active:
            self.scroll_offset = 0
            self.selected_index = 0
            logger.info("[TRADE UI] Trade route UI opened")
    
    def handle_input(self, event, trade_route_system, player, current_town):
        """Handle keyboard/mouse input"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return None
            elif event.key == pygame.K_TAB:
                self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
                self.selected_index = 0
                self.scroll_offset = 0
            elif event.key == pygame.K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
            elif event.key == pygame.K_DOWN:
                max_index = self._get_max_index(trade_route_system, current_town)
                if self.selected_index < max_index - 1:
                    self.selected_index += 1
            elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
                # Try to fulfill selected contract
                if self.selected_tab == 2:  # Contracts tab
                    return self._fulfill_selected_contract(trade_route_system, player, current_town)
        
        return None
    
    def _get_max_index(self, trade_route_system, current_town):
        """Get max selectable index for current tab"""
        if self.selected_tab == 0:  # Routes
            return len(trade_route_system.routes)
        elif self.selected_tab == 1:  # Caravans
            return len(trade_route_system.caravans)
        elif self.selected_tab == 2:  # Contracts
            contracts = trade_route_system.get_available_contracts_for_player(current_town)
            return len(contracts)
        return 0
    
    def _fulfill_selected_contract(self, trade_route_system, player, current_town):
        """Attempt to fulfill the selected contract"""
        contracts = trade_route_system.get_available_contracts_for_player(current_town)
        if 0 <= self.selected_index < len(contracts):
            contract = contracts[self.selected_index]
            # Try to deliver full quantity
            success, message = trade_route_system.fulfill_contract(contract.contract_id, player, contract.quantity)
            logger.info(f"[TRADE UI] Contract fulfillment: {message}")
            return message
        return None
    
    def draw(self, screen, font, trade_route_system, current_town):
        """Draw the trade route UI"""
        if not self.active:
            return
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 900
        panel_height = 700
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw title
        title_text = "Trade Routes & Commerce"
        title_surf = font.render(title_text, True, self.text_color)
        screen.blit(title_surf, (panel_x + 20, panel_y + 15))
        
        # Draw tabs
        tab_y = panel_y + 60
        tab_width = 280
        tab_height = 40
        for i, tab_name in enumerate(self.tabs):
            tab_x = panel_x + 20 + i * (tab_width + 10)
            tab_color = self.tab_active_color if i == self.selected_tab else self.tab_inactive_color
            
            pygame.draw.rect(screen, tab_color, (tab_x, tab_y, tab_width, tab_height))
            pygame.draw.rect(screen, self.text_color, (tab_x, tab_y, tab_width, tab_height), 2)
            
            tab_text = font.render(tab_name, True, self.text_color)
            text_rect = tab_text.get_rect(center=(tab_x + tab_width // 2, tab_y + tab_height // 2))
            screen.blit(tab_text, text_rect)
        
        # Draw content based on selected tab
        content_y = tab_y + tab_height + 20
        content_height = panel_height - (content_y - panel_y) - 20
        
        if self.selected_tab == 0:
            self._draw_routes(screen, font, trade_route_system, panel_x, content_y, panel_width, content_height)
        elif self.selected_tab == 1:
            self._draw_caravans(screen, font, trade_route_system, panel_x, content_y, panel_width, content_height)
        elif self.selected_tab == 2:
            self._draw_contracts(screen, font, trade_route_system, current_town, panel_x, content_y, panel_width, content_height)
        
        # Draw controls hint
        controls_text = "TAB: Switch Tab | UP/DOWN: Navigate | E: Fulfill Contract | ESC: Close"
        controls_surf = font.render(controls_text, True, (180, 180, 180))
        screen.blit(controls_surf, (panel_x + 20, panel_y + panel_height - 35))
    
    def _draw_routes(self, screen, font, trade_route_system, x, y, width, height):
        """Draw trade routes tab"""
        item_height = 80
        y_offset = y + 10 - self.scroll_offset
        
        for i, route in enumerate(trade_route_system.routes):
            if y_offset > y + height:
                break
            if y_offset + item_height < y:
                y_offset += item_height
                continue
            
            # Highlight selected
            if i == self.selected_index:
                pygame.draw.rect(screen, self.highlight_color, (x + 10, y_offset, width - 20, item_height - 5))
            else:
                pygame.draw.rect(screen, self.panel_color, (x + 10, y_offset, width - 20, item_height - 5))
            
            pygame.draw.rect(screen, self.text_color, (x + 10, y_offset, width - 20, item_height - 5), 1)
            
            # Route info
            route_text = f"{route.town_a} ↔ {route.town_b}"
            distance_text = f"Distance: {int(route.distance)} | Travel Time: {route.get_travel_time_days()} days"
            danger_text = f"Danger: {'★' * route.danger_level}{'☆' * (5 - route.danger_level)}"
            caravans_text = f"Active Caravans: {len(route.caravans)} | Volume: {route.trade_volume}g"
            
            text_surf = font.render(route_text, True, (255, 255, 100))
            screen.blit(text_surf, (x + 20, y_offset + 5))
            
            text_surf = font.render(distance_text, True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 30))
            
            text_surf = font.render(f"{danger_text} | {caravans_text}", True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 52))
            
            y_offset += item_height
    
    def _draw_caravans(self, screen, font, trade_route_system, x, y, width, height):
        """Draw caravans tab"""
        item_height = 100
        y_offset = y + 10 - self.scroll_offset
        
        if not trade_route_system.caravans:
            no_data_text = "No active caravans at the moment"
            text_surf = font.render(no_data_text, True, (180, 180, 180))
            screen.blit(text_surf, (x + 20, y + 20))
            return
        
        for i, caravan in enumerate(trade_route_system.caravans):
            if y_offset > y + height:
                break
            if y_offset + item_height < y:
                y_offset += item_height
                continue
            
            # Highlight selected
            if i == self.selected_index:
                pygame.draw.rect(screen, self.highlight_color, (x + 10, y_offset, width - 20, item_height - 5))
            else:
                pygame.draw.rect(screen, self.panel_color, (x + 10, y_offset, width - 20, item_height - 5))
            
            pygame.draw.rect(screen, self.text_color, (x + 10, y_offset, width - 20, item_height - 5), 1)
            
            # Caravan info
            route_text = f"{caravan.caravan_id}: {caravan.origin_town} → {caravan.destination_town}"
            status_text = f"Status: {caravan.status.upper()} | Progress: {int(caravan.travel_progress * 100)}%"
            gold_text = f"Dubloons: {caravan.gold}db | Goods Value: {caravan.goods_value}db"
            
            # List inventory
            inventory_items = []
            for item, qty in caravan.inventory.items():
                inventory_items.append(f"{item}({qty})")
            inventory_text = f"Cargo: {', '.join(inventory_items) if inventory_items else 'Empty'}"
            
            text_surf = font.render(route_text, True, (100, 255, 100))
            screen.blit(text_surf, (x + 20, y_offset + 5))
            
            text_surf = font.render(status_text, True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 30))
            
            text_surf = font.render(gold_text, True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 52))
            
            text_surf = font.render(inventory_text, True, (200, 200, 100))
            screen.blit(text_surf, (x + 20, y_offset + 74))
            
            y_offset += item_height
    
    def _draw_contracts(self, screen, font, trade_route_system, current_town, x, y, width, height):
        """Draw contracts tab"""
        item_height = 120
        y_offset = y + 10 - self.scroll_offset
        
        contracts = trade_route_system.get_available_contracts_for_player(current_town)
        
        if not contracts:
            no_data_text = "No available contracts in this town"
            text_surf = font.render(no_data_text, True, (180, 180, 180))
            screen.blit(text_surf, (x + 20, y + 20))
            return
        
        for i, contract in enumerate(contracts):
            if y_offset > y + height:
                break
            if y_offset + item_height < y:
                y_offset += item_height
                continue
            
            # Highlight selected
            if i == self.selected_index:
                pygame.draw.rect(screen, self.highlight_color, (x + 10, y_offset, width - 20, item_height - 5))
            else:
                pygame.draw.rect(screen, self.panel_color, (x + 10, y_offset, width - 20, item_height - 5))
            
            pygame.draw.rect(screen, self.text_color, (x + 10, y_offset, width - 20, item_height - 5), 1)
            
            # Contract info
            title_text = f"{contract.contract_id}: Deliver {contract.resource_type}"
            route_text = f"{contract.supplier_town} → {contract.buyer_town}"
            quantity_text = f"Quantity: {contract.quantity} @ {contract.price_per_unit}g each = {contract.total_value}g total"
            progress_text = f"Progress: {contract.delivered_quantity}/{contract.quantity} ({contract.get_completion_percentage()}%)"
            deadline_text = f"Deadline: {contract.deadline_days} days | Status: {contract.status.upper()}"
            
            text_surf = font.render(title_text, True, (255, 200, 100))
            screen.blit(text_surf, (x + 20, y_offset + 5))
            
            text_surf = font.render(route_text, True, (150, 200, 255))
            screen.blit(text_surf, (x + 20, y_offset + 28))
            
            text_surf = font.render(quantity_text, True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 50))
            
            text_surf = font.render(progress_text, True, (100, 255, 100))
            screen.blit(text_surf, (x + 20, y_offset + 72))
            
            text_surf = font.render(deadline_text, True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 94))
            
            y_offset += item_height
