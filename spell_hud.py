"""
Spell HUD System
Visual interface for spell casting with cooldowns, mana costs, and quick selection
"""

import pygame
import time
from spells import SPELLS

class SpellHUD:
    """
    HUD overlay showing current spells, mana, cooldowns, and casting indicators
    Displays in bottom-right corner above hotbar
    """
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # UI positioning (bottom-right, above hotbar)
        self.panel_width = 280
        self.panel_height = 140
        self.panel_x = screen_width - self.panel_width - 15
        self.panel_y = screen_height - 200  # Above hotbar
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 22, bold=True)
        self.spell_font = pygame.font.SysFont(None, 20)
        self.small_font = pygame.font.SysFont(None, 16)
        
        # Colors
        self.bg_color = (20, 20, 35, 200)  # Dark blue, semi-transparent
        self.border_color = (80, 120, 200)
        self.primary_color = (255, 200, 50)  # Gold for primary spell
        self.secondary_color = (100, 200, 255)  # Light blue for secondary
        self.cooldown_color = (200, 50, 50)
        self.ready_color = (50, 255, 100)
        self.mana_color = (100, 150, 255)
        self.low_mana_color = (200, 50, 50)
        
        # Animation states
        self.last_cast_time = 0
        self.cast_flash_duration = 0.3  # seconds
        self.casting_spell = None
        
        # Spell cooldown tracking (shared with advanced_spells)
        self.cooldowns = {}  # spell_id -> end_time
        
        # Visibility toggle (can be hidden with hotkey)
        self.visible = True
    
    def update_cooldown(self, spell_id, cooldown_time):
        """Update cooldown for a spell after casting"""
        self.cooldowns[spell_id] = time.time() + cooldown_time
        self.casting_spell = spell_id
        self.last_cast_time = time.time()
    
    def get_cooldown_remaining(self, spell_id):
        """Get remaining cooldown time for a spell"""
        if spell_id not in self.cooldowns:
            return 0.0
        remaining = self.cooldowns[spell_id] - time.time()
        return max(0.0, remaining)
    
    def is_spell_ready(self, spell_id):
        """Check if spell is off cooldown"""
        return self.get_cooldown_remaining(spell_id) <= 0
    
    def toggle_visibility(self):
        """Toggle HUD visibility"""
        self.visible = not self.visible
    
    def draw(self, screen, player):
        """Draw the spell HUD"""
        if not self.visible:
            return
        
        # Create semi-transparent background
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.bg_color, (0, 0, self.panel_width, self.panel_height), border_radius=8)
        pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.panel_width, self.panel_height), 2, border_radius=8)
        
        # Title
        title = self.title_font.render("⚡ Spells", True, (255, 255, 255))
        panel_surface.blit(title, (10, 8))
        
        # Mana bar
        mana_ratio = player.mana / player.max_mana if player.max_mana > 0 else 0
        mana_bar_width = self.panel_width - 80
        mana_bar_height = 16
        mana_bar_x = 60
        mana_bar_y = 10
        
        # Mana bar background
        pygame.draw.rect(panel_surface, (30, 30, 50), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), border_radius=3)
        
        # Mana bar fill
        mana_color = self.mana_color if mana_ratio > 0.3 else self.low_mana_color
        mana_fill_width = int(mana_bar_width * mana_ratio)
        if mana_fill_width > 0:
            pygame.draw.rect(panel_surface, mana_color, (mana_bar_x, mana_bar_y, mana_fill_width, mana_bar_height), border_radius=3)
        
        # Mana text
        mana_text = self.small_font.render(f"{int(player.mana)}/{int(player.max_mana)}", True, (255, 255, 255))
        panel_surface.blit(mana_text, (mana_bar_x + mana_bar_width // 2 - mana_text.get_width() // 2, mana_bar_y + 2))
        
        # Primary spell (Q key or hotbar slot)
        y_offset = 40
        self._draw_spell_slot(panel_surface, player.selected_spell, "Primary (Q)", self.primary_color, 10, y_offset, player)
        
        # Secondary spell (E key)
        y_offset = 88
        self._draw_spell_slot(panel_surface, player.secondary_spell, "Secondary (E)", self.secondary_color, 10, y_offset, player)
        
        # Cast flash effect
        if self.casting_spell and time.time() - self.last_cast_time < self.cast_flash_duration:
            flash_alpha = int(255 * (1.0 - (time.time() - self.last_cast_time) / self.cast_flash_duration))
            flash_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
            pygame.draw.rect(flash_surface, (255, 255, 255, flash_alpha), (0, 0, self.panel_width, self.panel_height), 3, border_radius=8)
            panel_surface.blit(flash_surface, (0, 0))
        
        # Blit to screen
        screen.blit(panel_surface, (self.panel_x, self.panel_y))
    
    def _draw_spell_slot(self, surface, spell_id, label, color, x, y, player):
        """Draw a single spell slot with icon, name, cooldown, and cost"""
        if not spell_id:
            # Empty slot
            empty_text = self.spell_font.render(f"{label}: None", True, (120, 120, 120))
            surface.blit(empty_text, (x, y))
            hint_text = self.small_font.render("Press 'B' to select", True, (100, 100, 100))
            surface.blit(hint_text, (x, y + 20))
            return
        
        # Get spell data
        spell = SPELLS.get(spell_id)
        if not spell:
            return
        
        # Spell name with key binding
        name_text = self.spell_font.render(f"{label}:", True, color)
        surface.blit(name_text, (x, y))
        
        spell_name = self.spell_font.render(spell["name"], True, (255, 255, 255))
        surface.blit(spell_name, (x + 90, y))
        
        # Cooldown indicator
        cooldown_remaining = self.get_cooldown_remaining(spell_id)
        is_ready = cooldown_remaining <= 0
        
        # Mana cost
        mana_cost = spell.get("mana_cost", 0)
        has_mana = player.mana >= mana_cost
        
        # Status indicator (ready/cooldown/no mana)
        status_y = y + 22
        if not is_ready:
            # Show cooldown
            cooldown_text = self.small_font.render(f"⏱ {cooldown_remaining:.1f}s", True, self.cooldown_color)
            surface.blit(cooldown_text, (x, status_y))
        elif not has_mana:
            # Not enough mana
            mana_text = self.small_font.render(f"✗ Need {mana_cost} mana", True, self.low_mana_color)
            surface.blit(mana_text, (x, status_y))
        else:
            # Ready to cast
            ready_text = self.small_font.render("✓ Ready", True, self.ready_color)
            surface.blit(ready_text, (x, status_y))
            
            # Show mana cost
            cost_text = self.small_font.render(f"({mana_cost} mana)", True, self.mana_color)
            surface.blit(cost_text, (x + 60, status_y))
        
        # Draw cooldown progress bar
        if not is_ready:
            bar_width = 120
            bar_height = 3
            bar_x = x + 110
            bar_y = status_y + 2
            
            spell_cooldown = spell.get("cooldown", 1.0)
            progress = 1.0 - (cooldown_remaining / spell_cooldown)
            
            # Background
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Progress
            pygame.draw.rect(surface, self.ready_color, (bar_x, bar_y, int(bar_width * progress), bar_height))
    
    def draw_cast_indicator(self, screen, target_x, target_y, spell_id, player_x, player_y):
        """Draw targeting line and indicator when aiming a spell"""
        if not spell_id or not self.visible:
            return
        
        spell = SPELLS.get(spell_id)
        if not spell:
            return
        
        # Draw line from player to target
        pygame.draw.line(screen, (255, 255, 100, 100), (player_x, player_y), (target_x, target_y), 2)
        
        # Draw target indicator
        spell_range = spell.get("range", 300)
        indicator_color = (255, 255, 100) if self.is_spell_ready(spell_id) else (200, 50, 50)
        
        # Circle at target
        pygame.draw.circle(screen, indicator_color, (int(target_x), int(target_y)), 15, 2)
        
        # Show spell name at cursor
        spell_name = self.spell_font.render(spell["name"], True, indicator_color)
        screen.blit(spell_name, (target_x + 20, target_y - 10))
        
        # Show range indicator if targeting too far
        distance = ((target_x - player_x) ** 2 + (target_y - player_y) ** 2) ** 0.5
        if distance > spell_range:
            warning = self.small_font.render("OUT OF RANGE", True, (255, 50, 50))
            screen.blit(warning, (target_x - warning.get_width() // 2, target_y + 20))
