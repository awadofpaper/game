"""
Save Slot System - Manage multiple save slots
"""

import os
import json
import gzip
from datetime import datetime


class SaveSlot:
    """Represents a single save slot"""
    
    def __init__(self, slot_number):
        self.slot_number = slot_number
        # Support both legacy and enhanced save systems
        self.save_file = f"savegame_slot{slot_number}.json"
        self.save_file_compressed = f"savegame_slot{slot_number}.json.gz"
        self.world_file = f"world_slot{slot_number}.json"
        # Enhanced save system files
        self.enhanced_save_file = os.path.join("saves", f"save_slot_{slot_number}.pkl.gz")
        
    def exists(self):
        """Check if this save slot has data (checks both legacy and enhanced formats)"""
        # Check enhanced save system first
        if os.path.exists(self.enhanced_save_file):
            return True
        # Fall back to legacy format
        return os.path.exists(self.save_file_compressed) or os.path.exists(self.save_file)
    
    def get_info(self):
        """Get save slot information (character name, level, playtime, last saved)"""
        try:
            # Try enhanced save system first
            if os.path.exists(self.enhanced_save_file):
                import pickle
                with open(self.enhanced_save_file, 'rb') as f:
                    save_package = pickle.load(f)
                
                # Extract game data
                if isinstance(save_package, dict) and "data" in save_package:
                    data = save_package["data"]
                else:
                    data = save_package
                
                player_data = data.get('player', {})
                timestamp = os.path.getmtime(self.enhanced_save_file)
                last_saved = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
                
                return {
                    'name': player_data.get('name', 'Unknown'),
                    'level': player_data.get('level', 1),
                    'playtime': player_data.get('playtime', 0),
                    'dubloons': player_data.get('dubloons', 0),
                    'last_saved': last_saved,
                    'slot_number': self.slot_number
                }
            
            # Fall back to legacy format
            if os.path.exists(self.save_file_compressed):
                with open(self.save_file_compressed, 'rb') as f:
                    compressed = f.read()
                serialized = gzip.decompress(compressed)
                data = json.loads(serialized.decode('utf-8'))
            elif os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
            else:
                return None
            
            player_data = data.get('player', {})
            
            # Get last modified time
            if os.path.exists(self.save_file_compressed):
                timestamp = os.path.getmtime(self.save_file_compressed)
            else:
                timestamp = os.path.getmtime(self.save_file)
            
            last_saved = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
            
            return {
                'name': player_data.get('name', 'Unknown'),
                'level': player_data.get('level', 1),
                'playtime': player_data.get('playtime', 0),
                'dubloons': player_data.get('dubloons', 0),
                'last_saved': last_saved,
                'slot_number': self.slot_number
            }
        except Exception as e:
            print(f"Error reading save slot {self.slot_number}: {e}")
            return None
    
    def delete(self):
        """Delete this save slot (both legacy and enhanced formats)"""
        try:
            deleted_any = False
            # Delete enhanced save file
            if os.path.exists(self.enhanced_save_file):
                os.remove(self.enhanced_save_file)
                deleted_any = True
            # Also try backup
            enhanced_backup = self.enhanced_save_file + ".backup"
            if os.path.exists(enhanced_backup):
                os.remove(enhanced_backup)
            # Delete legacy files
            if os.path.exists(self.save_file):
                os.remove(self.save_file)
                deleted_any = True
            if os.path.exists(self.save_file_compressed):
                os.remove(self.save_file_compressed)
                deleted_any = True
            if os.path.exists(self.world_file):
                os.remove(self.world_file)
                deleted_any = True
            return deleted_any
        except Exception as e:
            print(f"Error deleting save slot {self.slot_number}: {e}")
            return False


class SaveSlotManager:
    """Manages all save slots"""
    
    def __init__(self, num_slots=5):
        self.num_slots = num_slots
        self.slots = [SaveSlot(i+1) for i in range(num_slots)]
        self.current_slot = None
    
    def get_all_slots(self):
        """Get information for all save slots"""
        slot_info = []
        for slot in self.slots:
            info = slot.get_info()
            if info:
                slot_info.append(info)
            else:
                slot_info.append({
                    'name': 'Empty Slot',
                    'level': None,
                    'playtime': None,
                    'dubloons': None,
                    'last_saved': None,
                    'slot_number': slot.slot_number
                })
        return slot_info
    
    def select_slot(self, slot_number):
        """Select a slot for saving/loading"""
        if 1 <= slot_number <= self.num_slots:
            self.current_slot = self.slots[slot_number - 1]
            return self.current_slot
        return None
    
    def has_any_saves(self):
        """Check if there are any save files at all"""
        return any(slot.exists() for slot in self.slots)
    
    def get_slot(self, slot_number):
        """Get a specific slot"""
        if 1 <= slot_number <= self.num_slots:
            return self.slots[slot_number - 1]
        return None


def format_playtime(seconds):
    """Format playtime in hours and minutes"""
    if seconds is None:
        return "N/A"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
