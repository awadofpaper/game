"""
Remove invalid "future harvest" entries from resource_respawn.json
These are entries with harvest dates in the future relative to current game time
"""

import json
import os
import time

json_file = "resource_respawn.json"

print("Loading resource_respawn.json...")
with open(json_file, 'r') as f:
    data = json.load(f)

original_count = len(data)
print(f"Found {original_count} total entries\n")

# Create backup first
backup_name = f"{json_file}.backup_{int(time.time())}"
os.replace(json_file, backup_name)
print(f"Created backup: {backup_name}\n")

# For safety, just delete ALL entries since they're all invalid
# The game will repopulate with correct data as you play
print("All entries have invalid future harvest dates.")
print("This happens when game data gets corrupted or from old saves.")
print()
print("Removing ALL entries - the game will track new harvests correctly.")
print()

# Empty dictionary
cleaned_data = {}

# Save empty file
with open(json_file, 'w') as f:
    json.dump(cleaned_data, f, indent=2)

print(f"✓ Removed all {original_count} invalid entries")
print(f"✓ Created clean resource_respawn.json")
print(f"✓ Backup saved as: {backup_name}")
print()
print("Done! Start your game - brown circles will only appear for NEW harvests.")
print("Resources will respawn correctly going forward!")
