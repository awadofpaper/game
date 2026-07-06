"""
Dialogue UI - Full-screen dialogue window with NPC portraits
"""

import pygame
import time
from dialogue_system import DialogueNodeType

class DialogueUI:
    """Full-screen dialogue interface"""
    
    def __init__(self):
        self.active = False
        self.current_npc_id = None  # Track current NPC for shop system
        self.selected_choice = 0
        self.text_reveal_speed = 2  # Characters per frame
        self.revealed_text = ""
        self.reveal_index = 0
        self.full_text = ""
        self.text_fully_revealed = False
        
        # Colors
        self.bg_color = (15, 15, 25, 240)
        self.panel_color = (30, 30, 50)
        self.border_color = (100, 100, 150)
        self.npc_name_color = (255, 255, 180)
        self.text_color = (255, 255, 255)
        self.choice_color = (220, 220, 220)
        self.choice_selected_color = (255, 255, 100)
        self.choice_locked_color = (120, 120, 120)
        self.requirement_color = (255, 150, 150)
        
    def start_dialogue(self, dialogue_manager, npc_id=None):
        """Start displaying dialogue"""
        self.active = True
        self.current_npc_id = npc_id  # Store NPC ID for shop system
        self.selected_choice = 0
        self.reveal_index = 0
        self.revealed_text = ""
        self.text_fully_revealed = False
        self._update_text(dialogue_manager)
    
    def close(self):
        """Close the dialogue UI"""
        self.active = False
        self.current_npc_id = None

    def _update_text(self, dialogue_manager):
        """Update the text to display"""
        self.full_text = dialogue_manager.get_current_text() or ""
        self.reveal_index = 0
        self.revealed_text = ""
        self.text_fully_revealed = False
    
    def update(self, dialogue_manager):
        """Update text reveal animation"""
        if not self.text_fully_revealed and self.reveal_index < len(self.full_text):
            # Reveal more characters
            self.reveal_index = min(self.reveal_index + self.text_reveal_speed, len(self.full_text))
            self.revealed_text = self.full_text[:self.reveal_index]
            
            if self.reveal_index >= len(self.full_text):
                self.text_fully_revealed = True
    
    def skip_text_reveal(self):
        """Instantly reveal all text"""
        self.revealed_text = self.full_text
        self.reveal_index = len(self.full_text)
        self.text_fully_revealed = True
    
    def draw(self, screen, dialogue_manager, player):
        """Draw the dialogue window"""
        if not self.active or not dialogue_manager.is_in_conversation():
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Full-screen semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Main dialogue panel (bottom 40% of screen)
        panel_height = int(screen_height * 0.45)
        panel_y = screen_height - panel_height
        panel_margin = 40
        panel_width = screen_width - (panel_margin * 2)
        panel_x = panel_margin
        
        # Draw panel background
        pygame.draw.rect(screen, self.panel_color, 
                        (panel_x, panel_y, panel_width, panel_height), 
                        border_radius=15)
        pygame.draw.rect(screen, self.border_color, 
                        (panel_x, panel_y, panel_width, panel_height), 
                        3, border_radius=15)
        
        # NPC Portrait area (left side)
        portrait_size = 180
        portrait_x = panel_x + 30
        portrait_y = panel_y + 30
        
        # Draw portrait background
        pygame.draw.rect(screen, (40, 40, 60), 
                        (portrait_x, portrait_y, portrait_size, portrait_size), 
                        border_radius=10)
        pygame.draw.rect(screen, self.border_color, 
                        (portrait_x, portrait_y, portrait_size, portrait_size), 
                        2, border_radius=10)
        
        # Draw NPC portrait with styled design
        npc = dialogue_manager.current_npc
        if npc:
            # Get NPC color and create gradient effect
            portrait_color = getattr(npc, 'color', (100, 150, 200))
            lighter_color = tuple(min(255, c + 40) for c in portrait_color)
            darker_color = tuple(max(0, c - 40) for c in portrait_color)
            
            center_x = portrait_x + portrait_size // 2
            center_y = portrait_y + portrait_size // 2
            
            # Draw layered circles for depth
            pygame.draw.circle(screen, darker_color, (center_x + 2, center_y + 2), portrait_size // 3)  # Shadow
            pygame.draw.circle(screen, portrait_color, (center_x, center_y), portrait_size // 3)  # Base
            pygame.draw.circle(screen, lighter_color, (center_x - 5, center_y - 5), portrait_size // 6)  # Highlight
            
            # Draw NPC initials in stylized font
            initial_font = pygame.font.SysFont(None, 72, bold=True)
            npc_name = getattr(npc, 'name', 'NPC')
            initials = ''.join([word[0] for word in npc_name.split()[:2]]).upper()
            initial_text = initial_font.render(initials, True, (255, 255, 255))
            screen.blit(initial_text, 
                       (center_x - initial_text.get_width()//2, 
                        center_y - initial_text.get_height()//2))
        
        # NPC Name below portrait
        name_font = pygame.font.SysFont(None, 28)
        npc_name_text = name_font.render(getattr(npc, 'name', 'Unknown'), True, self.npc_name_color)
        screen.blit(npc_name_text, 
                   (portrait_x + portrait_size//2 - npc_name_text.get_width()//2, 
                    portrait_y + portrait_size + 10))
        
        # Reputation indicator
        if npc:
            rep_level = dialogue_manager.reputation_system.get_npc_reputation_level(npc.id)
            rep_font = pygame.font.SysFont(None, 18)
            
            # Color based on reputation
            if rep_level in ['Revered', 'Exalted']:
                rep_color = (100, 255, 100)
            elif rep_level in ['Honored', 'Friendly']:
                rep_color = (150, 255, 150)
            elif rep_level in ['Hostile', 'Hated']:
                rep_color = (255, 100, 100)
            else:
                rep_color = (200, 200, 200)
            
            rep_text = rep_font.render(rep_level, True, rep_color)
            screen.blit(rep_text, 
                       (portrait_x + portrait_size//2 - rep_text.get_width()//2, 
                        portrait_y + portrait_size + 35))
        
        # Dialogue text area (right side)
        text_x = portrait_x + portrait_size + 40
        text_y = panel_y + 30
        text_width = panel_width - (portrait_size + 100)
        text_height = 180
        
        # Current node type
        current_node = dialogue_manager.current_node
        
        if current_node and current_node.type == DialogueNodeType.TEXT:
            # Display NPC dialogue
            dialogue_font = pygame.font.SysFont(None, 26)
            
            # Word wrap the revealed text
            words = self.revealed_text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if dialogue_font.size(test_line)[0] <= text_width - 20:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Draw text lines
            line_y = text_y
            for line in lines[:7]:  # Max 7 lines
                line_text = dialogue_font.render(line, True, self.text_color)
                screen.blit(line_text, (text_x, line_y))
                line_y += 28
            
            # Show continuation indicator if text is still revealing
            if not self.text_fully_revealed:
                indicator = dialogue_font.render("...", True, (150, 150, 150))
                screen.blit(indicator, (text_x + text_width - 50, text_y + text_height - 30))
            else:
                # Show "Press SPACE to continue" when text is fully revealed
                continue_font = pygame.font.SysFont(None, 20)
                continue_text = continue_font.render("[SPACE] Continue", True, (180, 180, 180))
                screen.blit(continue_text, (panel_x + panel_width - continue_text.get_width() - 30, 
                                           panel_y + panel_height - 30))
        
        elif current_node and current_node.type == DialogueNodeType.CHOICE:
            # Display NPC's last text (stored from previous node)
            if hasattr(dialogue_manager, '_last_text'):
                dialogue_font = pygame.font.SysFont(None, 24)
                last_text = dialogue_font.render(dialogue_manager._last_text, True, (220, 220, 220))
                screen.blit(last_text, (text_x, text_y))
            
            # Display player choices
            choices = dialogue_manager.get_current_choices(player)
            choice_y = panel_y + panel_height - 260
            choice_font = pygame.font.SysFont(None, 24)
            
            # Draw "Your Response:" label
            response_label = choice_font.render("Your Response:", True, self.npc_name_color)
            screen.blit(response_label, (text_x, choice_y - 30))
            
            for i, choice_data in enumerate(choices[:8]):  # Max 8 choices
                choice = choice_data['choice']
                available = choice_data['available']
                requirement_text = choice_data['requirement_text']
                
                choice_y_pos = choice_y + i * 32
                
                # Choice background
                if i == self.selected_choice:
                    choice_bg_color = (60, 60, 100)
                    pygame.draw.rect(screen, choice_bg_color, 
                                   (text_x - 5, choice_y_pos - 2, text_width, 28), 
                                   border_radius=5)
                
                # Choice text
                if available:
                    if i == self.selected_choice:
                        color = self.choice_selected_color
                        prefix = "► "
                    else:
                        color = self.choice_color
                        prefix = "  "
                else:
                    color = self.choice_locked_color
                    prefix = "✗ "
                
                choice_text = choice_font.render(prefix + choice.text, True, color)
                screen.blit(choice_text, (text_x, choice_y_pos))
                
                # Show requirements if locked
                if not available and requirement_text:
                    req_font = pygame.font.SysFont(None, 18)
                    req_text = req_font.render(requirement_text, True, self.requirement_color)
                    screen.blit(req_text, (text_x + text_width - req_text.get_width(), choice_y_pos + 2))
            
            # Controls hint
            controls_font = pygame.font.SysFont(None, 20)
            controls_text = controls_font.render("[↑↓] Select | [SPACE/ENTER] Choose | [ESC] Walk away", 
                                                True, (180, 180, 180))
            screen.blit(controls_text, (panel_x + panel_width - controls_text.get_width() - 30, 
                                       panel_y + panel_height - 30))
    
    def handle_input(self, event, dialogue_manager, player, game_time=None):
        """Handle keyboard input for dialogue"""
        if not self.active or not dialogue_manager.is_in_conversation():
            return None
        
        current_node = dialogue_manager.current_node
        
        if event.type == pygame.KEYDOWN:
            # ESC to walk away (end conversation)
            if event.key == pygame.K_ESCAPE:
                dialogue_manager.end_conversation()
                self.active = False
                return "walked_away"
            
            # Handle TEXT nodes
            if current_node and current_node.type == DialogueNodeType.TEXT:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if not self.text_fully_revealed:
                        # Skip to end of text reveal
                        self.skip_text_reveal()
                    else:
                        # Move to next node
                        # Store current text for reference
                        dialogue_manager._last_text = self.full_text[:60] + "..." if len(self.full_text) > 60 else self.full_text
                        
                        # Advance to next node in dialogue tree
                        if dialogue_manager.advance_conversation():
                            self.selected_choice = 0
                            self._update_text(dialogue_manager)
                            return "advanced"
                        else:
                            # No next node, conversation ended
                            # Return the node ID we were on before ending
                            ended_at_node = current_node.id if current_node else None
                            self.active = False
                            return {"type": "ended", "node_id": ended_at_node}
            
            # Handle CHOICE nodes
            elif current_node and current_node.type == DialogueNodeType.CHOICE:
                choices = dialogue_manager.get_current_choices(player)
                
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_choice = (self.selected_choice - 1) % len(choices)
                
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_choice = (self.selected_choice + 1) % len(choices)
                
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    # Get the selected choice before processing
                    selected_choice_data = choices[self.selected_choice]
                    selected_choice = selected_choice_data['choice']
                    
                    # Choose the selected option
                    success, result = dialogue_manager.choose_option(self.selected_choice, player)
                    
                    if success:
                        # Handle gatherer NPC consequences if applicable
                        if selected_choice.consequences and dialogue_manager.current_npc:
                            # Check if this is a gatherer NPC
                            npc = dialogue_manager.current_npc
                            is_gatherer = hasattr(npc, 'gatherer_type')
                            
                            if is_gatherer and game_time:
                                # Import and call consequence handler
                                from gatherer_dialogue import handle_dialogue_consequence
                                consequence_result = handle_dialogue_consequence(
                                    selected_choice.consequences,
                                    npc,
                                    player,
                                    game_time
                                )
                                
                                # Process consequence results
                                if consequence_result:
                                    if consequence_result.get('combat'):
                                        self.active = False
                                        dialogue_manager.end_conversation()
                                        return {'type': 'gatherer_combat', 'npc': npc, 'message': consequence_result.get('message', '')}
                                    elif consequence_result.get('warning'):
                                        # Continue dialogue but return warning
                                        return {'type': 'gatherer_warning', 'npc': npc, 'message': consequence_result.get('message', '')}
                                    elif consequence_result.get('success'):
                                        # Continue with message
                                        return {'type': 'gatherer_success', 'message': consequence_result.get('message', '')}
                        
                        if result == "shop":
                            return "open_shop"
                        elif result == "Conversation ended":
                            self.active = False
                            return "ended"
                        elif result in ["quest_accepted_auto_close", "quest_completed_auto_close"]:
                            # Auto-close dialogue after quest acceptance/completion
                            dialogue_manager.end_conversation()
                            self.active = False
                            return "auto_closed"
                        else:
                            # Update to new node
                            self.selected_choice = 0
                            self._update_text(dialogue_manager)
                            return result
                    else:
                        return f"failed: {result}"
        
        return None


class DialogueHistoryUI:
    """UI for viewing conversation history"""
    
    def __init__(self):
        self.active = False
        self.scroll_offset = 0
    
    def toggle(self):
        """Toggle history UI"""
        self.active = not self.active
        if self.active:
            self.scroll_offset = 0
    
    def draw(self, screen, font, dialogue_manager):
        """Draw conversation history"""
        if not self.active:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Panel
        panel_width = 600
        panel_height = 500
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Panel background
        pygame.draw.rect(screen, (30, 30, 50), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 150), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)
        
        # Title
        title_font = pygame.font.SysFont(None, 40)
        title = title_font.render("Conversation History", True, (255, 255, 180))
        screen.blit(title, (panel_x + panel_width//2 - title.get_width()//2, panel_y + 15))
        
        # History entries
        history = dialogue_manager.conversation_history
        
        if not history:
            empty_font = pygame.font.SysFont(None, 28)
            empty_text = empty_font.render("No conversations yet", True, (150, 150, 150))
            screen.blit(empty_text, (panel_x + panel_width//2 - empty_text.get_width()//2, 
                                    panel_y + panel_height//2))
        else:
            entry_y = panel_y + 70
            entry_font = pygame.font.SysFont(None, 22)
            time_font = pygame.font.SysFont(None, 18)
            
            visible_entries = history[self.scroll_offset:self.scroll_offset + 10]
            
            for entry in visible_entries:
                # NPC name
                name_text = entry_font.render(f"• {entry['npc_name']}", True, (255, 255, 255))
                screen.blit(name_text, (panel_x + 30, entry_y))
                
                # Time ago
                time_ago = time.time() - entry['timestamp']
                if time_ago < 60:
                    time_str = "Just now"
                elif time_ago < 3600:
                    time_str = f"{int(time_ago / 60)} min ago"
                else:
                    time_str = f"{int(time_ago / 3600)} hr ago"
                
                time_text = time_font.render(time_str, True, (180, 180, 180))
                screen.blit(time_text, (panel_x + panel_width - time_text.get_width() - 30, entry_y + 2))
                
                entry_y += 40
        
        # Instructions
        instr_font = pygame.font.SysFont(None, 20)
        instr_text = instr_font.render("[H] Close | [↑↓] Scroll", True, (180, 180, 180))
        screen.blit(instr_text, (panel_x + panel_width//2 - instr_text.get_width()//2, 
                                panel_y + panel_height - 30))
    
    def handle_input(self, event):
        """Handle input for history UI"""
        if not self.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h or event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.scroll_offset += 1
