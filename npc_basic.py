"""
Basic NPC System (Without Dialogue)
Simple NPCs that can be placed in the world for future dialogue integration
"""

import pygame
import random
import math
from equipment_renderer import EquipmentRenderer

class BasicNPC:
    """Simple NPC without dialogue - just visual representation and basic interaction"""
    def __init__(self, name: str, x: int, y: int, npc_type="villager", sprite_color=(100, 150, 200)):
        # SECURITY: Sanitize NPC name to prevent save corruption and display issues
        from utils import sanitize_name
        self.name = sanitize_name(name, max_length=32)
        self.id = self.name  # ID for dialogue system
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 32, 32)
        self.sprite_color = sprite_color
        self.npc_type = npc_type  # villager, merchant, guard, etc.
        self.interaction_radius = 80
        self.has_quest_marker = False
        
        # Movement for wandering NPCs
        self.can_wander = True
        self.wander_speed = 20
        self.wander_timer = 0
        self.wander_direction = None
        self.wander_cooldown = random.randint(60, 180)  # frames between movements
        
        # Patrol behavior for guards
        self.is_patrolling = False
        self.patrol_points = []
        self.current_patrol_index = 0
        self.patrol_speed = 30
        self.patrol_wait_time = 0
        self.patrol_wait_duration = 120  # frames to wait at each point
        self.facing = 'right'  # Direction NPC is facing (for vision cones)
        
        # Equipment system - NPCs can wear gear!
        self.equipment = {
            "head": None,
            "chest": None,
            "legs": None,
            "feet": None,
            "main_hand": None,
            "off_hand": None
        }
        
        # AI State System
        self.state = "idle"  # Current AI state: idle, wander, patrol, chase, flee, interact
        self.previous_state = "idle"
        self.state_timer = 0  # Time spent in current state
        self.state_change_cooldown = 60  # Minimum frames between state changes
        
        # Chase/Flee behavior
        self.chase_target = None  # Entity being chased
        self.flee_target = None  # Entity being fled from
        self.chase_speed = 40  # Speed when chasing
        self.flee_speed = 50  # Speed when fleeing
        self.chase_radius = 200  # How close to get before stopping chase
        self.detection_radius = 150  # How far NPC can detect entities
        self.alert_timer = 0  # Time remaining in alert state
        
        # Dialogue system
        self.dialogue = self._get_default_dialogue(npc_type)
        self.dialogue_state = "greeting"  # Current dialogue state
        self.conversation_count = 0  # Track how many times player talked to this NPC
        
        # Performance: Pre-render name tag (avoid creating fonts every frame)
        self._name_surface = None
        self._name_bg = None
        self._quest_marker_text = None
        self._render_name_tag()
        
        # Set initial AI state based on NPC settings (do this LAST after all attributes set)
        self._initialize_state()
        
    def _render_name_tag(self):
        """Pre-render name tag surfaces (called once in __init__)"""
        font = pygame.font.SysFont(None, 18)
        self._name_surface = font.render(self.name, True, (255, 255, 255))
        self._name_bg = pygame.Surface((self._name_surface.get_width() + 4, self._name_surface.get_height() + 2))
        self._name_bg.set_alpha(180)
        self._name_bg.fill((0, 0, 0))
        
        # Pre-render quest marker exclamation mark
        marker_font = pygame.font.SysFont(None, 16)
        self._quest_marker_text = marker_font.render("!", True, (0, 0, 0))
    
    def _initialize_state(self):
        """Initialize AI state based on NPC settings (called at end of __init__)"""
        if self.is_patrolling:
            self.state = "patrol"
        elif self.can_wander:
            self.state = "wander"
        else:
            self.state = "idle"
    
    def _get_default_dialogue(self, npc_type):
        """Get default dialogue lines based on NPC type"""
        dialogues = {
            "villager": {
                "greeting": [
                    "Hello there, traveler!",
                    "Good day to you!",
                    "Welcome to our village!",
                    "Nice weather we're having."
                ],
                "repeat": [
                    "Back again?",
                    "What can I help you with?",
                    "Still around, I see.",
                    "Need something?"
                ],
                "farewell": [
                    "Safe travels!",
                    "Come back soon!",
                    "Take care out there.",
                    "May your journey be safe."
                ]
            },
            "merchant": {
                "greeting": [
                    "Welcome! Looking to buy or sell?",
                    "Greetings! I have many fine wares.",
                    "Hello! Take a look at my goods!",
                    "Good to see you! I have special deals today."
                ],
                "repeat": [
                    "Changed your mind about that purchase?",
                    "See anything you like?",
                    "I can make you a good deal.",
                    "My prices are the best around!"
                ],
                "farewell": [
                    "Come back when you have more coin!",
                    "Thanks for your business!",
                    "May your pockets always be full!",
                    "Safe travels, and come back soon!"
                ]
            },
            "guard": {
                "greeting": [
                    "Halt! State your business.",
                    "Keep the peace, citizen.",
                    "Move along, nothing to see here.",
                    "Stay out of trouble."
                ],
                "repeat": [
                    "You again? What is it this time?",
                    "Still here? Keep moving.",
                    "I'm watching you.",
                    "No trouble from you, I hope."
                ],
                "farewell": [
                    "Stay vigilant.",
                    "Keep your wits about you.",
                    "Don't cause any problems.",
                    "Move along now."
                ]
            },
            "elder": {
                "greeting": [
                    "Ah, a new face. Welcome, young one.",
                    "Greetings, traveler. I am the village elder.",
                    "Welcome. I have lived through many ages.",
                    "Hello there. What brings you to our humble village?"
                ],
                "repeat": [
                    "Seeking more wisdom?",
                    "You return with questions, I see.",
                    "The path ahead is not always clear.",
                    "Patience, young one. All in good time."
                ],
                "farewell": [
                    "May wisdom guide your path.",
                    "Go forth with courage.",
                    "The world needs heroes like you.",
                    "Return when you seek guidance."
                ]
            },
            "blacksmith": {
                "greeting": [
                    "Hail! Need something forged?",
                    "Welcome to my smithy!",
                    "Looking for quality weapons and armor?",
                    "I can craft whatever you need!"
                ],
                "repeat": [
                    "Need something repaired?",
                    "My forge is always burning.",
                    "Bring me materials and I'll craft you something.",
                    "Quality work takes time!"
                ],
                "farewell": [
                    "May your blade stay sharp!",
                    "Good steel makes good warriors!",
                    "Come back if you need repairs!",
                    "Stay strong, adventurer!"
                ]
            },
            "miner": {
                "greeting": [
                    "Aye! Fellow miner, are ye?",
                    "Greetings from the mines!",
                    "Looking to strike it rich?",
                    "The rocks hold many secrets!"
                ],
                "repeat": [
                    "Found any good ore?",
                    "The deeper you dig, the better the treasure!",
                    "Watch out for cave-ins!",
                    "Mining is honest work."
                ],
                "farewell": [
                    "Happy mining!",
                    "May you strike gold!",
                    "Keep your pickaxe sharp!",
                    "See you in the mines!"
                ]
            },
            "fisher": {
                "greeting": [
                    "Good fishing weather today!",
                    "Ahoy! Cast your line, friend!",
                    "The fish are biting today!",
                    "Welcome to the best fishing spot!"
                ],
                "repeat": [
                    "Catch anything good?",
                    "Patience is key to fishing.",
                    "The big one is still out there!",
                    "Try using different bait!"
                ],
                "farewell": [
                    "Tight lines!",
                    "May your catch be plentiful!",
                    "Good luck out there!",
                    "The fish will wait for you!"
                ]
            }
        }
        
        # Return dialogue for this type, or default to villager
        return dialogues.get(npc_type, dialogues["villager"])
    
    def get_dialogue(self, player=None):
        """
        Get current dialogue line based on conversation state
        
        Args:
            player: Optional player object for context-aware dialogue
            
        Returns:
            str: Dialogue line to display
        """
        # Determine which dialogue set to use
        if self.conversation_count == 0:
            dialogue_set = self.dialogue.get("greeting", ["Hello."])
        elif "farewell" in self.dialogue_state:
            dialogue_set = self.dialogue.get("farewell", ["Goodbye."])
        else:
            dialogue_set = self.dialogue.get("repeat", ["..."])
        
        # Pick a random line from the set
        if dialogue_set:
            return random.choice(dialogue_set)
        return "..."
    
    def talk(self, player=None):
        """
        Main dialogue interaction method - call this when player talks to NPC
        
        Args:
            player: Optional player object for context
            
        Returns:
            str: Dialogue response
        """
        self.conversation_count += 1
        
        # Reset dialogue state if it's set to farewell
        if "farewell" in self.dialogue_state:
            self.dialogue_state = "repeat"
        
        # Get and return dialogue
        response = self.get_dialogue(player)
        
        # After a few conversations, set state to farewell
        if self.conversation_count % 3 == 0:
            self.dialogue_state = "farewell"
        else:
            self.dialogue_state = "repeat"
        
        return response
    
    def set_custom_dialogue(self, dialogue_dict):
        """
        Set custom dialogue for this NPC
        
        Args:
            dialogue_dict: Dictionary with keys 'greeting', 'repeat', 'farewell'
                          Each value should be a list of dialogue strings
        """
        self.dialogue = dialogue_dict
    
    def reset_conversation(self):
        """Reset conversation state (e.g., after player leaves and comes back)"""
        self.dialogue_state = "greeting"
        self.conversation_count = 0
    
    def set_patrol_points(self, points):
        """Set patrol points for this NPC (list of (x, y) tuples)"""
        self.patrol_points = points
        self.is_patrolling = True
        self.can_wander = False
        self.change_state("patrol")
    
    def change_state(self, new_state):
        """Change AI state with validation and transition logic"""
        if new_state == self.state:
            return  # Already in this state
        
        # Store previous state
        self.previous_state = self.state
        self.state = new_state
        self.state_timer = 0
        
        # State-specific initialization
        if new_state == "idle":
            self.wander_direction = None
        elif new_state == "wander":
            if self.can_wander:
                self.wander_timer = 0
        elif new_state == "chase":
            self.alert_timer = 300  # 5 seconds at 60 FPS
        elif new_state == "flee":
            self.alert_timer = 180  # 3 seconds at 60 FPS
    
    def get_state(self):
        """Get current AI state"""
        return self.state
    
    def is_idle(self):
        """Check if NPC is idle"""
        return self.state == "idle"
    
    def is_moving(self):
        """Check if NPC is in a moving state"""
        return self.state in ["wander", "patrol", "chase", "flee"]
        
    def can_interact(self, player_x: int, player_y: int):
        """Check if player is close enough to interact"""
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        return distance <= self.interaction_radius
    
    def update(self, dt=1/60, world=None, player=None):
        """Update NPC state (AI, movement, animations, etc.)"""
        # DEBUG: Log once every 60 frames for patrol guards
        if self.is_patrolling and self.state_timer % 60 == 0:
            print(f"[DEBUG NPC] {self.name}: state={self.state}, is_patrolling={self.is_patrolling}, patrol_points={len(self.patrol_points) if self.patrol_points else 0}")
        
        # Increment state timer
        self.state_timer += 1
        
        # Decrement alert timer
        if self.alert_timer > 0:
            self.alert_timer -= 1
        
        # Handle state-based behavior
        if self.state == "idle":
            self._update_idle(dt, player)
        elif self.state == "wander":
            self._update_wander(dt, world)
        elif self.state == "patrol":
            self._update_patrol(dt)
        elif self.state == "chase":
            self._update_chase(dt, player)
        elif self.state == "flee":
            self._update_flee(dt, player)
        elif self.state == "interact":
            self._update_interact(dt)
        
        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _update_idle(self, dt, player=None):
        """Update idle state - standing still, may transition to wander"""
        # After some time idle, consider wandering
        if self.can_wander and self.state_timer > self.state_change_cooldown:
            if random.random() < 0.02:  # 2% chance per frame
                self.change_state("wander")
    
    def _update_wander(self, dt, world=None):
        """Update wandering state - moving randomly"""
        self.wander_timer += 1
        
        if self.wander_timer >= self.wander_cooldown:
            # Choose random direction
            directions = ['up', 'down', 'left', 'right', 'idle']
            self.wander_direction = random.choice(directions)
            self.wander_cooldown = random.randint(60, 180)
            self.wander_timer = 0
            
            # Sometimes return to idle
            if self.wander_direction == 'idle':
                self.change_state("idle")
                return
        
        # Move in current direction
        if self.wander_direction == 'up':
            self.y -= self.wander_speed * dt
        elif self.wander_direction == 'down':
            self.y += self.wander_speed * dt
        elif self.wander_direction == 'left':
            self.x -= self.wander_speed * dt
        elif self.wander_direction == 'right':
            self.x += self.wander_speed * dt
    
    def _update_patrol(self, dt):
        """Update patrol state - following patrol route"""
        if not self.is_patrolling or not self.patrol_points:
            print(f"[DEBUG] {self.name}: Patrol failed - is_patrolling={self.is_patrolling}, points={len(self.patrol_points) if self.patrol_points else 0}")
            self.change_state("idle")
            return
        # Get current target patrol point
        if self.patrol_wait_time > 0:
            self.patrol_wait_time -= 1
            # Log once every 60 frames when waiting
            if self.patrol_wait_time % 60 == 0:
                print(f"[DEBUG] {self.name}: Waiting at patrol point {self.current_patrol_index}, wait time remaining: {self.patrol_wait_time}")
            return
            
        target_x, target_y = self.patrol_points[self.current_patrol_index]
        
        # Calculate distance to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If close to target, move to next patrol point
        if distance < 10:
            print(f"[DEBUG] {self.name}: Reached patrol point {self.current_patrol_index} at ({int(self.x)}, {int(self.y)}), moving to next")
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            self.patrol_wait_time = self.patrol_wait_duration
        else:
            # Move towards target
            if distance > 0:
                move_x = (dx / distance) * self.patrol_speed * dt
                move_y = (dy / distance) * self.patrol_speed * dt
                old_x, old_y = self.x, self.y
                self.x += move_x
                self.y += move_y
                # Log movement every 30 frames to reduce spam
                if self.state_timer % 30 == 0:
                    print(f"[DEBUG] {self.name}: Moving from ({old_x:.1f}, {old_y:.1f}) to ({self.x:.1f}, {self.y:.1f}), target=({target_x}, {target_y}), dist={distance:.1f}, dt={dt:.4f}")
                
                # Update facing direction based on movement for vision cones
                if not hasattr(self, 'facing'):
                    self.facing = 'right'
                
                # Determine primary movement direction
                if abs(dx) > abs(dy):
                    # Moving more horizontally
                    self.facing = 'right' if dx > 0 else 'left'
                else:
                    # Moving more vertically
                    self.facing = 'down' if dy > 0 else 'up'
    
    def _update_chase(self, dt, player=None):
        """Update chase state - pursuing a target"""
        if not self.chase_target and not player:
            self.change_state("idle")
            return
        
        # Use player if no specific chase target
        target = self.chase_target if self.chase_target else player
        
        # Calculate distance to target
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If target too far, give up chase
        if distance > self.detection_radius * 2:
            self.chase_target = None
            self.change_state("idle")
            return
        
        # If close enough, stop chasing
        if distance < 30:
            self.change_state("interact")
            return
        
        # Move towards target
        if distance > 0:
            move_x = (dx / distance) * self.chase_speed * dt
            move_y = (dy / distance) * self.chase_speed * dt
            self.x += move_x
            self.y += move_y
    
    def _update_flee(self, dt, player=None):
        """Update flee state - running away from a target"""
        if not self.flee_target and not player:
            self.change_state("idle")
            return
        
        # Use player if no specific flee target
        target = self.flee_target if self.flee_target else player
        
        # Calculate distance to target
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If far enough away, stop fleeing
        if distance > self.detection_radius * 1.5:
            self.flee_target = None
            self.change_state("idle")
            return
        
        # Move away from target
        if distance > 0:
            move_x = -(dx / distance) * self.flee_speed * dt
            move_y = -(dy / distance) * self.flee_speed * dt
            self.x += move_x
            self.y += move_y
    
    def _update_interact(self, dt):
        """Update interact state - NPC reached target and is interacting"""
        # After a short time, return to previous behavior
        if self.state_timer > 120:  # 2 seconds
            if self.is_patrolling:
                self.change_state("patrol")
            elif self.can_wander:
                self.change_state("wander")
            else:
                self.change_state("idle")
    
    def equip(self, slot, item_id):
        """Equip an item to a specific slot"""
        if slot in self.equipment:
            self.equipment[slot] = item_id
    
    def unequip(self, slot):
        """Remove equipped item from a slot"""
        if slot in self.equipment:
            self.equipment[slot] = None
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the NPC on screen with equipment"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw NPC body (ellipse for character)
        pygame.draw.ellipse(screen, self.sprite_color, (screen_x, screen_y, 32, 32))
        pygame.draw.ellipse(screen, (255, 255, 255), (screen_x, screen_y, 32, 32), 2)
        
        # Draw simple face
        pygame.draw.circle(screen, (0, 0, 0), (screen_x + 10, screen_y + 12), 2)  # Left eye
        pygame.draw.circle(screen, (0, 0, 0), (screen_x + 22, screen_y + 12), 2)  # Right eye
        pygame.draw.arc(screen, (0, 0, 0), (screen_x + 8, screen_y + 18, 16, 8), 0, 3.14, 2)  # Smile
        
        # Draw equipment on NPC using shared renderer
        center_pos = (screen_x + 16, screen_y + 16)  # Center of the ellipse
        EquipmentRenderer.draw_equipment(screen, self, center_pos, entity_type="npc", 
                                        equipped_items=self.equipment)
        
        # Draw quest marker if available
        if self.has_quest_marker:
            marker_y = screen_y - 10
            pygame.draw.circle(screen, (255, 215, 0), (screen_x + 16, marker_y), 6)
            pygame.draw.circle(screen, (255, 255, 255), (screen_x + 16, marker_y), 6, 2)
            # Pre-rendered exclamation mark
            if self._quest_marker_text:
                screen.blit(self._quest_marker_text, (screen_x + 13, marker_y - 6))
        
        # Draw pre-rendered name tag (performance optimization)
        if self._name_surface and self._name_bg:
            name_x = screen_x + 16 - self._name_surface.get_width()//2
            screen.blit(self._name_bg, (name_x, screen_y + 35))
            screen.blit(self._name_surface, (name_x + 2, screen_y + 36))


class NPCManager:
    """Manages all NPCs in the game world"""
    def __init__(self):
        self.npcs = []
        self.interaction_messages = {}  # Store simple messages for each NPC
        self.population = 0
        
    def add_npc(self, npc: BasicNPC, interaction_message="Hello!"):
        """Add an NPC to the world"""
        self.npcs.append(npc)
        self.interaction_messages[npc.name] = interaction_message
        self.population += 1
        
    def remove_npc(self, npc_name: str):
        """Remove an NPC by name"""
        before = len(self.npcs)
        self.npcs = [npc for npc in self.npcs if npc.name != npc_name]
        after = len(self.npcs)
        if npc_name in self.interaction_messages:
            del self.interaction_messages[npc_name]
        # Only decrement if an NPC was actually removed
        if after < before:
            self.population = max(0, self.population - (before - after))

    def get_population(self):
        """Return current global population (NPCs only)"""
        return self.population
    
    def get_npc_at(self, x: int, y: int, radius: int = 40):
        """Get NPC near a position"""
        for npc in self.npcs:
            distance = ((npc.x - x) ** 2 + (npc.y - y) ** 2) ** 0.5
            if distance <= radius:
                return npc
        return None
    
    def get_interactable_npc(self, player_x: int, player_y: int):
        """Get NPC that player can interact with"""
        for npc in self.npcs:
            if npc.can_interact(player_x, player_y):
                return npc
        return None
    
    def update(self, dt, world=None):
        """Update all NPCs"""
        for npc in self.npcs:
            npc.update(dt, world)
    
    def draw(self, screen, camera_x, camera_y, current_town=None):
        """Draw all NPCs. If current_town is specified, only draw NPCs in that town."""
        for npc in self.npcs:
            # Skip NPCs not in the current town if town filtering is enabled
            if current_town and hasattr(npc, 'current_town'):
                if npc.current_town != current_town:
                    continue
            npc.draw(screen, camera_x, camera_y)
    
    def show_interaction_prompt(self, screen, npc: BasicNPC):
        """Show a simple prompt when player can interact"""
        font = pygame.font.SysFont(None, 24)
        message = self.interaction_messages.get(npc.name, "Press E to interact")
        text = font.render(message, True, (255, 255, 255))
        
        # Draw at top center of screen
        screen_width = screen.get_width()
        text_bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
        text_bg.set_alpha(200)
        text_bg.fill((0, 0, 0))
        
        bg_x = screen_width // 2 - text_bg.get_width() // 2
        bg_y = 50
        
        screen.blit(text_bg, (bg_x, bg_y))
        screen.blit(text, (bg_x + 10, bg_y + 5))


def create_starter_npcs():
    """Create some basic NPCs for the game world"""
    npcs = []
    
    # Village Elder - purple robes
    elder = BasicNPC("Elder Sage", 400, 300, "elder", sprite_color=(120, 80, 150))
    elder.can_wander = False  # Elders don't wander
    elder.has_quest_marker = True
    npcs.append(elder)
    
    # Merchant - gold/yellow
    merchant = BasicNPC("Trader Tom", 600, 400, "merchant", sprite_color=(200, 180, 50))
    merchant.can_wander = False
    npcs.append(merchant)
    
    # Wandering villagers
    villager1 = BasicNPC("Mary", 450, 500, "villager", sprite_color=(80, 120, 180))
    npcs.append(villager1)
    
    villager2 = BasicNPC("John", 550, 350, "villager", sprite_color=(100, 150, 100))
    npcs.append(villager2)
    
    return npcs


def create_town_guards(town_system):
    """Create guard NPCs for each town"""
    guards = []
    
    for town in town_system.towns:
        town_x = town.center_x
        town_y = town.center_y
        town_name = town.name
        
        # Find town hall building
        town_hall = None
        for building in town.buildings:
            # building.type is a BuildingType enum, compare with enum member
            from town_system import BuildingType
            if building.type == BuildingType.TOWN_HALL:
                town_hall = building
                break
        
        if town_hall:
            # Stationary guard outside town hall
            guard_x = town_hall.door_x + 80  # Position to the right of town hall
            guard_y = town_hall.door_y
            stationary_guard = BasicNPC(
                f"{town_name} Guard", 
                guard_x, 
                guard_y, 
                "guard", 
                sprite_color=(150, 50, 50)
            )
            stationary_guard.can_wander = False
            stationary_guard.current_town = town_name  # Track which town this guard belongs to
            guards.append(stationary_guard)
            
            # Patrolling guard - create patrol route around town
            patrol_guard = BasicNPC(
                f"{town_name} Patrol", 
                town_x, 
                town_y, 
                "guard", 
                sprite_color=(180, 60, 60)
            )
            
            # Create circular patrol route around town center
            import math
            patrol_points = []
            num_points = 6
            patrol_radius = 150
            for i in range(num_points):
                angle = (2 * math.pi * i) / num_points
                px = town_x + int(patrol_radius * math.cos(angle))
                py = town_y + int(patrol_radius * math.sin(angle))
                patrol_points.append((px, py))
            
            patrol_guard.set_patrol_points(patrol_points)
            patrol_guard.current_town = town_name  # Track which town this guard belongs to
            guards.append(patrol_guard)
    
    return guards

