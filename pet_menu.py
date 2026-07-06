"""
Pet Menu UI - Select active pet from unlocked pets
"""
import pygame


class PetMenuUI:
    """UI for selecting active pet"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.selected_index = 0
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 40)
        self.small_font = pygame.font.SysFont(None, 22)
        
    def toggle(self):
        """Toggle pet menu"""
        self.active = not self.active
        return self.active
    
    def handle_input(self, event, pet_manager):
        """Handle keyboard input"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            unlocked = pet_manager.achievement_manager.unlocked_pets
            
            if event.key in [pygame.K_ESCAPE]:
                self.active = False
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(unlocked) - 1, self.selected_index + 1)
            elif event.key == pygame.K_LEFT:
                self.selected_index = max(0, self.selected_index - 4)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = min(len(unlocked) - 1, self.selected_index + 4)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                # Select this pet
                selected_pet = unlocked[self.selected_index]
                pet_manager.set_pet(selected_pet)
                return selected_pet
        
        return None
    
    def draw(self, screen, pet_manager):
        """Draw pet menu"""
        if not self.active:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(220)
        overlay.fill((20, 20, 40))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("Pet Selection", True, (100, 200, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 30))
        
        # Current pet display
        current_text = self.font.render(f"Current Pet: {pet_manager.current_pet.title() if pet_manager.enabled else 'None'}", 
                                       True, (200, 200, 200))
        screen.blit(current_text, (self.screen_width // 2 - current_text.get_width() // 2, 80))
        
        # Pet grid
        unlocked_pets = pet_manager.achievement_manager.unlocked_pets
        self.selected_index = min(self.selected_index, len(unlocked_pets) - 1)
        
        pets_per_row = 4
        pet_box_size = 120
        start_x = self.screen_width // 2 - (pets_per_row * pet_box_size) // 2
        start_y = 140
        
        for i, pet_type in enumerate(unlocked_pets):
            row = i // pets_per_row
            col = i % pets_per_row
            
            x = start_x + col * pet_box_size
            y = start_y + row * pet_box_size
            
            # Pet box
            is_selected = (i == self.selected_index)
            is_active = (pet_manager.enabled and pet_manager.current_pet == pet_type)
            
            if is_active:
                box_color = (50, 150, 50)
            elif is_selected:
                box_color = (100, 150, 255)
            else:
                box_color = (60, 60, 80)
            
            box_rect = pygame.Rect(x, y, pet_box_size - 10, pet_box_size - 10)
            pygame.draw.rect(screen, box_color, box_rect)
            
            if is_selected:
                pygame.draw.rect(screen, (255, 255, 255), box_rect, 3)
            else:
                pygame.draw.rect(screen, (150, 150, 150), box_rect, 2)
            
            # Pet name
            pet_name = self.font.render(pet_type.title(), True, (255, 255, 255))
            screen.blit(pet_name, (box_rect.centerx - pet_name.get_width() // 2, 
                                   box_rect.top + 10))
            
            # Simple pet preview (colored circle)
            from chicken_pet import PET_DEFINITIONS
            if pet_type in PET_DEFINITIONS:
                pet_def = PET_DEFINITIONS[pet_type]
                preview_size = 30
                pygame.draw.circle(screen, pet_def["body_color"], 
                                 (box_rect.centerx, box_rect.centery + 10), preview_size)
                pygame.draw.circle(screen, (0, 0, 0), 
                                 (box_rect.centerx, box_rect.centery + 10), preview_size, 2)
            
            # Active indicator
            if is_active:
                active_text = self.small_font.render("ACTIVE", True, (100, 255, 100))
                screen.blit(active_text, (box_rect.centerx - active_text.get_width() // 2, 
                                         box_rect.bottom - 25))
        
        # Controls help
        help_lines = [
            "Arrow Keys: Navigate | ENTER/SPACE: Select Pet",
            "ESC: Close | Press U in-game to toggle pet on/off"
        ]
        
        y = self.screen_height - 80
        for line in help_lines:
            help_text = self.small_font.render(line, True, (150, 150, 150))
            screen.blit(help_text, (self.screen_width // 2 - help_text.get_width() // 2, y))
            y += 25
