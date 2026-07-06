"""
Mayor Powers UI
Provides interface for player-mayors to activate/deactivate their powers
"""

import pygame

class MayorPowersUI:
    """UI for mayor to manage their powers and view town info"""
    
    def __init__(self):
        self.active = False
        self.selected_option = 0
        self.showing_confirmation = False
        self.confirmation_action = None
        self.confirmation_message = ""
        
        # Current town being managed
        self.current_town = None
        
        # Systems references (set externally)
        self.curfew_system = None
        self.weapon_restriction_system = None
        self.town_entry_fee_system = None
        self.embargo_system = None
        self.town_treasury_system = None
        self.game_time = None
        
        # Colors
        self.bg_color = (20, 20, 35, 240)
        self.panel_color = (35, 35, 60)
        self.border_color = (120, 120, 180)
        self.header_color = (255, 215, 0)  # Gold
        self.text_color = (255, 255, 255)
        self.active_color = (100, 255, 100)  # Green
        self.inactive_color = (200, 100, 100)  # Red
        self.selected_color = (255, 255, 100)
        self.disabled_color = (120, 120, 120)
        
    def open(self, town_name):
        """Open the mayor powers menu for a specific town"""
        self.active = True
        self.current_town = town_name
        self.selected_option = 0
        self.showing_confirmation = False
        
    def close(self):
        """Close the mayor powers menu"""
        self.active = False
        self.showing_confirmation = False
        self.current_town = None
        
    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.active:
            return None
            
        if event.type != pygame.KEYDOWN:
            return None
        
        # Confirmation dialog input
        if self.showing_confirmation:
            if event.key == pygame.K_y:
                # Execute the confirmed action
                result = self._execute_action(self.confirmation_action)
                self.showing_confirmation = False
                return result
            elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                # Cancel
                self.showing_confirmation = False
                return None
            return None
        
        # Main menu input
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 5
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 5
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            return self._handle_selection()
        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
            self.close()
            return "closed"
            
        return None
    
    def _handle_selection(self):
        """Handle menu selection"""
        if self.selected_option == 0:
            # Toggle Curfew
            if self.curfew_system and self.current_town:
                is_active = self.curfew_system.is_curfew_active(self.current_town)
                if is_active:
                    # Disable curfew
                    self.curfew_system.disable_curfew(self.current_town)
                    return "curfew_disabled"
                else:
                    # Enable curfew - show confirmation
                    self.showing_confirmation = True
                    self.confirmation_action = "enable_curfew"
                    self.confirmation_message = f"Enable curfew in {self.current_town}?\n\nCitizens must be indoors from {self.curfew_system.curfew_start}:00 to {self.curfew_system.curfew_end}:00\nViolators will be fined {self.curfew_system.fine_amount}g by guards"
                    return None
                    
        elif self.selected_option == 1:
            # Toggle Weapon Restrictions
            if self.weapon_restriction_system:
                if self.weapon_restriction_system.restriction_active:
                    # Disable restrictions
                    self.weapon_restriction_system.restriction_active = False
                    return "weapon_restrictions_disabled"
                else:
                    # Enable restrictions - show confirmation
                    self.showing_confirmation = True
                    self.confirmation_action = "enable_weapons"
                    self.confirmation_message = "Enable weapon restrictions?\n\nAll weapons will be confiscated at town gates\nStored in Town Hall guard locker"
                    return None
                    
        elif self.selected_option == 2:
            # Toggle Entry Fees
            if self.town_entry_fee_system:
                if self.town_entry_fee_system.lockdown_active:
                    # Disable entry fee
                    self.town_entry_fee_system.lockdown_active = False
                    return "entry_fee_disabled"
                else:
                    # Enable entry fee - show confirmation
                    self.showing_confirmation = True
                    self.confirmation_action = "enable_entry_fee"
                    self.confirmation_message = f"Enable town entry fee?\n\nCharge {self.town_entry_fee_system.entry_fee}g to enter {self.current_town}\nFunds go to town treasury"
                    return None
                    
        elif self.selected_option == 3:
            # Start Embargo
            if self.embargo_system:
                if self.embargo_system.embargo_active:
                    # Show info about active embargo
                    days_remaining = self.embargo_system.embargo_duration - (self.game_time.day_count - self.embargo_system.embargo_start_day)
                    return f"embargo_info:{days_remaining}"
                else:
                    # Start embargo - show confirmation
                    self.showing_confirmation = True
                    self.confirmation_action = "start_embargo"
                    self.confirmation_message = f"Start trade embargo?\n\nAll sales will incur {int(self.embargo_system.embargo_fee_percent*100)}% fee\nLasts {self.embargo_system.embargo_duration} days\nSeverely impacts merchants"
                    return None
                    
        elif self.selected_option == 4:
            # View Treasury (info only)
            if self.town_treasury_system and self.current_town:
                balance = self.town_treasury_system.get_balance(self.current_town)
                return f"treasury_info:{balance}"
                
        return None
    
    def _execute_action(self, action):
        """Execute a confirmed action"""
        if action == "enable_curfew":
            if self.curfew_system and self.current_town:
                self.curfew_system.enable_curfew(self.current_town)
                return "curfew_enabled"
                
        elif action == "enable_weapons":
            if self.weapon_restriction_system:
                self.weapon_restriction_system.restriction_active = True
                return "weapon_restrictions_enabled"
                
        elif action == "enable_entry_fee":
            if self.town_entry_fee_system:
                self.town_entry_fee_system.lockdown_active = True
                return "entry_fee_enabled"
                
        elif action == "start_embargo":
            if self.embargo_system and self.game_time:
                self.embargo_system.start_embargo(self.game_time)
                return "embargo_started"
                
        return None
    
    def draw(self, screen, font):
        """Draw the mayor powers menu"""
        if not self.active:
            return
            
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if self.showing_confirmation:
            self._draw_confirmation(screen, font, screen_width, screen_height)
        else:
            self._draw_main_menu(screen, font, screen_width, screen_height)
    
    def _draw_main_menu(self, screen, font, screen_width, screen_height):
        """Draw the main mayor powers menu"""
        # Panel dimensions
        panel_width = 700
        panel_height = 600
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Background panel
        pygame.draw.rect(screen, self.panel_color, (panel_x, panel_y, panel_width, panel_height), border_radius=12)
        pygame.draw.rect(screen, self.border_color, (panel_x, panel_y, panel_width, panel_height), 4, border_radius=12)
        
        # Header
        header_font = pygame.font.SysFont(None, 48, bold=True)
        header = header_font.render("👑 MAYOR POWERS", True, self.header_color)
        screen.blit(header, (panel_x + panel_width//2 - header.get_width()//2, panel_y + 20))
        
        # Town name
        town_font = pygame.font.SysFont(None, 28)
        if self.current_town:
            town_text = town_font.render(f"Managing: {self.current_town}", True, (200, 200, 200))
            screen.blit(town_text, (panel_x + panel_width//2 - town_text.get_width()//2, panel_y + 70))
        
        # Menu options
        option_y = panel_y + 130
        option_height = 70
        menu_font = pygame.font.SysFont(None, 32)
        status_font = pygame.font.SysFont(None, 24)
        
        options = [
            {
                "name": "Curfew Control",
                "status": self._get_curfew_status(),
                "info": f"{self.curfew_system.curfew_start}:00-{self.curfew_system.curfew_end}:00, Fine: {self.curfew_system.fine_amount}g"
            },
            {
                "name": "Weapon Restrictions",
                "status": self._get_weapon_status(),
                "info": "Confiscate all weapons at gates"
            },
            {
                "name": "Town Entry Fee",
                "status": self._get_entry_fee_status(),
                "info": f"{self.town_entry_fee_system.entry_fee}g to enter town"
            },
            {
                "name": "Trade Embargo",
                "status": self._get_embargo_status(),
                "info": f"{int(self.embargo_system.embargo_fee_percent*100)}% fee on sales, {self.embargo_system.embargo_duration} days"
            },
            {
                "name": "View Town Treasury",
                "status": self._get_treasury_balance(),
                "info": "Total funds available"
            }
        ]
        
        for i, option in enumerate(options):
            is_selected = (i == self.selected_option)
            
            # Option background
            option_rect = pygame.Rect(panel_x + 20, option_y + i * option_height, panel_width - 40, option_height - 10)
            
            if is_selected:
                pygame.draw.rect(screen, (60, 60, 100), option_rect, border_radius=8)
                pygame.draw.rect(screen, self.selected_color, option_rect, 3, border_radius=8)
            else:
                pygame.draw.rect(screen, (40, 40, 65), option_rect, border_radius=8)
            
            # Option name
            name_color = self.selected_color if is_selected else self.text_color
            name_text = menu_font.render(option["name"], True, name_color)
            screen.blit(name_text, (option_rect.x + 15, option_rect.y + 8))
            
            # Status indicator
            status_color = self.active_color if "ACTIVE" in option["status"] or "ENABLED" in option["status"] else (
                self.inactive_color if "INACTIVE" in option["status"] or "DISABLED" in option["status"] else (220, 220, 220)
            )
            status_text = status_font.render(option["status"], True, status_color)
            screen.blit(status_text, (option_rect.x + 15, option_rect.y + 38))
            
            # Info text
            info_text = status_font.render(option["info"], True, (180, 180, 180))
            screen.blit(info_text, (option_rect.x + option_rect.width - info_text.get_width() - 15, option_rect.y + 38))
        
        # Instructions
        instructions_y = panel_y + panel_height - 60
        inst_font = pygame.font.SysFont(None, 24)
        instructions = [
            "↑/↓: Navigate  |  ENTER/SPACE: Select  |  M/ESC: Close"
        ]
        for i, instruction in enumerate(instructions):
            inst_text = inst_font.render(instruction, True, (180, 180, 200))
            screen.blit(inst_text, (panel_x + panel_width//2 - inst_text.get_width()//2, instructions_y + i * 25))
    
    def _draw_confirmation(self, screen, font, screen_width, screen_height):
        """Draw confirmation dialog"""
        # Confirmation panel
        conf_width = 600
        conf_height = 350
        conf_x = (screen_width - conf_width) // 2
        conf_y = (screen_height - conf_height) // 2
        
        # Background
        pygame.draw.rect(screen, (40, 20, 20), (conf_x, conf_y, conf_width, conf_height), border_radius=10)
        pygame.draw.rect(screen, (200, 100, 100), (conf_x, conf_y, conf_width, conf_height), 4, border_radius=10)
        
        # Warning icon
        warning_font = pygame.font.SysFont(None, 72)
        warning = warning_font.render("⚠️", True, (255, 200, 0))
        screen.blit(warning, (conf_x + conf_width//2 - warning.get_width()//2, conf_y + 20))
        
        # Confirmation message
        msg_font = pygame.font.SysFont(None, 28)
        msg_y = conf_y + 100
        for line in self.confirmation_message.split('\n'):
            if line.strip():
                msg_text = msg_font.render(line.strip(), True, (255, 255, 255))
                screen.blit(msg_text, (conf_x + conf_width//2 - msg_text.get_width()//2, msg_y))
                msg_y += 35
        
        # Yes/No buttons
        button_font = pygame.font.SysFont(None, 36, bold=True)
        yes_text = button_font.render("Y - CONFIRM", True, (100, 255, 100))
        no_text = button_font.render("N - CANCEL", True, (255, 100, 100))
        
        button_y = conf_y + conf_height - 80
        screen.blit(yes_text, (conf_x + conf_width//4 - yes_text.get_width()//2, button_y))
        screen.blit(no_text, (conf_x + 3*conf_width//4 - no_text.get_width()//2, button_y))
    
    def _get_curfew_status(self):
        """Get curfew status text"""
        if not self.curfew_system or not self.current_town:
            return "UNAVAILABLE"
        return "ACTIVE" if self.curfew_system.is_curfew_active(self.current_town) else "INACTIVE"
    
    def _get_weapon_status(self):
        """Get weapon restriction status text"""
        if not self.weapon_restriction_system:
            return "UNAVAILABLE"
        return "ENABLED" if self.weapon_restriction_system.restriction_active else "DISABLED"
    
    def _get_entry_fee_status(self):
        """Get entry fee status text"""
        if not self.town_entry_fee_system:
            return "UNAVAILABLE"
        return "ENABLED" if self.town_entry_fee_system.lockdown_active else "DISABLED"
    
    def _get_embargo_status(self):
        """Get embargo status text"""
        if not self.embargo_system:
            return "UNAVAILABLE"
        if self.embargo_system.embargo_active:
            if self.game_time:
                days_left = self.embargo_system.embargo_duration - (self.game_time.day_count - self.embargo_system.embargo_start_day)
                return f"ACTIVE ({days_left} days left)"
            return "ACTIVE"
        return "INACTIVE"
    
    def _get_treasury_balance(self):
        """Get town treasury balance"""
        if not self.town_treasury_system or not self.current_town:
            return "N/A"
        balance = self.town_treasury_system.get_balance(self.current_town)
        return f"{balance}g"
