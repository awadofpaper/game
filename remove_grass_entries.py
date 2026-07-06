"""
Remove grass harvest entries from resource_respawn.json
Grass doesn't respawn, so these entries just clutter the data.
"""
import json
import os

json_file = "resource_respawn.json"

if not os.path.exists(json_file):
    print(f"Error: {json_file} not found")
    exit(1)

# Load the data
print(f"Loading {json_file}...")
with open(json_file, 'r') as f:
    data = json.load(f)

original_count = len(data)
print(f"Found {original_count} harvest entries")

# Filter out grass entries
filtered_data = {}
grass_count = 0
for coord_key, harvest_info in data.items():
    resource_type = harvest_info.get('type', '')
    if resource_type == 'grass':
        grass_count += 1
    else:
        filtered_data[coord_key] = harvest_info

print(f"Removed {grass_count} grass entries")
print(f"Kept {len(filtered_data)} resource entries (trees, bushes, mushrooms)")

# Create backup
backup_file = f"{json_file}.backup_no_grass"
if os.path.exists(json_file):
    os.replace(json_file, backup_file)
    print(f"Created backup: {backup_file}")

# Write cleaned data
with open(json_file, 'w') as f:
    json.dump(filtered_data, f, indent=2)

print(f"Wrote cleaned data to {json_file}")
print("Done!")
