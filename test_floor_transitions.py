"""Test floor transition interaction in inn"""

from building_interior import BuildingInterior
from town_system import BuildingType

# Create inn
print("Creating inn with 2 floors...")
inn = BuildingInterior(BuildingType.INN)

# Simulate player on floor 1 near staircase
print(f"\nPlayer on floor {inn.current_floor}")
player_x = 360  # Near staircase at x=300
player_y = 650  # Near staircase at y=600

# Try to find nearby interactable (should find staircase)
print(f"\nLooking for interactables near player at ({player_x}, {player_y})...")
nearby = inn.get_nearby_interactable(player_x, player_y, max_distance=100)

if nearby:
    print(f"✓ Found: {nearby.name} (type: {nearby.type})")
    print(f"  Position: ({nearby.x}, {nearby.y})")
    print(f"  Floor: {nearby.floor}")
    print(f"  Target floor: {nearby.target_floor if hasattr(nearby, 'target_floor') else 'N/A'}")
    
    if nearby.type == "staircase":
        print(f"\n✓ Staircase detected! Attempting to change floor...")
        success = inn.change_floor(nearby.target_floor)
        if success:
            print(f"✓ SUCCESS! Now on floor {inn.current_floor}")
            
            # Check what's on this floor
            floor_2_objects = [o for o in inn.objects if hasattr(o, 'floor') and o.floor == 2]
            print(f"  Floor 2 has {len(floor_2_objects)} objects")
            
            room_doors = [o for o in floor_2_objects if o.type == "room_door"]
            print(f"  Including {len(room_doors)} room doors")
            
            # Try to find staircase going back down
            print(f"\nLooking for stairs back down...")
            nearby_down = inn.get_nearby_interactable(player_x, player_y, max_distance=100)
            if nearby_down and nearby_down.type == "staircase":
                print(f"✓ Found: {nearby_down.name} (goes to floor {nearby_down.target_floor})")
            else:
                print(f"✗ No staircase found at same position")
        else:
            print(f"✗ Failed to change floor")
    else:
        print(f"✗ Wrong type: {nearby.type}")
else:
    print(f"✗ No interactables found!")
    print(f"\nDebugging: All staircases in inn:")
    staircases = [o for o in inn.objects if o.type == "staircase"]
    for stair in staircases:
        print(f"  - {stair.name} at ({stair.x}, {stair.y}), floor {stair.floor}")

print(f"\n{'='*50}")
print("✅ Floor transition system test complete!")
