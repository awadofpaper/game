"""
Quick test to verify Player serialization round-trip works
"""
import pygame
from config import Config
from world import World
from player import Player

# Initialize pygame
pygame.init()

# Create game objects
config = Config()
world = World(config)
player = Player(config, world, name="TestHero", color=(100, 150, 200))

# Modify player state
player.level = 5
player.experience = 500
player.dubloons = 1000
player.inventory['stick'] = 50
player.health = 75

print("Original Player State:")
print(f"  Name: {player.name}")
print(f"  Level: {player.level}")
print(f"  XP: {player.experience}")
print(f"  Gold: {player.dubloons}")
print(f"  Health: {player.health}")
print(f"  Sticks: {player.inventory['stick']}")
print()

# Serialize
player_data = player.to_dict()
print(f"[OK] Serialized to dict with {len(player_data)} keys")
print()

# Deserialize
restored_player = Player.from_dict(player_data, config, world)
print("Restored Player State:")
print(f"  Name: {restored_player.name}")
print(f"  Level: {restored_player.level}")
print(f"  XP: {restored_player.experience}")
print(f"  Gold: {restored_player.dubloons}")
print(f"  Health: {restored_player.health}")
print(f"  Sticks: {restored_player.inventory['stick']}")
print()

# Verify
success = True
if restored_player.name != player.name:
    print("[FAIL] Name mismatch")
    success = False
if restored_player.level != player.level:
    print("[FAIL] Level mismatch")
    success = False
if restored_player.experience != player.experience:
    print("[FAIL] Experience mismatch")
    success = False
if restored_player.dubloons != player.dubloons:
    print("[FAIL] Gold mismatch")
    success = False
if restored_player.health != player.health:
    print("[FAIL] Health mismatch")
    success = False
if restored_player.inventory['stick'] != player.inventory['stick']:
    print("[FAIL] Inventory mismatch")
    success = False

if success:
    print("[OK] ALL DATA PRESERVED - Serialization round-trip successful! !")
else:
    print("[FAIL] Some data was lost during serialization")
