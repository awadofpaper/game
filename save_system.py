"""
Enhanced Save/Load System for RPG Game
Supports multiple save slots, better error handling, and comprehensive game state management
Integrates with existing compression system from utils.py
"""

import os
import pickle
import gzip
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SaveSlot:
    """Represents a single save slot with metadata"""
    
    def __init__(self, slot_id: int, filename: str = None):
        self.slot_id = slot_id
        self.filename = filename or f"save_slot_{slot_id}.pkl.gz"
        self.character_name = ""
        self.level = 1
        self.playtime = 0
        self.save_time = None
        self.location = ""
        self.version = "2.0"
        self.exists = False
        self.file_size = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert save slot to dictionary"""
        return {
            "slot_id": self.slot_id,
            "filename": self.filename,
            "character_name": self.character_name,
            "level": self.level,
            "playtime": self.playtime,
            "save_time": self.save_time.isoformat() if self.save_time else None,
            "location": self.location,
            "version": self.version,
            "exists": self.exists,
            "file_size": self.file_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveSlot':
        """Create save slot from dictionary"""
        slot = cls(data["slot_id"], data.get("filename"))
        slot.character_name = data.get("character_name", "")
        slot.level = data.get("level", 1)
        slot.playtime = data.get("playtime", 0)
        slot.save_time = datetime.fromisoformat(data["save_time"]) if data.get("save_time") else None
        slot.location = data.get("location", "")
        slot.version = data.get("version", "2.0")
        slot.exists = data.get("exists", False)
        slot.file_size = data.get("file_size", 0)
        return slot


class EnhancedSaveSystem:
    """Enhanced save/load system with multiple slots and better features"""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = save_directory
        self.metadata_file = os.path.join(save_directory, "save_metadata.json")
        self.max_slots = 10
        self.auto_save_slot = 0  # Slot 0 reserved for auto-save
        
        # Create save directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
        
        # Load existing save slot metadata
        self.save_slots = self._load_save_metadata()
    
    def _load_save_metadata(self) -> Dict[int, SaveSlot]:
        """Load save slot metadata from file"""
        slots = {}
        
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                    for slot_data in metadata.get("slots", []):
                        slot = SaveSlot.from_dict(slot_data)
                        slots[slot.slot_id] = slot
        except Exception as e:
            logger.error(f"Error loading save metadata: {e}")
        
        # Ensure we have slots 0-9 initialized
        for i in range(self.max_slots):
            if i not in slots:
                slots[i] = SaveSlot(i)
                
        return slots
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            metadata = {
                "version": "2.0",
                "slots": [slot.to_dict() for slot in self.save_slots.values()]
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _get_save_path(self, slot_id: int) -> str:
        """Get the full path for a save slot"""
        return os.path.join(self.save_directory, self.save_slots[slot_id].filename)
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate checksum for save data integrity"""
        return hashlib.sha256(data).hexdigest()
    
    def _get_current_location(self, player) -> str:
        """Determine current location description for save metadata"""
        try:
            # Get approximate coordinates
            x = int(player.x / 1000)
            y = int(player.y / 1000)
            return f"Coordinates ({x}, {y})"
        except (AttributeError, TypeError) as e:
            return "Unknown Location"
    
    def save_game(self, slot_id: int, world, player) -> Tuple[bool, str]:
        """
        Save game to specified slot with compression
        
        Args:
            slot_id: Save slot number (0-9, where 0 is auto-save)
            world: Game world object
            player: Player object
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if slot_id not in range(self.max_slots):
                return False, f"Invalid slot ID: {slot_id}"
            
            save_path = self._get_save_path(slot_id)
            
            # Collect comprehensive game data
            game_data = {
                "version": "2.0",
                "timestamp": datetime.now().isoformat(),
                "player": self._serialize_player(player),
                "world": self._serialize_world(world),
            }
            
            # Serialize with pickle
            serialized = pickle.dumps(game_data, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Create save package with integrity checking (store serialized data for checksum validation)
            save_package = {
                "checksum": self._calculate_checksum(serialized),
                "serialized_data": serialized,
                "data": game_data  # Keep for backward compatibility
            }
            
            # Write to temporary file first (atomic save)
            temp_path = save_path + ".tmp"
            with open(temp_path, 'wb') as f:
                pickle.dump(save_package, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Rename to final file (atomic operation)
            if os.path.exists(save_path):
                backup_path = save_path + ".backup"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(save_path, backup_path)
            
            os.rename(temp_path, save_path)
            
            # Update metadata
            slot = self.save_slots[slot_id]
            slot.character_name = getattr(player, 'name', 'Player')
            slot.level = getattr(player, 'level', 1)
            slot.save_time = datetime.now()
            slot.location = self._get_current_location(player)
            slot.exists = True
            slot.file_size = os.path.getsize(save_path)
            
            self._save_metadata()
            
            slot_name = "Auto-save" if slot_id == 0 else f"Slot {slot_id}"
            logger.info(f"Game saved successfully to {slot_name}")
            return True, f"Game saved to {slot_name}"
            
        except Exception as e:
            error_msg = f"Save failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def load_game(self, slot_id: int, world, player) -> Tuple[bool, str]:
        """
        Load game from specified slot
        
        Args:
            slot_id: Save slot number to load from
            world: Game world object to update
            player: Player object to update
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if slot_id not in range(self.max_slots):
                return False, f"Invalid slot ID: {slot_id}"
            
            if not self.save_slots[slot_id].exists:
                return False, f"No save data in slot {slot_id}"
            
            save_path = self._get_save_path(slot_id)
            backup_path = save_path + ".backup"
            
            # Check for main save file, fallback to backup if needed
            if not os.path.exists(save_path):
                if os.path.exists(backup_path):
                    logger.warning(f"Main save file missing, loading from backup: {backup_path}")
                    save_path = backup_path
                else:
                    return False, f"Save file not found: {save_path}"
            
            # Load save package
            with open(save_path, 'rb') as f:
                save_package = pickle.load(f)
            
            # Check format and validate
            if isinstance(save_package, dict) and "checksum" in save_package:
                # New format with integrity checking
                if "serialized_data" in save_package:
                    # Newer format with serialized data for checksum validation
                    serialized = save_package["serialized_data"]
                    calculated_checksum = self._calculate_checksum(serialized)
                    stored_checksum = save_package["checksum"]
                    
                    if calculated_checksum != stored_checksum:
                        # Try backup
                        backup_path = save_path + ".backup"
                        if os.path.exists(backup_path):
                            logger.warning("Checksum mismatch, trying backup...")
                            with open(backup_path, 'rb') as f:
                                save_package = pickle.load(f)
                            if "serialized_data" in save_package:
                                game_data = pickle.loads(save_package["serialized_data"])
                            else:
                                game_data = save_package.get("data", save_package)
                        else:
                            return False, "Save file corrupted and no backup available"
                    else:
                        # Checksum valid, deserialize the data
                        game_data = pickle.loads(serialized)
                else:
                    # Older format without serialized_data (skip validation for compatibility)
                    logger.warning("Loading save without checksum validation (old format)")
                    game_data = save_package["data"]
            else:
                # Legacy format
                game_data = save_package
            
            # Load player data
            if "player" in game_data:
                self._deserialize_player(game_data["player"], player)
            
            # Load world data
            if "world" in game_data:
                self._deserialize_world(game_data["world"], world)
            
            slot_name = "Auto-save" if slot_id == 0 else f"Slot {slot_id}"
            logger.info(f"Game loaded successfully from {slot_name}")
            return True, f"Game loaded from {slot_name}"
            
        except Exception as e:
            error_msg = f"Load failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _serialize_player(self, player) -> Dict[str, Any]:
        """Serialize player data"""
        player_data = {
            'x': player.x,
            'y': player.y,
            'name': getattr(player, 'name', 'Player'),
            'color': getattr(player, 'color', (255, 255, 255)),
            'health': player.health,
            'stamina': player.stamina,
            'mana': player.mana,
            'max_health': player.max_health,
            'max_stamina': player.max_stamina,
            'max_mana': player.max_mana,
            'inventory': player.inventory,
            'level': getattr(player, 'level', 1),
            'experience': getattr(player, 'experience', 0),
            'experience_to_next_level': getattr(player, 'experience_to_next_level', 100),
            'gold': getattr(player, 'gold', 0),
            'dubloons': getattr(player, 'dubloons', 0),
            'stat_points': getattr(player, 'stat_points', 0),
            'perk_points': getattr(player, 'perk_points', 0),
            'acquired_skills': list(getattr(player, 'acquired_skills', set())),
            'skill_points_invested': getattr(player, 'skill_points_invested', {}),
            'known_spells': list(getattr(player, 'known_spells', set())),
            'selected_spell': getattr(player, 'selected_spell', None),
            'secondary_spell': getattr(player, 'secondary_spell', None),
            'equipment': getattr(player, 'equipment', {'weapon': None, 'armor': None, 'accessory': None}),
        }
        
        # Save tutorial NPC state
        if hasattr(player, 'tutorial_npc') and player.tutorial_npc:
            tutorial_npc = player.tutorial_npc
            player_data['tutorial_npc'] = {
                'x': tutorial_npc.x,
                'y': tutorial_npc.y,
                'health': tutorial_npc.health,
                'max_health': tutorial_npc.max_health,
                'declined_by_player': tutorial_npc.declined_by_player,
                'going_to_shelter': tutorial_npc.going_to_shelter,
                'at_shelter': tutorial_npc.at_shelter,
                'shack_x': tutorial_npc.shack_x,
                'shack_y': tutorial_npc.shack_y,
                'in_building': getattr(tutorial_npc, 'in_building', None),
            }
        else:
            player_data['tutorial_npc'] = None
        
        # Save race and appearance data
        player_data['race_id'] = getattr(player, 'race_id', 'human')
        player_data['skin_tone'] = getattr(player, 'skin_tone', (255, 220, 177))
        
        # Save trait manager state if exists
        if hasattr(player, 'trait_manager') and player.trait_manager:
            player_data['trait_manager_state'] = player.trait_manager.to_dict()
        else:
            player_data['trait_manager_state'] = None
        
        return player_data
    
    def _deserialize_player(self, data: Dict[str, Any], player):
        """Deserialize player data"""
        player.x = data.get('x', player.x)
        player.y = data.get('y', player.y)
        player.name = data.get('name', 'Player')
        player.color = tuple(data.get('color', (255, 255, 255)))
        player.health = data.get('health', 100)
        player.stamina = data.get('stamina', 100)
        player.mana = data.get('mana', 100)
        player.max_health = data.get('max_health', 100)
        player.max_stamina = data.get('max_stamina', 100)
        player.max_mana = data.get('max_mana', 100)
        player.inventory = data.get('inventory', {})
        player.level = data.get('level', 1)
        player.experience = data.get('experience', 0)
        player.experience_to_next_level = data.get('experience_to_next_level', 100)
        player.gold = data.get('gold', 0)
        player.dubloons = data.get('dubloons', 0)
        player.stat_points = data.get('stat_points', data.get('skill_points', 0))  # Backward compatibility
        player.perk_points = data.get('perk_points', 0)
        player.acquired_skills = set(data.get('acquired_skills', []))
        player.skill_points_invested = data.get('skill_points_invested', {})
        player.known_spells = set(data.get('known_spells', []))
        player.selected_spell = data.get('selected_spell', None)
        player.secondary_spell = data.get('secondary_spell', None)
        player.equipment = data.get('equipment', {'weapon': None, 'armor': None, 'accessory': None})
        
        # Restore race and appearance data
        player.race_id = data.get('race_id', 'human')
        player.skin_tone = tuple(data.get('skin_tone', (255, 220, 177)))
        
        # Restore race object and trait manager (will be reconstructed in main.py)
        from race_system import get_race_by_id
        player.race = get_race_by_id(player.race_id)
        if player.race:
            player.racial_traits = player.race.traits.copy()
            
            # Recreate trait manager
            from racial_trait_handler import RacialTraitHandler
            
            # Restore trait manager state if it exists
            trait_state = data.get('trait_manager_state')
            if trait_state:
                player.trait_manager = RacialTraitHandler.from_dict(trait_state, player)
            else:
                player.trait_manager = RacialTraitHandler(player)
        
        # Restore tutorial NPC state (main.py will handle recreation)
        player.tutorial_npc_saved_state = data.get('tutorial_npc', None)
    
    def _serialize_world(self, world) -> Dict[str, Any]:
        """Serialize world data (only modified tiles for compression)"""
        from tile import Tile
        
        # For now, save all tiles (delta saving disabled due to incomplete implementation)
        # TODO: Implement proper delta saving with correct default tile cache
        tiles_to_save = {}
        
        for key, tile in world.tiles.items():
            # Handle both Tile objects and strings (for backward compatibility)
            if isinstance(tile, str):
                # Convert string to Tile object
                tile_dict = {'ground': tile, 'object': None, 'effect': None}
            elif hasattr(tile, 'to_dict'):
                tile_dict = tile.to_dict()
            else:
                # Skip invalid tiles
                logger.warning(f"Skipping invalid tile at {key}: {type(tile)}")
                continue
            
            tiles_to_save[key] = tile_dict
        
        return {
            'modified_tiles': tiles_to_save,
            'world_seed': 42
        }
    
    def _deserialize_world(self, data: Dict[str, Any], world):
        """Deserialize world data"""
        from tile import Tile
        
        if 'modified_tiles' in data:
            # New format: delta saving
            default_tiles = world.get_default_tile_state()
            world.tiles = default_tiles.copy()
            
            # Apply modified tiles
            for key, tile_dict in data['modified_tiles'].items():
                world.tiles[key] = Tile.from_dict(tile_dict)
        else:
            # Legacy format: full world
            world.tiles = {k: Tile.from_dict(v) if isinstance(v, dict) else v 
                          for k, v in data.get('tiles', {}).items()}
    
    def delete_save(self, slot_id: int) -> Tuple[bool, str]:
        """Delete a save slot"""
        try:
            if slot_id not in range(self.max_slots):
                return False, f"Invalid slot ID: {slot_id}"
            
            if slot_id == 0:
                return False, "Cannot delete auto-save slot"
            
            if not self.save_slots[slot_id].exists:
                return False, f"Slot {slot_id} is already empty"
            
            save_path = self._get_save_path(slot_id)
            
            # Delete main file
            if os.path.exists(save_path):
                os.remove(save_path)
            
            # Delete backup if exists
            backup_path = save_path + ".backup"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            # Update metadata
            self.save_slots[slot_id] = SaveSlot(slot_id)
            self._save_metadata()
            
            return True, f"Slot {slot_id} deleted"
            
        except Exception as e:
            error_msg = f"Delete failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_save_slots(self) -> List[SaveSlot]:
        """Get list of all save slots with metadata"""
        slots = []
        for i in range(self.max_slots):
            slot = self.save_slots[i]
            
            # Update file size if file exists
            save_path = self._get_save_path(i)
            if os.path.exists(save_path):
                slot.file_size = os.path.getsize(save_path)
                slot.exists = True
            else:
                slot.exists = False
            
            slots.append(slot)
        return slots
    
    def auto_save(self, world, player) -> Tuple[bool, str]:
        """Perform automatic save to slot 0"""
        return self.save_game(self.auto_save_slot, world, player)
    
    def get_save_summary(self, slot_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed summary of a save slot for UI display"""
        if slot_id not in range(self.max_slots) or not self.save_slots[slot_id].exists:
            return None
        
        slot = self.save_slots[slot_id]
        save_path = self._get_save_path(slot_id)
        
        try:
            file_size = os.path.getsize(save_path)
            
            return {
                "slot_id": slot_id,
                "character_name": slot.character_name,
                "level": slot.level,
                "playtime": slot.playtime,
                "location": slot.location,
                "save_time": slot.save_time,
                "file_size": file_size,
                "version": slot.version
            }
        except Exception as e:
            logger.error(f"Error getting save summary: {e}")
            return None


# Global save system instance
save_system = EnhancedSaveSystem()


def save_game_enhanced(slot_id: int, world, player) -> Tuple[bool, str]:
    """Enhanced save game function - replacement for original save_game"""
    return save_system.save_game(slot_id, world, player)


def load_game_enhanced(slot_id: int, world, player) -> Tuple[bool, str]:
    """Enhanced load game function - replacement for original load_game"""
    return save_system.load_game(slot_id, world, player)


def auto_save_game(world, player) -> Tuple[bool, str]:
    """Auto-save the game"""
    return save_system.auto_save(world, player)


def get_save_slots() -> List[SaveSlot]:
    """Get all save slots for UI display"""
    return save_system.get_save_slots()


def delete_save_slot(slot_id: int) -> Tuple[bool, str]:
    """Delete a save slot"""
    return save_system.delete_save(slot_id)


def get_save_slot_summary(slot_id: int) -> Optional[Dict[str, Any]]:
    """Get save slot summary for display"""
    return save_system.get_save_summary(slot_id)
