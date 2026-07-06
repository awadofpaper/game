"""
Smoke/Particle Effect System for visual effects
"""

import pygame
import random
import math

class SmokeParticle:
    """A single smoke particle"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-30, 30)  # Horizontal velocity
        self.vy = random.uniform(-80, -40)  # Upward velocity
        self.size = random.randint(8, 20)
        self.max_size = self.size + random.randint(15, 30)
        self.alpha = 255
        self.lifetime = random.uniform(0.8, 1.5)  # seconds
        self.age = 0
        self.color = random.choice([
            (200, 200, 200),
            (220, 220, 220),
            (180, 180, 180),
            (150, 150, 180),  # Slightly purple
        ])
    
    def update(self, dt):
        """Update particle position and properties"""
        self.age += dt
        
        # Move particle
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Slow down horizontal movement
        self.vx *= 0.95
        # Slow down vertical movement (gravity-like)
        self.vy *= 0.98
        
        # Grow size
        growth_rate = (self.max_size - self.size) / self.lifetime
        self.size += growth_rate * dt
        
        # Fade out
        fade_rate = 255 / self.lifetime
        self.alpha -= fade_rate * dt
        self.alpha = max(0, self.alpha)
    
    def is_dead(self):
        """Check if particle should be removed"""
        return self.age >= self.lifetime or self.alpha <= 0
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the particle"""
        if self.alpha <= 0:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Create a surface for the smoke particle with alpha
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        
        # Draw multiple circles for a softer look
        for i in range(3):
            radius = int(self.size * (1 - i * 0.3))
            alpha = int(self.alpha * (1 - i * 0.3))
            color = (*self.color, alpha)
            pygame.draw.circle(particle_surface, color, 
                             (int(self.size), int(self.size)), 
                             radius)
        
        # Blit to screen
        screen.blit(particle_surface, 
                   (screen_x - int(self.size), screen_y - int(self.size)),
                   special_flags=pygame.BLEND_ALPHA_SDL2)


class SmokeEffect:
    """Manages smoke particle effects"""
    
    def __init__(self):
        self.active_effects = []  # List of (x, y, particles, timer)
    
    def create_poof(self, x, y, particle_count=20):
        """Create a smoke poof effect at position"""
        particles = []
        for _ in range(particle_count):
            particles.append(SmokeParticle(x, y))
        
        self.active_effects.append({
            'x': x,
            'y': y,
            'particles': particles,
            'timer': 0
        })
    
    def update(self, dt):
        """Update all active effects"""
        for effect in self.active_effects[:]:
            effect['timer'] += dt
            
            # Update all particles
            for particle in effect['particles'][:]:
                particle.update(dt)
                if particle.is_dead():
                    effect['particles'].remove(particle)
            
            # Remove effect if all particles are dead
            if not effect['particles']:
                self.active_effects.remove(effect)
    
    def draw(self, screen, camera_x, camera_y):
        """Draw all active effects"""
        for effect in self.active_effects:
            for particle in effect['particles']:
                particle.draw(screen, camera_x, camera_y)
    
    def clear(self):
        """Clear all effects"""
        self.active_effects.clear()
