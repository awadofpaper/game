"""
Cleanup script to remove invalid respawn entries
This removes entries where the resource has already respawned (progress >= 100%)
"""

import json
import time

# Configuration
json_file = "resource_respawn.json"

print("Loading resource_respawn.json...")
with open(json_file, 'r') as f:
    data = json.load(f)

original_count = len(data)
print(f"Found {original_count} harvest entries")

# We'll keep ALL entries since we can't check the actual game world state from here
# Instead, the game's check_respawns() method should handle cleanup
# But we can remove entries that are clearly invalid (missing required fields)

filtered_data = {}
invalid_count = 0

for coord_key, harvest_info in data.items():
    # Validate entry has required fields
    required_fields = ['type', 'harvested_day', 'harvested_month', 'harvested_year']
    
    has_all_fields = all(field in harvest_info for field in required_fields)
    
    # Validate resource type is respawnable
    resource_type = harvest_info.get('type', '')
    respawnable_types = ('tree', 'bush', 'mushroom', 'mushroom_patch', 'grass')
    is_valid_type = resource_type in respawnable_types
    
    if has_all_fields and is_valid_type:
        filtered_data[coord_key] = harvest_info
    else:
        invalid_count += 1
        print(f"  Removing invalid entry at {coord_key}: {harvest_info}")

kept_count = len(filtered_data)

if invalid_count > 0:
    # Create backup
    import os
    backup_name = f"{json_file}.backup_{int(time.time())}"
    os.replace(json_file, backup_name)
    print(f"Created backup: {backup_name}")
    
    # Write cleaned data
    with open(json_file, 'w') as f:
        json.dump(filtered_data, f, indent=2)
    
    print(f"Removed {invalid_count} invalid entries")
    print(f"Kept {kept_count} valid entries")
    print(f"Wrote cleaned data to {json_file}")
else:
    print("No invalid entries found - data is clean!")

print("\nDone!")
print("\nNote: The game's check_respawns() method will automatically")
print("remove entries when resources fully respawn during gameplay.")
