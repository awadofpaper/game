"""
Library System - Historical newspaper archive and reading room
Stores past newspapers for players to review historical events
"""

import pygame
import logging
from typing import Dict, List, Optional
from newspaper_system import Newspaper

logger = logging.getLogger(__name__)


class Library:
    """Represents a library building with newspaper archives"""
    
    def __init__(self, building_id: str, town_name: str, x: int, y: int):
        self.building_id = building_id
        self.town_name = town_name
        self.x = x
        self.y = y
        self.newspaper_archive = []  # List of all past newspapers
        self.max_archive_size = 365  # Store up to 1 year of newspapers
        self.archive_fee = 5  # Cost to access archives (dubloons)
        self.reading_rooms = 3  # Number of NPCs that can read at once
        self.open_hours = (8, 20)  # 8 AM to 8 PM
        
    def add_newspaper(self, newspaper: Newspaper):
        """Add a newspaper to the archive"""
        self.newspaper_archive.append(newspaper)
        
        # Remove oldest if exceeds max size
        if len(self.newspaper_archive) > self.max_archive_size:
            removed = self.newspaper_archive.pop(0)
            logger.debug(f"[LIBRARY] Removed old newspaper from {removed.date} to make room")
        
        logger.info(f"[LIBRARY] Archived newspaper from day {newspaper.date} in {self.town_name}")
    
    def get_newspaper_by_date(self, date: int) -> Optional[Newspaper]:
        """Retrieve a newspaper by date"""
        for newspaper in self.newspaper_archive:
            if newspaper.date == date:
                return newspaper
        return None
    
    def get_newspapers_by_date_range(self, start_date: int, end_date: int) -> List[Newspaper]:
        """Get all newspapers in a date range"""
        return [n for n in self.newspaper_archive if start_date <= n.date <= end_date]
    
    def search_archives(self, keyword: str) -> List[Newspaper]:
        """Search archives for keyword in headlines or content"""
        results = []
        keyword_lower = keyword.lower()
        
        for newspaper in self.newspaper_archive:
            for article in newspaper.articles:
                if keyword_lower in article.headline.lower() or keyword_lower in article.content.lower():
                    if newspaper not in results:
                        results.append(newspaper)
                    break
        
        return results
    
    def get_most_recent(self, count: int = 10) -> List[Newspaper]:
        """Get the most recent newspapers"""
        return self.newspaper_archive[-count:][::-1]  # Most recent first
    
    def is_open(self, current_hour: int) -> bool:
        """Check if library is open"""
        return self.open_hours[0] <= current_hour < self.open_hours[1]


class LibraryManager:
    """Manages all libraries in the game world"""
    
    def __init__(self):
        self.libraries = {}  # library_id: Library
        self.town_to_library = {}  # town_name: library_id
        
    def register_library(self, library: Library):
        """Register a library"""
        self.libraries[library.building_id] = library
        self.town_to_library[library.town_name] = library.building_id
        logger.info(f"[LIBRARY] Registered library in {library.town_name}")
    
    def get_library_in_town(self, town_name: str) -> Optional[Library]:
        """Get the library in a specific town"""
        library_id = self.town_to_library.get(town_name)
        if library_id:
            return self.libraries.get(library_id)
        return None
    
    def add_newspaper_to_all_libraries(self, newspaper: Newspaper):
        """Add a newspaper to all library archives"""
        for library in self.libraries.values():
            library.add_newspaper(newspaper)
    
    def get_all_libraries(self) -> List[Library]:
        """Get all libraries"""
        return list(self.libraries.values())


class LibraryUI:
    """UI for interacting with libraries"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.current_library = None
        self.view_mode = "main"  # 'main', 'browse', 'search', 'reading'
        self.selected_newspaper = None
        self.scroll_offset = 0
        self.search_query = ""
        self.search_results = []
        
        # UI dimensions
        self.panel_width = int(screen_width * 0.8)
        self.panel_height = int(screen_height * 0.8)
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
    def open(self, library: Library):
        """Open the library UI"""
        self.active = True
        self.current_library = library
        self.view_mode = "main"
        self.scroll_offset = 0
        self.selected_newspaper = None
        logger.info(f"[LIBRARY] Opened library UI for {library.town_name}")
    
    def close(self):
        """Close the library UI"""
        self.active = False
        self.current_library = None
        self.view_mode = "main"
        self.selected_newspaper = None
        logger.info("[LIBRARY] Closed library UI")
    
    def handle_input(self, event, player) -> Optional[str]:
        """Handle input events"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.view_mode == "reading":
                    self.view_mode = "browse"
                    self.selected_newspaper = None
                    return None
                else:
                    self.close()
                    return "closed"
            
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            
            elif event.key == pygame.K_DOWN:
                self.scroll_offset += 1
            
            elif event.key == pygame.K_1 and self.view_mode == "main":
                self.view_mode = "browse"
                return None
            
            elif event.key == pygame.K_2 and self.view_mode == "main":
                self.view_mode = "search"
                return None
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Handle newspaper selection in browse mode
                if self.view_mode == "browse":
                    result = self._handle_browse_click(mouse_x, mouse_y)
                    if result:
                        return result
        
        return None
    
    def _handle_browse_click(self, mouse_x: int, mouse_y: int) -> Optional[str]:
        """Handle clicks in browse mode"""
        # Check if clicked on a newspaper entry
        recent = self.current_library.get_most_recent(20)
        
        list_start_y = self.panel_y + 100
        item_height = 40
        
        for i, newspaper in enumerate(recent[self.scroll_offset:]):
            item_y = list_start_y + (i * item_height)
            
            if item_y > self.panel_y + self.panel_height - 100:
                break
            
            if (self.panel_x < mouse_x < self.panel_x + self.panel_width and
                item_y < mouse_y < item_y + item_height):
                self.selected_newspaper = newspaper
                self.view_mode = "reading"
                return None
        
        return None
    
    def draw(self, screen, font, title_font):
        """Draw the library UI"""
        if not self.active or not self.current_library:
            return
        
        # Draw semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(screen, (40, 30, 20), panel_rect)
        pygame.draw.rect(screen, (200, 180, 140), panel_rect, 3)
        
        # Draw title
        title = f"📚 {self.current_library.town_name} Library Archives"
        title_surf = title_font.render(title, True, (255, 240, 200))
        screen.blit(title_surf, (self.panel_x + 20, self.panel_y + 20))
        
        # Draw based on view mode
        if self.view_mode == "main":
            self._draw_main_menu(screen, font)
        elif self.view_mode == "browse":
            self._draw_browse_view(screen, font)
        elif self.view_mode == "reading":
            self._draw_reading_view(screen, font, title_font)
    
    def _draw_main_menu(self, screen, font):
        """Draw main menu"""
        y_offset = self.panel_y + 100
        
        options = [
            "1. Browse Recent Newspapers",
            "2. Search Archives",
            "3. Exit Library",
            "",
            f"Total newspapers archived: {len(self.current_library.newspaper_archive)}",
            f"Archive fee: {self.current_library.archive_fee} dubloons"
        ]
        
        for option in options:
            text_surf = font.render(option, True, (255, 240, 200))
            screen.blit(text_surf, (self.panel_x + 40, y_offset))
            y_offset += 35
    
    def _draw_browse_view(self, screen, font):
        """Draw browse view with recent newspapers"""
        y_offset = self.panel_y + 80
        
        info_text = f"Recent Newspapers (Press ESC to return)"
        info_surf = font.render(info_text, True, (255, 240, 200))
        screen.blit(info_surf, (self.panel_x + 20, y_offset))
        
        y_offset += 50
        
        recent = self.current_library.get_most_recent(20)
        
        if not recent:
            no_papers = font.render("No newspapers in archive yet", True, (200, 180, 140))
            screen.blit(no_papers, (self.panel_x + 40, y_offset))
            return
        
        for i, newspaper in enumerate(recent[self.scroll_offset:]):
            if y_offset > self.panel_y + self.panel_height - 80:
                break
            
            # Draw newspaper entry
            date_text = f"Day {newspaper.date} - Edition #{newspaper.edition_number}"
            article_count = len(newspaper.articles)
            details = f"   {article_count} articles"
            
            date_surf = font.render(date_text, True, (255, 240, 180))
            details_surf = font.render(details, True, (180, 160, 120))
            
            screen.blit(date_surf, (self.panel_x + 40, y_offset))
            screen.blit(details_surf, (self.panel_x + 60, y_offset + 25))
            
            y_offset += 50
        
        # Draw scroll indicator
        if len(recent) > 10:
            scroll_text = f"Scroll: {self.scroll_offset + 1}/{len(recent)}"
            scroll_surf = font.render(scroll_text, True, (150, 130, 100))
            screen.blit(scroll_surf, (self.panel_x + self.panel_width - 200, self.panel_y + self.panel_height - 40))
    
    def _draw_reading_view(self, screen, font, title_font):
        """Draw reading view for selected newspaper"""
        if not self.selected_newspaper:
            return
        
        y_offset = self.panel_y + 80
        
        # Draw newspaper header
        header = f"Edition {self.selected_newspaper.edition_number} - Day {self.selected_newspaper.date}"
        header_surf = title_font.render(header, True, (255, 240, 200))
        screen.blit(header_surf, (self.panel_x + 20, y_offset))
        
        y_offset += 50
        
        # Draw articles
        for article in self.selected_newspaper.articles:
            if y_offset > self.panel_y + self.panel_height - 100:
                break
            
            # Section header
            section_text = f"[{article.section.upper()}]"
            section_surf = font.render(section_text, True, (200, 180, 140))
            screen.blit(section_surf, (self.panel_x + 40, y_offset))
            y_offset += 25
            
            # Headline
            headline_surf = font.render(article.headline, True, (255, 240, 180))
            screen.blit(headline_surf, (self.panel_x + 40, y_offset))
            y_offset += 30
            
            # Content (truncate if too long)
            content_lines = self._wrap_text(article.content, font, self.panel_width - 100)
            for line in content_lines[:3]:  # Show first 3 lines
                line_surf = font.render(line, True, (220, 200, 160))
                screen.blit(line_surf, (self.panel_x + 60, y_offset))
                y_offset += 22
            
            y_offset += 15  # Space between articles
        
        # Instructions
        inst_text = "Press ESC to return to browse"
        inst_surf = font.render(inst_text, True, (150, 130, 100))
        screen.blit(inst_surf, (self.panel_x + 20, self.panel_y + self.panel_height - 40))
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text to fit within max width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
