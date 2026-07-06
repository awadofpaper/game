"""
Shop Ownership UI - Buy, manage, and upgrade player-owned shops
"""

import pygame


class ShopOwnershipUI:
    """Visual interface for shop ownership system"""
    
    # UI States
    STATE_MAIN_MENU = "main_menu"
    STATE_BROWSE_SHOPS = "browse_shops"
    STATE_MANAGE_SHOPS = "manage_shops"
    STATE_UPGRADE_SHOP = "upgrade_shop"
    STATE_CONFIRM_PURCHASE = "confirm_purchase"
    
    def __init__(self):
        self.active = False
        self.state = self.STATE_MAIN_MENU
        
        # References
        self.shop_ownership_manager = None
        self.player = None
        self.game_time = None
        
        # Selection state
        self.selected_index = 0
        self.selected_shop_id = None
        
        # Message display
        self.message = ""
        self.message_timer = 0
        self.message_color = (255, 255, 255)
        
        # Scrolling
        self.scroll_offset = 0
        self.max_visible_items = 8
        
        # Colors
        self.bg_color = (25, 20, 35)
        self.panel_color = (45, 35, 60)
        self.header_color = (60, 45, 80)
        self.selected_color = (90, 70, 120)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.green_color = (100, 255, 100)
        self.red_color = (255, 100, 100)
        self.gray_color = (150, 150, 150)
        self.accent_color = (150, 120, 200)
        
    def open(self, shop_ownership_manager, player, game_time):
        """Open the shop ownership interface"""
        self.active = True
        self.state = self.STATE_MAIN_MENU
        self.shop_ownership_manager = shop_ownership_manager
        self.player = player
        self.game_time = game_time
        self.selected_index = 0
        self.scroll_offset = 0
        self.message = ""
        
    def close(self):
        """Close the interface"""
        self.active = False
        
    def update(self):
        """Update timers and animations"""
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
                
    def _show_message(self, message: str, color=(255, 255, 255), duration=180):
        """Display a message"""
        self.message = message
        self.message_color = color
        self.message_timer = duration
        
    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.active:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Go back or close
                if self.state == self.STATE_MAIN_MENU:
                    return "close"
                else:
                    self.state = self.STATE_MAIN_MENU
                    self.selected_index = 0
                    self.scroll_offset = 0
                    
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                self._adjust_scroll()
                
            elif event.key == pygame.K_DOWN:
                max_index = self._get_max_index()
                self.selected_index = min(max_index, self.selected_index + 1)
                self._adjust_scroll()
                
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._handle_selection()
                
        return None
        
    def _get_max_index(self):
        """Get maximum selection index for current state"""
        if self.state == self.STATE_MAIN_MENU:
            return 1  # Browse, Manage
        elif self.state == self.STATE_BROWSE_SHOPS:
            return len(self.shop_ownership_manager.available_for_sale) - 1
        elif self.state == self.STATE_MANAGE_SHOPS:
            return len(self.shop_ownership_manager.player_shops) - 1
        elif self.state == self.STATE_UPGRADE_SHOP:
            from shop_ownership_system import ShopUpgrade
            return len(ShopUpgrade.UPGRADES) - 1
        elif self.state == self.STATE_CONFIRM_PURCHASE:
            return 1  # Yes/No
        return 0
        
    def _adjust_scroll(self):
        """Adjust scroll offset to keep selection visible"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1
            
    def _handle_selection(self):
        """Handle Enter/Space key selection"""
        if self.state == self.STATE_MAIN_MENU:
            if self.selected_index == 0:
                # Browse Shops
                self.state = self.STATE_BROWSE_SHOPS
                self.selected_index = 0
                self.scroll_offset = 0
            elif self.selected_index == 1:
                # Manage Shops
                if not self.shop_ownership_manager.player_shops:
                    self._show_message("You don't own any shops yet!", self.red_color)
                else:
                    self.state = self.STATE_MANAGE_SHOPS
                    self.selected_index = 0
                    self.scroll_offset = 0
                    
        elif self.state == self.STATE_BROWSE_SHOPS:
            # Select shop to view details/purchase
            shop_ids = list(self.shop_ownership_manager.available_for_sale.keys())
            if 0 <= self.selected_index < len(shop_ids):
                self.selected_shop_id = shop_ids[self.selected_index]
                self.state = self.STATE_CONFIRM_PURCHASE
                self.selected_index = 0
                
        elif self.state == self.STATE_MANAGE_SHOPS:
            # Select owned shop to manage
            shop_ids = list(self.shop_ownership_manager.player_shops.keys())
            if 0 <= self.selected_index < len(shop_ids):
                self.selected_shop_id = shop_ids[self.selected_index]
                self.state = self.STATE_UPGRADE_SHOP
                self.selected_index = 0
                self.scroll_offset = 0
                
        elif self.state == self.STATE_UPGRADE_SHOP:
            # Purchase upgrade
            from shop_ownership_system import ShopUpgrade
            upgrade_ids = list(ShopUpgrade.UPGRADES.keys())
            
            if 0 <= self.selected_index < len(upgrade_ids):
                upgrade_id = upgrade_ids[self.selected_index]
                success, message = self.shop_ownership_manager.purchase_upgrade(
                    self.selected_shop_id, upgrade_id, self.player
                )
                
                if success:
                    self._show_message(message, self.green_color)
                else:
                    self._show_message(message, self.red_color)
                    
        elif self.state == self.STATE_CONFIRM_PURCHASE:
            if self.selected_index == 0:
                # Yes - Purchase shop
                success, message = self.shop_ownership_manager.purchase_shop(
                    self.selected_shop_id, self.player, self.game_time.day_count
                )
                
                if success:
                    self._show_message(message, self.green_color)
                    self.state = self.STATE_MAIN_MENU
                else:
                    self._show_message(message, self.red_color)
                    self.state = self.STATE_BROWSE_SHOPS
            else:
                # No - Go back
                self.state = self.STATE_BROWSE_SHOPS
                
    def draw(self, screen):
        """Draw the shop ownership interface"""
        if not self.active:
            return
            
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill(self.bg_color)
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 800
        panel_height = 600
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, self.panel_color, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, self.accent_color, 
                        (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Draw content based on state
        if self.state == self.STATE_MAIN_MENU:
            self._draw_main_menu(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_BROWSE_SHOPS:
            self._draw_browse_shops(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_MANAGE_SHOPS:
            self._draw_manage_shops(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_UPGRADE_SHOP:
            self._draw_upgrade_shop(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_CONFIRM_PURCHASE:
            self._draw_confirm_purchase(screen, panel_x, panel_y, panel_width, panel_height)
            
        # Draw message
        if self.message:
            self._draw_message(screen, screen_width, screen_height)
            
    def _draw_main_menu(self, screen, x, y, width, height):
        """Draw main menu"""
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        
        # Title
        title_surf = font_large.render("Shop Ownership", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        # Player's gold
        gold_text = f"Your Dubloons: {self.player.gold}db"
        gold_surf = font_medium.render(gold_text, True, self.gold_color)
        gold_rect = gold_surf.get_rect(centerx=x + width // 2, top=y + 80)
        screen.blit(gold_surf, gold_rect)
        
        # Stats
        owned_count = len(self.shop_ownership_manager.player_shops)
        daily_income = self.shop_ownership_manager.get_total_daily_income()
        
        stats_y = y + 130
        stats_lines = [
            f"Shops Owned: {owned_count}",
            f"Daily Income: {daily_income}g",
            f"Available for Sale: {len(self.shop_ownership_manager.available_for_sale)}"
        ]
        
        for i, line in enumerate(stats_lines):
            surf = font_medium.render(line, True, self.text_color)
            rect = surf.get_rect(centerx=x + width // 2, top=stats_y + i * 35)
            screen.blit(surf, rect)
        
        # Menu options
        menu_y = y + 300
        options = ["Browse Shops for Sale", "Manage Your Shops"]
        
        for i, option in enumerate(options):
            is_selected = (i == self.selected_index)
            color = self.gold_color if is_selected else self.text_color
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 100, menu_y + i * 60 - 5, width - 200, 50)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
            
            surf = font_medium.render(option, True, color)
            rect = surf.get_rect(centerx=x + width // 2, top=menu_y + i * 60)
            screen.blit(surf, rect)
        
        # Controls
        controls_y = y + height - 60
        controls_text = "↑↓: Navigate  ENTER: Select  ESC: Back"
        controls_surf = font_medium.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_browse_shops(self, screen, x, y, width, height):
        """Draw available shops for purchase"""
        font_large = pygame.font.Font(None, 40)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)
        
        # Title
        title_surf = font_large.render("Shops for Sale", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        # Gold
        gold_text = f"Your Dubloons: {self.player.gold}db"
        gold_surf = font_medium.render(gold_text, True, self.gold_color)
        gold_rect = gold_surf.get_rect(right=x + width - 30, top=y + 30)
        screen.blit(gold_surf, gold_rect)
        
        # List shops
        list_y = y + 90
        
        if not self.shop_ownership_manager.available_for_sale:
            no_shops_surf = font_medium.render("No shops available for sale", True, self.gray_color)
            no_shops_rect = no_shops_surf.get_rect(centerx=x + width // 2, top=list_y + 50)
            screen.blit(no_shops_surf, no_shops_rect)
        else:
            shop_ids = list(self.shop_ownership_manager.available_for_sale.keys())
            
            for i, shop_id in enumerate(shop_ids):
                if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible_items:
                    continue
                    
                shop_info = self.shop_ownership_manager.available_for_sale[shop_id]
                is_selected = (i == self.selected_index)
                
                item_y = list_y + (i - self.scroll_offset) * 60
                
                # Selection highlight
                if is_selected:
                    highlight_rect = pygame.Rect(x + 30, item_y - 5, width - 60, 55)
                    pygame.draw.rect(screen, self.selected_color, highlight_rect)
                    pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
                
                # Shop info
                shop_type = shop_info['type'].title()
                shop_name = f"{shop_type} Shop"
                location = shop_info['town']
                price = shop_info['price']
                
                color = self.gold_color if is_selected else self.text_color
                can_afford = self.player.gold >= price
                price_color = self.green_color if can_afford else self.red_color
                
                # Name and location
                name_surf = font_medium.render(f"{shop_name} - {location}", True, color)
                screen.blit(name_surf, (x + 50, item_y))
                
                # Price
                price_surf = font_medium.render(f"{price}g", True, price_color)
                price_rect = price_surf.get_rect(right=x + width - 50, centery=item_y + 15)
                screen.blit(price_surf, price_rect)
                
                # Type description
                type_text = f"Type: {shop_type}"
                type_surf = font_small.render(type_text, True, self.gray_color)
                screen.blit(type_surf, (x + 50, item_y + 30))
        
        # Controls
        controls_y = y + height - 40
        controls_text = "↑↓: Navigate  ENTER: Purchase  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_manage_shops(self, screen, x, y, width, height):
        """Draw player's owned shops"""
        font_large = pygame.font.Font(None, 40)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 22)
        
        # Title
        title_surf = font_large.render("Your Shops", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        # Total income
        total_income = self.shop_ownership_manager.get_total_daily_income()
        income_text = f"Total Daily Income: {total_income}g"
        income_color = self.green_color if total_income > 0 else self.red_color
        income_surf = font_medium.render(income_text, True, income_color)
        income_rect = income_surf.get_rect(right=x + width - 30, top=y + 30)
        screen.blit(income_surf, income_rect)
        
        # List shops
        list_y = y + 90
        
        if not self.shop_ownership_manager.player_shops:
            no_shops_surf = font_medium.render("You don't own any shops", True, self.gray_color)
            no_shops_rect = no_shops_surf.get_rect(centerx=x + width // 2, top=list_y + 50)
            screen.blit(no_shops_surf, no_shops_rect)
        else:
            shop_ids = list(self.shop_ownership_manager.player_shops.keys())
            
            for i, shop_id in enumerate(shop_ids):
                if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible_items:
                    continue
                    
                shop = self.shop_ownership_manager.player_shops[shop_id]
                is_selected = (i == self.selected_index)
                
                item_y = list_y + (i - self.scroll_offset) * 100
                
                # Selection highlight
                if is_selected:
                    highlight_rect = pygame.Rect(x + 30, item_y - 5, width - 60, 95)
                    pygame.draw.rect(screen, self.selected_color, highlight_rect)
                    pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
                
                color = self.gold_color if is_selected else self.text_color
                
                # Shop name and location
                name_surf = font_medium.render(f"{shop.shop_name} - {shop.location}", True, color)
                screen.blit(name_surf, (x + 50, item_y))
                
                # Stats
                profit = shop.daily_revenue - shop.daily_expenses
                profit_color = self.green_color if profit > 0 else self.red_color
                
                stats = [
                    f"Days Owned: {shop.days_owned}",
                    f"Daily Revenue: {shop.daily_revenue}g",
                    f"Daily Expenses: {shop.daily_expenses}g",
                    f"Daily Profit: {profit}g"
                ]
                
                for j, stat in enumerate(stats[:2]):
                    stat_surf = font_small.render(stat, True, self.gray_color)
                    screen.blit(stat_surf, (x + 50, item_y + 30 + j * 22))
                
                # Profit (highlighted)
                profit_surf = font_small.render(stats[3], True, profit_color)
                screen.blit(profit_surf, (x + 50, item_y + 74))
                
                # Upgrades count
                upgrade_text = f"Upgrades: {len(shop.upgrades)}/8"
                upgrade_surf = font_small.render(upgrade_text, True, self.accent_color)
                upgrade_rect = upgrade_surf.get_rect(right=x + width - 50, centery=item_y + 40)
                screen.blit(upgrade_surf, upgrade_rect)
        
        # Controls
        controls_y = y + height - 40
        controls_text = "↑↓: Navigate  ENTER: Manage  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_upgrade_shop(self, screen, x, y, width, height):
        """Draw upgrade menu for a specific shop"""
        from shop_ownership_system import ShopUpgrade
        
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        # Get shop
        shop = self.shop_ownership_manager.player_shops.get(self.selected_shop_id)
        if not shop:
            return
        
        # Title
        title_surf = font_large.render(f"{shop.shop_name} - Upgrades", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 15)
        screen.blit(title_surf, title_rect)
        
        # Gold
        gold_text = f"Your Dubloons: {self.player.gold}db"
        gold_surf = font_medium.render(gold_text, True, self.gold_color)
        gold_rect = gold_surf.get_rect(right=x + width - 30, top=y + 20)
        screen.blit(gold_surf, gold_rect)
        
        # Shop stats
        stats_y = y + 55
        profit = shop.daily_revenue - shop.daily_expenses
        profit_color = self.green_color if profit > 0 else self.red_color
        
        stats_text = f"Daily Profit: {profit}g  |  Upgrades: {len(shop.upgrades)}/8"
        stats_surf = font_small.render(stats_text, True, self.text_color)
        stats_rect = stats_surf.get_rect(centerx=x + width // 2, top=stats_y)
        screen.blit(stats_surf, stats_rect)
        
        # Upgrades list
        list_y = y + 95
        upgrade_ids = list(ShopUpgrade.UPGRADES.keys())
        
        for i, upgrade_id in enumerate(upgrade_ids):
            if i < self.scroll_offset or i >= self.scroll_offset + 6:
                continue
                
            upgrade = ShopUpgrade.UPGRADES[upgrade_id]
            is_selected = (i == self.selected_index)
            has_upgrade = upgrade_id in shop.upgrades
            can_afford = self.player.gold >= upgrade['cost']
            
            item_y = list_y + (i - self.scroll_offset) * 75
            
            # Selection highlight
            if is_selected and not has_upgrade:
                highlight_rect = pygame.Rect(x + 30, item_y - 5, width - 60, 70)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
            
            # Gray out if owned
            if has_upgrade:
                color = self.gray_color
                status_text = "[OWNED]"
                status_color = self.green_color
            elif is_selected:
                color = self.gold_color
                status_text = ""
                status_color = self.text_color
            else:
                color = self.text_color
                status_text = ""
                status_color = self.text_color
            
            # Name
            name_text = f"{upgrade['name']}"
            if status_text:
                name_text = f"{status_text} {name_text}"
            name_surf = font_medium.render(name_text, True, color)
            screen.blit(name_surf, (x + 50, item_y))
            
            # Description
            desc_surf = font_small.render(upgrade['description'], True, self.gray_color)
            screen.blit(desc_surf, (x + 50, item_y + 28))
            
            # Cost
            if not has_upgrade:
                cost_color = self.green_color if can_afford else self.red_color
                cost_surf = font_medium.render(f"{upgrade['cost']}g", True, cost_color)
                cost_rect = cost_surf.get_rect(right=x + width - 50, centery=item_y + 20)
                screen.blit(cost_surf, cost_rect)
        
        # Controls
        controls_y = y + height - 40
        controls_text = "↑↓: Navigate  ENTER: Purchase  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_confirm_purchase(self, screen, x, y, width, height):
        """Draw purchase confirmation dialog"""
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 28)
        
        # Get shop info
        shop_info = self.shop_ownership_manager.available_for_sale.get(self.selected_shop_id)
        if not shop_info:
            return
        
        # Title
        title_surf = font_large.render("Confirm Purchase", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 50)
        screen.blit(title_surf, title_rect)
        
        # Shop details
        shop_type = shop_info['type'].title()
        location = shop_info['town']
        price = shop_info['price']
        
        details_y = y + 150
        details = [
            f"Shop Type: {shop_type}",
            f"Location: {location}",
            f"Price: {price}db",
            "",
            f"Your Dubloons: {self.player.gold}db",
            f"After Purchase: {self.player.gold - price}db"
        ]
        
        for i, line in enumerate(details):
            if line:
                surf = font_medium.render(line, True, self.text_color)
                rect = surf.get_rect(centerx=x + width // 2, top=details_y + i * 35)
                screen.blit(surf, rect)
        
        # Confirmation buttons
        buttons_y = y + 420
        options = ["Yes, Purchase", "No, Cancel"]
        
        for i, option in enumerate(options):
            is_selected = (i == self.selected_index)
            
            button_x = x + 200 + i * 250
            button_rect = pygame.Rect(button_x - 80, buttons_y - 10, 160, 50)
            
            if is_selected:
                pygame.draw.rect(screen, self.selected_color, button_rect)
                pygame.draw.rect(screen, self.gold_color, button_rect, 2)
                color = self.gold_color
            else:
                pygame.draw.rect(screen, self.header_color, button_rect)
                pygame.draw.rect(screen, self.gray_color, button_rect, 2)
                color = self.text_color
            
            surf = font_medium.render(option, True, color)
            rect = surf.get_rect(center=button_rect.center)
            screen.blit(surf, rect)
        
        # Warning if can't afford
        if self.player.gold < price:
            warning_surf = font_medium.render("Not enough dubloons!", True, self.red_color)
            warning_rect = warning_surf.get_rect(centerx=x + width // 2, top=buttons_y + 80)
            screen.blit(warning_surf, warning_rect)
        
    def _draw_message(self, screen, screen_width, screen_height):
        """Draw message overlay"""
        font = pygame.font.Font(None, 32)
        
        # Message background
        msg_surf = font.render(self.message, True, self.message_color)
        msg_width = msg_surf.get_width() + 40
        msg_height = 60
        msg_x = (screen_width - msg_width) // 2
        msg_y = screen_height - 150
        
        pygame.draw.rect(screen, self.panel_color, (msg_x, msg_y, msg_width, msg_height))
        pygame.draw.rect(screen, self.message_color, (msg_x, msg_y, msg_width, msg_height), 2)
        
        msg_rect = msg_surf.get_rect(center=(screen_width // 2, msg_y + msg_height // 2))
        screen.blit(msg_surf, msg_rect)
