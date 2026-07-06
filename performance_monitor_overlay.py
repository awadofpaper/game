"""
Performance Monitoring and Stress Test Utility
==============================================

This script adds real-time performance metrics display.
"""

import pygame
import time

class PerformanceMonitor:
    """Track and display game performance metrics"""
    
    def __init__(self):
        self.frame_times = []
        self.max_samples = 60  # Track last 60 frames
        self.update_times = []
        self.render_times = []
        
        # Performance counters
        self.enemy_count = 0
        self.projectile_count = 0
        self.npc_count = 0
        self.entity_count = 0
        
        # Timing
        self.last_update_start = 0
        self.last_render_start = 0
        
        # Display settings
        self.show_detailed = True
        self.position = (10, 200)
        
    def start_update(self):
        """Mark start of update phase"""
        self.last_update_start = time.perf_counter()
    
    def end_update(self):
        """Mark end of update phase"""
        update_time = (time.perf_counter() - self.last_update_start) * 1000  # ms
        self.update_times.append(update_time)
        if len(self.update_times) > self.max_samples:
            self.update_times.pop(0)
    
    def start_render(self):
        """Mark start of render phase"""
        self.last_render_start = time.perf_counter()
    
    def end_render(self):
        """Mark end of render phase"""
        render_time = (time.perf_counter() - self.last_render_start) * 1000  # ms
        self.render_times.append(render_time)
        if len(self.render_times) > self.max_samples:
            self.render_times.pop(0)
    
    def add_frame_time(self, frame_time):
        """Add frame time in milliseconds"""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)
    
    def update_counts(self, enemies=0, projectiles=0, npcs=0, entities=0):
        """Update entity counts"""
        self.enemy_count = enemies
        self.projectile_count = projectiles
        self.npc_count = npcs
        self.entity_count = entities
    
    def get_fps(self):
        """Get current FPS"""
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        if avg_frame_time == 0:
            return 0
        return 1000 / avg_frame_time
    
    def get_avg_update_time(self):
        """Get average update time in ms"""
        if not self.update_times:
            return 0
        return sum(self.update_times) / len(self.update_times)
    
    def get_avg_render_time(self):
        """Get average render time in ms"""
        if not self.render_times:
            return 0
        return sum(self.render_times) / len(self.render_times)
    
    def get_frame_budget_usage(self):
        """Get percentage of 16.67ms frame budget used (for 60fps)"""
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return (avg_frame_time / 16.67) * 100
    
    def draw(self, screen, font=None):
        """Draw performance overlay"""
        if font is None:
            font = pygame.font.SysFont('Courier New', 16, bold=True)
        
        x, y = self.position
        line_height = 20
        
        # Background panel
        panel_width = 280
        panel_height = 160 if self.show_detailed else 80
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))
        screen.blit(panel_surface, (x - 5, y - 5))
        
        # FPS
        fps = self.get_fps()
        fps_color = (100, 255, 100) if fps >= 55 else (255, 200, 100) if fps >= 30 else (255, 100, 100)
        fps_text = font.render(f"FPS: {fps:.1f}", True, fps_color)
        screen.blit(fps_text, (x, y))
        y += line_height
        
        # Frame budget
        budget = self.get_frame_budget_usage()
        budget_color = (100, 255, 100) if budget < 80 else (255, 200, 100) if budget < 100 else (255, 100, 100)
        budget_text = font.render(f"Budget: {budget:.1f}%", True, budget_color)
        screen.blit(budget_text, (x, y))
        y += line_height
        
        if self.show_detailed:
            # Update time
            update_time = self.get_avg_update_time()
            update_color = (200, 200, 200)
            update_text = font.render(f"Update: {update_time:.2f}ms", True, update_color)
            screen.blit(update_text, (x, y))
            y += line_height
            
            # Render time
            render_time = self.get_avg_render_time()
            render_text = font.render(f"Render: {render_time:.2f}ms", True, update_color)
            screen.blit(render_text, (x, y))
            y += line_height
            
            # Entity counts
            entities_text = font.render(f"Enemies: {self.enemy_count}", True, (200, 200, 200))
            screen.blit(entities_text, (x, y))
            y += line_height
            
            projectiles_text = font.render(f"Projectiles: {self.projectile_count}", True, (200, 200, 200))
            screen.blit(projectiles_text, (x, y))
            y += line_height
            
            # Memory estimate (rough)
            total_objects = self.enemy_count + self.projectile_count + self.npc_count + self.entity_count
            objects_text = font.render(f"Objects: {total_objects}", True, (200, 200, 200))
            screen.blit(objects_text, (x, y))
        
        # Toggle hint
        hint_font = pygame.font.SysFont('Courier New', 12)
        hint_text = hint_font.render("[F3] Toggle", True, (150, 150, 150))
        screen.blit(hint_text, (x + 180, self.position[1]))
    
    def toggle_detailed(self):
        """Toggle detailed display"""
        self.show_detailed = not self.show_detailed


# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor():
    """Get singleton performance monitor"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
