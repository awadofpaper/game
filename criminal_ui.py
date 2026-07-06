"""
Criminal Underworld UI
Comprehensive UI for all criminal activities
"""

import pygame
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class CriminalUnderworldUI:
    """Master UI for criminal underworld activities"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.mode = 'main'  # main, guild, gang, enterprise, heist, scam, launder
        
        # UI settings
        self.bg_color = (15, 10, 25, 220)
        self.panel_color = (25, 15, 35)
        self.text_color = (200, 200, 200)
        self.highlight_color = (180, 50, 50)  # Criminal red
        self.gold_color = (255, 215, 0)
        
        # Menu navigation
        self.selected_index = 0
        self.scroll_offset = 0
        
        # References (set from main)
        self.thieves_guild = None
        self.assassins_guild = None
        self.gang_manager = None
        self.criminal_rank_system = None
        self.protection_racket = None
        self.money_laundering = None
        self.enterprise_manager = None
        self.heist_manager = None
        self.favor_system = None
        self.criminal_skills = None
        self.market_manipulation = None
        self.scamming_system = None
        self.stolen_goods_appraiser = None
        self.criminal_quests = None
        
    def open(self):
        """Open UI"""
        self.active = True
        self.mode = 'main'
        self.selected_index = 0
        logger.info("[CRIMINAL UI] Opened")
    
    def close(self):
        """Close UI"""
        self.active = False
        logger.info("[CRIMINAL UI] Closed")
    
    def handle_input(self, event, player, game_time) -> Optional[str]:
        """Handle keyboard input"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.mode == 'main':
                    self.close()
                    return 'close'
                else:
                    self.mode = 'main'
                    self.selected_index = 0
                return None
            
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            
            elif event.key == pygame.K_DOWN:
                max_index = self._get_max_index()
                self.selected_index = min(max_index, self.selected_index + 1)
            
            elif event.key == pygame.K_RETURN:
                return self._handle_selection(player, game_time)
        
        return None
    
    def _get_max_index(self) -> int:
        """Get maximum index for current mode"""
        if self.mode == 'main':
            return 10  # Number of main menu options
        elif self.mode == 'guild':
            return 5
        elif self.mode == 'gang':
            return 4
        elif self.mode == 'enterprise':
            return 6
        elif self.mode == 'heist':
            return 3
        elif self.mode == 'scam':
            return 4
        elif self.mode == 'launder':
            return 5
        return 0
    
    def _handle_selection(self, player, game_time) -> Optional[str]:
        """Handle menu selection"""
        if self.mode == 'main':
            return self._handle_main_menu(player, game_time)
        elif self.mode == 'guild':
            return self._handle_guild_menu(player, game_time)
        elif self.mode == 'gang':
            return self._handle_gang_menu(player, game_time)
        elif self.mode == 'enterprise':
            return self._handle_enterprise_menu(player, game_time)
        elif self.mode == 'heist':
            return self._handle_heist_menu(player, game_time)
        elif self.mode == 'scam':
            return self._handle_scam_menu(player, game_time)
        elif self.mode == 'launder':
            return self._handle_launder_menu(player, game_time)
        return None
    
    def _handle_main_menu(self, player, game_time) -> Optional[str]:
        """Handle main menu selection"""
        options = [
            'view_status', 'guilds', 'gangs', 'enterprises', 'heists',
            'protection', 'laundering', 'scams', 'market', 'skills', 'quests'
        ]
        
        if self.selected_index < len(options):
            action = options[self.selected_index]
            
            if action == 'view_status':
                # Stay on main menu, shows status
                pass
            elif action == 'guilds':
                self.mode = 'guild'
                self.selected_index = 0
            elif action == 'gangs':
                self.mode = 'gang'
                self.selected_index = 0
            elif action == 'enterprises':
                self.mode = 'enterprise'
                self.selected_index = 0
            elif action == 'heists':
                self.mode = 'heist'
                self.selected_index = 0
            elif action == 'scams':
                self.mode = 'scam'
                self.selected_index = 0
            elif action == 'laundering':
                self.mode = 'launder'
                self.selected_index = 0
            elif action == 'skills':
                # Open skill tree (to be implemented)
                pass
            elif action == 'quests':
                # Show criminal quests
                pass
        
        return None
    
    def _handle_guild_menu(self, player, game_time) -> Optional[str]:
        """Handle guild menu"""
        # To be implemented
        return None
    
    def _handle_gang_menu(self, player, game_time) -> Optional[str]:
        """Handle gang menu"""
        # To be implemented
        return None
    
    def _handle_enterprise_menu(self, player, game_time) -> Optional[str]:
        """Handle enterprise menu"""
        # To be implemented
        return None
    
    def _handle_heist_menu(self, player, game_time) -> Optional[str]:
        """Handle heist menu"""
        # To be implemented
        return None
    
    def _handle_scam_menu(self, player, game_time) -> Optional[str]:
        """Handle scam menu"""
        # To be implemented
        return None
    
    def _handle_launder_menu(self, player, game_time) -> Optional[str]:
        """Handle laundering menu"""
        # To be implemented
        return None
    
    def draw(self, screen, player, game_time):
        """Draw UI"""
        if not self.active:
            return
        
        # Create semi-transparent background
        surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.bg_color, surface.get_rect())
        screen.blit(surface, (0, 0))
        
        # Draw main panel
        panel_width = 800
        panel_height = 600
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, self.panel_color, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, self.highlight_color, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Draw content based on mode
        if self.mode == 'main':
            self._draw_main_menu(screen, panel_x, panel_y, panel_width, panel_height, player)
        elif self.mode == 'guild':
            self._draw_guild_menu(screen, panel_x, panel_y, panel_width, panel_height, player)
        elif self.mode == 'gang':
            self._draw_gang_menu(screen, panel_x, panel_y, panel_width, panel_height, player)
        elif self.mode == 'enterprise':
            self._draw_enterprise_menu(screen, panel_x, panel_y, panel_width, panel_height, player)
        elif self.mode == 'heist':
            self._draw_heist_menu(screen, panel_x, panel_y, panel_width, panel_height, player)
        elif self.mode == 'scam':
            self._draw_scam_menu(screen, panel_x, panel_y, panel_width, panel_height, player)
        elif self.mode == 'launder':
            self._draw_launder_menu(screen, panel_x, panel_y, panel_width, panel_height, player)
    
    def _draw_main_menu(self, screen, x, y, width, height, player):
        """Draw main menu"""
        font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 24)
        
        # Title
        title = font.render("Criminal Underworld", True, self.highlight_color)
        screen.blit(title, (x + 20, y + 10))
        
        # Criminal status
        if self.criminal_rank_system:
            rank = self.criminal_rank_system.get_current_rank()
            status_text = f"Rank: {rank['name']} | Crimes: {self.criminal_rank_system.crime_count}"
            status_surf = small_font.render(status_text, True, self.text_color)
            screen.blit(status_surf, (x + 20, y + 50))
            
            # Heat level
            heat_text = f"Heat: {self.criminal_rank_system.heat}/100"
            heat_color = (255, int(255 * (1 - self.criminal_rank_system.heat / 100)), 0)
            heat_surf = small_font.render(heat_text, True, heat_color)
            screen.blit(heat_surf, (x + 400, y + 50))
        
        # Menu options
        options = [
            ("View Status", "Current criminal standing and perks"),
            ("Crime Syndicates", "Thieves & Assassins Guilds"),
            ("Gang Operations", "Manage gangs and territories"),
            ("Criminal Enterprises", "Passive income businesses"),
            ("Heist Planning", "Plan and execute heists"),
            ("Protection Racket", "Extort businesses for money"),
            ("Money Laundering", "Clean dirty money"),
            ("Scams & Cons", "Create fake items and run schemes"),
            ("Market Manipulation", "Control prices and create scarcity"),
            ("Criminal Skills", "Upgrade criminal abilities"),
            ("Quest Network", "Criminal quest paths")
        ]
        
        start_y = y + 100
        for i, (option, desc) in enumerate(options):
            color = self.gold_color if i == self.selected_index else self.text_color
            
            # Option name
            option_surf = font.render(option, True, color)
            screen.blit(option_surf, (x + 40, start_y + i * 45))
            
            # Description
            desc_surf = small_font.render(desc, True, self.text_color)
            screen.blit(desc_surf, (x + 60, start_y + i * 45 + 25))
        
        # Instructions
        inst_text = "↑↓: Navigate | ENTER: Select | ESC: Close"
        inst_surf = small_font.render(inst_text, True, self.text_color)
        screen.blit(inst_surf, (x + 20, y + height - 30))
    
    def _draw_guild_menu(self, screen, x, y, width, height, player):
        """Draw guild menu"""
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        
        title = font.render("Crime Syndicates", True, self.highlight_color)
        screen.blit(title, (x + 20, y + 10))
        
        info_lines = [
            "Join criminal organizations for exclusive benefits:",
            "",
            "Thieves Guild - Master stealth and lockpicking",
            "Assassins Guild - Lethal contracts and infiltration",
            "Smugglers Network - Black market trading routes",
            "",
            "Each guild offers unique skills, quests, and rewards.",
            "Build reputation to unlock higher-tier operations."
        ]
        
        for i, line in enumerate(info_lines):
            text = small_font.render(line, True, self.text_color)
            screen.blit(text, (x + 20, y + 50 + i * 25))
    
    def _draw_gang_menu(self, screen, x, y, width, height, player):
        """Draw gang menu"""
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        
        title = font.render("Gang Operations", True, self.highlight_color)
        screen.blit(title, (x + 20, y + 10))
        
        info_lines = [
            "Control territory and build your criminal empire:",
            "",
            "Recruit gang members with unique skills",
            "Establish protection rackets in towns",
            "Defend territory from rival gangs",
            "Expand influence through intimidation",
            "",
            "Manage gang loyalty, resources, and reputation."
        ]
        
        for i, line in enumerate(info_lines):
            text = small_font.render(line, True, self.text_color)
            screen.blit(text, (x + 20, y + 50 + i * 25))
    
    def _draw_enterprise_menu(self, screen, x, y, width, height, player):
        """Draw enterprise menu"""
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        
        title = font.render("Criminal Enterprises", True, self.highlight_color)
        screen.blit(title, (x + 20, y + 10))
        
        info_lines = [
            "Establish illegal business operations:",
            "",
            "Gambling Dens - High-risk, high-reward betting",
            "Counterfeiting Shops - Forge coins and documents",
            "Smuggling Routes - Transport contraband",
            "Underground Markets - Sell stolen goods",
            "",
            "Manage operations, avoid law enforcement."
        ]
        
        for i, line in enumerate(info_lines):
            text = small_font.render(line, True, self.text_color)
            screen.blit(text, (x + 20, y + 50 + i * 25))
    
    def _draw_heist_menu(self, screen, x, y, width, height, player):
        """Draw heist menu"""
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        
        title = font.render("Heist Planning", True, self.highlight_color)
        screen.blit(title, (x + 20, y + 10))
        
        info_lines = [
            "Plan and execute high-stakes robberies:",
            "",
            "Scout locations and identify weak points",
            "Recruit skilled crew members (hacker, muscle, driver)",
            "Choose approach: Stealth, Force, or Deception",
            "Escape with the loot and evade pursuers",
            "",
            "Risk vs Reward: Bigger heists = Bigger bounties!"
        ]
        
        for i, line in enumerate(info_lines):
            text = small_font.render(line, True, self.text_color)
            screen.blit(text, (x + 20, y + 50 + i * 25))
    
    def _draw_scam_menu(self, screen, x, y, width, height, player):
        """Draw scam menu"""
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        
        title = font.render("Scams & Cons", True, self.highlight_color)
        screen.blit(title, (x + 20, y + 10))
        
        info_lines = [
            "Use deception and manipulation for profit:",
            "",
            "Confidence Tricks - Earn trust, then exploit it",
            "Fake Investments - Promise returns, disappear",
            "Market Manipulation - Spread rumors, profit",
            "Identity Theft - Impersonate wealthy targets",
            "",
            "Higher charisma = More convincing scams!"
        ]
        
        for i, line in enumerate(info_lines):
            text = small_font.render(line, True, self.text_color)
            screen.blit(text, (x + 20, y + 50 + i * 25))
    
    def _draw_launder_menu(self, screen, x, y, width, height, player):
        """Draw laundering menu"""
        font = pygame.font.Font(None, 28)
        
        title = font.render("Money Laundering", True, self.highlight_color)
        screen.blit(title, (x + 20, y + 10))
        
        if self.money_laundering:
            info_lines = [
                f"Dirty Money: {self.money_laundering.dirty_money}g",
                f"Clean Money: {self.money_laundering.clean_money}g",
                f"Suspicion: {self.money_laundering.get_suspicion_status()}",
                f"Active Operations: {len(self.money_laundering.active_operations)}"
            ]
            
            for i, line in enumerate(info_lines):
                surf = font.render(line, True, self.text_color)
                screen.blit(surf, (x + 20, y + 50 + i * 30))


# Global instance
criminal_ui = None

def get_criminal_ui(screen_width: int = 1920, screen_height: int = 1080) -> CriminalUnderworldUI:
    """Get or create global criminal UI instance"""
    global criminal_ui
    if criminal_ui is None:
        criminal_ui = CriminalUnderworldUI(screen_width, screen_height)
    return criminal_ui
