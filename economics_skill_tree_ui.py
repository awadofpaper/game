"""
Economics Skill Tree UI - Visual interface for economics skills
"""

import pygame
from typing import Optional
from economics_skill_tree import EconomicsSkillTree, EconomicsSkill


class EconomicsSkillTreeUI:
    """UI for viewing and upgrading economics skills"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        
        # State
        self.selected_skill = None
        self.scroll_offset = 0
        
        # UI dimensions
        self.width = 1000
        self.height = 650
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.header_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # Colors
        self.bg_color = (40, 40, 50)
        self.panel_color = (50, 50, 60)
        self.selected_color = (70, 130, 180)
        self.text_color = (255, 255, 255)
        self.dim_text_color = (180, 180, 180)
        self.unlocked_color = (100, 220, 100)
        self.locked_color = (150, 50, 50)
        self.gold_color = (255, 215, 0)
        
        # References (set externally)
        self.skill_tree = None
        self.player = None
    
    def open(self):
        """Open the skill tree UI"""
        self.active = True
        self.scroll_offset = 0
    
    def close(self):
        """Close the skill tree UI"""
        self.active = False
    
    def toggle(self):
        """Toggle the UI"""
        if self.active:
            self.close()
        else:
            self.open()
    
    def handle_input(self, event) -> bool:
        """Handle input events. Returns True if consumed."""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_e:
                self.close()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 40)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_offset += 40
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_skill:
                    self._try_upgrade_selected()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check skill boxes
            tiers = self.skill_tree.get_all_skills_by_tier() if self.skill_tree else {}
            
            y_offset = self.y + 120 - self.scroll_offset
            for tier_name, skills in tiers.items():
                y_offset += 40  # Tier header
                
                for skill in skills:
                    skill_rect = pygame.Rect(self.x + 30, y_offset, self.width - 60, 80)
                    
                    if skill_rect.collidepoint(mouse_pos):
                        self.selected_skill = skill.skill_id
                        return True
                    
                    # Check upgrade button
                    if self.selected_skill == skill.skill_id:
                        button_rect = pygame.Rect(self.x + self.width - 150, y_offset + 45, 120, 30)
                        if button_rect.collidepoint(mouse_pos):
                            self._try_upgrade_selected()
                            return True
                    
                    y_offset += 90
        
        return False
    
    def _try_upgrade_selected(self):
        """Attempt to upgrade selected skill"""
        if not self.selected_skill or not self.skill_tree or not self.player:
            return
        
        success, message = self.skill_tree.upgrade_skill(self.player, self.selected_skill)
        
        # Show message (would integrate with game's message system)
        print(f"[ECONOMICS SKILL] {message}")
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font = None):
        """Draw the skill tree UI"""
        if not self.active or not self.skill_tree:
            return
        
        # Background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, panel_rect)
        pygame.draw.rect(screen, self.text_color, panel_rect, 2)
        
        # Title
        title = self.title_font.render("💰 ECONOMICS SKILL TREE", True, self.gold_color)
        title_x = self.x + (self.width - title.get_width()) // 2
        screen.blit(title, (title_x, self.y + 15))
        
        # Player gold
        gold_text = f"Dubloons: {self.player.dubloons:.0f}db" if self.player else "Dubloons: 0db"
        gold_surf = self.text_font.render(gold_text, True, self.gold_color)
        screen.blit(gold_surf, (self.x + 20, self.y + 60))
        
        # Active bonuses summary
        if self.player and hasattr(self.player, 'economics_skills'):
            summary = self.skill_tree.get_skill_summary(self.player)
            
            bonuses = []
            if summary['transaction_fee_reduction'] > 0:
                bonuses.append(f"Fee Reduction: -{summary['transaction_fee_reduction']*100:.0f}%")
            if summary['buying_bonus'] > 0:
                bonuses.append(f"Buy Bonus: -{summary['buying_bonus']*100:.0f}%")
            if summary['selling_bonus'] > 0:
                bonuses.append(f"Sell Bonus: +{summary['selling_bonus']*100:.0f}%")
            
            if bonuses:
                bonus_text = " | ".join(bonuses)
                bonus_surf = self.small_font.render(bonus_text, True, self.unlocked_color)
                screen.blit(bonus_surf, (self.x + 20, self.y + 85))
        
        # Scrollable content area
        content_rect = pygame.Rect(self.x + 20, self.y + 120, self.width - 40, 470)
        screen.set_clip(content_rect)
        
        # Draw skills by tier
        tiers = self.skill_tree.get_all_skills_by_tier()
        y_offset = content_rect.y - self.scroll_offset
        
        for tier_name, skills in tiers.items():
            # Tier header
            tier_header = self.header_font.render(tier_name, True, self.text_color)
            screen.blit(tier_header, (content_rect.x, y_offset))
            y_offset += 40
            
            # Skills in tier
            for skill in skills:
                self._draw_skill_box(screen, skill, content_rect.x, y_offset, content_rect.width)
                y_offset += 90
            
            y_offset += 10  # Spacing between tiers
        
        screen.set_clip(None)
        
        # Controls
        controls = "↑↓: Scroll | Click: Select | SPACE/ENTER: Upgrade | E/ESC: Close"
        controls_surf = self.small_font.render(controls, True, self.dim_text_color)
        controls_x = self.x + (self.width - controls_surf.get_width()) // 2
        screen.blit(controls_surf, (self.x + 20, self.y + 610))
    
    def _draw_skill_box(self, screen: pygame.Surface, skill: EconomicsSkill, 
                        x: int, y: int, width: int):
        """Draw a single skill box"""
        if not self.player:
            return
        
        # Update skill level from player
        if hasattr(self.player, 'economics_skills'):
            skill.current_level = self.player.economics_skills.get(skill.skill_id, 0)
        
        # Skill box
        skill_rect = pygame.Rect(x, y, width, 80)
        is_selected = self.selected_skill == skill.skill_id
        
        # Background color
        if skill.current_level > 0:
            bg_color = (60, 80, 60) if is_selected else (50, 70, 50)
        else:
            bg_color = self.selected_color if is_selected else self.panel_color
        
        pygame.draw.rect(screen, bg_color, skill_rect)
        
        # Border color based on state
        if skill.current_level >= skill.max_level:
            border_color = self.unlocked_color  # Maxed
        elif skill.current_level > 0:
            border_color = (150, 200, 150)  # Partially unlocked
        else:
            border_color = self.dim_text_color  # Locked
        
        pygame.draw.rect(screen, border_color, skill_rect, 2)
        
        # Skill name and level
        name_text = f"{skill.name} [{skill.current_level}/{skill.max_level}]"
        name_surf = self.text_font.render(name_text, True, self.text_color)
        screen.blit(name_surf, (x + 10, y + 5))
        
        # Description (word wrapped)
        desc_lines = skill.description.split('\n')
        desc_y = y + 28
        for line in desc_lines[:2]:  # Max 2 lines
            desc_surf = self.small_font.render(line, True, self.dim_text_color)
            screen.blit(desc_surf, (x + 10, desc_y))
            desc_y += 18
        
        # Prerequisites check
        if skill.prerequisites and skill.current_level == 0:
            prereq_text = "Requires: " + ", ".join(skill.prerequisites)
            prereq_surf = self.small_font.render(prereq_text, True, self.locked_color)
            screen.blit(prereq_surf, (x + 10, y + 63))
        
        # Upgrade button (if can upgrade)
        can_upgrade, message = skill.can_upgrade(
            self.player.economics_skills if hasattr(self.player, 'economics_skills') else {},
            self.player.level
        )
        
        if can_upgrade:
            cost = skill.get_upgrade_cost()
            button_rect = pygame.Rect(x + width - 140, y + 45, 120, 30)
            
            # Button color
            if self.player.dubloons >= cost:
                button_color = (80, 150, 80)
            else:
                button_color = (120, 60, 60)
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, self.text_color, button_rect, 2)
            
            button_text = f"Upgrade: {cost}g"
            button_surf = self.small_font.render(button_text, True, self.text_color)
            button_x = button_rect.x + (button_rect.width - button_surf.get_width()) // 2
            button_y = button_rect.y + (button_rect.height - button_surf.get_height()) // 2
            screen.blit(button_surf, (button_x, button_y))
        elif skill.current_level >= skill.max_level:
            # Maxed indicator
            maxed_surf = self.text_font.render("★ MAXED ★", True, self.gold_color)
            screen.blit(maxed_surf, (x + width - 140, y + 50))
        else:
            # Show why can't upgrade
            reason_surf = self.small_font.render(message, True, self.locked_color)
            screen.blit(reason_surf, (x + width - 240, y + 53))
