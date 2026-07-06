"""
Cooking System - Fire placement and cooking mechanics
"""

import pygame
import random
import logging
import math
from skills_system import COOKING_RESOURCES

logger = logging.getLogger(__name__)


class Fire:
    """A campfire for cooking"""
    
    def __init__(self, x, y, game_time):
        self.x = x
        self.y = y
        self.placed_time = game_time.get_total_minutes()
        self.duration_minutes = 5 * 60  # Burns for 5 game hours (300 minutes)
        self.size = 24
        
        # Animation
        self.flame_offset = 0
        self.animation_timer = 0
        self.flicker_offset = random.uniform(0, 3.14)
        
    def is_active(self, game_time):
        """Check if fire is still burning"""
        elapsed_minutes = game_time.get_total_minutes() - self.placed_time
        return elapsed_minutes < self.duration_minutes
    
    def get_remaining_time(self, game_time):
        """Get remaining burn time in hours"""
        elapsed_minutes = game_time.get_total_minutes() - self.placed_time
        remaining_minutes = max(0, self.duration_minutes - elapsed_minutes)
        return remaining_minutes / 60.0  # Convert to hours
    
    def update(self, dt):
        """Update fire animation"""
        self.animation_timer += dt * 8  # Speed of animation
        self.flame_offset = math.sin(self.animation_timer + self.flicker_offset) * 4
    
    def draw(self, screen, camera):
        """Draw animated fire"""
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        
        # Draw fire base (darker orange)
        base_rect = pygame.Rect(
            screen_x - self.size // 2,
            screen_y - self.size // 2,
            self.size,
            self.size
        )
        pygame.draw.ellipse(screen, (139, 69, 19), base_rect)  # Brown/dark orange
        
        # Draw main flame (bright orange with flicker)
        flame_height = self.size + int(self.flame_offset)
        flame_rect = pygame.Rect(
            screen_x - self.size // 3,
            screen_y - flame_height // 2,
            self.size // 1.5,
            flame_height
        )
        pygame.draw.ellipse(screen, (255, 140, 0), flame_rect)  # Orange
        
        # Draw inner flame (yellow with more flicker)
        inner_height = flame_height * 0.6
        inner_offset = math.sin(self.animation_timer * 1.5 + self.flicker_offset) * 3
        inner_rect = pygame.Rect(
            screen_x - self.size // 4,
            screen_y - inner_height // 2 + inner_offset,
            self.size // 2,
            inner_height
        )
        pygame.draw.ellipse(screen, (255, 200, 0), inner_rect)  # Yellow


class FireManager:
    """Manages player's campfire"""
    
    def __init__(self):
        self.fire = None  # Only one fire at a time
        
    def can_place_fire(self, player):
        """Check if player can place a fire"""
        if self.fire is not None:
            return False, "You already have an active cooking fire. Wait for it to burn out."
        
        stick_count = player.get_stick_count()
        if stick_count < 2:
            return False, f"Cannot build fire: need 2 sticks (you have {stick_count})"
        
        return True, "Can place fire"
    
    def place_fire(self, player, game_time):
        """Place a fire at player's location"""
        can_place, message = self.can_place_fire(player)
        
        if not can_place:
            return False, message
        
        # Consume sticks
        player.consume_sticks(2)
        
        # Create fire
        self.fire = Fire(player.x, player.y, game_time)
        logger.info(f"[COOKING] Player placed fire at ({player.x}, {player.y})")
        
        return True, "Fire built! (lasts 5 game hours)"
    
    def get_nearby_fire(self, player_x, player_y, max_distance=60):
        """Check if player is near their fire"""
        if self.fire is None:
            return None
        
        dx = player_x - self.fire.x
        dy = player_y - self.fire.y
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= max_distance:
            return self.fire
        return None
    
    def update(self, dt, game_time):
        """Update fire (check expiration, animate)"""
        if self.fire is not None:
            # Check if fire expired
            if not self.fire.is_active(game_time):
                logger.info("[COOKING] Fire burned out")
                self.fire = None
            else:
                self.fire.update(dt)
    
    def draw(self, screen, camera):
        """Draw active fire"""
        if self.fire is not None:
            self.fire.draw(screen, camera)


class CookingUI:
    """UI for cooking raw food"""
    
    def __init__(self, config):
        self.config = config
        self.active = False
        self.selected_item = 0
        self.message = ""
        self.message_timer = 0
        self.is_town_range = False  # Cooking at town vs campfire
        self.on_cook_success = None  # Callback for achievement tracking
        
    def open(self, is_town_range=False):
        """Open cooking menu"""
        self.active = True
        self.selected_item = 0
        self.message = ""
        self.message_timer = 0
        self.is_town_range = is_town_range
        location = "town range" if is_town_range else "campfire"
        logger.info(f"[COOKING UI] Opened at {location}")
    
    def close(self):
        """Close cooking menu"""
        self.active = False
        logger.info("[COOKING UI] Closed")
    
    def get_cookable_items(self, player):
        """Get list of raw food player can cook"""
        cookable = []
        
        for item_name, item_data in COOKING_RESOURCES.items():
            raw_name = f"raw_{item_name}"
            if raw_name in player.inventory and player.inventory[raw_name] > 0:
                cookable.append({
                    'raw_name': raw_name,
                    'cooked_name': item_name,
                    'count': player.inventory[raw_name],
                    'data': item_data
                })
        
        return cookable
    
    def calculate_burn_chance(self, player, item_data):
        """Calculate chance to burn food (0.0 to 1.0)"""
        cooking_level = player.skills_manager.get_level('Cooking')
        burn_level = item_data['burn_level']
        required_level = item_data['level']
        
        # Linear decrease: 100% burn at required level, 0% burn at burn level
        if cooking_level >= burn_level:
            return 0.0  # Never burns at or above burn level
        
        if cooking_level < required_level:
            return 1.0  # Always burns below required level
        
        # Linear interpolation between required and burn level
        progress = (cooking_level - required_level) / (burn_level - required_level)
        return 1.0 - progress
    
    def cook_item(self, player, item_info):
        """Attempt to cook a raw item"""
        raw_name = item_info['raw_name']
        cooked_name = item_info['cooked_name']
        item_data = item_info['data']
        
        # Check if player has the item
        if raw_name not in player.inventory or player.inventory[raw_name] <= 0:
            return False, "No raw food to cook"
        
        # Check cooking level requirement
        required_level = item_data['level']
        cooking_level = player.skills_manager.get_level('Cooking')
        if cooking_level < required_level:
            return False, f"Need Cooking {required_level}"
        
        # Remove raw item
        player.inventory[raw_name] -= 1
        if player.inventory[raw_name] <= 0:
            del player.inventory[raw_name]
        
        # Calculate burn chance
        burn_chance = self.calculate_burn_chance(player, item_data)
        
        # Roll for success
        if random.random() < burn_chance:
            # Burnt!
            burnt_name = f"burnt_{cooked_name}"
            player.inventory[burnt_name] = player.inventory.get(burnt_name, 0) + 1
            
            # Give 1 XP for trying
            player.skills_manager.add_xp('Cooking', 1)
            
            burn_pct = int(burn_chance * 100)
            logger.info(f"[COOKING] Player burnt {cooked_name} ({burn_pct}% chance)")
            return True, f"You burnt the {cooked_name}! (+1 Cooking XP)"
        else:
            # Success!
            player.inventory[cooked_name] = player.inventory.get(cooked_name, 0) + 1
            
            # Give full XP
            xp_reward = item_data['xp']
            levels_gained = player.skills_manager.add_xp('Cooking', xp_reward)
            
            level_up_text = ""
            if levels_gained:
                level_up_text = f" LEVEL {levels_gained[-1]}!"
            
            # Track cooking for achievements (meals_cooked stat should be tracked by caller)
            
            logger.info(f"[COOKING] Player cooked {cooked_name} (+{xp_reward} XP)")
            return True, f"Cooked {cooked_name}! (+{xp_reward} Cooking XP){level_up_text}"
    
    def handle_input(self, event, player):
        """Handle keyboard input for cooking menu"""
        if not self.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_c:
                self.close()
            
            elif event.key == pygame.K_UP:
                cookable = self.get_cookable_items(player)
                if cookable:
                    self.selected_item = (self.selected_item - 1) % len(cookable)
            
            elif event.key == pygame.K_DOWN:
                cookable = self.get_cookable_items(player)
                if cookable:
                    self.selected_item = (self.selected_item + 1) % len(cookable)
            
            elif event.key == pygame.K_RETURN:
                cookable = self.get_cookable_items(player)
                if cookable and self.selected_item < len(cookable):
                    success, message = self.cook_item(player, cookable[self.selected_item])
                    self.message = message
                    self.message_timer = 180 if success else 120
                    
                    # Trigger achievement callback on successful cook
                    if success and self.on_cook_success and "burnt" not in message.lower():
                        self.on_cook_success()
    
    def draw(self, screen, player):
        """Draw cooking menu"""
        if not self.active:
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
        menu_bg.fill((30, 25, 20, 240))
        pygame.draw.rect(menu_bg, (255, 140, 0), (0, 0, menu_width, menu_height), 4)  # Orange border
        screen.blit(menu_bg, (menu_x, menu_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        location = "Town Range" if self.is_town_range else "Campfire"
        title = title_font.render(f"Cooking - {location}", True, (255, 180, 80))
        screen.blit(title, (menu_x + menu_width // 2 - title.get_width() // 2, menu_y + 20))
        
        # Player cooking level
        level_font = pygame.font.SysFont(None, 28)
        cooking_level = player.skills_manager.get_level('Cooking')
        level_text = level_font.render(f"Cooking Level: {cooking_level}", True, (200, 180, 150))
        screen.blit(level_text, (menu_x + 20, menu_y + 80))
        
        # Get cookable items
        cookable = self.get_cookable_items(player)
        
        if not cookable:
            no_food_font = pygame.font.SysFont(None, 36)
            no_food = no_food_font.render("No raw food to cook!", True, (200, 150, 100))
            screen.blit(no_food, (menu_x + menu_width // 2 - no_food.get_width() // 2, menu_y + 200))
        else:
            # Draw cookable items
            content_y = menu_y + 130
            self._draw_cookable_items(screen, menu_x, content_y, menu_width, cookable, player)
        
        # Instructions
        instr_y = menu_y + menu_height - 60
        instr_font = pygame.font.SysFont(None, 24)
        instructions = ["↑↓: Select", "ENTER: Cook", "ESC/C: Close"]
        
        instr_x = menu_x + 20
        for instruction in instructions:
            instr = instr_font.render(instruction, True, (200, 180, 150))
            screen.blit(instr, (instr_x, instr_y))
            instr_x += 200
        
        # Message
        if self.message:
            msg_font = pygame.font.SysFont(None, 28)
            
            # Color based on message
            if "burnt" in self.message.lower():
                msg_color = (255, 100, 100)
            elif "LEVEL" in self.message:
                msg_color = (255, 215, 0)
            else:
                msg_color = (100, 255, 100)
            
            msg_surf = msg_font.render(self.message, True, msg_color)
            
            msg_x = (self.config.SCREEN_WIDTH - msg_surf.get_width()) // 2
            msg_y = menu_y + menu_height + 20
            
            msg_bg = pygame.Surface((msg_surf.get_width() + 40, msg_surf.get_height() + 20), pygame.SRCALPHA)
            msg_bg.fill((20, 20, 20, 220))
            pygame.draw.rect(msg_bg, msg_color, (0, 0, msg_bg.get_width(), msg_bg.get_height()), 2)
            
            screen.blit(msg_bg, (msg_x - 20, msg_y - 10))
            screen.blit(msg_surf, (msg_x, msg_y))
    
    def _draw_cookable_items(self, screen, menu_x, start_y, menu_width, cookable, player):
        """Draw list of cookable items"""
        item_font = pygame.font.SysFont(None, 28)
        detail_font = pygame.font.SysFont(None, 20)
        
        visible_count = 5
        scroll_offset = max(0, self.selected_item - visible_count + 1)
        
        for i in range(scroll_offset, min(scroll_offset + visible_count, len(cookable))):
            item_info = cookable[i]
            is_selected = (i == self.selected_item)
            
            y_pos = start_y + (i - scroll_offset) * 70
            
            # Item background
            bg_color = (80, 60, 40, 200) if is_selected else (50, 40, 30, 150)
            bg = pygame.Surface((menu_width - 40, 65), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                pygame.draw.rect(bg, (255, 140, 0), (0, 0, menu_width - 40, 65), 3)
            
            screen.blit(bg, (menu_x + 20, y_pos))
            
            # Item name
            display_name = item_info['cooked_name'].replace('_', ' ').title()
            count_text = f" x{item_info['count']}"
            name = item_font.render(f"{display_name}{count_text}", True, (255, 255, 255))
            screen.blit(name, (menu_x + 35, y_pos + 8))
            
            # Requirements and burn chance
            item_data = item_info['data']
            required_level = item_data['level']
            burn_level = item_data['burn_level']
            xp_reward = item_data['xp']
            heals = item_data['heals']
            
            cooking_level = player.skills_manager.get_level('Cooking')
            burn_chance = self.calculate_burn_chance(player, item_data)
            burn_pct = int(burn_chance * 100)
            
            # Details line
            if cooking_level < required_level:
                detail_text = f"Req: Cooking {required_level} | You: {cooking_level}"
                detail_color = (255, 100, 100)
            else:
                detail_text = f"Level {required_level} | Burn: {burn_pct}% | XP: {xp_reward} | Heals: {heals}"
                
                # Color based on burn chance
                if burn_pct == 0:
                    detail_color = (100, 255, 100)
                elif burn_pct < 50:
                    detail_color = (200, 200, 100)
                else:
                    detail_color = (255, 150, 100)
            
            detail = detail_font.render(detail_text, True, detail_color)
            screen.blit(detail, (menu_x + 35, y_pos + 38))
