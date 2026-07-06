"""
Inn and Rest System
Provides lodging, healing, and time advancement services
"""

import pygame
import logging

logger = logging.getLogger(__name__)


class InnService:
    """Individual service offered at an inn"""
    def __init__(self, name, description, cost, heal_amount=0, mana_amount=0, time_advance=0):
        self.name = name
        self.description = description
        self.cost = cost
        self.heal_amount = heal_amount  # Percentage of max HP
        self.mana_amount = mana_amount  # Percentage of max mana
        self.time_advance = time_advance  # Hours to advance


class Inn:
    """Represents an inn with various services"""
    def __init__(self, building, town_name):
        self.building = building
        self.town_name = town_name
        self.name = f"{town_name} Inn"
        
        # Define available services
        self.services = [
            InnService(
                "Quick Rest",
                "Rest for a few hours (4h)",
                cost=5,
                heal_amount=0.5,  # 50% HP
                mana_amount=0.5,  # 50% mana
                time_advance=4
            ),
            InnService(
                "Full Rest",
                "Rest until evening (8h)",
                cost=15,
                heal_amount=1.0,  # 100% HP
                mana_amount=1.0,  # 100% mana
                time_advance=8
            ),
            InnService(
                "Rent a Room",
                "Sleep until morning (+full heal)",
                cost=25,
                heal_amount=1.0,
                mana_amount=1.0,
                time_advance=12  # Sleep until next morning
            ),
            InnService(
                "Extended Stay",
                "Rest for a full day (24h)",
                cost=50,
                heal_amount=1.0,
                mana_amount=1.0,
                time_advance=24
            ),
        ]
    
    def can_afford(self, player, service_index):
        """Check if player can afford a service"""
        if 0 <= service_index < len(self.services):
            return player.dubloons >= self.services[service_index].cost
        return False
    
    def use_service(self, player, service_index, game_time):
        """Use an inn service"""
        if not (0 <= service_index < len(self.services)):
            return False, "Invalid service"
        
        service = self.services[service_index]
        
        # Check if player can afford
        if player.dubloons < service.cost:
            return False, f"Not enough dubloons! Need {service.cost}db"
        
        # Deduct cost
        player.dubloons -= service.cost
        
        # Heal player
        if service.heal_amount > 0:
            heal_amount = int(player.max_hp * service.heal_amount)
            player.hp = min(player.max_hp, player.hp + heal_amount)
        
        # Restore mana
        if service.mana_amount > 0:
            mana_amount = int(player.max_mana * service.mana_amount)
            player.mana = min(player.max_mana, player.mana + mana_amount)
        
        # Advance time
        if service.time_advance > 0 and game_time:
            game_time.advance_time(service.time_advance * 60)  # Convert hours to minutes
        
        logger.info(f"[INN] Player used '{service.name}' at {self.name} for {service.cost}g")
        return True, f"Rested at {self.name}. HP/Mana restored!"


class InnManager:
    """Manages all inns in the game world"""
    def __init__(self):
        self.inns = []
    
    def register_inn(self, building, town_name):
        """Register a building as an inn"""
        inn = Inn(building, town_name)
        self.inns.append(inn)
        logger.info(f"[INN] Registered inn: {inn.name}")
        return inn
    
    def get_nearby_inn(self, player_x, player_y, max_distance=80):
        """Find the nearest inn within interaction range"""
        nearest_inn = None
        nearest_distance = max_distance
        
        for inn in self.inns:
            # Check distance to inn door
            door_x = inn.building.x + inn.building.width // 2
            door_y = inn.building.y + inn.building.height
            
            dx = player_x - door_x
            dy = player_y - door_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_inn = inn
        
        return nearest_inn


class InnUI:
    """UI for inn interactions"""
    def __init__(self, config):
        self.config = config
        self.active = False
        self.current_inn = None
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
    
    def open(self, inn):
        """Open the inn menu"""
        self.active = True
        self.current_inn = inn
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        logger.info(f"[INN UI] Opened menu for {inn.name}")
    
    def close(self):
        """Close the inn menu"""
        self.active = False
        self.current_inn = None
        self.selected_index = 0
        self.message = ""
        logger.info("[INN UI] Closed inn menu")
    
    def handle_input(self, event, player, game_time):
        """Handle keyboard input for inn menu"""
        if not self.active or not self.current_inn:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.close()
            
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.current_inn.services)
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.current_inn.services)
            
            elif event.key == pygame.K_RETURN:
                # Use selected service
                success, message = self.current_inn.use_service(player, self.selected_index, game_time)
                self.message = message
                self.message_timer = 120  # 2 seconds
                
                if success:
                    # Close menu after successful service use
                    pygame.time.set_timer(pygame.USEREVENT + 10, 1500)  # Close after 1.5 seconds
    
    def draw(self, screen, player):
        """Draw the inn menu"""
        if not self.active or not self.current_inn:
            return
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        # Semi-transparent background
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Menu dimensions
        menu_width = 600
        menu_height = 500
        menu_x = (self.config.SCREEN_WIDTH - menu_width) // 2
        menu_y = (self.config.SCREEN_HEIGHT - menu_height) // 2
        
        # Menu background
        menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_bg.fill((40, 30, 20, 240))
        pygame.draw.rect(menu_bg, (150, 100, 50), (0, 0, menu_width, menu_height), 4)
        screen.blit(menu_bg, (menu_x, menu_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render(self.current_inn.name, True, (255, 200, 100))
        screen.blit(title, (menu_x + menu_width // 2 - title.get_width() // 2, menu_y + 20))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 24)
        subtitle = subtitle_font.render("Rest and restore your strength", True, (200, 180, 150))
        screen.blit(subtitle, (menu_x + menu_width // 2 - subtitle.get_width() // 2, menu_y + 70))
        
        # Player info
        info_font = pygame.font.SysFont(None, 28)
        gold_text = info_font.render(f"Your Dubloons: {player.dubloons}db", True, (255, 215, 0))
        hp_text = info_font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 100, 100))
        mana_text = info_font.render(f"Mana: {player.mana}/{player.max_mana}", True, (100, 150, 255))
        
        screen.blit(gold_text, (menu_x + 20, menu_y + 110))
        screen.blit(hp_text, (menu_x + 220, menu_y + 110))
        screen.blit(mana_text, (menu_x + 420, menu_y + 110))
        
        # Services list
        service_y = menu_y + 160
        service_font = pygame.font.SysFont(None, 32)
        desc_font = pygame.font.SysFont(None, 22)
        
        for i, service in enumerate(self.current_inn.services):
            is_selected = (i == self.selected_index)
            can_afford = self.current_inn.can_afford(player, i)
            
            # Service background
            service_height = 70
            service_bg_color = (80, 60, 40, 200) if is_selected else (50, 40, 30, 150)
            service_bg = pygame.Surface((menu_width - 40, service_height), pygame.SRCALPHA)
            service_bg.fill(service_bg_color)
            
            if is_selected:
                pygame.draw.rect(service_bg, (200, 150, 100), (0, 0, menu_width - 40, service_height), 3)
            
            screen.blit(service_bg, (menu_x + 20, service_y))
            
            # Service name and cost
            name_color = (255, 255, 255) if can_afford else (150, 150, 150)
            cost_color = (255, 215, 0) if can_afford else (150, 100, 50)
            
            name_text = service_font.render(service.name, True, name_color)
            cost_text = service_font.render(f"{service.cost}g", True, cost_color)
            
            screen.blit(name_text, (menu_x + 35, service_y + 10))
            screen.blit(cost_text, (menu_x + menu_width - 100, service_y + 10))
            
            # Service description
            desc_text = desc_font.render(service.description, True, (180, 160, 140))
            screen.blit(desc_text, (menu_x + 35, service_y + 42))
            
            service_y += service_height + 10
        
        # Instructions
        instruction_y = menu_y + menu_height - 60
        instruction_font = pygame.font.SysFont(None, 24)
        instructions = [
            "↑↓: Select service",
            "ENTER: Use service",
            "ESC/I: Close"
        ]
        
        instruction_x = menu_x + 20
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (200, 180, 150))
            screen.blit(instr_text, (instruction_x, instruction_y))
            instruction_x += 200
        
        # Message (success/error)
        if self.message:
            message_font = pygame.font.SysFont(None, 32)
            message_color = (100, 255, 100) if "restored" in self.message.lower() or "rested" in self.message.lower() else (255, 100, 100)
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
