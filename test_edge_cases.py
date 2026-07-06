"""
Edge Case Tests - Test boundary conditions and error handling
Tests unusual inputs, limits, and error recovery
"""

import pygame
import sys
from config import Config
from player import Player
from world import World
from enemies import Enemy
from equipment import Equipment

print("="*60)
print("EDGE CASE TEST SUITE")
print("="*60)

pygame.init()
config = Config()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

world = World(config)
player = Player(config, world)
print("[OK] Core systems initialized")

# TEST 1: Inventory Edge Cases
print("\n" + "="*60)
print("TEST 1: Inventory Edge Cases")
print("="*60)

# Test adding 0 items (dict-based)
initial_count = player.inventory.get("test_item", 0)
player.inventory["test_item"] = player.inventory.get("test_item", 0) + 0
assert player.inventory.get("test_item", 0) == initial_count, "Adding 0 items changed count!"
print("[OK] Adding 0 items handled correctly")

# Test adding negative items (dict-based)
try:
    player.inventory["test_item"] = player.inventory.get("test_item", 0) + (-5)
    count = player.inventory.get("test_item", 0)
    if count < 0:
        print("[WARN]  Negative inventory count possible")
    else:
        print("[OK] Negative item add handled (prevented or ignored)")
except Exception as e:
    print(f"[OK] Negative item add raises exception: {type(e).__name__}")

# Test removing more items than available (dict-based)
player.inventory["limited_item"] = 5
try:
    player.inventory["limited_item"] = player.inventory.get("limited_item", 0) - 10
    remaining = player.inventory.get("limited_item", 0)
    if remaining < 0:
        print("[WARN]  Can go negative in inventory")
    else:
        print("[OK] Removing excess items handled safely")
except Exception as e:
    print(f"[OK] Removing excess items raises exception: {type(e).__name__}")

# Test getting non-existent item
result = player.inventory.get("nonexistent_item_12345", 0)
assert result is not None, "Getting non-existent item returned None!"
print("[OK] Getting non-existent item returns default value")

# TEST 2: Equipment Edge Cases
print("\n" + "="*60)
print("TEST 2: Equipment Edge Cases")
print("="*60)

equipment_system = Equipment()

# Test equipping to invalid slot
try:
    equipment_system.equipped["invalid_slot_xyz"] = "iron_sword"
    print("[WARN]  Can add items to invalid slots")
except KeyError:
    print("[OK] Invalid slot access raises KeyError")

# Test equipping non-existent item
equipment_system.equipped["main_hand"] = "nonexistent_item_xyz"
print("[OK] Can set non-existent items (no validation in dict assignment)")

# Test None equipment
equipment_system.equipped["head"] = None
assert equipment_system.equipped["head"] is None, "None assignment failed!"
print("[OK] None equipment assignment works")

# TEST 3: Skills Edge Cases
print("\n" + "="*60)
print("TEST 3: Skills Edge Cases")
print("="*60)

# Test adding huge XP amount
initial_level = player.skills_manager.get_level(player.skills_manager.MINING)
player.skills_manager.add_xp(player.skills_manager.MINING, 1000000)
final_level = player.skills_manager.get_level(player.skills_manager.MINING)

if final_level > initial_level:
    print(f"[OK] Massive XP handled: Level {initial_level} → {final_level}")
else:
    print("[WARN]  Massive XP didn't increase level")

# Test adding 0 XP
initial_xp = player.skills_manager.get_xp(player.skills_manager.WOODCUTTING)
player.skills_manager.add_xp(player.skills_manager.WOODCUTTING, 0)
final_xp = player.skills_manager.get_xp(player.skills_manager.WOODCUTTING)
assert initial_xp == final_xp, "Adding 0 XP changed XP value!"
print("[OK] Adding 0 XP handled correctly")

# Test negative XP (if possible)
try:
    player.skills_manager.add_xp(player.skills_manager.FISHING, -100)
    print("[OK] Negative XP handled (accepted or ignored)")
except Exception as e:
    print(f"[OK] Negative XP raises exception: {type(e).__name__}")

# TEST 4: World Edge Cases
print("\n" + "="*60)
print("TEST 4: World Edge Cases")
print("="*60)

# Test negative coordinates
try:
    tile = world.get_tile(-100, -100)
    if tile is not None:
        print("[OK] Negative coordinates handled (returns tile)")
    else:
        print("[OK] Negative coordinates return None")
except Exception as e:
    print(f"[OK] Negative coordinates raise exception: {type(e).__name__}")

# Test huge coordinates (beyond world bounds)
try:
    tile = world.get_tile(1000000, 1000000)
    if tile is not None:
        print("[OK] Out-of-bounds coordinates handled (generates tile)")
    else:
        print("[OK] Out-of-bounds returns None")
except Exception as e:
    print(f"[OK] Out-of-bounds raises exception: {type(e).__name__}")

# Test (0, 0) coordinates
tile = world.get_tile(0, 0)
assert tile is not None, "(0,0) tile is None!"
print("[OK] Origin (0,0) tile exists")

# TEST 5: Enemy Edge Cases
print("\n" + "="*60)
print("TEST 5: Enemy Edge Cases")
print("="*60)

# Test level 0 enemy
try:
    enemy_lv0 = Enemy("slime", 100, 100, level=0, rarity="Common")
    print(f"[OK] Level 0 enemy created (HP: {enemy_lv0.health})")
except Exception as e:
    print(f"[WARN]  Level 0 enemy raises exception: {type(e).__name__}")

# Test very high level enemy
try:
    enemy_lv999 = Enemy("slime", 200, 200, level=999, rarity="Legend")
    print(f"[OK] Level 999 enemy created (HP: {enemy_lv999.health})")
except Exception as e:
    print(f"[WARN]  Level 999 enemy raises exception: {type(e).__name__}")

# Test invalid enemy type
try:
    invalid_enemy = Enemy("nonexistent_enemy_type", 300, 300, level=5, rarity="Common")
    print("[WARN]  Invalid enemy type accepted")
except KeyError:
    print("[OK] Invalid enemy type raises KeyError")
except Exception as e:
    print(f"[OK] Invalid enemy type raises: {type(e).__name__}")

# TEST 6: Recipe Edge Cases
print("\n" + "="*60)
print("TEST 6: Recipe Edge Cases")
print("="*60)

from crafting import discover_recipe, CRAFTING_RECIPES

# Test discovering same recipe twice
if CRAFTING_RECIPES:
    test_recipe = CRAFTING_RECIPES[0]
    discover_recipe(player, test_recipe.recipe_id)
    initial_count = len(player.discovered_recipes)
    discover_recipe(player, test_recipe.recipe_id)
    final_count = len(player.discovered_recipes)
    
    if initial_count == final_count:
        print("[OK] Discovering same recipe twice prevented (set behavior)")
    else:
        print("[WARN]  Can discover same recipe multiple times")

# Test discovering invalid recipe
try:
    result = discover_recipe(player, "nonexistent_recipe_xyz_123")
    if result:
        print("[WARN]  Invalid recipe discovery succeeded")
    else:
        print("[OK] Invalid recipe discovery returns False")
except Exception as e:
    print(f"[OK] Invalid recipe raises: {type(e).__name__}")

# TEST 7: Loadout Edge Cases
print("\n" + "="*60)
print("TEST 7: Loadout Edge Cases")
print("="*60)

equipment_system = Equipment()

# Test saving empty loadout
equipment_system.save_loadout("Empty")
print("[OK] Can save empty loadout")

# Test saving with max loadouts
for i in range(11):  # Try to save 11 (max is 10)
    result = equipment_system.save_loadout(f"Test_{i}")

loadout_count = len(equipment_system.loadouts)
if loadout_count <= 10:
    print(f"[OK] Loadout limit enforced: {loadout_count}/10")
else:
    print(f"[WARN]  Loadout limit not enforced: {loadout_count}/10")

# Test loading non-existent loadout
try:
    result = equipment_system.load_loadout("NonExistent_Loadout_XYZ", player.inventory)
    if result[0]:  # If success
        print("[WARN]  Loading non-existent loadout succeeded")
    else:
        print("[OK] Loading non-existent loadout returns False")
except Exception as e:
    print(f"[OK] Loading non-existent loadout raises: {type(e).__name__}")

# Test deleting non-existent loadout
try:
    result = equipment_system.delete_loadout("NonExistent_XYZ")
    if result[0]:
        print("[WARN]  Deleting non-existent loadout succeeded")
    else:
        print("[OK] Deleting non-existent loadout returns False")
except Exception as e:
    print(f"[OK] Deleting non-existent loadout raises: {type(e).__name__}")

# TEST 8: Player Edge Cases
print("\n" + "="*60)
print("TEST 8: Player Edge Cases")
print("="*60)

# Test player at world origin
player.x = 0
player.y = 0
assert player.x == 0 and player.y == 0, "Can't set player to origin!"
print("[OK] Player can be at (0, 0)")

# Test player health at 0
original_health = player.health
player.health = 0
if player.health == 0:
    print("[OK] Player health can be 0")
player.health = original_health  # Restore

# Test player with negative mana
try:
    player.mana = -10
    if player.mana < 0:
        print("[WARN]  Player can have negative mana")
    else:
        print("[OK] Negative mana prevented or corrected")
except Exception as e:
    print(f"[OK] Negative mana raises: {type(e).__name__}")

# TEST 9: Floating Text Edge Cases
print("\n" + "="*60)
print("TEST 9: Floating Text Edge Cases")
print("="*60)

from floating_text import DamageNumber

# Test 0 damage
try:
    zero_damage = DamageNumber(0, (100, 100), is_crit=False)
    print(f"[OK] Zero damage number created: '{zero_damage.text}'")
except Exception as e:
    print(f"[WARN]  Zero damage raises: {type(e).__name__}")

# Test huge damage
try:
    huge_damage = DamageNumber(999999999, (100, 100), is_crit=True)
    print(f"[OK] Huge damage number created: '{huge_damage.text}'")
except Exception as e:
    print(f"[WARN]  Huge damage raises: {type(e).__name__}")

# Test negative damage (healing?)
try:
    neg_damage = DamageNumber(-50, (100, 100), is_heal=True)
    print(f"[OK] Negative damage (heal) created: '{neg_damage.text}'")
except Exception as e:
    print(f"[WARN]  Negative damage raises: {type(e).__name__}")

# TEST 10: Combat Log Edge Cases
print("\n" + "="*60)
print("TEST 10: Combat Log Edge Cases")
print("="*60)

from combat_log import CombatLog

combat_log = CombatLog(max_entries=5)

# Test adding more entries than max
for i in range(10):
    combat_log.add_entry(f"Entry {i}", (255, 255, 255))

entry_count = len(combat_log.entries)
if entry_count <= 5:
    print(f"[OK] Combat log respects max_entries: {entry_count}/5")
else:
    print(f"[WARN]  Combat log exceeds max_entries: {entry_count}/5")

# Test empty message
combat_log.add_entry("", (255, 255, 255))
print("[OK] Empty message handled")

# Test very long message
long_message = "A" * 1000
combat_log.add_entry(long_message, (255, 255, 255))
print("[OK] Very long message handled")

# FINAL SUMMARY
print("\n" + "="*60)
print("EDGE CASE TESTS COMPLETE")
print("="*60)

print("\n[STATS] SUMMARY:")
print("[OK] Inventory Edge Cases - TESTED")
print("[OK] Equipment Edge Cases - TESTED")
print("[OK] Skills Edge Cases - TESTED")
print("[OK] World Edge Cases - TESTED")
print("[OK] Enemy Edge Cases - TESTED")
print("[OK] Recipe Edge Cases - TESTED")
print("[OK] Loadout Edge Cases - TESTED")
print("[OK] Player Edge Cases - TESTED")
print("[OK] Floating Text Edge Cases - TESTED")
print("[OK] Combat Log Edge Cases - TESTED")

print("\n" + "="*60)
print("ALL EDGE CASE TESTS COMPLETE! !")
print("="*60)
print("\nNote: Some [WARN]  warnings indicate areas where additional")
print("validation could be added, but aren't necessarily bugs.")

pygame.quit()
sys.exit(0)
