"""
Advanced Trading UI
Access to Quality/Condition, Time-Based Sales, Appraisal, Consignment/Auction
"""

import pygame
from typing import Optional


class AdvancedTradingUI:
    """Unified UI for advanced trading features"""
    
    # UI states
    STATE_MAIN_MENU = "main"
    STATE_CLEARANCE = "clearance"
    STATE_MARKET_EVENTS = "events"
    STATE_APPRAISAL = "appraisal"
    STATE_CONSIGNMENT = "consignment"
    STATE_AUCTION_BROWSE = "auction_browse"
    STATE_AUCTION_CREATE = "auction_create"
    STATE_MY_LISTINGS = "my_listings"
    
    def __init__(self):
        self.active = False
        self.state = self.STATE_MAIN_MENU
        
        # System references
        self.quality_manager = None
        self.time_sales_manager = None
        self.appraisal_system = None
        self.consignment_manager = None
        self.player = None
        self.game_time = None
        self.current_shop_id = None
        
        # Selection state
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible = 6
        
        # Input state
        self.input_mode = None  # 'price', 'quantity', 'buyout', 'days'
        self.input_value = ""
        self.temp_item_data = {}
        
        # Message
        self.message = ""
        self.message_timer = 0
        self.message_color = (255, 255, 255)
        
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
        
    def open(self, quality_manager, time_sales_manager, appraisal_system,
             consignment_manager, player, game_time, shop_id=None):
        """Open the advanced trading UI"""
        self.active = True
        self.quality_manager = quality_manager
        self.time_sales_manager = time_sales_manager
        self.appraisal_system = appraisal_system
        self.consignment_manager = consignment_manager
        self.player = player
        self.game_time = game_time
        self.current_shop_id = shop_id
        self.state = self.STATE_MAIN_MENU
        self.selected_index = 0
        self.scroll_offset = 0
        
    def close(self):
        """Close the UI"""
        self.active = False
        
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
            # Input mode for entering values
            if self.input_mode:
                if event.key == pygame.K_RETURN:
                    self._confirm_input()
                elif event.key == pygame.K_ESCAPE:
                    self.input_mode = None
                    self.input_value = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.input_value = self.input_value[:-1]
                elif event.unicode.isdigit():
                    self.input_value += event.unicode
                return None
                
            # Normal navigation
            if event.key == pygame.K_ESCAPE:
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
                
            elif event.key == pygame.K_RETURN:
                self._handle_selection()
                
        return None
        
    def _get_max_index(self):
        """Get maximum index for current state"""
        if self.state == self.STATE_MAIN_MENU:
            return 4  # 5 main options
        elif self.state == self.STATE_CLEARANCE:
            if not self.current_shop_id or not self.quality_manager:
                return 0
            items = self.quality_manager.get_clearance_items(self.current_shop_id)
            return max(0, len(items) - 1)
        elif self.state == self.STATE_APPRAISAL:
            if not self.appraisal_system:
                return 0
            items = list(self.appraisal_system.unidentified_items.keys())
            return max(0, len(items) - 1)
        elif self.state == self.STATE_AUCTION_BROWSE:
            if not self.consignment_manager:
                return 0
            auctions = self.consignment_manager.get_active_auctions()
            return max(0, len(auctions) - 1)
        elif self.state == self.STATE_MY_LISTINGS:
            if not self.consignment_manager:
                return 0
            consignments = self.consignment_manager.get_player_consignments()
            auctions = self.consignment_manager.get_player_auctions()
            return max(0, len(consignments) + len(auctions) - 1)
        return 0
        
    def _adjust_scroll(self):
        """Adjust scroll to keep selection visible"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible:
            self.scroll_offset = self.selected_index - self.max_visible + 1
            
    def _handle_selection(self):
        """Handle Enter key selection"""
        if self.state == self.STATE_MAIN_MENU:
            options = [
                self.STATE_CLEARANCE,
                self.STATE_MARKET_EVENTS,
                self.STATE_APPRAISAL,
                self.STATE_CONSIGNMENT,
                self.STATE_AUCTION_BROWSE
            ]
            if self.selected_index < len(options):
                self.state = options[self.selected_index]
                self.selected_index = 0
                self.scroll_offset = 0
                
        elif self.state == self.STATE_CLEARANCE:
            # Buy clearance item
            items = self.quality_manager.get_clearance_items(self.current_shop_id)
            if 0 <= self.selected_index < len(items):
                item = items[self.selected_index]
                condition = self.quality_manager.get_condition(item['instance_id'])
                price = self.quality_manager.calculate_price(item['base_price'], item['instance_id'])
                
                if self.player.dubloons >= price:
                    self.player.dubloons -= price
                    # Add to player inventory
                    self.player.inventory[item['item_id']] = self.player.inventory.get(item['item_id'], 0) + 1
                    items.remove(item)
                    self._show_message(f"Bought {item['item_id']} ({condition.get_name()}) for {price}g", self.green_color)
                else:
                    self._show_message("Not enough dubloons!", self.red_color)
                    
        elif self.state == self.STATE_APPRAISAL:
            # Appraise item
            items = list(self.appraisal_system.unidentified_items.keys())
            if 0 <= self.selected_index < len(items):
                instance_id = items[self.selected_index]
                success, name, value = self.appraisal_system.appraise_item(instance_id, self.player)
                if success:
                    self._show_message(f"Identified: {name} (worth {value}g)", self.green_color)
                else:
                    self._show_message(name, self.red_color)
                    
        elif self.state == self.STATE_CONSIGNMENT:
            # Start consignment - need to select item from inventory
            if hasattr(self.player, 'inventory') and self.player.inventory:
                items = list(self.player.inventory.items())
                if 0 <= self.selected_index < len(items):
                    item_id, quantity = items[self.selected_index]
                    if quantity > 0:
                        self.temp_item_data = {'item_id': item_id, 'quantity': quantity}
                        self.input_mode = 'price'
                        self.input_value = ""
                        self._show_message(f"Enter asking price per {item_id}", self.accent_color)
                        
        elif self.state == self.STATE_AUCTION_BROWSE:
            # Bid on auction
            auctions = self.consignment_manager.get_active_auctions()
            if 0 <= self.selected_index < len(auctions):
                auction = auctions[self.selected_index]
                # Simple bid logic - bid current + 50g
                bid_amount = auction.current_bid + 50
                if self.player.dubloons >= bid_amount:
                    success, msg = auction.place_bid('player', bid_amount)
                    if success:
                        self.player.dubloons -= bid_amount
                        self._show_message(msg, self.green_color)
                    else:
                        self._show_message(msg, self.red_color)
                else:
                    self._show_message("Not enough dubloons to bid!", self.red_color)
                    
    def _confirm_input(self):
        """Confirm input value"""
        if not self.input_value:
            self.input_mode = None
            return
            
        try:
            value = int(self.input_value)
            
            if self.input_mode == 'price':
                # Store price, ask for quantity
                self.temp_item_data['price'] = value
                self.input_mode = 'quantity'
                self.input_value = ""
                self._show_message("Enter quantity to list", self.accent_color)
                
            elif self.input_mode == 'quantity':
                # Create consignment
                quantity = min(value, self.temp_item_data['quantity'])
                if quantity > 0:
                    msg = self.consignment_manager.add_consignment(
                        self.temp_item_data['item_id'],
                        self.temp_item_data['item_id'],
                        quantity,
                        self.temp_item_data['price'],
                        self.current_shop_id or 'general_store'
                    )
                    # Remove from inventory
                    self.player.inventory[self.temp_item_data['item_id']] -= quantity
                    self._show_message(msg, self.green_color)
                    
                self.input_mode = None
                self.temp_item_data = {}
                self.state = self.STATE_MY_LISTINGS
                
        except ValueError:
            self._show_message("Invalid number!", self.red_color)
            
        self.input_value = ""
        
    def draw(self, screen):
        """Draw the UI"""
        if not self.active:
            return
            
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill(self.bg_color)
        overlay.set_alpha(220)
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 900
        panel_height = 650
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, self.panel_color,
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, self.accent_color,
                        (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Draw based on state
        if self.state == self.STATE_MAIN_MENU:
            self._draw_main_menu(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_CLEARANCE:
            self._draw_clearance(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_MARKET_EVENTS:
            self._draw_market_events(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_APPRAISAL:
            self._draw_appraisal(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_CONSIGNMENT:
            self._draw_consignment(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_AUCTION_BROWSE:
            self._draw_auction_browse(screen, panel_x, panel_y, panel_width, panel_height)
        elif self.state == self.STATE_MY_LISTINGS:
            self._draw_my_listings(screen, panel_x, panel_y, panel_width, panel_height)
            
        # Message
        if self.message:
            self._draw_message(screen, screen_width, screen_height)
            
        # Input overlay
        if self.input_mode:
            self._draw_input_overlay(screen, screen_width, screen_height)
            
    def _draw_main_menu(self, screen, x, y, width, height):
        """Draw main menu"""
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 30)
        font_small = pygame.font.Font(None, 22)
        
        # Title
        title_surf = font_large.render("Advanced Trading", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 20)
        screen.blit(title_surf, title_rect)
        
        # Menu options
        menu_y = y + 100
        options = [
            ("🔖 Clearance Bin", "Browse damaged goods at discount prices"),
            ("🕐 Market Events", "Check active time-based market specials"),
            ("🔍 Item Appraisal", "Identify mysterious items (10g per item)"),
            ("📦 Consignment", "List items for sale over time (15% commission)"),
            ("⚖️ Auction House", "Browse and bid on auctions")
        ]
        
        for i, (title, desc) in enumerate(options):
            is_selected = (i == self.selected_index)
            item_y = menu_y + i * 90
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 40, item_y - 5, width - 80, 80)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
            
            color = self.gold_color if is_selected else self.text_color
            
            # Title
            title_surf = font_medium.render(title, True, color)
            screen.blit(title_surf, (x + 60, item_y))
            
            # Description
            desc_surf = font_small.render(desc, True, self.gray_color)
            screen.blit(desc_surf, (x + 60, item_y + 35))
            
        # Show uncollected proceeds
        if self.consignment_manager and self.consignment_manager.player_proceeds > 0:
            proceeds_y = y + height - 80
            proceeds_text = f"💰 Uncollected Proceeds: {self.consignment_manager.player_proceeds}g"
            proceeds_surf = font_medium.render(proceeds_text, True, self.green_color)
            proceeds_rect = proceeds_surf.get_rect(centerx=x + width // 2, top=proceeds_y)
            screen.blit(proceeds_surf, proceeds_rect)
            
            collect_text = "Press C to collect"
            collect_surf = font_small.render(collect_text, True, self.gray_color)
            collect_rect = collect_surf.get_rect(centerx=x + width // 2, top=proceeds_y + 35)
            screen.blit(collect_surf, collect_rect)
        
        # Controls
        controls_y = y + height - 40
        controls_font = pygame.font.Font(None, 20)
        controls_text = "↑↓: Navigate  ENTER: Select  ESC: Close"
        controls_surf = controls_font.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_clearance(self, screen, x, y, width, height):
        """Draw clearance bin"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        title_surf = font_large.render("🔖 Clearance Bin - Damaged Goods", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 15)
        screen.blit(title_surf, title_rect)
        
        if not self.current_shop_id or not self.quality_manager:
            no_items = font_medium.render("Visit a shop to browse clearance items", True, self.gray_color)
            no_rect = no_items.get_rect(centerx=x + width // 2, centery=y + height // 2)
            screen.blit(no_items, no_rect)
            return
        
        items = self.quality_manager.get_clearance_items(self.current_shop_id)
        if not items:
            no_items = font_medium.render("No clearance items available", True, self.gray_color)
            no_rect = no_items.get_rect(centerx=x + width // 2, centery=y + height // 2)
            screen.blit(no_items, no_rect)
            return
        
        list_y = y + 70
        for i, item in enumerate(items):
            if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible:
                continue
                
            is_selected = (i == self.selected_index)
            item_y = list_y + (i - self.scroll_offset) * 85
            
            condition = self.quality_manager.get_condition(item['instance_id'])
            price = self.quality_manager.calculate_price(item['base_price'], item['instance_id'])
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 30, item_y, width - 60, 80)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
            
            # Item name with condition
            name_text = f"{item['item_id']} [{condition.get_name()}]"
            name_surf = font_medium.render(name_text, True, condition.get_color())
            screen.blit(name_surf, (x + 45, item_y + 10))
            
            # Price comparison
            price_text = f"{price}g (was {item['base_price']}g)"
            price_surf = font_small.render(price_text, True, self.green_color)
            screen.blit(price_surf, (x + 45, item_y + 40))
            
            # Savings
            savings = item['base_price'] - price
            savings_text = f"Save {savings}g ({int((1 - condition.get_value_multiplier()) * 100)}% off)"
            savings_surf = font_small.render(savings_text, True, self.accent_color)
            screen.blit(savings_surf, (x + 45, item_y + 60))
        
        # Controls
        controls_y = y + height - 35
        controls_text = "↑↓: Navigate  ENTER: Buy  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_market_events(self, screen, x, y, width, height):
        """Draw active market events"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 22)
        
        title_surf = font_large.render("🕐 Active Market Events", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 15)
        screen.blit(title_surf, title_rect)
        
        if not self.time_sales_manager:
            return
        
        active_events = self.time_sales_manager.get_active_events()
        
        if not active_events:
            no_events = font_medium.render("No special events active right now", True, self.gray_color)
            no_rect = no_events.get_rect(centerx=x + width // 2, centery=y + height // 2)
            screen.blit(no_events, no_rect)
            
            # Show upcoming events hint
            hint_y = y + height // 2 + 60
            hint_text = "Check back during:"
            hints = [
                "Weekends (Sat/Sun 8am-6pm) - Weekend Market",
                "Nights (10pm-4am) - Night Market",
                "Dawn (5am-9am) - Fisherman's Market",
                "Wednesday Noon (12pm-2pm) - Flash Sale"
            ]
            
            hint_surf = font_small.render(hint_text, True, self.accent_color)
            hint_rect = hint_surf.get_rect(centerx=x + width // 2, top=hint_y)
            screen.blit(hint_surf, hint_rect)
            
            for i, hint in enumerate(hints):
                hint_surf = font_small.render(f"• {hint}", True, self.gray_color)
                screen.blit(hint_surf, (x + 100, hint_y + 30 + i * 25))
            
            return
        
        event_y = y + 80
        for i, event in enumerate(active_events):
            box_y = event_y + i * 120
            
            # Event box
            box_rect = pygame.Rect(x + 40, box_y, width - 80, 110)
            pygame.draw.rect(screen, self.header_color, box_rect)
            pygame.draw.rect(screen, self.accent_color, box_rect, 2)
            
            # Event name
            event_names = {
                'weekend_market': '🎪 Weekend Market',
                'night_market': '🌙 Night Market',
                'dawn_market': '🌅 Fisherman\'s Dawn Market',
                'flash_sale': '⚡ Midweek Flash Sale'
            }
            name = event_names.get(event.event_type, event.event_type)
            name_surf = font_medium.render(name, True, self.gold_color)
            screen.blit(name_surf, (x + 55, box_y + 10))
            
            # Price modifiers
            mods_y = box_y + 45
            if event.price_modifiers:
                for category, mult in event.price_modifiers.items():
                    discount = int((1 - mult) * 100)
                    if discount > 0:
                        mod_text = f"{category.capitalize()}: {discount}% OFF"
                        color = self.green_color
                    else:
                        increase = int((mult - 1) * 100)
                        mod_text = f"{category.capitalize()}: +{increase}%"
                        color = self.red_color
                    
                    mod_surf = font_small.render(mod_text, True, color)
                    screen.blit(mod_surf, (x + 55, mods_y))
                    mods_y += 25
            
            # Special items
            if event.special_items:
                items_text = f"Special items: {', '.join(event.special_items[:3])}"
                items_surf = font_small.render(items_text, True, self.accent_color)
                screen.blit(items_surf, (x + 55, box_y + 85))
        
        # Controls
        controls_y = y + height - 35
        controls_text = "ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_appraisal(self, screen, x, y, width, height):
        """Draw appraisal screen"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        title_surf = font_large.render("🔍 Item Appraisal Service", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 15)
        screen.blit(title_surf, title_rect)
        
        if not self.appraisal_system:
            return
        
        # Show appraisal skill
        skill_text = f"Appraisal Skill: {self.appraisal_system.player_appraisal_skill}/100"
        skill_surf = font_small.render(skill_text, True, self.accent_color)
        screen.blit(skill_surf, (x + 40, y + 60))
        
        items = list(self.appraisal_system.unidentified_items.items())
        
        if not items:
            no_items = font_medium.render("No unidentified items in inventory", True, self.gray_color)
            no_rect = no_items.get_rect(centerx=x + width // 2, centery=y + height // 2)
            screen.blit(no_items, no_rect)
            return
        
        list_y = y + 100
        for i, (instance_id, item_data) in enumerate(items):
            if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible:
                continue
                
            is_selected = (i == self.selected_index)
            item_y = list_y + (i - self.scroll_offset) * 80
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 30, item_y, width - 60, 75)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
            
            # Item name
            name = self.appraisal_system.get_display_name(instance_id)
            name_surf = font_medium.render(name, True, self.text_color if item_data['identified'] else self.accent_color)
            screen.blit(name_surf, (x + 45, item_y + 10))
            
            # Value estimate
            value = self.appraisal_system.get_estimated_value(instance_id)
            value_text = f"Est. Value: {value}"
            value_surf = font_small.render(value_text, True, self.gold_color)
            screen.blit(value_surf, (x + 45, item_y + 40))
            
            # Appraisal cost if not identified
            if not item_data['identified']:
                cost_text = f"Appraisal Cost: {self.appraisal_system.APPRAISAL_COST}g"
                cost_surf = font_small.render(cost_text, True, self.green_color)
                cost_rect = cost_surf.get_rect(right=x + width - 45, centery=item_y + 40)
                screen.blit(cost_surf, cost_rect)
        
        # Controls
        controls_y = y + height - 35
        controls_text = "↑↓: Navigate  ENTER: Appraise (10g)  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_consignment(self, screen, x, y, width, height):
        """Draw consignment listing screen"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        title_surf = font_large.render("📦 Consignment - List Items for Sale", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 15)
        screen.blit(title_surf, title_rect)
        
        # Info text
        info_text = "Select an item from your inventory to list (15% commission on sale)"
        info_surf = font_small.render(info_text, True, self.accent_color)
        info_rect = info_surf.get_rect(centerx=x + width // 2, top=y + 60)
        screen.blit(info_surf, info_rect)
        
        if not hasattr(self.player, 'inventory') or not self.player.inventory:
            no_items = font_medium.render("No items in inventory", True, self.gray_color)
            no_rect = no_items.get_rect(centerx=x + width // 2, centery=y + height // 2)
            screen.blit(no_items, no_rect)
            return
        
        items = list(self.player.inventory.items())
        list_y = y + 100
        
        for i, (item_id, quantity) in enumerate(items):
            if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible:
                continue
                
            if quantity <= 0:
                continue
                
            is_selected = (i == self.selected_index)
            item_y = list_y + (i - self.scroll_offset) * 60
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 30, item_y, width - 60, 55)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
            
            # Item name and quantity
            item_text = f"{item_id} (x{quantity})"
            item_surf = font_medium.render(item_text, True, self.text_color)
            screen.blit(item_surf, (x + 45, item_y + 15))
        
        # Controls
        controls_y = y + height - 35
        controls_text = "↑↓: Navigate  ENTER: List Item  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_auction_browse(self, screen, x, y, width, height):
        """Draw auction browsing screen"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        title_surf = font_large.render("⚖️ Auction House - Browse Auctions", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 15)
        screen.blit(title_surf, title_rect)
        
        if not self.consignment_manager:
            return
        
        auctions = self.consignment_manager.get_active_auctions()
        
        if not auctions:
            no_auctions = font_medium.render("No active auctions", True, self.gray_color)
            no_rect = no_auctions.get_rect(centerx=x + width // 2, centery=y + height // 2)
            screen.blit(no_auctions, no_rect)
            return
        
        list_y = y + 70
        for i, auction in enumerate(auctions):
            if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible:
                continue
                
            is_selected = (i == self.selected_index)
            item_y = list_y + (i - self.scroll_offset) * 95
            
            # Selection highlight
            if is_selected:
                highlight_rect = pygame.Rect(x + 30, item_y, width - 60, 90)
                pygame.draw.rect(screen, self.selected_color, highlight_rect)
                pygame.draw.rect(screen, self.gold_color, highlight_rect, 2)
            
            # Item name
            name_surf = font_medium.render(auction.item_name, True, self.text_color)
            screen.blit(name_surf, (x + 45, item_y + 10))
            
            # Current bid
            bid_text = f"Current Bid: {auction.current_bid}g"
            bid_surf = font_small.render(bid_text, True, self.gold_color)
            screen.blit(bid_surf, (x + 45, item_y + 40))
            
            # Buyout price
            buyout_text = f"Buyout: {auction.buyout_price}g"
            buyout_surf = font_small.render(buyout_text, True, self.accent_color)
            screen.blit(buyout_surf, (x + 45, item_y + 63))
            
            # Time remaining
            days_left = auction.days_remaining(self.game_time.day_count)
            time_text = f"{days_left} days left"
            time_color = self.green_color if days_left > 2 else self.red_color
            time_surf = font_small.render(time_text, True, time_color)
            time_rect = time_surf.get_rect(right=x + width - 45, centery=item_y + 50)
            screen.blit(time_surf, time_rect)
        
        # Controls
        controls_y = y + height - 35
        controls_text = "↑↓: Navigate  ENTER: Bid +50g  ESC: Back"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=x + width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
        
    def _draw_my_listings(self, screen, x, y, width, height):
        """Draw player's active listings"""
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        title_surf = font_large.render("My Active Listings", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=x + width // 2, top=y + 15)
        screen.blit(title_surf, title_rect)
        
        # Combined list of consignments and auctions
        # This view would show status of player's items
        
    def _draw_input_overlay(self, screen, screen_width, screen_height):
        """Draw input overlay for entering values"""
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        box_width = 400
        box_height = 120
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2
        
        pygame.draw.rect(screen, self.panel_color, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, self.gold_color, (box_x, box_y, box_width, box_height), 3)
        
        # Prompt
        prompts = {
            'price': "Enter asking price:",
            'quantity': "Enter quantity:",
            'buyout': "Enter buyout price:",
            'days': "Enter auction days:"
        }
        prompt_text = prompts.get(self.input_mode, "Enter value:")
        prompt_surf = font_small.render(prompt_text, True, self.text_color)
        prompt_rect = prompt_surf.get_rect(centerx=box_x + box_width // 2, top=box_y + 15)
        screen.blit(prompt_surf, prompt_rect)
        
        # Input field
        input_rect = pygame.Rect(box_x + 50, box_y + 55, box_width - 100, 40)
        pygame.draw.rect(screen, self.header_color, input_rect)
        pygame.draw.rect(screen, self.accent_color, input_rect, 2)
        
        input_text = self.input_value or ""
        input_surf = font_medium.render(input_text, True, self.text_color)
        screen.blit(input_surf, (box_x + 60, box_y + 62))
        
    def _draw_message(self, screen, screen_width, screen_height):
        """Draw message overlay"""
        font = pygame.font.Font(None, 28)
        
        msg_surf = font.render(self.message, True, self.message_color)
        msg_width = msg_surf.get_width() + 40
        msg_height = 50
        msg_x = (screen_width - msg_width) // 2
        msg_y = screen_height - 100
        
        pygame.draw.rect(screen, self.panel_color, (msg_x, msg_y, msg_width, msg_height))
        pygame.draw.rect(screen, self.message_color, (msg_x, msg_y, msg_width, msg_height), 2)
        
        msg_rect = msg_surf.get_rect(center=(screen_width // 2, msg_y + msg_height // 2))
        screen.blit(msg_surf, msg_rect)
