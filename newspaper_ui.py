"""
Newspaper UI - Readable newspaper interface with multiple sections
"""

import pygame
from typing import Optional
from newspaper_system import Newspaper, NewsArticle


class NewspaperUI:
    """Interactive UI for reading newspapers"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        
        # Current state
        self.current_newspaper = None
        self.current_section = 'front_page'  # front_page, obituary, politics, society, market, world
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # UI dimensions (newspaper style - tall and narrow)
        self.width = 700
        self.height = 800
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Fonts (newspaper style)
        self.title_font = pygame.font.SysFont("Times New Roman", 42, bold=True)
        self.header_font = pygame.font.SysFont("Times New Roman", 28, bold=True)
        self.subheader_font = pygame.font.SysFont("Times New Roman", 20, bold=True)
        self.text_font = pygame.font.SysFont("Georgia", 16)
        self.small_font = pygame.font.SysFont("Georgia", 14)
        
        # Colors (classic newspaper)
        self.paper_color = (245, 240, 230)  # Aged paper
        self.text_color = (20, 20, 20)  # Near black
        self.headline_color = (0, 0, 0)  # Pure black
        self.section_color = (60, 60, 60)  # Dark gray
        self.border_color = (100, 100, 100)  # Medium gray
        self.highlight_color = (200, 200, 150)  # Pale yellow highlight
        
        # Section tabs
        self.sections = [
            ('front_page', '📰 Front Page'),
            ('market', '💰 Market'),
            ('politics', '🏛️ Politics'),
            ('society', '👥 Society'),
            ('obituary', '🕯️ Obituaries'),
            ('world', '🌍 World')
        ]
        self.section_tabs = []
        self._create_section_tabs()
    
    def _create_section_tabs(self):
        """Create clickable tabs for each section"""
        tab_width = self.width // len(self.sections)
        tab_height = 40
        
        for i, (section_id, section_name) in enumerate(self.sections):
            x = self.x + i * tab_width
            y = self.y + 60
            self.section_tabs.append({
                'rect': pygame.Rect(x, y, tab_width, tab_height),
                'id': section_id,
                'name': section_name
            })
    
    def open(self, newspaper: Newspaper):
        """Open newspaper for reading"""
        self.active = True
        self.current_newspaper = newspaper
        self.current_section = 'front_page'
        self.scroll_offset = 0
        self._calculate_max_scroll()
    
    def close(self):
        """Close newspaper"""
        self.active = False
        self.current_newspaper = None
        self.scroll_offset = 0
    
    def _calculate_max_scroll(self):
        """Calculate maximum scroll based on content"""
        if not self.current_newspaper:
            self.max_scroll = 0
            return
        
        # Estimate content height
        line_height = 22
        articles = self._get_current_section_articles()
        
        total_lines = 10  # Base offset
        for article in articles:
            total_lines += 3  # Headline
            # Count content lines (rough estimate)
            content_lines = len(article.content) // 60 + 1
            total_lines += content_lines + 2  # Content + spacing
        
        content_height = total_lines * line_height
        visible_height = 650
        self.max_scroll = max(0, content_height - visible_height)
    
    def _get_current_section_articles(self) -> list:
        """Get articles for current section"""
        if not self.current_newspaper:
            return []
        
        if self.current_section == 'front_page':
            # Front page shows highlights from all sections
            all_articles = self.current_newspaper.articles[:]
            # Sort by importance
            all_articles.sort(key=lambda a: a.importance, reverse=True)
            return all_articles[:8]  # Top 8 most important
        elif self.current_section == 'obituary':
            return self.current_newspaper.obituaries
        elif self.current_section == 'politics':
            return self.current_newspaper.political_news
        elif self.current_section == 'society':
            return self.current_newspaper.society_news
        elif self.current_section == 'market':
            return self.current_newspaper.market_reports
        elif self.current_section == 'world':
            return self.current_newspaper.world_events
        return []
    
    def handle_input(self, event) -> bool:
        """Handle input events. Returns True if consumed."""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                self.close()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 30)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                return True
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - 200)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 200)
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_offset = 0
                return True
            elif event.key == pygame.K_END:
                self.scroll_offset = self.max_scroll
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check section tabs
            for tab in self.section_tabs:
                if tab['rect'].collidepoint(mouse_pos):
                    self.current_section = tab['id']
                    self.scroll_offset = 0
                    self._calculate_max_scroll()
                    return True
            
            # Mouse wheel scrolling
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 30)
                return True
            elif event.button == 5:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                return True
        
        return False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font = None):
        """Draw the newspaper UI"""
        if not self.active or not self.current_newspaper:
            return
        
        # Background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Newspaper background (paper texture)
        paper_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.paper_color, paper_rect)
        pygame.draw.rect(screen, self.border_color, paper_rect, 3)
        
        # Masthead (newspaper title)
        from newspaper_system import NewspaperGenerator
        newspaper_name = "The Merchant's Digest"  # Could be loaded from generator
        
        masthead = self.title_font.render(newspaper_name, True, self.headline_color)
        masthead_x = self.x + (self.width - masthead.get_width()) // 2
        screen.blit(masthead, (masthead_x, self.y + 15))
        
        # Date and edition
        date_text = f"Day {self.current_newspaper.date} | Edition #{self.current_newspaper.edition_number}"
        date_surf = self.small_font.render(date_text, True, self.section_color)
        date_x = self.x + (self.width - date_surf.get_width()) // 2
        screen.blit(date_surf, (date_x, self.y + 48))
        
        # Section tabs
        for tab in self.section_tabs:
            is_active = tab['id'] == self.current_section
            
            # Tab background
            if is_active:
                pygame.draw.rect(screen, self.highlight_color, tab['rect'])
            else:
                pygame.draw.rect(screen, (220, 220, 210), tab['rect'])
            
            pygame.draw.rect(screen, self.border_color, tab['rect'], 2)
            
            # Tab label
            label = self.small_font.render(tab['name'], True, self.text_color)
            label_x = tab['rect'].x + (tab['rect'].width - label.get_width()) // 2
            label_y = tab['rect'].y + (tab['rect'].height - label.get_height()) // 2
            screen.blit(label, (label_x, label_y))
        
        # Content area
        content_rect = pygame.Rect(self.x + 20, self.y + 110, self.width - 40, 650)
        
        # Create clipping region for scrollable content
        screen.set_clip(content_rect)
        
        # Draw content with scroll offset
        y_offset = content_rect.y - self.scroll_offset
        
        # Section header
        section_name = dict(self.sections)[self.current_section]
        section_header = self.header_font.render(section_name, True, self.headline_color)
        screen.blit(section_header, (content_rect.x, y_offset))
        y_offset += 40
        
        # Draw divider line
        pygame.draw.line(screen, self.border_color, 
                        (content_rect.x, y_offset), 
                        (content_rect.x + content_rect.width, y_offset), 2)
        y_offset += 15
        
        # Weather report on front page
        if self.current_section == 'front_page' and self.current_newspaper.weather_report:
            weather_label = self.subheader_font.render("🌤️ Weather Forecast", True, self.section_color)
            screen.blit(weather_label, (content_rect.x, y_offset))
            y_offset += 30
            
            weather_text = self._wrap_text(self.current_newspaper.weather_report, 
                                          self.text_font, content_rect.width - 20)
            for line in weather_text:
                line_surf = self.text_font.render(line, True, self.text_color)
                screen.blit(line_surf, (content_rect.x + 10, y_offset))
                y_offset += 22
            
            y_offset += 20
            pygame.draw.line(screen, self.border_color, 
                            (content_rect.x, y_offset), 
                            (content_rect.x + content_rect.width, y_offset), 1)
            y_offset += 15
        
        # Draw articles
        articles = self._get_current_section_articles()
        
        if not articles:
            no_news = self.text_font.render("No news in this section today.", True, self.section_color)
            screen.blit(no_news, (content_rect.x + 20, y_offset))
        else:
            for i, article in enumerate(articles):
                # Article headline
                headline = self.subheader_font.render(article.headline, True, self.headline_color)
                screen.blit(headline, (content_rect.x, y_offset))
                y_offset += 32
                
                # Article content (word wrapped)
                wrapped_lines = self._wrap_text(article.content, self.text_font, content_rect.width - 20)
                for line in wrapped_lines:
                    line_surf = self.text_font.render(line, True, self.text_color)
                    screen.blit(line_surf, (content_rect.x + 10, y_offset))
                    y_offset += 22
                
                # Spacing between articles
                y_offset += 20
                
                # Divider between articles (except last)
                if i < len(articles) - 1:
                    pygame.draw.line(screen, (180, 180, 180), 
                                    (content_rect.x + 20, y_offset), 
                                    (content_rect.x + content_rect.width - 20, y_offset), 1)
                    y_offset += 15
        
        # Clear clipping region
        screen.set_clip(None)
        
        # Scroll indicator
        if self.max_scroll > 0:
            scroll_text = f"Scroll: {int((self.scroll_offset / self.max_scroll) * 100)}%"
            scroll_surf = self.small_font.render(scroll_text, True, self.section_color)
            screen.blit(scroll_surf, (self.x + self.width - 100, self.y + self.height - 30))
        
        # Controls hint
        controls = "↑↓: Scroll | TAB: Sections | N/ESC: Close"
        controls_surf = self.small_font.render(controls, True, self.section_color)
        controls_x = self.x + (self.width - controls_surf.get_width()) // 2
        screen.blit(controls_surf, (controls_x, self.y + self.height - 30))
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Handle newlines in text
            if '\n' in word:
                parts = word.split('\n')
                for i, part in enumerate(parts):
                    if i > 0:
                        lines.append(' '.join(current_line))
                        current_line = []
                    if part:
                        current_line.append(part)
                continue
            
            # Test if adding word exceeds width
            test_line = ' '.join(current_line + [word])
            test_surf = font.render(test_line, True, self.text_color)
            
            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
