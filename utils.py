import json
import gzip
import os
import tempfile
import shutil
import re

# Compression settings
USE_COMPRESSION = True  # Enable/disable compression
USE_BINARY_FORMAT = False  # SECURITY: Use JSON instead of pickle (pickle allows arbitrary code execution)

def sanitize_name(name: str, max_length: int = 32) -> str:
    """Sanitize user input names to prevent save corruption and exploits"""
    if not name or not isinstance(name, str):
        return "Player"
    
    # Remove control characters and restrict to safe characters
    # Allow: letters, numbers, spaces, hyphens, apostrophes, underscores
    safe_name = re.sub(r'[^a-zA-Z0-9 \-\'_]', '', name)
    
    # Remove leading/trailing whitespace
    safe_name = safe_name.strip()
    
    # Collapse multiple spaces
    safe_name = re.sub(r'\s+', ' ', safe_name)
    
    # Enforce length limit
    safe_name = safe_name[:max_length]
    
    # Ensure not empty after sanitization
    if not safe_name:
        return "Player"
    
    return safe_name

def atomic_write(filepath: str, data: bytes, use_compression: bool = False):
    """Write file atomically to prevent corruption if write is interrupted"""
    # Write to temporary file first
    dir_name = os.path.dirname(filepath) or '.'
    
    # Ensure directory exists
    os.makedirs(dir_name, exist_ok=True)
    
    # Create temp file in same directory (ensures same filesystem for atomic rename)
    fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_', suffix='.sav')
    
    try:
        # Write data to temp file
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
        
        # Atomic rename (overwrites existing file)
        # On Windows, we need to remove the target first
        if os.path.exists(filepath):
            os.replace(temp_path, filepath)  # Atomic on both Unix and Windows (Python 3.3+)
        else:
            os.rename(temp_path, filepath)
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        raise e

def save_game(player, world, config, save_slot=None):
    """
    Optimized save system with compression and delta saving.
    Reduces file size from ~305MB to ~5-20MB.
    save_slot: SaveSlot object (if None, uses legacy config.SAVE_FILE)
    """
    # Determine save file path
    if save_slot:
        save_file = save_slot.save_file
        world_file = save_slot.world_file
    else:
        save_file = config.SAVE_FILE
        world_file = config.WORLD_FILE
    # Collect player data with full attributes
    player_data = {
        'x': player.x,
        'y': player.y,
        'name': getattr(player, 'name', 'Player'),
        'color': getattr(player, 'color', (255, 255, 255)),
        'health': player.health,
        'stamina': player.stamina,
        'mana': player.mana,
        'inventory': player.inventory,
        'level': getattr(player, 'level', 1),
        'experience': getattr(player, 'experience', 0),
        'experience_to_next_level': getattr(player, 'experience_to_next_level', 100),
        'stat_points': getattr(player, 'stat_points', 0),
        'perk_points': getattr(player, 'perk_points', 0),
        'acquired_skills': list(getattr(player, 'acquired_skills', set())),
        'skill_points_invested': getattr(player, 'skill_points_invested', {}),
        'known_spells': list(getattr(player, 'known_spells', set())),
        'selected_spell': getattr(player, 'selected_spell', None),
        'secondary_spell': getattr(player, 'secondary_spell', None),
        'equipment': getattr(player, 'equipment', {'weapon': None, 'armor': None, 'accessory': None}),
        'trees_broken_count': getattr(player, 'trees_broken_count', 0),
        'bushes_broken_count': getattr(player, 'bushes_broken_count', 0),
        'rocks_broken_count': getattr(player, 'rocks_broken_count', 0),
        'mushrooms_broken_count': getattr(player, 'mushrooms_broken_count', 0),
        'gathering_skills': getattr(player, 'skills_manager', None).to_dict() if hasattr(player, 'skills_manager') else None,
        'dubloons': getattr(player, 'dubloons', 0),
        'hotbar': getattr(player, 'hotbar_system', None).to_dict() if hasattr(player, 'hotbar_system') else None,
        'cosmetic_manager': getattr(player, 'cosmetic_manager', None).to_dict() if hasattr(player, 'cosmetic_manager') else None,
        'lootbox_shop': getattr(player, 'lootbox_shop', None).to_dict() if hasattr(player, 'lootbox_shop') else None,
        'bestiary': getattr(player, 'bestiary', None).to_dict() if hasattr(player, 'bestiary') else None,
        # Tutorial system state
        'tutorial_completed': getattr(player, 'tutorial_completed', False),
        'tutorial_active': getattr(player, 'tutorial_active', False),
        'tutorial_stage': getattr(player, 'tutorial_stage', 'not_started'),
        'tutorial_enemies_killed': getattr(player, 'tutorial_enemies_killed', 0),
        'tutorial_sticks_equipped': getattr(player, 'tutorial_sticks_equipped', False),
        'tutorial_sticks_stacked': getattr(player, 'tutorial_stacks_stacked', False),
        'tutorials_shown': getattr(player, 'tutorials_shown', {}),  # Tutorial popups that have been shown
        # Tutorial NPC state (if exists)
        'tutorial_npc': None if not hasattr(player, 'tutorial_npc') or player.tutorial_npc is None else {
            'x': player.tutorial_npc.x,
            'y': player.tutorial_npc.y,
            'health': player.tutorial_npc.health,
            'max_health': player.tutorial_npc.max_health,
            'declined_by_player': player.tutorial_npc.declined_by_player,
            'going_to_shelter': player.tutorial_npc.going_to_shelter,
            'at_shelter': player.tutorial_npc.at_shelter,
            'shack_x': player.tutorial_npc.shack_x,
            'shack_y': player.tutorial_npc.shack_y,
            'in_building': getattr(player.tutorial_npc, 'in_building', None),
        },
    }
    
    # Save market state if available
    market_state = None
    if hasattr(player, 'market_manager') and player.market_manager:
        market_state = player.market_manager.save_state()
    
    # Save AI learning data (new in 3.1)
    ai_learning_data = None
    try:
        from ai_personality_system import get_personality_manager
        personality_manager = get_personality_manager()
        ai_learning_data = {
            'global_learning': personality_manager.global_learning_data,
            'personalities': {}
        }
        # Save individual personality learning data
        for enemy_id, personality_system in personality_manager.personalities.items():
            ai_learning_data['personalities'][enemy_id] = {
                'player_combat_patterns': dict(personality_system.learning_memory.player_combat_patterns),
                'successful_tactics': dict(personality_system.learning_memory.successful_tactics),
                'failed_tactics': dict(personality_system.learning_memory.failed_tactics),
                'damage_taken_by_ability': dict(personality_system.learning_memory.damage_taken_by_ability),
                'damage_dealt_by_ability': dict(personality_system.learning_memory.damage_dealt_by_ability)
            }
    except ImportError:
        pass  # AI system not available
    
    # Only save modified tiles (delta saving)
    # Generate default tiles to compare against
    default_tiles = world.get_default_tile_state()
    modified_tiles = {}
    
    for key, tile in world.tiles.items():
        tile_dict = tile.to_dict()
        # Only save if different from default
        if key not in default_tiles or tile_dict != default_tiles[key].to_dict():
            modified_tiles[key] = tile_dict
    
    data = {
        'version': '3.1',  # Version 3.1: Added AI learning persistence
        'player': player_data,
        'modified_tiles': modified_tiles,  # Only changed tiles
        'world_seed': 42,  # For regenerating default world
        'market_state': market_state,  # Market prices and transaction history
        'ai_learning': ai_learning_data,  # AI learning and adaptation data
    }
    
    # SECURITY: Always use JSON (pickle removed for security)
    # JSON is safe from arbitrary code execution attacks
    serialized = json.dumps(data, indent=None, separators=(',', ':')).encode('utf-8')
    
    if USE_COMPRESSION:
        # Compress with gzip (50-70% size reduction even with JSON)
        compressed = gzip.compress(serialized, compresslevel=6)
        # Use atomic write to prevent save corruption
        atomic_write(save_file + '.gz', compressed, use_compression=True)
        # Remove old uncompressed file if it exists
        if os.path.exists(save_file):
            try:
                os.remove(save_file)
            except:
                pass  # Ignore if removal fails
    else:
        # Use atomic write even for uncompressed saves
        atomic_write(save_file, serialized, use_compression=False)

def load_game(player, world, config, save_slot=None):
    """Load save file with decompression (JSON only for security)
    save_slot: SaveSlot object (if None, uses legacy config.SAVE_FILE)
    """
    # Determine save file path
    if save_slot:
        save_file = save_slot.save_file
        compressed_file = save_slot.save_file_compressed
    else:
        save_file = config.SAVE_FILE
        compressed_file = config.SAVE_FILE + '.gz'
    
    try:
        # Try loading compressed file first
        if os.path.exists(compressed_file):
            with open(compressed_file, 'rb') as f:
                compressed = f.read()
            serialized = gzip.decompress(compressed)
            data = json.loads(serialized.decode('utf-8'))
        
        # Fall back to old format
        elif os.path.exists(save_file):
            with open(save_file, 'r') as f:
                data = json.load(f)
        else:
            return  # No save file found
        
        # Load player data
        player_data = data.get('player', {})
        player.x = player_data.get('x', config.WORLD_WIDTH // 2)
        player.y = player_data.get('y', config.WORLD_HEIGHT // 2)
        # SECURITY: Sanitize name from save file
        player.name = sanitize_name(player_data.get('name', 'Player'))
        player.color = tuple(player_data.get('color', (255, 255, 255)))
        player.health = player_data.get('health', 100)
        player.stamina = player_data.get('stamina', 100)
        player.mana = player_data.get('mana', 100)
        player.inventory = player_data.get('inventory', {})
        player.level = player_data.get('level', 1)
        player.experience = player_data.get('experience', 0)
        player.experience_to_next_level = player_data.get('experience_to_next_level', 100)
        player.stat_points = player_data.get('stat_points', player_data.get('skill_points', 0))  # Backward compatibility
        player.perk_points = player_data.get('perk_points', 0)
        player.acquired_skills = set(player_data.get('acquired_skills', []))
        player.skill_points_invested = player_data.get('skill_points_invested', {})
        player.known_spells = set(player_data.get('known_spells', []))
        player.selected_spell = player_data.get('selected_spell', None)
        
        # Load bestiary data if available
        if 'bestiary' in player_data and player_data['bestiary'] and hasattr(player, 'bestiary'):
            player.bestiary.from_dict(player_data['bestiary'])
        player.secondary_spell = player_data.get('secondary_spell', None)
        player.equipment = player_data.get('equipment', {'weapon': None, 'armor': None, 'accessory': None})
        player.trees_broken_count = player_data.get('trees_broken_count', 0)
        player.bushes_broken_count = player_data.get('bushes_broken_count', 0)
        player.rocks_broken_count = player_data.get('rocks_broken_count', 0)
        player.mushrooms_broken_count = player_data.get('mushrooms_broken_count', 0)
        player.dubloons = player_data.get('dubloons', 0)
        
        # Load gathering skills
        if 'gathering_skills' in player_data and player_data['gathering_skills']:
            if not hasattr(player, 'skills_manager') or player.skills_manager is None:
                from skills_system import SkillsManager
                player.skills_manager = SkillsManager()
            player.skills_manager.from_dict(player_data['gathering_skills'])
        
        # Load market state if available
        if 'market_state' in data and data['market_state'] and hasattr(player, 'market_manager'):
            if player.market_manager:
                player.market_manager.load_state(data['market_state'])
        
        # Load AI learning data if available (version 3.1+)
        if 'ai_learning' in data and data['ai_learning']:
            try:
                from ai_personality_system import get_personality_manager
                personality_manager = get_personality_manager()
                
                # Load global learning data
                if 'global_learning' in data['ai_learning']:
                    personality_manager.global_learning_data = data['ai_learning']['global_learning']
                
                # Load individual personality learning data
                if 'personalities' in data['ai_learning']:
                    for enemy_id, learning_data in data['ai_learning']['personalities'].items():
                        # Personality will be recreated when enemy spawns
                        # Store learning data for later restoration
                        if not hasattr(personality_manager, 'pending_learning_data'):
                            personality_manager.pending_learning_data = {}
                        personality_manager.pending_learning_data[enemy_id] = learning_data
            except ImportError:
                pass  # AI system not available
        
        # Load hotbar state if available
        if 'hotbar' in player_data and player_data['hotbar']:
            from hotbar_system import HotbarSystem
            if not hasattr(player, 'hotbar_system'):
                player.hotbar_system = HotbarSystem(num_slots=9)
            player.hotbar_system = HotbarSystem.from_dict(player_data['hotbar'])
        
        # Load cosmetic manager state if available
        if 'cosmetic_manager' in player_data and player_data['cosmetic_manager']:
            from cosmetic_system import CosmeticManager
            if not hasattr(player, 'cosmetic_manager'):
                player.cosmetic_manager = CosmeticManager()
            player.cosmetic_manager = CosmeticManager.from_dict(player_data['cosmetic_manager'])
        
        # Load loot box shop state if available
        if 'lootbox_shop' in player_data and player_data['lootbox_shop']:
            from max_shop_system import LootBoxShop
            if not hasattr(player, 'lootbox_shop'):
                player.lootbox_shop = LootBoxShop()
            player.lootbox_shop = LootBoxShop.from_dict(player_data['lootbox_shop'])
        
        # Load tutorial system state
        player.tutorial_completed = player_data.get('tutorial_completed', False)
        player.tutorial_active = player_data.get('tutorial_active', False)
        player.tutorial_stage = player_data.get('tutorial_stage', 'not_started')
        player.tutorial_enemies_killed = player_data.get('tutorial_enemies_killed', 0)
        player.tutorial_sticks_equipped = player_data.get('tutorial_sticks_equipped', False)
        player.tutorial_sticks_stacked = player_data.get('tutorial_sticks_stacked', False)
        player.tutorials_shown = player_data.get('tutorials_shown', {})
        # Store tutorial NPC state for restoration (will be restored in main.py after NPC is created)
        player.tutorial_npc_saved_state = player_data.get('tutorial_npc', None)
        
        # Load world tiles
        if 'modified_tiles' in data:
            # New format: delta saving
            # Regenerate default world
            default_tiles = world.get_default_tile_state()
            world.tiles = default_tiles.copy()
            
            # Apply modified tiles
            from tile import Tile
            for key, tile_dict in data['modified_tiles'].items():
                world.tiles[key] = Tile.from_dict(tile_dict)
        else:
            # Old format: full world save
            world.tiles = {k: Tile.from_dict(v) if isinstance(v, dict) else v 
                          for k, v in data.get('world', {}).items()}
        
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error loading save file: {e}")
        print("Starting new game...")
