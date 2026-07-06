"""
Floating text system for damage numbers and combat feedback
"""
import pygame
import time

class FloatingText:
    """Animated floating text that rises and fades"""
    def __init__(self, text, position, color=(255, 255, 255), duration=1.5, font_size=20):
        """
        Create floating text
        
        Args:
            text: String to display
            position: (x, y) tuple for starting position
            color: RGB color tuple
            duration: How long the text lasts (seconds)
            font_size: Font size for the text
        """
        self.text = str(text)
        self.x, self.y = position
        self.start_y = self.y
        self.color = color
        self.duration = duration
        self.birth_time = time.time()
        self.alive = True
        
        # Movement parameters
        self.velocity_y = -50  # Pixels per second upward
        self.fade_start = 0.5  # Start fading after 50% of duration
        
        # Render the text
        try:
            self.font = pygame.font.Font(None, font_size)
        except (pygame.error, OSError, FileNotFoundError):
            self.font = pygame.font.SysFont('arial', font_size)
        
        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect(center=(self.x, self.y))
    
    def update(self, dt, camera_x=0, camera_y=0):
        """Update position and check if expired"""
        age = time.time() - self.birth_time
        
        if age >= self.duration:
            self.alive = False
            return
        
        # Move upward
        self.y += self.velocity_y * dt
        self.rect.centery = self.y
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the floating text with fade effect"""
        if not self.alive:
            return
        
        age = time.time() - self.birth_time
        
        # Calculate alpha (fade out in last 50% of lifetime)
        if age > self.duration * self.fade_start:
            progress = (age - self.duration * self.fade_start) / (self.duration * (1 - self.fade_start))
            alpha = int(255 * (1 - progress))
        else:
            alpha = 255
        
        # Create surface with alpha
        temp_surface = self.surface.copy()
        temp_surface.set_alpha(alpha)
        
        # Draw at screen position (adjusted for camera)
        screen_x = self.rect.centerx - camera_x
        screen_y = self.rect.centery - camera_y
        screen.blit(temp_surface, (screen_x - temp_surface.get_width() // 2, 
                                    screen_y - temp_surface.get_height() // 2))


class DamageNumber(FloatingText):
    """Specialized floating text for damage numbers"""
    def __init__(self, damage, position, is_crit=False, is_heal=False, is_dodge=False):
        """
        Create damage number
        
        Args:
            damage: Damage amount (integer or float)
            position: (x, y) tuple
            is_crit: True for critical hits (larger, yellow)
            is_heal: True for healing (green)
            is_dodge: True for dodge messages (blue)
        """
        import random
        
        # Format the text
        if is_dodge:
            text = "DODGE!"
            color = (100, 200, 255)  # Light blue
            font_size = 26
            duration = 1.2
        elif is_crit:
            text = f"CRIT! {int(damage)}"
            color = (255, 255, 0)  # Yellow for visibility
            font_size = 32
            duration = 2.0
        elif is_heal:
            text = f"+{int(damage)}"
            color = (50, 205, 50)  # Lime green
            font_size = 22
            duration = 1.5
        else:
            text = str(int(damage))
            color = (255, 255, 255)  # White for normal damage
            font_size = 24
            duration = 1.5
        
        super().__init__(text, position, color, duration, font_size)
        
        # Store if this is a critical hit for special rendering
        self.is_crit = is_crit
        self.is_dodge = is_dodge
        
        # Add slight horizontal drift for variety
        import random
        self.velocity_x = random.uniform(-20, 20)
        
        # Critical hits have bolder font
        if is_crit:
            try:
                self.font = pygame.font.Font(None, font_size)
                self.font.set_bold(True)
            except (pygame.error, AttributeError):
                self.font = pygame.font.SysFont('arial', font_size, bold=True)
            self.surface = self.font.render(self.text, True, self.color)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw damage number with outline for critical hits"""
        if not self.alive:
            return
        
        age = time.time() - self.birth_time
        
        # Calculate alpha (fade out in last 50% of lifetime)
        if age > self.duration * self.fade_start:
            progress = (age - self.duration * self.fade_start) / (self.duration * (1 - self.fade_start))
            alpha = int(255 * (1 - progress))
        else:
            alpha = 255
        
        # Screen position (adjusted for camera)
        screen_x = self.rect.centerx - camera_x
        screen_y = self.rect.centery - camera_y
        
        # Draw outline for critical hits
        if self.is_crit and alpha > 100:
            outline_color = (128, 0, 0)  # Dark red outline
            try:
                outline_font = pygame.font.Font(None, self.font.get_height())
                outline_font.set_bold(True)
            except (pygame.error, AttributeError):
                outline_font = pygame.font.SysFont('arial', self.font.get_height(), bold=True)
            
            outline_surface = outline_font.render(self.text, True, outline_color)
            outline_surface.set_alpha(alpha)
            
            # Draw outline in 4 directions
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                screen.blit(outline_surface, (screen_x - outline_surface.get_width() // 2 + dx,
                                             screen_y - outline_surface.get_height() // 2 + dy))
        
        # Draw main text
        temp_surface = self.surface.copy()
        temp_surface.set_alpha(alpha)
        screen.blit(temp_surface, (screen_x - temp_surface.get_width() // 2,
                                   screen_y - temp_surface.get_height() // 2))
    
    def update(self, dt, camera_x=0, camera_y=0):
        """Update with horizontal drift"""
        super().update(dt, camera_x, camera_y)
        
        if self.alive:
            self.x += self.velocity_x * dt
            self.rect.centerx = self.x


class CombatText(FloatingText):
    """Specialized text for combat events (Miss, Block, Resist, etc.)"""
    def __init__(self, text, position):
        """
        Create combat event text
        
        Args:
            text: Event text (e.g., "MISS!", "BLOCK!", "RESIST!")
            position: (x, y) tuple
        """
        # Color coding for different events
        color_map = {
            "MISS": (128, 128, 128),      # Gray
            "BLOCK": (100, 149, 237),      # Cornflower blue
            "RESIST": (147, 112, 219),     # Medium purple
            "IMMUNE": (255, 215, 0),       # Gold
            "DODGE": (255, 255, 255),      # White
            "PARRY": (255, 223, 0),        # Gold
        }
        
        text_upper = text.upper().strip("!")
        color = color_map.get(text_upper, (200, 200, 200))
        
        super().__init__(text, position, color, duration=1.2, font_size=18)
