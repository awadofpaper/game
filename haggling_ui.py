"""
Haggling UI - Interactive price negotiation interface
"""

import pygame


class HagglingUI:
    """Visual interface for haggling with merchants"""
    
    def __init__(self):
        self.active = False
        self.haggling_system = None
        self.reputation_manager = None
        self.player = None
        self.merchant_id = None
        self.merchant_name = None
        self.selected_item = None
        
        # Haggle state
        self.base_price = 0
        self.offered_price = 0
        self.is_buying = True
        self.success_chance = 0.0
        self.result_message = ""
        self.result_timer = 0
        self.haggle_completed = False
        self.final_price = 0
        
        # UI state
        self.offer_percentage = 0.85  # Start at 85% of price (15% discount)
        self.adjusting = False
        
        # Colors
        self.bg_color = (40, 30, 50)
        self.panel_color = (60, 50, 70)
        self.selected_color = (100, 80, 140)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.success_color = (100, 255, 100)
        self.failure_color = (255, 100, 100)
        self.warning_color = (255, 200, 100)
        
    def open(self, haggling_system, reputation_manager, player, merchant_id, 
             merchant_name, item, base_price, is_buying=True):
        """Open the haggling interface"""
        self.active = True
        self.haggling_system = haggling_system
        self.reputation_manager = reputation_manager
        self.player = player
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name
        self.selected_item = item
        self.base_price = base_price
        self.is_buying = is_buying
        self.offer_percentage = 0.85 if is_buying else 1.15  # 15% discount when buying, 15% more when selling
        self.result_message = ""
        self.result_timer = 0
        self.haggle_completed = False
        
        # Start haggle session in the system
        self.haggling_system.start_haggle(
            merchant_id, merchant_name, item.name, base_price, is_buying
        )
        
        self._update_offer()
    
    def close(self):
        """Close the haggling interface"""
        self.active = False
        if self.haggling_system:
            self.haggling_system.end_haggle()
        return self.haggle_completed, self.final_price
    
    def _update_offer(self):
        """Update the offered price and success chance"""
        self.offered_price = int(self.base_price * self.offer_percentage)
        
        # Calculate success chance
        if self.haggling_system and self.reputation_manager and self.player:
            self.success_chance = self.haggling_system.calculate_success_chance(
                self.player,
                self.reputation_manager,
                self.merchant_id,
                self.merchant_name,
                self.offer_percentage
            )
        else:
            self.success_chance = 0.5
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"
            
            elif event.key == pygame.K_LEFT:
                # Decrease offer (ask for better deal)
                if self.is_buying:
                    self.offer_percentage = max(0.5, self.offer_percentage - 0.05)
                else:
                    self.offer_percentage = max(1.0, self.offer_percentage - 0.05)
                self._update_offer()
            
            elif event.key == pygame.K_RIGHT:
                # Increase offer (safer)
                if self.is_buying:
                    self.offer_percentage = min(1.0, self.offer_percentage + 0.05)
                else:
                    self.offer_percentage = min(1.5, self.offer_percentage + 0.05)
                self._update_offer()
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Attempt the haggle
                if not self.haggle_completed:
                    self._attempt_haggle()
                else:
                    # Close after seeing result
                    return "close"
        
        return None
    
    def _attempt_haggle(self):
        """Attempt to haggle with current offer"""
        success, message, final_price = self.haggling_system.attempt_haggle(
            self.player,
            self.reputation_manager,
            self.merchant_id,
            self.merchant_name,
            self.offered_price
        )
        
        self.result_message = message
        self.result_timer = 180  # 3 seconds at 60fps
        
        if success:
            self.haggle_completed = True
            self.final_price = final_price
        else:
            # Check if we're out of attempts
            if self.haggling_system.active_haggle:
                attempts = self.haggling_system.active_haggle['attempts']
                max_attempts = self.haggling_system.active_haggle['max_attempts']
                if attempts >= max_attempts:
                    # Failed completely
                    self.haggle_completed = True
                    self.final_price = self.base_price
    
    def update(self):
        """Update UI state"""
        if self.result_timer > 0:
            self.result_timer -= 1
    
    def draw(self, screen, font):
        """Draw the haggling UI"""
        if not self.active:
            return
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Main haggling panel
        panel_width = 600
        panel_height = 450
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, self.bg_color, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, self.gold_color, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Header
        header_font = pygame.font.SysFont(None, 40)
        header_text = "💰 Haggling 💰"
        header_surf = header_font.render(header_text, True, self.gold_color)
        screen.blit(header_surf, (panel_x + panel_width//2 - header_surf.get_width()//2, panel_y + 15))
        
        # Merchant name
        merchant_font = pygame.font.SysFont(None, 28)
        merchant_text = f"Negotiating with {self.merchant_name}"
        merchant_surf = merchant_font.render(merchant_text, True, self.text_color)
        screen.blit(merchant_surf, (panel_x + panel_width//2 - merchant_surf.get_width()//2, panel_y + 55))
        
        # Item info
        item_font = pygame.font.SysFont(None, 32)
        action_text = "Buying" if self.is_buying else "Selling"
        item_text = f"{action_text}: {self.selected_item.name}"
        item_surf = item_font.render(item_text, True, self.text_color)
        screen.blit(item_surf, (panel_x + 20, panel_y + 95))
        
        # Base price
        price_y = panel_y + 135
        base_price_text = f"Base Price: {self.base_price}g"
        base_surf = font.render(base_price_text, True, self.text_color)
        screen.blit(base_surf, (panel_x + 20, price_y))
        
        if not self.haggle_completed:
            # Offer slider
            slider_y = panel_y + 180
            slider_label = "Your Offer:" if self.is_buying else "You Want:"
            label_surf = font.render(slider_label, True, self.text_color)
            screen.blit(label_surf, (panel_x + 20, slider_y))
            
            # Offer amount
            offer_font = pygame.font.SysFont(None, 36)
            offer_color = self.gold_color
            if self.is_buying and self.offered_price < self.base_price:
                discount_pct = int((1.0 - self.offer_percentage) * 100)
                offer_text = f"{self.offered_price}g (-{discount_pct}%)"
            elif not self.is_buying and self.offered_price > self.base_price:
                increase_pct = int((self.offer_percentage - 1.0) * 100)
                offer_text = f"{self.offered_price}g (+{increase_pct}%)"
            else:
                offer_text = f"{self.offered_price}g"
            
            offer_surf = offer_font.render(offer_text, True, offer_color)
            screen.blit(offer_surf, (panel_x + 20, slider_y + 30))
            
            # Visual slider
            slider_x = panel_x + 20
            slider_width = panel_width - 40
            slider_bar_y = slider_y + 75
            
            # Slider background
            pygame.draw.rect(screen, self.panel_color, 
                           (slider_x, slider_bar_y, slider_width, 20))
            pygame.draw.rect(screen, self.text_color, 
                           (slider_x, slider_bar_y, slider_width, 20), 2)
            
            # Slider position
            if self.is_buying:
                # 0.5 to 1.0 maps to left to right
                slider_pos = (self.offer_percentage - 0.5) / 0.5
            else:
                # 1.0 to 1.5 maps to left to right
                slider_pos = (self.offer_percentage - 1.0) / 0.5
            
            slider_pos = max(0, min(1, slider_pos))
            handle_x = slider_x + int(slider_pos * slider_width)
            
            pygame.draw.circle(screen, self.gold_color, (handle_x, slider_bar_y + 10), 12)
            pygame.draw.circle(screen, self.text_color, (handle_x, slider_bar_y + 10), 12, 2)
            
            # Success chance
            chance_y = slider_y + 110
            chance_text = f"Success Chance: {int(self.success_chance * 100)}%"
            
            # Color based on chance
            if self.success_chance >= 0.7:
                chance_color = self.success_color
            elif self.success_chance >= 0.4:
                chance_color = self.warning_color
            else:
                chance_color = self.failure_color
            
            chance_surf = font.render(chance_text, True, chance_color)
            screen.blit(chance_surf, (panel_x + 20, chance_y))
            
            # Visual chance bar
            bar_y = chance_y + 30
            bar_width = panel_width - 40
            bar_height = 25
            
            pygame.draw.rect(screen, self.panel_color, 
                           (panel_x + 20, bar_y, bar_width, bar_height))
            
            # Filled portion
            fill_width = int(bar_width * self.success_chance)
            pygame.draw.rect(screen, chance_color, 
                           (panel_x + 20, bar_y, fill_width, bar_height))
            
            pygame.draw.rect(screen, self.text_color, 
                           (panel_x + 20, bar_y, bar_width, bar_height), 2)
            
            # Attempts remaining
            if self.haggling_system.active_haggle:
                attempts = self.haggling_system.active_haggle['attempts']
                max_attempts = self.haggling_system.active_haggle['max_attempts']
                attempts_text = f"Attempts: {attempts}/{max_attempts}"
                attempts_surf = font.render(attempts_text, True, self.text_color)
                screen.blit(attempts_surf, (panel_x + panel_width - attempts_surf.get_width() - 20, chance_y))
            
            # Instructions
            instruct_y = panel_y + panel_height - 80
            instruct_font = pygame.font.SysFont(None, 22)
            instructions = [
                "← → : Adjust offer",
                "ENTER: Make offer",
                "ESC: Cancel"
            ]
            
            for i, instruction in enumerate(instructions):
                instruct_surf = instruct_font.render(instruction, True, (180, 180, 180))
                screen.blit(instruct_surf, (panel_x + 20 + i * 190, instruct_y))
        
        else:
            # Show result
            result_y = panel_y + 200
            result_font = pygame.font.SysFont(None, 32)
            
            # Determine result color
            if self.final_price < self.base_price and self.is_buying:
                result_color = self.success_color
                result_prefix = "✓ SUCCESS! "
            elif self.final_price > self.base_price and not self.is_buying:
                result_color = self.success_color
                result_prefix = "✓ SUCCESS! "
            else:
                result_color = self.failure_color
                result_prefix = "✗ FAILED! "
            
            # Result message
            msg_surf = result_font.render(result_prefix, True, result_color)
            screen.blit(msg_surf, (panel_x + panel_width//2 - msg_surf.get_width()//2, result_y))
            
            # Merchant's response
            response_y = result_y + 45
            response_font = pygame.font.SysFont(None, 24)
            
            # Word wrap the message
            words = self.result_message.split()
            lines = []
            current_line = []
            max_width = panel_width - 80
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surf = response_font.render(test_line, True, self.text_color)
                if test_surf.get_width() <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for i, line in enumerate(lines):
                line_surf = response_font.render(line, True, self.text_color)
                screen.blit(line_surf, (panel_x + 40, response_y + i * 30))
            
            # Final price
            final_y = response_y + len(lines) * 30 + 40
            final_font = pygame.font.SysFont(None, 36)
            final_text = f"Final Price: {self.final_price}g"
            final_surf = final_font.render(final_text, True, self.gold_color)
            screen.blit(final_surf, (panel_x + panel_width//2 - final_surf.get_width()//2, final_y))
            
            # Press any key to continue
            continue_y = panel_y + panel_height - 50
            continue_font = pygame.font.SysFont(None, 24)
            continue_text = "Press ENTER to continue..."
            continue_surf = continue_font.render(continue_text, True, (180, 180, 180))
            screen.blit(continue_surf, (panel_x + panel_width//2 - continue_surf.get_width()//2, continue_y))
"""
Haggling UI - Interactive price negotiation interface
"""

import pygame
import logging

logger = logging.getLogger(__name__)


class HagglingUI:
    """Visual interface for haggling with merchants"""
    
    def __init__(self):
        self.active = False
        self.item = None
        self.base_price = 0
        self.current_offer = 0
        self.is_buying = True
        
        # System references
        self.haggling_system = None
        self.reputation_manager = None
        self.player = None
        self.merchant_id = None
        self.merchant_name = None
        
        # UI state
        self.slider_dragging = False
        self.min_offer_percent = 0.5  # Can haggle down to 50%
        self.max_offer_percent = 1.0  # Up to full price
        self.offer_percent = 0.9  # Start at 10% off
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.panel_color = (40, 40, 50)
        self.accent_color = (80, 120, 180)
        self.success_color = (100, 200, 100)
        self.warning_color = (255, 200, 0)
        self.danger_color = (255, 100, 100)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        
        # Result message
        self.result_message = ""
        self.result_timer = 0
        self.result_color = (255, 255, 255)
        
    def open(self, item, base_price, is_buying, player, haggling_system, 
             reputation_manager, merchant_id, merchant_name):
        """Open the haggling UI"""
        self.active = True
        self.item = item
        self.base_price = base_price
        self.is_buying = is_buying
        self.player = player
        self.haggling_system = haggling_system
        self.reputation_manager = reputation_manager
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name
        
        # Initialize offer
        if is_buying:
            self.offer_percent = 0.9  # Start at 10% off
        else:
            self.offer_percent = 1.1  # Start asking for 10% more
        
        self._update_current_offer()
        
        # Start haggle session
        self.haggling_system.start_haggle(
            merchant_id, merchant_name, item.name, base_price, is_buying
        )
        
        self.result_message = ""
        self.result_timer = 0
        
        logger.info(f"[HAGGLE UI] Opened haggling for {item.name} at {base_price}g")
    
    def close(self):
        """Close the haggling UI"""
        self.active = False
        if self.haggling_system:
            self.haggling_system.end_haggle()
        logger.info("[HAGGLE UI] Closed")
    
    def _update_current_offer(self):
        """Update current offer based on slider percentage"""
        self.current_offer = int(self.base_price * self.offer_percent)
    
    def _get_success_chance(self) -> float:
        """Calculate and return current success chance"""
        if not self.haggling_system or not self.haggling_system.active_haggle:
            return 0.5
        
        return self.haggling_system.calculate_success_chance(
            self.player, self.reputation_manager, 
            self.merchant_id, self.merchant_name, 
            self.offer_percent
        )
    
    def _get_charisma_bonus(self) -> float:
        """Get charisma bonus percentage"""
        if hasattr(self.player, 'charisma'):
            return (self.player.charisma - 10) * 0.02
        return 0.0
    
    def _get_reputation_bonus(self) -> float:
        """Get reputation bonus percentage"""
        if not self.reputation_manager:
            return 0.0
        
        rep = self.reputation_manager.get_or_create_reputation(
            self.merchant_id, self.merchant_name
        )
        tier_index = next((i for i, t in enumerate(rep.TIERS) 
                          if t.name == rep.get_current_tier().name), 2)
        neutral_index = 2
        return (tier_index - neutral_index) * 0.05
    
    def _attempt_haggle(self):
        """Attempt to haggle with current offer"""
        if not self.haggling_system or not self.haggling_system.active_haggle:
            return False
        
        success, message, final_price = self.haggling_system.attempt_haggle(
            self.player, self.reputation_manager,
            self.merchant_id, self.merchant_name,
            self.current_offer
        )
        
        self.result_message = message
        self.result_timer = 180  # 3 seconds at 60fps
        self.result_color = self.success_color if success else self.danger_color
        
        if success or (not success and self.haggling_system.active_haggle['attempts'] >= 3):
            # Close after success or final failure
            return True
        
        return False
    
    def handle_input(self, event):
        """Handle user input"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return "closed"
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Attempt haggle
                should_close = self._attempt_haggle()
                if should_close:
                    return "haggle_complete"
            
            elif event.key == pygame.K_LEFT:
                # Decrease offer
                self.offer_percent = max(self.min_offer_percent, self.offer_percent - 0.05)
                self._update_current_offer()
            
            elif event.key == pygame.K_RIGHT:
                # Increase offer
                self.offer_percent = min(self.max_offer_percent, self.offer_percent + 0.05)
                self._update_current_offer()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicking on slider
                screen_width = pygame.display.get_surface().get_width()
                screen_height = pygame.display.get_surface().get_height()
                panel_width = 600
                panel_x = (screen_width - panel_width) // 2
                panel_y = (screen_height - 450) // 2
                
                slider_y = panel_y + 220
                slider_x = panel_x + 50
                slider_width = panel_width - 100
                
                slider_rect = pygame.Rect(slider_x, slider_y - 10, slider_width, 20)
                if slider_rect.collidepoint(mouse_pos):
                    self.slider_dragging = True
                    # Update offer based on click position
                    relative_x = mouse_pos[0] - slider_x
                    self.offer_percent = self.min_offer_percent + (relative_x / slider_width) * (self.max_offer_percent - self.min_offer_percent)
                    self.offer_percent = max(self.min_offer_percent, min(self.max_offer_percent, self.offer_percent))
                    self._update_current_offer()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.slider_dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.slider_dragging:
                mouse_pos = pygame.mouse.get_pos()
                screen_width = pygame.display.get_surface().get_width()
                panel_width = 600
                panel_x = (screen_width - panel_width) // 2
                slider_x = panel_x + 50
                slider_width = panel_width - 100
                
                relative_x = mouse_pos[0] - slider_x
                self.offer_percent = self.min_offer_percent + (relative_x / slider_width) * (self.max_offer_percent - self.min_offer_percent)
                self.offer_percent = max(self.min_offer_percent, min(self.max_offer_percent, self.offer_percent))
                self._update_current_offer()
        
        return None
    
    def draw(self, screen, font):
        """Draw the haggling UI"""
        if not self.active or not self.item:
            return
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Main haggling panel
        panel_width = 600
        panel_height = 450
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, self.bg_color, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, self.accent_color, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Header
        header_font = pygame.font.SysFont(None, 36)
        header_text = "HAGGLING"
        header_surf = header_font.render(header_text, True, self.gold_color)
        screen.blit(header_surf, (panel_x + panel_width//2 - header_surf.get_width()//2, panel_y + 15))
        
        # Item name
        item_font = pygame.font.SysFont(None, 28)
        item_text = f"Item: {self.item.name}"
        item_surf = item_font.render(item_text, True, self.text_color)
        screen.blit(item_surf, (panel_x + 30, panel_y + 60))
        
        # Base price
        base_price_text = f"Base Price: {self.base_price}g"
        base_surf = font.render(base_price_text, True, (200, 200, 200))
        screen.blit(base_surf, (panel_x + 30, panel_y + 95))
        
        # Current offer
        offer_text = f"Your Offer: {self.current_offer}g"
        discount_amount = self.base_price - self.current_offer
        discount_percent = int((1.0 - self.offer_percent) * 100)
        if discount_percent > 0:
            offer_detail = f"({discount_percent}% off, saving {discount_amount}g)"
        else:
            offer_detail = "(full price)"
        
        offer_surf = item_font.render(offer_text, True, self.gold_color)
        detail_surf = font.render(offer_detail, True, self.warning_color if discount_percent > 20 else self.text_color)
        screen.blit(offer_surf, (panel_x + 30, panel_y + 125))
        screen.blit(detail_surf, (panel_x + 30, panel_y + 155))
        
        # Slider for adjusting offer
        slider_y = panel_y + 220
        slider_x = panel_x + 50
        slider_width = panel_width - 100
        slider_height = 8
        
        # Slider background
        pygame.draw.rect(screen, self.panel_color, (slider_x, slider_y - slider_height//2, slider_width, slider_height))
        pygame.draw.rect(screen, self.text_color, (slider_x, slider_y - slider_height//2, slider_width, slider_height), 1)
        
        # Slider fill (shows current position)
        fill_width = int(slider_width * (self.offer_percent - self.min_offer_percent) / (self.max_offer_percent - self.min_offer_percent))
        pygame.draw.rect(screen, self.accent_color, (slider_x, slider_y - slider_height//2, fill_width, slider_height))
        
        # Slider handle
        handle_x = slider_x + fill_width
        handle_radius = 12
        pygame.draw.circle(screen, self.gold_color, (handle_x, slider_y), handle_radius)
        pygame.draw.circle(screen, self.text_color, (handle_x, slider_y), handle_radius, 2)
        
        # Slider labels
        small_font = pygame.font.SysFont(None, 20)
        min_label = small_font.render("50% off", True, self.text_color)
        max_label = small_font.render("Full price", True, self.text_color)
        screen.blit(min_label, (slider_x, slider_y + 15))
        screen.blit(max_label, (slider_x + slider_width - max_label.get_width(), slider_y + 15))
        
        # Success chance display
        success_chance = self._get_success_chance()
        chance_y = panel_y + 260
        
        chance_text = "Success Chance:"
        chance_surf = font.render(chance_text, True, self.text_color)
        screen.blit(chance_surf, (panel_x + 30, chance_y))
        
        # Success chance bar
        bar_width = 400
        bar_height = 25
        bar_x = panel_x + 180
        bar_y = chance_y
        
        pygame.draw.rect(screen, self.panel_color, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, self.text_color, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Fill based on success chance
        fill_width = int(bar_width * success_chance)
        if success_chance >= 0.7:
            bar_color = self.success_color
        elif success_chance >= 0.4:
            bar_color = self.warning_color
        else:
            bar_color = self.danger_color
        
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Percentage text
        percent_text = f"{int(success_chance * 100)}%"
        percent_surf = item_font.render(percent_text, True, self.text_color)
        screen.blit(percent_surf, (bar_x + bar_width//2 - percent_surf.get_width()//2, bar_y + 3))
        
        # Bonuses breakdown
        bonus_y = chance_y + 35
        charisma_bonus = self._get_charisma_bonus()
        reputation_bonus = self._get_reputation_bonus()
        
        if charisma_bonus != 0 or reputation_bonus != 0:
            bonuses = []
            if charisma_bonus > 0:
                bonuses.append(f"+{int(charisma_bonus*100)}% Charisma")
            if reputation_bonus > 0:
                bonuses.append(f"+{int(reputation_bonus*100)}% Reputation")
            elif reputation_bonus < 0:
                bonuses.append(f"{int(reputation_bonus*100)}% Reputation")
            
            bonus_text = "Bonuses: " + ", ".join(bonuses)
            bonus_surf = small_font.render(bonus_text, True, self.success_color if reputation_bonus >= 0 else self.danger_color)
            screen.blit(bonus_surf, (panel_x + 30, bonus_y))
        
        # Attempts remaining
        if self.haggling_system and self.haggling_system.active_haggle:
            attempts = self.haggling_system.active_haggle['attempts']
            max_attempts = self.haggling_system.active_haggle['max_attempts']
            remaining = max_attempts - attempts
            
            attempts_text = f"Attempts Remaining: {remaining}/{max_attempts}"
            attempts_color = self.success_color if remaining > 1 else self.danger_color
            attempts_surf = font.render(attempts_text, True, attempts_color)
            screen.blit(attempts_surf, (panel_x + 30, panel_y + 330))
        
        # Controls
        controls_y = panel_y + panel_height - 60
        controls_font = pygame.font.SysFont(None, 22)
        controls = [
            "←/→ or Mouse: Adjust Offer",
            "ENTER: Make Offer",
            "ESC: Cancel"
        ]
        
        for i, control in enumerate(controls):
            control_surf = controls_font.render(control, True, (180, 180, 180))
            screen.blit(control_surf, (panel_x + 30, controls_y + i * 25))
        
        # Result message
        if self.result_message and self.result_timer > 0:
            self.result_timer -= 1
            
            msg_font = pygame.font.SysFont(None, 26)
            msg_surf = msg_font.render(self.result_message, True, self.result_color)
            msg_bg = pygame.Surface((msg_surf.get_width() + 30, msg_surf.get_height() + 20))
            msg_bg.set_alpha(240)
            msg_bg.fill((0, 0, 0))
            
            msg_x = panel_x + panel_width//2 - msg_surf.get_width()//2
            msg_y = panel_y + 370
            
            screen.blit(msg_bg, (msg_x - 15, msg_y - 10))
            pygame.draw.rect(screen, self.result_color, (msg_x - 15, msg_y - 10, msg_surf.get_width() + 30, msg_surf.get_height() + 20), 2)
            screen.blit(msg_surf, (msg_x, msg_y))
