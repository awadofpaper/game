"""
Stealth Indicator UI - Shows stealth status and detection level
"""

import pygame
import math


class StealthIndicatorUI:
    """Display stealth mode status and detection level"""
    
    def __init__(self):
        self.position = "top-left"  # Position on screen
        self.font = None
        self.icon_size = 32
        self.detection_bar_width = 100
        self.detection_bar_height = 8
        
    def draw(self, screen, player, detections, offset_x=20, offset_y=60):
        """
        Draw stealth indicator
        
        Args:
            screen: Pygame screen surface
            player: Player object with in_stealth_mode attribute
            detections: List of (npc_id, detection_chance, npc) tuples from stealth system
            offset_x: X offset from left edge
            offset_y: Y offset from top edge
        """
        # Only draw if stealth mode is active
        if not getattr(player, 'in_stealth_mode', False):
            return
        
        # Initialize font if needed
        if self.font is None:
            self.font = pygame.font.SysFont('arial', 16, bold=True)
        
        x = offset_x
        y = offset_y
        
        # Determine detection state
        is_detected = len(detections) > 0 if detections else False
        max_detection_chance = 0.0
        detecting_npcs = 0
        
        if detections:
            detecting_npcs = len(detections)
            max_detection_chance = max(d[1] for d in detections)
        
        # Background panel
        panel_width = 200
        panel_height = 80 if is_detected else 50
        panel_rect = pygame.Rect(x - 5, y - 5, panel_width, panel_height)
        
        # Semi-transparent background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (0, 0, 0, 180), (0, 0, panel_width, panel_height), border_radius=8)
        screen.blit(panel_surface, (x - 5, y - 5))
        
        # Draw stealth icon (eye with slash for hidden, eye for detected)
        icon_x = x + 5
        icon_y = y + 5
        
        if is_detected:
            # Open eye (detected) - RED
            self._draw_eye_icon(screen, icon_x, icon_y, open_eye=True, color=(255, 50, 50))
            status_text = "DETECTED"
            status_color = (255, 80, 80)
        else:
            # Closed/slashed eye (hidden) - GREEN
            self._draw_eye_icon(screen, icon_x, icon_y, open_eye=False, color=(50, 255, 50))
            status_text = "HIDDEN"
            status_color = (100, 255, 100)
        
        # Draw "STEALTH MODE" text
        stealth_text = self.font.render("STEALTH", True, (200, 200, 255))
        screen.blit(stealth_text, (icon_x + self.icon_size + 10, y + 5))
        
        # Draw status text (HIDDEN/DETECTED)
        status_font = pygame.font.SysFont('arial', 14, bold=True)
        status_surface = status_font.render(status_text, True, status_color)
        screen.blit(status_surface, (icon_x + self.icon_size + 10, y + 25))
        
        # If detected, show detection level bar and count
        if is_detected:
            bar_x = x + 5
            bar_y = y + 50
            
            # Draw detection bar background
            pygame.draw.rect(screen, (50, 50, 50), 
                           (bar_x, bar_y, self.detection_bar_width, self.detection_bar_height))
            
            # Draw detection level (red bar)
            detection_width = int(self.detection_bar_width * max_detection_chance)
            color = self._get_detection_color(max_detection_chance)
            pygame.draw.rect(screen, color, 
                           (bar_x, bar_y, detection_width, self.detection_bar_height))
            
            # Draw border
            pygame.draw.rect(screen, (255, 255, 255), 
                           (bar_x, bar_y, self.detection_bar_width, self.detection_bar_height), 1)
            
            # Draw detection percentage
            detection_percent = int(max_detection_chance * 100)
            percent_text = status_font.render(f"{detection_percent}%", True, (255, 255, 255))
            screen.blit(percent_text, (bar_x + self.detection_bar_width + 5, bar_y - 2))
            
            # Draw NPC count if multiple
            if detecting_npcs > 1:
                npc_label = "guards" if "Guard" in str(detections[0][0]) else "enemies"
                npc_count_text = status_font.render(f"({detecting_npcs} {npc_label})", True, (255, 200, 100))
                screen.blit(npc_count_text, (bar_x, bar_y + 12))
    
    def _draw_eye_icon(self, screen, x, y, open_eye=True, color=(255, 255, 255)):
        """Draw eye icon for stealth indicator"""
        center_x = x + self.icon_size // 2
        center_y = y + self.icon_size // 2
        
        if open_eye:
            # Draw open eye (detected)
            # Eye outline
            pygame.draw.ellipse(screen, color, 
                              (x + 4, y + 10, self.icon_size - 8, self.icon_size // 2), 2)
            # Pupil
            pygame.draw.circle(screen, color, (center_x, center_y), 6)
            pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 3)
            
            # Alert triangle
            alert_points = [
                (center_x - 6, y + 2),
                (center_x + 6, y + 2),
                (center_x, y - 6)
            ]
            pygame.draw.polygon(screen, (255, 200, 0), alert_points)
            pygame.draw.polygon(screen, (255, 100, 0), alert_points, 2)
            
            # Exclamation mark in triangle
            pygame.draw.line(screen, (200, 0, 0), (center_x, y - 4), (center_x, y), 2)
            pygame.draw.circle(screen, (200, 0, 0), (center_x, y + 1), 1)
        else:
            # Draw closed/hidden eye (hidden)
            # Eye outline
            pygame.draw.ellipse(screen, color, 
                              (x + 4, y + 10, self.icon_size - 8, self.icon_size // 2), 2)
            # Slash through eye
            pygame.draw.line(screen, color, 
                           (x + 2, y + self.icon_size - 4), 
                           (x + self.icon_size - 2, y + 4), 3)
            
            # Checkmark for hidden
            check_points = [
                (x + 8, center_y),
                (center_x - 2, center_y + 8),
                (x + self.icon_size - 6, y + 4)
            ]
            for i in range(len(check_points) - 1):
                pygame.draw.line(screen, color, check_points[i], check_points[i + 1], 3)
    
    def _get_detection_color(self, detection_chance):
        """Get color based on detection level"""
        if detection_chance < 0.3:
            return (255, 200, 0)  # Yellow (low)
        elif detection_chance < 0.6:
            return (255, 140, 0)  # Orange (medium)
        else:
            return (255, 50, 50)  # Red (high)


# Global instance
_stealth_indicator_ui = None


def get_stealth_indicator_ui():
    """Get or create stealth indicator UI singleton"""
    global _stealth_indicator_ui
    if _stealth_indicator_ui is None:
        _stealth_indicator_ui = StealthIndicatorUI()
    return _stealth_indicator_ui
