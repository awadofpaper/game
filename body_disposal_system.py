"""
Body Disposal and Grave System
Handles corpses, body pickup, burial, and grave markers
"""

import pygame
import time


class Corpse:
    """Represents a dead body on the ground"""
    
    def __init__(self, npc_id, name, x, y, death_time, cause_of_death="Unknown", 
                 age=0, birth_date="Unknown", inventory=None, equipment=None):
        """
        Initialize a corpse
        
        Args:
            npc_id: Unique identifier for the NPC
            name: Name of the deceased
            x, y: World position
            death_time: Game time when death occurred (in days)
            cause_of_death: How they died
            age: Age at death
            birth_date: Date of birth
            inventory: Items the NPC had
            equipment: Equipment the NPC wore
        """
        self.npc_id = npc_id
        self.name = name
        self.x = x
        self.y = y
        self.death_time = death_time
        self.cause_of_death = cause_of_death
        self.age = age
        self.birth_date = birth_date
        self.death_date = self.format_game_time(death_time)
        self.inventory = inventory or {}
        self.equipment = equipment or {}
        
        # Visual properties
        self.rect = pygame.Rect(int(x) - 16, int(y) - 16, 32, 32)
        self.color = (139, 69, 19)  # Brown/dead color
        
        # State tracking
        self.discovered = False
        self.reported = False
        self.buried = False
        self.picked_up = False
    
    def format_game_time(self, day_count):
        """Format game time as a readable date"""
        # Assuming 1 year = 365 days, 1 month = 30 days
        years = day_count // 365
        remaining_days = day_count % 365
        months = remaining_days // 30
        days = remaining_days % 30
        return f"Year {years}, Month {months}, Day {days}"
    
    def can_be_discovered(self):
        """Check if body can still be discovered (visible for 4 days)"""
        return not self.picked_up and not self.buried
    
    def is_near(self, x, y, radius=50):
        """Check if position is near the corpse"""
        dx = x - self.x
        dy = y - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= radius
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the corpse on screen"""
        if self.picked_up or self.buried:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw body (X shape)
        pygame.draw.line(screen, self.color, 
                        (screen_x - 12, screen_y - 12), 
                        (screen_x + 12, screen_y + 12), 3)
        pygame.draw.line(screen, self.color, 
                        (screen_x + 12, screen_y - 12), 
                        (screen_x - 12, screen_y + 12), 3)
        
        # Draw circle for head
        pygame.draw.circle(screen, self.color, (screen_x, screen_y - 20), 8)
        
        # Draw name label
        font = pygame.font.SysFont(None, 16)
        name_surface = font.render(f"{self.name}'s body", True, (255, 0, 0))
        screen.blit(name_surface, (screen_x - name_surface.get_width() // 2, screen_y + 20))


class Grave:
    """Represents a grave marker"""
    
    def __init__(self, corpse, burial_time, x, y):
        """
        Initialize a grave
        
        Args:
            corpse: Corpse object with NPC information
            burial_time: Game time when buried (in days)
            x, y: World position of grave
        """
        self.npc_id = corpse.npc_id
        self.name = corpse.name
        self.x = x
        self.y = y
        self.burial_time = burial_time
        self.age = corpse.age
        self.birth_date = corpse.birth_date
        self.death_date = corpse.death_date
        self.cause_of_death = corpse.cause_of_death
        
        # Visual properties
        self.rect = pygame.Rect(int(x) - 16, int(y) - 16, 32, 48)
        self.color = (105, 105, 105)  # Gray stone
        self.flower_color = (255, 182, 193)  # Pink flowers
        
        # Grave only appears 1 month after burial
        self.visible = False
        self.appear_time = burial_time + 30  # 1 month = 30 days
    
    def update_visibility(self, current_time):
        """Check if grave should be visible (1 month after burial)"""
        if not self.visible and current_time >= self.appear_time:
            self.visible = True
    
    def is_near(self, x, y, radius=50):
        """Check if position is near the grave"""
        if not self.visible:
            return False
        dx = x - self.x
        dy = y - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= radius
    
    def get_epitaph(self):
        """Get the text displayed on the gravestone"""
        lines = [
            f"Here lies {self.name}",
            f"Age: {self.age}",
            f"Born: {self.birth_date}",
            f"Died: {self.death_date}",
            f"Cause: {self.cause_of_death}"
        ]
        return lines
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the grave marker"""
        if not self.visible:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw gravestone (rounded rectangle)
        stone_rect = pygame.Rect(screen_x - 12, screen_y - 20, 24, 40)
        pygame.draw.rect(screen, self.color, stone_rect, border_radius=5)
        pygame.draw.rect(screen, (80, 80, 80), stone_rect, 2, border_radius=5)
        
        # Draw cross on stone
        pygame.draw.line(screen, (200, 200, 200), 
                        (screen_x, screen_y - 15), 
                        (screen_x, screen_y + 5), 2)
        pygame.draw.line(screen, (200, 200, 200), 
                        (screen_x - 6, screen_y - 8), 
                        (screen_x + 6, screen_y - 8), 2)
        
        # Draw flowers
        for i in range(3):
            flower_x = screen_x - 8 + i * 8
            flower_y = screen_y + 22
            pygame.draw.circle(screen, self.flower_color, (flower_x, flower_y), 3)
            # Stem
            pygame.draw.line(screen, (34, 139, 34), 
                           (flower_x, flower_y), 
                           (flower_x, flower_y + 5), 1)


class BodyDisposalSystem:
    """Manages corpses, burial, and graves"""
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.corpses = []  # List of Corpse objects
        self.graves = []  # List of Grave objects
        self.body_in_inventory = None  # Currently carried body (Corpse object)
    
    def create_corpse(self, npc_id, name, x, y, cause_of_death="Unknown", 
                     age=0, birth_date="Unknown", inventory=None, equipment=None):
        """
        Create a corpse when an NPC dies
        
        Args:
            npc_id: Unique identifier for the NPC
            name: Name of the deceased
            x, y: World position
            cause_of_death: How they died
            age: Age at death
            birth_date: Date of birth
            inventory: Items the NPC had
            equipment: Equipment the NPC wore
            
        Returns:
            Corpse: The created corpse object
        """
        current_time = self.game_time.day_count if self.game_time else 0
        corpse = Corpse(npc_id, name, x, y, current_time, cause_of_death, 
                       age, birth_date, inventory, equipment)
        self.corpses.append(corpse)
        return corpse
    
    def can_pickup_body(self, player, corpse):
        """
        Check if player can pick up a body
        
        Args:
            player: Player object
            corpse: Corpse to pick up
            
        Returns:
            tuple: (can_pickup: bool, reason: str)
        """
        if self.body_in_inventory is not None:
            return False, "Already carrying a body"
        
        if corpse.picked_up:
            return False, "Body already picked up"
        
        if corpse.buried:
            return False, "Body already buried"
        
        if not corpse.is_near(player.x, player.y):
            return False, "Too far away"
        
        return True, "Can pick up body"
    
    def pickup_body(self, player, corpse):
        """
        Player picks up a body (goes into inventory with 0 weight)
        
        Args:
            player: Player object
            corpse: Corpse to pick up
            
        Returns:
            tuple: (success: bool, message: str)
        """
        can_pickup, reason = self.can_pickup_body(player, corpse)
        if not can_pickup:
            return False, reason
        
        # Mark corpse as picked up
        corpse.picked_up = True
        self.body_in_inventory = corpse
        
        # Add items from corpse to special inventory flag
        # (items have weight, but body itself has 0 weight)
        
        return True, f"Picked up {corpse.name}'s body"
    
    def can_bury_body(self, player, x, y):
        """
        Check if player can bury the body they're carrying
        
        Args:
            player: Player object
            x, y: Position to bury
            
        Returns:
            tuple: (can_bury: bool, reason: str)
        """
        if self.body_in_inventory is None:
            return False, "Not carrying a body"
        
        # Check if player has shovel
        if not hasattr(player, 'inventory'):
            return False, "No inventory"
        
        if player.inventory.get('shovel', 0) <= 0:
            return False, "Need a shovel to bury body"
        
        # Check if outside town (simplified - just check not too close to origin)
        # In full implementation, check against town boundaries
        town_distance = ((x * x) + (y * y)) ** 0.5
        if town_distance < 300:  # Arbitrary town radius
            return False, "Must bury outside of town"
        
        return True, "Can bury body"
    
    def bury_body(self, player, x, y):
        """
        Bury the body player is carrying (instant, no animation)
        
        Args:
            player: Player object
            x, y: Position to bury
            
        Returns:
            tuple: (success: bool, message: str)
        """
        can_bury, reason = self.can_bury_body(player, x, y)
        if not can_bury:
            return False, reason
        
        corpse = self.body_in_inventory
        current_time = self.game_time.day_count if self.game_time else 0
        
        # Create grave
        grave = Grave(corpse, current_time, x, y)
        self.graves.append(grave)
        
        # Mark corpse as buried
        corpse.buried = True
        self.body_in_inventory = None
        
        return True, f"Buried {corpse.name}"
    
    def update(self):
        """Update system each frame"""
        current_time = self.game_time.day_count if self.game_time else 0
        
        # Update grave visibility (appear after 1 month)
        for grave in self.graves:
            grave.update_visibility(current_time)
        
        # Remove corpses that are too old (4 days visible, then auto-despawn if not picked up)
        # But only if not picked up and not buried
        self.corpses = [c for c in self.corpses 
                       if c.picked_up or c.buried or (current_time - c.death_time) <= 4]
    
    def get_nearby_corpse(self, x, y, radius=50):
        """Get corpse near position"""
        for corpse in self.corpses:
            if corpse.can_be_discovered() and corpse.is_near(x, y, radius):
                return corpse
        return None
    
    def get_nearby_grave(self, x, y, radius=50):
        """Get grave near position"""
        for grave in self.graves:
            if grave.is_near(x, y, radius):
                return grave
        return None
    
    def draw_corpses(self, screen, camera_x, camera_y):
        """Draw all visible corpses"""
        for corpse in self.corpses:
            corpse.draw(screen, camera_x, camera_y)
    
    def draw_graves(self, screen, camera_x, camera_y):
        """Draw all visible graves"""
        for grave in self.graves:
            grave.draw(screen, camera_x, camera_y)
