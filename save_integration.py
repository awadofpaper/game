"""
Save System Integration Helper
Simplifies integration of the enhanced save system into the main game
"""

import logging
import time
from typing import Optional
from save_system import save_game_enhanced, load_game_enhanced, auto_save_game, delete_save_slot
from save_load_ui import SaveLoadUI

logger = logging.getLogger(__name__)


class SaveLoadIntegrator:
    """Integrates enhanced save/load system with the game"""
    
    def __init__(self, game_instance=None):
        self.game = game_instance
        self.ui: Optional[SaveLoadUI] = None
        
        # Auto-save configuration
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5 minutes
        self.last_auto_save = 0
        
        # Current game state references
        self.world = None
        self.player = None
        
        # Selected save slot (set by main menu)
        self.selected_save_slot = None
        
        # Message display
        self.message = ""
        self.message_timer = 0
        
    def initialize_ui(self, screen_width: int, screen_height: int):
        """Initialize the save/load UI"""
        self.ui = SaveLoadUI(screen_width, screen_height)
        self._setup_ui_callbacks()
    
    def set_game_state(self, world, player, save_slot=None):
        """Set references to current game state and save slot"""
        self.world = world
        self.player = player
        if save_slot is not None:
            self.selected_save_slot = save_slot
    
    def _setup_ui_callbacks(self):
        """Set up UI callback functions"""
        if not self.ui:
            return
        
        self.ui.on_save = self._on_save
        self.ui.on_load = self._on_load
        self.ui.on_delete = self._on_delete
        self.ui.on_cancel = self._on_cancel
    
    def _on_save(self, slot_id: int):
        """Handle save action from UI"""
        if not self.world or not self.player:
            self._show_message("Error: Game state not set")
            return
        
        success, message = save_game_enhanced(slot_id, self.world, self.player)
        self._show_message(message)
        
        if success:
            logger.info(f"Game saved to slot {slot_id}")
    
    def _on_load(self, slot_id: int):
        """Handle load action from UI"""
        if not self.world or not self.player:
            self._show_message("Error: Game state not set")
            return
        
        success, message = load_game_enhanced(slot_id, self.world, self.player)
        self._show_message(message)
        
        if success:
            logger.info(f"Game loaded from slot {slot_id}")
    
    def _on_delete(self, slot_id: int):
        """Handle delete action from UI"""
        success, message = delete_save_slot(slot_id)
        self._show_message(message)
        
        if success and self.ui:
            self.ui.refresh_saves()
    
    def _on_cancel(self):
        """Handle cancel action"""
        self._show_message("")
    
    def _show_message(self, message: str):
        """Display a message to the player"""
        self.message = message
        self.message_timer = 180  # Show for 3 seconds at 60 FPS
    
    def quick_save(self):
        """Quick save to the selected slot"""
        if not self.world or not self.player:
            self._show_message("Error: Game state not set")
            return False
        
        # Use the selected save slot if available, otherwise use utils save_game
        if self.selected_save_slot:
            from utils import save_game
            from config import Config
            config = Config()
            try:
                save_game(self.player, self.world, config, self.selected_save_slot)
                self._show_message(f"Quick saved to Slot {self.selected_save_slot.slot_number}!")
                return True
            except Exception as e:
                self._show_message(f"Save failed: {e}")
                return False
        else:
            # Fallback to old system
            success, message = save_game_enhanced(1, self.world, self.player)
            self._show_message(message)
            return success
    
    def quick_load(self):
        """Quick load from the selected slot"""
        if not self.world or not self.player:
            self._show_message("Error: Game state not set")
            return False
        
        # Use the selected save slot if available, otherwise use utils load_game
        if self.selected_save_slot:
            from utils import load_game
            from config import Config
            config = Config()
            try:
                load_game(self.player, self.world, config, self.selected_save_slot)
                self._show_message(f"Quick loaded from Slot {self.selected_save_slot.slot_number}!")
                return True
            except Exception as e:
                self._show_message(f"Load failed: {e}")
                return False
        else:
            # Fallback to old system
            success, message = load_game_enhanced(1, self.world, self.player)
            self._show_message(message)
            return success
        if not self.world or not self.player:
            self._show_message("Error: Game state not set")
            return False
        
        success, message = load_game_enhanced(1, self.world, self.player)
        self._show_message(message)
        return success
    
    def perform_auto_save(self):
        """Perform auto-save"""
        if not self.auto_save_enabled or not self.world or not self.player:
            return False
        
        success, message = auto_save_game(self.world, self.player)
        if success:
            self._show_message("Auto-save completed")
            self.last_auto_save = time.time()
            logger.info("Auto-save completed")
        else:
            logger.error(f"Auto-save failed: {message}")
        
        return success
    
    def check_auto_save(self):
        """Check if auto-save should trigger"""
        if not self.auto_save_enabled:
            return
        
        current_time = time.time()
        if current_time - self.last_auto_save >= self.auto_save_interval:
            self.perform_auto_save()
    
    def open_save_dialog(self):
        """Open save dialog"""
        if self.ui:
            self.ui.open_save_dialog()
    
    def open_load_dialog(self):
        """Open load dialog"""
        if self.ui:
            self.ui.open_load_dialog()
    
    def handle_event(self, event):
        """Handle pygame events"""
        if self.ui and self.ui.active:
            return self.ui.handle_event(event)
        return False
    
    def update(self, dt: float):
        """Update integrator state"""
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        # Check for auto-save
        self.check_auto_save()
    
    def draw(self, screen):
        """Draw UI elements"""
        # Draw save/load UI
        if self.ui:
            self.ui.draw(screen)
        
        # Draw message if active
        if self.message and self.message_timer > 0:
            self._draw_message(screen)
    
    def _draw_message(self, screen):
        """Draw status message"""
        import pygame
        
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render(self.message, True, (255, 255, 255))
        
        # Background
        padding = 20
        bg_width = text_surface.get_width() + padding * 2
        bg_height = text_surface.get_height() + padding * 2
        bg_x = (screen.get_width() - bg_width) // 2
        bg_y = screen.get_height() - bg_height - 50
        
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((40, 40, 50, 200))
        screen.blit(bg_surface, (bg_x, bg_y))
        
        # Border
        pygame.draw.rect(screen, (100, 100, 120), 
                        (bg_x, bg_y, bg_width, bg_height), 2)
        
        # Text
        text_x = bg_x + padding
        text_y = bg_y + padding
        screen.blit(text_surface, (text_x, text_y))


def integrate_enhanced_saves(screen_width: int = 800, screen_height: int = 600):
    """
    Create and configure a save integrator
    
    Usage:
        # In your main game initialization:
        save_integrator = integrate_enhanced_saves(800, 600)
        save_integrator.set_game_state(world, player)
        
        # In your event loop:
        if save_integrator.handle_event(event):
            continue  # Event was handled
        
        # In your update loop:
        save_integrator.update(dt)
        
        # In your draw loop:
        save_integrator.draw(screen)
        
        # For quick save/load:
        # F5: save_integrator.quick_save()
        # F9: save_integrator.quick_load()
        
        # For save/load dialogs:
        # save_integrator.open_save_dialog()
        # save_integrator.open_load_dialog()
    """
    integrator = SaveLoadIntegrator()
    integrator.initialize_ui(screen_width, screen_height)
    return integrator


# Quick access functions for simple integration
def quick_save(world, player) -> bool:
    """Quick save to slot 1"""
    success, message = save_game_enhanced(1, world, player)
    print(message)
    return success


def quick_load(world, player) -> bool:
    """Quick load from slot 1"""
    success, message = load_game_enhanced(1, world, player)
    print(message)
    return success


def emergency_save(world, player) -> bool:
    """Emergency save to auto-save slot"""
    success, message = auto_save_game(world, player)
    print(message)
    return success
