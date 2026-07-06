"""
Boss loot preview UI - shows potential drops before fighting boss
"""
import pygame
from typing import Dict, Optional

class BossLootPreviewUI:
    """UI for showing boss loot table before engagement"""
    
    def __init__(self):
        self.active = False
        self.boss_type = None
        self.loot_data = None
        self.width = 500
        self.height = 400
        self.padding = 20
        self.line_height = 25
        
        # Colors
        self.bg_color = (20, 20, 30, 240)
        self.border_color = (100, 100, 150)
        self.title_color = (255, 215, 0)  # Gold
        self.guaranteed_color = (255, 100, 50)  # Orange
        self.possible_color = (100, 200, 255)  # Blue
        
        # Rarity colors
        self.rarity_colors = {
            "common": (200, 200, 200),
            "uncommon": (0, 255, 0),
            "rare": (0, 100, 255),
            "epic": (150, 0, 255),
            "legendary": (255, 165, 0),
            "artifact": (255, 215, 0)
        }
    
    def show(self, boss_type: str, loot_data: Dict):
        """Show boss loot preview"""
        self.active = True
        self.boss_type = boss_type
        self.loot_data = loot_data
    
    def hide(self):
        """Hide loot preview"""
        self.active = False
        self.boss_type = None
        self.loot_data = None
    
    def draw(self, screen):
        """Draw the boss loot preview UI"""
        if not self.active or not self.loot_data:
            return
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Center the UI
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        # Create semi-transparent surface
        preview_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(preview_surface, self.bg_color, (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(preview_surface, self.border_color, (0, 0, self.width, self.height), 3, border_radius=10)
        
        # Draw title
        title_font = pygame.font.Font(None, 36)
        boss_name = self.boss_type.replace('_', ' ').title()
        title_text = title_font.render(f"{boss_name} - Loot Table", True, self.title_color)
        preview_surface.blit(title_text, (self.width // 2 - title_text.get_width() // 2, self.padding))
        
        # Draw separator
        pygame.draw.line(preview_surface, self.border_color, 
                        (self.padding, 60), 
                        (self.width - self.padding, 60), 2)
        
        y_offset = 80
        
        # Draw guaranteed drop
        if self.loot_data.get("guaranteed"):
            guaranteed = self.loot_data["guaranteed"]
            
            # Section header
            header_font = pygame.font.Font(None, 28)
            header_text = header_font.render("⭐ GUARANTEED DROP", True, self.guaranteed_color)
            preview_surface.blit(header_text, (self.padding, y_offset))
            y_offset += 35
            
            # Item name with rarity color
            item_font = pygame.font.Font(None, 24)
            rarity_color = self.rarity_colors.get(guaranteed["rarity"], (255, 255, 255))
            item_name_text = item_font.render(f"• {guaranteed['name']}", True, rarity_color)
            preview_surface.blit(item_name_text, (self.padding + 10, y_offset))
            y_offset += self.line_height
            
            # Description
            desc_font = pygame.font.Font(None, 18)
            desc_text = desc_font.render(guaranteed["description"], True, (200, 200, 200))
            preview_surface.blit(desc_text, (self.padding + 20, y_offset))
            y_offset += self.line_height
            
            # Stats
            if guaranteed.get("stats"):
                stats_text = ", ".join([f"{stat}: +{value}" for stat, value in guaranteed["stats"].items()])
                stats_surface = desc_font.render(stats_text, True, (150, 255, 150))
                preview_surface.blit(stats_surface, (self.padding + 20, y_offset))
                y_offset += self.line_height
            
            # Special ability
            if guaranteed.get("special_ability"):
                ability_font = pygame.font.Font(None, 18)
                ability_text = ability_font.render(f"Special: {guaranteed['special_ability'].replace('_', ' ').title()}", 
                                                  True, (255, 215, 100))
                preview_surface.blit(ability_text, (self.padding + 20, y_offset))
                y_offset += self.line_height
            
            y_offset += 15
        
        # Draw possible drops
        if self.loot_data.get("possible"):
            # Section header
            header_font = pygame.font.Font(None, 28)
            header_text = header_font.render("🎲 POSSIBLE DROPS", True, self.possible_color)
            preview_surface.blit(header_text, (self.padding, y_offset))
            y_offset += 35
            
            # List possible items
            item_font = pygame.font.Font(None, 20)
            for drop in self.loot_data["possible"]:
                rarity_color = self.rarity_colors.get(drop["rarity"], (255, 255, 255))
                chance_percent = int(drop["chance"] * 100)
                
                # Item name with chance
                item_text = f"• {drop['item'].replace('_', ' ').title()} ({chance_percent}% chance)"
                item_surface = item_font.render(item_text, True, rarity_color)
                preview_surface.blit(item_surface, (self.padding + 10, y_offset))
                y_offset += self.line_height - 3
        
        # Draw "Press any key to continue" at bottom
        footer_font = pygame.font.Font(None, 22)
        footer_text = footer_font.render("Press any key to continue...", True, (150, 150, 150))
        preview_surface.blit(footer_text, 
                           (self.width // 2 - footer_text.get_width() // 2, 
                            self.height - self.padding - 10))
        
        # Blit to screen
        screen.blit(preview_surface, (x, y))


class SetBonusDisplayUI:
    """UI for displaying active set bonuses"""
    
    def __init__(self):
        self.width = 300
        self.height = 200
        self.padding = 15
        self.line_height = 22
        
        # Colors
        self.bg_color = (20, 30, 40, 220)
        self.border_color = (50, 255, 150)
        self.title_color = (50, 255, 150)
        self.bonus_color = (150, 255, 150)
    
    def draw(self, screen, active_bonuses: Dict, position="top-right"):
        """Draw active set bonuses"""
        if not active_bonuses:
            return
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate dynamic height based on content
        content_lines = 2  # Title + separator
        for set_id, bonus_data in active_bonuses.items():
            content_lines += 3  # Set name, pieces count, bonuses
            if "special_ability" in bonus_data["bonuses"]:
                content_lines += 1
        
        dynamic_height = min(self.height, content_lines * self.line_height + self.padding * 2)
        
        # Position
        if position == "top-right":
            x = screen_width - self.width - 10
            y = 10
        elif position == "top-left":
            x = 10
            y = 10
        else:
            x = 10
            y = screen_height - dynamic_height - 10
        
        # Create surface
        set_surface = pygame.Surface((self.width, dynamic_height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(set_surface, self.bg_color, (0, 0, self.width, dynamic_height), border_radius=8)
        pygame.draw.rect(set_surface, self.border_color, (0, 0, self.width, dynamic_height), 2, border_radius=8)
        
        # Title
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render("⚡ Active Set Bonuses", True, self.title_color)
        set_surface.blit(title_text, (self.padding, self.padding))
        
        # Separator
        pygame.draw.line(set_surface, self.border_color, 
                        (self.padding, 40), 
                        (self.width - self.padding, 40), 1)
        
        y_offset = 50
        
        # Draw each active set bonus
        name_font = pygame.font.Font(None, 20)
        bonus_font = pygame.font.Font(None, 18)
        
        for set_id, bonus_data in active_bonuses.items():
            # Set name
            set_name_text = name_font.render(f"• {bonus_data['name']}", True, (255, 215, 0))
            set_surface.blit(set_name_text, (self.padding, y_offset))
            y_offset += self.line_height
            
            # Pieces count
            pieces_text = bonus_font.render(f"  ({bonus_data['pieces']} pieces - Tier {bonus_data['tier']})", 
                                           True, (200, 200, 200))
            set_surface.blit(pieces_text, (self.padding + 5, y_offset))
            y_offset += self.line_height - 3
            
            # Bonuses
            bonuses = bonus_data["bonuses"]
            if "description" in bonuses:
                desc_text = bonus_font.render(f"  {bonuses['description']}", True, self.bonus_color)
                set_surface.blit(desc_text, (self.padding + 5, y_offset))
                y_offset += self.line_height - 3
            
            y_offset += 5  # Extra spacing between sets
        
        # Blit to screen
        screen.blit(set_surface, (x, y))


# Global instances
boss_loot_preview_ui = BossLootPreviewUI()
set_bonus_display_ui = SetBonusDisplayUI()


def get_boss_loot_preview_ui() -> BossLootPreviewUI:
    """Get the global boss loot preview UI instance"""
    return boss_loot_preview_ui


def get_set_bonus_display_ui() -> SetBonusDisplayUI:
    """Get the global set bonus display UI instance"""
    return set_bonus_display_ui
