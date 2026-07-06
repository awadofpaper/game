"""
Key Bindings UI
User interface for customizing key bindings
"""

import pygame

class KeyBindingsUI:
    """UI for viewing and changing key bindings"""
    
    def __init__(self, key_bindings):
        self.key_bindings = key_bindings
        self.selected_category = 0
        self.selected_action = 0
        self.waiting_for_key = False
        self.waiting_slot = 0
        self.scroll_offset = 0
        
    def handle_event(self, event, screen):
        """Handle input events for the key bindings menu"""
        if event.type != pygame.KEYDOWN:
            return None
        
        if self.waiting_for_key:
            # Waiting for a key to bind
            if event.key == pygame.K_ESCAPE:
                # Cancel binding
                self.waiting_for_key = False
                return None
            elif event.key == pygame.K_BACKSPACE:
                # Unbind the key
                categories = self.key_bindings.get_categorized_actions()
                cat_names = list(categories.keys())
                actions = categories[cat_names[self.selected_category]]
                if self.selected_action < len(actions):
                    action = actions[self.selected_action]
                    self.key_bindings.unbind_key(action, self.waiting_slot)
                self.waiting_for_key = False
                return None
            else:
                # Bind the key
                categories = self.key_bindings.get_categorized_actions()
                cat_names = list(categories.keys())
                actions = categories[cat_names[self.selected_category]]
                if self.selected_action < len(actions):
                    action = actions[self.selected_action]
                    self.key_bindings.bind_key(action, event.key, self.waiting_slot)
                self.waiting_for_key = False
                return None
        
        # Normal navigation
        if event.key in [pygame.K_ESCAPE]:
            return "close"
        elif event.key in [pygame.K_LEFT, pygame.K_a]:
            self.selected_category = max(0, self.selected_category - 1)
            self.selected_action = 0
            self.scroll_offset = 0
        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
            categories = self.key_bindings.get_categorized_actions()
            self.selected_category = min(len(categories) - 1, self.selected_category + 1)
            self.selected_action = 0
            self.scroll_offset = 0
        elif event.key in [pygame.K_UP, pygame.K_w]:
            self.selected_action = max(0, self.selected_action - 1)
            # Scroll up if needed
            if self.selected_action < self.scroll_offset:
                self.scroll_offset = self.selected_action
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            categories = self.key_bindings.get_categorized_actions()
            cat_names = list(categories.keys())
            actions = categories[cat_names[self.selected_category]]
            self.selected_action = min(len(actions) - 1, self.selected_action + 1)
            # Scroll down if needed
            max_visible = 12
            if self.selected_action >= self.scroll_offset + max_visible:
                self.scroll_offset = self.selected_action - max_visible + 1
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_1]:
            # Start binding primary key (slot 0)
            self.waiting_for_key = True
            self.waiting_slot = 0
        elif event.key == pygame.K_2:
            # Start binding secondary key (slot 1)
            self.waiting_for_key = True
            self.waiting_slot = 1
        elif event.key == pygame.K_r:
            # Reset current action to default
            categories = self.key_bindings.get_categorized_actions()
            cat_names = list(categories.keys())
            actions = categories[cat_names[self.selected_category]]
            if self.selected_action < len(actions):
                action = actions[self.selected_action]
                if action in self.key_bindings.DEFAULT_BINDINGS:
                    self.key_bindings.bindings[action] = self.key_bindings.DEFAULT_BINDINGS[action].copy()
        elif event.key == pygame.K_F12:
            # Reset all to defaults
            self.key_bindings.reset_to_defaults()
        elif event.key == pygame.K_F5:
            # Save bindings
            self.key_bindings.save_bindings()
        
        return None
    
    def draw(self, screen, font):
        """Draw the key bindings configuration UI"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Key Bindings", True, (255, 215, 0))
        screen.blit(title, ((screen_width - title.get_width()) // 2, 30))
        
        # Instructions
        small_font = pygame.font.SysFont(None, 20)
        instructions = [
            "Arrow Keys/WASD: Navigate  |  1/Enter: Bind Primary  |  2: Bind Secondary",
            "Backspace: Unbind  |  R: Reset Action  |  F12: Reset All  |  F5: Save  |  ESC: Close"
        ]
        y = 80
        for instruction in instructions:
            text = small_font.render(instruction, True, (180, 180, 180))
            screen.blit(text, ((screen_width - text.get_width()) // 2, y))
            y += 22
        
        # Category tabs
        categories = self.key_bindings.get_categorized_actions()
        cat_names = list(categories.keys())
        
        tab_y = 130
        tab_width = screen_width // len(cat_names)
        for i, cat_name in enumerate(cat_names):
            color = (100, 150, 200) if i == self.selected_category else (60, 80, 100)
            pygame.draw.rect(screen, color, (i * tab_width, tab_y, tab_width, 40))
            pygame.draw.rect(screen, (255, 255, 255), (i * tab_width, tab_y, tab_width, 40), 2)
            
            tab_text = font.render(cat_name, True, (255, 255, 255))
            text_x = i * tab_width + (tab_width - tab_text.get_width()) // 2
            screen.blit(tab_text, (text_x, tab_y + 10))
        
        # Action list
        list_y = tab_y + 50
        list_height = screen_height - list_y - 100
        max_visible = 12
        
        actions = categories[cat_names[self.selected_category]]
        visible_actions = actions[self.scroll_offset:self.scroll_offset + max_visible]
        
        action_y = list_y
        item_height = 50
        
        for i, action in enumerate(visible_actions):
            actual_index = i + self.scroll_offset
            is_selected = actual_index == self.selected_action
            
            # Background
            bg_color = (80, 120, 160) if is_selected else (40, 50, 60)
            pygame.draw.rect(screen, bg_color, (100, action_y, screen_width - 200, item_height))
            pygame.draw.rect(screen, (150, 150, 150), (100, action_y, screen_width - 200, item_height), 2)
            
            # Action name and description
            name, description = self.key_bindings.get_action_info(action)
            name_text = font.render(name, True, (255, 255, 255))
            desc_text = small_font.render(description, True, (180, 180, 180))
            
            screen.blit(name_text, (120, action_y + 5))
            screen.blit(desc_text, (120, action_y + 28))
            
            # Current bindings
            keys = self.key_bindings.get_keys_for_action(action)
            key_x = screen_width - 280
            
            # Primary key
            primary_text = self.key_bindings.get_key_name(keys[0]) if len(keys) > 0 else "Unbound"
            if is_selected and self.waiting_for_key and self.waiting_slot == 0:
                primary_text = "Press key..."
                key_color = (255, 255, 0)
            else:
                key_color = (100, 255, 100) if len(keys) > 0 else (255, 100, 100)
            
            key_bg = pygame.Surface((110, 35), pygame.SRCALPHA)
            key_bg.fill((*key_color, 80))
            screen.blit(key_bg, (key_x, action_y + 7))
            pygame.draw.rect(screen, key_color, (key_x, action_y + 7, 110, 35), 2)
            
            key_text = small_font.render(primary_text, True, (255, 255, 255))
            screen.blit(key_text, (key_x + (110 - key_text.get_width()) // 2, action_y + 15))
            
            # Secondary key
            key_x += 120
            secondary_text = self.key_bindings.get_key_name(keys[1]) if len(keys) > 1 else "None"
            if is_selected and self.waiting_for_key and self.waiting_slot == 1:
                secondary_text = "Press key..."
                key_color = (255, 255, 0)
            else:
                key_color = (100, 200, 255) if len(keys) > 1 else (100, 100, 100)
            
            key_bg = pygame.Surface((110, 35), pygame.SRCALPHA)
            key_bg.fill((*key_color, 60))
            screen.blit(key_bg, (key_x, action_y + 7))
            pygame.draw.rect(screen, key_color, (key_x, action_y + 7, 110, 35), 2)
            
            key_text = small_font.render(secondary_text, True, (200, 200, 200))
            screen.blit(key_text, (key_x + (110 - key_text.get_width()) // 2, action_y + 15))
            
            action_y += item_height
        
        # Scroll indicator
        if len(actions) > max_visible:
            scroll_bar_height = max(30, int(list_height * max_visible / len(actions)))
            scroll_bar_y = list_y + int(list_height * self.scroll_offset / len(actions))
            pygame.draw.rect(screen, (100, 100, 100), (screen_width - 80, list_y, 20, list_height))
            pygame.draw.rect(screen, (200, 200, 200), (screen_width - 80, scroll_bar_y, 20, scroll_bar_height))
        
        # Bottom info
        bottom_y = screen_height - 80
        if self.waiting_for_key:
            info_text = small_font.render("Waiting for key input... (ESC to cancel, Backspace to unbind)", True, (255, 255, 0))
        else:
            info_text = small_font.render(f"Showing {self.scroll_offset + 1}-{min(self.scroll_offset + max_visible, len(actions))} of {len(actions)} actions", True, (180, 180, 180))
        screen.blit(info_text, ((screen_width - info_text.get_width()) // 2, bottom_y))


def get_keybindings_ui(key_bindings):
    """Get or create the key bindings UI instance"""
    return KeyBindingsUI(key_bindings)
