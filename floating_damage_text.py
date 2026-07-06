"""
Floating Damage Text System
Displays damage numbers that float upward and fade out
"""

import pygame
import time
import random

class FloatingDamageText:
    """Represents a single floating damage number"""
    def __init__(self, x, y, amount, is_critical=False, is_heal=False, is_dodge=False):
        self.x = x
        self.y = y
        self.amount = amount
        self.is_critical = is_critical
        self.is_heal = is_heal
        self.is_dodge = is_dodge
        self.start_time = time.time()
        self.duration = 1.5  # seconds
        
        # Visual properties
        if is_dodge:
            self.color = (200, 200, 255)  # Light blue for dodge
            self.text = "DODGE!"
            self.font_size = 24
        elif is_critical:
            self.color = (255, 255, 0)  # Yellow for crits
            self.text = str(int(amount))
            self.font_size = 32
        elif is_heal:
            self.color = (100, 255, 100)  # Green for healing
            self.text = "+" + str(int(amount))
            self.font_size = 24
        else:
            self.color = (255, 255, 255)  # White for normal damage
            self.text = str(int(amount))
            self.font_size = 24
        
        # Movement properties
        self.velocity_y = -80  # pixels per second (upward)
        self.velocity_x = random.uniform(-20, 20)  # Slight horizontal drift
        
        # Cache the rendered text
        self.font = pygame.font.SysFont("Arial", self.font_size, bold=is_critical)
        self.rendered_text = self.font.render(self.text, True, self.color)
        
    def update(self, dt):
        """Update position and check if expired"""
        elapsed = time.time() - self.start_time
        
        # Move upward with slight horizontal drift
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Slow down over time
        self.velocity_y *= 0.95
        
        return elapsed < self.duration
    
    def draw(self, screen, offset):
        """Draw the floating text with fade effect"""
        elapsed = time.time() - self.start_time
        alpha = int(255 * (1 - elapsed / self.duration))  # Fade out
        
        # Create a copy with alpha for fading
        text_surface = self.rendered_text.copy()
        text_surface.set_alpha(max(0, alpha))
        
        # Draw with screen offset
        screen_x = int(self.x - offset[0] - text_surface.get_width() / 2)
        screen_y = int(self.y - offset[1])
        
        # Draw outline for better visibility (critical hits)
        if self.is_critical and alpha > 128:
            outline_color = (128, 0, 0)
            outline_surface = self.font.render(self.text, True, outline_color)
            outline_surface.set_alpha(alpha)
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                screen.blit(outline_surface, (screen_x + dx, screen_y + dy))
        
        screen.blit(text_surface, (screen_x, screen_y))


class FloatingDamageTextManager:
    """Manages all floating damage text instances"""
    def __init__(self):
        self.texts = []
        self.max_texts = 50  # Limit for performance
    
    def add_damage(self, x, y, amount, is_critical=False):
        """Add a damage number"""
        if len(self.texts) >= self.max_texts:
            self.texts.pop(0)  # Remove oldest
        self.texts.append(FloatingDamageText(x, y, amount, is_critical=is_critical))
    
    def add_heal(self, x, y, amount):
        """Add a healing number"""
        if len(self.texts) >= self.max_texts:
            self.texts.pop(0)
        self.texts.append(FloatingDamageText(x, y, amount, is_heal=True))
    
    def add_dodge(self, x, y):
        """Add a dodge message"""
        if len(self.texts) >= self.max_texts:
            self.texts.pop(0)
        self.texts.append(FloatingDamageText(x, y, 0, is_dodge=True))
    
    def update(self, dt):
        """Update all floating texts and remove expired ones"""
        self.texts = [text for text in self.texts if text.update(dt)]
    
    def draw(self, screen, offset):
        """Draw all floating texts"""
        for text in self.texts:
            text.draw(screen, offset)
    
    def clear(self):
        """Remove all floating texts"""
        self.texts.clear()
