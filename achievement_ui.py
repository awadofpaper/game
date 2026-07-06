"""
Achievement UI - Display achievements and progress
"""
import pygame


class AchievementUI:
    """UI for viewing achievements"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.scroll_offset = 0
        self.selected_category = 0
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # Mouse tracking
        self.mouse_pos = None
        self.category_rects = []
        self.achievement_rects = []
        
    def toggle(self):
        """Toggle achievement UI"""
        self.active = not self.active
        if self.active:
            self.scroll_offset = 0
        return self.active
    
    def handle_input(self, event):
        """Handle keyboard and mouse input"""
        if not self.active:
            return
        
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            # Check category hover
            for i, rect in enumerate(self.category_rects):
                if rect.collidepoint(self.mouse_pos):
                    self.selected_category = i
                    self.scroll_offset = 0
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check category click
                for i, rect in enumerate(self.category_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_category = i
                        self.scroll_offset = 0
                        break
            elif event.button == 4:  # Mouse wheel up
                self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.button == 5:  # Mouse wheel down
                self.scroll_offset += 30
        
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_a]:
                self.active = False
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset += 30
            elif event.key == pygame.K_LEFT:
                self.selected_category = max(0, self.selected_category - 1)
                self.scroll_offset = 0
            elif event.key == pygame.K_RIGHT:
                self.selected_category += 1
                self.scroll_offset = 0
    
    def draw(self, screen, achievement_manager):
        """Draw achievement UI"""
        if not self.active:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("Achievements", True, (255, 215, 0))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 20))
        
        # Progress counter
        unlocked = achievement_manager.get_unlocked_count()
        total = achievement_manager.get_total_count()
        progress_text = self.font.render(f"{unlocked}/{total} Unlocked", True, (200, 200, 200))
        screen.blit(progress_text, (self.screen_width // 2 - progress_text.get_width() // 2, 60))
        
        # Category tabs
        categories = list(achievement_manager.get_achievements_by_category().keys())
        self.selected_category = min(self.selected_category, len(categories) - 1)
        
        tab_y = 100
        tab_width = 150
        self.category_rects = []  # Reset for this frame
        
        for i, category in enumerate(categories):
            is_hovered = False
            tab_rect = pygame.Rect(50 + i * (tab_width + 10), tab_y, tab_width, 40)
            self.category_rects.append(tab_rect)
            
            # Check hover
            if self.mouse_pos and tab_rect.collidepoint(self.mouse_pos):
                is_hovered = True
            
            color = (100, 150, 255) if (i == self.selected_category or is_hovered) else (60, 60, 80)
            pygame.draw.rect(screen, color, tab_rect)
            pygame.draw.rect(screen, (255, 255, 255), tab_rect, 2)
            
            cat_text = self.font.render(category, True, (255, 255, 255))
            screen.blit(cat_text, (tab_rect.centerx - cat_text.get_width() // 2, 
                                   tab_rect.centery - cat_text.get_height() // 2))
        
        # Achievement list
        current_category = categories[self.selected_category]
        achievements = achievement_manager.get_achievements_by_category()[current_category]
        
        y = 160 - self.scroll_offset
        for achievement in achievements:
            if y > 140 and y < self.screen_height - 50:
                # Achievement box
                box_color = (50, 100, 50) if achievement.unlocked else (60, 60, 80)
                box_rect = pygame.Rect(50, y, self.screen_width - 100, 80)
                pygame.draw.rect(screen, box_color, box_rect)
                pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)
                
                # Achievement name
                name_text = self.font.render(achievement.name, True, (255, 255, 255))
                screen.blit(name_text, (70, y + 10))
                
                # Description
                desc_text = self.small_font.render(achievement.description, True, (200, 200, 200))
                screen.blit(desc_text, (70, y + 35))
                
                # Progress
                progress_text = self.small_font.render(achievement.get_progress_text(), True, (150, 200, 255))
                screen.blit(progress_text, (70, y + 55))
                
                # Pet reward icon
                if achievement.pet_reward:
                    pet_text = self.small_font.render(f"Reward: {achievement.pet_reward.title()}", 
                                                     True, (255, 215, 0))
                    screen.blit(pet_text, (self.screen_width - 250, y + 30))
                
            y += 90
        
        # Controls help
        help_text = self.small_font.render("Arrow Keys: Navigate | ESC/A: Close", True, (150, 150, 150))
        screen.blit(help_text, (self.screen_width // 2 - help_text.get_width() // 2, 
                                self.screen_height - 30))


class AchievementPopup:
    """Popup notification when achievement is unlocked"""
    
    def __init__(self):
        self.active = False
        self.achievement = None
        self.timer = 0
        self.duration = 5.0  # Show for 5 seconds
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)
        
    def show(self, achievement):
        """Show popup for unlocked achievement"""
        self.active = True
        self.achievement = achievement
        self.timer = 0
        
    def update(self, dt):
        """Update popup timer"""
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.active = False
                self.achievement = None
    
    def draw(self, screen, screen_width, screen_height):
        """Draw achievement popup"""
        if not self.active or not self.achievement:
            return
        
        # Popup box at top center
        box_width = 400
        box_height = 100
        box_x = screen_width // 2 - box_width // 2
        box_y = 50
        
        # Background with glow effect
        glow_rect = pygame.Rect(box_x - 5, box_y - 5, box_width + 10, box_height + 10)
        pygame.draw.rect(screen, (255, 215, 0), glow_rect)
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (40, 40, 60), box_rect)
        pygame.draw.rect(screen, (255, 215, 0), box_rect, 3)
        
        # "Achievement Unlocked!" text
        unlock_text = self.font.render("Achievement Unlocked!", True, (255, 215, 0))
        screen.blit(unlock_text, (box_x + box_width // 2 - unlock_text.get_width() // 2, box_y + 10))
        
        # Achievement name
        name_text = self.font.render(self.achievement.name, True, (255, 255, 255))
        screen.blit(name_text, (box_x + box_width // 2 - name_text.get_width() // 2, box_y + 40))
        
        # Pet reward
        if self.achievement.pet_reward:
            reward_text = self.small_font.render(f"Pet Unlocked: {self.achievement.pet_reward.title()}", 
                                                 True, (100, 255, 100))
            screen.blit(reward_text, (box_x + box_width // 2 - reward_text.get_width() // 2, box_y + 70))
