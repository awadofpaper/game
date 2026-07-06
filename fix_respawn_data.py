"""
Script to fix coordinate formatting in resource_respawn.json
This normalizes all keys to use integer coordinates (e.g., "52364,51844" instead of "52364.0,51844.0")
"""
import json
import os

json_file = "resource_respawn.json"

print(f"Loading {json_file}...")
if not os.path.exists(json_file):
    print(f"File {json_file} not found!")
    exit(1)

with open(json_file, 'r') as f:
    data = json.load(f)

print(f"Found {len(data)} harvest entries")
print("Normalizing coordinate keys...")

# Create new dictionary with normalized keys
normalized_data = {}
fixed_count = 0

for old_key, harvest_info in data.items():
    # Parse coordinates (handle both int and float formats)
    try:
        coord_parts = old_key.split(',')
        x = int(float(coord_parts[0]))
        y = int(float(coord_parts[1]))
        new_key = f"{x},{y}"
        
        # Only keep the entry if the key format changed or it's the first occurrence
        if new_key not in normalized_data:
            normalized_data[new_key] = harvest_info
            if old_key != new_key:
                fixed_count += 1
        else:
            # Duplicate found - keep the newer one (higher harvest_time)
            if harvest_info.get('harvest_time', 0) > normalized_data[new_key].get('harvest_time', 0):
                normalized_data[new_key] = harvest_info
                print(f"  Replaced duplicate at {new_key}")
    except Exception as e:
        print(f"  Warning: Could not parse key '{old_key}': {e}")

print(f"\nNormalized {fixed_count} keys")
print(f"Removed {len(data) - len(normalized_data)} duplicate entries")
print(f"Final count: {len(normalized_data)} entries")

# Backup original file
backup_file = "resource_respawn.json.backup"
print(f"\nCreating backup: {backup_file}")
os.replace(json_file, backup_file)

# Write normalized data
print(f"Writing normalized data to {json_file}...")
with open(json_file, 'w') as f:
    json.dump(normalized_data, f)

print("Done! The game should now properly track respawning resources.")
print("If any issues occur, restore the backup file.")
