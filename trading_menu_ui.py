"""
Comprehensive Trading UI System
Black Market, Special Orders, Merchant Quests, Loyalty Status, Traveling Merchants
"""

import pygame
from typing import Optional


class TradingMenuUI:
    """Unified trading menu with access to all trading features"""
    
    def __init__(self):
        self.active = False
        self.state = "main"  # main, black_market, orders, quests, loyalty
        self.selected_index = 0
        
        # System references
        self.smuggling_system = None
        self.special_order_manager = None
        self.merchant_quest_manager = None
        self.caravan_manager = None
        self.reputation_manager = None
        self.player = None
        self.game_time = None
        self.current_merchant_id = None
        
        # Black market state
        self.password_input = ""
        self.selected_vendor_id = None
        self.password_attempts = 0
        self.vendor_unlocked = False
        
        # Message
        self.message = ""
        self.message_timer = 0
        self.message_color = (255, 255, 255)
        
        # Scrolling
        self.scroll_offset = 0
        self.max_visible = 8
        
        # Colors
        self.bg_color = (15, 10, 25)
        self.panel_color = (35, 25, 50)
        self.header_color = (55, 40, 75)
        self.selected_color = (80, 60, 110)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.green_color = (100, 255, 100)
        self.red_color = (255, 100, 100)
        self.gray_color = (150, 150, 150)
        self.accent_color = (180, 120, 220)
        self.danger_color = (200, 50, 50)
        
    def open(self, smuggling_system=None, special_order_manager=None, 
             merchant_quest_manager=None, caravan_manager=None, 
             reputation_manager=None, player=None, game_time=None,
             merchant_id=None):
        """Open the trading menu"""
        self.active = True
        self.state = "main"
        self.smuggling_system = smuggling_system
        self.special_order_manager = special_order_manager
        self.merchant_quest_manager = merchant_quest_manager
        self.caravan_manager = caravan_manager
        self.reputation_manager = reputation_manager
        self.player = player
        self.game_time = game_time
        self.current_merchant_id = merchant_id
        self.selected_index = 0
        self.scroll_offset = 0
        
    def close(self):
        """Close the menu"""
        self.active = False
        self.password_input = ""
        self.vendor_unlocked = False
        
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
        
    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.active:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == "main":
                    return "close"
                else:
                    # Go back to main menu
                    self.state = "main"
                    self.selected_index = 0
                    self.password_input = ""
                    self.vendor_unlocked = False
                    
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                self._adjust_scroll()
                
            elif event.key == pygame.K_DOWN:
                max_index = self._get_max_index()
                self.selected_index = min(max_index, self.selected_index + 1)
                self._adjust_scroll()
                
            elif event.key == pygame.K_RETURN:
                self._handle_selection()
                
            elif self.state == "black_market" and not self.vendor_unlocked:
                # Password input
                if event.key == pygame.K_BACKSPACE:
                    self.password_input = self.password_input[:-1]
                elif event.unicode.isprintable():
                    self.password_input += event.unicode
                    
        return None
        
    def _get_max_index(self):
        """Get maximum index for current state"""
        if self.state == "main":
            return 4  # 5 options
        elif self.state == "black_market":
            if not self.smuggling_system:
                return 0
            return len(self.smuggling_system.black_market_vendors) - 1
        elif self.state == "orders":
            if not self.special_order_manager:
                return 0
            return len(self.special_order_manager.active_orders) - 1
        elif self.state == "quests":
            if not self.merchant_quest_manager:
                return 0
            return len(self.merchant_quest_manager.active_quests) - 1
        elif self.state == "loyalty":
            if not self.merchant_quest_manager:
                return 0
            return len(self.merchant_quest_manager.loyalty_programs) - 1
        return 0
        
    def _adjust_scroll(self):
        """Adjust scroll to keep selection visible"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible:
            self.scroll_offset = self.selected_index - self.max_visible + 1
            
    def _handle_selection(self):
        """Handle Enter key selection"""
        if self.state == "main":
            options = ["black_market", "orders", "quests", "loyalty", "merchants"]
            if self.selected_index < len(options):
                self.state = options[self.selected_index]
                self.selected_index = 0
                self.scroll_offset = 0
                
        elif self.state == "black_market":
            if not self.vendor_unlocked:
                # Try password
                vendors = list(self.smuggling_system.black_market_vendors.values())
                if 0 <= self.selected_index < len(vendors):
                    vendor = vendors[self.selected_index]
                    if vendor.check_password(self.password_input):
                        self.vendor_unlocked = True
                        vendor.discovered = True
                        self._show_message(f"Access granted to {vendor.name}!", self.green_color)
                    else:
                        self.password_attempts += 1
                        self._show_message("Incorrect password!", self.red_color)
                        self.password_input = ""
                        
        elif self.state == "orders":
            # Collect completed orders
            orders = list(self.special_order_manager.active_orders.values())
            if 0 <= self.selected_index < len(orders):
                order = orders[self.selected_index]
                if order.is_ready and self.player.dubloons >= order.remaining_payment:
                    success, message = self.special_order_manager.collect_order(
                        order.order_id, self.player
                    )
                    color = self.green_color if success else self.red_color
                    self._show_message(message, color)
                    
        elif self.state == "quests":
            # Accept or complete quest
            quests = list(self.merchant_quest_manager.active_quests.values())
            if 0 <= self.selected_index < len(quests):
                quest = quests[self.selected_index]
                if quest.check_completion():
                    success, message = self.merchant_quest_manager.complete_quest(
                        quest.quest_id, self.player, self.reputation_manager
                    )
                    color = self.green_color if success else self.red_color
                    self._show_message(message, color)
                    
    def draw(self, screen):
        """Draw the trading menu"""
        if not self.active:
            return
            
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill(self.bg_color)
        overlay.set_alpha(230)
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
        if self.state == "main":
            self._draw_main_menu(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == "black_market":
            self._draw_black_market(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == "orders":
            self._draw_special_orders(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == "quests":
            self._draw_merchant_quests(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == "loyalty":
            self._draw_loyalty_status(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == "merchants":
            self._draw_traveling_merchants(screen, panel_x, panel_y, panel_width, panel_height)
            
        # Draw message
        if self.message:
            self._draw_message(screen, screen_width, screen_height)
            
    def _draw_main_menu(self, screen, x, y, width, height):
        """Draw main trading menu"""
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        
        # Title
        title_surf = font_large.render("Trading Network", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        # Menu options
        menu_y = y + 120
        options = [
            ("🔒 Black Market", "Access hidden contraband vendors"),
            ("📋 Special Orders", "View active bulk orders and commissions"),
            ("⚔️ Merchant Quests", "Browse delivery and escort missions"),
            ("⭐ Loyalty Status", "Check your standing with merchants"),
            ("🚐 Traveling Merchants", "See visiting exotic traders")
        ]
        
        for i, (option, desc) in enumerate(options):
            is_selected = (i == self.selected_index)
            item_y = menu_y + i * 85
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 50, item_y - 5, width - 100, 75)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
            
            color = self.gold_color if is_selected else self.text_color
            
            # Option name
            option_surf = font_medium.render(option, True, color)
            screen.blit(option_surf, (x + 70, item_y))
            
            # Description
            desc_font = pygame.font.Font(None, 22)
            desc_surf = desc_font.render(desc, True, self.gray_color)
            screen.blit(desc_surf, (x + 70, item_y + 35))
        
        # Controls
        controls_y = y + height - 40
        controls_font = pygame.font.Font(None, 24)
        controls_text = "↑↓: Navigate  ENTER: Select  ESC: Close"
        controls_surf = controls_font.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_black_market(self, screen, x, y, width, height):
        """Draw black market access screen"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)
        
        # Title
        title_surf = font_large.render("🔒 Black Market Access", True, self.danger_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        if not self.smuggling_system or not self.smuggling_system.black_market_vendors:
            no_vendors_surf = font_medium.render("No black market contacts found", True, self.gray_color)
            no_vendors_rect = no_vendors_surf.get_rect(centerx=x + width // 2, top=y + 150)
            screen.blit(no_vendors_surf, no_vendors_rect)
            return
        
        # List vendors
        list_y = y + 90
        vendors = list(self.smuggling_system.black_market_vendors.values())
        
        for i, vendor in enumerate(vendors):
            if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible:
                continue
                
            is_selected = (i == self.selected_index)
            item_y = list_y + (i - self.scroll_offset) * 80
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 30, item_y - 5, width - 60, 75)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.danger_color, highlight_rect, 2)
            
            color = self.danger_color if is_selected else self.text_color
            
            # Vendor name and location
            name_text = f"{'[DISCOVERED]' if vendor.discovered else '[HIDDEN]'} {vendor.name}"
            name_surf = font_medium.render(name_text, True, color)
            screen.blit(name_surf, (x + 50, item_y))
            
            # Location hint
            location_surf = font_small.render(f"Location: {vendor.location}", True, self.gray_color)
            screen.blit(location_surf, (x + 50, item_y + 32))
            
            # Specialization
            spec_surf = font_small.render(f"Specialty: {vendor.specializes_in}", True, self.accent_color)
            screen.blit(spec_surf, (x + 50, item_y + 54))
        
        # Password input area (bottom of panel)
        if self.selected_index < len(vendors):
            input_y = y + height - 150
            
            # Password prompt
            prompt_surf = font_medium.render("Enter Password:", True, self.gold_color)
            screen.blit(prompt_surf, (x + 50, input_y))
            
            # Input box
            input_box = pygame.Rect(x + 50, input_y + 40, width - 100, 50)
            pygame.draw.rect(screen, self.header_color, input_box)
            pygame.draw.rect(screen, self.accent_color, input_box, 2)
            
            # Password text (masked)
            masked_text = "*" * len(self.password_input)
            input_surf = font_medium.render(masked_text, True, self.text_color)
            screen.blit(input_surf, (x + 60, input_y + 50))
            
            # Hint
            if self.password_attempts > 0:
                hint_surf = font_small.render(f"Failed attempts: {self.password_attempts}", True, self.red_color)
                screen.blit(hint_surf, (x + 50, input_y + 100))
        
        # Controls
        controls_y = y + height - 40
        controls_text = "↑↓: Select  Type Password  ENTER: Submit  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_special_orders(self, screen, x, y, width, height):
        """Draw special orders tracker"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        # Title
        title_surf = font_large.render("📋 Special Orders & Commissions", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        if not self.special_order_manager or not self.special_order_manager.active_orders:
            no_orders_surf = font_medium.render("No active special orders", True, self.gray_color)
            no_orders_rect = no_orders_surf.get_rect(centerx=x + width // 2, top=y + 150)
            screen.blit(no_orders_surf, no_orders_rect)
            return
        
        # List orders
        list_y = y + 85
        orders = list(self.special_order_manager.active_orders.values())
        
        for i, order in enumerate(orders):
            if i < self.scroll_offset or i >= self.scroll_offset + 6:
                continue
                
            is_selected = (i == self.selected_index)
            item_y = list_y + (i - self.scroll_offset) * 85
            
            # Selection highlight
            if is_selected and order.is_ready:
                highlight_rect = pygame.Rect(x + 30, item_y - 5, width - 60, 80)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.green_color, highlight_rect, 2)
            
            # Order info
            name_color = self.green_color if order.is_ready else self.gold_color
            name_text = f"{order.item_name} x{order.quantity}"
            if order.is_ready:
                name_text += " [READY]"
            name_surf = font_medium.render(name_text, True, name_color)
            screen.blit(name_surf, (x + 50, item_y))
            
            # Merchant and price
            merchant_surf = font_small.render(f"Merchant: {order.merchant_name}", True, self.text_color)
            screen.blit(merchant_surf, (x + 50, item_y + 28))
            
            price_text = f"Remaining: {order.remaining_payment}g (Deposit: {order.deposit}g)"
            price_surf = font_small.render(price_text, True, self.gold_color)
            screen.blit(price_surf, (x + 50, item_y + 50))
            
            # Days remaining or ready status
            if order.is_ready:
                status_surf = font_small.render("✓ Ready for pickup!", True, self.green_color)
            else:
                days = order.days_until_ready(self.game_time.day_count)
                status_surf = font_small.render(f"⏰ {days} days remaining", True, self.accent_color)
            status_rect = status_surf.get_rect(right=x + width - 50, centery=item_y + 40)
            screen.blit(status_surf, status_rect)
        
        # Controls
        controls_y = y + height - 40
        controls_text = "↑↓: Navigate  ENTER: Collect (if ready)  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_merchant_quests(self, screen, x, y, width, height):
        """Draw merchant quest board"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        
        # Title
        title_surf = font_large.render("⚔️ Merchant Quest Board", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        if not self.merchant_quest_manager or not self.merchant_quest_manager.active_quests:
            no_quests_surf = font_medium.render("No active quests available", True, self.gray_color)
            no_quests_rect = no_quests_surf.get_rect(centerx=x + width // 2, top=y + 150)
            screen.blit(no_quests_surf, no_quests_rect)
            return
        
        # List quests
        list_y = y + 85
        quests = list(self.merchant_quest_manager.active_quests.values())
        
        for i, quest in enumerate(quests):
            if i < self.scroll_offset or i >= self.scroll_offset + 5:
                continue
                
            is_selected = (i == self.selected_index)
            is_complete = quest.check_completion()
            item_y = list_y + (i - self.scroll_offset) * 105
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 30, item_y - 5, width - 60, 100)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                color_border = self.green_color if is_complete else self.gold_color
                pygame.draw.rect(screen, color_border, highlight_rect, 2)
            
            # Quest type icon and name
            icons = {'delivery': '📦', 'gathering': '🌾', 'protection': '🛡️', 'retrieval': '🔍'}
            icon = icons.get(quest.quest_type, '❓')
            title_text = f"{icon} {quest.quest_type.title()} Quest"
            if is_complete:
                title_text += " [COMPLETE]"
            title_color = self.green_color if is_complete else self.gold_color
            title_surf = font_medium.render(title_text, True, title_color)
            screen.blit(title_surf, (x + 50, item_y))
            
            # Merchant
            merchant_surf = font_small.render(f"From: {quest.merchant_name}", True, self.text_color)
            screen.blit(merchant_surf, (x + 50, item_y + 28))
            
            # Description
            desc_surf = font_small.render(quest.description[:60], True, self.gray_color)
            screen.blit(desc_surf, (x + 50, item_y + 48))
            
            # Rewards
            reward_text = f"💰 {quest.reward_gold}g  ⭐ {quest.reputation_reward} rep"
            reward_surf = font_small.render(reward_text, True, self.accent_color)
            screen.blit(reward_surf, (x + 50, item_y + 70))
            
            # Deadline
            deadline_surf = font_small.render(f"⏰ Day {quest.deadline_day}", True, self.red_color)
            deadline_rect = deadline_surf.get_rect(right=x + width - 50, centery=item_y + 40)
            screen.blit(deadline_surf, deadline_rect)
        
        # Controls
        controls_y = y + height - 40
        controls_text = "↑↓: Navigate  ENTER: Complete (if done)  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_loyalty_status(self, screen, x, y, width, height):
        """Draw loyalty program status"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 22)
        
        # Title
        title_surf = font_large.render("⭐ Merchant Loyalty Programs", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        if not self.merchant_quest_manager or not self.merchant_quest_manager.loyalty_programs:
            no_loyalty_surf = font_medium.render("No loyalty programs active", True, self.gray_color)
            no_loyalty_rect = no_loyalty_surf.get_rect(centerx=x + width // 2, top=y + 150)
            screen.blit(no_loyalty_surf, no_loyalty_rect)
            return
        
        # List loyalty programs
        list_y = y + 85
        programs = list(self.merchant_quest_manager.loyalty_programs.items())
        
        for i, (merchant_id, program) in enumerate(programs):
            if i < self.scroll_offset or i >= self.scroll_offset + 6:
                continue
                
            item_y = list_y + (i - self.scroll_offset) * 85
            tier = program.get_tier()
            
            # Box
            box_rect = pygame.Rect(x + 40, item_y, width - 80, 78)
            pygame.draw.rect(screen, self.header_color, box_rect)
            pygame.draw.rect(screen, self.accent_color, box_rect, 2)
            
            # Merchant and tier
            merchant_text = f"{merchant_id} - {tier['name']}"
            merchant_surf = font_medium.render(merchant_text, True, self.gold_color)
            screen.blit(merchant_surf, (x + 55, item_y + 8))
            
            # Progress
            progress_text = f"Purchases: {program.purchase_count}  |  Total Spent: {program.total_spent}g"
            progress_surf = font_small.render(progress_text, True, self.text_color)
            screen.blit(progress_surf, (x + 55, item_y + 36))
            
            # Discount and points
            discount_text = f"Discount: {int(tier['discount'] * 100)}%  |  Points: {program.points}"
            discount_surf = font_small.render(discount_text, True, self.green_color)
            screen.blit(discount_surf, (x + 55, item_y + 56))
        
        # Controls
        controls_y = y + height - 40
        controls_text = "↑↓: Navigate  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_traveling_merchants(self, screen, x, y, width, height):
        """Draw traveling merchant schedule"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)
        
        # Title
        title_surf = font_large.render("🚐 Traveling Merchants", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        if not self.caravan_manager or not self.caravan_manager.traveling_merchants:
            no_merchants_surf = font_medium.render("No traveling merchants tracked", True, self.gray_color)
            no_merchants_rect = no_merchants_surf.get_rect(centerx=x + width // 2, top=y + 150)
            screen.blit(no_merchants_surf, no_merchants_rect)
            return
        
        # List merchants
        list_y = y + 90
        merchants = list(self.caravan_manager.traveling_merchants.values())
        
        for i, merchant in enumerate(merchants):
            if i < self.scroll_offset or i >= self.scroll_offset + 6:
                continue
                
            item_y = list_y + (i - self.scroll_offset) * 85
            
            # Box
            box_rect = pygame.Rect(x + 40, item_y, width - 80, 78)
            pygame.draw.rect(screen, self.header_color, box_rect)
            pygame.draw.rect(screen, self.accent_color, box_rect, 2)
            
            # Merchant name and specialty
            name_text = f"🚐 {merchant.name} - {merchant.specialty.title()}"
            name_surf = font_medium.render(name_text, True, self.gold_color)
            screen.blit(name_surf, (x + 55, item_y + 8))
            
            # Current location or schedule
            if merchant.current_town:
                location_text = f"📍 Currently in: {merchant.current_town}"
                location_color = self.green_color
                
                days_left = merchant.stay_duration - (self.game_time.day_count - merchant.arrival_day)
                if days_left > 0:
                    location_text += f" ({days_left} days left)"
            elif merchant.next_town:
                days_until = merchant.arrival_day - self.game_time.day_count
                location_text = f"⏰ Arriving in {merchant.next_town} in {days_until} days"
                location_color = self.accent_color
            else:
                location_text = "🗺️ Route unknown"
                location_color = self.gray_color
                
            location_surf = font_small.render(location_text, True, location_color)
            screen.blit(location_surf, (x + 55, item_y + 40))
        
        # Controls
        controls_y = y + height - 40
        controls_text = "↑↓: Navigate  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
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
