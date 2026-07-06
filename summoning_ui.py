"""
UI for summoning and necromancy system
Displays active summons, their stats, and provides control options
"""
import pygame
from typing import List


class SummonInfoUI:
    """UI panel showing active summons"""
    
    def __init__(self):
        self.visible = True
        self.position = "top-right"
        self.panel_width = 250
        self.compact_mode = False
        
    def draw(self, screen, summons: List, font):
        """Draw summon info panel"""
        if not self.visible or not summons:
            return
        
        # Panel dimensions
        margin = 20
        entry_height = 60 if not self.compact_mode else 40
        panel_height = min(400, len(summons) * entry_height + 60)
        
        # Position
        if self.position == "top-right":
            panel_x = screen.get_width() - self.panel_width - margin
            panel_y = margin + 140  # Below dungeon info
        else:
            panel_x = margin
            panel_y = margin
        
        # Draw semi-transparent background
        surface = pygame.Surface((self.panel_width, panel_height))
        surface.set_alpha(200)
        surface.fill((30, 20, 40))
        screen.blit(surface, (panel_x, panel_y))
        
        # Border
        pygame.draw.rect(screen, (150, 100, 255), (panel_x, panel_y, self.panel_width, panel_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 28)
        title_text = title_font.render(f"👻 Summons ({len(summons)}/5)", True, (200, 150, 255))
        screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # Draw each summon
        y_offset = panel_y + 45
        
        for i, summon in enumerate(summons[:5]):  # Max 5 displayed
            # Summon name
            summon_name = summon.summon_type.value.replace('_', ' ').title()
            if summon.from_corpse:
                summon_name = f"💀 {summon_name}"
            
            name_text = font.render(summon_name, True, (255, 255, 255))
            screen.blit(name_text, (panel_x + 10, y_offset))
            
            # Health bar
            bar_width = self.panel_width - 20
            bar_height = 8
            bar_x = panel_x + 10
            bar_y = y_offset + 20
            
            # Background
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            # Health
            health_percent = summon.health / summon.max_health
            health_width = int(bar_width * health_percent)
            
            if health_percent > 0.6:
                health_color = (0, 255, 0)
            elif health_percent > 0.3:
                health_color = (255, 200, 0)
            else:
                health_color = (255, 100, 100)
            
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
            
            # Health text
            health_label = font.render(f"{int(summon.health)}/{summon.max_health}", True, (200, 200, 200))
            screen.blit(health_label, (bar_x + 5, bar_y - 1))
            
            if not self.compact_mode:
                # Lifetime bar
                if summon.duration > 0:
                    lifetime_bar_y = y_offset + 32
                    lifetime_percent = 1.0 - (summon.lifetime / summon.duration)
                    lifetime_width = int(bar_width * lifetime_percent)
                    
                    # Background
                    pygame.draw.rect(screen, (40, 40, 40), (bar_x, lifetime_bar_y, bar_width, 6))
                    # Lifetime
                    pygame.draw.rect(screen, (100, 150, 255), (bar_x, lifetime_bar_y, lifetime_width, 6))
                    
                    # Time remaining text
                    time_remaining = int(summon.duration - summon.lifetime)
                    time_label = pygame.font.Font(None, 16).render(f"{time_remaining}s", True, (150, 150, 150))
                    screen.blit(time_label, (bar_x + bar_width - 25, lifetime_bar_y - 2))
                
                # Damage stat
                dmg_text = pygame.font.Font(None, 18).render(f"⚔️ {summon.damage}", True, (255, 150, 150))
                screen.blit(dmg_text, (panel_x + 10, y_offset + 42))
                
                # State indicator
                state_colors = {
                    "following": (100, 200, 100),
                    "attacking": (255, 100, 100),
                    "defending": (100, 150, 255)
                }
                state_text = summon.state.value.title()
                state_color = state_colors.get(summon.state.value, (200, 200, 200))
                state_label = pygame.font.Font(None, 16).render(state_text, True, state_color)
                screen.blit(state_label, (panel_x + 90, y_offset + 44))
            
            y_offset += entry_height
        
        # Instructions at bottom
        if len(summons) > 0:
            inst_font = pygame.font.Font(None, 16)
            instructions = "Press K to dismiss oldest"
            inst_text = inst_font.render(instructions, True, (150, 150, 150))
            screen.blit(inst_text, (panel_x + 10, panel_y + panel_height - 25))
    
    def toggle_compact(self):
        """Toggle compact display mode"""
        self.compact_mode = not self.compact_mode


class NecromancyIndicatorUI:
    """Shows nearby corpses available for raising"""
    
    def __init__(self):
        self.visible = True
        self.corpse_indicators = []
        
    def update(self, corpses: List, camera_x: float, camera_y: float, screen_width: int, screen_height: int):
        """Update corpse indicators"""
        self.corpse_indicators.clear()
        
        for corpse in corpses:
            screen_x = corpse['x'] - camera_x
            screen_y = corpse['y'] - camera_y
            
            # Only show if on screen
            if 0 <= screen_x <= screen_width and 0 <= screen_y <= screen_height:
                self.corpse_indicators.append({
                    'x': screen_x,
                    'y': screen_y,
                    'type': corpse.get('type', 'unknown')
                })
    
    def draw(self, screen):
        """Draw corpse indicators"""
        if not self.visible:
            return
        
        for indicator in self.corpse_indicators:
            x = int(indicator['x'])
            y = int(indicator['y'])
            
            # Draw skull indicator
            pygame.draw.circle(screen, (200, 200, 200), (x, y), 12, 2)
            
            # Skull shape
            pygame.draw.circle(screen, (180, 180, 180), (x, y - 2), 8)
            pygame.draw.circle(screen, (0, 0, 0), (x - 3, y - 4), 2)
            pygame.draw.circle(screen, (0, 0, 0), (x + 3, y - 4), 2)
            
            # Pulsing effect
            pulse = abs((pygame.time.get_ticks() // 100) % 20 - 10)
            pygame.draw.circle(screen, (150, 50, 255, 100), (x, y), 12 + pulse, 1)


class SummonCastEffectUI:
    """Visual effect when casting summon spells"""
    
    def __init__(self):
        self.active_effects = []
    
    def add_effect(self, x: float, y: float, summon_type: str):
        """Add a summoning circle effect"""
        self.active_effects.append({
            'x': x,
            'y': y,
            'type': summon_type,
            'timer': 1.0,
            'radius': 20
        })
    
    def update(self, dt: float):
        """Update effects"""
        for effect in self.active_effects:
            effect['timer'] -= dt
            effect['radius'] += 30 * dt
        
        # Remove expired effects
        self.active_effects = [e for e in self.active_effects if e['timer'] > 0]
    
    def draw(self, screen, camera_x: float, camera_y: float):
        """Draw summoning effects"""
        for effect in self.active_effects:
            screen_x = int(effect['x'] - camera_x)
            screen_y = int(effect['y'] - camera_y)
            
            # Determine color based on summon type
            if 'fire' in effect['type']:
                color = (255, 100, 0)
            elif 'ice' in effect['type']:
                color = (100, 150, 255)
            elif 'lightning' in effect['type']:
                color = (255, 255, 100)
            elif effect['type'] == 'buff':
                color = (255, 200, 0)  # Gold for buff
            elif any(word in effect['type'] for word in ['skeleton', 'zombie', 'ghost']):
                color = (150, 50, 255)
            else:
                color = (200, 100, 255)
            
            # Draw expanding circle
            alpha = int(255 * effect['timer'])
            radius = int(effect['radius'])
            
            # Create surface for alpha blending
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*color, alpha), (radius, radius), radius, 3)
            
            # Draw pentagram/circle
            if effect['timer'] > 0.5:
                # Draw mystical symbols
                for i in range(5):
                    angle = (i * 72 - 90) * 3.14159 / 180
                    x1 = radius + int(radius * 0.8 * math.cos(angle))
                    y1 = radius + int(radius * 0.8 * math.sin(angle))
                    angle2 = ((i + 2) * 72 - 90) * 3.14159 / 180
                    x2 = radius + int(radius * 0.8 * math.cos(angle2))
                    y2 = radius + int(radius * 0.8 * math.sin(angle2))
                    pygame.draw.line(surface, (*color, alpha // 2), (x1, y1), (x2, y2), 2)
            
            screen.blit(surface, (screen_x - radius, screen_y - radius))


import math


# Global instances
summon_info_ui = SummonInfoUI()
necromancy_indicator_ui = NecromancyIndicatorUI()
summon_cast_effect_ui = SummonCastEffectUI()


def get_summon_info_ui():
    return summon_info_ui


def get_necromancy_indicator_ui():
    return necromancy_indicator_ui


def get_summon_cast_effect_ui():
    return summon_cast_effect_ui
