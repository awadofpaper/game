"""
Diagnostic script to find problematic respawn entries
"""

import json
import time

# Mock classes to calculate progress
class MockGameTime:
    def __init__(self):
        # Use current values - you may need to adjust these
        self.day_count = 100  # Assume we're at day 100
        self.month_count = 3
        self.year_count = 0
        
    def get_season(self):
        return 'Summer'

class MockWeatherSystem:
    def get_current_weather(self):
        return ('Clear', 1.0)

# Load data
json_file = "resource_respawn.json"
with open(json_file, 'r') as f:
    data = json.load(f)

print(f"Total entries: {len(data)}\n")

# Base respawn times
base_respawn_times = {
    'tree': 14,
    'bush': 7,
    'grass': 3,
    'mushroom_patch': 9
}

# Check each entry
game_time = MockGameTime()
problem_entries = []
completed_entries = []

for coord_key, harvest_data in data.items():
    resource_type = harvest_data['type']
    base_days = base_respawn_times.get(resource_type, 7)
    
    # Calculate days passed
    harvest_year = harvest_data['harvested_year']
    harvest_month = harvest_data['harvested_month']
    harvest_day = harvest_data['harvested_day']
    
    days_passed = (game_time.year_count - harvest_year) * 360
    days_passed += (game_time.month_count - harvest_month) * 30
    days_passed += (game_time.day_count - harvest_day)
    
    if days_passed < 0:
        print(f"⚠️  FUTURE HARVEST at {coord_key}: days_passed = {days_passed}")
        print(f"    Harvest date: Year {harvest_year}, Month {harvest_month}, Day {harvest_day}")
        print(f"    Current date: Year {game_time.year_count}, Month {game_time.month_count}, Day {game_time.day_count}")
        problem_entries.append(coord_key)
        continue
    
    # Simple progress calculation
    progress = days_passed / base_days
    
    if progress >= 1.0:
        completed_entries.append({
            'coord': coord_key,
            'type': resource_type,
            'days_passed': days_passed,
            'progress': progress,
            'harvest_day': harvest_day
        })

print(f"\n{'='*60}")
print(f"COMPLETED ENTRIES (should have respawned already):")
print(f"{'='*60}")
if completed_entries:
    print(f"Found {len(completed_entries)} entries that should have respawned!\n")
    
    # Show first 10
    for i, entry in enumerate(completed_entries[:10]):
        print(f"{i+1}. {entry['coord']} - {entry['type']}")
        print(f"   Days passed: {entry['days_passed']}, Progress: {entry['progress']:.1%}")
        print(f"   Harvested on day: {entry['harvest_day']}")
        print()
    
    if len(completed_entries) > 10:
        print(f"... and {len(completed_entries) - 10} more")
else:
    print("None found - all entries are still growing!")

print(f"\n{'='*60}")
print("SUMMARY:")
print(f"{'='*60}")
print(f"Total entries: {len(data)}")
print(f"Problem entries (future harvests): {len(problem_entries)}")
print(f"Completed entries (should respawn): {len(completed_entries)}")
print(f"Still growing: {len(data) - len(problem_entries) - len(completed_entries)}")

if len(completed_entries) > 0:
    print(f"\n⚠️  WARNING: {len(completed_entries)} entries show progress >= 100%!")
    print("These should have been removed by check_respawns().")
    print("Possible causes:")
    print("1. check_respawns() isn't being called frequently enough")
    print("2. World tiles aren't being updated correctly")
    print("3. The JSON isn't being saved after respawning")
    print("\nThe graphics.py fix will now skip drawing these indicators.")
