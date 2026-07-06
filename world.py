import json
import gzip
import os
import random
import tempfile
from config import Config
from tile import Tile
from logger_config import get_logger

logger = get_logger(__name__)

# Compression settings for world files
USE_WORLD_COMPRESSION = True

class World:
    def __init__(self, config):
        self.config = config
        self.width = config.WORLD_WIDTH
        self.height = config.WORLD_HEIGHT
        self.seed = 42  # Fixed seed for deterministic generation
        self.tiles = {}  # Empty dict - tiles generated on demand
        self._default_tiles_cache = None  # Cache for delta saving
        self._lazy_generation = True  # Use lazy tile generation
        
        # Locked chests moved to chest_manager in main.py
        self.locked_chests = []
        # self._generate_locked_chests()  # Disabled - using chest_manager now
        
        # Try to load existing world
        self.load_world_if_exists()
    
    def load_world_if_exists(self):
        """Load world from compressed file if it exists (JSON only for security)"""
        compressed_file = self.config.WORLD_FILE + '.gz'
        
        # Try loading compressed world file
        if os.path.exists(compressed_file):
            try:
                with open(compressed_file, 'rb') as f:
                    compressed = f.read()
                serialized = gzip.decompress(compressed)
                # SECURITY: Use JSON only (no pickle)
                raw = json.loads(serialized.decode('utf-8'))
                
                # Check if old massive world (> 100k tiles = needs regeneration)
                if len(raw) > 100000:
                    logger.warning(f"Old world file too large ({len(raw)} tiles), regenerating with lazy loading")
                    os.remove(compressed_file)
                    logger.info("New world initialized with lazy generation")
                    return
                
                # Deserialize tiles
                self.tiles = {k: Tile.from_dict(v) for k, v in raw.items()}
                self._lazy_generation = False  # Already have tiles loaded
                logger.info(f"Loaded world with {len(self.tiles)} tiles")
                return
            except Exception as e:
                logger.error(f"Error loading compressed world: {e}")
                
        # Try loading old uncompressed format
        if os.path.exists(self.config.WORLD_FILE):
            try:
                with open(self.config.WORLD_FILE, 'r') as f:
                    raw = json.load(f)
                
                # Check if old massive world
                if len(raw) > 100000:
                    logger.warning(f"Old world file too large ({len(raw)} tiles), regenerating with lazy loading")
                    os.remove(self.config.WORLD_FILE)
                    logger.info("New world initialized with lazy generation")
                    return
                
                # Deserialize tiles
                self.tiles = {k: Tile.from_dict(v) for k, v in raw.items()}
                self._lazy_generation = False
                # Save in new compressed format
                self.save_tiles(self.tiles)
                # Remove old uncompressed file
                os.remove(self.config.WORLD_FILE)
                logger.info(f"Migrated world to compressed format ({len(self.tiles)} tiles)")
                return
            except Exception as e:
                logger.error(f"Error loading world: {e}")
        
        # New world - will use lazy generation
        logger.info("New world initialized with lazy generation")

    def get_tile(self, x, y):
        """Get tile at position, generating it lazily if needed"""
        key = f"{x},{y}"
        
        # Return cached tile if it exists
        if key in self.tiles:
            return self.tiles[key]
        
        # Generate tile on-demand using deterministic algorithm
        tile = self._generate_tile_at(x, y)
        self.tiles[key] = tile
        return tile
    
    def _generate_tile_at(self, x, y):
        """Generate a single tile at given position (deterministic)"""
        # Use position-based random seed for deterministic generation (10x faster than MD5)
        import random
        random.seed(f"{self.seed}:{x}:{y}")
        hash_val = random.randint(0, 2**32 - 1)
        
        tile_size = self.config.TILE_SIZE
        width = self.width
        height = self.height
        center_x = width // 2
        center_y = height // 2
        
        # Check if in spawn clearing (7x7 tiles around center)
        if (abs(x - center_x) <= tile_size * 3 and abs(y - center_y) <= tile_size * 3):
            # Add some trees around the spawn clearing
            dx = abs(x - center_x) // tile_size
            dy = abs(y - center_y) // tile_size
            # Place trees at corners and edges of spawn area (not in center)
            if (dx == 3 or dy == 3) and (dx >= 2 and dy >= 2):
                if (hash_val % 3) == 0:  # 33% of edge tiles
                    return Tile(ground='grass', obj='tree')
            # Simplified: no blade variations
            return Tile(ground='grass')
        
        # Check if in ocean region (bottom right)
        ocean_tiles_w = (width // 3) // tile_size
        ocean_tiles_h = (height // 3) // tile_size
        ocean_start_x = (width // tile_size - ocean_tiles_w) * tile_size
        ocean_start_y = (height // tile_size - ocean_tiles_h) * tile_size
        
        if x >= ocean_start_x and y >= ocean_start_y:
            return Tile(ground='water')
        
        # Check if in beach (3 tiles around ocean)
        beach_start_x = ocean_start_x - tile_size * 3
        beach_start_y = ocean_start_y - tile_size * 3
        if x >= beach_start_x and y >= beach_start_y:
            return Tile(ground='sand')
        
        # Check if in river
        river_y = ocean_start_y + (ocean_tiles_h // 2) * tile_size
        if ocean_start_x >= x >= center_x and abs(y - river_y) <= tile_size:
            return Tile(ground='water')
        
        # Original lakes near ocean/river (3 lakes)
        for i in range(3):
            lake_x = ocean_start_x - (i+2)*tile_size*8
            lake_y = river_y + (i-1)*tile_size*12
            dx = (x - lake_x) // tile_size
            dy = (y - lake_y) // tile_size
            if abs(dx) <= 4 and abs(dy) <= 3:
                return Tile(ground='water')
        
        # Additional scattered lakes across the world for swimming training (12 more lakes)
        # These are positioned in different quadrants so players always have water nearby
        lake_configs = [
            # Northwest quadrant
            (center_x // 2, center_y // 2, 5, 4),  # Medium lake
            (center_x // 3, center_y // 3, 4, 3),  # Small lake
            (center_x // 4, center_y * 2 // 3, 6, 4),  # Medium-large lake
            # Northeast quadrant
            (center_x + width // 6, center_y // 3, 5, 3),  # Medium lake
            (center_x + width // 4, center_y // 2, 4, 4),  # Small-medium lake
            # Southwest quadrant
            (center_x // 3, center_y + height // 6, 5, 4),  # Medium lake
            (center_x // 2, center_y + height // 4, 4, 3),  # Small lake
            # North central
            (center_x - tile_size * 20, center_y // 4, 6, 4),  # Medium-large lake
            (center_x + tile_size * 25, center_y // 4, 5, 4),  # Medium lake
            # West central
            (center_x // 4, center_y, 5, 5),  # Round medium lake
            # Southeast (not too close to ocean)
            (center_x + width // 6, center_y + height // 6, 4, 3),  # Small lake
            # South central
            (center_x, center_y + height // 5, 6, 5),  # Large lake
        ]
        
        for lake_center_x, lake_center_y, radius_x, radius_y in lake_configs:
            dx = (x - lake_center_x) // tile_size
            dy = (y - lake_center_y) // tile_size
            # Use ellipse equation for varied lake shapes
            if (dx * dx) / (radius_x * radius_x) + (dy * dy) / (radius_y * radius_y) <= 1:
                return Tile(ground='water')
        
        # Check if in rock patches
        for i in range(10):
            patch_cx = width//4 + i*tile_size*6
            patch_cy = height//4 + (i%3)*tile_size*8
            dx = (x - patch_cx) // tile_size
            dy = (y - patch_cy) // tile_size
            if dx*dx + dy*dy <= 4:
                return Tile(ground='grass', obj='rock_group')
        
        # Default: grass with random features
        r = (hash_val % 100) / 100.0  # Convert hash to 0.0-1.0 range
        if r < 0.10:  # 10% trees for abundance (stick drops)
            return Tile(ground='grass', obj='tree')
        elif r < 0.15:  # 5% bushes
            return Tile(ground='grass', obj='bush')
        elif r < 0.03:  # 3% mushrooms
            return Tile(ground='grass', obj='mushroom_patch')
        elif r < 0.08:  # 5% dirt patches
            return Tile(ground='dirt')
        else:
            # Simplified: no blade variations for performance
            return Tile(ground='grass')

    def set_tile(self, x, y, tile):
        """Set tile at position with input validation"""
        # Input validation
        if not isinstance(x, (int, float)):
            logger.warning(f"Invalid x coordinate type: {type(x)}. Expected number.")
            return
        if not isinstance(y, (int, float)):
            logger.warning(f"Invalid y coordinate type: {type(y)}. Expected number.")
            return
        if tile is None:
            logger.warning("Attempted to set None tile")
            return
        if not hasattr(tile, 'layers'):
            logger.warning(f"Invalid tile object: {type(tile)}. Missing 'layers' attribute.")
            return
        
        self.tiles[f"{x},{y}"] = tile

    def save(self):
        self.save_tiles(self.tiles)

    def save_tiles(self, tiles):
        """Save tiles with delta compression - only save changed tiles"""
        # Default grass tile state
        default_tile_dict = {'ground': 'grass', 'object': None, 'effect': None}
        
        # Only save tiles that differ from default grass
        changed_tiles = {}
        for k, v in tiles.items():
            tile_dict = v.to_dict()
            # Check if this tile differs from default
            if tile_dict != default_tile_dict:
                changed_tiles[k] = tile_dict
        
        logger.info(f"[WORLD SAVE] Saving {len(changed_tiles)} changed tiles (out of {len(tiles)} total)")
        
        if USE_WORLD_COMPRESSION:
            # SECURITY: Use JSON instead of pickle (safe from code execution attacks)
            serialized = json.dumps(changed_tiles, separators=(',', ':')).encode('utf-8')
            compressed = gzip.compress(serialized, compresslevel=6)
            
            # Atomic write to prevent corruption
            self._atomic_write_world(self.config.WORLD_FILE + '.gz', compressed)
            
            # Remove old uncompressed file if it exists
            if os.path.exists(self.config.WORLD_FILE):
                os.remove(self.config.WORLD_FILE)
        else:
            # Fallback to uncompressed JSON
            serialized = json.dumps(changed_tiles, indent=2)
            self._atomic_write_world(self.config.WORLD_FILE, serialized.encode('utf-8'))
    
    def _atomic_write_world(self, filepath: str, data: bytes):
        """Write world file atomically to prevent corruption"""
        dir_name = os.path.dirname(filepath) or '.'
        os.makedirs(dir_name, exist_ok=True)
        
        # Create temp file in same directory
        fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_world_', suffix='.dat')
        
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic rename
            if os.path.exists(filepath):
                os.replace(temp_path, filepath)
            else:
                os.rename(temp_path, filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise e
    
    def get_default_tile_state(self):
        """Get default tile state for delta saving comparison"""
        if self._default_tiles_cache is None:
            # Default tile is simple grass
            default_tile = Tile(ground='grass')
            default_tile.layers['blade'] = '/'
            self._default_tiles_cache = {
                'terrain': 'grass',
                'elevation': 0
            }
        return self._default_tiles_cache
    
    def to_dict(self):
        """
        Serialize world to dictionary for saving
        
        Returns:
            dict: World state as dictionary
        """
        # Only save changed tiles (delta compression)
        default_tile_dict = {'ground': 'grass', 'object': None, 'effect': None}
        changed_tiles = {}
        
        for k, v in self.tiles.items():
            tile_dict = v.to_dict()
            if tile_dict != default_tile_dict:
                changed_tiles[k] = tile_dict
        
        return {
            'width': self.width,
            'height': self.height,
            'seed': self.seed,
            'tiles': changed_tiles,
            'lazy_generation': self._lazy_generation,
            'locked_chests': [
                {'x': chest.x, 'y': chest.y, 'unlocked': chest.unlocked}
                for chest in self.locked_chests
            ] if self.locked_chests else []
        }