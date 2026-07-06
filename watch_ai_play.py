"""
Watch the AI Play the Game Visually
This script shows the AI playing with actual graphics rendered
"""

import pygame
import numpy as np
from rpg_gym_env import RPGGameEnv
from config import Config
from graphics import Graphics

# Initialize pygame
pygame.init()

# Create config and screen
config = Config()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("AI Playing RPG - Watch Mode")

# Create graphics renderer
graphics = Graphics(config, screen)

# Create RL environment
env = RPGGameEnv()

# Clock for frame rate
clock = pygame.time.Clock()

# Font for displaying info
font = pygame.font.SysFont(None, 24)
info_font = pygame.font.SysFont(None, 18)

def draw_info_overlay(screen, step, phase, action, reward, total_reward, obs):
    """Draw information overlay on screen"""
    # Semi-transparent black background for text
    overlay = pygame.Surface((config.SCREEN_WIDTH, 150))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Title
    title = font.render(f"AI Playing - Step {step}", True, (255, 255, 0))
    screen.blit(title, (10, 10))
    
    # Phase and action
    phase_text = info_font.render(f"Phase: {phase}", True, (255, 255, 255))
    screen.blit(phase_text, (10, 40))
    
    action_names = {
        0: "Move Up/Add Strength",
        1: "Move Down/Add Stamina", 
        2: "Move Left/Add Stealth",
        3: "Move Right/Add Endurance",
        4: "Attack/Add Magic",
        5: "Talk/Remove Point",
        6: "Train Skill/Next",
        7: "Pick Skill/Prev",
        8: "Use Perk/Confirm"
    }
    action_text = info_font.render(f"Action: {action_names.get(action, 'Unknown')}", True, (200, 200, 255))
    screen.blit(action_text, (10, 60))
    
    # Rewards
    reward_text = info_font.render(f"Reward: {reward:.2f} | Total: {total_reward:.2f}", True, (0, 255, 0))
    screen.blit(reward_text, (10, 80))
    
    # Player stats (if in game)
    if phase == "in_game" and len(obs) >= 13:
        stats_text = info_font.render(
            f"Pos: ({obs[0]:.0f}, {obs[1]:.0f}) | HP: {obs[2]:.0f} | Level: {obs[3]:.0f} | Dubloons: {obs[5]:.0f}",
            True, (255, 200, 100)
        )
        screen.blit(stats_text, (10, 100))
        
        skills_text = info_font.render(
            f"Skills - Str: {obs[7]:.0f} Agi: {obs[8]:.0f} Int: {obs[9]:.0f} Cha: {obs[10]:.0f}",
            True, (200, 255, 200)
        )
        screen.blit(skills_text, (10, 120))
    elif phase == "character_creation":
        char_text = info_font.render(
            f"Skill Points: {obs[1]:.0f} remaining | Allocating skills...",
            True, (255, 200, 255)
        )
        screen.blit(char_text, (10, 100))

def get_tile_color(tile):
    """Get color for a tile based on its ground type"""
    ground_type = tile.layers.get('ground', 'grass')
    
    tile_colors = {
        'grass': (60, 180, 60),
        'water': (30, 100, 200),
        'sand': (200, 180, 120),
        'snow': (220, 220, 255),
        'stone': (100, 100, 100),
        'rock_group': (100, 100, 100),
        'tree': (30, 120, 30),
        'empty': (40, 40, 40),
    }
    
    return tile_colors.get(ground_type, (60, 180, 60))  # Default to grass

def render_game_state(screen, env, obs):
    """Render the current game state"""
    # Fill background
    screen.fill((20, 20, 30))
    
    if env.game.phase == "menu":
        # Menu phase
        title = font.render("=== MAIN MENU ===", True, (255, 255, 0))
        screen.blit(title, (config.SCREEN_WIDTH // 2 - 100, 200))
        
        start_text = info_font.render("AI is starting a new game...", True, (255, 255, 255))
        screen.blit(start_text, (config.SCREEN_WIDTH // 2 - 100, 250))
        
    elif env.game.phase == "character_creation":
        # Character creation phase
        title = font.render("=== CHARACTER CREATION ===", True, (255, 255, 0))
        screen.blit(title, (config.SCREEN_WIDTH // 2 - 150, 100))
        
        y_offset = 150
        skill_names = ["Strength", "Stamina", "Stealth", "Endurance", "Magic"]
        for i, skill in enumerate(skill_names):
            points = env.game.char_skills.get(skill, 0)
            color = (255, 255, 0) if i == env.game.current_skill_idx else (200, 200, 200)
            skill_text = info_font.render(f"{skill}: {points}", True, color)
            screen.blit(skill_text, (config.SCREEN_WIDTH // 2 - 50, y_offset + i * 30))
        
        points_text = info_font.render(f"Points Remaining: {env.game.skill_points_left}", True, (255, 100, 100))
        screen.blit(points_text, (config.SCREEN_WIDTH // 2 - 80, y_offset + 180))
        
    elif env.game.phase == "in_game" and env.game.player:
        # In-game phase - render the world and player
        player = env.game.player
        world = env.game.world
        
        # Calculate camera offset (center on player)
        camera_x = player.x - config.SCREEN_WIDTH // 2
        camera_y = player.y - config.SCREEN_HEIGHT // 2
        
        # Draw visible tiles
        tile_size = config.TILE_SIZE
        start_tile_x = max(0, int(camera_x // tile_size) - 1)
        start_tile_y = max(0, int(camera_y // tile_size) - 1)
        end_tile_x = min(int(world.width // tile_size), int((camera_x + config.SCREEN_WIDTH) // tile_size) + 2)
        end_tile_y = min(int(world.height // tile_size), int((camera_y + config.SCREEN_HEIGHT) // tile_size) + 2)
        
        for tile_x in range(start_tile_x, end_tile_x):
            for tile_y in range(start_tile_y, end_tile_y):
                tile = world.get_tile(tile_x, tile_y)
                if tile:
                    screen_x = tile_x * tile_size - camera_x
                    screen_y = tile_y * tile_size - camera_y
                    tile_color = get_tile_color(tile)
                    pygame.draw.rect(screen, tile_color, (screen_x, screen_y, tile_size, tile_size))
        
        # Draw player
        player_screen_x = player.x - camera_x
        player_screen_y = player.y - camera_y
        pygame.draw.circle(screen, player.color, (int(player_screen_x), int(player_screen_y)), 15)
        
        # Draw player name above
        name_text = info_font.render(player.name, True, (255, 255, 255))
        screen.blit(name_text, (player_screen_x - 20, player_screen_y - 30))

def main():
    print("Starting AI visual playthrough...")
    print("Press ESC to stop, SPACE to pause/unpause")
    print("=" * 60)
    
    obs = env.reset()
    total_reward = 0
    step = 0
    max_steps = 1000
    running = True
    paused = False
    
    while running and step < max_steps:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print(f"{'Paused' if paused else 'Resumed'}")
        
        if not paused:
            # AI takes random action (for now)
            action = env.action_space.sample()
            
            # Execute action
            obs, reward, done, info = env.step(action)
            total_reward += reward
            step += 1
            
            # Print interesting events
            if reward > 5:
                print(f"Step {step}: High reward! {reward:.2f} - {info.get('action', '')}")
            
            if 'character_created' in info:
                print(f"Step {step}: Character created! Entering game world...")
            
            if done:
                print(f"Episode finished at step {step}")
                obs = env.reset()
                total_reward = 0
        
        # Render current state
        render_game_state(screen, env, obs)
        
        # Draw overlay with info
        draw_info_overlay(screen, step, info.get('phase', env.game.phase), 
                         action if not paused else -1, reward if not paused else 0, 
                         total_reward, obs)
        
        # Draw pause indicator
        if paused:
            pause_text = font.render("PAUSED (Press SPACE)", True, (255, 100, 100))
            screen.blit(pause_text, (config.SCREEN_WIDTH // 2 - 120, config.SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(10)  # 10 FPS for watching (increase for faster playback)
    
    print(f"\nPlaythrough finished!")
    print(f"Total steps: {step}")
    print(f"Total reward: {total_reward:.2f}")
    
    pygame.quit()

if __name__ == "__main__":
    main()
