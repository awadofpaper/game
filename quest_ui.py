"""
Quest UI - Quest log and quest tracker
"""

import pygame
from quest_system import QuestState, QuestType, QuestCategory

class QuestLogUI:
    """Quest log menu (accessed with L key)"""
    
    def __init__(self):
        self.active = False
        self.selected_tab = 0  # 0=active, 1=completed, 2=available
        self.selected_quest_idx = 0
        self.scroll_offset = 0
        
    def toggle(self):
        """Toggle quest log on/off"""
        self.active = not self.active
        if self.active:
            self.selected_quest_idx = 0
            self.scroll_offset = 0
    
    def draw(self, screen, font, quest_manager, player):
        """Draw the quest log"""
        if not self.active:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 900
        panel_height = 650
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Draw panel background
        pygame.draw.rect(screen, (30, 30, 50), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 150), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Quest Log", True, (255, 255, 180))
        screen.blit(title, (panel_x + 20, panel_y + 15))
        
        # Tabs
        tabs = ["Active", "Completed", "Available"]
        tab_width = 120
        tab_height = 40
        tab_y = panel_y + 70
        
        for i, tab_name in enumerate(tabs):
            tab_x = panel_x + 20 + i * (tab_width + 10)
            
            # Tab background
            if i == self.selected_tab:
                color = (60, 60, 100)
                border_color = (150, 150, 200)
            else:
                color = (40, 40, 60)
                border_color = (80, 80, 120)
            
            pygame.draw.rect(screen, color, (tab_x, tab_y, tab_width, tab_height), border_radius=6)
            pygame.draw.rect(screen, border_color, (tab_x, tab_y, tab_width, tab_height), 2, border_radius=6)
            
            # Tab text
            tab_text = font.render(tab_name, True, (255, 255, 255))
            screen.blit(tab_text, (tab_x + tab_width//2 - tab_text.get_width()//2, 
                                  tab_y + tab_height//2 - tab_text.get_height()//2))
        
        # Content area
        content_x = panel_x + 20
        content_y = panel_y + 130
        content_width = panel_width - 40
        content_height = panel_height - 180
        
        # Get quests for current tab
        if self.selected_tab == 0:  # Active
            quests = quest_manager.get_active_quests()
            empty_message = "No active quests"
        elif self.selected_tab == 1:  # Completed
            quests = [q for q in quest_manager.all_quests.values() if q.state == QuestState.TURNED_IN]
            empty_message = "No completed quests"
        else:  # Available
            quests = quest_manager.get_available_quests(player)
            empty_message = "No available quests"
        
        if not quests:
            # Empty state
            empty_font = pygame.font.SysFont(None, 36)
            empty_text = empty_font.render(empty_message, True, (150, 150, 150))
            screen.blit(empty_text, (content_x + content_width//2 - empty_text.get_width()//2, 
                                    content_y + content_height//2))
        else:
            # Quest list on left, details on right
            list_width = 320
            detail_width = content_width - list_width - 20
            
            # Quest list
            pygame.draw.rect(screen, (40, 40, 60), (content_x, content_y, list_width, content_height), border_radius=6)
            pygame.draw.rect(screen, (80, 80, 120), (content_x, content_y, list_width, content_height), 2, border_radius=6)
            
            # Draw quests in list
            quest_height = 70
            visible_quests = content_height // quest_height
            
            for i, quest in enumerate(quests[self.scroll_offset:self.scroll_offset + visible_quests]):
                quest_y = content_y + 10 + i * quest_height
                
                # Highlight selected
                if i + self.scroll_offset == self.selected_quest_idx:
                    pygame.draw.rect(screen, (70, 70, 110), (content_x + 5, quest_y, list_width - 10, quest_height - 5), border_radius=4)
                
                # Quest type indicator
                if quest.quest_type == QuestType.MAIN:
                    type_color = (255, 200, 50)
                    type_text = "MAIN"
                else:
                    type_color = (100, 200, 255)
                    type_text = "SIDE"
                
                small_font = pygame.font.SysFont(None, 18)
                type_label = small_font.render(type_text, True, type_color)
                screen.blit(type_label, (content_x + 15, quest_y + 5))
                
                # Quest name
                name_font = pygame.font.SysFont(None, 24)
                name = name_font.render(quest.name[:30], True, (255, 255, 255))
                screen.blit(name, (content_x + 15, quest_y + 25))
                
                # Quest category
                category_text = small_font.render(quest.category.value.capitalize(), True, (180, 180, 180))
                screen.blit(category_text, (content_x + 15, quest_y + 48))
            
            # Quest details on right
            if 0 <= self.selected_quest_idx < len(quests):
                selected_quest = quests[self.selected_quest_idx]
                detail_x = content_x + list_width + 20
                
                pygame.draw.rect(screen, (40, 40, 60), (detail_x, content_y, detail_width, content_height), border_radius=6)
                pygame.draw.rect(screen, (80, 80, 120), (detail_x, content_y, detail_width, content_height), 2, border_radius=6)
                
                # Quest name
                detail_title_font = pygame.font.SysFont(None, 32)
                detail_name = detail_title_font.render(selected_quest.name, True, (255, 255, 180))
                screen.blit(detail_name, (detail_x + 15, content_y + 15))
                
                # Quest description
                desc_y = content_y + 55
                desc_font = pygame.font.SysFont(None, 20)
                
                # Word wrap description
                words = selected_quest.description.split()
                lines = []
                current_line = ""
                max_width = detail_width - 30
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if desc_font.size(test_line)[0] <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                for line in lines[:6]:  # Limit to 6 lines
                    desc_text = desc_font.render(line, True, (200, 200, 200))
                    screen.blit(desc_text, (detail_x + 15, desc_y))
                    desc_y += 22
                
                # Objectives
                obj_y = desc_y + 20
                obj_title = font.render("Objectives:", True, (255, 255, 180))
                screen.blit(obj_title, (detail_x + 15, obj_y))
                obj_y += 30
                
                for obj in selected_quest.objectives:
                    if obj.completed:
                        color = (100, 255, 100)
                        check = "✓ "
                    else:
                        color = (255, 255, 255)
                        check = "• "
                    
                    obj_text = desc_font.render(check + obj.get_progress_text(), True, color)
                    screen.blit(obj_text, (detail_x + 25, obj_y))
                    obj_y += 25
                
                # Rewards
                reward_y = content_y + content_height - 120
                reward_title = font.render("Rewards:", True, (255, 255, 180))
                screen.blit(reward_title, (detail_x + 15, reward_y))
                reward_y += 30
                
                reward_font = pygame.font.SysFont(None, 20)
                if selected_quest.rewards.get('xp', 0) > 0:
                    xp_text = reward_font.render(f"• {selected_quest.rewards['xp']} XP", True, (150, 255, 150))
                    screen.blit(xp_text, (detail_x + 25, reward_y))
                    reward_y += 22
                
                if selected_quest.rewards.get('gold', 0) > 0:
                    gold_text = reward_font.render(f"• {selected_quest.rewards['gold']} Dubloons", True, (255, 215, 0))
                    screen.blit(gold_text, (detail_x + 25, reward_y))
                    reward_y += 22
                
                # Actions
                action_y = panel_y + panel_height - 50
                action_font = pygame.font.SysFont(None, 22)
                
                if self.selected_tab == 0:  # Active quests
                    if selected_quest.state == QuestState.COMPLETED:
                        action_text = action_font.render("[ENTER] Turn in quest | [T] Toggle tracking | [ESC] Close", True, (200, 200, 200))
                    else:
                        action_text = action_font.render("[T] Toggle tracking | [ESC] Close", True, (200, 200, 200))
                elif self.selected_tab == 2:  # Available quests
                    action_text = action_font.render("[ENTER] Accept quest | [ESC] Close", True, (200, 200, 200))
                else:  # Completed quests
                    action_text = action_font.render("[ESC] Close", True, (200, 200, 200))
                
                screen.blit(action_text, (panel_x + panel_width//2 - action_text.get_width()//2, action_y))
        
        # Instructions at bottom
        instr_y = panel_y + panel_height - 50
        instr_font = pygame.font.SysFont(None, 20)
        instr_text = instr_font.render("[←→] Switch tabs | [↑↓] Select quest | [L] Close", True, (180, 180, 180))
        screen.blit(instr_text, (panel_x + 20, instr_y))
    
    def handle_input(self, event, quest_manager, player):
        """Handle keyboard input for quest log"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            # Get quests for current tab
            if self.selected_tab == 0:
                quests = quest_manager.get_active_quests()
            elif self.selected_tab == 1:
                quests = [q for q in quest_manager.all_quests.values() if q.state == QuestState.TURNED_IN]
            else:
                quests = quest_manager.get_available_quests(player)
            
            if event.key in [pygame.K_UP, pygame.K_w]:
                if quests:
                    self.selected_quest_idx = max(0, self.selected_quest_idx - 1)
                    if self.selected_quest_idx < self.scroll_offset:
                        self.scroll_offset = self.selected_quest_idx
            
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                if quests:
                    self.selected_quest_idx = min(len(quests) - 1, self.selected_quest_idx + 1)
                    visible_quests = 7  # Approximate
                    if self.selected_quest_idx >= self.scroll_offset + visible_quests:
                        self.scroll_offset = self.selected_quest_idx - visible_quests + 1
            
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                self.selected_tab = max(0, self.selected_tab - 1)
                self.selected_quest_idx = 0
                self.scroll_offset = 0
            
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.selected_tab = min(2, self.selected_tab + 1)
                self.selected_quest_idx = 0
                self.scroll_offset = 0
            
            elif event.key == pygame.K_t and self.selected_tab == 0:
                # Toggle tracking
                if quests and 0 <= self.selected_quest_idx < len(quests):
                    quest = quests[self.selected_quest_idx]
                    quest_manager.toggle_quest_tracking(quest.id)
                    return f"Quest tracking: {'ON' if quest.tracked else 'OFF'}"
            
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if quests and 0 <= self.selected_quest_idx < len(quests):
                    quest = quests[self.selected_quest_idx]
                    
                    if self.selected_tab == 0 and quest.state == QuestState.COMPLETED:
                        # Turn in quest
                        success, message = quest_manager.turn_in_quest(quest.id, player)
                        return message
                    
                    elif self.selected_tab == 2:
                        # Accept quest
                        success, message = quest_manager.accept_quest(quest.id, player)
                        if success:
                            self.selected_tab = 0  # Switch to active tab
                            self.selected_quest_idx = 0
                        return message
            
            elif event.key == pygame.K_l or event.key == pygame.K_ESCAPE:
                self.toggle()
                return "Quest log closed"
        
        return None


class QuestTrackerUI:
    """On-screen quest tracker overlay"""
    
    def __init__(self):
        self.enabled = True
        self.position = 'top-left'  # Can be 'top-left', 'top-right', 'bottom-left', 'bottom-right'
        self.max_quests_shown = 3
    
    def toggle(self):
        """Toggle tracker on/off"""
        self.enabled = not self.enabled
    
    def draw(self, screen, font, quest_manager):
        """Draw quest tracker overlay"""
        if not self.enabled:
            return
        
        tracked_quests = quest_manager.get_tracked_quests()
        if not tracked_quests:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Position
        padding = 250  # Below minimap
        
        if self.position == 'top-right':
            x = screen_width - 350
            y = padding
        elif self.position == 'bottom-right':
            x = screen_width - 350
            y = screen_height - 400
        elif self.position == 'bottom-left':
            x = 10
            y = screen_height - 400
        else:  # top-left
            x = 10
            y = padding
        
        # Background
        tracker_width = 340
        tracker_height = min(len(tracked_quests), self.max_quests_shown) * 120 + 40
        
        bg_surface = pygame.Surface((tracker_width, tracker_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (20, 20, 30, 220), (0, 0, tracker_width, tracker_height), border_radius=8)
        pygame.draw.rect(bg_surface, (100, 100, 150, 255), (0, 0, tracker_width, tracker_height), 2, border_radius=8)
        screen.blit(bg_surface, (x, y))
        
        # Title
        title_font = pygame.font.SysFont(None, 24)
        title = title_font.render("Active Quests", True, (255, 255, 180))
        screen.blit(title, (x + 10, y + 10))
        
        # Draw quests
        quest_y = y + 40
        small_font = pygame.font.SysFont(None, 18)
        
        for i, quest in enumerate(tracked_quests[:self.max_quests_shown]):
            # Quest name
            name_text = font.render(quest.name[:30], True, (255, 255, 255))
            screen.blit(name_text, (x + 10, quest_y))
            quest_y += 25
            
            # Objectives
            for obj in quest.objectives[:3]:  # Show max 3 objectives
                if obj.completed:
                    color = (100, 255, 100)
                    check = "✓"
                else:
                    color = (200, 200, 200)
                    check = "•"
                
                obj_text = small_font.render(f"{check} {obj.get_progress_text()}", True, color)
                screen.blit(obj_text, (x + 20, quest_y))
                quest_y += 20
            
            quest_y += 10  # Space between quests
        
        # Toggle hint
        hint_font = pygame.font.SysFont(None, 14)
        hint_text = hint_font.render("[Q] Toggle Tracker", True, (150, 150, 150))
        screen.blit(hint_text, (x + 10, y + tracker_height - 20))
