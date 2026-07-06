"""
Economic Events Display UI
Shows active price events affecting the economy
"""

import pygame
from shop_system import ShopCategory


class EconomicEventsUI:
    """Visual display for active economic events"""
    
    def __init__(self):
        self.active = False
        self.price_event_manager = None
        self.current_town = None
        self.current_day = 0
        
        # Scrolling
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Colors
        self.bg_color = (20, 15, 30)
        self.panel_color = (40, 30, 55)
        self.header_color = (60, 45, 80)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.green_color = (100, 255, 100)
        self.red_color = (255, 100, 100)
        self.blue_color = (100, 200, 255)
        self.gray_color = (150, 150, 150)
        self.accent_color = (150, 120, 200)
        
    def open(self, price_event_manager, current_town: str, current_day: int):
        """Open the events display"""
        self.active = True
        self.price_event_manager = price_event_manager
        self.current_town = current_town
        self.current_day = current_day
        self.scroll_offset = 0
        
    def close(self):
        """Close the display"""
        self.active = False
        
    def toggle(self, price_event_manager=None, current_town=None, current_day=0):
        """Toggle the display on/off"""
        if self.active:
            self.close()
        else:
            if price_event_manager:
                self.open(price_event_manager, current_town, current_day)
                
    def handle_input(self, event):
        """Handle keyboard input"""
        if not self.active:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_e:
                return "close"
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 20)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 20)
                
        return None
        
    def _get_category_icon(self, category: ShopCategory) -> str:
        """Get icon for shop category"""
        icons = {
            ShopCategory.WEAPONS: "⚔️",
            ShopCategory.ARMOR: "🛡️",
            ShopCategory.CONSUMABLES: "🧪",
            ShopCategory.MATERIALS: "📦",
            ShopCategory.MISC: "✨"
        }
        return icons.get(category, "📍")
        
    def _get_category_name(self, category: ShopCategory) -> str:
        """Get display name for category"""
        names = {
            ShopCategory.WEAPONS: "Weapons",
            ShopCategory.ARMOR: "Armor",
            ShopCategory.CONSUMABLES: "Consumables",
            ShopCategory.MATERIALS: "Materials",
            ShopCategory.MISC: "Miscellaneous"
        }
        return names.get(category, str(category))
        
    def draw(self, screen):
        """Draw the events display"""
        if not self.active or not self.price_event_manager:
            return
            
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill(self.bg_color)
        overlay.set_alpha(220)
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 700
        panel_height = 550
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        # Panel background
        pygame.draw.rect(screen, self.panel_color, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, self.accent_color, 
                        (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Header
        header_height = 70
        pygame.draw.rect(screen, self.header_color,
                        (panel_x, panel_y, panel_width, header_height))
        pygame.draw.line(screen, self.accent_color,
                        (panel_x, panel_y + header_height),
                        (panel_x + panel_width, panel_y + header_height), 2)
        
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)
        
        # Title
        title_surf = font_large.render("Economic Events", True, self.gold_color)
        title_rect = title_surf.get_rect(centerx=panel_x + panel_width // 2, top=panel_y + 12)
        screen.blit(title_surf, title_rect)
        
        # Current location
        location_text = f"Current Location: {self.current_town or 'World Map'}"
        location_surf = font_small.render(location_text, True, self.blue_color)
        location_rect = location_surf.get_rect(centerx=panel_x + panel_width // 2, top=panel_y + 48)
        screen.blit(location_surf, location_rect)
        
        # Content area
        content_y = panel_y + header_height + 10
        content_height = panel_height - header_height - 60
        
        # Get active events
        active_events = list(self.price_event_manager.active_events.values())
        
        if not active_events:
            # No events message
            no_events_surf = font_medium.render("No active economic events", True, self.gray_color)
            no_events_rect = no_events_surf.get_rect(
                centerx=panel_x + panel_width // 2,
                centery=content_y + content_height // 2
            )
            screen.blit(no_events_surf, no_events_rect)
            
            # Peaceful message
            peaceful_surf = font_small.render("Trade is stable and prices are normal", True, self.green_color)
            peaceful_rect = peaceful_surf.get_rect(
                centerx=panel_x + panel_width // 2,
                centery=content_y + content_height // 2 + 35
            )
            screen.blit(peaceful_surf, peaceful_rect)
        else:
            # Create scrollable surface
            item_height = 140
            total_height = len(active_events) * item_height
            self.max_scroll = max(0, total_height - content_height)
            
            # Create clipping rect for scrolling
            clip_rect = pygame.Rect(panel_x + 10, content_y, panel_width - 20, content_height)
            screen.set_clip(clip_rect)
            
            # Draw each event
            y_offset = content_y - self.scroll_offset
            
            for i, event in enumerate(active_events):
                # Skip if completely off-screen
                if y_offset + item_height < content_y or y_offset > content_y + content_height:
                    y_offset += item_height
                    continue
                
                # Filter by current town if set
                show_dimmed = False
                if self.current_town and event.affected_towns and self.current_town not in event.affected_towns:
                    show_dimmed = True
                
                # Event box
                box_x = panel_x + 20
                box_y = y_offset
                box_width = panel_width - 40
                box_height = 130
                
                # Background
                box_color = self.header_color if not show_dimmed else (30, 25, 35)
                pygame.draw.rect(screen, box_color, (box_x, box_y, box_width, box_height))
                pygame.draw.rect(screen, self.accent_color if not show_dimmed else self.gray_color,
                               (box_x, box_y, box_width, box_height), 2)
                
                text_alpha = 255 if not show_dimmed else 100
                
                # Event name
                name_color = self.gold_color if not show_dimmed else self.gray_color
                name_surf = font_medium.render(event.name, True, name_color)
                screen.blit(name_surf, (box_x + 10, box_y + 8))
                
                # Scope (Global or specific towns)
                if event.affected_towns:
                    scope_text = f"📍 {', '.join(event.affected_towns)}"
                else:
                    scope_text = "🌍 Global Event"
                scope_color = self.blue_color if not show_dimmed else self.gray_color
                scope_surf = font_small.render(scope_text, True, scope_color)
                scope_rect = scope_surf.get_rect(right=box_x + box_width - 10, top=box_y + 10)
                screen.blit(scope_surf, scope_rect)
                
                # Description
                desc_color = self.text_color if not show_dimmed else self.gray_color
                desc_surf = font_small.render(event.description, True, desc_color)
                screen.blit(desc_surf, (box_x + 10, box_y + 38))
                
                # Price impact
                price_change = (event.price_modifier - 1.0) * 100
                if price_change > 0:
                    impact_text = f"Price Impact: +{int(price_change)}%"
                    impact_color = self.red_color if not show_dimmed else self.gray_color
                    impact_icon = "📈"
                else:
                    impact_text = f"Price Impact: {int(price_change)}%"
                    impact_color = self.green_color if not show_dimmed else self.gray_color
                    impact_icon = "📉"
                
                impact_surf = font_small.render(f"{impact_icon} {impact_text}", True, impact_color)
                screen.blit(impact_surf, (box_x + 10, box_y + 65))
                
                # Affected categories
                categories_text = "Affects: " + ", ".join([
                    self._get_category_name(cat) for cat in event.affected_categories
                ])
                categories_color = self.accent_color if not show_dimmed else self.gray_color
                categories_surf = font_small.render(categories_text, True, categories_color)
                screen.blit(categories_surf, (box_x + 10, box_y + 90))
                
                # Days remaining
                days_left = max(0, (event.start_day + event.duration_days) - self.current_day)
                if days_left > 7:
                    days_color = self.green_color if not show_dimmed else self.gray_color
                elif days_left > 3:
                    days_color = self.gold_color if not show_dimmed else self.gray_color
                else:
                    days_color = self.red_color if not show_dimmed else self.gray_color
                
                days_text = f"⏰ {days_left} day{'s' if days_left != 1 else ''} remaining"
                days_surf = font_small.render(days_text, True, days_color)
                days_rect = days_surf.get_rect(right=box_x + box_width - 10, top=box_y + 90)
                screen.blit(days_surf, days_rect)
                
                y_offset += item_height
            
            # Remove clipping
            screen.set_clip(None)
            
            # Scroll indicators
            if self.scroll_offset > 0:
                scroll_up_surf = font_small.render("▲ Scroll Up", True, self.accent_color)
                scroll_up_rect = scroll_up_surf.get_rect(
                    centerx=panel_x + panel_width // 2,
                    top=content_y + 5
                )
                screen.blit(scroll_up_surf, scroll_up_rect)
            
            if self.scroll_offset < self.max_scroll:
                scroll_down_surf = font_small.render("▼ Scroll Down", True, self.accent_color)
                scroll_down_rect = scroll_down_surf.get_rect(
                    centerx=panel_x + panel_width // 2,
                    bottom=content_y + content_height - 5
                )
                screen.blit(scroll_down_surf, scroll_down_rect)
        
        # Controls hint
        controls_y = panel_y + panel_height - 45
        controls_text = "↑↓: Scroll  E/ESC: Close"
        controls_surf = font_small.render(controls_text, True, self.gray_color)
        controls_rect = controls_surf.get_rect(centerx=panel_x + panel_width // 2, top=controls_y)
        screen.blit(controls_surf, controls_rect)
