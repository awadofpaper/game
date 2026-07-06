"""
Quick test to verify the sprite rendering system works
"""

import pygame
import sys
sys.path.insert(0, 'c:\\Users\\Public\\rpg_game')

from sprite_renderer import SpriteRenderer
from config import Config

# Simple mock player class for testing
class MockPlayer:
    def __init__(self):
        self.color = (100, 150, 200)
        self.equipment = {
            'head': 'iron_helmet',
            'chest': 'iron_chestplate',
            'legs': 'iron_leggings',
            'feet': 'iron_boots',
            'main_hand': 'iron_sword',
            'off_hand': 'wooden_shield'
        }

def test_sprite_rendering():
    """Test that sprite rendering doesn't crash"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sprite System Test")
    
    # Create test player
    player = MockPlayer()
    
    # Test rendering loop
    clock = pygame.time.Clock()
    running = True
    
    print("Testing sprite renderer...")
    print("You should see a character with equipment in the center of the screen")
    print("Press ESC to exit")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill((50, 50, 50))
        
        # Draw player sprite in center of screen
        center = (400, 300)
        try:
            SpriteRenderer.draw_player_sprite(screen, player, center)
            
            # Test text
            font = pygame.font.SysFont(None, 24)
            text = font.render("Character sprite with equipment!", True, (255, 255, 255))
            screen.blit(text, (400 - text.get_width()//2, 500))
            
            instructions = font.render("Press ESC to exit", True, (200, 200, 200))
            screen.blit(instructions, (400 - instructions.get_width()//2, 550))
            
        except Exception as e:
            # Draw error
            font = pygame.font.SysFont(None, 20)
            error_text = font.render(f"Error: {str(e)}", True, (255, 0, 0))
            screen.blit(error_text, (50, 50))
            print(f"Error rendering sprite: {e}")
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Test complete!")

if __name__ == "__main__":
    test_sprite_rendering()
