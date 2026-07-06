"""
NPC Skill Switching UI
Shows NPCs in training, their progress, and allows viewing of profession changes
"""
import pygame
from logger_config import logger


class NPCSkillSwitchingUI:
    """UI for viewing NPC profession changes and training progress"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.selected_tab = 0  # 0=training, 1=all NPCs, 2=history
        self.scroll_offset = 0
        self.selected_index = 0
        self.tabs = ["Training NPCs", "All NPCs", "Switch History"]
        
        # Colors
        self.bg_color = (20, 20, 30, 230)
        self.panel_color = (40, 40, 50)
        self.highlight_color = (80, 120, 180)
        self.text_color = (220, 220, 220)
        self.tab_active_color = (60, 100, 160)
        self.tab_inactive_color = (30, 30, 40)
        self.training_color = (255, 200, 100)
        self.cooldown_color = (255, 100, 100)
        
    def toggle(self):
        """Toggle UI visibility"""
        self.active = not self.active
        if self.active:
            self.scroll_offset = 0
            self.selected_index = 0
            logger.info("[SKILL SWITCH UI] Skill switching UI opened")
    
    def handle_input(self, event):
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
                # Max index depends on current tab content
                self.selected_index += 1
        
        return None
    
    def draw(self, screen, font, npc_skill_switching_system, gatherer_npc_manager):
        """Draw the skill switching UI"""
        if not self.active:
            return
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 1000
        panel_height = 700
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw title
        title_text = "NPC Profession Management"
        title_surf = font.render(title_text, True, self.text_color)
        screen.blit(title_surf, (panel_x + 20, panel_y + 15))
        
        # Draw tabs
        tab_y = panel_y + 60
        tab_width = 320
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
        content_height = panel_height - (content_y - panel_y) - 60
        
        if self.selected_tab == 0:
            self._draw_training_npcs(screen, font, npc_skill_switching_system, gatherer_npc_manager, panel_x, content_y, panel_width, content_height)
        elif self.selected_tab == 1:
            self._draw_all_npcs(screen, font, npc_skill_switching_system, gatherer_npc_manager, panel_x, content_y, panel_width, content_height)
        elif self.selected_tab == 2:
            self._draw_switch_history(screen, font, npc_skill_switching_system, panel_x, content_y, panel_width, content_height)
        
        # Draw stats summary
        stats_y = panel_y + panel_height - 50
        stats = npc_skill_switching_system.get_stats()
        stats_text = f"Active Training: {stats['active_training']} | Cooldowns: {stats['active_cooldowns']} | Total Switches: {stats['total_switches']}"
        stats_surf = font.render(stats_text, True, (180, 180, 180))
        screen.blit(stats_surf, (panel_x + 20, stats_y))
        
        # Draw controls hint
        controls_text = "TAB: Switch Tab | UP/DOWN: Navigate | ESC: Close"
        controls_surf = font.render(controls_text, True, (180, 180, 180))
        screen.blit(controls_surf, (panel_x + 20, stats_y + 25))
    
    def _draw_training_npcs(self, screen, font, system, npc_manager, x, y, width, height):
        """Draw NPCs currently in training"""
        item_height = 110
        y_offset = y + 10 - self.scroll_offset
        
        training_npcs = []
        for npc in npc_manager.npcs:
            training_info = system.get_training_info(npc)
            if training_info:
                training_npcs.append((npc, training_info))
        
        if not training_npcs:
            no_data_text = "No NPCs currently training"
            text_surf = font.render(no_data_text, True, (180, 180, 180))
            screen.blit(text_surf, (x + 20, y + 20))
            return
        
        for i, (npc, info) in enumerate(training_npcs):
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
            
            # NPC info
            name_text = f"{npc.name} - Level {npc.skills_manager.get_level(system.profession_skills.get(npc.gatherer_type, 'Mining'))}"
            switch_text = f"Training: {info['old_profession'].upper()} → {info['new_profession'].upper()}"
            progress_text = f"Progress: {int(info['progress'] * 100)}% ({info['days_remaining']} days remaining)"
            gold_text = f"Dubloons: {npc.dubloons}db | Location: {npc.town.name if npc.town else 'Unknown'}"
            
            # Progress bar
            bar_width = width - 60
            bar_height = 20
            bar_x = x + 30
            bar_y = y_offset + 68
            
            # Draw progress bar background
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            # Draw progress fill
            fill_width = int(bar_width * info['progress'])
            pygame.draw.rect(screen, self.training_color, (bar_x, bar_y, fill_width, bar_height))
            pygame.draw.rect(screen, self.text_color, (bar_x, bar_y, bar_width, bar_height), 1)
            
            text_surf = font.render(name_text, True, (100, 255, 100))
            screen.blit(text_surf, (x + 20, y_offset + 5))
            
            text_surf = font.render(switch_text, True, self.training_color)
            screen.blit(text_surf, (x + 20, y_offset + 28))
            
            text_surf = font.render(progress_text, True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 45))
            
            text_surf = font.render(gold_text, True, (200, 200, 100))
            screen.blit(text_surf, (x + 20, y_offset + 92))
            
            y_offset += item_height
    
    def _draw_all_npcs(self, screen, font, system, npc_manager, x, y, width, height):
        """Draw all gatherer NPCs with their profession info"""
        item_height = 95
        y_offset = y + 10 - self.scroll_offset
        
        for i, npc in enumerate(npc_manager.npcs):
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
            
            # Get NPC profession info
            current_skill = system.profession_skills.get(npc.gatherer_type, 'Mining')
            current_level = npc.skills_manager.get_level(current_skill)
            
            # Check if training or on cooldown
            training_info = system.get_training_info(npc)
            cooldown_info = system.get_cooldown_info(npc)
            
            # NPC info
            name_text = f"{npc.name} - {npc.gatherer_type.upper()} (Lvl {current_level})"
            gold_text = f"Dubloons: {npc.dubloons}db | Town: {npc.town.name if npc.town else 'Unknown'}"
            tool_text = f"Tool: {npc.tool.replace('_', ' ').title()}"
            
            status_text = "Status: Active"
            status_color = (100, 255, 100)
            
            if training_info:
                status_text = f"Status: Training {training_info['new_profession']} ({training_info['days_remaining']} days left)"
                status_color = self.training_color
            elif cooldown_info:
                status_text = f"Status: Cooldown ({cooldown_info['days_remaining']} days remaining)"
                status_color = self.cooldown_color
            
            text_surf = font.render(name_text, True, (100, 200, 255))
            screen.blit(text_surf, (x + 20, y_offset + 5))
            
            text_surf = font.render(gold_text, True, (200, 200, 100))
            screen.blit(text_surf, (x + 20, y_offset + 28))
            
            text_surf = font.render(tool_text, True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 50))
            
            text_surf = font.render(status_text, True, status_color)
            screen.blit(text_surf, (x + 20, y_offset + 72))
            
            y_offset += item_height
    
    def _draw_switch_history(self, screen, font, system, x, y, width, height):
        """Draw history of completed profession switches"""
        item_height = 85
        y_offset = y + 10 - self.scroll_offset
        
        if not system.switch_history:
            no_data_text = "No profession switches yet"
            text_surf = font.render(no_data_text, True, (180, 180, 180))
            screen.blit(text_surf, (x + 20, y + 20))
            return
        
        # Show most recent first
        history = list(reversed(system.switch_history))
        
        for i, record in enumerate(history):
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
            
            # Find NPC name (if still exists)
            npc_name = "Unknown NPC"
            # We can't easily map back to NPC without storing name in record
            # For now, show the profession change
            
            switch_text = f"Profession Change: {record.old_profession.upper()} → {record.new_profession.upper()}"
            days_text = f"Completed: Day {record.complete_day} (Training: {record.training_days} days)"
            levels_text = f"Old Skill Level: {record.old_skill_level} → Retained at ~{int(record.old_skill_level * 0.5)}"
            
            text_surf = font.render(switch_text, True, (150, 255, 150))
            screen.blit(text_surf, (x + 20, y_offset + 5))
            
            text_surf = font.render(days_text, True, self.text_color)
            screen.blit(text_surf, (x + 20, y_offset + 30))
            
            text_surf = font.render(levels_text, True, (200, 200, 100))
            screen.blit(text_surf, (x + 20, y_offset + 55))
            
            y_offset += item_height
