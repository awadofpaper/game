"""
UI for displaying dungeon modifiers, difficulty, traps, and speed run timer
"""
import pygame
from typing import Dict, Optional
from dungeon_variety import DUNGEON_MODIFIERS, DIFFICULTY_TIERS


class DungeonInfoUI:
    """UI overlay showing dungeon modifier and difficulty"""
    
    def __init__(self):
        self.visible = True
        self.position = "top-left"
        self.fade_timer = 10.0  # Show for 10 seconds then fade
        self.alpha = 255
        
    def draw(self, screen, dungeon, font):
        """Draw dungeon info panel"""
        if not self.visible or self.alpha <= 0:
            return
        
        # Extract info
        difficulty = getattr(dungeon, 'difficulty', 'normal')
        modifier = getattr(dungeon, 'modifier', None)
        difficulty_data = DIFFICULTY_TIERS.get(difficulty, DIFFICULTY_TIERS['normal'])
        modifier_data = DUNGEON_MODIFIERS.get(modifier, None) if modifier else None
        
        # Panel dimensions
        panel_width = 400
        panel_height = 120 if modifier_data else 80
        margin = 20
        
        # Position
        if self.position == "top-left":
            panel_x = margin
            panel_y = margin
        else:
            panel_x = screen.get_width() - panel_width - margin
            panel_y = margin
        
        # Draw semi-transparent background
        surface = pygame.Surface((panel_width, panel_height))
        surface.set_alpha(self.alpha)
        surface.fill((20, 20, 30))
        screen.blit(surface, (panel_x, panel_y))
        
        # Border
        border_color = difficulty_data.get('color', (200, 200, 200))
        pygame.draw.rect(screen, border_color, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 32)
        title_text = title_font.render("⚔️ DUNGEON INFO", True, (255, 255, 255))
        screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # Difficulty
        diff_icon = difficulty_data.get('icon', '⚔️')
        diff_name = difficulty_data.get('name', 'Normal')
        diff_color = difficulty_data.get('color', (200, 200, 200))
        
        diff_text = font.render(f"{diff_icon} Difficulty: {diff_name}", True, diff_color)
        screen.blit(diff_text, (panel_x + 10, panel_y + 50))
        
        # Modifier
        if modifier_data:
            mod_icon = modifier_data.get('icon', '✨')
            mod_name = modifier_data.get('name', 'Unknown')
            mod_color = modifier_data.get('color', (255, 255, 255))
            
            mod_text = font.render(f"{mod_icon} {mod_name}", True, mod_color)
            screen.blit(mod_text, (panel_x + 10, panel_y + 75))
            
            # Description (smaller font)
            desc_font = pygame.font.Font(None, 18)
            description = modifier_data.get('description', '')
            desc_text = desc_font.render(description, True, (180, 180, 180))
            screen.blit(desc_text, (panel_x + 10, panel_y + 95))
    
    def update(self, dt: float):
        """Update fade timer"""
        if self.fade_timer > 0:
            self.fade_timer -= dt
        elif self.alpha > 0:
            self.alpha = max(0, self.alpha - 5)  # Fade out gradually


class SpeedRunTimerUI:
    """UI for speed run challenge timer"""
    
    def __init__(self):
        self.visible = False
        self.time_remaining = 0
        self.bonus_active = True
        
    def update(self, timer_data: Dict):
        """Update timer from dungeon variety system"""
        if timer_data.get('active', False):
            self.visible = True
            self.time_remaining = timer_data.get('time_remaining', 0)
            self.bonus_active = timer_data.get('bonus_active', True)
        else:
            self.visible = False
    
    def draw(self, screen):
        """Draw speed run timer"""
        if not self.visible:
            return
        
        # Position at top center
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate minutes and seconds
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        
        # Timer color based on time remaining
        if self.time_remaining > 180:  # > 3 minutes
            timer_color = (100, 255, 100)
        elif self.time_remaining > 60:  # > 1 minute
            timer_color = (255, 215, 0)
        else:
            timer_color = (255, 100, 100)
        
        # Draw timer background
        panel_width = 250
        panel_height = 60
        panel_x = (screen_width - panel_width) // 2
        panel_y = 20
        
        # Background
        surface = pygame.Surface((panel_width, panel_height))
        surface.set_alpha(200)
        surface.fill((20, 20, 30))
        screen.blit(surface, (panel_x, panel_y))
        
        # Border (pulsing if low time)
        if self.time_remaining < 30:
            # Pulsing effect
            pulse = int(abs(pygame.time.get_ticks() % 1000 - 500) / 500 * 100) + 155
            border_color = (pulse, 50, 50)
        else:
            border_color = timer_color
        
        pygame.draw.rect(screen, border_color, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Timer icon and text
        font = pygame.font.Font(None, 40)
        timer_text = font.render(f"⏱️ {minutes:02d}:{seconds:02d}", True, timer_color)
        text_rect = timer_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 25))
        screen.blit(timer_text, text_rect)
        
        # Bonus indicator
        if self.bonus_active:
            bonus_font = pygame.font.Font(None, 18)
            bonus_text = bonus_font.render("Bonus Active!", True, (255, 215, 0))
            bonus_rect = bonus_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 48))
            screen.blit(bonus_text, bonus_rect)


class TrapWarningUI:
    """UI for showing trap warnings"""
    
    def __init__(self):
        self.active_warnings = []  # List of (x, y, trap_type, timer)
        
    def add_warning(self, world_x: float, world_y: float, trap_type: str, duration: float = 0.5):
        """Add a trap warning indicator"""
        self.active_warnings.append({
            'x': world_x,
            'y': world_y,
            'trap_type': trap_type,
            'timer': duration
        })
    
    def update(self, dt: float):
        """Update warnings"""
        self.active_warnings = [w for w in self.active_warnings if w['timer'] > 0]
        for warning in self.active_warnings:
            warning['timer'] -= dt
    
    def draw(self, screen, camera_x: float, camera_y: float):
        """Draw trap warnings"""
        from dungeon_variety import TRAP_TYPES
        
        for warning in self.active_warnings:
            # Convert world coordinates to screen coordinates
            screen_x = warning['x'] - camera_x
            screen_y = warning['y'] - camera_y
            
            # Get trap color
            trap_data = TRAP_TYPES.get(warning['trap_type'], {})
            color = trap_data.get('color', (255, 0, 0))
            
            # Pulsing effect
            pulse = int((warning['timer'] / 0.5) * 255)
            alpha = max(50, min(255, pulse))
            
            # Draw circle warning
            radius = int(30 + (0.5 - warning['timer']) * 20)  # Expanding circle
            
            # Create surface for alpha blending
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*color, alpha), (radius, radius), radius, 3)
            screen.blit(surface, (screen_x - radius, screen_y - radius))
            
            # Draw exclamation mark
            font = pygame.font.Font(None, 24)
            text = font.render("!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_x, screen_y))
            screen.blit(text, text_rect)


class SecretDiscoveredUI:
    """UI for displaying secret room discovery"""
    
    def __init__(self):
        self.active = False
        self.timer = 0
        self.secret_name = ""
        self.description = ""
        
    def show(self, secret_room):
        """Show secret discovery message"""
        from dungeon_variety import SECRET_ROOM_TYPES
        
        self.active = True
        self.timer = 5.0  # Show for 5 seconds
        
        room_data = SECRET_ROOM_TYPES.get(secret_room.room_type, {})
        self.secret_name = room_data.get('name', 'Secret Room')
        self.description = room_data.get('description', 'You discovered a secret!')
    
    def update(self, dt: float):
        """Update timer"""
        if self.timer > 0:
            self.timer -= dt
        else:
            self.active = False
    
    def draw(self, screen):
        """Draw secret discovery message"""
        if not self.active:
            return
        
        # Center of screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Panel dimensions
        panel_width = 500
        panel_height = 150
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2 - 100
        
        # Background with glow effect
        surface = pygame.Surface((panel_width, panel_height))
        alpha = int(min(255, self.timer * 100))
        surface.set_alpha(alpha)
        surface.fill((40, 20, 60))
        screen.blit(surface, (panel_x, panel_y))
        
        # Golden border
        pygame.draw.rect(screen, (255, 215, 0), (panel_x, panel_y, panel_width, panel_height), 4)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("✨ SECRET DISCOVERED! ✨", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 40))
        screen.blit(title_text, title_rect)
        
        # Secret name
        name_font = pygame.font.Font(None, 32)
        name_text = name_font.render(self.secret_name, True, (200, 180, 255))
        name_rect = name_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 80))
        screen.blit(name_text, name_rect)
        
        # Description
        desc_font = pygame.font.Font(None, 20)
        desc_text = desc_font.render(self.description, True, (180, 180, 180))
        desc_rect = desc_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 110))
        screen.blit(desc_text, desc_rect)


class DungeonModifierSelectionUI:
    """UI for selecting dungeon difficulty and modifiers before entry"""
    
    def __init__(self):
        self.active = False
        self.selected_difficulty = "normal"
        self.selected_modifier = None
        self.selection_index = 0  # 0 = difficulty, 1+ = modifiers
        
    def show(self):
        """Show the selection UI"""
        self.active = True
        self.selection_index = 0
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selection_index = max(0, self.selection_index - 1)
            elif event.key == pygame.K_DOWN:
                max_index = len(DIFFICULTY_TIERS) + len(DUNGEON_MODIFIERS)
                self.selection_index = min(max_index, self.selection_index + 1)
            elif event.key == pygame.K_RETURN:
                self.active = False
                return {
                    'difficulty': self.selected_difficulty,
                    'modifier': self.selected_modifier
                }
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                return None
        
        return None
    
    def draw(self, screen):
        """Draw modifier selection UI"""
        if not self.active:
            return
        
        # Full screen overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Panel
        panel_width = 700
        panel_height = 600
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = (screen.get_height() - panel_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (200, 200, 200), (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("⚔️ SELECT DUNGEON OPTIONS", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 40))
        screen.blit(title_text, title_rect)
        
        # Difficulty section
        y_offset = panel_y + 100
        header_font = pygame.font.Font(None, 32)
        header_text = header_font.render("DIFFICULTY:", True, (255, 200, 100))
        screen.blit(header_text, (panel_x + 20, y_offset))
        y_offset += 40
        
        # List difficulties
        item_font = pygame.font.Font(None, 24)
        for i, (diff_id, diff_data) in enumerate(DIFFICULTY_TIERS.items()):
            selected = (self.selection_index == i)
            color = (255, 255, 100) if selected else (200, 200, 200)
            
            icon = diff_data.get('icon', '⚔️')
            name = diff_data.get('name', diff_id)
            desc = diff_data.get('description', '')
            
            text = item_font.render(f"{icon} {name} - {desc}", True, color)
            screen.blit(text, (panel_x + 40, y_offset))
            
            if selected:
                self.selected_difficulty = diff_id
                pygame.draw.rect(screen, color, (panel_x + 30, y_offset - 2, 640, 28), 2)
            
            y_offset += 35
        
        # Modifier section
        y_offset += 20
        header_text = header_font.render("MODIFIER (Optional):", True, (255, 200, 100))
        screen.blit(header_text, (panel_x + 20, y_offset))
        y_offset += 40
        
        # None option
        none_index = len(DIFFICULTY_TIERS)
        selected = (self.selection_index == none_index)
        color = (255, 255, 100) if selected else (200, 200, 200)
        text = item_font.render("❌ No Modifier (Standard dungeon)", True, color)
        screen.blit(text, (panel_x + 40, y_offset))
        if selected:
            self.selected_modifier = None
            pygame.draw.rect(screen, color, (panel_x + 30, y_offset - 2, 640, 28), 2)
        y_offset += 35
        
        # List modifiers (show first 3 to fit on screen)
        for i, (mod_id, mod_data) in enumerate(list(DUNGEON_MODIFIERS.items())[:3]):
            selected = (self.selection_index == none_index + 1 + i)
            color = (255, 255, 100) if selected else mod_data.get('color', (200, 200, 200))
            
            icon = mod_data.get('icon', '✨')
            name = mod_data.get('name', mod_id)
            
            text = item_font.render(f"{icon} {name}", True, color)
            screen.blit(text, (panel_x + 40, y_offset))
            
            if selected:
                self.selected_modifier = mod_id
                pygame.draw.rect(screen, color, (panel_x + 30, y_offset - 2, 640, 28), 2)
            
            y_offset += 35
        
        # Instructions
        inst_font = pygame.font.Font(None, 20)
        instructions = [
            "↑↓ Navigate  |  ENTER Confirm  |  ESC Cancel"
        ]
        y_offset = panel_y + panel_height - 40
        for inst in instructions:
            text = inst_font.render(inst, True, (150, 150, 150))
            text_rect = text.get_rect(center=(panel_x + panel_width // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 25


# Global instances
dungeon_info_ui = DungeonInfoUI()
speed_run_timer_ui = SpeedRunTimerUI()
trap_warning_ui = TrapWarningUI()
secret_discovered_ui = SecretDiscoveredUI()
dungeon_modifier_selection_ui = DungeonModifierSelectionUI()


def get_dungeon_info_ui():
    return dungeon_info_ui


def get_speed_run_timer_ui():
    return speed_run_timer_ui


def get_trap_warning_ui():
    return trap_warning_ui


def get_secret_discovered_ui():
    return secret_discovered_ui


def get_dungeon_modifier_selection_ui():
    return dungeon_modifier_selection_ui
