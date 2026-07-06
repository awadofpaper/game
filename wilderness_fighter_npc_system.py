"""
Wilderness Fighter NPC System
Manages NPCs who live and fight in the wilderness, including patrols, camps, and combat encounters.
"""
import random
import time

class WildernessFighterNPC:
    def __init__(self, npc_id, name, level, camp_x, camp_y):
        self.npc_id = npc_id
        self.name = name
        self.level = level
        self.camp_x = camp_x
        self.camp_y = camp_y
        self.is_patrolling = True
        self.patrol_radius = random.randint(100, 400)
        self.current_x = camp_x
        self.current_y = camp_y
        self.last_combat_time = 0
        self.alive = True

    def patrol(self):
        # Move within patrol radius
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(0, self.patrol_radius)
        self.current_x = self.camp_x + int(distance * random.uniform(-1, 1))
        self.current_y = self.camp_y + int(distance * random.uniform(-1, 1))

    def encounter(self, player):
        # Simple combat logic
        if self.alive and self.is_near(player.x, player.y):
            # Engage in combat
            self.last_combat_time = time.time()
            # ...combat logic here...
            return True
        return False

    def is_near(self, x, y, threshold=80):
        dx = self.current_x - x
        dy = self.current_y - y
        return (dx*dx + dy*dy) ** 0.5 < threshold

class WildernessFighterNPCSystem:
    def __init__(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height
        self.fighters = {}  # {npc_id: WildernessFighterNPC}

    def spawn_fighter(self, npc_id, name, level):
        camp_x = random.randint(100, self.world_width - 100)
        camp_y = random.randint(100, self.world_height - 100)
        fighter = WildernessFighterNPC(npc_id, name, level, camp_x, camp_y)
        self.fighters[npc_id] = fighter
        return fighter

    def update(self):
        for fighter in self.fighters.values():
            if fighter.alive:
                fighter.patrol()
                # ...additional wilderness logic...

    def get_active_fighters(self):
        return [f for f in self.fighters.values() if f.alive]

    def draw(self, screen, camera_x, camera_y):
        """Draw all active wilderness fighters"""
        import pygame
        for fighter in self.fighters.values():
            if fighter.alive:
                # Calculate screen position
                screen_x = int(fighter.current_x - camera_x)
                screen_y = int(fighter.current_y - camera_y)
                
                # Only draw if on screen
                if -50 < screen_x < screen.get_width() + 50 and -50 < screen_y < screen.get_height() + 50:
                    # Draw fighter body (humanoid shape)
                    body_color = (100, 50, 50)  # Dark red/brown for wilderness fighter
                    
                    # Body (rectangle)
                    pygame.draw.rect(screen, body_color, (screen_x - 8, screen_y - 12, 16, 24))
                    
                    # Head (circle)
                    pygame.draw.circle(screen, (255, 200, 150), (screen_x, screen_y - 20), 8)
                    
                    # Weapon indicator (simple line)
                    weapon_color = (150, 150, 150)  # Gray weapon
                    pygame.draw.line(screen, weapon_color, 
                                   (screen_x + 8, screen_y - 8), 
                                   (screen_x + 16, screen_y - 16), 2)
                    
                    # Level indicator
                    font = pygame.font.Font(None, 16)
                    level_text = font.render(f"Lv{fighter.level}", True, (255, 255, 0))
                    screen.blit(level_text, (screen_x - 12, screen_y + 14))
                    
                    # Name (only if close to player)
                    # This check will be done by caller if needed
                    name_font = pygame.font.Font(None, 14)
                    name_text = name_font.render(fighter.name, True, (255, 255, 255))
                    name_rect = name_text.get_rect(center=(screen_x, screen_y - 32))
                    screen.blit(name_text, name_rect)
