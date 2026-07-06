"""
Tutorial NPC - Special NPC that guides new players through basic mechanics
"""

import pygame
import math

class TutorialNPC:
    """Tutorial guide NPC that teaches basic game mechanics"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = "tutorial_guide"
        self.name = "Wandering Guide"
        self.type = "tutorial_guide"
        
        # Combat properties (strong but not invincible)
        self.health = 275
        self.max_health = 275
        self.level = 12
        self.damage = 30
        self.defense = 12
        self.attack_range = 55
        self.attack_cooldown = 1.2
        self.last_attack_time = 0
        self.combat_target = None  # Player or enemy
        self.aggro_timer = 0  # Timer before retaliating
        
        # Inventory/Loot (special legendary items)
        self.inventory = {
            'Gold': 200,
            'Bread': 1,
            'Water': 1,
            'Basic Healing Herbs': 1
        }
        
        # Visual properties
        self.size = 32
        self.color = (100, 150, 255)  # Blue
        self.glow_color = (150, 200, 255)
        self.glow_pulse = 0.0
        self.glow_speed = 0.05
        
        # State
        self.facing_direction = 'down'
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Quest marker
        self.has_quest = True
        self.quest_marker_bounce = 0.0
        self.quest_marker_speed = 0.1
        
        # Interaction
        self.interaction_radius = 80
        self.dialogue_active = False
        
        # AI state
        self.declined_by_player = False  # Track if player politely declined
        self.going_to_shelter = False  # Track if NPC is walking to shelter
        self.at_shelter = False  # Track if NPC reached shelter
        self.shack_x = None  # Shack location
        self.shack_y = None
        self.in_building = None  # Building ID if NPC is inside a building
        self.move_speed = 100  # Pixels per second
        
        # Tutorial tracking (will be updated by main game loop)
        self.tutorial_stage = 'initial'  # initial, collecting_sticks, sticks_collected, equipped_stacked, quest_complete
    
    def take_damage(self, amount, attacker=None):
        """Take damage and start fighting back"""
        self.health -= amount
        
        if self.health <= 0:
            self.health = 0
        else:
            # Fight back when attacked!
            if attacker and not self.combat_target:
                self.combat_target = attacker
                # Stop going to shelter if attacked
                self.going_to_shelter = False
    
    def attack_target(self, target, current_time):
        """Attack the player who attacked us"""
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        # Check range
        distance = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        if distance > self.attack_range:
            return False
        
        # Deal damage
        if hasattr(target, 'take_damage'):
            # Player's take_damage doesn't accept attacker parameter
            target.take_damage(self.damage)
        elif hasattr(target, 'health'):
            target.health -= self.damage
        
        self.last_attack_time = current_time
        return True
    
    def update(self, dt, player):
        """Update NPC state"""
        # If in combat, move towards target
        if self.combat_target and self.combat_target.health > 0:
            dx = self.combat_target.x - self.x
            dy = self.combat_target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            # Move towards target if out of range
            if distance > self.attack_range - 10:
                move_x = (dx / distance) * self.move_speed * dt
                move_y = (dy / distance) * self.move_speed * dt
                self.x += move_x
                self.y += move_y
                
                # Update facing direction
                if abs(dx) > abs(dy):
                    self.facing_direction = 'right' if dx > 0 else 'left'
                else:
                    self.facing_direction = 'down' if dy > 0 else 'up'
            else:
                # Face the target
                if abs(dx) > abs(dy):
                    self.facing_direction = 'right' if dx > 0 else 'left'
                else:
                    self.facing_direction = 'down' if dy > 0 else 'up'
        # If going to shelter (not in combat), move towards shack
        elif self.going_to_shelter and not self.at_shelter and self.shack_x is not None:
            dx = self.shack_x - self.x
            dy = self.shack_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 10:  # Reached shelter
                self.at_shelter = True
                self.going_to_shelter = False
            else:
                # Move towards shack
                move_x = (dx / distance) * self.move_speed * dt
                move_y = (dy / distance) * self.move_speed * dt
                self.x += move_x
                self.y += move_y
                
                # Update facing direction based on movement
                if abs(dx) > abs(dy):
                    self.facing_direction = 'right' if dx > 0 else 'left'
                else:
                    self.facing_direction = 'down' if dy > 0 else 'up'
        else:
            # Always face the player when not moving
            dx = player.x - self.x
            dy = player.y - self.y
            
            if abs(dx) > abs(dy):
                self.facing_direction = 'right' if dx > 0 else 'left'
            else:
                self.facing_direction = 'down' if dy > 0 else 'up'
        
        # Update glow pulse
        self.glow_pulse += self.glow_speed
        if self.glow_pulse > 2 * math.pi:
            self.glow_pulse -= 2 * math.pi
        
        # Update quest marker bounce
        if self.has_quest:
            self.quest_marker_bounce += self.quest_marker_speed
            if self.quest_marker_bounce > 2 * math.pi:
                self.quest_marker_bounce -= 2 * math.pi
    
    def is_player_nearby(self, player):
        """Check if player is close enough to interact"""
        distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        return distance < self.interaction_radius
    
    def get_screen_position(self, camera_x, camera_y):
        """Get position on screen relative to camera"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        return screen_x, screen_y
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the NPC"""
        screen_x, screen_y = self.get_screen_position(camera_x, camera_y)
        
        # Don't draw if off-screen
        if screen_x < -50 or screen_x > screen.get_width() + 50:
            return
        if screen_y < -50 or screen_y > screen.get_height() + 50:
            return
        
        # Draw glow effect
        glow_intensity = int(50 + 30 * math.sin(self.glow_pulse))
        glow_radius = self.size + 10
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.glow_color, glow_intensity), 
                         (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (int(screen_x - glow_radius), int(screen_y - glow_radius)), 
                   special_flags=pygame.BLEND_RGBA_ADD)
        
        # Draw NPC body
        npc_rect = pygame.Rect(int(screen_x - self.size // 2), int(screen_y - self.size // 2), 
                               self.size, self.size)
        pygame.draw.rect(screen, self.color, npc_rect, border_radius=5)
        
        # Draw face based on direction
        face_color = (255, 255, 255)
        if self.facing_direction == 'down':
            # Eyes
            pygame.draw.circle(screen, face_color, (int(screen_x - 6), int(screen_y - 2)), 3)
            pygame.draw.circle(screen, face_color, (int(screen_x + 6), int(screen_y - 2)), 3)
            # Mouth
            pygame.draw.arc(screen, face_color, 
                          (int(screen_x - 6), int(screen_y + 2), 12, 8), 
                          math.pi, 0, 2)
        elif self.facing_direction == 'up':
            # Eyes
            pygame.draw.circle(screen, face_color, (int(screen_x - 6), int(screen_y)), 3)
            pygame.draw.circle(screen, face_color, (int(screen_x + 6), int(screen_y)), 3)
        elif self.facing_direction == 'left':
            # Eye
            pygame.draw.circle(screen, face_color, (int(screen_x - 4), int(screen_y)), 3)
        else:  # right
            # Eye
            pygame.draw.circle(screen, face_color, (int(screen_x + 4), int(screen_y)), 3)
        
        # Draw quest marker if has quest
        if self.has_quest and self.tutorial_stage != 'quest_complete':
            marker_bounce = int(10 * math.sin(self.quest_marker_bounce))
            marker_y = int(screen_y - self.size - 20 + marker_bounce)
            
            # Draw exclamation mark background
            marker_size = 24
            marker_rect = pygame.Rect(int(screen_x - marker_size // 2), marker_y - marker_size // 2,
                                     marker_size, marker_size)
            pygame.draw.rect(screen, (255, 215, 0), marker_rect, border_radius=marker_size // 2)
            
            # Draw exclamation mark
            try:
                font = pygame.font.Font(None, 36)
                marker_text = font.render("!", True, (0, 0, 0))
                text_rect = marker_text.get_rect(center=(int(screen_x), marker_y))
                screen.blit(marker_text, text_rect)
            except:
                pass
        
        # Draw name above NPC
        try:
            font = pygame.font.Font(None, 24)
            name_text = font.render(self.name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(int(screen_x), int(screen_y - self.size - 45)))
            
            # Draw name background
            bg_rect = name_rect.inflate(10, 4)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            screen.blit(bg_surface, bg_rect)
            
            screen.blit(name_text, name_rect)
        except:
            pass
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            bar_width = 60
            bar_height = 8
            bar_x = int(screen_x - bar_width // 2)
            bar_y = int(screen_y - self.size - 65)
            
            # Background
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            
            # Health fill
            health_ratio = max(0, self.health / self.max_health)
            health_width = int(bar_width * health_ratio)
            
            # Color based on health
            if health_ratio > 0.6:
                health_color = (0, 255, 0)
            elif health_ratio > 0.3:
                health_color = (255, 255, 0)
            else:
                health_color = (255, 0, 0)
            
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
            
            # Border
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
    
    def get_interaction_prompt(self):
        """Get the text to display when player is nearby"""
        if self.tutorial_stage == 'initial':
            return "Press T to talk to Wandering Guide"
        elif self.tutorial_stage == 'quest_complete':
            return "Press T to talk to Wandering Guide"
        else:
            return "Press T to talk to Wandering Guide"
    
    def update_tutorial_stage(self, stage):
        """Update the tutorial stage"""
        self.tutorial_stage = stage
        
        # Update quest marker visibility
        if stage == 'quest_complete':
            self.has_quest = False
        else:
            self.has_quest = True
