"""
Quick test to verify World serialization works
"""
from config import Config
from world import World

# Create world
config = Config()
world = World(config)

# Modify world state by accessing some tiles
tile1 = world.get_tile(100, 200)
tile2 = world.get_tile(500, 600)
tile3 = world.get_tile(1000, 1000)

print(f"Original World State:")
print(f"  Width: {world.width}")
print(f"  Height: {world.height}")
print(f"  Seed: {world.seed}")
print(f"  Tiles loaded: {len(world.tiles)}")
print()

# Serialize
world_data = world.to_dict()
print(f"[OK] Serialized to dict with {len(world_data)} keys")
print(f"  Keys: {list(world_data.keys())}")
print(f"  Changed tiles saved: {len(world_data['tiles'])}")
print()

# Verify structure
success = True
if 'width' not in world_data:
    print("[FAIL] Missing 'width' in serialized data")
    success = False
if 'height' not in world_data:
    print("[FAIL] Missing 'height' in serialized data")
    success = False
if 'seed' not in world_data:
    print("[FAIL] Missing 'seed' in serialized data")
    success = False
if 'tiles' not in world_data:
    print("[FAIL] Missing 'tiles' in serialized data")
    success = False

if success:
    print("[OK] ALL REQUIRED FIELDS PRESENT - World serialization successful! !")
else:
    print("[FAIL] Some fields missing from serialization")
