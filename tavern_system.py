"""
Tavern System
Provides rest, rumors, drinks, and social interactions
"""

import pygame
import random
import logging
from building_expansions import TavernFoodTrading

logger = logging.getLogger(__name__)


class Rumor:
    """A rumor that can be heard in the tavern"""
    def __init__(self, text, rumor_type="general", value=0):
        self.text = text
        self.rumor_type = rumor_type  # general, quest_hint, location, lore, warning
        self.value = value  # How valuable the rumor is


class TavernService:
    """Individual service offered at a tavern"""
    def __init__(self, name, description, cost, effect_type="rest", effect_value=0):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect_type = effect_type  # rest, drink, food, room
        self.effect_value = effect_value


class Tavern:
    """Represents a tavern with services and rumors"""
    def __init__(self, building, town_name):
        self.building = building
        self.town_name = town_name
        self.name = building.name
        
        # Define available services
        self.services = [
            TavernService(
                "Trade Food",
                "Buy and sell food items and ingredients",
                cost=0,
                effect_type="food_trade",
                effect_value=0
            ),
            TavernService(
                "Order a Drink",
                "Ale or wine to quench your thirst",
                cost=3,
                effect_type="drink",
                effect_value=10  # HP restoration
            ),
            TavernService(
                "Order a Meal",
                "Hearty food to restore energy",
                cost=8,
                effect_type="food",
                effect_value=30  # HP restoration
            ),
            TavernService(
                "Rest at the Bar",
                "Take a short break (2h)",
                cost=5,
                effect_type="rest_short",
                effect_value=2  # Hours
            ),
            TavernService(
                "Rent a Room",
                "Sleep in a bed for the night (8h)",
                cost=15,
                effect_type="rest_long",
                effect_value=8  # Hours
            ),
            TavernService(
                "Listen to Rumors",
                "Gather information from patrons",
                cost=10,
                effect_type="rumor",
                effect_value=0
            ),
        ]
        
        # Food trading system
        self.food_trading = TavernFoodTrading()
        
        # Generate rumors for this tavern
        self.rumors = self._generate_rumors()
        self.rumors_heard = set()  # Track which rumors player has heard
    
    def _generate_rumors(self):
        """Generate a pool of rumors for this tavern"""
        rumor_pool = [
            # General rumors
            Rumor("A traveler mentioned strange lights in the forest at night...", "general", 1),
            Rumor("The merchant's prices seem higher than usual lately.", "general", 1),
            Rumor("Someone said they saw a rare herb growing near the old ruins.", "location", 2),
            Rumor("The guards have been on high alert recently.", "warning", 2),
            Rumor("There's talk of bandits on the roads to the east.", "warning", 2),
            
            # Quest hints
            Rumor("The Elder is looking for someone brave to help with a problem.", "quest_hint", 3),
            Rumor("A lost artifact was supposedly hidden in the caves years ago.", "quest_hint", 3),
            Rumor("The blacksmith mentioned needing rare ore from the mountains.", "quest_hint", 2),
            
            # Location rumors
            Rumor(f"There's a hidden treasure chest near the old oak tree.", "location", 3),
            Rumor("Dangerous creatures have been spotted near the northern caves.", "location", 2),
            Rumor(f"A dungeon entrance was discovered to the west of {self.town_name}.", "location", 3),
            
            # Lore
            Rumor("They say the founders of this town were great heroes.", "lore", 1),
            Rumor("Legend speaks of a powerful weapon sealed away long ago.", "lore", 2),
            Rumor("The old temple was built to honor the ancient gods.", "lore", 1),
            
            # Warnings
            Rumor("Don't go out at night - monsters are more aggressive then.", "warning", 2),
            Rumor("Always check your equipment durability before long journeys.", "warning", 1),
            Rumor("The woods to the south are said to be cursed.", "warning", 2),
            
            # Trade tips
            Rumor("The merchant in the next town offers better prices for weapons.", "general", 2),
            Rumor("Inns are cheaper than tavern rooms, but taverns have better food.", "general", 1),
            Rumor("You can sell damaged equipment to merchants, though at reduced prices.", "general", 1),
        ]
        
        # Select 8-12 random rumors for this tavern
        num_rumors = random.randint(8, 12)
        return random.sample(rumor_pool, min(num_rumors, len(rumor_pool)))
    
    def get_random_rumor(self):
        """Get a random rumor that hasn't been heard yet (or repeat if all heard)"""
        unheard = [r for r in self.rumors if r not in self.rumors_heard]
        
        if unheard:
            rumor = random.choice(unheard)
            self.rumors_heard.add(rumor)
            return rumor
        else:
            # All rumors heard, give a generic one
            generic = [
                "Nothing interesting to report right now.",
                "Just the usual gossip around here.",
                "Things have been quiet lately.",
                "The same old stories you've heard before."
            ]
            return Rumor(random.choice(generic), "general", 0)
    
    def use_service(self, player, service_index, game_time):
        """Use a tavern service"""
        if not (0 <= service_index < len(self.services)):
            return False, "Invalid service"
        
        service = self.services[service_index]
        
        # Check if player can afford
        if player.dubloons < service.cost:
            return False, f"Not enough dubloons! Need {service.cost}db"
        
        # Deduct cost
        player.dubloons -= service.cost
        
        result_message = ""
        
        # Apply service effects
        if service.effect_type == "drink":
            heal_amount = service.effect_value
            player.hp = min(player.max_hp, player.hp + heal_amount)
            result_message = f"Refreshing! Restored {heal_amount} HP"
            logger.info(f"[TAVERN] Player ordered drink at {self.name}")
        
        elif service.effect_type == "food":
            heal_amount = service.effect_value
            player.hp = min(player.max_hp, player.hp + heal_amount)
            result_message = f"Delicious! Restored {heal_amount} HP"
            logger.info(f"[TAVERN] Player ordered meal at {self.name}")
        
        elif service.effect_type == "rest_short":
            heal_amount = int(player.max_hp * 0.3)
            player.hp = min(player.max_hp, player.hp + heal_amount)
            if game_time:
                game_time.advance_time(service.effect_value * 60)
            result_message = f"Rested for {service.effect_value}h, restored {heal_amount} HP"
            logger.info(f"[TAVERN] Player rested at {self.name}")
        
        elif service.effect_type == "rest_long":
            heal_amount = int(player.max_hp * 0.8)
            player.hp = min(player.max_hp, player.hp + heal_amount)
            mana_amount = int(player.max_mana * 0.8)
            player.mana = min(player.max_mana, player.mana + mana_amount)
            if game_time:
                game_time.advance_time(service.effect_value * 60)
            result_message = f"Slept well! Restored {heal_amount} HP and {mana_amount} Mana"
            logger.info(f"[TAVERN] Player rented room at {self.name}")
        
        elif service.effect_type == "rumor":
            rumor = self.get_random_rumor()
            result_message = f'Rumor: "{rumor.text}"'
            logger.info(f"[TAVERN] Player heard rumor: {rumor.text[:50]}...")
        
        return True, result_message


class TavernManager:
    """Manages all taverns in the game world"""
    def __init__(self):
        self.taverns = []
    
    def register_tavern(self, building, town_name):
        """Register a building as a tavern"""
        tavern = Tavern(building, town_name)
        self.taverns.append(tavern)
        logger.info(f"[TAVERN] Registered: {tavern.name}")
        return tavern
    
    def get_nearby_tavern(self, player_x, player_y, max_distance=80):
        """Find the nearest tavern within interaction range"""
        nearest = None
        nearest_distance = max_distance
        
        for tavern in self.taverns:
            door_x = tavern.building.x + tavern.building.width // 2
            door_y = tavern.building.y + tavern.building.height
            
            dx = player_x - door_x
            dy = player_y - door_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest = tavern
        
        return nearest


class TavernUI:
    """UI for tavern interactions"""
    def __init__(self, config):
        self.config = config
        self.active = False
        self.current_tavern = None
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        self.rumor_display = ""
        self.rumor_timer = 0
        self.food_trading_ui = None  # Will be set by main.py
    
    def open(self, tavern):
        """Open the tavern menu"""
        self.active = True
        self.current_tavern = tavern
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        self.rumor_display = ""
        self.rumor_timer = 0
        logger.info(f"[TAVERN UI] Opened {tavern.name}")
    
    def close(self):
        """Close the tavern menu"""
        self.active = False
        self.current_tavern = None
        self.selected_index = 0
        logger.info("[TAVERN UI] Closed")
    
    def handle_input(self, event, player, game_time):
        """Handle keyboard input for tavern menu"""
        if not self.active or not self.current_tavern:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_t:
                self.close()
            
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.current_tavern.services)
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.current_tavern.services)
            
            elif event.key == pygame.K_RETURN:
                # Check if it's the food trading service
                if self.selected_index == 0:  # Food Trading is first service
                    # Open food trading UI
                    if self.food_trading_ui:
                        self.food_trading_ui.open(self.current_tavern, player)
                        self.close()  # Close tavern main menu
                    return
                
                # Use selected service
                success, message = self.current_tavern.use_service(player, self.selected_index, game_time)
                
                # Check if it's a rumor (show differently)
                if "Rumor:" in message:
                    self.rumor_display = message.replace("Rumor: ", "").strip('"')
                    self.rumor_timer = 300  # 5 seconds
                    self.message = "You listen intently..."
                    self.message_timer = 60
                else:
                    self.message = message
                    self.message_timer = 120
    
    def draw(self, screen, player):
        """Draw the tavern menu"""
        if not self.active or not self.current_tavern:
            return
        
        # Update timers
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        if self.rumor_timer > 0:
            self.rumor_timer -= 1
            if self.rumor_timer <= 0:
                self.rumor_display = ""
        
        # Semi-transparent background
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Menu dimensions
        menu_width = 650
        menu_height = 520
        menu_x = (self.config.SCREEN_WIDTH - menu_width) // 2
        menu_y = (self.config.SCREEN_HEIGHT - menu_height) // 2
        
        # Menu background - warm tavern colors
        menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_bg.fill((50, 35, 25, 240))
        pygame.draw.rect(menu_bg, (180, 120, 60), (0, 0, menu_width, menu_height), 4)
        screen.blit(menu_bg, (menu_x, menu_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render(self.current_tavern.name, True, (255, 200, 120))
        screen.blit(title, (menu_x + menu_width // 2 - title.get_width() // 2, menu_y + 20))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 24)
        subtitle = subtitle_font.render("A warm and lively establishment", True, (220, 180, 140))
        screen.blit(subtitle, (menu_x + menu_width // 2 - subtitle.get_width() // 2, menu_y + 70))
        
        # Player info
        info_font = pygame.font.SysFont(None, 28)
        gold_text = info_font.render(f"Your Dubloons: {player.dubloons}db", True, (255, 215, 0))
        hp_text = info_font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 100, 100))
        
        screen.blit(gold_text, (menu_x + 20, menu_y + 110))
        screen.blit(hp_text, (menu_x + 300, menu_y + 110))
        
        # Services list
        service_y = menu_y + 160
        service_font = pygame.font.SysFont(None, 32)
        desc_font = pygame.font.SysFont(None, 22)
        
        for i, service in enumerate(self.current_tavern.services):
            is_selected = (i == self.selected_index)
            can_afford = player.dubloons >= service.cost
            
            # Service background
            service_height = 65
            service_bg_color = (90, 60, 40, 200) if is_selected else (60, 45, 30, 150)
            service_bg = pygame.Surface((menu_width - 40, service_height), pygame.SRCALPHA)
            service_bg.fill(service_bg_color)
            
            if is_selected:
                pygame.draw.rect(service_bg, (220, 160, 100), (0, 0, menu_width - 40, service_height), 3)
            
            screen.blit(service_bg, (menu_x + 20, service_y))
            
            # Service name and cost
            name_color = (255, 255, 255) if can_afford else (150, 150, 150)
            cost_color = (255, 215, 0) if can_afford else (150, 100, 50)
            
            name_text = service_font.render(service.name, True, name_color)
            cost_text = service_font.render(f"{service.cost}g", True, cost_color)
            
            screen.blit(name_text, (menu_x + 35, service_y + 10))
            screen.blit(cost_text, (menu_x + menu_width - 100, service_y + 10))
            
            # Service description
            desc_text = desc_font.render(service.description, True, (200, 170, 140))
            screen.blit(desc_text, (menu_x + 35, service_y + 40))
            
            service_y += service_height + 8
        
        # Instructions
        instruction_y = menu_y + menu_height - 60
        instruction_font = pygame.font.SysFont(None, 24)
        instructions = ["↑↓: Select", "ENTER: Order", "ESC/T: Leave"]
        
        instruction_x = menu_x + 20
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (220, 180, 140))
            screen.blit(instr_text, (instruction_x, instruction_y))
            instruction_x += 210
        
        # Rumor display (if active)
        if self.rumor_display:
            self._draw_rumor(screen, menu_x, menu_y, menu_width, menu_height)
        
        # Regular message (success/error)
        elif self.message:
            message_font = pygame.font.SysFont(None, 32)
            message_color = (100, 255, 100) if "Restored" in self.message or "well" in self.message else (255, 100, 100)
            message_surf = message_font.render(self.message, True, message_color)
            
            # Message background
            msg_width = message_surf.get_width() + 40
            msg_height = message_surf.get_height() + 20
            msg_x = (self.config.SCREEN_WIDTH - msg_width) // 2
            msg_y = menu_y + menu_height + 20
            
            msg_bg = pygame.Surface((msg_width, msg_height), pygame.SRCALPHA)
            msg_bg.fill((20, 20, 20, 220))
            pygame.draw.rect(msg_bg, message_color, (0, 0, msg_width, msg_height), 2)
            
            screen.blit(msg_bg, (msg_x, msg_y))
            screen.blit(message_surf, (msg_x + 20, msg_y + 10))
    
    def _draw_rumor(self, screen, menu_x, menu_y, menu_width, menu_height):
        """Draw the rumor overlay"""
        # Rumor panel
        rumor_width = menu_width - 80
        rumor_height = 120
        rumor_x = menu_x + 40
        rumor_y = menu_y + menu_height + 30
        
        rumor_bg = pygame.Surface((rumor_width, rumor_height), pygame.SRCALPHA)
        rumor_bg.fill((30, 20, 10, 240))
        pygame.draw.rect(rumor_bg, (200, 150, 80), (0, 0, rumor_width, rumor_height), 3)
        
        screen.blit(rumor_bg, (rumor_x, rumor_y))
        
        # Rumor title
        title_font = pygame.font.SysFont(None, 28)
        title = title_font.render("You overhear a rumor...", True, (255, 200, 100))
        screen.blit(title, (rumor_x + 20, rumor_y + 15))
        
        # Rumor text (word wrap)
        rumor_font = pygame.font.SysFont(None, 24)
        words = self.rumor_display.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if rumor_font.size(test_line)[0] < rumor_width - 40:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw rumor lines
        text_y = rumor_y + 50
        for line in lines[:2]:  # Max 2 lines
            text = rumor_font.render(line, True, (230, 210, 180))
            screen.blit(text, (rumor_x + 20, text_y))
            text_y += 28
