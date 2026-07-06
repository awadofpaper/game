"""
Leaderboard UI - Display skill rankings

Press L to open/close leaderboard
Navigate with arrow keys and Tab
"""

import pygame
from typing import Optional


class LeaderboardUI:
    """UI for displaying skill leaderboards"""
    
    def __init__(self, config, leaderboard_system):
        self.config = config
        self.leaderboard_system = leaderboard_system
        self.active = False
        
        # UI state
        self.selected_skill_idx = 0  # Which skill tab is selected
        self.scroll_offset = 0  # Scrolling through rankings
        self.show_overall = False  # Show overall rankings vs specific skill
        
        # Available skills + Overall
        self.skill_tabs = leaderboard_system.SKILLS + ['Overall']
        
        # Colors
        self.bg_color = (20, 15, 25, 240)
        self.border_color = (100, 80, 150)
        self.tab_active_color = (80, 60, 120)
        self.tab_inactive_color = (40, 30, 60)
        self.rank_colors = {
            1: (255, 215, 0),    # Gold
            2: (192, 192, 192),  # Silver
            3: (205, 127, 50),   # Bronze
        }
        self.highlight_color = (120, 100, 200, 100)
    
    def open(self):
        """Open the leaderboard UI"""
        self.active = True
        self.scroll_offset = 0
    
    def close(self):
        """Close the leaderboard UI"""
        if self.active:
            # Save leaderboards when closing
            self.leaderboard_system.save()
        self.active = False
    
    def toggle(self):
        """Toggle leaderboard visibility"""
        if self.active:
            self.close()
        else:
            self.open()
    
    def handle_input(self, event, player_name: str):
        """Handle keyboard input"""
        if not self.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_l:
                self.close()
            
            elif event.key == pygame.K_LEFT:
                # Previous skill tab
                self.selected_skill_idx = (self.selected_skill_idx - 1) % len(self.skill_tabs)
                self.scroll_offset = 0
                self.show_overall = (self.selected_skill_idx == len(self.skill_tabs) - 1)
            
            elif event.key == pygame.K_RIGHT:
                # Next skill tab
                self.selected_skill_idx = (self.selected_skill_idx + 1) % len(self.skill_tabs)
                self.scroll_offset = 0
                self.show_overall = (self.selected_skill_idx == len(self.skill_tabs) - 1)
            
            elif event.key == pygame.K_TAB:
                # Cycle through skills
                self.selected_skill_idx = (self.selected_skill_idx + 1) % len(self.skill_tabs)
                self.scroll_offset = 0
                self.show_overall = (self.selected_skill_idx == len(self.skill_tabs) - 1)
            
            elif event.key == pygame.K_UP:
                # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            
            elif event.key == pygame.K_DOWN:
                # Scroll down
                if self.show_overall:
                    max_entries = len(self.leaderboard_system.get_overall_rankings())
                else:
                    skill_name = self.skill_tabs[self.selected_skill_idx]
                    max_entries = len(self.leaderboard_system.get_rankings(skill_name))
                
                visible_count = 15
                self.scroll_offset = min(max(0, max_entries - visible_count), self.scroll_offset + 1)
    
    def draw(self, screen, player_name: str):
        """Draw the leaderboard UI"""
        if not self.active:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Main panel dimensions
        panel_width = 1000
        panel_height = 700
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        # Main background
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill(self.bg_color)
        pygame.draw.rect(panel_bg, self.border_color, (0, 0, panel_width, panel_height), 4)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 56, bold=True)
        title = title_font.render("SKILL LEADERBOARDS", True, (200, 180, 255))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Draw skill tabs
        tab_y = panel_y + 90
        self._draw_tabs(screen, panel_x, tab_y, panel_width)
        
        # Draw rankings
        content_y = tab_y + 60
        if self.show_overall:
            self._draw_overall_rankings(screen, panel_x, content_y, panel_width, panel_height - (content_y - panel_y), player_name)
        else:
            skill_name = self.skill_tabs[self.selected_skill_idx]
            self._draw_skill_rankings(screen, panel_x, content_y, panel_width, panel_height - (content_y - panel_y), skill_name, player_name)
        
        # Instructions
        instr_y = panel_y + panel_height - 50
        instr_font = pygame.font.SysFont(None, 22)
        instructions = ["←→/TAB: Switch Skills", "↑↓: Scroll", "L/ESC: Close"]
        
        instr_x = panel_x + 30
        for instruction in instructions:
            instr = instr_font.render(instruction, True, (180, 180, 180))
            screen.blit(instr, (instr_x, instr_y))
            instr_x += 280
    
    def _draw_tabs(self, screen, x, y, width):
        """Draw skill selection tabs"""
        tab_width = width // len(self.skill_tabs)
        tab_font = pygame.font.SysFont(None, 24, bold=True)
        
        for i, skill in enumerate(self.skill_tabs):
            is_selected = (i == self.selected_skill_idx)
            tab_x = x + i * tab_width
            
            # Tab background
            tab_color = self.tab_active_color if is_selected else self.tab_inactive_color
            tab_bg = pygame.Surface((tab_width, 50), pygame.SRCALPHA)
            tab_bg.fill(tab_color)
            
            if is_selected:
                pygame.draw.rect(tab_bg, self.border_color, (0, 0, tab_width, 50), 3)
            else:
                pygame.draw.rect(tab_bg, (60, 50, 80), (0, 0, tab_width, 50), 1)
            
            screen.blit(tab_bg, (tab_x, y))
            
            # Tab text
            text_color = (255, 255, 255) if is_selected else (150, 150, 150)
            text = tab_font.render(skill, True, text_color)
            text_x = tab_x + tab_width // 2 - text.get_width() // 2
            text_y = y + 25 - text.get_height() // 2
            screen.blit(text, (text_x, text_y))
    
    def _draw_skill_rankings(self, screen, x, y, width, height, skill_name, player_name):
        """Draw rankings for a specific skill"""
        rankings = self.leaderboard_system.get_rankings(skill_name, limit=50)
        
        if not rankings:
            # No data
            no_data_font = pygame.font.SysFont(None, 36)
            no_data = no_data_font.render("No rankings yet!", True, (150, 150, 150))
            screen.blit(no_data, (x + width // 2 - no_data.get_width() // 2, y + 100))
            return
        
        # Headers
        header_font = pygame.font.SysFont(None, 28, bold=True)
        header_y = y + 10
        
        headers = [
            ("Rank", 50),
            ("Player", 200),
            ("Level", 400),
            ("Experience", 550),
            ("Last Updated", 750)
        ]
        
        for header_text, header_x in headers:
            header = header_font.render(header_text, True, (200, 200, 200))
            screen.blit(header, (x + header_x, header_y))
        
        # Draw line under headers
        pygame.draw.line(screen, (100, 100, 100), (x + 30, header_y + 35), (x + width - 30, header_y + 35), 2)
        
        # Draw rankings
        entry_font = pygame.font.SysFont(None, 24)
        entry_start_y = header_y + 50
        entry_height = 35
        visible_count = 15
        
        # Get player's rank for highlighting
        player_rank_data = self.leaderboard_system.get_player_rank(player_name, skill_name)
        player_rank = player_rank_data[0] if player_rank_data else None
        
        for i in range(self.scroll_offset, min(self.scroll_offset + visible_count, len(rankings))):
            entry = rankings[i]
            rank = i + 1
            entry_y = entry_start_y + (i - self.scroll_offset) * entry_height
            
            # Highlight current player
            is_player = (entry.player_name == player_name)
            if is_player:
                highlight_bg = pygame.Surface((width - 60, entry_height - 2), pygame.SRCALPHA)
                highlight_bg.fill(self.highlight_color)
                screen.blit(highlight_bg, (x + 30, entry_y))
            
            # Rank (with medal colors for top 3)
            rank_color = self.rank_colors.get(rank, (200, 200, 200))
            rank_text = entry_font.render(f"#{rank}", True, rank_color)
            screen.blit(rank_text, (x + 50, entry_y + 5))
            
            # Player name
            name_color = (255, 255, 100) if is_player else (220, 220, 220)
            name_text = entry_font.render(entry.player_name[:20], True, name_color)
            screen.blit(name_text, (x + 200, entry_y + 5))
            
            # Level
            level_text = entry_font.render(str(entry.level), True, (150, 255, 150))
            screen.blit(level_text, (x + 400, entry_y + 5))
            
            # Experience
            xp_text = entry_font.render(f"{entry.xp:,}", True, (150, 200, 255))
            screen.blit(xp_text, (x + 550, entry_y + 5))
            
            # Last updated
            updated_text = entry_font.render(entry.last_updated[:16], True, (180, 180, 180))
            screen.blit(updated_text, (x + 750, entry_y + 5))
        
        # Show player's rank if not visible in current scroll
        if player_rank and (player_rank - 1 < self.scroll_offset or player_rank - 1 >= self.scroll_offset + visible_count):
            rank_info_y = y + height - 60
            rank_info_font = pygame.font.SysFont(None, 26, bold=True)
            rank_info = rank_info_font.render(f"Your Rank: #{player_rank} (Level {player_rank_data[1].level}, {player_rank_data[1].xp:,} XP)", True, (255, 255, 100))
            
            # Background for rank info
            rank_bg = pygame.Surface((rank_info.get_width() + 40, 40), pygame.SRCALPHA)
            rank_bg.fill((40, 30, 60, 220))
            pygame.draw.rect(rank_bg, self.border_color, (0, 0, rank_bg.get_width(), 40), 2)
            
            screen.blit(rank_bg, (x + width // 2 - rank_bg.get_width() // 2, rank_info_y - 5))
            screen.blit(rank_info, (x + width // 2 - rank_info.get_width() // 2, rank_info_y))
        elif not player_rank:
            # Player not ranked yet
            rank_info_y = y + height - 60
            rank_info_font = pygame.font.SysFont(None, 26)
            rank_info = rank_info_font.render(f"You are not ranked in {skill_name} yet!", True, (200, 150, 150))
            screen.blit(rank_info, (x + width // 2 - rank_info.get_width() // 2, rank_info_y))
    
    def _draw_overall_rankings(self, screen, x, y, width, height, player_name):
        """Draw overall rankings based on total level"""
        rankings = self.leaderboard_system.get_overall_rankings(limit=50)
        
        if not rankings:
            # No data
            no_data_font = pygame.font.SysFont(None, 36)
            no_data = no_data_font.render("No rankings yet!", True, (150, 150, 150))
            screen.blit(no_data, (x + width // 2 - no_data.get_width() // 2, y + 100))
            return
        
        # Headers
        header_font = pygame.font.SysFont(None, 28, bold=True)
        header_y = y + 10
        
        headers = [
            ("Rank", 50),
            ("Player", 200),
            ("Total Level", 400)
        ]
        
        for header_text, header_x in headers:
            header = header_font.render(header_text, True, (200, 200, 200))
            screen.blit(header, (x + header_x, header_y))
        
        # Draw line under headers
        pygame.draw.line(screen, (100, 100, 100), (x + 30, header_y + 35), (x + width - 30, header_y + 35), 2)
        
        # Draw rankings
        entry_font = pygame.font.SysFont(None, 24)
        entry_start_y = header_y + 50
        entry_height = 35
        visible_count = 15
        
        # Get player's rank for highlighting
        player_rank = None
        for i, (name, total) in enumerate(rankings):
            if name == player_name:
                player_rank = i + 1
                break
        
        for i in range(self.scroll_offset, min(self.scroll_offset + visible_count, len(rankings))):
            name, total_level = rankings[i]
            rank = i + 1
            entry_y = entry_start_y + (i - self.scroll_offset) * entry_height
            
            # Highlight current player
            is_player = (name == player_name)
            if is_player:
                highlight_bg = pygame.Surface((width - 60, entry_height - 2), pygame.SRCALPHA)
                highlight_bg.fill(self.highlight_color)
                screen.blit(highlight_bg, (x + 30, entry_y))
            
            # Rank (with medal colors for top 3)
            rank_color = self.rank_colors.get(rank, (200, 200, 200))
            rank_text = entry_font.render(f"#{rank}", True, rank_color)
            screen.blit(rank_text, (x + 50, entry_y + 5))
            
            # Player name
            name_color = (255, 255, 100) if is_player else (220, 220, 220)
            name_text = entry_font.render(name[:30], True, name_color)
            screen.blit(name_text, (x + 200, entry_y + 5))
            
            # Total level
            level_text = entry_font.render(str(total_level), True, (150, 255, 150))
            screen.blit(level_text, (x + 400, entry_y + 5))
        
        # Show player's rank if not visible in current scroll
        if player_rank and (player_rank - 1 < self.scroll_offset or player_rank - 1 >= self.scroll_offset + visible_count):
            player_total = self.leaderboard_system.get_player_total_level(player_name)
            rank_info_y = y + height - 60
            rank_info_font = pygame.font.SysFont(None, 26, bold=True)
            rank_info = rank_info_font.render(f"Your Overall Rank: #{player_rank} (Total Level: {player_total})", True, (255, 255, 100))
            
            # Background for rank info
            rank_bg = pygame.Surface((rank_info.get_width() + 40, 40), pygame.SRCALPHA)
            rank_bg.fill((40, 30, 60, 220))
            pygame.draw.rect(rank_bg, self.border_color, (0, 0, rank_bg.get_width(), 40), 2)
            
            screen.blit(rank_bg, (x + width // 2 - rank_bg.get_width() // 2, rank_info_y - 5))
            screen.blit(rank_info, (x + width // 2 - rank_info.get_width() // 2, rank_info_y))
        elif not player_rank:
            # Player not ranked yet
            player_total = self.leaderboard_system.get_player_total_level(player_name)
            rank_info_y = y + height - 60
            rank_info_font = pygame.font.SysFont(None, 26)
            if player_total > 0:
                rank_info = rank_info_font.render(f"Your Total Level: {player_total} (Not in Top 50)", True, (200, 200, 150))
            else:
                rank_info = rank_info_font.render("You are not ranked yet! Start training skills!", True, (200, 150, 150))
            screen.blit(rank_info, (x + width // 2 - rank_info.get_width() // 2, rank_info_y))
