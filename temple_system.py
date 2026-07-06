"""
Temple System
Provides healing, blessings, and divine services
"""

import pygame
import logging

logger = logging.getLogger(__name__)


class Blessing:
    """A temporary blessing that provides buffs"""
    def __init__(self, name, description, duration, effect_type, effect_value):
        self.name = name
        self.description = description
        self.duration = duration  # In seconds
        self.remaining_time = duration
        self.effect_type = effect_type  # damage_boost, defense_boost, xp_boost, luck
        self.effect_value = effect_value
        self.active = True
    
    def update(self, dt):
        """Update blessing timer"""
        if self.active:
            self.remaining_time -= dt
            if self.remaining_time <= 0:
                self.active = False
                return True  # Blessing expired
        return False
    
    def get_time_remaining_text(self):
        """Get formatted time remaining"""
        minutes = int(self.remaining_time // 60)
        seconds = int(self.remaining_time % 60)
        return f"{minutes}:{seconds:02d}"


class TempleService:
    """Individual service offered at a temple"""
    def __init__(self, name, description, cost, service_type, effect_value=0, duration=0):
        self.name = name
        self.description = description
        self.cost = cost
        self.service_type = service_type  # heal, cure, blessing, prayer, donate
        self.effect_value = effect_value
        self.duration = duration  # For blessings


class Temple:
    """Represents a temple with divine services"""
    def __init__(self, building, town_name):
        self.building = building
        self.town_name = town_name
        self.name = building.name
        
        # Define available services
        self.services = [
            TempleService(
                "Minor Healing",
                "Restore 50% HP through divine magic",
                cost=10,
                service_type="heal",
                effect_value=0.5
            ),
            TempleService(
                "Greater Healing",
                "Fully restore HP through prayer",
                cost=25,
                service_type="heal",
                effect_value=1.0
            ),
            TempleService(
                "Divine Restoration",
                "Restore HP and Mana completely",
                cost=40,
                service_type="heal_all",
                effect_value=1.0
            ),
            TempleService(
                "Blessing of Strength",
                "Increase damage by 20% (5 min)",
                cost=30,
                service_type="blessing",
                effect_value=0.20,
                duration=300
            ),
            TempleService(
                "Blessing of Protection",
                "Increase defense by 25% (5 min)",
                cost=30,
                service_type="blessing",
                effect_value=0.25,
                duration=300
            ),
            TempleService(
                "Blessing of Fortune",
                "Increase XP gain by 50% (10 min)",
                cost=50,
                service_type="blessing",
                effect_value=0.50,
                duration=600
            ),
            TempleService(
                "Cure Common Ailments",
                "Cure common diseases (cold, flu) - 100db",
                cost=100,
                service_type="cure_common",
                effect_value=0
            ),
            TempleService(
                "Cure STDs (Night Only)",
                "Discreet treatment for STDs - 300db",
                cost=300,
                service_type="cure_std",
                effect_value=0
            ),
            TempleService(
                "Purify Body",
                "Remove all curable diseases - 500db",
                cost=500,
                service_type="cure_all",
                effect_value=0
            ),
            TempleService(
                "Donate to Temple",
                "Make an offering (any amount)",
                cost=0,
                service_type="donate",
                effect_value=0
            ),
        ]
    
    def use_service(self, player, service_index, custom_amount=0):
        """Use a temple service"""
        if not (0 <= service_index < len(self.services)):
            return False, "Invalid service", None
        
        service = self.services[service_index]
        
        # Handle donation separately
        if service.service_type == "donate":
            if custom_amount <= 0:
                return False, "Enter amount to donate", None
            if player.dubloons < custom_amount:
                return False, f"Not enough dubloons!", None
            
            player.dubloons -= custom_amount
            # Small HP bonus for donating
            bonus = min(20, custom_amount // 5)
            player.hp = min(player.max_hp, player.hp + bonus)
            logger.info(f"[TEMPLE] Player donated {custom_amount}g to {self.name}")
            return True, f"Thank you for your {custom_amount}g donation! +{bonus} HP", None
        
        # Check if player can afford
        if player.dubloons < service.cost:
            return False, f"Not enough dubloons! Need {service.cost}db", None
        
        # Deduct cost
        player.dubloons -= service.cost
        
        result_message = ""
        blessing = None
        
        # Apply service effects
        if service.service_type == "heal":
            heal_amount = int(player.max_hp * service.effect_value)
            old_hp = player.hp
            player.hp = min(player.max_hp, player.hp + heal_amount)
            actual_heal = player.hp - old_hp
            result_message = f"Divine healing restored {actual_heal} HP!"
            logger.info(f"[TEMPLE] Player healed at {self.name}")
        
        elif service.service_type == "heal_all":
            hp_heal = player.max_hp - player.hp
            mana_heal = player.max_mana - player.mana
            player.hp = player.max_hp
            player.mana = player.max_mana
            result_message = f"Fully restored! +{hp_heal} HP, +{mana_heal} Mana"
            logger.info(f"[TEMPLE] Player fully restored at {self.name}")
        
        elif service.service_type == "blessing":
            # Create blessing effect
            if "Strength" in service.name:
                blessing = Blessing(
                    "Blessing of Strength",
                    f"+{int(service.effect_value * 100)}% Damage",
                    service.duration,
                    "damage_boost",
                    service.effect_value
                )
                result_message = "You feel stronger! Damage increased!"
            
            elif "Protection" in service.name:
                blessing = Blessing(
                    "Blessing of Protection",
                    f"+{int(service.effect_value * 100)}% Defense",
                    service.duration,
                    "defense_boost",
                    service.effect_value
                )
                result_message = "You feel protected! Defense increased!"
            
            elif "Fortune" in service.name:
                blessing = Blessing(
                    "Blessing of Fortune",
                    f"+{int(service.effect_value * 100)}% XP Gain",
                    service.duration,
                    "xp_boost",
                    service.effect_value
                )
                result_message = "Fortune smiles upon you! XP gain increased!"
            
            logger.info(f"[TEMPLE] Player received {blessing.name} at {self.name}")
        
        elif service.service_type == "cure_common":
            # Import disease_manager if not already available
            from disease_system import DiseaseType
            
            # Get disease_manager from main game (passed via player attribute)
            if not hasattr(player, 'disease_manager'):
                result_message = "Temple healing unavailable"
                return True, result_message, None
            
            disease_manager = player.disease_manager
            active_diseases = disease_manager.get_entity_diseases("player")
            cured_count = 0
            
            for disease_infection in active_diseases:
                disease = disease_infection.disease
                # Cure common diseases (cold, flu)
                if disease.type == DiseaseType.COMMON and disease.is_curable:
                    if "temple" in disease.cures:
                        disease_manager.cure_disease("player", disease.disease_id, "temple")
                        cured_count += 1
                        logger.info(f"[TEMPLE] Cured {disease.name} for player")
            
            if cured_count > 0:
                result_message = f"Cured {cured_count} common ailment(s)!"
            else:
                result_message = "No common diseases to cure (money not refunded)"
        
        elif service.service_type == "cure_std":
            # Check if it's night time (temples only cure STDs discreetly at night)
            if hasattr(player, 'game_time'):
                current_hour = player.game_time.hour
                if not (20 <= current_hour or current_hour < 6):
                    result_message = "STD treatments only available at night (8 PM - 6 AM)"
                    player.dubloons += service.cost  # Refund
                    return False, result_message, None
            
            from disease_system import DiseaseType
            
            if not hasattr(player, 'disease_manager'):
                result_message = "Temple healing unavailable"
                return True, result_message, None
            
            disease_manager = player.disease_manager
            active_diseases = disease_manager.get_entity_diseases("player")
            cured_count = 0
            
            for disease_infection in active_diseases:
                disease = disease_infection.disease
                # Cure STDs
                if disease.type in [DiseaseType.STD, DiseaseType.MAGICAL_STD] and disease.is_curable:
                    if "temple_night" in disease.cures or "temple" in disease.cures:
                        disease_manager.cure_disease("player", disease.disease_id, "temple_night")
                        cured_count += 1
                        logger.info(f"[TEMPLE] Cured {disease.name} for player")
            
            if cured_count > 0:
                result_message = f"Discreetly treated {cured_count} ailment(s). All is well."
            else:
                result_message = "No such ailments found (money not refunded)"
        
        elif service.service_type == "cure_all":
            # Cure all curable diseases
            from disease_system import DiseaseType
            
            if not hasattr(player, 'disease_manager'):
                result_message = "Temple healing unavailable"
                return True, result_message, None
            
            disease_manager = player.disease_manager
            active_diseases = disease_manager.get_entity_diseases("player")
            cured_count = 0
            
            for disease_infection in active_diseases:
                disease = disease_infection.disease
                # Cure any curable disease
                if disease.is_curable:
                    cure_method = "temple_night" if "temple_night" in disease.cures else "temple"
                    disease_manager.cure_disease("player", disease.disease_id, cure_method)
                    cured_count += 1
                    logger.info(f"[TEMPLE] Cured {disease.name} for player")
            
            if cured_count > 0:
                result_message = f"Purified! Cured {cured_count} disease(s)!"
            else:
                result_message = "No curable diseases found (money not refunded)"
        
        return True, result_message, blessing


class TempleManager:
    """Manages all temples in the game world"""
    def __init__(self):
        self.temples = []
    
    def register_temple(self, building, town_name):
        """Register a building as a temple"""
        temple = Temple(building, town_name)
        self.temples.append(temple)
        logger.info(f"[TEMPLE] Registered: {temple.name}")
        return temple
    
    def get_nearby_temple(self, player_x, player_y, max_distance=80):
        """Find the nearest temple within interaction range"""
        nearest = None
        nearest_distance = max_distance
        
        for temple in self.temples:
            door_x = temple.building.x + temple.building.width // 2
            door_y = temple.building.y + temple.building.height
            
            dx = player_x - door_x
            dy = player_y - door_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest = temple
        
        return nearest


class TempleUI:
    """UI for temple interactions"""
    def __init__(self, config):
        self.config = config
        self.active = False
        self.current_temple = None
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        self.donation_mode = False
        self.donation_amount = ""
    
    def open(self, temple):
        """Open the temple menu"""
        self.active = True
        self.current_temple = temple
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        self.donation_mode = False
        self.donation_amount = ""
        logger.info(f"[TEMPLE UI] Opened {temple.name}")
    
    def close(self):
        """Close the temple menu"""
        self.active = False
        self.current_temple = None
        self.donation_mode = False
        logger.info("[TEMPLE UI] Closed")
    
    def handle_input(self, event, player):
        """Handle keyboard input for temple menu"""
        if not self.active or not self.current_temple:
            return None
        
        if event.type == pygame.KEYDOWN:
            # Handle donation input
            if self.donation_mode:
                if event.key == pygame.K_ESCAPE:
                    self.donation_mode = False
                    self.donation_amount = ""
                elif event.key == pygame.K_RETURN:
                    try:
                        amount = int(self.donation_amount)
                        success, message, _ = self.current_temple.use_service(player, self.selected_index, amount)
                        self.message = message
                        self.message_timer = 180
                        self.donation_mode = False
                        self.donation_amount = ""
                    except ValueError:
                        self.message = "Invalid amount"
                        self.message_timer = 60
                elif event.key == pygame.K_BACKSPACE:
                    self.donation_amount = self.donation_amount[:-1]
                elif event.unicode.isdigit() and len(self.donation_amount) < 6:
                    self.donation_amount += event.unicode
                return None
            
            # Normal menu controls
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.close()
            
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.current_temple.services)
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.current_temple.services)
            
            elif event.key == pygame.K_RETURN:
                service = self.current_temple.services[self.selected_index]
                
                # Check if donation
                if service.service_type == "donate":
                    self.donation_mode = True
                    self.donation_amount = ""
                    return None
                
                # Use service
                success, message, blessing = self.current_temple.use_service(player, self.selected_index)
                self.message = message
                self.message_timer = 180
                
                return blessing  # Return blessing to be added to player
        
        return None
    
    def draw(self, screen, player):
        """Draw the temple menu"""
        if not self.active or not self.current_temple:
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
        menu_width = 700
        menu_height = 580
        menu_x = (self.config.SCREEN_WIDTH - menu_width) // 2
        menu_y = (self.config.SCREEN_HEIGHT - menu_height) // 2
        
        # Menu background - holy/sacred colors
        menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_bg.fill((35, 35, 50, 240))
        pygame.draw.rect(menu_bg, (200, 180, 255), (0, 0, menu_width, menu_height), 4)
        screen.blit(menu_bg, (menu_x, menu_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render(self.current_temple.name, True, (230, 220, 255))
        screen.blit(title, (menu_x + menu_width // 2 - title.get_width() // 2, menu_y + 20))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 24)
        subtitle = subtitle_font.render("A sacred place of healing and blessings", True, (200, 190, 230))
        screen.blit(subtitle, (menu_x + menu_width // 2 - subtitle.get_width() // 2, menu_y + 70))
        
        # Player info
        info_font = pygame.font.SysFont(None, 28)
        gold_text = info_font.render(f"Dubloons: {player.dubloons}db", True, (255, 215, 0))
        hp_text = info_font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 100, 100))
        mana_text = info_font.render(f"Mana: {player.mana}/{player.max_mana}", True, (100, 150, 255))
        
        screen.blit(gold_text, (menu_x + 20, menu_y + 110))
        screen.blit(hp_text, (menu_x + 250, menu_y + 110))
        screen.blit(mana_text, (menu_x + 470, menu_y + 110))
        
        # Services list
        service_y = menu_y + 160
        service_font = pygame.font.SysFont(None, 30)
        desc_font = pygame.font.SysFont(None, 22)
        
        for i, service in enumerate(self.current_temple.services):
            is_selected = (i == self.selected_index)
            can_afford = player.dubloons >= service.cost or service.cost == 0
            
            # Service background
            service_height = 60
            service_bg_color = (70, 60, 90, 200) if is_selected else (50, 45, 65, 150)
            service_bg = pygame.Surface((menu_width - 40, service_height), pygame.SRCALPHA)
            service_bg.fill(service_bg_color)
            
            if is_selected:
                pygame.draw.rect(service_bg, (200, 180, 255), (0, 0, menu_width - 40, service_height), 3)
            
            screen.blit(service_bg, (menu_x + 20, service_y))
            
            # Service name and cost
            name_color = (255, 255, 255) if can_afford else (150, 150, 150)
            
            name_text = service_font.render(service.name, True, name_color)
            screen.blit(name_text, (menu_x + 35, service_y + 8))
            
            # Cost (if not donation)
            if service.cost > 0:
                cost_color = (255, 215, 0) if can_afford else (150, 100, 50)
                cost_text = service_font.render(f"{service.cost}g", True, cost_color)
                screen.blit(cost_text, (menu_x + menu_width - 100, service_y + 8))
            
            # Service description
            desc_text = desc_font.render(service.description, True, (200, 190, 220))
            screen.blit(desc_text, (menu_x + 35, service_y + 38))
            
            service_y += service_height + 5
        
        # Donation input overlay
        if self.donation_mode:
            self._draw_donation_input(screen, menu_x, menu_y, menu_width, menu_height)
        
        # Instructions
        instruction_y = menu_y + menu_height - 50
        instruction_font = pygame.font.SysFont(None, 24)
        instructions = ["↑↓: Select", "ENTER: Confirm", "ESC/P: Leave"]
        
        instruction_x = menu_x + 20
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (200, 190, 220))
            screen.blit(instr_text, (instruction_x, instruction_y))
            instruction_x += 220
        
        # Message
        if self.message and not self.donation_mode:
            message_font = pygame.font.SysFont(None, 32)
            
            # Determine color
            if "restored" in self.message.lower() or "feel" in self.message.lower() or "thank" in self.message.lower():
                message_color = (150, 255, 150)
            elif "Not enough" in self.message:
                message_color = (255, 100, 100)
            else:
                message_color = (200, 200, 255)
            
            message_surf = message_font.render(self.message, True, message_color)
            
            msg_x = (self.config.SCREEN_WIDTH - message_surf.get_width()) // 2
            msg_y = menu_y + menu_height + 20
            
            msg_bg = pygame.Surface((message_surf.get_width() + 40, message_surf.get_height() + 20), pygame.SRCALPHA)
            msg_bg.fill((20, 20, 30, 220))
            pygame.draw.rect(msg_bg, message_color, (0, 0, msg_bg.get_width(), msg_bg.get_height()), 2)
            
            screen.blit(msg_bg, (msg_x - 20, msg_y - 10))
            screen.blit(message_surf, (msg_x, msg_y))
    
    def _draw_donation_input(self, screen, menu_x, menu_y, menu_width, menu_height):
        """Draw donation input overlay"""
        # Donation panel
        panel_width = 400
        panel_height = 150
        panel_x = menu_x + (menu_width - panel_width) // 2
        panel_y = menu_y + (menu_height - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((40, 35, 60, 250))
        pygame.draw.rect(panel_bg, (200, 180, 255), (0, 0, panel_width, panel_height), 3)
        
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 32)
        title = title_font.render("Enter Donation Amount", True, (220, 210, 255))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Input field
        input_font = pygame.font.SysFont(None, 48)
        input_text = self.donation_amount if self.donation_amount else "0"
        input_surf = input_font.render(input_text + "g", True, (255, 215, 0))
        
        input_bg = pygame.Surface((panel_width - 40, 50), pygame.SRCALPHA)
        input_bg.fill((20, 20, 30, 200))
        pygame.draw.rect(input_bg, (255, 215, 0), (0, 0, panel_width - 40, 50), 2)
        
        screen.blit(input_bg, (panel_x + 20, panel_y + 60))
        screen.blit(input_surf, (panel_x + 30, panel_y + 68))
        
        # Instructions
        instr_font = pygame.font.SysFont(None, 20)
        instr = instr_font.render("ENTER: Donate | ESC: Cancel", True, (200, 190, 220))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, panel_y + 120))
