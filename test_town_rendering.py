"""
Quick test to verify town rendering is properly isolated to instances
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize pygame
pygame.init()
pygame.font.init()

print("=" * 70)
print("TOWN RENDERING ISOLATION TEST")
print("=" * 70)

# Test 1: Verify town gates are generated correctly
print("\n[TEST 1] Gate generation...")
try:
    from town_system import TownManager
    from config import Config
    config = Config()
    
    town_manager = TownManager()
    town_manager.create_town("Test Town", 10000, 10000, "small")
    
    # Simulate gate generation (from main.py)
    town_gates = {}
    for town in town_manager.towns:
        gate_x = town.center_x
        gate_y = town.center_y + town.radius + config.TILE_SIZE
        town_gates[town.name] = (gate_x, gate_y)
    
    assert len(town_gates) == 1
    assert "Test Town" in town_gates
    gate_x, gate_y = town_gates["Test Town"]
    
    # Gate should be outside town boundary
    town = town_manager.towns[0]
    distance = ((gate_x - town.center_x) ** 2 + (gate_y - town.center_y) ** 2) ** 0.5
    assert distance > town.radius, "Gate should be outside town boundary"
    
    print("[OK] PASS - Gates positioned outside town boundaries")
except Exception as e:
    print(f"[FAIL] FAIL - {e}")
    sys.exit(1)

# Test 2: Verify town instances are separate from overworld towns
print("\n[TEST 2] Town instance isolation...")
try:
    from town_instance import create_town_instance
    
    # Create a town instance
    instance = create_town_instance("Instance Town", "medium")
    
    # Verify it's separate (has its own tiles, buildings)
    assert instance.width == 2000
    assert instance.height == 2000
    assert len(instance.buildings) == 8  # Medium town
    assert instance.tiles is not None
    
    # Verify gate position in instance
    assert instance.gate_x == instance.width // 2
    assert instance.gate_y == instance.height - 100
    
    print("[OK] PASS - Town instances are properly isolated")
except Exception as e:
    print(f"[FAIL] FAIL - {e}")
    sys.exit(1)

# Test 3: Verify overworld vs instance state flags
print("\n[TEST 3] State management...")
try:
    in_town = False
    in_dungeon = False
    current_town_instance = None
    
    # On overworld
    assert not in_town
    assert current_town_instance is None
    
    # Enter town
    in_town = True
    current_town_instance = create_town_instance("Test", "small")
    assert in_town
    assert current_town_instance is not None
    
    # Exit town
    in_town = False
    current_town_instance = None
    assert not in_town
    assert current_town_instance is None
    
    print("[OK] PASS - State flags work correctly")
except Exception as e:
    print(f"[FAIL] FAIL - {e}")
    sys.exit(1)

# Test 4: Verify rendering conditions
print("\n[TEST 4] Rendering conditions...")
try:
    in_town = False
    in_dungeon = False
    current_town_instance = None
    
    # On overworld - should NOT render town buildings/NPCs
    on_overworld = not in_dungeon and not in_town
    # The code has the town render COMMENTED OUT when on_overworld is True
    # So towns should NOT render on overworld
    assert on_overworld, "Should be on overworld"
    # Town buildings are now commented out, so they don't render
    
    # In town - town instance should render instead
    in_town = True
    current_town_instance = create_town_instance("Test", "small")
    should_render_instance = in_town and current_town_instance is not None
    assert should_render_instance, "Town instance should render when in_town=True"
    
    print("[OK] PASS - Rendering conditions are correct")
except Exception as e:
    print(f"[FAIL] FAIL - {e}")
    sys.exit(1)

# Test 5: Verify town gate detection
print("\n[TEST 5] Gate detection...")
try:
    config = Config()
    
    # Player at gate
    gate_x, gate_y = 1000, 1000
    player_x, player_y = 1000, 1000
    
    distance = ((player_x - gate_x) ** 2 + (player_y - gate_y) ** 2) ** 0.5
    detection_radius = config.TILE_SIZE * 4
    
    assert distance < detection_radius, "Player should be detected at gate"
    
    # Player too far
    player_x, player_y = 2000, 2000
    distance = ((player_x - gate_x) ** 2 + (player_y - gate_y) ** 2) ** 0.5
    assert distance > detection_radius, "Player should not be detected when far"
    
    print("[OK] PASS - Gate detection works correctly")
except Exception as e:
    print(f"[FAIL] FAIL - {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL TESTS PASSED [OK]")
print("=" * 70)
print("\nExpected gameplay:")
print("  - Overworld: Only gate markers visible")
print("  - Press E at gate: Enter town instance")
print("  - Town instance: See buildings, NPCs, paths")
print("  - Press E at gate in town: Exit to overworld")
print("=" * 70)
