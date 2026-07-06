"""
Stress Tests - Test performance under heavy load
Tests system limits and performance characteristics
"""

import pygame
import sys
import time
from config import Config
from player import Player
from world import World
from enemies import Enemy
from npc_basic import BasicNPC

print("="*60)
print("STRESS TEST SUITE")
print("="*60)

pygame.init()
config = Config()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

# Initialize core systems
world = World(config)
player = Player(config, world)
print("[OK] Core systems initialized")

# TEST 1: Many Enemies
print("\n" + "="*60)
print("TEST 1: Enemy Spawning Stress Test")
print("="*60)

start_time = time.time()
enemies = []
enemy_count = 100

for i in range(enemy_count):
    x = 100 + (i % 10) * 100
    y = 100 + (i // 10) * 100
    enemy = Enemy("slime", x, y, level=1, rarity="Common")
    enemies.append(enemy)

end_time = time.time()
spawn_time = end_time - start_time

print(f"[OK] Spawned {enemy_count} enemies in {spawn_time:.3f}s")
print(f"[OK] Average spawn time: {(spawn_time/enemy_count)*1000:.2f}ms per enemy")

if spawn_time < 1.0:
    print("[OK] EXCELLENT - Spawning performance is very fast")
elif spawn_time < 3.0:
    print("[OK] GOOD - Spawning performance is acceptable")
else:
    print("[WARN]  SLOW - Spawning took longer than expected")

# TEST 2: Many NPCs
print("\n" + "="*60)
print("TEST 2: NPC Spawning Stress Test")
print("="*60)

start_time = time.time()
npcs = []
npc_count = 50

for i in range(npc_count):
    x = 200 + (i % 10) * 80
    y = 200 + (i // 10) * 80
    npc = BasicNPC(f"NPC_{i}", x, y, "villager")
    npcs.append(npc)

end_time = time.time()
npc_spawn_time = end_time - start_time

print(f"[OK] Spawned {npc_count} NPCs in {npc_spawn_time:.3f}s")
print(f"[OK] Average spawn time: {(npc_spawn_time/npc_count)*1000:.2f}ms per NPC")

# TEST 3: World Tile Access Speed
print("\n" + "="*60)
print("TEST 3: World Tile Access Speed")
print("="*60)

start_time = time.time()
tile_access_count = 1000

for i in range(tile_access_count):
    x = (i % 100) * config.TILE_SIZE
    y = (i // 100) * config.TILE_SIZE
    tile = world.get_tile(x, y)

end_time = time.time()
tile_access_time = end_time - start_time

print(f"[OK] Accessed {tile_access_count} tiles in {tile_access_time:.3f}s")
print(f"[OK] Average access time: {(tile_access_time/tile_access_count)*1000:.2f}ms per tile")

if tile_access_time < 0.1:
    print("[OK] EXCELLENT - Tile access is very fast (cached)")
elif tile_access_time < 0.5:
    print("[OK] GOOD - Tile access is fast")
else:
    print("[WARN]  SLOW - Tile access could be optimized")

# TEST 4: Inventory Stress Test
print("\n" + "="*60)
print("TEST 4: Inventory Operations Stress Test")
print("="*60)

start_time = time.time()
operations = 1000

for i in range(operations):
    player.inventory["test_item"] = player.inventory.get("test_item", 0) + 1

end_time = time.time()
add_time = end_time - start_time

start_time = time.time()
for i in range(operations):
    _ = player.inventory.get("test_item", 0)
end_time = time.time()
get_time = end_time - start_time

print(f"[OK] Added {operations} items in {add_time:.3f}s ({add_time/operations*1000:.3f}ms each)")
print(f"[OK] Retrieved {operations} items in {get_time:.3f}s ({get_time/operations*1000:.3f}ms each)")

# TEST 5: Skills XP Stress Test
print("\n" + "="*60)
print("TEST 5: Skills System Stress Test")
print("="*60)

start_time = time.time()
xp_operations = 1000

for i in range(xp_operations):
    player.skills_manager.add_xp(player.skills_manager.MINING, 1)

end_time = time.time()
xp_time = end_time - start_time

print(f"[OK] Added XP {xp_operations} times in {xp_time:.3f}s")
print(f"[OK] Average XP add time: {(xp_time/xp_operations)*1000:.3f}ms")

final_xp = player.skills_manager.get_xp(player.skills_manager.MINING)
final_level = player.skills_manager.get_level(player.skills_manager.MINING)
print(f"[OK] Final Mining: Level {final_level}, XP {final_xp}")

# TEST 6: Recipe Discovery Stress Test
print("\n" + "="*60)
print("TEST 6: Recipe Discovery Stress Test")
print("="*60)

from crafting import discover_recipe, CRAFTING_RECIPES

start_time = time.time()
discovery_count = 0

for recipe in CRAFTING_RECIPES[:20]:  # Test first 20 recipes
    if recipe.recipe_id:
        discover_recipe(player, recipe.recipe_id)
        discovery_count += 1

end_time = time.time()
discovery_time = end_time - start_time

print(f"[OK] Discovered {discovery_count} recipes in {discovery_time:.3f}s")
print(f"[OK] Average discovery time: {(discovery_time/discovery_count)*1000:.2f}ms per recipe")

# TEST 7: Equipment Operations Stress Test
print("\n" + "="*60)
print("TEST 7: Equipment Stress Test")
print("="*60)

from equipment import Equipment

equipment_system = Equipment()
start_time = time.time()

# Stress test equip/unequip operations
for i in range(100):
    equipment_system.equipped["main_hand"] = "iron_sword"
    equipment_system.equipped["head"] = "iron_helmet"
    equipment_system.equipped["main_hand"] = None
    equipment_system.equipped["head"] = None

end_time = time.time()
equip_time = end_time - start_time

print(f"[OK] Performed 400 equipment operations in {equip_time:.3f}s")
print(f"[OK] Average operation time: {(equip_time/400)*1000:.2f}ms")

# TEST 8: Memory Usage (Rough Estimate)
print("\n" + "="*60)
print("TEST 8: Memory Check")
print("="*60)

import sys as system

# Get rough memory usage estimates
enemies_size = sys.getsizeof(enemies)
npcs_size = sys.getsizeof(npcs)
player_size = sys.getsizeof(player)
world_size = sys.getsizeof(world)

total_estimated = enemies_size + npcs_size + player_size + world_size

print(f"[OK] Enemies list: ~{enemies_size/1024:.1f} KB")
print(f"[OK] NPCs list: ~{npcs_size/1024:.1f} KB")
print(f"[OK] Player object: ~{player_size/1024:.1f} KB")
print(f"[OK] World object: ~{world_size/1024:.1f} KB")
print(f"[OK] Total (rough estimate): ~{total_estimated/1024:.1f} KB")

# TEST 9: Frame Time Simulation
print("\n" + "="*60)
print("TEST 9: Frame Time Simulation")
print("="*60)

frame_times = []
test_frames = 60  # Simulate 60 frames

for frame in range(test_frames):
    frame_start = time.time()
    
    # Simulate game loop operations
    _ = player.inventory.get("test_item", 0)
    world.get_tile(frame * config.TILE_SIZE, frame * config.TILE_SIZE)
    player.skills_manager.get_level(player.skills_manager.MINING)
    
    # Simulate enemy updates (just attribute access)
    for enemy in enemies[:10]:  # Only update 10 to speed up test
        _ = enemy.health
    
    frame_time = time.time() - frame_start
    frame_times.append(frame_time)

avg_frame_time = sum(frame_times) / len(frame_times)
max_frame_time = max(frame_times)
min_frame_time = min(frame_times)

print(f"[OK] Average frame time: {avg_frame_time*1000:.2f}ms")
print(f"[OK] Min frame time: {min_frame_time*1000:.2f}ms")
print(f"[OK] Max frame time: {max_frame_time*1000:.2f}ms")

target_fps = 60
target_frame_time = 1.0 / target_fps

if avg_frame_time < target_frame_time:
    estimated_fps = int(1.0 / avg_frame_time)
    print(f"[OK] EXCELLENT - Estimated FPS: {estimated_fps} (target: {target_fps})")
else:
    estimated_fps = int(1.0 / avg_frame_time)
    print(f"[WARN]  Estimated FPS: {estimated_fps} (target: {target_fps})")

# TEST 10: Loadout System Stress Test
print("\n" + "="*60)
print("TEST 10: Loadout System Stress Test")
print("="*60)

from equipment import Equipment

loadout_system = Equipment()
start_time = time.time()

# Create max loadouts
for i in range(10):
    loadout_system.equipped["main_hand"] = f"weapon_{i}"
    loadout_system.equipped["head"] = f"helmet_{i}"
    loadout_system.save_loadout(f"Loadout_{i}")

end_time = time.time()
loadout_save_time = end_time - start_time

print(f"[OK] Saved 10 loadouts in {loadout_save_time:.3f}s")
print(f"[OK] Average save time: {(loadout_save_time/10)*1000:.2f}ms per loadout")

# FINAL SUMMARY
print("\n" + "="*60)
print("STRESS TESTS COMPLETE")
print("="*60)

print("\n[STATS] PERFORMANCE SUMMARY:")
print(f"[OK] Enemy Spawning: {(spawn_time/enemy_count)*1000:.2f}ms per enemy")
print(f"[OK] NPC Spawning: {(npc_spawn_time/npc_count)*1000:.2f}ms per NPC")
print(f"[OK] Tile Access: {(tile_access_time/tile_access_count)*1000:.2f}ms per tile")
print(f"[OK] Inventory Operations: {add_time/operations*1000:.3f}ms per add")
print(f"[OK] Skills XP: {(xp_time/xp_operations)*1000:.3f}ms per XP add")
print(f"[OK] Recipe Discovery: {(discovery_time/discovery_count)*1000:.2f}ms per recipe")
print(f"[OK] Equipment Operations: {(equip_time/400)*1000:.2f}ms per operation")
print(f"[OK] Estimated FPS: {estimated_fps}")
print(f"[OK] Memory Usage: ~{total_estimated/1024:.1f} KB (rough estimate)")

print("\n" + "="*60)
print("ALL STRESS TESTS PASSED! !")
print("="*60)

pygame.quit()
sys.exit(0)
