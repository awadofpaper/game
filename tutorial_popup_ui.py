"""
Tutorial Popup UI - Renders tutorial windows with multiple pages
"""

import pygame
import math

class TutorialPopupUI:
    """Displays tutorial information in popup windows"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.current_tutorial = None
        self.current_page = 0
        self.tutorial_data = None
        
        # Animation
        self.animation_progress = 0.0
        self.animation_speed = 0.15
        
        # Panel dimensions (60% of screen)
        self.panel_width = int(screen_width * 0.6)
        self.panel_height = int(screen_height * 0.65)
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # Colors
        self.colors = {
            'overlay': (0, 0, 0, 180),
            'panel_bg': (20, 30, 50, 245),
            'panel_border': (255, 215, 0),  # Gold
            'title_bg': (40, 50, 80),
            'text': (255, 255, 255),
            'text_dim': (180, 180, 200),
            'button': (60, 80, 120),
            'button_hover': (80, 100, 150),
            'button_text': (255, 255, 255),
            'progress': (100, 150, 255)
        }
        
        # Fonts (will be initialized when showing)
        self.font_title = None
        self.font_heading = None
        self.font_body = None
        self.font_small = None
        
        # Button states
        self.close_button_rect = None
        self.next_button_rect = None
        self.prev_button_rect = None
        self.skip_button_rect = None
        self.dont_show_rect = None
        self.dont_show_again = False
        
        # Mouse tracking
        self.mouse_pos = (0, 0)
    
    def show(self, tutorial_name, tutorial_data):
        """Display a tutorial"""
        self.active = True
        self.current_tutorial = tutorial_name
        self.tutorial_data = tutorial_data
        self.current_page = 0
        self.animation_progress = 0.0
        self.dont_show_again = False
        
        # Initialize fonts
        try:
            self.font_title = pygame.font.Font(None, 48)
            self.font_heading = pygame.font.Font(None, 36)
            self.font_body = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 22)
        except:
            self.font_title = pygame.font.SysFont('arial', 48, bold=True)
            self.font_heading = pygame.font.SysFont('arial', 36, bold=True)
            self.font_body = pygame.font.SysFont('arial', 28)
            self.font_small = pygame.font.SysFont('arial', 22)
    
    def close(self):
        """Close the tutorial"""
        self.active = False
        self.current_tutorial = None
        self.tutorial_data = None
    
    def handle_input(self, event, tutorial_manager):
        """Handle input events"""
        if not self.active:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check button clicks
                if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                    if self.dont_show_again and tutorial_manager:
                        tutorial_manager.mark_shown(self.current_tutorial)
                    self.close()
                    return True
                
                if self.next_button_rect and self.next_button_rect.collidepoint(event.pos):
                    self.next_page()
                    return True
                
                if self.prev_button_rect and self.prev_button_rect.collidepoint(event.pos):
                    self.previous_page()
                    return True
                
                if self.skip_button_rect and self.skip_button_rect.collidepoint(event.pos):
                    if tutorial_manager:
                        tutorial_manager.mark_shown(self.current_tutorial)
                    self.close()
                    return True
                
                if self.dont_show_rect and self.dont_show_rect.collidepoint(event.pos):
                    self.dont_show_again = not self.dont_show_again
                    return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.dont_show_again and tutorial_manager:
                    tutorial_manager.mark_shown(self.current_tutorial)
                self.close()
                return True
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.current_page < len(self.tutorial_data['pages']) - 1:
                    self.next_page()
                else:
                    if self.dont_show_again and tutorial_manager:
                        tutorial_manager.mark_shown(self.current_tutorial)
                    self.close()
                return True
            
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.next_page()
                return True
            
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.previous_page()
                return True
        
        return False
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < len(self.tutorial_data['pages']) - 1:
            self.current_page += 1
            self.animation_progress = 0.0
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.animation_progress = 0.0
    
    def update(self):
        """Update animation"""
        if self.active and self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
    
    def draw(self, screen):
        """Draw the tutorial popup"""
        if not self.active or not self.tutorial_data:
            return
        
        # Update animation
        self.update()
        
        # Ease-out animation
        t = self.animation_progress
        ease = 1 - (1 - t) ** 3  # Cubic ease-out
        
        # Draw overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.colors['overlay'])
        screen.blit(overlay, (0, 0))
        
        # Calculate animated panel position
        target_y = self.panel_y
        current_y = target_y + int((1 - ease) * 100)  # Slide down from above
        
        # Draw main panel with border
        border_rect = pygame.Rect(
            self.panel_x - 4,
            current_y - 4,
            self.panel_width + 8,
            self.panel_height + 8
        )
        pygame.draw.rect(screen, self.colors['panel_border'], border_rect, border_radius=12)
        
        panel_rect = pygame.Rect(self.panel_x, current_y, self.panel_width, self.panel_height)
        pygame.draw.rect(screen, self.colors['panel_bg'], panel_rect, border_radius=10)
        
        # Draw title bar
        title_rect = pygame.Rect(self.panel_x, current_y, self.panel_width, 70)
        pygame.draw.rect(screen, self.colors['title_bg'], title_rect, border_top_left_radius=10, border_top_right_radius=10)
        
        title_text = self.font_title.render(self.tutorial_data['title'], True, self.colors['panel_border'])
        title_x = self.panel_x + (self.panel_width - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, current_y + 15))
        
        # Draw page content
        page_data = self.tutorial_data['pages'][self.current_page]
        content_y = current_y + 90
        content_x = self.panel_x + 40
        content_width = self.panel_width - 80
        
        # Draw heading
        if 'heading' in page_data:
            heading_text = self.font_heading.render(page_data['heading'], True, self.colors['panel_border'])
            screen.blit(heading_text, (content_x, content_y))
            content_y += 50
        
        # Draw body text (word-wrapped)
        body_lines = self._wrap_text(page_data['text'], self.font_body, content_width)
        line_height = 35
        for line in body_lines:
            line_surface = self.font_body.render(line, True, self.colors['text'])
            screen.blit(line_surface, (content_x, content_y))
            content_y += line_height
        
        # Draw page indicator
        total_pages = len(self.tutorial_data['pages'])
        page_text = f"Page {self.current_page + 1} of {total_pages}"
        page_surface = self.font_small.render(page_text, True, self.colors['text_dim'])
        page_x = self.panel_x + (self.panel_width - page_surface.get_width()) // 2
        page_y = current_y + self.panel_height - 120
        screen.blit(page_surface, (page_x, page_y))
        
        # Draw navigation buttons
        button_y = current_y + self.panel_height - 90
        button_height = 40
        
        # Previous button
        if self.current_page > 0:
            prev_x = self.panel_x + 40
            self.prev_button_rect = pygame.Rect(prev_x, button_y, 120, button_height)
            is_hover = self.prev_button_rect.collidepoint(self.mouse_pos)
            button_color = self.colors['button_hover'] if is_hover else self.colors['button']
            pygame.draw.rect(screen, button_color, self.prev_button_rect, border_radius=8)
            prev_text = self.font_body.render("← Previous", True, self.colors['button_text'])
            text_x = prev_x + (120 - prev_text.get_width()) // 2
            text_y = button_y + (button_height - prev_text.get_height()) // 2
            screen.blit(prev_text, (text_x, text_y))
        else:
            self.prev_button_rect = None
        
        # Next/Close button
        if self.current_page < total_pages - 1:
            next_x = self.panel_x + self.panel_width - 160
            self.next_button_rect = pygame.Rect(next_x, button_y, 120, button_height)
            is_hover = self.next_button_rect.collidepoint(self.mouse_pos)
            button_color = self.colors['button_hover'] if is_hover else self.colors['button']
            pygame.draw.rect(screen, button_color, self.next_button_rect, border_radius=8)
            next_text = self.font_body.render("Next →", True, self.colors['button_text'])
            text_x = next_x + (120 - next_text.get_width()) // 2
            text_y = button_y + (button_height - next_text.get_height()) // 2
            screen.blit(next_text, (text_x, text_y))
        else:
            close_x = self.panel_x + self.panel_width - 160
            self.close_button_rect = pygame.Rect(close_x, button_y, 120, button_height)
            is_hover = self.close_button_rect.collidepoint(self.mouse_pos)
            button_color = self.colors['button_hover'] if is_hover else self.colors['button']
            pygame.draw.rect(screen, button_color, self.close_button_rect, border_radius=8)
            close_text = self.font_body.render("Got it!", True, self.colors['button_text'])
            text_x = close_x + (120 - close_text.get_width()) // 2
            text_y = button_y + (button_height - close_text.get_height()) // 2
            screen.blit(close_text, (text_x, text_y))
            self.next_button_rect = None
        
        # Draw "Don't show again" checkbox
        checkbox_y = current_y + self.panel_height - 40
        checkbox_x = self.panel_x + 40
        checkbox_size = 20
        self.dont_show_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
        
        # Checkbox background
        pygame.draw.rect(screen, (255, 255, 255), self.dont_show_rect, border_radius=3)
        pygame.draw.rect(screen, self.colors['panel_border'], self.dont_show_rect, 2, border_radius=3)
        
        # Checkmark if checked
        if self.dont_show_again:
            checkmark_points = [
                (checkbox_x + 4, checkbox_y + 10),
                (checkbox_x + 8, checkbox_y + 14),
                (checkbox_x + 16, checkbox_y + 6)
            ]
            pygame.draw.lines(screen, (0, 200, 0), False, checkmark_points, 3)
        
        # Checkbox label
        checkbox_label = self.font_small.render("Don't show this tutorial again", True, self.colors['text_dim'])
        screen.blit(checkbox_label, (checkbox_x + 30, checkbox_y - 2))
        
        # Draw skip button (small, top-right)
        skip_x = self.panel_x + self.panel_width - 120
        skip_y = current_y + 10
        self.skip_button_rect = pygame.Rect(skip_x, skip_y, 100, 30)
        is_hover = self.skip_button_rect.collidepoint(self.mouse_pos)
        skip_color = self.colors['text'] if is_hover else self.colors['text_dim']
        skip_text = self.font_small.render("Skip (ESC)", True, skip_color)
        screen.blit(skip_text, (skip_x + 10, skip_y + 5))
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        lines = []
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                lines.append('')
                continue
            
            words = paragraph.split(' ')
            current_line = ''
            
            for word in words:
                test_line = current_line + word + ' '
                test_width = font.size(test_line)[0]
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.rstrip())
                    current_line = word + ' '
            
            if current_line:
                lines.append(current_line.rstrip())
        
        return lines
