"""
Mage Service System - Cure Magical Diseases and Provide Arcane Services
"""

import pygame
import logging

logger = logging.getLogger(__name__)

class MageService:
    """A service offered by mages"""
    
    def __init__(self, name, description, cost, service_type, required_ingredient=None, disease_id=None):
        self.name = name
        self.description = description
        self.cost = cost  # Dubloons cost
        self.service_type = service_type  # 'cure_magical', 'enchant', 'identify', etc.
        self.required_ingredient = required_ingredient  # Dungeon ingredient needed
        self.disease_id = disease_id  # Which disease this cures


class Mage:
    """A mage NPC who provides arcane services"""
    
    def __init__(self, building, town_name):
        self.building = building
        self.town_name = town_name
        self.name = building.name if hasattr(building, 'name') else "Arcane Sanctum"
        
        # Define available services
        self.services = [
            # Magical Disease Cures
            MageService(
                "Cure Mana Rot",
                "Purify corrupted mana channels (requires Arcane Crystal + 2000db)",
                cost=2000,
                service_type="cure_magical",
                required_ingredient="arcane_crystal",
                disease_id="mana_rot"
            ),
            MageService(
                "Cure Arcane Flu",
                "Stabilize uncontrolled magic (requires Arcane Crystal + 1000db)",
                cost=1000,
                service_type="cure_magical",
                required_ingredient="arcane_crystal",
                disease_id="arcane_flu"
            ),
            MageService(
                "Cure Shadow Plague",
                "Cleanse dark corruption (requires Shadow Essence + 1500db)",
                cost=1500,
                service_type="cure_magical",
                required_ingredient="shadow_essence",
                disease_id="shadow_plague"
            ),
            MageService(
                "Cure Fey Fever",
                "Break fey enchantment (requires Fey Dust + 1500db)",
                cost=1500,
                service_type="cure_magical",
                required_ingredient="fey_dust",
                disease_id="fey_fever"
            ),
            MageService(
                "Cure Fire Sneezing",
                "Remove fire curse (requires Infernal Ash + 1000db)",
                cost=1000,
                service_type="cure_magical",
                required_ingredient="infernal_ash",
                disease_id="fire_sneezing"
            ),
            MageService(
                "Cure Soul Binding Sickness",
                "Break soul bond (requires Soul Fragment + 2500db)",
                cost=2500,
                service_type="cure_magical",
                required_ingredient="soul_fragment",
                disease_id="soul_binding_sickness"
            ),
            MageService(
                "Magical Diagnosis",
                "Identify all active magical diseases - 50db",
                cost=50,
                service_type="diagnose"
            ),
        ]
    
    def use_service(self, player, service_index):
        """Use a mage service"""
        if not (0 <= service_index < len(self.services)):
            return False, "Invalid service", None
        
        service = self.services[service_index]
        
        # Handle magical diagnosis
        if service.service_type == "diagnose":
            if player.dubloons < service.cost:
                return False, f"Not enough dubloons! Need {service.cost}db", None
            
            player.dubloons -= service.cost
            
            if hasattr(player, 'disease_manager'):
                from disease_system import DiseaseType
                diseases = player.disease_manager.get_entity_diseases("player")
                magical_diseases = [d for d in diseases 
                                  if d.disease.type.name in ["MAGICAL", "MAGICAL_STD"]]
                
                if magical_diseases:
                    disease_names = [d.disease.name for d in magical_diseases]
                    result_message = f"Magical diseases detected:\\n" + "\\n".join(f"- {name}" for name in disease_names)
                else:
                    result_message = "No magical diseases detected. You are healthy!"
            else:
                result_message = "Diagnosis unavailable"
            
            logger.info(f"[MAGE] Player used magical diagnosis at {self.name}")
            return True, result_message, None
        
        # Handle magical disease cure
        elif service.service_type == "cure_magical":
            # Check if player can afford
            if player.dubloons < service.cost:
                return False, f"Not enough dubloons! Need {service.cost}db", None
            
            # Check if player has required ingredient
            if service.required_ingredient:
                if player.inventory.get(service.required_ingredient, 0) < 1:
                    ingredient_name = service.required_ingredient.replace("_", " ").title()
                    return False, f"Need {ingredient_name} to perform this cure!", None
            
            # Check if player has the disease
            if not hasattr(player, 'disease_manager'):
                return False, "Disease system unavailable", None
            
            diseases = player.disease_manager.get_entity_diseases("player")
            has_disease = any(d.disease.disease_id == service.disease_id for d in diseases)
            
            if not has_disease:
                return False, f"You don't have {service.name.replace('Cure ', '')}!", None
            
            # Perform the cure
            player.dubloons -= service.cost
            if service.required_ingredient:
                player.inventory[service.required_ingredient] -= 1
            
            player.disease_manager.cure_disease("player", service.disease_id, "mage")
            
            result_message = f"✨ Magical cure successful!\\nCured {service.name.replace('Cure ', '')}!"
            logger.info(f"[MAGE] Player cured {service.disease_id} at {self.name}")
            return True, result_message, None
        
        return False, "Service unavailable", None


class MageManager:
    """Manages all mages in the game world"""
    
    def __init__(self):
        self.mages = []
    
    def register_mage(self, building, town_name):
        """Register a building as a mage tower"""
        mage = Mage(building, town_name)
        self.mages.append(mage)
        logger.info(f"[MAGE] Registered: {mage.name} in {town_name}")
        return mage
    
    def get_nearby_mage(self, player_x, player_y, max_distance=80):
        """Find the nearest mage within interaction range"""
        nearest = None
        nearest_distance = max_distance
        
        for mage in self.mages:
            door_x = mage.building.x + mage.building.width // 2
            door_y = mage.building.y + mage.building.height
            
            dx = player_x - door_x
            dy = player_y - door_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest = mage
        
        return nearest


class MageUI:
    """UI for interacting with mages"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.current_mage = None
        self.selected_service = 0
        self.scroll_offset = 0
        self.result_message = ""
        self.result_timer = 0
    
    def open(self, mage):
        """Open the mage UI"""
        self.active = True
        self.current_mage = mage
        self.selected_service = 0
        self.scroll_offset = 0
        self.result_message = ""
        self.result_timer = 0
    
    def close(self):
        """Close the mage UI"""
        self.active = False
        self.current_mage = None
        self.result_message = ""
    
    def handle_input(self, event, player):
        """Handle keyboard/mouse input"""
        if not self.active or not self.current_mage:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_f:
                self.close()
                return "closed"
            
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_service = max(0, self.selected_service - 1)
                self.result_message = ""
            
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                max_services = len(self.current_mage.services)
                self.selected_service = min(max_services - 1, self.selected_service + 1)
                self.result_message = ""
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Purchase selected service
                success, message, _ = self.current_mage.use_service(player, self.selected_service)
                self.result_message = message
                self.result_timer = 180  # 3 seconds
        
        return None
    
    def draw(self, screen, font, title_font):
        """Draw the mage UI"""
        if not self.active or not self.current_mage:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Main window
        window_width = 700
        window_height = 600
        window_x = (self.screen_width - window_width) // 2
        window_y = (self.screen_height - window_height) // 2
        
        # Window background (dark purple/blue for arcane theme)
        pygame.draw.rect(screen, (30, 20, 60), (window_x, window_y, window_width, window_height))
        pygame.draw.rect(screen, (100, 80, 200), (window_x, window_y, window_width, window_height), 3)
        
        # Title
        title_text = title_font.render(f"✨ {self.current_mage.name} ✨", True, (200, 180, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, window_y + 40))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle = font.render("Arcane Services & Magical Disease Treatment", True, (150, 130, 200))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, window_y + 75))
        screen.blit(subtitle, subtitle_rect)
        
        # Service list
        service_y = window_y + 110
        service_height = 60
        
        for i, service in enumerate(self.current_mage.services):
            y_pos = service_y + (i * service_height)
            
            # Skip if scrolled out of view
            if y_pos < window_y + 100 or y_pos > window_y + window_height - 100:
                continue
            
            # Highlight selected service
            if i == self.selected_service:
                pygame.draw.rect(screen, (60, 50, 100), 
                               (window_x + 20, y_pos, window_width - 40, service_height - 5))
                pygame.draw.rect(screen, (150, 130, 255), 
                               (window_x + 20, y_pos, window_width - 40, service_height - 5), 2)
            else:
                pygame.draw.rect(screen, (40, 30, 70), 
                               (window_x + 20, y_pos, window_width - 40, service_height - 5))
            
            # Service name
            name_text = font.render(service.name, True, (220, 200, 255))
            screen.blit(name_text, (window_x + 30, y_pos + 5))
            
            # Service description
            desc_text = font.render(service.description, True, (180, 160, 220))
            screen.blit(desc_text, (window_x + 30, y_pos + 30))
        
        # Result message
        if self.result_message and self.result_timer > 0:
            self.result_timer -= 1
            
            # Determine color based on success
            if "successful" in self.result_message.lower() or "cured" in self.result_message.lower():
                msg_color = (100, 255, 100)
            elif "not enough" in self.result_message.lower() or "need" in self.result_message.lower():
                msg_color = (255, 100, 100)
            else:
                msg_color = (200, 200, 255)
            
            # Split message into lines
            lines = self.result_message.split("\\n")
            msg_y = window_y + window_height - 120
            
            for line in lines:
                msg_text = font.render(line, True, msg_color)
                msg_rect = msg_text.get_rect(center=(self.screen_width // 2, msg_y))
                screen.blit(msg_text, msg_rect)
                msg_y += 25
        
        # Controls hint
        controls_text = font.render("↑/↓: Select | ENTER: Use Service | ESC/F: Close", True, (150, 130, 200))
        controls_rect = controls_text.get_rect(center=(self.screen_width // 2, window_y + window_height - 30))
        screen.blit(controls_text, controls_rect)
