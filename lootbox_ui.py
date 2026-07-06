"""
Loot Box Animation UI - The predatory microtransaction experience

Features an exciting (and suspenseful) chest opening animation that flashes
random cosmetics for 5-8 seconds before revealing your "prize".
"""

import pygame
import random
import math
import time
from typing import Optional, List
from cosmetic_system import Cosmetic, CosmeticGenerator, CosmeticRarity


class LootBoxAnimation:
    """Handles the chest opening animation and skin reveal"""
    
    # Animation states
    STATE_IDLE = "idle"
    STATE_CHEST_APPEAR = "chest_appear"
    STATE_CHEST_OPENING = "chest_opening"
    STATE_FLASHING = "flashing"
    STATE_SLOWING = "slowing"
    STATE_REVEAL = "reveal"
    STATE_CELEBRATE = "celebrate"
    STATE_DONE = "done"
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Animation state
        self.state = self.STATE_IDLE
        self.animation_time = 0.0
        self.total_duration = random.uniform(5.0, 8.0)  # 5-8 seconds
        
        # Chest properties
        self.chest_x = screen_width // 2
        self.chest_y = screen_height // 2
        self.chest_width = 150
        self.chest_height = 120
        self.chest_scale = 0.0
        self.lid_angle = 0.0  # 0 = closed, 90 = open
        
        # Flashing cosmetics
        self.flash_cosmetics: List[Cosmetic] = []
        self.current_flash_index = 0
        self.flash_speed = 10.0  # Changes per second
        self.current_cosmetic: Optional[Cosmetic] = None
        self.final_cosmetic: Optional[Cosmetic] = None
        
        # Particle effects
        self.particles: List[dict] = []
        
        # Celebration
        self.celebration_scale = 1.0
        self.celebration_rotation = 0.0
        
    def start_animation(self, won_cosmetic: Cosmetic):
        """Begin the loot box opening sequence"""
        self.state = self.STATE_CHEST_APPEAR
        self.animation_time = 0.0
        self.total_duration = random.uniform(5.0, 8.0)
        self.final_cosmetic = won_cosmetic
        
        # Generate lots of random cosmetics to flash through
        self.flash_cosmetics = []
        for _ in range(50):
            rarity = CosmeticGenerator.roll_rarity()
            cosmetic = CosmeticGenerator.generate_cosmetic(
                applies_to=won_cosmetic.applies_to,
                force_rarity=rarity
            )
            self.flash_cosmetics.append(cosmetic)
        
        # Add the final cosmetic at the end
        self.flash_cosmetics.append(won_cosmetic)
        
        self.current_flash_index = 0
        self.current_cosmetic = self.flash_cosmetics[0]
        self.particles = []
        
    def update(self, dt: float):
        """Update animation state"""
        if self.state == self.STATE_IDLE or self.state == self.STATE_DONE:
            return
        
        self.animation_time += dt
        
        if self.state == self.STATE_CHEST_APPEAR:
            # Chest scales up
            self.chest_scale = min(1.0, self.animation_time / 0.5)
            if self.animation_time >= 0.5:
                self.state = self.STATE_CHEST_OPENING
                self.animation_time = 0.0
                
        elif self.state == self.STATE_CHEST_OPENING:
            # Lid opens
            self.lid_angle = min(90.0, (self.animation_time / 0.3) * 90)
            if self.animation_time >= 0.3:
                self.state = self.STATE_FLASHING
                self.animation_time = 0.0
                
        elif self.state == self.STATE_FLASHING:
            # Fast flashing through cosmetics
            if self.animation_time < self.total_duration * 0.7:
                # Full speed flashing
                self.flash_speed = 15.0
                new_index = int(self.animation_time * self.flash_speed) % len(self.flash_cosmetics)
                if new_index != self.current_flash_index:
                    self.current_flash_index = new_index
                    self.current_cosmetic = self.flash_cosmetics[self.current_flash_index]
                    self._spawn_particles()
            else:
                self.state = self.STATE_SLOWING
                self.animation_time = 0.0
                
        elif self.state == self.STATE_SLOWING:
            # Slow down the flashing
            progress = self.animation_time / (self.total_duration * 0.3)
            self.flash_speed = 15.0 * (1.0 - progress) + 1.0 * progress
            
            new_index = int((self.animation_time * self.flash_speed)) % len(self.flash_cosmetics)
            # Ensure we're getting close to the final cosmetic
            if progress > 0.8:
                new_index = len(self.flash_cosmetics) - 1
            
            if new_index != self.current_flash_index:
                self.current_flash_index = new_index
                self.current_cosmetic = self.flash_cosmetics[self.current_flash_index]
                self._spawn_particles()
            
            if self.animation_time >= self.total_duration * 0.3:
                self.state = self.STATE_REVEAL
                self.animation_time = 0.0
                self.current_cosmetic = self.final_cosmetic
                self._spawn_celebration_particles()
                
        elif self.state == self.STATE_REVEAL:
            # Show the final cosmetic with celebration
            self.celebration_scale = 1.0 + math.sin(self.animation_time * 5) * 0.1
            self.celebration_rotation = math.sin(self.animation_time * 3) * 5
            
            if self.animation_time >= 2.0:
                self.state = self.STATE_CELEBRATE
                self.animation_time = 0.0
                
        elif self.state == self.STATE_CELEBRATE:
            # Keep celebrating
            self.celebration_scale = 1.0 + math.sin(self.animation_time * 3) * 0.05
            self.celebration_rotation = math.sin(self.animation_time * 2) * 3
        
        # Update particles
        self._update_particles(dt)
    
    def _spawn_particles(self):
        """Spawn particles during flashing"""
        for _ in range(3):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.particles.append({
                'x': self.chest_x,
                'y': self.chest_y - 50,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 50,
                'life': 0.5,
                'max_life': 0.5,
                'color': self.current_cosmetic.primary_color if self.current_cosmetic else (255, 255, 255)
            })
    
    def _spawn_celebration_particles(self):
        """Spawn celebration particles when revealing final cosmetic"""
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 300)
            self.particles.append({
                'x': self.chest_x,
                'y': self.chest_y - 50,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 100,
                'life': 1.5,
                'max_life': 1.5,
                'color': self.final_cosmetic.primary_color if self.final_cosmetic else (255, 255, 255)
            })
    
    def _update_particles(self, dt: float):
        """Update particle physics"""
        gravity = 400
        for p in self.particles[:]:
            p['life'] -= dt
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += gravity * dt
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the loot box animation"""
        if self.state == self.STATE_IDLE or self.state == self.STATE_DONE:
            return
        
        # Draw darkened background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw particles
        for p in self.particles:
            alpha = int((p['life'] / p['max_life']) * 255)
            size = int((p['life'] / p['max_life']) * 8) + 2
            color = p['color']
            
            # Create particle surface with alpha
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*color, alpha), (size, size), size)
            screen.blit(particle_surf, (int(p['x']) - size, int(p['y']) - size))
        
        # Draw chest
        if self.state != self.STATE_IDLE:
            self._draw_chest(screen)
        
        # Draw current cosmetic display
        if self.current_cosmetic and self.state in [self.STATE_FLASHING, self.STATE_SLOWING, 
                                                      self.STATE_REVEAL, self.STATE_CELEBRATE]:
            self._draw_cosmetic_display(screen, font)
    
    def _draw_chest(self, screen: pygame.Surface):
        """Draw the chest with opening animation"""
        # Scale the chest
        scaled_width = int(self.chest_width * self.chest_scale)
        scaled_height = int(self.chest_height * self.chest_scale)
        
        chest_rect = pygame.Rect(
            self.chest_x - scaled_width // 2,
            self.chest_y - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        # Draw chest body
        pygame.draw.rect(screen, (139, 69, 19), chest_rect)  # Brown
        pygame.draw.rect(screen, (101, 67, 33), chest_rect, 3)  # Dark brown border
        
        # Draw lock/latch
        lock_rect = pygame.Rect(
            self.chest_x - 10,
            self.chest_y,
            20,
            15
        )
        pygame.draw.rect(screen, (255, 215, 0), lock_rect)  # Gold lock
        
        # Draw lid (rotates as it opens)
        if self.lid_angle > 0:
            # Simplified lid - just draw it higher up as it "opens"
            lid_offset = int((self.lid_angle / 90.0) * scaled_height * 0.8)
            lid_rect = pygame.Rect(
                self.chest_x - scaled_width // 2,
                self.chest_y - scaled_height // 2 - lid_offset,
                scaled_width,
                scaled_height // 3
            )
            pygame.draw.rect(screen, (160, 82, 45), lid_rect)  # Lighter brown
            pygame.draw.rect(screen, (101, 67, 33), lid_rect, 3)
            
            # Draw shiny glow coming from chest when open
            if self.lid_angle > 45:
                glow_alpha = int((self.lid_angle - 45) / 45 * 150)
                glow_surf = pygame.Surface((scaled_width, scaled_height * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, (255, 255, 100, glow_alpha),
                                  (0, 0, scaled_width, scaled_height * 2))
                screen.blit(glow_surf, (self.chest_x - scaled_width // 2, 
                                       self.chest_y - scaled_height // 2))
    
    def _draw_cosmetic_display(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the current cosmetic being shown"""
        if not self.current_cosmetic:
            return
        
        # Display area above chest
        display_y = self.chest_y - 200
        
        # Apply celebration effects
        scale = self.celebration_scale if self.state in [self.STATE_REVEAL, self.STATE_CELEBRATE] else 1.0
        
        # Draw cosmetic preview box
        box_width = int(250 * scale)
        box_height = int(150 * scale)
        box_rect = pygame.Rect(
            self.chest_x - box_width // 2,
            display_y - box_height // 2,
            box_width,
            box_height
        )
        
        # Background
        pygame.draw.rect(screen, (40, 40, 40), box_rect)
        
        # Rarity-colored border
        rarity_color = CosmeticRarity.COLORS.get(self.current_cosmetic.rarity, (150, 150, 150))
        border_width = 5 if self.state in [self.STATE_REVEAL, self.STATE_CELEBRATE] else 3
        pygame.draw.rect(screen, rarity_color, box_rect, border_width)
        
        # Draw cosmetic name
        name_text = font.render(self.current_cosmetic.name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(self.chest_x, display_y - 40))
        screen.blit(name_text, name_rect)
        
        # Draw rarity
        rarity_text = font.render(self.current_cosmetic.rarity, True, rarity_color)
        rarity_rect = rarity_text.get_rect(center=(self.chest_x, display_y))
        screen.blit(rarity_text, rarity_rect)
        
        # Draw color swatches
        swatch_size = 30
        swatch_y = display_y + 30
        
        # Primary color
        pygame.draw.rect(screen, self.current_cosmetic.primary_color,
                        (self.chest_x - swatch_size - 5, swatch_y, swatch_size, swatch_size))
        pygame.draw.rect(screen, (255, 255, 255),
                        (self.chest_x - swatch_size - 5, swatch_y, swatch_size, swatch_size), 2)
        
        # Secondary color
        pygame.draw.rect(screen, self.current_cosmetic.secondary_color,
                        (self.chest_x + 5, swatch_y, swatch_size, swatch_size))
        pygame.draw.rect(screen, (255, 255, 255),
                        (self.chest_x + 5, swatch_y, swatch_size, swatch_size), 2)
        
        # If this is the reveal state, show instructions
        if self.state in [self.STATE_REVEAL, self.STATE_CELEBRATE]:
            instruction_text = font.render("Press ENTER to continue", True, (255, 255, 255))
            instruction_rect = instruction_text.get_rect(center=(self.chest_x, display_y + 80))
            screen.blit(instruction_text, instruction_rect)
            
            # Show if duplicate
            if hasattr(self, 'is_duplicate') and self.is_duplicate:
                duplicate_text = font.render("(DUPLICATE - 30 dubloons refunded)", True, (255, 100, 100))
                dup_rect = duplicate_text.get_rect(center=(self.chest_x, display_y + 100))
                screen.blit(duplicate_text, dup_rect)
    
    def is_showing(self) -> bool:
        """Check if animation is currently showing"""
        return self.state not in [self.STATE_IDLE, self.STATE_DONE]
    
    def is_waiting_for_input(self) -> bool:
        """Check if waiting for player to acknowledge the result"""
        return self.state in [self.STATE_REVEAL, self.STATE_CELEBRATE]
    
    def finish(self):
        """Mark animation as complete"""
        self.state = self.STATE_DONE
    
    def get_final_cosmetic(self) -> Optional[Cosmetic]:
        """Get the cosmetic that was won"""
        return self.final_cosmetic
