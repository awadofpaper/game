"""
Cosmetic pet system that follows the player
Supports multiple pet types unlocked through achievements
"""
import pygame
import math
import random


# Pet visual definitions
PET_DEFINITIONS = {
    "chicken": {
        "name": "Chicken",
        "body_color": (255, 255, 255),
        "accent_color": (255, 140, 0),  # beak
        "feature_color": (200, 50, 50),  # comb/feet
        "size": 16
    },
    "dog": {
        "name": "Dog",
        "body_color": (139, 90, 43),
        "accent_color": (210, 180, 140),  # snout
        "feature_color": (0, 0, 0),  # nose
        "size": 18
    },
    "cat": {
        "name": "Cat",
        "body_color": (255, 140, 0),
        "accent_color": (255, 200, 150),
        "feature_color": (0, 0, 0),
        "size": 14
    },
    "mouse": {
        "name": "Mouse",
        "body_color": (150, 150, 150),
        "accent_color": (255, 192, 203),  # ears
        "feature_color": (0, 0, 0),
        "size": 8
    },
    "snake": {
        "name": "Snake",
        "body_color": (34, 139, 34),
        "accent_color": (144, 238, 144),
        "feature_color": (255, 0, 0),  # tongue
        "size": 12
    },
    "cow": {
        "name": "Cow",
        "body_color": (255, 255, 255),
        "accent_color": (0, 0, 0),  # spots
        "feature_color": (255, 192, 203),  # udder
        "size": 24
    },
    "monkey": {
        "name": "Monkey",
        "body_color": (139, 90, 43),
        "accent_color": (255, 200, 150),
        "feature_color": (255, 140, 0),
        "size": 16
    },
    "wolf": {
        "name": "Wolf",
        "body_color": (105, 105, 105),
        "accent_color": (169, 169, 169),
        "feature_color": (255, 255, 255),
        "size": 20
    },
    "fox": {
        "name": "Fox",
        "body_color": (255, 87, 34),
        "accent_color": (255, 255, 255),
        "feature_color": (0, 0, 0),
        "size": 16
    },
    "bear": {
        "name": "Bear",
        "body_color": (101, 67, 33),
        "accent_color": (139, 90, 43),
        "feature_color": (0, 0, 0),
        "size": 26
    },
    "beaver": {
        "name": "Beaver",
        "body_color": (139, 90, 43),
        "accent_color": (160, 82, 45),
        "feature_color": (255, 140, 0),  # teeth
        "size": 16
    },
    "otter": {
        "name": "Otter",
        "body_color": (101, 67, 33),
        "accent_color": (210, 180, 140),
        "feature_color": (0, 0, 139),  # water theme
        "size": 14
    },
    "raccoon": {
        "name": "Raccoon",
        "body_color": (105, 105, 105),
        "accent_color": (255, 255, 255),
        "feature_color": (0, 0, 0),  # mask
        "size": 16
    },
    "parrot": {
        "name": "Parrot",
        "body_color": (255, 0, 0),
        "accent_color": (0, 255, 0),
        "feature_color": (0, 0, 255),
        "size": 14
    },
    "horse": {
        "name": "Horse",
        "body_color": (139, 90, 43),
        "accent_color": (101, 67, 33),
        "feature_color": (255, 255, 255),
        "size": 28
    },
    "bat": {
        "name": "Bat",
        "body_color": (0, 0, 0),
        "accent_color": (105, 105, 105),
        "feature_color": (255, 0, 0),
        "size": 12
    },
    "pig": {
        "name": "Pig",
        "body_color": (255, 192, 203),
        "accent_color": (255, 182, 193),
        "feature_color": (255, 105, 180),
        "size": 18
    },
    "owl": {
        "name": "Owl",
        "body_color": (139, 90, 43),
        "accent_color": (255, 255, 255),
        "feature_color": (255, 215, 0),  # eyes
        "size": 16
    },
    "eagle": {
        "name": "Eagle",
        "body_color": (101, 67, 33),
        "accent_color": (255, 255, 255),
        "feature_color": (255, 215, 0),
        "size": 18
    },
    "rabbit": {
        "name": "Rabbit",
        "body_color": (255, 255, 255),
        "accent_color": (255, 192, 203),  # ears
        "feature_color": (255, 182, 193),
        "size": 12
    },
    "rooster": {
        "name": "Rooster",
        "body_color": (139, 0, 0),
        "accent_color": (255, 215, 0),
        "feature_color": (255, 0, 0),
        "size": 16
    },
    "dragon": {
        "name": "Dragon",
        "body_color": (255, 0, 0),
        "accent_color": (255, 215, 0),
        "feature_color": (255, 140, 0),
        "size": 24
    },
    "phoenix": {
        "name": "Phoenix",
        "body_color": (255, 140, 0),
        "accent_color": (255, 0, 0),
        "feature_color": (255, 215, 0),
        "size": 20
    }
}


class PetCompanion:
    """A pet companion that follows the player around"""
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.enabled = False
        self.current_pet = "chicken"  # Current active pet
        self.follow_distance = 40  # Distance to stay behind player
        self.teleport_distance = 300  # Teleport if too far away
        
        # Animation states
        self.hop_timer = 0
        self.hop_height = 0  # For bobbing animation
        self.hop_speed = 8.0
        
        # Pecking animation
        self.idle_timer = 0
        self.idle_threshold = 3.0  # Start pecking after 3 seconds of player idle
        self.peck_timer = 0
        self.peck_duration = 0.5
        self.is_pecking = False
        self.peck_angle = 0  # Head rotation for pecking
        
        # Random movement when idle
        self.wander_timer = 0
        self.wander_target_x = 0
        self.wander_target_y = 0
        
    def toggle(self, player_x, player_y):
        """Toggle pet on/off"""
        self.enabled = not self.enabled
        if self.enabled:
            # Spawn behind player
            self.x = player_x
            self.y = player_y + self.follow_distance
            self.idle_timer = 0
        return self.enabled
    
    def set_pet(self, pet_type):
        """Change current pet type"""
        if pet_type in PET_DEFINITIONS:
            self.current_pet = pet_type
            return True
        return False
    
    def cycle_pet(self, unlocked_pets):
        """Cycle to next unlocked pet"""
        if not unlocked_pets:
            return
        
        try:
            current_index = unlocked_pets.index(self.current_pet)
            next_index = (current_index + 1) % len(unlocked_pets)
            self.current_pet = unlocked_pets[next_index]
        except ValueError:
            # Current pet not in list, use first
            self.current_pet = unlocked_pets[0]
    
    def update(self, dt, player_x, player_y, player_moving):
        """Update chicken position and animation"""
        if not self.enabled:
            return
        
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Teleport if too far away
        if distance > self.teleport_distance:
            self.x = player_x - dx / distance * self.follow_distance
            self.y = player_y - dy / distance * self.follow_distance
            return
        
        # Update idle timer
        if player_moving:
            self.idle_timer = 0
            self.is_pecking = False
        else:
            self.idle_timer += dt
        
        # Follow player if they're moving or too far
        if player_moving and distance > self.follow_distance:
            # Move towards player
            speed = 120  # Pixels per second
            move_x = (dx / distance) * speed * dt
            move_y = (dy / distance) * speed * dt
            self.x += move_x
            self.y += move_y
            
            # Hopping animation when moving
            self.hop_timer += dt * self.hop_speed
            self.hop_height = abs(math.sin(self.hop_timer)) * 8
            
        else:
            # Player is idle or chicken is close enough
            self.hop_height = 0
            
            # Start pecking animation after idle threshold
            if self.idle_timer > self.idle_threshold:
                if not self.is_pecking:
                    # Start new peck cycle
                    if random.random() < 0.3 * dt:  # Random chance to peck
                        self.is_pecking = True
                        self.peck_timer = 0
                
                # Random wandering when idle
                self.wander_timer += dt
                if self.wander_timer > 2.0:
                    # Pick new wander target near current position
                    self.wander_target_x = self.x + random.uniform(-20, 20)
                    self.wander_target_y = self.y + random.uniform(-20, 20)
                    self.wander_timer = 0
                
                # Move towards wander target slowly
                wander_dx = self.wander_target_x - self.x
                wander_dy = self.wander_target_y - self.y
                wander_dist = math.sqrt(wander_dx * wander_dx + wander_dy * wander_dy)
                if wander_dist > 2:
                    wander_speed = 20 * dt
                    self.x += (wander_dx / wander_dist) * wander_speed
                    self.y += (wander_dy / wander_dist) * wander_speed
        
        # Update pecking animation
        if self.is_pecking:
            self.peck_timer += dt
            # Peck down and up
            peck_progress = self.peck_timer / self.peck_duration
            if peck_progress < 0.5:
                # Peck down
                self.peck_angle = peck_progress * 2 * 45  # 45 degrees max
            else:
                # Peck up
                self.peck_angle = (1 - (peck_progress - 0.5) * 2) * 45
            
            if self.peck_timer >= self.peck_duration:
                self.is_pecking = False
                self.peck_angle = 0
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the pet with type-specific appearance"""
        if not self.enabled:
            return
        
        pet_def = PET_DEFINITIONS.get(self.current_pet, PET_DEFINITIONS["chicken"])
        
        # Screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y - self.hop_height)
        
        size = pet_def["size"]
        body_color = pet_def["body_color"]
        accent_color = pet_def["accent_color"]
        feature_color = pet_def["feature_color"]
        
        # Draw shadow
        shadow_rect = pygame.Rect(screen_x - size//2, int(self.y - camera_y) + size//2, size, size//4)
        pygame.draw.ellipse(screen, (50, 50, 50), shadow_rect)
        
        # Draw based on pet type
        if self.current_pet == "chicken":
            self._draw_chicken(screen, screen_x, screen_y, body_color, accent_color, feature_color)
        elif self.current_pet in ["dog", "wolf", "fox"]:
            self._draw_canine(screen, screen_x, screen_y, body_color, accent_color, feature_color, size)
        elif self.current_pet == "cat":
            self._draw_cat(screen, screen_x, screen_y, body_color, accent_color, feature_color, size)
        elif self.current_pet == "snake":
            self._draw_snake(screen, screen_x, screen_y, body_color, accent_color, feature_color, size)
        elif self.current_pet in ["cow", "pig", "bear", "horse"]:
            self._draw_large_mammal(screen, screen_x, screen_y, body_color, accent_color, feature_color, size)
        elif self.current_pet == "mouse":
            self._draw_mouse(screen, screen_x, screen_y, body_color, accent_color, feature_color, size)
        elif self.current_pet in ["parrot", "owl", "eagle", "bat", "rooster", "phoenix"]:
            self._draw_bird(screen, screen_x, screen_y, body_color, accent_color, feature_color, size)
        elif self.current_pet == "rabbit":
            self._draw_rabbit(screen, screen_x, screen_y, body_color, accent_color, feature_color, size)
        elif self.current_pet == "dragon":
            self._draw_dragon(screen, screen_x, screen_y, body_color, accent_color, feature_color, size)
        else:
            # Generic pet (simple circle)
            self._draw_generic(screen, screen_x, screen_y, body_color, accent_color, size)
    
    def _draw_generic(self, screen, x, y, body_color, accent_color, size):
        """Generic pet drawing"""
        # Body
        pygame.draw.circle(screen, body_color, (x, y), size//2)
        pygame.draw.circle(screen, accent_color, (x, y), size//2, 2)
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (x - size//6, y - size//8), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + size//6, y - size//8), 2)
    
    def _draw_chicken(self, screen, x, y, body_color, accent_color, feature_color):
        # Define chicken dimensions
        body_width = 20
        body_height = 16
        screen_x = x
        screen_y = y
        foot_y = screen_y + body_height // 2 + 2
        # Left foot
        pygame.draw.line(screen, (255, 200, 0), 
                        (screen_x - 4, screen_y + body_height // 2), 
                        (screen_x - 4, foot_y), 2)
        pygame.draw.line(screen, (200, 50, 50), 
                        (screen_x - 4, foot_y), 
                        (screen_x - 7, foot_y + 2), 2)
        pygame.draw.line(screen, (200, 50, 50), 
                        (screen_x - 4, foot_y), 
                        (screen_x - 1, foot_y + 2), 2)
        
        # Right foot
        pygame.draw.line(screen, (255, 200, 0), 
                        (screen_x + 4, screen_y + body_height // 2), 
                        (screen_x + 4, foot_y), 2)
        pygame.draw.line(screen, (200, 50, 50), 
                        (screen_x + 4, foot_y), 
                        (screen_x + 1, foot_y + 2), 2)
        pygame.draw.line(screen, (200, 50, 50), 
                        (screen_x + 4, foot_y), 
                        (screen_x + 7, foot_y + 2), 2)
        
        # Draw body (white oval)
        body_rect = pygame.Rect(screen_x - body_width // 2, screen_y - body_height // 2, 
                               body_width, body_height)
        pygame.draw.ellipse(screen, (255, 255, 255), body_rect)
        pygame.draw.ellipse(screen, (200, 200, 200), body_rect, 1)  # Outline
        
        # Draw wings (small white curves on sides)
        # Left wing
        wing_points_left = [
            (screen_x - body_width // 2, screen_y - 2),
            (screen_x - body_width // 2 - 4, screen_y),
            (screen_x - body_width // 2, screen_y + 2)
        ]
        pygame.draw.lines(screen, (220, 220, 220), False, wing_points_left, 2)
        
        # Right wing
        wing_points_right = [
            (screen_x + body_width // 2, screen_y - 2),
            (screen_x + body_width // 2 + 4, screen_y),
            (screen_x + body_width // 2, screen_y + 2)
        ]
        pygame.draw.lines(screen, (220, 220, 220), False, wing_points_right, 2)
        
        # Draw head (white circle, rotates when pecking)
        head_offset_y = -6
        if self.is_pecking:
            # Tilt head down when pecking
            head_offset_y = -6 + int(self.peck_angle / 45 * 4)
        
        head_x = screen_x + 6
        head_y = screen_y + head_offset_y
        pygame.draw.circle(screen, (255, 255, 255), (head_x, head_y), 5)
        pygame.draw.circle(screen, (200, 200, 200), (head_x, head_y), 5, 1)
        
        # Draw eyes (two small black dots)
        eye_y = head_y - 1
        pygame.draw.circle(screen, (0, 0, 0), (head_x + 2, eye_y), 1)
        pygame.draw.circle(screen, (0, 0, 0), (head_x + 2, eye_y + 2), 1)
        
        # Draw beak (orange triangle)
        beak_tip_x = head_x + 7
        beak_tip_y = head_y + 1
        if self.is_pecking:
            beak_tip_y += int(self.peck_angle / 45 * 3)
        
        beak_points = [
            (head_x + 4, head_y),
            (beak_tip_x, beak_tip_y),
            (head_x + 4, head_y + 2)
        ]
        pygame.draw.polygon(screen, (255, 140, 0), beak_points)
        
        # Draw comb (red bumps on top of head)
        comb_y = head_y - 4
        pygame.draw.circle(screen, (200, 50, 50), (head_x - 1, comb_y), 2)
        pygame.draw.circle(screen, (200, 50, 50), (head_x + 1, comb_y), 2)
    
    def _draw_canine(self, screen, x, y, body_color, accent_color, feature_color, size):
        """Draw dog/wolf/fox style pet"""
        # Body
        pygame.draw.ellipse(screen, body_color, (x - size//2, y - size//3, size, size//1.5))
        # Head
        pygame.draw.circle(screen, body_color, (x + size//3, y - size//4), size//3)
        # Snout
        pygame.draw.circle(screen, accent_color, (x + size//2, y - size//6), size//5)
        # Nose
        pygame.draw.circle(screen, feature_color, (x + size//2 + 2, y - size//6), 2)
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (x + size//4, y - size//3), 2)
        # Ears
        pygame.draw.polygon(screen, body_color, [(x + size//6, y - size//2), (x + size//4, y - size//2 - 4), (x + size//3, y - size//2)])
        # Tail
        pygame.draw.line(screen, body_color, (x - size//2, y), (x - size//2 - 4, y - 6), 3)
    
    def _draw_cat(self, screen, x, y, body_color, accent_color, feature_color, size):
        """Draw cat style pet"""
        # Body
        pygame.draw.ellipse(screen, body_color, (x - size//2, y - size//3, size, size//1.5))
        # Head
        pygame.draw.circle(screen, body_color, (x + size//3, y - size//4), size//3)
        # Ears (pointed)
        pygame.draw.polygon(screen, body_color, [(x + size//5, y - size//2), (x + size//4, y - size//2 - 6), (x + size//3, y - size//2)])
        pygame.draw.polygon(screen, body_color, [(x + size//3, y - size//2), (x + size//2 - 2, y - size//2 - 6), (x + size//2, y - size//2)])
        # Eyes
        pygame.draw.circle(screen, feature_color, (x + size//4, y - size//3), 2)
        pygame.draw.circle(screen, feature_color, (x + size//3 + 2, y - size//3), 2)
        # Whiskers
        pygame.draw.line(screen, (0, 0, 0), (x + size//3, y - size//5), (x + size//2 + 4, y - size//5), 1)
        # Tail (curved up)
        pygame.draw.arc(screen, body_color, (x - size//2 - 4, y - size//2, 8, size), 0, 3.14, 2)
    
    def _draw_snake(self, screen, x, y, body_color, accent_color, feature_color, size):
        """Draw snake style pet"""
        # Coiled body
        for i in range(3):
            offset = i * 4
            pygame.draw.circle(screen, body_color, (x - offset + 2, y + offset - 4), size//3)
        # Head
        pygame.draw.circle(screen, body_color, (x + 4, y - 4), size//2)
        pygame.draw.circle(screen, accent_color, (x + 4, y - 4), size//2, 1)
        # Eyes
        pygame.draw.circle(screen, (255, 255, 0), (x + 2, y - 6), 2)
        pygame.draw.circle(screen, (255, 255, 0), (x + 6, y - 6), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + 2, y - 6), 1)
        pygame.draw.circle(screen, (0, 0, 0), (x + 6, y - 6), 1)
        # Tongue
        if self.is_pecking:
            pygame.draw.line(screen, feature_color, (x + 6, y - 2), (x + 10, y - 4), 1)
            pygame.draw.line(screen, feature_color, (x + 6, y - 2), (x + 10, y), 1)
    
    def _draw_large_mammal(self, screen, x, y, body_color, accent_color, feature_color, size):
        """Draw cow/pig/bear/horse style pet"""
        # Body
        pygame.draw.ellipse(screen, body_color, (x - size//2, y - size//3, size, size//1.5))
        # Head
        pygame.draw.ellipse(screen, body_color, (x + size//3, y - size//4, size//2, size//2.5))
        # Snout
        pygame.draw.ellipse(screen, accent_color, (x + size//2, y - size//8, size//4, size//5))
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (x + size//3, y - size//4), 2)
        # Legs
        pygame.draw.line(screen, body_color, (x - size//4, y + size//6), (x - size//4, y + size//3), 3)
        pygame.draw.line(screen, body_color, (x + size//4, y + size//6), (x + size//4, y + size//3), 3)
        # Tail
        pygame.draw.line(screen, accent_color, (x - size//2, y), (x - size//2 - 4, y + 4), 2)
    
    def _draw_mouse(self, screen, x, y, body_color, accent_color, feature_color, size):
        """Draw mouse style pet"""
        # Body (small)
        pygame.draw.ellipse(screen, body_color, (x - size//2, y - size//3, size, size//1.5))
        # Head
        pygame.draw.circle(screen, body_color, (x + size//4, y - size//4), size//3)
        # Ears (large)
        pygame.draw.circle(screen, accent_color, (x, y - size//2), size//3)
        pygame.draw.circle(screen, accent_color, (x + size//3, y - size//2), size//3)
        pygame.draw.circle(screen, body_color, (x, y - size//2), size//4)
        pygame.draw.circle(screen, body_color, (x + size//3, y - size//2), size//4)
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (x + size//6, y - size//3), 1)
        # Tail (long thin)
        pygame.draw.line(screen, body_color, (x - size//2, y), (x - size - 2, y + 2), 1)
    
    def _draw_bird(self, screen, x, y, body_color, accent_color, feature_color, size):
        """Draw bird style pet (parrot/owl/eagle/bat)"""
        # Body
        pygame.draw.ellipse(screen, body_color, (x - size//3, y - size//2, size//1.5, size))
        # Head
        pygame.draw.circle(screen, body_color, (x, y - size//2), size//3)
        # Beak
        beak_y = y - size//2
        if self.is_pecking:
            beak_y += int(self.peck_angle / 45 * 2)
        pygame.draw.polygon(screen, feature_color, [(x + size//6, y - size//2), (x + size//3, beak_y), (x + size//6, y - size//2 + 2)])
        # Wings
        pygame.draw.ellipse(screen, accent_color, (x - size//2, y - size//4, size//3, size//2))
        pygame.draw.ellipse(screen, accent_color, (x + size//6, y - size//4, size//3, size//2))
        # Eyes
        pygame.draw.circle(screen, (255, 255, 255), (x - size//8, y - size//2), 3)
        pygame.draw.circle(screen, (255, 255, 255), (x + size//8, y - size//2), 3)
        pygame.draw.circle(screen, (0, 0, 0), (x - size//8, y - size//2), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + size//8, y - size//2), 2)
    
    def _draw_rabbit(self, screen, x, y, body_color, accent_color, feature_color, size):
        """Draw rabbit style pet"""
        # Body
        pygame.draw.ellipse(screen, body_color, (x - size//3, y - size//3, size//1.5, size//1.5))
        # Head
        pygame.draw.circle(screen, body_color, (x + size//4, y - size//4), size//3)
        # Long ears
        pygame.draw.ellipse(screen, body_color, (x, y - size, size//4, size//1.5))
        pygame.draw.ellipse(screen, accent_color, (x + 1, y - size + 2, size//5, size//2))
        pygame.draw.ellipse(screen, body_color, (x + size//4, y - size, size//4, size//1.5))
        pygame.draw.ellipse(screen, accent_color, (x + size//4 + 1, y - size + 2, size//5, size//2))
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (x + size//6, y - size//4), 2)
        # Tail (fluffy)
        pygame.draw.circle(screen, body_color, (x - size//2, y), size//4)
    
    def _draw_dragon(self, screen, x, y, body_color, accent_color, feature_color, size):
        """Draw dragon style pet"""
        # Body (larger, scaled)
        pygame.draw.ellipse(screen, body_color, (x - size//2, y - size//3, size, size//1.5))
        # Head
        pygame.draw.polygon(screen, body_color, [(x + size//3, y - size//3), (x + size//2, y - size//4), (x + size//2, y - size//6)])
        # Horns
        pygame.draw.polygon(screen, feature_color, [(x + size//2 - 2, y - size//3), (x + size//2, y - size//2), (x + size//2 + 2, y - size//3)])
        # Wings
        pygame.draw.polygon(screen, accent_color, [(x - size//4, y - size//4), (x - size, y - size//2), (x - size//3, y)])
        pygame.draw.polygon(screen, accent_color, [(x + size//6, y - size//4), (x + size, y - size//2), (x + size//3, y)])
        # Eyes
        pygame.draw.circle(screen, (255, 255, 0), (x + size//3, y - size//4), 2)
        # Tail (long)
        pygame.draw.line(screen, body_color, (x - size//2, y), (x - size, y + size//4), 3)
        pygame.draw.polygon(screen, feature_color, [(x - size, y + size//4 - 2), (x - size - 4, y + size//4), (x - size, y + size//4 + 2)])
