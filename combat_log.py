"""
Combat log system for displaying recent combat actions
"""
import pygame
import time
from collections import deque

class CombatLog:
    """Scrollable combat log showing recent actions"""
    def __init__(self, max_entries=10, position="bottom-right"):
        """
        Create combat log
        
        Args:
            max_entries: Maximum number of log entries to keep
            position: Screen position ("bottom-right", "bottom-left", "top-right", "top-left")
        """
        self.entries = deque(maxlen=max_entries)
        self.max_entries = max_entries
        self.position = position
        
        # Visual settings
        self.width = 400
        self.height = 250
        self.padding = 10
        self.line_height = 22
        self.bg_color = (20, 20, 30, 200)  # Semi-transparent dark
        self.border_color = (100, 100, 120)
        self.scroll_offset = 0
        
        # Auto-hide settings
        self.last_entry_time = 0
        self.fade_delay = 5.0  # Start fading after 5 seconds
        self.fade_duration = 2.0  # Fade over 2 seconds
        
        # Enabled state
        self.enabled = True
    
    def add_entry(self, text, color=(255, 255, 255)):
        """Add a new entry to the log"""
        if not self.enabled:
            return
        
        entry = {
            'text': text,
            'color': color,
            'time': time.time()
        }
        self.entries.append(entry)
        self.last_entry_time = time.time()
        self.scroll_offset = 0  # Reset scroll when new entry added
    
    def add_damage(self, attacker, target, damage, is_crit=False, weapon_type=None, damage_type=None):
        """Add damage entry with enhanced details"""
        weapon_icon = ""
        if weapon_type:
            weapon_icons = {
                "sword": "⚔", "axe": "🪓", "dagger": "🗡",
                "hammer": "🔨", "spear": "🗡", "bow": "🏹",
                "staff": "🪄", "magic": "✨"
            }
            weapon_icon = weapon_icons.get(weapon_type, "⚔") + " "
        
        damage_suffix = ""
        if damage_type:
            type_colors = {
                "fire": (255, 100, 50),
                "ice": (100, 200, 255),
                "poison": (100, 200, 50),
                "lightning": (255, 255, 100)
            }
            if damage_type in type_colors:
                damage_suffix = f" ({damage_type})"
        
        if is_crit:
            text = f"{weapon_icon}{attacker} CRIT {target} for {int(damage)} damage!{damage_suffix}"
            color = (255, 100, 100)
        else:
            text = f"{weapon_icon}{attacker} hit {target} for {int(damage)} damage{damage_suffix}"
            color = (255, 180, 180)
        self.add_entry(text, color)
    
    def add_dodge(self, attacker, target):
        """Add dodge entry"""
        text = f"⚡ {target} DODGED {attacker}'s attack!"
        color = (100, 200, 255)
        self.add_entry(text, color)
    
    def add_kill(self, attacker, target, xp):
        """Add kill entry"""
        text = f"{attacker} defeated {target}! (+{int(xp)} XP)"
        color = (255, 215, 0)  # Gold
        self.add_entry(text, color)
    
    def add_heal(self, target, amount):
        """Add heal entry"""
        text = f"{target} healed for {int(amount)} HP"
        color = (100, 255, 100)
        self.add_entry(text, color)
    
    def add_miss(self, attacker, target):
        """Add miss entry"""
        text = f"{attacker} missed {target}"
        color = (150, 150, 150)
        self.add_entry(text, color)
    
    def add_block(self, target):
        """Add block entry"""
        text = f"{target} blocked the attack!"
        color = (100, 149, 237)
        self.add_entry(text, color)
    
    def add_event(self, text, color=(200, 200, 255)):
        """Add general combat event"""
        self.add_entry(text, color)
    
    def get_alpha(self):
        """Calculate current alpha based on fade timer"""
        time_since_entry = time.time() - self.last_entry_time
        
        if time_since_entry < self.fade_delay:
            return 255  # Fully visible
        elif time_since_entry < self.fade_delay + self.fade_duration:
            # Fade out
            fade_progress = (time_since_entry - self.fade_delay) / self.fade_duration
            return int(255 * (1 - fade_progress))
        else:
            return 0  # Invisible
    
    def scroll_up(self):
        """Scroll log up (show older entries)"""
        if self.scroll_offset < len(self.entries) - (self.height // self.line_height):
            self.scroll_offset += 1
    
    def scroll_down(self):
        """Scroll log down (show newer entries)"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
    
    def draw(self, screen, font=None):
        """Draw the combat log"""
        if not self.enabled or not self.entries:
            return
        
        # Get alpha for fade effect
        alpha = self.get_alpha()
        if alpha == 0:
            return
        
        # Calculate position based on setting
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        if self.position == "bottom-right":
            x = screen_width - self.width - 10
            y = screen_height - self.height - 10
        elif self.position == "bottom-left":
            x = 10
            y = screen_height - self.height - 10
        elif self.position == "top-right":
            x = screen_width - self.width - 10
            y = 10
        else:  # top-left
            x = 10
            y = 10
        
        # Create semi-transparent surface for the log
        log_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background
        bg_color_alpha = (*self.bg_color[:3], int(self.bg_color[3] * alpha / 255))
        pygame.draw.rect(log_surface, bg_color_alpha, (0, 0, self.width, self.height))
        pygame.draw.rect(log_surface, self.border_color, (0, 0, self.width, self.height), 2)
        
        # Draw title
        if font is None:
            try:
                font = pygame.font.Font(None, 20)
            except (pygame.error, OSError, FileNotFoundError):
                font = pygame.font.SysFont('arial', 20)
        
        title_font = pygame.font.Font(None, 22) if font else None
        title_text = title_font.render("Combat Log", True, (200, 200, 255))
        log_surface.blit(title_text, (self.padding, self.padding))
        
        # Draw separator
        pygame.draw.line(log_surface, self.border_color, 
                        (self.padding, 35), 
                        (self.width - self.padding, 35), 1)
        
        # Draw entries (newest at bottom, scrollable)
        y_offset = self.height - self.padding
        visible_entries = list(self.entries)[self.scroll_offset:]
        
        # Reverse to show newest at bottom
        for i, entry in enumerate(reversed(visible_entries)):
            # Calculate position from bottom
            entry_y = y_offset - (i + 1) * self.line_height
            
            # Stop if we've gone above the visible area
            if entry_y < 40:
                break
            
            # Apply fade to text color
            text_color = (*entry['color'], int(255 * alpha / 255))
            
            # Render and draw text
            text_surface = font.render(entry['text'], True, entry['color'])
            text_surface.set_alpha(alpha)
            
            # Truncate text if too long
            if text_surface.get_width() > self.width - self.padding * 2:
                # Truncate with ellipsis
                truncated_text = entry['text']
                while text_surface.get_width() > self.width - self.padding * 2 - 20:
                    truncated_text = truncated_text[:-1]
                    text_surface = font.render(truncated_text + "...", True, entry['color'])
                text_surface.set_alpha(alpha)
            
            log_surface.blit(text_surface, (self.padding, entry_y))
        
        # Draw scroll indicator if needed
        if self.scroll_offset > 0:
            scroll_text = font.render("▲ More", True, (150, 150, 200))
            scroll_text.set_alpha(alpha)
            log_surface.blit(scroll_text, (self.width - 60, 40))
        
        if len(visible_entries) > self.height // self.line_height:
            scroll_text = font.render("▼ More", True, (150, 150, 200))
            scroll_text.set_alpha(alpha)
            log_surface.blit(scroll_text, (self.width - 60, self.height - 25))
        
        # Blit log surface to screen
        screen.blit(log_surface, (x, y))
    
    def toggle(self):
        """Toggle combat log visibility"""
        self.enabled = not self.enabled
    
    def clear(self):
        """Clear all entries"""
        self.entries.clear()
        self.scroll_offset = 0
    
    def update(self, dt=None):
        """
        Update combat log state
        
        Args:
            dt: Delta time (optional, currently uses system time)
        """
        # Combat log uses system time (time.time()) for fade effects
        # This method exists for compatibility with game loop update calls
        # Auto-fade is handled by get_alpha() based on last_entry_time
        pass
