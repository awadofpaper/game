"""
Skills UI - Display gathering skills progress (Runescape-style)
Shows Mining, Woodcutting, Fishing, and Cooking with levels and XP bars
"""
import pygame
from skills_system import MINING_RESOURCES, WOODCUTTING_RESOURCES, FISHING_RESOURCES, COOKING_RESOURCES


class SkillsUI:
    """UI for displaying gathering skills"""
    
    def __init__(self):
        self.active = False
        self.selected_skill = 0  # 0-3 for the 4 skills
        self.skill_names = ['Mining', 'Woodcutting', 'Fishing', 'Cooking']
        self.skill_colors = {
            'Mining': (180, 180, 180),
            'Woodcutting': (139, 69, 19),
            'Fishing': (65, 105, 225),
            'Cooking': (255, 140, 0)
        }
    
    def toggle(self):
        """Toggle the skills UI"""
        self.active = not self.active
    
    def open(self):
        """Open the skills UI"""
        self.active = True
    
    def close(self):
        """Close the skills UI"""
        self.active = False
    
    def handle_input(self, event, player):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_k:
                self.close()
                return True
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_skill = (self.selected_skill - 1) % 4
                return True
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_skill = (self.selected_skill + 1) % 4
                return True
        return False
    
    def draw(self, screen, player):
        """Draw the skills UI"""
        if not self.active:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 700
        panel_height = 600
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = (screen.get_height() - panel_height) // 2
        
        # Draw panel background
        pygame.draw.rect(screen, (40, 40, 50), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (200, 200, 200), (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title
        font_large = pygame.font.SysFont(None, 48)
        font_medium = pygame.font.SysFont(None, 32)
        font_small = pygame.font.SysFont(None, 24)
        
        title_text = font_large.render("Skills", True, (255, 255, 255))
        screen.blit(title_text, (panel_x + 20, panel_y + 20))
        
        # Total level
        total_level = player.skills_manager.get_total_level()
        total_text = font_medium.render(f"Total Level: {total_level}", True, (255, 215, 0))
        screen.blit(total_text, (panel_x + panel_width - total_text.get_width() - 20, panel_y + 25))
        
        # Draw each skill
        start_y = panel_y + 100
        skill_height = 110
        
        for i, skill_name in enumerate(self.skill_names):
            skill = player.skills_manager.get_skill(skill_name)
            y_pos = start_y + i * skill_height
            
            # Highlight selected skill
            if i == self.selected_skill:
                pygame.draw.rect(screen, (60, 60, 80), (panel_x + 20, y_pos - 5, panel_width - 40, skill_height - 10))
            
            # Skill icon/color box
            color = self.skill_colors.get(skill_name, (100, 100, 100))
            pygame.draw.rect(screen, color, (panel_x + 30, y_pos, 60, 60))
            pygame.draw.rect(screen, (255, 255, 255), (panel_x + 30, y_pos, 60, 60), 2)
            
            # Skill name and level
            name_text = font_medium.render(skill_name, True, (255, 255, 255))
            screen.blit(name_text, (panel_x + 110, y_pos + 5))
            
            level_text = font_large.render(str(skill.level), True, (255, 215, 0))
            screen.blit(level_text, (panel_x + 110, y_pos + 30))
            
            # XP progress bar
            bar_x = panel_x + 250
            bar_y = y_pos + 20
            bar_width = 380
            bar_height = 30
            
            # Calculate XP progress to next level
            if skill.level >= 100:
                progress = 1.0
                xp_text = "MAX LEVEL"
            else:
                current_level_xp = skill.xp_for_level(skill.level)
                next_level_xp = skill.xp_for_level(skill.level + 1)
                progress = (skill.xp - current_level_xp) / (next_level_xp - current_level_xp)
                xp_needed = next_level_xp - skill.xp
                xp_text = f"{int(xp_needed)} XP to level {skill.level + 1}"
            
            # Draw progress bar background
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            
            # Draw progress bar fill
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
            
            # Draw progress bar border
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
            
            # XP text
            xp_label = font_small.render(xp_text, True, (255, 255, 255))
            screen.blit(xp_label, (bar_x + (bar_width - xp_label.get_width()) // 2, bar_y + 5))
        
        # Instructions
        instructions = [
            "Press ESC or K to close",
            "Use UP/DOWN to navigate"
        ]
        
        inst_y = panel_y + panel_height - 60
        for i, inst in enumerate(instructions):
            inst_text = font_small.render(inst, True, (180, 180, 180))
            screen.blit(inst_text, (panel_x + 20, inst_y + i * 25))
        
        # Resource information for selected skill
        self._draw_resource_info(screen, panel_x, panel_y, panel_width, panel_height, player, font_small)
    
    def _draw_resource_info(self, screen, panel_x, panel_y, panel_width, panel_height, player, font):
        """Draw information about resources for the selected skill"""
        skill_name = self.skill_names[self.selected_skill]
        skill = player.skills_manager.get_skill(skill_name)
        
        # Get resource list based on skill
        if skill_name == 'Mining':
            resources = MINING_RESOURCES
        elif skill_name == 'Woodcutting':
            resources = WOODCUTTING_RESOURCES
        elif skill_name == 'Fishing':
            resources = FISHING_RESOURCES
        elif skill_name == 'Cooking':
            resources = COOKING_RESOURCES
        else:
            return
        
        # Draw resource info panel on the right side
        info_x = panel_x + panel_width + 20
        info_y = panel_y
        info_width = 300
        info_height = panel_height
        
        # Only draw if it fits on screen
        if info_x + info_width > screen.get_width():
            return
        
        # Draw info background
        pygame.draw.rect(screen, (40, 40, 50), (info_x, info_y, info_width, info_height))
        pygame.draw.rect(screen, (200, 200, 200), (info_x, info_y, info_width, info_height), 2)
        
        # Title
        title = font.render(f"{skill_name} Resources", True, (255, 255, 255))
        screen.blit(title, (info_x + 10, info_y + 10))
        
        # List resources
        y_offset = 50
        for resource_name, data in resources.items():
            req_level = data['level']
            xp = data['xp']
            
            # Color code based on level requirement
            if skill.level >= req_level:
                color = (100, 255, 100)  # Green - can gather
            elif skill.level >= req_level - 5:
                color = (255, 255, 100)  # Yellow - almost there
            else:
                color = (150, 150, 150)  # Gray - too low level
            
            # Resource name and level
            resource_text = f"Lv{req_level}: {resource_name.replace('_', ' ').title()}"
            text_surface = font.render(resource_text, True, color)
            
            if info_y + y_offset + 20 < info_y + info_height - 10:
                screen.blit(text_surface, (info_x + 10, info_y + y_offset))
                
                # XP value
                xp_text = f"+{xp} XP"
                xp_surface = font.render(xp_text, True, (200, 200, 200))
                screen.blit(xp_surface, (info_x + info_width - xp_surface.get_width() - 10, info_y + y_offset))
                
                y_offset += 25


def draw_skills_hud(screen, player):
    """Draw a small HUD element showing skills overview (optional)"""
    # Could show current gathering progress, level ups, etc.
    # For now, just show if player is gathering
    if player.gathering_node:
        from gathering_nodes import NodeState
        if player.gathering_node.state == NodeState.BEING_GATHERED:
            # Show gathering progress
            progress = player.gathering_node.gather_progress
            resource_type = player.gathering_node.resource_type
            
            # Draw small progress bar at bottom of screen
            bar_width = 300
            bar_height = 30
            bar_x = (screen.get_width() - bar_width) // 2
            bar_y = screen.get_height() - 100
            
            # Background
            pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_width, bar_height))
            
            # Progress fill
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, fill_width, bar_height))
            
            # Border
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Text
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"Gathering {resource_type.replace('_', ' ').title()}... {int(progress * 100)}%", True, (255, 255, 255))
            screen.blit(text, (bar_x + (bar_width - text.get_width()) // 2, bar_y + 5))
