"""
Companion Hiring UI - Interface for hiring companions at inns/taverns
Shows available companions, their stats, requirements, and payment system
"""

import pygame
from companion_system import CompanionType


class CompanionHiringUI:
    """UI for hiring and managing companions at inns"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        
        # UI dimensions
        self.panel_width = 800
        self.panel_height = 600
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # References (set by main.py)
        self.companion_manager = None
        self.player = None
        self.current_inn = None
        self.game_time = None
        self.bank_system = None  # For bank integration
        self.floating_texts = None  # For message display
        
        # UI state
        self.selected_index = 0
        self.showing_payment_ui = False
        self.payment_companion = None
        self.transfer_mode = None  # "dubloons" or "items"
        self.transfer_amount = ""
        
        # New UI modes for TODO features
        self.showing_companion_selection = False
        self.companion_selection_index = 0
        self.showing_item_selection = False
        self.item_selection_index = 0
        self.selectable_items = []
        
    def open(self, inn_location):
        """Open hiring UI for specific inn"""
        self.active = True
        self.current_inn = inn_location
        self.selected_index = 0
        self.showing_payment_ui = False
    
    def close(self):
        """Close UI"""
        self.active = False
        self.current_inn = None
        self.showing_payment_ui = False
        self.payment_companion = None
    
    def toggle(self, inn_location=None):
        """Toggle UI"""
        if self.active:
            self.close()
        else:
            if inn_location:
                self.open(inn_location)
    
    def handle_input(self, event):
        """Handle keyboard/mouse input"""
        if not self.active:
            return
        
        if self.showing_item_selection:
            self._handle_item_selection_input(event)
            return
        
        if self.showing_companion_selection:
            self._handle_companion_selection_input(event)
            return
        
        if self.showing_payment_ui:
            self._handle_payment_input(event)
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
            
            elif event.key == pygame.K_UP:
                available = self.companion_manager.get_available_companions(self.current_inn)
                if available:
                    self.selected_index = (self.selected_index - 1) % len(available)
            
            elif event.key == pygame.K_DOWN:
                available = self.companion_manager.get_available_companions(self.current_inn)
                if available:
                    self.selected_index = (self.selected_index + 1) % len(available)
            
            elif event.key == pygame.K_h or event.key == pygame.K_RETURN:
                # Hire selected companion
                self._try_hire_selected()
            
            elif event.key == pygame.K_p:
                # Check payment for hired companions
                self._show_payment_for_selected()
    
    def _try_hire_selected(self):
        """Try to hire the selected companion"""
        if not self.companion_manager or not self.player:
            return
        
        available = self.companion_manager.get_available_companions(self.current_inn)
        if not available or self.selected_index >= len(available):
            return
        
        companion = available[self.selected_index]
        success, message = self.companion_manager.hire_companion(companion, self.player, self.game_time)
        
        print(f"[COMPANION HIRE] {message}")
        
        # Show message in game using floating text
        if hasattr(self, 'floating_texts') and self.floating_texts is not None:
            from floating_text import CombatText
            color = (50, 255, 50) if success else (255, 50, 50)
            message_text = CombatText(message, (self.screen_width // 2, self.screen_height // 2), color=color, duration=3.0)
            self.floating_texts.append(message_text)
    
    def _show_payment_for_selected(self):
        """Show payment UI for selected companion"""
        if not self.companion_manager or not self.player:
            return
        
        # Get player's hired companions
        hired = self.companion_manager.get_employer_companions(self.player)
        if not hired:
            return
        
        # If only one companion, select automatically
        if len(hired) == 1:
            self.payment_companion = hired[0]
            self.showing_payment_ui = True
        else:
            # Show selection UI for multiple companions
            self.showing_companion_selection = True
            self.companion_selection_index = 0
    
    def _handle_payment_input(self, event):
        """Handle input in payment UI"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.showing_payment_ui = False
                self.payment_companion = None
                self.transfer_mode = None
                self.transfer_amount = ""
            
            elif event.key == pygame.K_d:
                self.transfer_mode = "dubloons"
                self.transfer_amount = ""
            
            elif event.key == pygame.K_i:
                self.transfer_mode = "items"
                # Open item selection mode
                if hasattr(self.player, 'inventory') and self.player.inventory:
                    self.showing_item_selection = True
                    self.item_selection_index = 0
                    self.selectable_items = list(self.player.inventory.keys())
                else:
                    print("[COMPANION] You have no items to transfer")
            
            elif event.key == pygame.K_RETURN and self.transfer_mode == "dubloons":
                self._execute_payment_transfer()
            
            elif event.key == pygame.K_BACKSPACE:
                self.transfer_amount = self.transfer_amount[:-1]
            
            elif event.unicode.isdigit() and self.transfer_mode == "dubloons":
                self.transfer_amount += event.unicode
    
    def _handle_companion_selection_input(self, event):
        """Handle input when selecting which companion to pay"""
        if event.type == pygame.KEYDOWN:
            hired = self.companion_manager.get_employer_companions(self.player)
            
            if event.key == pygame.K_ESCAPE:
                self.showing_companion_selection = False
                self.companion_selection_index = 0
            
            elif event.key == pygame.K_UP:
                self.companion_selection_index = (self.companion_selection_index - 1) % len(hired)
            
            elif event.key == pygame.K_DOWN:
                self.companion_selection_index = (self.companion_selection_index + 1) % len(hired)
            
            elif event.key == pygame.K_RETURN:
                # Select this companion for payment
                self.payment_companion = hired[self.companion_selection_index]
                self.showing_companion_selection = False
                self.showing_payment_ui = True
    
    def _handle_item_selection_input(self, event):
        """Handle input when selecting items to transfer"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.showing_item_selection = False
                self.item_selection_index = 0
            
            elif event.key == pygame.K_UP and self.selectable_items:
                self.item_selection_index = (self.item_selection_index - 1) % len(self.selectable_items)
            
            elif event.key == pygame.K_DOWN and self.selectable_items:
                self.item_selection_index = (self.item_selection_index + 1) % len(self.selectable_items)
            
            elif event.key == pygame.K_RETURN and self.selectable_items:
                # Transfer selected item to companion
                selected_item_id = self.selectable_items[self.item_selection_index]
                if selected_item_id in self.player.inventory:
                    # Transfer one item
                    self.player.inventory[selected_item_id] -= 1
                    if self.player.inventory[selected_item_id] <= 0:
                        del self.player.inventory[selected_item_id]
                    
                    # Add to companion's inventory (if they have one)
                    if not hasattr(self.payment_companion, 'inventory'):
                        self.payment_companion.inventory = {}
                    
                    self.payment_companion.inventory[selected_item_id] = self.payment_companion.inventory.get(selected_item_id, 0) + 1
                    
                    print(f"[COMPANION] Transferred {selected_item_id} to {self.payment_companion.name}")
                    
                    # Update selectable items
                    self.selectable_items = list(self.player.inventory.keys())
                    if not self.selectable_items:
                        self.showing_item_selection = False
                    else:
                        self.item_selection_index = min(self.item_selection_index, len(self.selectable_items) - 1)
    
    def _execute_payment_transfer(self):
        """Execute payment transfer to companion"""
        if not self.payment_companion or not self.player:
            return
        
        try:
            amount = int(self.transfer_amount)
            if amount <= 0:
                return
            
            if amount > self.player.dubloons:
                print("[PAYMENT] Not enough dubloons!")
                return
            
            # Transfer money
            self.player.dubloons -= amount
            self.payment_companion.earnings_owed -= amount
            
            if self.payment_companion.earnings_owed < 0:
                # Overpaid, refund excess
                self.player.dubloons += abs(self.payment_companion.earnings_owed)
                self.payment_companion.earnings_owed = 0
            
            print(f"[PAYMENT] Paid {amount}g to {self.payment_companion.name}")
            self.transfer_amount = ""
            
        except ValueError:
            pass
    
    def draw(self, screen, font):
        """Draw hiring UI"""
        if not self.active or not self.companion_manager:
            return
        
        if self.showing_payment_ui:
            self._draw_payment_ui(screen, font)
            return
        
        # Draw main panel
        panel = pygame.Surface((self.panel_width, self.panel_height))
        panel.set_alpha(240)
        panel.fill((20, 20, 30))
        pygame.draw.rect(panel, (100, 100, 120), (0, 0, self.panel_width, self.panel_height), 3)
        
        # Title
        title_font = pygame.font.SysFont(None, 36)
        title = title_font.render("🛡️ HIRE COMPANION", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.panel_width // 2, 30))
        panel.blit(title, title_rect)
        
        # Get available companions
        available = self.companion_manager.get_available_companions(self.current_inn)
        
        if not available:
            no_companions = font.render("No companions available at this inn.", True, (200, 200, 200))
            panel.blit(no_companions, (50, 100))
        else:
            # Draw companion list
            y_offset = 80
            for i, companion in enumerate(available):
                self._draw_companion_card(panel, font, companion, 20, y_offset, i == self.selected_index)
                y_offset += 100
        
        # Draw controls
        controls_y = self.panel_height - 40
        controls = [
            "↑↓: Select",
            "H/Enter: Hire",
            "P: Check Payment (hired companions)",
            "ESC: Close"
        ]
        controls_text = " | ".join(controls)
        controls_surface = font.render(controls_text, True, (150, 150, 150))
        controls_rect = controls_surface.get_rect(center=(self.panel_width // 2, controls_y))
        panel.blit(controls_surface, controls_rect)
        
        # Blit to screen
        screen.blit(panel, (self.panel_x, self.panel_y))
    
    def _draw_companion_card(self, surface, font, companion, x, y, selected):
        """Draw individual companion card"""
        card_width = self.panel_width - 40
        card_height = 90
        
        # Background
        if selected:
            color = (50, 80, 120)
        else:
            color = (30, 30, 40)
        
        pygame.draw.rect(surface, color, (x, y, card_width, card_height))
        pygame.draw.rect(surface, (100, 100, 120), (x, y, card_width, card_height), 2)
        
        # Companion type icon/color
        pygame.draw.circle(surface, companion.color, (x + 30, y + 45), 25)
        
        # Name
        name_font = pygame.font.SysFont(None, 24)
        name_text = name_font.render(companion.name, True, (255, 255, 255))
        surface.blit(name_text, (x + 70, y + 10))
        
        # Type
        type_text = font.render(f"Type: {companion.companion_type.value.replace('_', ' ').title()}", True, (200, 200, 200))
        surface.blit(type_text, (x + 70, y + 35))
        
        # Stats
        stats_text = f"Lvl {companion.level} | HP: {companion.max_health} | Dmg: {companion.base_damage}"
        if companion.magic_power > 0:
            stats_text += f" | Magic: {companion.magic_power}"
        stats_surface = font.render(stats_text, True, (180, 180, 180))
        surface.blit(stats_surface, (x + 70, y + 55))
        
        # Requirements
        req_text = self._get_requirement_text(companion)
        req_color = (0, 255, 0) if companion.can_be_hired(self.player) else (255, 100, 100)
        req_surface = font.render(req_text, True, req_color)
        surface.blit(req_surface, (x + 430, y + 35))
        
        # Status
        if companion.is_resting:
            status = font.render("RESTING (1 month)", True, (255, 165, 0))
            surface.blit(status, (x + 430, y + 55))
        elif companion.can_be_hired(self.player):
            status = font.render("AVAILABLE", True, (0, 255, 0))
            surface.blit(status, (x + 430, y + 55))
        else:
            status = font.render("REQUIRES NOT MET", True, (255, 100, 100))
            surface.blit(status, (x + 430, y + 55))
    
    def _get_requirement_text(self, companion):
        """Get text for requirements"""
        req = companion.hire_level_requirement
        if "any" in req:
            return f"Requires: Level {req['any']}"
        parts = []
        if "level" in req:
            parts.append(f"Level {req['level']}")
        if "strength" in req:
            parts.append(f"Strength {req['strength']}")
        if "magic" in req:
            parts.append(f"Magic {req['magic']}")
        return "Requires: " + ", ".join(parts)
    
    def _draw_payment_ui(self, surface, font):
        """Draw payment interface"""
        if not self.payment_companion:
            return
        
        # Draw overlay panel
        panel = pygame.Surface((self.panel_width, self.panel_height))
        panel.set_alpha(240)
        panel.fill((20, 20, 30))
        pygame.draw.rect(panel, (100, 100, 120), (0, 0, self.panel_width, self.panel_height), 3)
        
        # Title
        title_font = pygame.font.SysFont(None, 32)
        title = title_font.render(f"💰 Payment for {self.payment_companion.name}", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.panel_width // 2, 30))
        panel.blit(title, title_rect)
        
        # Earnings owed
        owed_text = font.render(f"Payment Owed: {int(self.payment_companion.earnings_owed)} dubloons", True, (255, 100, 100))
        panel.blit(owed_text, (50, 80))
        
        # Player's resources
        player_dubloons = font.render(f"Your Dubloons: {self.player.dubloons}", True, (255, 215, 0))
        panel.blit(player_dubloons, (50, 110))
        
        # Payment options
        y_offset = 160
        options_title = font.render("Payment Options:", True, (200, 200, 200))
        panel.blit(options_title, (50, y_offset))
        
        y_offset += 30
        option1 = font.render("D: Pay with Dubloons", True, (150, 150, 255))
        panel.blit(option1, (70, y_offset))
        
        y_offset += 25
        option2 = font.render("I: Pay with Items (transfers items to companion)", True, (150, 150, 255))
        panel.blit(option2, (70, y_offset))
        
        # Transfer input
        if self.transfer_mode == "dubloons":
            y_offset += 50
            input_label = font.render("Enter amount:", True, (200, 200, 200))
            panel.blit(input_label, (50, y_offset))
            
            # Input box
            input_box = pygame.Rect(200, y_offset - 5, 150, 25)
            pygame.draw.rect(panel, (50, 50, 60), input_box)
            pygame.draw.rect(panel, (100, 150, 255), input_box, 2)
            
            # Input text
            input_text = font.render(self.transfer_amount, True, (255, 255, 255))
            panel.blit(input_text, (205, y_offset))
            
            # Submit instruction
            submit_text = font.render("Press ENTER to pay", True, (150, 150, 150))
            panel.blit(submit_text, (50, y_offset + 35))
        
        # Dismiss option
        y_offset = self.panel_height - 120
        dismiss_title = font.render("Dismiss Companion:", True, (200, 200, 200))
        panel.blit(dismiss_title, (50, y_offset))
        
        y_offset += 25
        dismiss_warning = font.render("If payment not in full, companion will contact the bank", True, (255, 165, 0))
        panel.blit(dismiss_warning, (70, y_offset))
        
        # Controls
        controls_y = self.panel_height - 40
        controls = font.render("ESC: Back | D: Dubloons | I: Items", True, (150, 150, 150))
        controls_rect = controls.get_rect(center=(self.panel_width // 2, controls_y))
        panel.blit(controls, controls_rect)
        
        # Blit to screen
        surface.blit(panel, (self.panel_x, self.panel_y))


class CompanionPaymentSystem:
    """Handles companion payment mechanics and bank debt integration"""
    
    def __init__(self, bank_system):
        self.bank_system = bank_system
    
    def dismiss_with_debt(self, companion, employer):
        """Dismiss companion with unpaid balance - creates bank debt"""
        if companion.earnings_owed <= 0:
            return True, "No payment owed. Companion dismissed."
        
        # Companion goes to bank, creates debt for employer
        debt_amount = int(companion.earnings_owed)
        
        # Create loan through bank system
        if hasattr(self.bank_system, 'take_loan'):
            # Use actual bank loan system
            success, loan_message = self.bank_system.take_loan(employer, debt_amount, self.game_time)
            if not success:
                # Fallback: add to wanted level if loan denied
                if not hasattr(employer, 'wanted_level'):
                    employer.wanted_level = 0
                employer.wanted_level += debt_amount
                print(f"[BANK] Loan denied. Bounty of {debt_amount}g added to employer")
        else:
            # Fallback: track as debt attribute
            if not hasattr(employer, 'companion_debt'):
                employer.companion_debt = 0
            employer.companion_debt += debt_amount
            print(f"[BANK] {debt_amount}g debt tracked for {employer.name}")
        
        print(f"[COMPANION] {companion.name}: Don't worry, I'll talk to the bank")
        print(f"[BANK] Debt of {debt_amount}g added for {employer.name}")
        
        # Reset companion earnings
        companion.earnings_owed = 0
        
        return True, f"{companion.name} went to the bank. You now owe {debt_amount}g."
    
    def calculate_earnings_from_loot(self, loot_value):
        """Calculate 30% earnings from loot value"""
        return loot_value * 0.3
    
    def transfer_item_payment(self, companion, employer, item_name, item_value):
        """Transfer item from employer to companion as payment"""
        # Remove from employer inventory
        if item_name in employer.inventory:
            employer.inventory[item_name] -= 1
            if employer.inventory[item_name] <= 0:
                del employer.inventory[item_name]
            
            # Add to companion inventory (will give to employer when dismissed)
            if item_name not in companion.inventory:
                companion.inventory[item_name] = 0
            companion.inventory[item_name] += 1
            
            # Reduce earnings owed
            companion.earnings_owed -= item_value
            if companion.earnings_owed < 0:
                companion.earnings_owed = 0
            
            return True, f"Transferred {item_name} (worth {item_value}g) as payment"
        
        return False, "You don't have that item"
